"""Owner-scoped versioned API. No endpoint executes an intoxication model."""

from __future__ import annotations

import base64
import hashlib
import re
import secrets
import threading
from contextlib import contextmanager
from datetime import datetime
from uuid import UUID as PyUUID

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jsonschema.exceptions import ValidationError as SchemaError
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError

from . import storage
from .auth import authenticate, family_hash, recent
from .canonical import canonical, digest, strict_loads
from .config import settings, web_origins
from .db import (
    Artifact,
    Audit,
    Check,
    Dedup,
    Job,
    Outbox,
    RateBucket,
    Record,
    Registry,
    Revocation,
    SystemState,
    factory,
    iso,
    now,
    uid,
)
from .domain import (
    NOTICE,
    NOTICE_SHA,
    NOTICE_VERSION,
    ROOT,
    Problem,
    check_scientific_snapshot,
    if_match,
    notice,
    owned_check,
    qualification,
    record,
    registry,
    require_draft,
    safe_result,
    save_record,
    validate_component,
    validate_measurement,
    verify_evidence,
    verify_signature,
)
from .dto import (
    UUID,
    Acknowledgment,
    Alcohol,
    ArtifactRequest,
    Attestation,
    BindChallenge,
    Binding,
    CaptureAttempt,
    CaptureAuthorization,
    CaptureContext,
    CompleteArtifact,
    Confirm,
    Consent,
    CreateCheck,
    DeleteRequest,
    EvidenceManifest,
    ExportRequest,
    Finalize,
    LabImport,
    Name,
    ProfileWrite,
    ReplacementLinks,
    StartAuthorization,
    Withdrawal,
)
from .errors import response_problem
from .replacement_links import replacement_links_view
from .report_revisions import router as report_revision_router

app = FastAPI(
    title="One-The-Go Detection",
    version="1.0.0",
    docs_url="/docs" if settings().environment in ("local", "test") else None,
    redoc_url=None,
)
capacity = threading.BoundedSemaphore(100)


@app.middleware("http")
async def boundary(request, call_next):
    request.state.request_id = uid()
    if not capacity.acquire(blocking=False):
        return response_problem(
            Problem(429, "LIMIT_EXCEEDED", headers={"Retry-After": "1"}),
            request.state.request_id,
        )
    try:
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            raw = bytearray()
            async for chunk in request.stream():
                raw.extend(chunk)
                if len(raw) > 1024 * 1024:
                    raise Problem(413, "LIMIT_EXCEEDED")
            request._body = bytes(raw)
            if raw:
                if (
                    request.headers.get("content-type", "").split(";")[0]
                    != "application/json"
                ):
                    raise Problem(415, "JSON_REQUIRED")
                try:
                    request.state.json_value = strict_loads(raw.decode("utf-8"))
                except (ValueError, UnicodeError):
                    raise Problem(422, "VALIDATION_FAILED") from None
            else:
                request.state.json_value = {}
        response = await call_next(request)
        response.headers["X-Request-Id"] = request.state.request_id
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response
    except Problem as e:
        return response_problem(e, request.state.request_id)
    finally:
        capacity.release()


@app.exception_handler(Problem)
async def problem_handler(request, exc):
    return response_problem(exc, request.state.request_id)


@app.exception_handler(RequestValidationError)
@app.exception_handler(PydanticValidationError)
async def validation_handler(request, exc):
    # Report field locations and stable codes, never Pydantic input/context values.
    fields = {}
    for error in exc.errors()[:32]:
        parts = [str(p) for p in error.get("loc", ()) if p != "body"]
        path = ".".join(
            p if re.fullmatch(r"[A-Za-z0-9_]{1,64}", p) else "field" for p in parts
        )
        fields[path or "body"] = error.get("type", "invalid")[:80]
    return JSONResponse(
        {
            "code": "VALIDATION_FAILED",
            "message": "Review the marked fields.",
            "request_id": request.state.request_id,
            "retryable": False,
            "field_errors": fields,
        },
        status_code=422,
        headers={"Cache-Control": "no-store"},
    )


@app.exception_handler(SchemaError)
@app.exception_handler(ValueError)
async def domain_validation(request, exc):
    return response_problem(Problem(422, "VALIDATION_FAILED"), request.state.request_id)


@app.exception_handler(SQLAlchemyError)
@app.exception_handler(BotoCoreError)
@app.exception_handler(ClientError)
async def dependency_handler(request, exc):
    return response_problem(
        Problem(503, "SERVICE_UNAVAILABLE", retryable=True), request.state.request_id
    )


def enforce_rate(db, account, request):
    privacy = (
        "/privacy/" in request.url.path
        or request.url.path.endswith("/withdrawals")
        or request.url.path.endswith("/logout")
    )
    kind = "privacy" if privacy else ("read" if request.method == "GET" else "write")
    rate, burst = (30, 10) if privacy else ((120, 40) if kind == "read" else (60, 20))
    key = account.id + ":" + kind
    row = db.get(RateBucket, key)
    current = now()
    if row is None:
        row = RateBucket(id=key, tokens=burst, updated=current)
        db.add(row)
    row.tokens = min(burst, row.tokens + max(0, current - row.updated) * rate / 60)
    row.updated = current
    if row.tokens < 1:
        db.commit()
        raise Problem(
            429,
            "LIMIT_EXCEEDED",
            headers={"Retry-After": str(max(1, min(3600, int(60 / rate) + 1)))},
        )
    row.tokens -= 1


@contextmanager
def access(request, receipt=False, allow_inactive=False):
    with factory()() as db:
        account, claims, revoked = authenticate(
            db, request.headers.get("authorization"), receipt
        )
        enforce_rate(db, account, request)
        db.commit()  # Rate cost persists even for rejected downstream writes.
        try:
            account, claims, revoked = authenticate(
                db, request.headers.get("authorization"), receipt
            )
            if account.state != "active" and not allow_inactive:
                raise Problem(403, "ACCOUNT_NOT_WRITABLE")
            yield db, account, claims, revoked
            db.commit()
        except Exception:
            db.rollback()
            raise


def generation(request):
    raw = request.headers.get("x-data-generation", "")
    if not raw.isdigit() or not 0 < int(raw) <= 9007199254740991:
        raise Problem(422, "DATA_GENERATION_REQUIRED")
    return int(raw)


