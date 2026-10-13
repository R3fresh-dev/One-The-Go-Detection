"""Explicit participant-copy authority; recording/upload approval never grants export.

The existing operator registry supplies independent immutable approval history.
Frozen sources are re-admitted at every worker/delivery boundary and read only
through their verified non-null S3 versions. No deployment seeds an authority.
"""
from __future__ import annotations

import hashlib
import threading
from typing import Annotated, Literal

from pydantic import Field, model_validator
from sqlalchemy import BigInteger, cast, select

from .canonical import canonical, digest
from .db import Account, Artifact, Check, Job, RegistryVersion, iso, now
from .dto import DTO, Name, SHA, UUID, RawExportScope
from .errors import Problem

RAW_KINDS = ("eye_video", "ecg_waveform")
MAX_RAW_FILES = 128
MAX_UNCOMPRESSED = 50 * 1024 * 1024
MAX_ARCHIVE = 64 * 1024 * 1024
MAX_SCOPE_PAGE = 4
# At most one fully verified archive buffer per API process. Network reads never
# hold an account/database lock; rejected/cancelled responses release this slot.
DOWNLOAD_SLOTS = threading.BoundedSemaphore(1)
STRUCTURED_UNCOMPRESSED = 50 * 1024 * 1024
STRUCTURED_ARCHIVE = 64 * 1024 * 1024
Version = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")]
RawName = Annotated[str, Field(min_length=1, max_length=128)]


class RawExportAuthorization(DTO):
    schema_version: Literal["1.0.0"] = "1.0.0"
    registry_id: RawName
    authorization_id: RawName
    version: Version
    expires_at: Annotated[float, Field(gt=0)]
    evidence_ref: Name
    evidence_sha256: SHA
    account_ref: UUID
    data_generation: Annotated[int, Field(ge=1, le=9007199254740991)]
    study_id: RawName
    raw_kinds: Annotated[list[Literal["eye_video", "ecg_waveform"]], Field(min_length=1, max_length=2)]
    purpose: Literal["participant_requested_raw_export"]
    purpose_id: RawName
    purpose_text: Annotated[str, Field(min_length=1, max_length=4096)]
    retention_policy_id: Name
    retention_policy_version: Version
    retention_policy_sha256: SHA
    export_notice_version: RawName
    export_notice_text: Annotated[str, Field(min_length=1, max_length=16384)]
    export_notice_sha256: SHA
    max_export_lifetime_seconds: Annotated[int, Field(ge=60, le=86400)]
    max_uncompressed_bytes: Annotated[int, Field(ge=1, le=MAX_UNCOMPRESSED)]
    max_archive_bytes: Annotated[int, Field(ge=1, le=MAX_ARCHIVE)]

    @model_validator(mode="after")
    def identity(self):
        if (self.registry_id != self.authorization_id or len(set(self.raw_kinds)) != len(self.raw_kinds)
            or len(self.export_notice_text.encode()) > 16384
            or hashlib.sha256(self.export_notice_text.encode()).hexdigest() != self.export_notice_sha256):
            raise ValueError("Raw export authority identity, notice or selection is invalid")
        return self


def validate_dependencies(db, body):
    """Called by independent registry release and every later admission."""
    from .operator_governance import active_body
    value = RawExportAuthorization.model_validate(body).data()
    account = db.get(Account, value["account_ref"])
    study = active_body(db, "study", value["study_id"])
    policy = active_body(db, "retention", value["retention_policy_id"])
    if (not account or account.state != "active" or account.generation != value["data_generation"]
        or account.id not in study["account_refs"] or policy["study_id"] != value["study_id"]
        or policy["version"] != value["retention_policy_version"] or digest(policy) != value["retention_policy_sha256"]
        or not set(value["raw_kinds"]).issubset(policy["raw_kinds"])):
        raise Problem(403, "RAW_EXPORT_SCOPE_MISMATCH")
    return value


def current_authorization(db, account, scope):
    from .operator_governance import released_version
    from .raw_retention import current_consent
    scope = RawExportScope.model_validate(scope).data()
    row = released_version(db, "raw_export", scope["authorization_id"])
    value = validate_dependencies(db, row.body)
    if (value["account_ref"] != account.id or value["data_generation"] != account.generation
        or value["version"] != scope["authorization_version"] or row.sha256 != scope["authorization_sha256"]
        or value["export_notice_version"] != scope["export_notice_version"]
        or value["export_notice_sha256"] != scope["export_notice_sha256"]):
        raise Problem(403, "RAW_EXPORT_SCOPE_MISMATCH")
    current_consent(db, account, value["study_id"])
    return value


