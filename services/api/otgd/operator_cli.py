"""Run with separately authorized maintenance credentials, never the API role."""

import argparse
import json
import re
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from .canonical import strict_loads
from .config import settings
from .db import factory
from .errors import Problem
from .operator_governance import SCHEMAS, history, submit, transition


def cloud_client(service, cfg):
    suffix = "amazonaws.com.cn" if cfg.aws_region.startswith("cn-") else "amazonaws.com"
    endpoint = "https://sts." + cfg.aws_region + "." + suffix
    if service == "iam":
        endpoint = "https://iam." + ("cn-north-1.amazonaws.com.cn" if cfg.aws_region.startswith("cn-") else "us-gov.amazonaws.com" if cfg.aws_region.startswith("us-gov-") else "amazonaws.com")
    return boto3.client(service, region_name=cfg.aws_region, endpoint_url=endpoint,
        config=Config(ignore_configured_endpoint_urls=True, connect_timeout=3, read_timeout=5,
            retries={"max_attempts": 1, "mode": "standard"}))


def principal(cfg, *, local_principal=None, expected_account=None, expected_role_arn=None, sts=None, iam=None):
    if cfg.environment in ("local", "test"):
        if not isinstance(local_principal, str) or not re.fullmatch(r"local:[A-Za-z0-9_.-]{1,100}", local_principal):
            raise ValueError("Local administration requires an explicit local:principal; it is not AWS/scientific evidence")
        if expected_account or expected_role_arn:
            raise ValueError("Local administration cannot pretend to verify an AWS role")
        return local_principal
    if local_principal:
        raise ValueError("Cloud administration requires independently authenticated AWS role credentials")
    if not isinstance(expected_account, str) or not re.fullmatch(r"[0-9]{12}", expected_account):
        raise ValueError("An explicit expected AWS account is required")
    if getattr(cfg, "deployment_account", None) != expected_account:
        raise ValueError("The operator account must match the configured deployment account")
    match = re.fullmatch(r"arn:(aws|aws-us-gov|aws-cn):iam::([0-9]{12}):role/([A-Za-z0-9_+=,.@/-]+)", expected_role_arn or "")
    if not match or match[2] != expected_account or len(expected_role_arn) > 256:
        raise ValueError("An exact expected maintenance IAM role ARN is required")
    partition = "aws-cn" if cfg.aws_region.startswith("cn-") else "aws-us-gov" if cfg.aws_region.startswith("us-gov-") else "aws"
    if match[1] != partition:
        raise ValueError("The operator role must match the configured deployment partition")
    identity = (sts or cloud_client("sts", cfg)).get_caller_identity()
    assumed = re.fullmatch(r"arn:([^:]+):sts::([0-9]{12}):assumed-role/([^/]+)/[^/]+", identity.get("Arn", ""))
    if (identity.get("Account") != expected_account or not assumed or assumed[1] != match[1]
        or assumed[2] != expected_account or assumed[3] != match[3].split("/")[-1]):
        raise ValueError("Authenticated AWS caller does not match the expected maintenance role/account")
    role = (iam or cloud_client("iam", cfg)).get_role(RoleName=assumed[3]).get("Role", {})
    caller_id = identity.get("UserId", "")
    if (role.get("Arn") != expected_role_arn or not isinstance(role.get("RoleId"), str)
        or not role["RoleId"] or not caller_id.startswith(role["RoleId"] + ":")):
        raise ValueError("Maintenance role path and immutable role ID must match independently resolved IAM identity")
    # Normalize away session names: three sessions of one role are one principal.
    return expected_role_arn


def require_maintenance_db(db, cfg):
    if db.bind.dialect.name != "postgresql":
        if cfg.environment != "test":
            raise ValueError("Administration requires PostgreSQL outside unit tests")
        return
    authority = db.execute(text("SELECT current_user, has_table_privilege(current_user, 'operator_registry', 'UPDATE')")).one()
    if authority[0] == cfg.app_database_user or not authority[1]:
        raise ValueError("The runtime database identity cannot administer registries")


def execute(args, *, cfg=None, sessions=None, sts=None, iam=None):
    cfg = cfg or settings()
    actor = principal(cfg, local_principal=args.local_principal, expected_account=args.expected_account,
        expected_role_arn=args.expected_role_arn, sts=sts, iam=iam)
    if cfg.environment in ("qa", "prod"):
        duty = {"submit": "submitter", "approve": "reviewer", "release": "releaser", "retire": "releaser", "revoke": "releaser"}.get(args.command)
        roles = {"otgd-" + cfg.environment + "-registry-" + name for name in ("submitter", "reviewer", "releaser")}
        if actor.split("/")[-1] not in roles or duty and actor.split("/")[-1] != "otgd-" + cfg.environment + "-registry-" + duty:
            raise ValueError("Authenticated operator role is not authorized for this lifecycle operation")
    with (sessions or factory())() as db:
        transaction = db.begin()
        try:
            require_maintenance_db(db, cfg)
            if args.command == "submit":
                path = Path(args.file)
                if path.stat().st_size > 262144:
                    raise ValueError("Submission file exceeds 256 KiB")
                result = submit(db, args.kind, strict_loads(path.read_bytes()), actor)
            elif args.command == "history":
                result = history(db, args.kind, args.registry_id)
            else:
                result = transition(db, args.kind, args.registry_id, args.version, args.command,
                    actor, args.reason, args.if_revision)
            db.flush()
            if args.apply and args.command != "history":
                transaction.commit()
            else:
                transaction.rollback()
            return {"environment": cfg.environment, "mode": "applied" if args.apply and args.command != "history" else "dry_run",
                "operation": args.command, "verified_principal": actor, "result": result}
        except BaseException:
            if transaction.is_active:
                transaction.rollback()
            raise


def parser():
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--apply", action="store_true", help="Commit the displayed operation; default executes validation then rolls back")
    value.add_argument("--local-principal", help="Only local/test; explicit fictional administration identity")
    value.add_argument("--expected-account", help="QA/prod: exact AWS account ID")
    value.add_argument("--expected-role-arn", help="QA/prod: exact IAM maintenance role ARN; STS session identity is verified")
    sub = value.add_subparsers(dest="command", required=True)
    for command in ("submit", "approve", "release", "retire", "revoke", "history"):
        child = sub.add_parser(command)
        child.add_argument("kind", choices=SCHEMAS)
        if command == "submit":
            child.add_argument("file", help="Strict UTF-8 JSON containing the typed submission")
        else:
            child.add_argument("registry_id")
        if command not in ("submit", "history"):
            child.add_argument("version")
            child.add_argument("--if-revision", type=int, required=True)
            child.add_argument("--reason", required=True, help="Audit decision reason, excluding participant health data/secrets")
    return value


def main(argv=None):
    try:
        result = execute(parser().parse_args(argv))
    except (ValueError, Problem) as error:
        # Do not print DSNs, AWS credentials, participant records or exception traces.
        print(json.dumps({"status": "rejected", "code": getattr(error, "code", "INVALID_OPERATOR_REQUEST")}))
        return 1
    except (OSError, BotoCoreError, ClientError, SQLAlchemyError):
        print(json.dumps({"status": "rejected", "code": "OPERATOR_DEPENDENCY_UNAVAILABLE"}))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
