"""Secret initialization and leases covering the entire serverless HTTP response."""
from __future__ import annotations

import asyncio
import os
import re
import time
from uuid import uuid4

import boto3
from botocore.config import Config

_secret_binding = None


def _enabled():
    return os.environ.get("OTGD_SERVERLESS_MODE", "").strip().lower() in ("1", "true", "yes", "on")


def load_runtime_secrets(*, force=False):
    """Resolve explicit same-account references without constructing Settings."""
    global _secret_binding
    if not _enabled():
        return
    region = os.environ.get("OTGD_AWS_REGION", "us-east-2")
    account = os.environ.get("OTGD_DEPLOYMENT_ACCOUNT", "")
    database = os.environ.get("OTGD_DATABASE_SECRET_ARN", "")
    application = os.environ.get("OTGD_APP_DATABASE_SECRET_ARN")
    tombstone = os.environ.get("OTGD_TOMBSTONE_SECRET_ARN", "")
    binding = (region, account, database, application, tombstone,
               os.environ.get("OTGD_DATABASE_USER", "otgd_app"),
               os.environ.get("OTGD_APP_DATABASE_USER", "otgd_app"))
    if binding == _secret_binding and not force:
        return
    try:
        if region != "us-east-2" or not re.fullmatch(r"[0-9]{12}", account):
            raise ValueError()
        prefix = f"arn:aws:secretsmanager:{region}:{account}:secret:"
        if any(not isinstance(arn, str) or not arn.startswith(prefix) or len(arn) > 2048
               for arn in (database, tombstone, *([application] if application is not None else []))):
            raise ValueError()
        # The canonical Ohio endpoint already supports IPv6. A blanket
        # dualstack switch would select an unsupported Secrets Manager hostname.
        client = boto3.client("secretsmanager", region_name=region,
            endpoint_url=f"https://secretsmanager.{region}.amazonaws.com",
            config=Config(ignore_configured_endpoint_urls=True, use_dualstack_endpoint=False,
                          connect_timeout=5, read_timeout=15,
                          retries={"mode": "standard", "max_attempts": 2}))
        from .canonical import strict_loads

        def read(arn):
            raw = client.get_secret_value(SecretId=arn).get("SecretString")
            if not isinstance(raw, str) or not 1 <= len(raw.encode()) <= 65536:
                raise ValueError()
            value = strict_loads(raw)
            if not isinstance(value, dict):
                raise ValueError()
            return value

        db = read(database)
        key = read(tombstone).get("key")
        username = os.environ.get("OTGD_DATABASE_USER", "otgd_app")
        if (db.get("username") != username or username not in ("otgd_app", "otgd_migrator") or
                not isinstance(db.get("password"), str) or not 16 <= len(db["password"]) <= 1024 or
                not isinstance(key, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", key)):
            raise ValueError()
        updates = {"OTGD_DATABASE_PASSWORD": db["password"], "OTGD_TOMBSTONE_KEY": key}
        if application is not None:
            app = read(application)
            app_username = os.environ.get("OTGD_APP_DATABASE_USER", "otgd_app")
            if (app.get("username") != app_username or app_username != "otgd_app" or
                    not isinstance(app.get("password"), str) or not 16 <= len(app["password"]) <= 1024):
                raise ValueError()
            updates["OTGD_APP_DATABASE_PASSWORD"] = app["password"]
        os.environ.update(updates)
        _secret_binding = binding
    except Exception:
        raise RuntimeError("Serverless runtime secret initialization is unavailable") from None


def dispose_database():
    """Close only an already-created pool; cleanup must not open the database."""
    from .db import engine
    if engine.cache_info().currsize:
        engine().dispose()


def acquire_api_lease(lease_id, deadline):
    from .serverless_control import acquire_lease
    return acquire_lease("api", lease_id, deadline)


def release_api_lease(lease_id):
    from .serverless_control import release_lease
    return release_lease(lease_id)


def kick_dispatcher():
    """Accept a bounded private dispatch event after SQL commit, before HTTP."""
    from .config import settings
    from .canonical import canonical
    from .storage import client
    cfg = settings()
    arn = cfg.serverless_dispatch_function_arn
    if not arn:
        raise RuntimeError("Serverless dispatch target is unavailable")
    response = client("lambda").invoke(FunctionName=arn, InvocationType="Event",
        Payload=canonical({"operation": "dispatch"}))
    if response.get("StatusCode") != 202 or response.get("FunctionError"):
        raise RuntimeError("Serverless dispatch was not accepted")


async def unavailable(scope, receive, send, request_id):
    from .errors import Problem, response_problem
    await response_problem(Problem(503, "SERVICE_UNAVAILABLE", retryable=True), request_id)(scope, receive, send)


class ServerlessLifecycleMiddleware:
    """ASGI completion includes streamed bodies, cancellation and client errors."""
    def __init__(self, app, *, config=None, acquire=None, release=None, dispose=None, clock=None, kick=None):
        self.app = app
        self.config = config
        self.acquire = acquire or acquire_api_lease
        self.release = release or release_api_lease
        self.dispose = dispose or dispose_database
        self.clock = clock or time.time
        self.kick = kick or kick_dispatcher

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        from .config import settings
        cfg = self.config or settings()
        # LWA polls this route while idle; it performs no SQL and must not
        # manufacture activity that prevents Aurora from automatically pausing.
        if not cfg.serverless_mode or scope.get("path") == "/health/live":
            await self.app(scope, receive, send)
            return
        lease_id = str(uuid4())
        try:
            await asyncio.to_thread(self.acquire, lease_id, self.clock() + 900)
        except Exception:
            await unavailable(scope, receive, send, lease_id)
            return
        held_body = None
        held_start = None
        end = None
        started = False
        dispatch_failed = False

        class DispatchUnavailable(Exception):
            pass

        async def guarded_send(message):
            nonlocal held_body, held_start, end, started
            if message["type"] == "http.response.start":
                if scope.get("method") in ("POST", "PUT", "PATCH", "DELETE") and 200 <= message["status"] < 300:
                    try:
                        await asyncio.to_thread(self.kick)
                    except Exception:
                        raise DispatchUnavailable() from None
                headers = {key.lower(): value for key, value in message.get("headers", [])}
                if scope.get("method") == "HEAD" or message["status"] in (204, 304) or headers.get(b"content-length") == b"0":
                    held_start = message
                else:
                    await send(message)
                    started = True
            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                if held_start is not None:
                    # HEAD, 204 and 304 have no HTTP payload; their headers are
                    # the completion barrier even when an ASGI app emits bytes.
                    if scope.get("method") == "HEAD" or held_start["status"] in (204, 304):
                        body = b""
                    elif body:
                        raise RuntimeError("Body contradicts its zero Content-Length")
                for offset in range(0, len(body), 64 * 1024):
                    if held_body is not None:
                        await send({"type": "http.response.body", "body": held_body, "more_body": True})
                    held_body = body[offset:offset + 64 * 1024]
                if not message.get("more_body", False):
                    end = {**message, "body": b"", "more_body": False}
            else:
                await send(message)

        try:
            try:
                await self.app(scope, receive, guarded_send)
            except DispatchUnavailable:
                if started:
                    raise
                dispatch_failed = True
        finally:
            # Leave the metadata lease visible if pool cleanup fails. A
            # reconciler must never infer completion before SQL is closed.
            await asyncio.to_thread(self.dispose)
            await asyncio.to_thread(self.release, lease_id)
        if dispatch_failed:
            await unavailable(scope, receive, send, lease_id)
            return
        # LWA can freeze the process as soon as Content-Length bytes arrive.
        # Keep only the final 64 KiB and end frame until cleanup has completed.
        if held_start is not None:
            await send(held_start)
        if held_body is not None:
            await send({"type": "http.response.body", "body": held_body, "more_body": True})
        if end is not None:
            await send(end)