def source_descriptor(db, account, authorization, artifact_id, session_ids):
    from .raw_retention import assert_artifact_admitted
    artifact = db.get(Artifact, artifact_id)
    if (not artifact or artifact.account_id != account.id or artifact.generation != account.generation
        or artifact.session_id not in session_ids or artifact.kind not in authorization["raw_kinds"]):
        raise Problem(403, "RAW_EXPORT_SELECTION_DENIED")
    check = db.get(Check, artifact.session_id)
    if (not check or check.account_id != account.id or check.generation != account.generation
        or check.study_id != authorization["study_id"] or check.state not in ("completed", "invalid")):
        raise Problem(403, "RAW_EXPORT_SELECTION_DENIED")
    from .domain import safe_result
    safe_result(check.result)
    if artifact.state in ("cleanup_pending", "purged"):
        raise Problem(403, "RAW_EXPORT_SELECTION_DENIED")
    if artifact.state != "verified" or not artifact.version_id or artifact.version_id == "null":
        raise Problem(409, "RAW_EXPORT_VERIFIED_VERSION_REQUIRED")
    retained = assert_artifact_admitted(db, account, artifact)
    if (retained.study_id != authorization["study_id"] or retained.kind != artifact.kind
        or retained.authority["policy_id"] != authorization["retention_policy_id"]
        or retained.authority["policy_sha256"] != authorization["retention_policy_sha256"]
        or not 0 < artifact.size <= {"eye_video": 64, "ecg_waveform": 16}[artifact.kind]*1024*1024):
        raise Problem(403, "RAW_EXPORT_SELECTION_DENIED")
    return {"artifact_id": artifact.id, "session_id": artifact.session_id, "kind": artifact.kind,
        "bucket": artifact.bucket, "key": artifact.key, "version_id": artifact.version_id,
        "sha256": artifact.sha256, "size_bytes": artifact.size, "media_type": artifact.media_type,
        "retained_until": retained.retained_until, "retention_authority_sha256": digest(retained.authority)}


def freeze_export(db, account, raw_scope, session_ids):
    """Freeze explicit selection; no object listing or new S3 read is needed."""
    from .raw_retention import timestamp
    scope = RawExportScope.model_validate(raw_scope.data() if isinstance(raw_scope, RawExportScope) else raw_scope).data()
    authorization = current_authorization(db, account, scope)
    tick = now()
    if not tick-600 <= timestamp(scope["acknowledged_at"]) <= tick+5:
        raise Problem(403, "RAW_EXPORT_CONFIRMATION_EXPIRED")
    sources = [source_descriptor(db, account, authorization, id, session_ids) for id in sorted(scope["artifact_ids"])]
    if sum(source["size_bytes"] for source in sources) > authorization["max_uncompressed_bytes"]:
        raise Problem(413, "EXPORT_TOO_LARGE")
    expiry = min(tick+authorization["max_export_lifetime_seconds"], tick+86400,
        authorization["expires_at"], *(source["retained_until"] for source in sources))
    if expiry <= tick:
        raise Problem(403, "RAW_EXPORT_WINDOW_CLOSED")
    value = {"schema_version": "1.0.0", "account_ref": account.id, "data_generation": account.generation,
        "scope": scope, "authorization": authorization, "sources": sources, "expires_at": expiry}
    value["frozen_sha256"] = digest(value)
    return {"raw_export": value, "expires_at": expiry}


