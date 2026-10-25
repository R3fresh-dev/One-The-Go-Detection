"""Prepare a private, bounded ledger for actual fictional local browser tests.

This command does not contact services, mint tokens, provision scientific
approval, clear data, change Docker, or replace the protected deletion journal.
The browser records only accepted session locators here, then refuses all-data
cleanup if an unexpected server record exists. Preserve this file on retries.
"""
import argparse
import json
import os
from pathlib import Path
import re
import stat
from urllib.parse import urlsplit
from uuid import uuid4

SCOPE = "FICTIONAL SOFTWARE BROWSER ACCEPTANCE ONLY; NO HUMAN OR SCIENTIFIC AUTHORITY"
ACCOUNTS = ("browser_mobile", "browser_desktop")
MAX_BYTES = 65536


def local_origin(value, port):
    parsed = urlsplit(value)
    if (parsed.scheme != "http" or parsed.hostname != "localhost" or parsed.port != port
        or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment):
        raise ValueError("Browser fixture requires exact localhost service origins")
    return value


def validate(value):
    if not isinstance(value, dict) or value.get("schema_version") != 1 or value.get("scope") != SCOPE:
        raise ValueError("Unrecognized browser fixture ledger")
    if not re.fullmatch(r"fictional-browser-[a-f0-9]{32}", value.get("namespace", "")):
        raise ValueError("Invalid fictional browser namespace")
    for name, port in (("api_origin", 8000), ("identity_origin", 8081), ("web_origin", 8082)):
        local_origin(value.get(name, ""), port)
    if not isinstance(value.get("accounts"), dict) or set(value["accounts"]) != set(ACCOUNTS):
        raise ValueError("Only the two reserved fictional browser identities are allowed")
    for account in value["accounts"].values():
        if not isinstance(account, dict) or set(account) != {"session_ids"}:
            raise ValueError("Unexpected account fixture metadata")
        ids = account["session_ids"]
        if not isinstance(ids, list) or len(ids) > 500 or len(ids) != len(set(ids)) or any(
            not isinstance(sid, str) or not re.fullmatch(r"[a-f0-9-]{36}", sid) for sid in ids
        ):
            raise ValueError("Invalid accepted session inventory")
    profiles = value.get("profile_versions", {})
    if not isinstance(profiles, dict) or set(profiles) - set(ACCOUNTS) or any(
        not isinstance(ids, list) or len(ids) > 500 or any(not isinstance(item, str) or not re.fullmatch(r"[a-f0-9-]{36}", item) for item in ids)
        for ids in profiles.values()
    ):
        raise ValueError("Unexpected profile ownership locators")
    governed = value.get("governed", {})
    if not isinstance(governed, dict) or set(governed) - set(ACCOUNTS):
        raise ValueError("Unexpected governed fixture identities")
    for refs in governed.values():
        if not isinstance(refs, dict) or set(refs) != {
            "study_id", "protocol_id", "invitation_id", "document_version", "document_sha256"
        } or not all(isinstance(item, str) for item in refs.values()):
            raise ValueError("Invalid fictional governed locators")
        if not refs["study_id"].startswith("fictional-probe-") or not re.fullmatch(r"[a-f0-9]{64}", refs["document_sha256"]):
            raise ValueError("Governed locators require explicit fictional provenance")
    return value


def require_owned_inventory(ledger, account, inventory):
    known = ledger["accounts"][account]["session_ids"]
    if (not isinstance(inventory, dict) or not isinstance(inventory.get("items"), list)
        or "next_cursor" not in inventory or any(not isinstance(item, dict) for item in inventory["items"])):
        raise ValueError("Incomplete server inventory; preserve all data and stop")
    if inventory.get("next_cursor") is not None or any(
        item.get("session_id") not in known for item in inventory.get("items", [])
    ):
        raise ValueError("Unexpected existing records; preserve all data and stop")


def provision_governed(ledger):
    """Maintenance-only fixture setup through existing immutable registry workflow."""
    import httpx
    from participant_probe import Actor, admit, provision
    from app_flow import signin
    from otgd.config import settings

    cfg = settings()
    admit(cfg)  # Exact local PostgreSQL, origins, buckets, queues and maintenance role.
    with httpx.Client(timeout=15, follow_redirects=False, trust_env=False) as http:
        staff = Actor(http, signin(http, cfg, "browser_staff"))
        governed = ledger.setdefault("governed", {})
        for account in ACCOUNTS:
            subject = Actor(http, signin(http, cfg, account))
            require_owned_inventory(ledger, account, subject.request("GET", "/v1/sessions?limit=100"))
            if account in governed:
                continue
            ids, _, study, _ = provision(cfg, subject.account, staff.account, uuid4().hex[:16],
                staff_subject="local-browser_staff")
            governed[account] = {"study_id": ids["study"], "protocol_id": ids["protocol"],
                **{key: study[key] for key in ("invitation_id", "document_version", "document_sha256")}}
    return validate(ledger)


def prepare(path, *, confirmed=False, api_origin="http://localhost:8000"):
    if not confirmed:
        raise ValueError("Explicit fictional workspace confirmation is required")
    local_origin(api_origin, 8000)
    path = Path(path)
    flags = os.O_NOFOLLOW | os.O_CLOEXEC
    try:
        fd = os.open(path, os.O_RDONLY | flags)
    except FileNotFoundError:
        value = validate({"schema_version": 1, "scope": SCOPE,
            "namespace": "fictional-browser-" + uuid4().hex,
            "api_origin": api_origin, "identity_origin": "http://localhost:8081",
            "web_origin": "http://localhost:8082",
            "accounts": {account: {"session_ids": []} for account in ACCOUNTS}})
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | flags, 0o600)
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        return value
    with os.fdopen(fd, "r") as stream:
        info = os.fstat(stream.fileno())
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
            or info.st_mode & 0o077 or info.st_nlink != 1 or info.st_size > MAX_BYTES):
            raise ValueError("Browser fixture ledger must be bounded, private and owned")
        value = validate(json.loads(stream.read(MAX_BYTES + 1)))
    if value["api_origin"] != api_origin:
        raise ValueError("Preserved fixture service origin changed")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-fictional-workspace", action="store_true")
    parser.add_argument("--manifest", default="/tmp/otgd-browser-fixture.json")
    parser.add_argument("--provision-governed", action="store_true",
        help="Requires canonical local maintenance environment; prints public fictional locators only")
    args = parser.parse_args()
    value = prepare(args.manifest, confirmed=args.confirm_fictional_workspace)
    if args.provision_governed:
        value = provision_governed(value)
        # Existing path has already passed private ownership/symlink admission.
        fd = os.open(args.manifest, os.O_WRONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
        with os.fdopen(fd, "w") as stream:
            stream.truncate(0)
            json.dump(value, stream, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        print(json.dumps(value, sort_keys=True))
        return
    print(json.dumps({"manifest": str(Path(args.manifest).resolve()), "namespace": value["namespace"],
        "fictional_only": True, "service_mutations": False}))


if __name__ == "__main__":
    main()