def operation(
    request,
    db,
    account,
    claims,
    revoked=False,
    escape_notice=False,
    allow_generation_ack=False,
):
    gen = generation(request)
    key = request.headers.get("idempotency-key", "")
    if not 1 <= len(key) <= 128 or any(ord(c) < 33 or ord(c) > 126 for c in key):
        raise Problem(422, "IDEMPOTENCY_KEY_REQUIRED")
    route = request.url.path
    family = claims["origin_jti"] if route == "/v1/auth/logout" else ""
    identity = digest([account.id, request.method, route, gen, key, family])
    bodyhash = digest(request.state.json_value)
    existing = db.get(Dedup, identity)
    exception = (
        route in ("/v1/auth/logout", "/v1/privacy/deletion-requests")
        and existing is not None
    )
    if exception:
        if existing.digest != bodyhash or existing.family != claims["origin_jti"]:
            raise Problem(409, "IDEMPOTENCY_CONFLICT")
        return existing, True
    if revoked:
        raise Problem(401, "AUTH_REQUIRED")
    if gen != account.generation and route != "/v1/auth/logout":
        raise Problem(410, "DATA_GENERATION_RETIRED")
    if account.state != "active" and route != "/v1/auth/logout" and not (
        allow_generation_ack and account.state == "awaiting_generation_ack"
    ):
        raise Problem(403, "ACCOUNT_NOT_WRITABLE")
    if existing:
        if existing.digest != bodyhash:
            raise Problem(409, "IDEMPOTENCY_CONFLICT")
        if existing.body is None:
            raise Problem(410, "DATA_GENERATION_RETIRED")
        return existing, True
    if not escape_notice:
        config = settings()
        if config.maintenance:
            raise Problem(
                503,
                "SERVICE_MAINTENANCE",
                retryable=True,
                headers={"Retry-After": "60"},
            )
        version = request.headers.get("x-app-version")
        if version is not None or config.environment in ("qa", "prod"):
            if (
                not version
                or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version)
                or version not in config.supported_app_versions
                or tuple(map(int, version.split(".")))
                < tuple(map(int, config.minimum_app_version.split(".")))
            ):
                raise Problem(
                    426, "UPDATE_REQUIRED", "Update required for synchronization."
                )
    if not escape_notice and account.notice != NOTICE_SHA:
        raise Problem(403, "NOTICE_ACKNOWLEDGMENT_REQUIRED")
    entry = Dedup(
        id=identity,
        account_id=account.id,
        generation=gen,
        digest=bodyhash,
        route=route,
        family=claims["origin_jti"],
        status=200,
        body=None,
        headers={},
    )
    db.add(entry)
    db.add(
        Audit(
            account_id=account.id,
            generation=gen,
            action=request.method + " " + route,
            request_id=request.state.request_id,
        )
    )
    return entry, False


def answer(entry, body=None, status=200, headers=None, operation_id=None):
    if body is not None:
        entry.body = body
        entry.status = status
        entry.headers = headers or {}
        entry.operation_id = operation_id
    return JSONResponse(entry.body, status_code=entry.status, headers=entry.headers)


def mutate(request, handler, escape=False, ack=False):
    with access(request, allow_inactive=True) as (db, a, c, r):
        entry, replay = operation(request, db, a, c, r, escape, ack)
        if replay:
            if entry.operation_id:
                job = db.get(Job, entry.operation_id)
                if job and job.kind == "export":
                    return JSONResponse(job_view(job), status_code=entry.status)
            return answer(entry)
        body, status, headers, opid = handler(db, a, c)
        return answer(entry, body, status, headers, opid)


def detail(check, include=True):
    data = {
        "session_id": check.id,
        "state": check.state,
        "revision": check.revision,
        "mode": check.mode,
        "created_at": check.snapshot["created_at"]
        if check.snapshot
        else iso(check.created),
        "snapshot_sha256": check.snapshot_sha256,
        "evidence_sha256": check.evidence_sha256,
        "result": safe_result(check.result),
    }
    if include:
        data["snapshot"] = check.snapshot
    return data


def evidence(db, a, check):
    rows = list(
        db.scalars(
            select(Record).where(
                Record.account_id == a.id,
                Record.generation == a.generation,
                Record.parent_id == check.id,
                Record.kind.in_(["context", "manifest", "attempt", "alcohol"]),
            )
        )
    )
    result = {
        "context": None,
        "manifest": None,
        "attempts": [],
        "alcohol": None,
        "raw_artifacts_omitted_reason": "NO_RAW_EXPORT_SCOPE",
    }
    for row in rows:
        if row.kind == "attempt":
            result["attempts"].append(row.body)
        else:
            result[row.kind] = row.body
    return result


def job_view(job):
    state = (
        "expired"
        if job.kind == "export" and job.expires and job.expires <= now()
        else job.state
    )
    result = {
        "schema_version": "1.0.0",
        "job_id": job.id,
        "kind": job.kind,
        "state": state,
        "scope": job.body.get("scope", job.body.get("selection")),
        "data_generation": job.generation,
        "accepted_at": iso(job.accepted),
        "started_at": iso(job.started) if job.started else None,
        "completed_at": iso(job.completed) if job.completed else None,
        "expires_at": iso(job.expires) if job.expires else None,
        "failure_code": job.failure,
        "retained_categories": [
            "identity_and_generation_barriers",
            "audit_and_security_metadata",
            "minimal_operation_receipts",
            "operator_membership_references",
            "private_cleanup_references",
            "deletion_journal",
        ] if job.kind == "deletion" else [],
        "policy_version": "privacy-v1",
        "attempt_count": job.attempts,
        "allowed_actions": ["refresh"] if state in ("pending", "running") else [],
    }
    if job.kind == "export" and state == "completed":
        result.update(
            download_path=f"/v1/privacy/jobs/{job.id}/download",
            download_metadata_expires_at=iso(min(now() + 300, job.expires)),
            sha256=job.output["sha256"],
            size_bytes=job.output["size_bytes"],
            manifest_sha256=digest(job.output["manifest"]),
        )
    return result


@app.get("/health/live")
def live():
    return {"status": "alive"}


@app.get("/health/ready")
def ready():
    with factory()() as db:
        from .identity_keys import require_key
        require_key(db)
        version = db.get(SystemState, "schema_version")
        recovery = db.get(SystemState, "recovery")
        if not version or version.body.get("version") != 1:
            raise Problem(503, "MIGRATION_REQUIRED")
        if settings().recovery_required and (
            not recovery or not recovery.body.get("verified")
        ):
            raise Problem(503, "RECOVERY_NOT_VERIFIED")
        db.execute(text("SELECT 1"))
    return {"status": "ready", "inference_available": False}


@app.get("/v1/app-config")
def app_config():
    s = settings()
    origin = s.identity_origin.rstrip("/")
    return {
        "schema_version": "1.0.0",
        "environment": s.environment,
        "maintenance": s.maintenance,
        "minimum_app_version": s.minimum_app_version,
        "supported_app_versions": s.supported_app_versions,
        "contract_versions": {
            "application": ["1.0.0"],
            "scientific": ["0.1.0"],
            "capture_evidence": ["1.0.0"],
            "native_task": ["1.0.0"],
        },
        "inference_available": False,
        "notice": notice(),
        "auth": {
            "issuer": s.issuer,
            "client_id": s.client_id,
            "authorization_endpoint": origin + "/oauth2/authorize",
            "token_endpoint": origin + "/oauth2/token",
            "revocation_endpoint": origin + "/oauth2/revoke",
            "logout_endpoint": origin + "/logout",
            "redirect_uris": s.oauth_redirect_uris,
        },
        "limits": {
            "request_bytes": 1048576,
            "attempt_bytes": 524288,
            "export_sessions": 500,
        },
    }