def validate_job(db, account, job):
    """Never use a frozen positive approval as a substitute for current authority."""
    if not job.body.get("include_raw"):
        if job.body.get("raw_export") is not None or job.body.get("raw_scope") is not None:
            raise Problem(503, "RAW_EXPORT_INTEGRITY_FAILURE")
        return None
    frozen = job.body.get("raw_export")
    if (not isinstance(frozen, dict) or frozen.get("schema_version") != "1.0.0"
        or frozen.get("frozen_sha256") != digest({key: value for key, value in frozen.items() if key != "frozen_sha256"})
        or frozen.get("account_ref") != account.id or frozen.get("data_generation") != account.generation
        or account.state != "active" or job.generation != account.generation or job.account_id != account.id
        or job.kind != "export" or job.body.get("raw_scope") != frozen.get("scope")):
        raise Problem(403, "RAW_EXPORT_INTEGRITY_FAILURE")
    authorization = current_authorization(db, account, frozen["scope"])
    if authorization != frozen.get("authorization"):
        raise Problem(403, "RAW_EXPORT_AUTHORITY_CHANGED")
    if (not job.expires or job.expires > frozen["expires_at"] or job.expires <= now()
        or frozen["expires_at"] > min(job.accepted+86400, job.accepted+authorization["max_export_lifetime_seconds"], authorization["expires_at"])):
        raise Problem(410, "EXPORT_EXPIRED")
    sources = frozen.get("sources")
    if (not isinstance(sources, list) or not 0 < len(sources) <= MAX_RAW_FILES
        or [source["artifact_id"] for source in sources] != sorted(frozen["scope"]["artifact_ids"])):
        raise Problem(403, "RAW_EXPORT_INTEGRITY_FAILURE")
    for original in sources:
        current = source_descriptor(db, account, authorization, original["artifact_id"], job.body["session_ids"])
        if current != original or job.expires > current["retained_until"]:
            raise Problem(403, "RAW_EXPORT_SOURCE_CHANGED")
    return frozen


def archive_bytes(job):
    return job.body["raw_export"]["authorization"]["max_archive_bytes"] if job.body.get("include_raw") else STRUCTURED_ARCHIVE


def raw_manifest(frozen):
    """Only archive members carry exact source versions; API never exposes keys."""
    authorization = frozen["authorization"]
    return {"schema_version": "1.0.0", "frozen_sha256": frozen["frozen_sha256"],
        "authorization_id": authorization["authorization_id"], "authorization_version": authorization["version"],
        "authorization_sha256": digest(authorization), "study_id": authorization["study_id"],
        "purpose": authorization["purpose"], "purpose_id": authorization["purpose_id"],
        "acknowledged_at": frozen["scope"]["acknowledged_at"], "export_notice_version": authorization["export_notice_version"],
        "export_notice_sha256": authorization["export_notice_sha256"],
        "sources": [{key: value for key, value in source.items() if key not in ("bucket", "key", "retention_authority_sha256")}
            | {"path": f'raw/{source["kind"]}/{source["artifact_id"]}.bin'} for source in frozen["sources"]]}


def public_job_scope(job):
    if (job.body.get("include_raw") and job.state in ("pending", "running", "completed")
        and job.expires and job.expires > now()):
        return raw_manifest(job.body["raw_export"])
    return None


def read_sources(claim, session_factory, current_claim, s3=None):
    """Read bounded immutable bytes outside account transactions, with fences."""
    from .storage import client
    s3 = s3 or client("s3")
    with session_factory.begin() as db:
        account, job = current_claim(db, claim)
        frozen = validate_job(db, account, job)
    if frozen is None:
        return {}, None
    files = {}
    for source in frozen["sources"]:
        with session_factory.begin() as db:
            account, job = current_claim(db, claim)
            if validate_job(db, account, job) != frozen:
                raise Problem(403, "RAW_EXPORT_AUTHORITY_CHANGED")
        response = s3.get_object(Bucket=source["bucket"], Key=source["key"], VersionId=source["version_id"])
        stream = response["Body"]
        try:
            if (response.get("VersionId") != source["version_id"] or response.get("ContentLength") != source["size_bytes"]
                or response.get("ContentType") != source["media_type"]):
                raise Problem(503, "RAW_EXPORT_SOURCE_INVALID")
            data = stream.read(source["size_bytes"]+1)
            if len(data) != source["size_bytes"] or hashlib.sha256(data).hexdigest() != source["sha256"]:
                raise Problem(503, "RAW_EXPORT_SOURCE_INVALID")
        finally:
            stream.close()
        with session_factory.begin() as db:
            account, job = current_claim(db, claim)
            if validate_job(db, account, job) != frozen:
                raise Problem(403, "RAW_EXPORT_AUTHORITY_CHANGED")
        files[f'raw/{source["kind"]}/{source["artifact_id"]}.bin'] = data
    return files, raw_manifest(frozen)


