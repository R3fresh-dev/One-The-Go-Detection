#!/usr/bin/env python3
"""Seal actual fresh study reapprovals; does not grant approvals or enable services."""

import argparse
import json

from otgd.config import settings
from otgd.db import factory
from otgd.operator_cli import principal, require_maintenance_db
from otgd.recovery_scopes import seal_study


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study-id", required=True)
    parser.add_argument("--local-principal")
    parser.add_argument("--expected-account")
    parser.add_argument("--expected-role-arn")
    args = parser.parse_args()
    cfg = settings()
    actor = principal(
        cfg,
        local_principal=args.local_principal,
        expected_account=args.expected_account,
        expected_role_arn=args.expected_role_arn,
    )
    if (
        cfg.environment in ("qa", "prod")
        and actor.split("/")[-1] != "otgd-" + cfg.environment + "-registry-releaser"
    ):
        raise ValueError(
            "Only the independently authenticated registry release role may seal reapproval"
        )
    with factory().begin() as db:
        require_maintenance_db(db, cfg)
        print(json.dumps(seal_study(db, args.study_id, actor), sort_keys=True))


if __name__ == "__main__":
    main()