@app.get("/v1/notices/{version}")
def get_notice(version: str):
    if version != NOTICE_VERSION:
        raise Problem(404, "NOT_FOUND")
    return {
        "version": version,
        "locale": "en",
        "content_type": "text/plain",
        "text": NOTICE,
        "sha256": NOTICE_SHA,
        "mandatory": True,
    }


@app.get("/v1/me/capabilities")
def capabilities(request: Request):
    with access(request, allow_inactive=True) as (db, a, c, r):
        return {
            "account_ref": a.id,
            "data_generation": a.generation,
            "account_state": a.state,
            "server_time": iso(),
            "notice": {**notice(), "acknowledged": a.notice == NOTICE_SHA},
            "inference_available": False,
            "channels": {
                k: {"available": False, "reason_codes": ["NO_QUALIFIED_CONFIGURATION"]}
                for k in ["saliva", "eyes", "cardiac", "ecg", "alcohol"]
            },
            "studies": [
                x.body
                for x in db.scalars(
                    select(Record).where(
                        Record.account_id == a.id,
                        Record.generation == a.generation,
                        Record.kind == "consent",
                    )
                )
            ],
        }


@app.post("/v1/me/acknowledgments")
def acknowledge(request: Request, body: Acknowledgment):
    def action(db, a, c):
        if body.version != NOTICE_VERSION or body.sha256 != NOTICE_SHA:
            raise Problem(409, "NOTICE_VERSION_CONFLICT")
        a.notice = body.sha256
        return (
            {"version": body.version, "sha256": body.sha256, "accepted_at": iso()},
            200,
            {},
            None,
        )

    return mutate(request, action, escape=True)


@app.get("/v1/me/profile")
def profile_get(request: Request):
    with access(request) as (db, a, c, r):
        row = record(db, a, "profile", "current")
        data = (
            {
                "profile_version_id": None,
                "revision": 0,
                "profile": None,
                "history": None,
                "context": None,
            }
            if not row
            else {**row.body, "revision": row.revision}
        )
        return JSONResponse(data, headers={"ETag": f'"{row.revision if row else 0}"'})


@app.patch("/v1/me/profile")
def profile_patch(request: Request, body: ProfileWrite):
    def action(db, a, c):
        row = record(db, a, "profile", "current")
        rev = row.revision if row else 0
        if_match(request, rev)
        if body.profile.source == "study_measurement":
            raise Problem(403, "CAPABILITY_DENIED")
        if body.profile.source == "synthetic" and settings().environment == "prod":
            raise Problem(403, "SYNTHETIC_CLOUD_UNAVAILABLE")
        data = {**body.data(), "profile_version_id": uid()}
        save_record(db, a, "profile_version", data["profile_version_id"], data)
        if row:
            row.body = data
            row.sha256 = digest(data)
            row.revision += 1
        else:
            row = save_record(db, a, "profile", "current", data)
        return {**data, "revision": rev + 1}, 200, {"ETag": f'"{rev + 1}"'}, None

    return mutate(request, action)


@app.post("/v1/auth/logout")
def logout(request: Request):
    with access(request, receipt=True, allow_inactive=True) as (db, a, c, r):
        entry, replay = operation(request, db, a, c, r, True)
        if replay:
            return answer(entry)
        if request.state.json_value != {}:
            raise Problem(422, "INVALID_LOGOUT_REQUEST")
        db.add(Revocation(id=family_hash(a.id, c["origin_jti"]), account_id=a.id))
        return answer(
            entry,
            {"state": "accepted", "remote_family_revoked": True, "accepted_at": iso()},
        )


@app.post("/v1/me/data-generation/acknowledgments")
def generation_ack(request: Request, body: Confirm):
    def action(db, a, c):
        if a.state != "awaiting_generation_ack":
            raise Problem(409, "STATE_CONFLICT")
        a.state = "active"
        a.notice = None
        return (
            {
                "account_ref": a.id,
                "data_generation": a.generation,
                "account_state": a.state,
            },
            200,
            {},
            None,
        )

    return mutate(request, action, escape=True, ack=True)


@app.post("/v1/sessions", status_code=201)
def session_create(request: Request, body: CreateCheck):
    def action(db, a, c):
        if db.get(Check, body.session_id):
            raise Problem(409, "SESSION_ID_CONFLICT")
        if body.mode == "synthetic" and settings().environment == "prod":
            raise Problem(403, "SYNTHETIC_CLOUD_UNAVAILABLE")
        if body.mode == "controlled_research":
            registry(db, "study", body.study_id or "")
            consent = record(db, a, "consent", body.study_id or "")
            if not consent or consent.body.get("state") != "active":
                raise Problem(403, "CAPABILITY_DENIED")
        if body.supersedes_session_id:
            owned_check(db, a, body.supersedes_session_id)
        row = Check(
            id=body.session_id,
            account_id=a.id,
            generation=a.generation,
            mode=body.mode,
            study_id=body.study_id,
            protocol_id=body.protocol_id,
            supersedes_id=body.supersedes_session_id,
        )
        db.add(row)
        return (
            {"session_id": row.id, "state": "draft", "revision": 1},
            201,
            {"ETag": '"1"'},
            None,
        )

    return mutate(request, action)


@app.get("/v1/sessions")
def session_list(request: Request, cursor: str | None = None, limit: int = 20):
    if not 1 <= limit <= 100:
        raise Problem(422, "VALIDATION_FAILED")
    with access(request) as (db, a, c, r):
        query = select(Check).where(
            Check.account_id == a.id, Check.generation == a.generation
        )
        if cursor:
            try:
                d = strict_loads(
                    base64.urlsafe_b64decode(cursor + "=" * ((4 - len(cursor) % 4) % 4))
                )
                if set(d) != {"id", "created"}:
                    raise ValueError()
                PyUUID(d["id"])
                created = float(d["created"])
            except Exception:
                raise Problem(422, "INVALID_CURSOR") from None
            query = query.where(
                (Check.created < created)
                | ((Check.created == created) & (Check.id < d["id"]))
            )
        rows = list(
            db.scalars(
                query.order_by(Check.created.desc(), Check.id.desc()).limit(limit + 1)
            )
        )
        more = len(rows) > limit
        rows = rows[:limit]
        next_cursor = (
            base64.urlsafe_b64encode(
                canonical({"id": rows[-1].id, "created": rows[-1].created})
            )
            .decode()
            .rstrip("=")
            if more
            else None
        )
        return {
            "items": [detail(row, False) for row in rows],
            "next_cursor": next_cursor,
        }