def validate_output(db, account, job, output):
    frozen = validate_job(db, account, job)
    if frozen is None:
        return
    manifest = output.get("manifest", {}) if isinstance(output, dict) else {}
    entries = manifest.get("files", [])
    expected = {f'raw/{source["kind"]}/{source["artifact_id"]}.bin':
        {"path": f'raw/{source["kind"]}/{source["artifact_id"]}.bin', "sha256": source["sha256"], "size_bytes": source["size_bytes"]}
        for source in frozen["sources"]}
    if (not isinstance(output, dict) or manifest.get("raw_export") != raw_manifest(frozen)
        or manifest.get("job_id") != job.id or manifest.get("selection") != job.body["selection"]
        or manifest.get("session_ids") != job.body["session_ids"] or manifest.get("expires_at") != iso(job.expires)
        or output.get("key") != f"exports/{job.account_id}/{job.generation}/{job.id}/{job.fence}.zip"
        or not output.get("version_id") or output["version_id"] == "null"
        or not 0 < output.get("size_bytes", MAX_ARCHIVE+1) <= frozen["authorization"]["max_archive_bytes"]
        or not isinstance(entries, list) or len({entry["path"] for entry in entries}) != len(entries)
        or sum(entry["size_bytes"] for entry in entries) > frozen["authorization"]["max_uncompressed_bytes"]
        or {entry["path"]: entry for entry in entries if entry["path"].startswith("raw/")} != expected):
        raise Problem(403, "RAW_EXPORT_INTEGRITY_FAILURE")


def available_scopes(db, account, study_id=None, authorization_id=None, artifact_cursor=None, authorization_cursor=None):
    """Current participant-only choices; never returns arbitrary bucket/key/URL."""
    if (artifact_cursor and not authorization_id) or (authorization_cursor and authorization_id):
        raise Problem(422, "RAW_EXPORT_CURSOR_MISMATCH")
    query = select(RegistryVersion).where(RegistryVersion.kind == "raw_export", RegistryVersion.state == "active",
        RegistryVersion.body["account_ref"].as_string() == account.id,
        cast(RegistryVersion.body["data_generation"].as_string(), BigInteger) == account.generation)
    if authorization_id:
        query = query.where(RegistryVersion.registry_key == "raw_export:"+authorization_id)
    if study_id:
        query = query.where(RegistryVersion.body["study_id"].as_string() == study_id)
    if authorization_cursor:
        query = query.where(RegistryVersion.id > authorization_cursor)
    rows = list(db.scalars(query.order_by(RegistryVersion.id).limit(MAX_SCOPE_PAGE+1)))
    scopes = []
    for row in rows[:MAX_SCOPE_PAGE]:
        grant = row.body
        if study_id and grant["study_id"] != study_id:
            continue
        scope = {"authorization_id": grant["authorization_id"], "authorization_version": grant["version"],
            "authorization_sha256": row.sha256, "export_notice_version": grant["export_notice_version"],
            "export_notice_sha256": grant["export_notice_sha256"], "confirmed": True,
            "acknowledged_at": iso(), "artifact_ids": ["00000000-0000-4000-8000-000000000001"]}
        try:
            current_authorization(db, account, scope)
        except Problem:
            continue
        query = select(Artifact).where(Artifact.account_id == account.id, Artifact.generation == account.generation,
            Artifact.state == "verified", Artifact.kind.in_(grant["raw_kinds"]))
        if artifact_cursor:
            query = query.where(Artifact.id > artifact_cursor)
        candidates = list(db.scalars(query.order_by(Artifact.id).limit(MAX_RAW_FILES+1)))
        artifacts = []
        for artifact in candidates[:MAX_RAW_FILES]:
            try:
                source = source_descriptor(db, account, grant, artifact.id, [artifact.session_id])
            except Problem:
                continue
            # A individually over-budget source is not selectable; selecting it
            # cannot produce an archive within this independently approved cap.
            if source["size_bytes"] > grant["max_uncompressed_bytes"]:
                continue
            artifacts.append({key: source[key] for key in ("artifact_id", "session_id", "kind", "size_bytes", "media_type")}
                | {"retained_until": iso(source["retained_until"])})
        scopes.append({"authorization_id": grant["authorization_id"], "authorization_version": grant["version"],
            "authorization_sha256": row.sha256, "study_id": grant["study_id"], "purpose_id": grant["purpose_id"],
            "purpose_text": grant["purpose_text"], "expires_at": iso(grant["expires_at"]),
            "max_export_lifetime_seconds": grant["max_export_lifetime_seconds"], "max_uncompressed_bytes": grant["max_uncompressed_bytes"],
            "max_archive_bytes": grant["max_archive_bytes"], "raw_kinds": grant["raw_kinds"],
            "export_notice": {"version": grant["export_notice_version"], "sha256": grant["export_notice_sha256"], "content": grant["export_notice_text"]},
            "artifacts": artifacts, "artifacts_next_cursor": candidates[MAX_RAW_FILES-1].id if len(candidates)>MAX_RAW_FILES else None})
    response = {"schema_version": "1.0.0", "scopes": scopes,
        "next_cursor": rows[MAX_SCOPE_PAGE-1].id if len(rows)>MAX_SCOPE_PAGE else None}
    if len(canonical(response)) > 512 * 1024:
        raise Problem(503, "RAW_EXPORT_SCOPE_RESPONSE_INVALID")
    return response


