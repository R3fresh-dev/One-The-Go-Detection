"""Fail-closed release evidence. Local JSON claims never replace GitHub checks."""
from __future__ import annotations

import base64
import hashlib
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re

import httpx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from otgd.canonical import canonical, strict_loads


class Gate(RuntimeError):
    pass


REPOSITORY = "R3fresh-dev/One-The-Go-Detection"
WORKFLOW_PATH = ".github/workflows/merge-gate.yml"
REQUIRED_JOBS = frozenset({
    "unit-coverage", "atdd", "components", "merge-gate",
    "platform / contracts-and-synthesis", "platform / postgres-integration",
    "platform / localstack-integration", "native / shared-and-firmware",
    "native / android", "native / ios",
})
REQUIRED_GATE_LABELS = frozenset({
    "unit-coverage", "atdd", "components", "performance", "live-dependencies",
    "docker-health", "localstack-api", "specifications", "native-android",
    "native-ios", "firmware",
})
QA_PROBES = frozenset({
    "private_network", "conditional_upload", "worker_kill_matrix",
    "deletion_restore", "authenticated_export", "alarm_delivery",
})


def bounded_json(path: Path, limit=65_536):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise Gate("Evidence exceeds its supported size")
    try:
        value = strict_loads(raw)
    except (ValueError, TypeError):
        raise Gate("Evidence is not strict bounded JSON") from None
    if not isinstance(value, dict):
        raise Gate("Evidence must be a JSON object")
    return value


def sha256(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def positive_int(value):
    return type(value) is int and 0 < value <= 9_007_199_254_740_991


def trusted_branch(event, branch):
    return ((event == "push" and branch == "main") or
            (event == "merge_group" and isinstance(branch, str) and
             branch.startswith("gh-readonly-queue/main/")))


def validate_gate_binding(proof, revision):
    fields = {"provider", "repository", "workflow_path", "workflow_id", "run_id",
              "run_attempt", "head_sha", "run_url", "event", "head_branch", "jobs"}
    if (not isinstance(proof, dict) or set(proof) != fields or
            not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision) or
            proof.get("provider") != "github_actions" or proof.get("repository") != REPOSITORY or
            proof.get("workflow_path") != WORKFLOW_PATH or proof.get("head_sha") != revision or
            not all(positive_int(proof.get(k)) for k in ("workflow_id", "run_id", "run_attempt")) or
            proof.get("run_url") != f"https://github.com/{REPOSITORY}/actions/runs/{proof.get('run_id')}" or
            not trusted_branch(proof.get("event"), proof.get("head_branch")) or
            not isinstance(proof.get("jobs"), dict) or set(proof["jobs"]) != REQUIRED_JOBS or
            not all(positive_int(x) for x in proof["jobs"].values()) or
            len(set(proof["jobs"].values())) != len(REQUIRED_JOBS)):
        raise Gate("Signed release lacks trusted exact-revision gate provenance")
    return sha256(proof)


def _github_json(client, path, **params):
    try:
        response = client.get(f"https://api.github.com/repos/{REPOSITORY}/{path}", params=params)
        if response.status_code != 200 or len(response.content) > 2_097_152:
            raise Gate("GitHub evidence is unavailable; authorized read access is required")
        value = strict_loads(response.content)
        if not isinstance(value, dict):
            raise Gate("GitHub evidence is malformed")
        return value
    except (httpx.HTTPError, ValueError, TypeError):
        raise Gate("GitHub evidence cannot be verified") from None


def verify_github_gates(evidence, revision, *, client=None):
    """Verify the run and every job from its latest attempt, without redirects."""
    labels = evidence.get("passed") if isinstance(evidence, dict) else None
    url = evidence.get("run_url") if isinstance(evidence, dict) else None
    if not isinstance(url,str):
        raise Gate("A trusted GitHub run URL is required")
    match = re.fullmatch(
        rf"https://github\.com/{re.escape(REPOSITORY)}/actions/runs/([1-9][0-9]*)",
        url,
    )
    if (not match or evidence.get("revision") != revision or
            not isinstance(labels, list) or any(not isinstance(x, str) for x in labels) or
            len(labels) != len(set(labels)) or not REQUIRED_GATE_LABELS.issubset(labels)):
        raise Gate("Supply exact-revision evidence from the trusted merge-gate workflow")
    if client is None:
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN") or os.getenv("GH_ADMIN_TOKEN")
        if token:
            headers["Authorization"] = "Bearer " + token
        with httpx.Client(headers=headers, timeout=15, follow_redirects=False) as owned:
            return verify_github_gates(evidence, revision, client=owned)
    run_id = int(match.group(1))
    run = _github_json(client, f"actions/runs/{run_id}")
    attempt = run.get("run_attempt")
    workflow_id = run.get("workflow_id")
    if (run.get("id") != run_id or run.get("head_sha") != revision or
            run.get("status") != "completed" or run.get("conclusion") != "success" or
            run.get("path") != WORKFLOW_PATH or
            run.get("repository", {}).get("full_name") != REPOSITORY or
            run.get("head_repository", {}).get("full_name") != REPOSITORY or
            not trusted_branch(run.get("event"), run.get("head_branch")) or
            not positive_int(attempt) or not positive_int(workflow_id)):
        raise Gate("GitHub run is not a successful trusted-main run for this exact revision")
    workflow = _github_json(client, f"actions/workflows/{workflow_id}")
    if workflow.get("id") != workflow_id or workflow.get("path") != WORKFLOW_PATH or workflow.get("state") != "active":
        raise Gate("GitHub run does not belong to the active trusted merge workflow")
    jobs = []
    total = None
    for page in range(1, 11):
        result = _github_json(client, f"actions/runs/{run_id}/attempts/{attempt}/jobs", per_page=100, page=page)
        batch = result.get("jobs")
        if not isinstance(batch, list) or type(result.get("total_count")) is not int:
            raise Gate("GitHub job pagination is malformed")
        if total is None:
            total = result["total_count"]
        if result["total_count"] != total or not 0 < total <= 1000 or len(batch) > 100:
            raise Gate("GitHub job evidence changed or exceeds its bounded pagination")
        jobs.extend(batch)
        if len(batch) < 100:
            break
    if len(jobs) != total:
        raise Gate("Complete latest-attempt GitHub job evidence is required")
    job_ids = {}
    seen_ids = set()
    for job in jobs:
        if (not isinstance(job, dict) or not positive_int(job.get("id")) or job["id"] in seen_ids or
                job.get("run_id") != run_id or job.get("run_attempt") != attempt or
                job.get("head_sha") != revision or job.get("status") != "completed" or
                job.get("conclusion") != "success"):
            raise Gate("A GitHub job failed, was skipped, or does not belong to the latest attempt")
        seen_ids.add(job["id"])
        name = job.get("name")
        if name in REQUIRED_JOBS:
            if name in job_ids:
                raise Gate("Required GitHub job names are ambiguous")
            job_ids[name] = job["id"]
    proof = {"provider": "github_actions", "repository": REPOSITORY,
             "workflow_path": WORKFLOW_PATH, "workflow_id": workflow_id,
             "run_id": run_id, "run_attempt": attempt, "head_sha": revision,
             "run_url": evidence["run_url"], "event": run["event"],
             "head_branch": run["head_branch"], "jobs": job_ids}
    validate_gate_binding(proof, revision)
    # Close the normal rerun window while evidence is fetched. Activation also
    # performs this verification immediately before its mutation.
    current = _github_json(client, f"actions/runs/{run_id}")
    if any(current.get(k) != run.get(k) for k in ("id", "run_attempt", "status", "conclusion", "head_sha", "workflow_id")):
        raise Gate("GitHub run changed during evidence verification")
    return proof