@app.get("/v1/sessions/{session_id}")
def session_get(request: Request, session_id: UUID):
    with access(request) as (db, a, c, r):
        row = owned_check(db, a, session_id)
        return JSONResponse(
            {**detail(row), **evidence(db, a, row)},
            headers={"ETag": f'"{row.revision}"'},
        )


@app.put("/v1/sessions/{session_id}/snapshot")
def snapshot_put(request: Request, session_id: UUID, body: dict):
    def action(db, a, c):
        row = owned_check(db, a, session_id)
        require_draft(row)
        if_match(request, row.revision)
        check_scientific_snapshot(body, a, row)
        row.snapshot = body
        row.snapshot_sha256 = digest(body)
        row.revision += 1
        return (
            {
                "session_id": row.id,
                "revision": row.revision,
                "snapshot_sha256": row.snapshot_sha256,
            },
            200,
            {"ETag": f'"{row.revision}"'},
            None,
        )

    return mutate(request, action)


@app.get("/v1/sessions/{session_id}/replacement-links", response_model=ReplacementLinks)
def session_replacement_links(
    request: Request, session_id: UUID, cursor: str | None = None, limit: int = 20
):
    with access(request) as (db, a, c, r):
        base = owned_check(db, a, session_id)
        return replacement_links_view(db, a, base, cursor, limit)


def evidence_write(request, session_id, kind, key, data):
    def action(db, a, c):
        check = owned_check(db, a, session_id)
        require_draft(check)
        if data["session_id"] != session_id:
            raise Problem(422, "SESSION_MISMATCH")
        old = record(db, a, kind, key)
        if_match(request, old.revision if old else 0)
        if old and kind == "context":
            raise Problem(409, "IMMUTABLE_CONTEXT")
        if kind == "attempt":
            if data["attempt_id"] != key:
                raise Problem(422, "ATTEMPT_MISMATCH")
            validate_component(data)
            if old:
                if old.body["status"] != "started" or data["status"] == "started":
                    raise Problem(409, "IMMUTABLE_ATTEMPT")
                for field in (
                    "session_id",
                    "attempt_id",
                    "component",
                    "record_id",
                    "source",
                    "started_at",
                    "configuration_id",
                    "configuration_hash",
                    "supersedes_attempt_id",
                ):
                    if old.body[field] != data[field]:
                        raise Problem(409, "ATTEMPT_IDENTITY_CONFLICT")
                if data["component"] == "cardiac" and old.body[
                    "component_metadata"
                ].get("modality") != data["component_metadata"].get("modality"):
                    raise Problem(409, "ATTEMPT_IDENTITY_CONFLICT")
            count = db.scalar(
                select(func.count())
                .select_from(Record)
                .where(
                    Record.account_id == a.id,
                    Record.generation == a.generation,
                    Record.parent_id == session_id,
                    Record.kind == "attempt",
                )
            )
            if not old and count >= 128:
                raise Problem(413, "LIMIT_EXCEEDED")
            if data["component"] in ("task", "cardiac") and data["status"] in (
                "started",
                "valid",
            ):
                for attempt in db.scalars(
                    select(Record).where(
                        Record.account_id == a.id,
                        Record.generation == a.generation,
                        Record.parent_id == session_id,
                        Record.kind == "attempt",
                    )
                ):
                    if (
                        attempt.body["component"] == data["component"]
                        and attempt.body["status"] == "valid"
                    ):
                        if data["component"] == "task":
                            raise Problem(409, "VALID_TASK_ALREADY_EXISTS")

                        def modality(body):
                            metadata = body["component_metadata"]
                            return metadata.get("modality") or metadata.get(
                                "projection", {}
                            ).get("modality")

                        if modality(data) == modality(attempt.body):
                            raise Problem(409, "VALID_CARDIAC_MODALITY_ALREADY_EXISTS")
        if old:
            old.body = data
            old.sha256 = digest(data)
            old.revision += 1
            row = old
        else:
            row = save_record(db, a, kind, key, data, session_id)
        return (
            {"record_id": key, "revision": row.revision, "sha256": row.sha256},
            200,
            {"ETag": f'"{row.revision}"'},
            None,
        )

    return mutate(request, action)


@app.put("/v1/sessions/{session_id}/context")
def context_put(request: Request, session_id: UUID, body: CaptureContext):
    return evidence_write(
        request, session_id, "context", session_id, request.state.json_value
    )


@app.put("/v1/sessions/{session_id}/attempts/{attempt_id}")
def attempt_put(
    request: Request, session_id: UUID, attempt_id: UUID, body: CaptureAttempt
):
    return evidence_write(request, session_id, "attempt", attempt_id, body.data())


@app.put("/v1/sessions/{session_id}/evidence-manifest")
def manifest_put(request: Request, session_id: UUID, body: EvidenceManifest):
    return evidence_write(
        request, session_id, "manifest", session_id, request.state.json_value
    )


@app.get("/v1/sessions/{session_id}/evidence")
def evidence_get(request: Request, session_id: UUID):
    with access(request) as (db, a, c, r):
        return evidence(db, a, owned_check(db, a, session_id))


@app.post("/v1/sessions/{session_id}/finalize", status_code=202)
def finalize(request: Request, session_id: UUID, body: Finalize):
    def action(db, a, c):
        row = owned_check(db, a, session_id)
        require_draft(row)
        if_match(request, row.revision)
        context, manifest = verify_evidence(db, a, row)
        if (
            row.snapshot_sha256 != body.snapshot_sha256
            or manifest.sha256 != body.evidence_sha256
        ):
            raise Problem(422, "DIGEST_MISMATCH")
        row.evidence_sha256 = body.evidence_sha256
        row.state = "processing"
        row.revision += 1
        job = Job(
            id=uid(),
            account_id=a.id,
            generation=a.generation,
            kind="result",
            body={"session_id": row.id},
        )
        db.add(job)
        db.flush()
        db.add(Outbox(job_id=job.id))
        return (
            {
                "session_id": row.id,
                "state": "processing",
                "job_id": job.id,
                "revision": row.revision,
                "snapshot_sha256": row.snapshot_sha256,
                "evidence_sha256": row.evidence_sha256,
            },
            202,
            {"ETag": f'"{row.revision}"'},
            job.id,
        )

    return mutate(request, action)


@app.get("/v1/sessions/{session_id}/result")
def result_get(request: Request, session_id: UUID):
    with access(request) as (db, a, c, r):
        row = owned_check(db, a, session_id)
        if not row.result:
            return JSONResponse(
                {"session_id": row.id, "state": row.state},
                status_code=202,
                headers={"Retry-After": "2"},
            )
        return JSONResponse(
            safe_result(row.result), headers={"X-Evidence-Sha256": row.evidence_sha256}
        )