def cleanup_once(session_factory, s3, *, tick=None):
    """Repeated prefix erasure closes late fence arrivals after authority loss."""
    tick = now() if tick is None else tick
    with session_factory.begin() as db:
        jobs = list(db.scalars(select(Job).where(Job.kind == "export", Job.body["include_raw"].as_boolean().is_(True),
            Job.cleanup_next_at <= tick).order_by(Job.cleanup_next_at, Job.id).limit(100)))
        ids = [job.id for job in jobs]
    purges = []
    failures = 0
    for id in ids:
        with session_factory.begin() as db:
            hint = db.get(Job, id)
            account = db.scalar(select(Account).where(Account.id == hint.account_id).with_for_update())
            job = db.scalar(select(Job).where(Job.id == id).with_for_update().execution_options(populate_existing=True))
            job.cleanup_next_at = tick+900
            try:
                validate_job(db, account, job)
                if job.state not in ("failed", "expired", "revoked"):
                    continue
            except Problem as error:
                job.failure = error.code
            # Cancel the fence before external cleanup; no new delivery can pass.
            job.state = "revoked" if job.expires and job.expires > tick else "expired"
            job.fence += 1
            job.lease_until = None
            job.output = None
            purges.append((job.id, job.account_id, job.generation))
    for id, owner, generation in purges:
        try:
            delete_versions_for_prefix(s3, f"exports/{owner}/{generation}/{id}/")
            with session_factory.begin() as db:
                job = db.get(Job, id)
                if job:
                    job.cleanup_last_success = tick
        except Exception:
            failures += 1
    return {"processed": len(ids), "purged": len(purges)-failures, "failures": failures}


def delete_versions_for_prefix(s3, prefix):
    """Storage helper uses a passed client so cleanup tests prove exact calls."""
    from .config import settings
    bucket = settings().export_bucket
    from .replica_cleanup import prepare_delete
    versions = []
    replica_rows = []
    for page in s3.get_paginator("list_object_versions").paginate(Bucket=bucket, Prefix=prefix):
        for item in page.get("Versions", [])+page.get("DeleteMarkers", []):
            version = item.get("VersionId")
            if not item["Key"].startswith(prefix) or not version or version == "null":
                raise Problem(503, "RAW_EXPORT_CLEANUP_INVALID")
            versions.append((item["Key"], version))
            replica_rows.append({"Key": item["Key"], "VersionId": version,
                "DeleteMarker": item in page.get("DeleteMarkers", [])})
            if len(versions) > 10000:
                raise Problem(503, "RAW_EXPORT_CLEANUP_LIMIT")
    prepare_delete(s3, bucket, prefix, replica_rows)
    for key, version in versions:
        s3.delete_object(Bucket=bucket, Key=key, VersionId=version)
    for page in s3.get_paginator("list_object_versions").paginate(Bucket=bucket, Prefix=prefix):
        if page.get("Versions") or page.get("DeleteMarkers"):
            raise Problem(503, "RAW_EXPORT_CLEANUP_PENDING")