def verify_gate_file(path, revision, *, client=None):
    if not path:
        raise Gate("Supply --gate-evidence from the exact-revision merge-gate run")
    return verify_github_gates(bounded_json(path), revision, client=client)


def verify_signed_record(path, public_path):
    envelope = bounded_json(path)
    if (set(envelope) != {"schema_version", "payload", "payload_sha256", "algorithm", "signature"} or
            envelope.get("schema_version") != "1.0.0" or envelope.get("algorithm") != "Ed25519" or
            not isinstance(envelope.get("payload"), dict) or
            envelope.get("payload_sha256") != sha256(envelope["payload"])):
        raise Gate("Invalid signed evidence envelope")
    public = serialization.load_pem_public_key(public_path.read_bytes())
    if not isinstance(public, Ed25519PublicKey):
        raise Gate("Expected an independently trusted Ed25519 key")
    try:
        signature = base64.b64decode(envelope["signature"], validate=True)
    except (ValueError, TypeError):
        raise Gate("Invalid evidence signature encoding") from None
    public.verify(signature, canonical(envelope["payload"]))
    return envelope["payload"]


def _utc(value):
    if not isinstance(value, str) or len(value) > 40:
        raise Gate("QA approval times must be explicit UTC timestamps")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise Gate("Invalid QA approval timestamp") from None
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise Gate("QA approval times must use UTC")
    return parsed


def validate_qa_approval(payload, expected, *, now=None):
    """Operator-signed approval of referenced QA probes, not execution of probes."""
    now = now or datetime.now(timezone.utc)
    required = {"schema_version", "purpose", "environment", "account", "region", "image_digest",
                "release_id", "qa_release_sha256", "gate_provenance_sha256", "status", "passed_gates",
                "executed_at", "approved_at", "expires_at", "operator_ref", "evidence_refs"}
    if (not isinstance(payload, dict) or set(payload) != required or payload.get("schema_version") != "1.0.0" or
            payload.get("purpose") != "qa-release-approval" or payload.get("environment") != "qa" or
            payload.get("status") != "passed" or
            any(payload.get(k) != expected.get(k) for k in ("account", "region", "image_digest", "release_id", "qa_release_sha256", "gate_provenance_sha256")) or
            not isinstance(payload.get("passed_gates"), list) or
            any(not isinstance(x, str) for x in payload["passed_gates"]) or
            len(payload["passed_gates"]) != len(set(payload["passed_gates"])) or
            not QA_PROBES.issubset(payload["passed_gates"])):
        raise Gate("QA approval is incomplete or does not bind the tested source release")
    refs = payload.get("evidence_refs")
    operator = payload.get("operator_ref")
    if (not isinstance(operator, str) or not operator.strip() or len(operator) > 256 or
            any(ord(c) < 32 for c in operator) or not isinstance(refs, dict) or
            not QA_PROBES.issubset(refs) or
            any(not isinstance(v, str) or not v.strip() or len(v) > 2048 or any(ord(c) < 32 for c in v) for v in refs.values())):
        raise Gate("QA approval requires an accountable operator and each probe's evidence reference")
    executed, approved, expires = (_utc(payload[k]) for k in ("executed_at", "approved_at", "expires_at"))
    if not executed <= approved <= now < expires or expires - executed > timedelta(days=7):
        raise Gate("QA approval is future-dated, expired, or exceeds seven days from probe execution")
    return payload


def verify_qa_approval(path, public_path, expected, *, now=None):
    if not path:
        raise Gate("Supply independently signed --qa-evidence for production promotion/activation")
    return validate_qa_approval(verify_signed_record(path, public_path), expected, now=now)