@app.get("/v1/me/studies")
def studies(request: Request):
    with access(request, allow_inactive=True) as (db, a, c, r):
        items = []
        for row in db.scalars(
            select(Registry).where(Registry.kind == "study", Registry.active.is_(True))
        ):
            if a.id not in row.body.get("account_refs", []):
                continue
            value = row.body
            items.append(
                {
                    k: value[k]
                    for k in (
                        "study_id",
                        "name",
                        "invitation_id",
                        "document_version",
                        "document_sha256",
                        "document_text",
                        "retention_summary",
                    )
                    if k in value
                }
                | {
                    "consent": record(db, a, "consent", value["study_id"]).body
                    if record(db, a, "consent", value["study_id"])
                    else None
                }
            )
        return {"items": items}


@app.post("/v1/studies/{study_id}/consents")
def consent(request: Request, study_id: Name, body: Consent):
    def action(db, a, c):
        recent(c)
        study = registry(db, "study", study_id)
        acknowledgment = datetime.fromisoformat(body.acknowledged_at.replace("Z", "+00:00")).timestamp()
        if acknowledgment < 0 or acknowledgment > now() + 5:
            raise Problem(422, "CONSENT_ACKNOWLEDGMENT_TIME_INVALID")
        if a.id not in study.get("account_refs", []) or any(
            getattr(body, k) != study.get(k)
            for k in ("invitation_id", "document_version", "document_sha256")
        ):
            raise Problem(403, "CAPABILITY_DENIED")
        if (
            len(study.get("document_text", "").encode()) > 65536
            or hashlib.sha256(study.get("document_text", "").encode()).hexdigest()
            != body.document_sha256
        ):
            raise Problem(403, "CONSENT_DOCUMENT_INVALID")
        existing = record(db, a, "consent", study_id)
        identity_fields = ("invitation_id", "document_version", "document_sha256")
        if existing and all(existing.body.get(k) == getattr(body, k) for k in identity_fields):
            raise Problem(409, "CONSENT_ALREADY_RECORDED")
        if existing and existing.body.get("state") == "withdrawn" and existing.body.get("invitation_id") == body.invitation_id:
            raise Problem(403, "STUDY_REINVITATION_REQUIRED")
        data = {
            **body.data(),
            "study_id": study_id,
            "consent_record_id": uid(),
            "state": "active",
            "accepted_at": iso(),
        }
        if existing:
            previous_id = existing.body["consent_record_id"]
            if not record(db, a, "consent_receipt", previous_id):
                save_record(db, a, "consent_receipt", previous_id, existing.body)
            existing.body = data
            existing.sha256 = digest(data)
            existing.revision += 1
        else:
            save_record(db, a, "consent", study_id, data)
        save_record(db, a, "consent_receipt", data["consent_record_id"], data)
        return data, 201, {}, None

    return mutate(request, action)


@app.post("/v1/studies/{study_id}/withdrawals")
def withdraw(request: Request, study_id: Name, body: Withdrawal):
    def action(db, a, c):
        row = record(db, a, "consent", study_id)
        if not row:
            raise Problem(404, "NOT_FOUND")
        row.body = {**row.body, "state": "withdrawn", "withdrawn_at": iso()}
        row.sha256 = digest(row.body)
        row.revision += 1
        return (
            {
                "study_id": study_id,
                "state": "withdrawn",
                "accepted_at": row.body["withdrawn_at"],
            },
            200,
            {},
            None,
        )

    return mutate(request, action, escape=True)


@app.get("/v1/device-bindings")
def bindings_get(request: Request):
    with access(request) as (db, a, c, r):
        items = []
        for row in db.scalars(
            select(Record).where(
                Record.account_id == a.id,
                Record.generation == a.generation,
                Record.kind == "binding",
            )
        ):
            b = row.body
            key = db.get(Registry, "device:" + b["device_id"] + ":" + b["key_id"])
            items.append(
                {
                    **b,
                    "key_active": bool(key and key.active),
                    "public_key_spki": key.body.get("public_key_spki") if key else None,
                }
            )
        return {"items": items}


@app.post("/v1/device-bindings/challenges")
def bind_challenge(request: Request, body: BindChallenge):
    def action(db, a, c):
        key = registry(db, "device", body.device_id + ":" + body.key_id)
        if a.id not in key.get("account_refs", []):
            raise Problem(403, "CAPABILITY_DENIED")
        id = uid()
        transcript = {
            "schema_version": "1.0.0",
            "challenge_id": id,
            "environment": settings().environment,
            "owner_ref": a.id,
            "data_generation": a.generation,
            "device_id": body.device_id,
            "key_id": body.key_id,
            "nonce": secrets.token_urlsafe(32),
            "expires_at": iso(now() + 300),
            "hardware_revision": key["hardware_revision"],
            "firmware_version": key["firmware_version"],
        }
        save_record(
            db,
            a,
            "challenge",
            id,
            {"transcript": transcript, "consumed": False, "expires": now() + 300},
        )
        return (
            {
                "challenge_id": id,
                "transcript": transcript,
                "signature_format": "ECDSA_P256_SHA256_DER_BASE64",
                "domain": "OTGD-BIND-v1\n",
            },
            201,
            {},
            None,
        )

    return mutate(request, action)


@app.post("/v1/device-bindings")
def bind(request: Request, body: Binding):
    def action(db, a, c):
        ch = record(db, a, "challenge", body.challenge_id)
        if not ch or ch.body["consumed"] or ch.body["expires"] <= now():
            raise Problem(409, "CHALLENGE_EXPIRED_OR_USED")
        t = ch.body["transcript"]
        key = registry(db, "device", t["device_id"] + ":" + t["key_id"])
        if a.id not in key.get("account_refs", []):
            raise Problem(403, "CAPABILITY_DENIED")
        verify_signature(key["public_key_spki"], body.signature, "OTGD-BIND-v1\n", t)
        ch.body = {**ch.body, "consumed": True}
        data = {
            "binding_id": uid(),
            "device_id": t["device_id"],
            "key_id": t["key_id"],
            "hardware_revision": t["hardware_revision"],
            "firmware_version": t["firmware_version"],
            "state": "active",
            "bound_at": iso(),
        }
        save_record(db, a, "binding", data["binding_id"], data)
        return data, 201, {}, None

    return mutate(request, action)


@app.delete("/v1/device-bindings/{binding_id}")
def unbind(request: Request, binding_id: UUID):
    def action(db, a, c):
        row = record(db, a, "binding", binding_id)
        if not row:
            raise Problem(404, "NOT_FOUND")
        row.body = {**row.body, "state": "revoked", "revoked_at": iso()}
        return {"binding_id": binding_id, "state": "revoked"}, 200, {}, None

    return mutate(request, action, escape=True)


@app.post("/v1/sessions/{session_id}/capture-authorizations")
def authorize_capture(request: Request, session_id: UUID, body: CaptureAuthorization):
    def action(db, a, c):
        check = owned_check(db, a, session_id)
        require_draft(check)
        config = qualification(
            db, a, check, body.channel, body.configuration_id, body.configuration_hash
        )
        attempt = record(db, a, "attempt", body.attempt_id)
        if (
            not attempt
            or attempt.parent_id != session_id
            or attempt.body["status"] != "started"
        ):
            raise Problem(409, "STARTED_ATTEMPT_REQUIRED")
        if body.binding_id:
            binding = record(db, a, "binding", body.binding_id)
            if (
                not binding
                or binding.body["state"] != "active"
                or binding.body["device_id"] != body.device_id
            ):
                raise Problem(403, "CAPABILITY_DENIED")
            registry(
                db, "device", binding.body["device_id"] + ":" + binding.body["key_id"]
            )
        elif body.channel not in ("task", "eyes"):
            raise Problem(403, "DEVICE_BINDING_REQUIRED")
        data = {
            **body.data(),
            "authorization_id": uid(),
            "session_id": session_id,
            "state": "issued",
            "expires_at": iso(now() + 60),
            "expires_epoch": now() + 60,
            "configuration_max_duration_ms": config["max_duration_ms"],
        }
        save_record(db, a, "authorization", data["authorization_id"], data, session_id)
        return data, 201, {}, None

    return mutate(request, action)


@app.post("/v1/sessions/{session_id}/capture-authorizations/{authorization_id}/start")
def start_capture(
    request: Request, session_id: UUID, authorization_id: UUID, body: StartAuthorization
):
    def action(db, a, c):
        check = owned_check(db, a, session_id)
        require_draft(check)
        row = record(db, a, "authorization", authorization_id)
        if not row or row.parent_id != session_id:
            raise Problem(404, "NOT_FOUND")
        v = row.body
        qualification(
            db, a, check, v["channel"], v["configuration_id"], v["configuration_hash"]
        )
        if (
            v["state"] != "issued"
            or v["expires_epoch"] <= now()
            or v["attempt_id"] != body.attempt_id
        ):
            raise Problem(409, "AUTHORIZATION_EXPIRED_OR_USED")
        row.body = {
            **v,
            "state": "started",
            "device_boot_id": body.device_boot_id,
            "server_started_at": iso(),
            "server_started_epoch": now(),
        }
        return (
            {
                "authorization_id": authorization_id,
                "attempt_id": body.attempt_id,
                "device_boot_id": body.device_boot_id,
                "state": "started",
                "server_started_at": row.body["server_started_at"],
            },
            200,
            {},
            None,
        )

    return mutate(request, action)


@app.post("/v1/sessions/{session_id}/attestations")
def attest(request: Request, session_id: UUID, body: Attestation):
    def action(db, a, c):
        check = owned_check(db, a, session_id)
        require_draft(check)
        e = body.envelope.data()
        if (
            e["owner_ref"] != a.id
            or e["data_generation"] != a.generation
            or e["environment"] != settings().environment
            or e["session_id"] != session_id
        ):
            raise Problem(403, "CAPTURE_SCOPE_MISMATCH")
        attempt = record(db, a, "attempt", e["attempt_id"])
        authorization = record(db, a, "authorization", e["authorization_id"])
        binding = record(db, a, "binding", e["binding_id"])
        if (
            not attempt
            or attempt.parent_id != session_id
            or attempt.body["status"] in ("started", "not_collected")
            or not authorization
            or not binding
        ):
            raise Problem(403, "CAPABILITY_DENIED")
        v = authorization.body
        if (
            v["state"] != "started"
            or v["attempt_id"] != e["attempt_id"]
            or v["binding_id"] != e["binding_id"]
            or v["device_boot_id"] != e["boot_id"]
            or binding.body["state"] != "active"
            or binding.body["device_id"] != e["device_id"]
            or binding.body["key_id"] != e["key_id"]
        ):
            raise Problem(403, "CAPTURE_SCOPE_MISMATCH")
        qualification(
            db, a, check, v["channel"], v["configuration_id"], e["configuration_hash"]
        )
        if (
            e["configuration_hash"] != v["configuration_hash"]
            or attempt.body["configuration_hash"] != e["configuration_hash"]
        ):
            raise Problem(403, "CONFIGURATION_MISMATCH")
        if e["payload_sha256"] != digest(body.normalized_payload) or digest(
            body.normalized_payload
        ) != digest(attempt.body["component_metadata"]["projection"]):
            raise Problem(422, "SIGNED_PAYLOAD_MISMATCH")
        key = registry(db, "device", e["device_id"] + ":" + e["key_id"])
        verify_signature(key["public_key_spki"], body.signature, "OTGD-CAPTURE-v1\n", e)
        if body.attestation_id not in attempt.body.get("attestation_refs", []):
            raise Problem(422, "ATTESTATION_REFERENCE_REQUIRED")
        replay_key = digest([e["device_id"], e["key_id"], e["boot_id"], e["sequence"]])
        if record(db, a, "sequence", replay_key):
            raise Problem(409, "DEVICE_SEQUENCE_REPLAY")
        save_record(
            db,
            a,
            "sequence",
            replay_key,
            {"attestation_id": body.attestation_id},
            session_id,
        )
        save_record(db, a, "attestation", body.attestation_id, body.data(), session_id)
        return (
            {
                "attestation_id": body.attestation_id,
                "verified": True,
                "payload_sha256": e["payload_sha256"],
            },
            201,
            {},
            None,
        )

    return mutate(request, action)


@app.post("/v1/artifact-uploads")
def artifact_upload(request: Request, body: ArtifactRequest):
    def action(db, a, c):
        from .report_revisions import ensure_artifact_capacity

        check = owned_check(db, a, body.session_id)
        require_draft(check)
        if check.study_id != body.study_id:
            raise Problem(403, "CAPABILITY_DENIED")
        channel = {
            "eye_video": "eyes",
            "ecg_waveform": "ecg",
            "source_lab_report": "saliva",
        }[body.artifact_kind]
        config = qualification(db, a, check, channel)
        consent = record(db, a, "consent", body.study_id)
        if (
            body.retention_policy_id != config["retention_policy_id"]
            or body.consent_record_id != consent.body["consent_record_id"]
            or not config.get("raw_retention_approved")
        ):
            raise Problem(403, "RAW_RETENTION_UNAVAILABLE")
        limit = (
            {"eye_video": 64, "ecg_waveform": 16, "source_lab_report": 8}[
                body.artifact_kind
            ]
            * 1024
            * 1024
        )
        media = {
            "eye_video": "video/mp4",
            "ecg_waveform": "application/octet-stream",
            "source_lab_report": "application/pdf",
        }[body.artifact_kind]
        if body.size_bytes > limit or body.media_type != media:
            raise Problem(413, "LIMIT_EXCEEDED")
        ensure_artifact_capacity(db, a.id, body.size_bytes)
        id = uid()
        row = Artifact(
            id=id,
            account_id=a.id,
            generation=a.generation,
            session_id=check.id,
            bucket=settings().artifact_bucket,
            key=f"quarantine/{a.id}/{a.generation}/{id}",
            sha256=body.sha256,
            size=body.size_bytes,
            media_type=body.media_type,
            kind=body.artifact_kind,
            expires=now() + 300,
            scope=body.data(),
        )
        db.add(row)
        ticket = storage.upload_ticket(row)
        ticket["expires_at"] = iso(row.expires)
        return ticket, 201, {}, None

    return mutate(request, action)


@app.get("/v1/artifact-uploads/{artifact_id}")
def artifact_status(request: Request, artifact_id: UUID):
    with access(request) as (db, a, c, r):
        row = db.get(Artifact, artifact_id)
        if not row or row.account_id != a.id or row.generation != a.generation:
            raise Problem(404, "NOT_FOUND")
        return {
            "artifact_id": row.id,
            "state": row.state,
            "sha256": row.sha256,
            "expires_at": iso(row.expires),
            "version_id": row.version_id,
        }


@app.post("/v1/artifact-uploads/{artifact_id}/complete")
def artifact_complete(request: Request, artifact_id: UUID, body: CompleteArtifact):
    with access(request) as (db, a, c, r):
        row = db.scalar(
            select(Artifact)
            .where(Artifact.id == artifact_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if not row or row.account_id != a.id or row.generation != a.generation:
            raise Problem(404, "NOT_FOUND")
        if row.scope.get("purpose") == "administrative_report_revision":
            raise Problem(403, "ARTIFACT_PURPOSE_MISMATCH")
        if (body.sha256, body.size_bytes, body.media_type) != (
            row.sha256,
            row.size,
            row.media_type,
        ):
            raise Problem(422, "ARTIFACT_MISMATCH")
        if row.state not in ("quarantine", "verified"):
            raise Problem(410, "ARTIFACT_RETIRED")
        detached = row
    version = (
        detached.version_id
        if detached.state == "verified"
        else storage.verify_artifact(detached)
    )

    def action(db, a, c):
        row = db.scalar(
            select(Artifact)
            .where(Artifact.id == artifact_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if not row or row.account_id != a.id or row.generation != a.generation:
            raise Problem(404, "NOT_FOUND")
        if row.scope.get("purpose") == "administrative_report_revision":
            raise Problem(403, "ARTIFACT_PURPOSE_MISMATCH")
        if row.state not in ("quarantine", "verified"):
            raise Problem(410, "ARTIFACT_RETIRED")
        if (body.sha256, body.size_bytes, body.media_type) != (
            row.sha256,
            row.size,
            row.media_type,
        ):
            raise Problem(422, "ARTIFACT_MISMATCH")
        check = owned_check(db, a, row.session_id)
        require_draft(check)
        qualification(
            db,
            a,
            check,
            {"eye_video": "eyes", "ecg_waveform": "ecg", "source_lab_report": "saliva"}[
                row.kind
            ],
        )
        if row.state == "verified" and row.version_id != version:
            raise Problem(409, "IMMUTABLE_ARTIFACT")
        row.version_id = version
        row.state = "verified"
        return (
            {
                "artifact_id": row.id,
                "state": "verified",
                "sha256": row.sha256,
                "size_bytes": row.size,
                "version_id": version,
            },
            200,
            {},
            None,
        )

    return mutate(request, action)


@app.post("/v1/research/lab-imports")
def lab_import(request: Request, body: LabImport):
    def action(db, a, c):
        check = owned_check(db, a, body.session_id)
        require_draft(check)
        qualification(db, a, check, "saliva")
        role = registry(db, "role", a.id)
        if (
            "lab_import" not in role.get("roles", [])
            or check.study_id not in role.get("study_ids", [])
            or role.get("expires_at", 0) <= now()
        ):
            raise Problem(403, "LAB_IMPORT_ROLE_REQUIRED")
        artifact = db.get(Artifact, body.source_report_artifact_id)
        if (
            not artifact
            or artifact.account_id != a.id
            or artifact.generation != a.generation
            or artifact.session_id != check.id
            or artifact.kind != "source_lab_report"
            or artifact.state != "verified"
        ):
            raise Problem(403, "VERIFIED_REPORT_REQUIRED")
        for reading in body.measurements:
            validate_measurement(reading)
            if reading["source"] != "reference_lab":
                raise Problem(422, "LAB_PROVENANCE_REQUIRED")
        id = uid()
        save_record(db, a, "lab_import", id, body.data(), check.id)
        return (
            {
                "import_id": id,
                "state": "verified_import",
                "measurements": body.measurements,
            },
            201,
            {},
            None,
        )

    return mutate(request, action)


@app.post("/v1/sessions/{session_id}/alcohol")
def alcohol_post(request: Request, session_id: UUID, body: Alcohol):
    def action(db, a, c):
        check = owned_check(db, a, session_id)
        require_draft(check)
        if body.session_id != session_id:
            raise Problem(422, "SESSION_MISMATCH")
        if (check.mode == "synthetic") != (body.source == "simulated"):
            raise Problem(422, "SYNTHETIC_PROVENANCE_REQUIRED")
        if body.source != "simulated":
            qualification(db, a, check, "alcohol")
        if record(db, a, "alcohol", session_id):
            raise Problem(409, "IMMUTABLE_ALCOHOL")
        save_record(db, a, "alcohol", session_id, body.data(), session_id)
        return body.data(), 201, {}, None

    return mutate(request, action)


@app.get("/v1/sessions/{session_id}/alcohol")
def alcohol_get(request: Request, session_id: UUID):
    with access(request) as (db, a, c, r):
        owned_check(db, a, session_id)
        row = record(db, a, "alcohol", session_id)
        if not row:
            raise Problem(404, "NOT_FOUND")
        return row.body


@app.get("/v1/model-manifests/{model_id}")
def model_get(request: Request, model_id: Name):
    with access(request) as (db, a, c, r):
        if model_id != "no-clinical-model-v1":
            raise Problem(404, "NOT_FOUND")
        from .canonical import strict_loads

        data = strict_loads(
            (ROOT / "examples/unvalidated_model_manifest.json").read_text()
        )
        data["model_id"] = model_id
        return data


@app.post("/v1/privacy/exports", status_code=202)
def export_post(request: Request, body: ExportRequest):
    def action(db, a, c):
        from .report_revisions import freeze_head

        recent(c)
        existing = list(
            db.scalars(
                select(Job).where(
                    Job.account_id == a.id,
                    Job.generation == a.generation,
                    Job.kind == "export",
                )
            )
        )
        if (
            any(j.state in ("pending", "running") for j in existing)
            or sum(j.accepted > now() - 86400 for j in existing) >= 5
        ):
            raise Problem(429, "LIMIT_EXCEEDED", headers={"Retry-After": "60"})
        if body.selection.kind == "all":
            ids = list(
                db.scalars(
                    select(Check.id)
                    .where(Check.account_id == a.id, Check.generation == a.generation)
                    .order_by(Check.created)
                    .limit(501)
                )
            )
            if len(ids) > 500:
                raise Problem(413, "LIMIT_EXCEEDED")
        else:
            ids = body.selection.session_ids
        report_heads = {}
        for id in ids:
            check = owned_check(db, a, id)
            if check.state not in ("completed", "invalid"):
                raise Problem(409, "FINALIZED_CHECK_REQUIRED")
            safe_result(check.result)
            report_heads[id] = freeze_head(db, a, check)
        version_ids = set()
        current_version = None
        if body.selection.kind == "all":
            versions = list(
                db.scalars(
                    select(Record).where(
                        Record.account_id == a.id,
                        Record.generation == a.generation,
                        Record.kind == "profile_version",
                    )
                )
            )
            version_ids = {v.body["profile_version_id"] for v in versions}
            profile = record(db, a, "profile", "current")
            current_version = profile.body["profile_version_id"] if profile else None
        else:
            for sid in ids:
                context = record(db, a, "context", sid)
                if context and context.body.get("profile_version_id"):
                    version_ids.add(context.body["profile_version_id"])
        job_body = {
            **body.data(),
            "session_ids": ids,
            "profile_version_ids": sorted(version_ids),
            "current_profile_version_id": current_version,
            "report_revision_heads": report_heads,
        }
        if len(canonical(job_body)) > 512 * 1024:
            raise Problem(413, "LIMIT_EXCEEDED")
        id = uid()
        job = Job(
            id=id,
            account_id=a.id,
            generation=a.generation,
            kind="export",
            body=job_body,
            accepted=now(),
            expires=now() + 86400,
            state="pending",
            attempts=0,
        )
        db.add(job)
        db.flush()
        db.add(Outbox(job_id=id))
        return job_view(job), 202, {}, id

    return mutate(request, action, escape=True)


@app.post("/v1/privacy/deletion-requests", status_code=202)
def deletion_post(request: Request, body: DeleteRequest):
    with access(request, receipt=True, allow_inactive=True) as (db, a, c, r):
        entry, replay = operation(request, db, a, c, r, True)
        if replay:
            job = db.get(Job, entry.operation_id)
            if not job:
                raise Problem(410, "RECEIPT_UNAVAILABLE")
            if job.journal_accepted:
                return answer(entry, job_view(job), 202, {}, job.id)
        else:
            recent(c)
            old = a.generation
            a.generation += 1
            a.state = "deleting"
            a.notice = None
            id = uid()
            accepted = now()
            job = Job(
                id=id,
                account_id=a.id,
                generation=old,
                kind="deletion",
                state="pending",
                attempts=0,
                body={
                    "scope": body.scope,
                    "accepted_at": iso(accepted),
                    "provider_sub": c["sub"],
                },
                accepted=accepted,
                journal_accepted=False,
            )
            db.add(job)
            db.flush()
            answer(entry, job_view(job), 202, {}, id)
        db.commit()  # The write barrier survives an unavailable independent journal.
        receipt = storage.journal_accept(job, a)
        db.refresh(job)
        db.refresh(a)
        job.journal_accepted = True
        job.body = {**job.body, "journal_receipt": receipt}
        if not db.scalar(select(Outbox).where(Outbox.job_id == job.id)):
            db.add(Outbox(job_id=job.id))
        result = answer(entry, job_view(job), 202, {}, job.id)
        return result


@app.get("/v1/privacy/jobs/{job_id}")
def privacy_status(request: Request, job_id: UUID):
    with access(request, receipt=True,allow_inactive=True) as (db, a, c, r):
        job = db.get(Job, job_id)
        if not job or job.account_id != a.id or job.kind not in ("export", "deletion"):
            raise Problem(404, "NOT_FOUND")
        if job.kind=='export' and (r or a.state!='active'):
            raise Problem(403,'CAPABILITY_DENIED')
        if job.kind == "export" and job.generation != a.generation:
            raise Problem(410, "DATA_GENERATION_RETIRED")
        return job_view(job)


@app.get("/v1/privacy/jobs/{job_id}/download")
def privacy_download(request: Request, job_id: UUID):
    from fastapi.responses import StreamingResponse

    with access(request) as (db, a, c, r):
        job = db.get(Job, job_id)
        if not job or job.account_id != a.id or job.kind != "export":
            raise Problem(404, "NOT_FOUND")
        if job.generation != a.generation:
            raise Problem(410, "DATA_GENERATION_RETIRED")
        if not job.expires or job.expires <= now():
            raise Problem(410, "EXPORT_EXPIRED")
        if job.state != "completed" or not job.output:
            raise Problem(409, "EXPORT_NOT_READY")
        for sid in job.body["session_ids"]:
            check = owned_check(db, a, sid)
            if check.study_id:
                consent = record(db, a, "consent", check.study_id)
                if not consent or consent.body["state"] != "active":
                    raise Problem(403, "CAPABILITY_DENIED")
            safe_result(check.result)
        if (
            request.headers.get("range")
            or request.headers.get("if-none-match")
            or request.headers.get("if-modified-since")
        ):
            raise Problem(416, "RESUME_UNSUPPORTED")
        output = job.output
        if not output.get("version_id") or output["size_bytes"] > 64 * 1024 * 1024:
            raise Problem(503, "EXPORT_MANIFEST_INVALID")
    obj = storage.client("s3").get_object(
        Bucket=settings().export_bucket,
        Key=output["key"],
        VersionId=output["version_id"],
    )
    if obj["ContentLength"] != output["size_bytes"]:
        obj["Body"].close()
        raise Problem(503, "EXPORT_MANIFEST_INVALID")

    def stream():
        total = 0
        try:
            while chunk := obj["Body"].read(64 * 1024):
                total += len(chunk)
                if total > output["size_bytes"]:
                    raise RuntimeError("Bounded export stream exceeded")
                yield chunk
        finally:
            obj["Body"].close()

    return StreamingResponse(
        stream(),
        media_type="application/zip",
        headers={
            "Content-Length": str(output["size_bytes"]),
            "Content-Disposition": f'attachment; filename="otgd-{job_id}.zip"',
            "Cache-Control": "private, no-store",
        },
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=web_origins(settings()),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Data-Generation",
        "Idempotency-Key",
        "If-Match",
        "X-App-Version",
    ],
    expose_headers=[
        "ETag",
        "X-Request-Id",
        "Retry-After",
        "Content-Length",
        "X-Evidence-Sha256",
    ],
    max_age=300,
)


# Report revisions have their own finalized-check authorization and immutable DTOs.
app.include_router(report_revision_router)
