"""Local-only fictional OAuth issuer with durable one-use PKCE codes and refresh rotation."""

import base64
import hashlib
import html
import os
import re
import secrets
import stat
from pathlib import Path
from urllib.parse import urlencode

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from sqlalchemy import select

from .config import settings, web_origins
from .db import OAuthRecord, Revocation, factory, now, uid
from .canonical import canonical
from .local_oauth_state import (
    ACCESS_SECONDS,
    FAMILY_SECONDS,
    FICTIONAL_ACCOUNTS,
    cleanup_expired,
    family_id,
    lock_account,
    lock_family,
    lock_identity,
    revoke_family,
)

s = settings()
if s.environment != "local":
    raise RuntimeError(
        "The fictional identity issuer can only run in the local environment"
    )

app = FastAPI(title="OTGD fictional local identity", docs_url=None, redoc_url=None)
COOKIE = "otgd_local_oauth"
MAX_KEY_BYTES = 16 * 1024


def key():
    path = Path(s.local_signing_key_path)
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
    try:
        fd = os.open(path, flags)
    except FileNotFoundError:
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        data = private.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        try:
            created = os.open(
                path,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
                0o600,
            )
            with os.fdopen(created, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
        except FileExistsError:
            pass
        fd = os.open(path, flags)
    with os.fdopen(fd, "rb") as source:
        before = os.fstat(source.fileno())
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_uid != os.geteuid()
            or before.st_mode & 0o077
            or before.st_nlink != 1
            or not 64 <= before.st_size <= MAX_KEY_BYTES
        ):
            raise RuntimeError(
                "Local signing key must be a bounded private regular file owned by this issuer"
            )
        data = source.read(MAX_KEY_BYTES + 1)
        after = os.fstat(source.fileno())
        if len(data) != before.st_size or (
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        ) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise RuntimeError("Local signing key changed during its bounded read")
    private = serialization.load_pem_private_key(data, password=None)
    if (
        not isinstance(private, rsa.RSAPrivateKey)
        or not 2048 <= private.key_size <= 4096
        or private.public_key().public_numbers().e != 65537
    ):
        raise RuntimeError("Local signing key must be a supported RSA private key")
    return private


def sha(v):
    return hashlib.sha256(v.encode()).hexdigest()


def b64(v):
    return base64.urlsafe_b64encode(v).decode().rstrip("=")


def err(code="invalid_grant"):
    return JSONResponse(
        {"error": code}, status_code=400, headers={"Cache-Control": "no-store"}
    )


def cleanup():
    # Do not retain cleanup's arbitrary expired-row locks while acquiring the
    # issuance Account→identity→family locks in the following transaction.
    with factory().begin() as db:
        cleanup_expired(db)


@app.middleware("http")
async def boundaries(request, call_next):
    response = await call_next(request)
    # Chromium applies form-action to redirects too. Permit only the browser
    # origins already registered for OAuth; exact callbacks remain checked by
    # authorize/choose and the POST still requires this issuer's Origin.
    form_targets = " ".join(["'self'", *web_origins(s)])
    response.headers.update(
        {
            "Cache-Control": "no-store",
            "Content-Security-Policy": f"default-src 'none'; form-action {form_targets}; frame-ancestors 'none'",
            "X-Content-Type-Options": "nosniff",
        }
    )
    return response


@app.get("/health/live")
def live():
    return {"status": "alive", "fictional_identity": True}


@app.get("/.well-known/openid-configuration")
def discovery():
    return {
        "issuer": s.issuer,
        "authorization_endpoint": s.identity_origin + "/oauth2/authorize",
        "token_endpoint": s.identity_origin + "/oauth2/token",
        "jwks_uri": s.jwks_url,
        "response_types_supported": ["code"],
        "code_challenge_methods_supported": ["S256"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
    }


@app.get("/.well-known/jwks.json")
def jwks():
    public = key().public_key().public_numbers()
    return {
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "alg": "RS256",
                "kid": "local-v1",
                "n": b64(public.n.to_bytes((public.n.bit_length() + 7) // 8, "big")),
                "e": b64(public.e.to_bytes((public.e.bit_length() + 7) // 8, "big")),
            }
        ]
    }


@app.get("/oauth2/authorize")
def authorize(
    request: Request,
    client_id: str,
    redirect_uri: str,
    response_type: str,
    state: str,
    code_challenge: str,
    code_challenge_method: str,
    scope: str = "",
    prompt: str = "",
):
    if (
        client_id != s.client_id
        or redirect_uri not in s.oauth_redirect_uris
        or response_type != "code"
        or code_challenge_method != "S256"
        or not re.fullmatch(r"[A-Za-z0-9_-]{43}", code_challenge)
        or not 16 <= len(state) <= 256
    ):
        return err("invalid_request")
    id = secrets.token_urlsafe(32)
    browser = request.cookies.get(COOKIE, "")
    if not re.fullmatch(r"[A-Za-z0-9_-]{43}", browser):
        browser = secrets.token_urlsafe(32)
    cleanup()
    with factory().begin() as db:
        db.add(
            OAuthRecord(
                id=sha(id),
                kind="authorization",
                body={
                    "client_id": client_id,
                    "redirect_uri": redirect_uri,
                    "state": state,
                    "challenge": code_challenge,
                    "browser_session": sha(browser),
                },
                expires=now() + 300,
            )
        )
    token = html.escape(id, quote=True)
    response = HTMLResponse(
        '<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Fictional local sign-in</title><h1>Local engineering account</h1><p>These named accounts contain fictional engineering data. This is not production authentication.</p><form method="post" action="/oauth2/authorize"><input type="hidden" name="authorization_id" value="'
        + token
        + '"><button name="account" value="fixture_a">Use Fictional Account A</button><button name="account" value="fixture_b">Use Fictional Account B</button><button name="account" value="browser_mobile">Use Fictional Browser Mobile</button><button name="account" value="browser_desktop">Use Fictional Browser Desktop</button></form></html>'
    )
    response.set_cookie(
        COOKIE,
        browser,
        max_age=300,
        httponly=True,
        secure=s.identity_origin.startswith("https://"),
        samesite="lax",
        path="/oauth2/authorize",
    )
    return response


@app.post("/oauth2/authorize")
def choose(
    request: Request, authorization_id: str = Form(...), account: str = Form(...)
):
    browser = request.cookies.get(COOKIE, "")
    if (
        account not in FICTIONAL_ACCOUNTS
        or not re.fullmatch(r"[A-Za-z0-9_-]{43}", authorization_id)
        or not re.fullmatch(r"[A-Za-z0-9_-]{43}", browser)
        or request.headers.get("origin") != s.identity_origin.rstrip("/")
    ):
        return err("invalid_request")
    with factory().begin() as db:
        subject = "local-" + account
        application_account = lock_account(db, subject, s)
        identity = lock_identity(db, subject)
        if identity.consumed or (
            application_account and application_account.state == "deleted"
        ):
            return err()
        row = db.scalar(
            select(OAuthRecord)
            .where(OAuthRecord.id == sha(authorization_id))
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if (
            not row
            or row.kind != "authorization"
            or row.consumed
            or row.expires <= now()
            or not secrets.compare_digest(
                row.body.get("browser_session", ""), sha(browser)
            )
        ):
            return err()
        row.consumed = True
        code = secrets.token_urlsafe(32)
        family = uid()
        family_expires = now() + FAMILY_SECONDS
        db.add(
            OAuthRecord(
                id=family_id(family),
                kind="family",
                body={"sub": subject, "expires_at": family_expires},
                expires=family_expires + ACCESS_SECONDS,
            )
        )
        db.add(
            OAuthRecord(
                id=sha(code),
                kind="code",
                body={
                    **row.body,
                    "sub": subject,
                    "auth_time": int(now()),
                    "family": family,
                    "family_expires_at": family_expires,
                },
                expires=now() + 120,
            )
        )
        return RedirectResponse(
            row.body["redirect_uri"]
            + "?"
            + urlencode({"code": code, "state": row.body["state"]}),
            status_code=303,
        )


@app.post("/oauth2/token")
def token(
    grant_type: str = Form(...),
    client_id: str = Form(...),
    code: str = Form(""),
    code_verifier: str = Form(""),
    redirect_uri: str = Form(""),
    refresh_token: str = Form(""),
):
    if client_id != s.client_id:
        return err("invalid_client")
    if grant_type not in ("authorization_code", "refresh_token"):
        return err("unsupported_grant_type")
    secret = code if grant_type == "authorization_code" else refresh_token
    if not re.fullmatch(
        r"[A-Za-z0-9_-]{43}"
        if grant_type == "authorization_code"
        else r"[A-Za-z0-9_-]{64}",
        secret,
    ):
        return err()
    cleanup()
    with factory().begin() as db:
        hint = db.get(OAuthRecord, sha(secret))
        expected = "code" if grant_type == "authorization_code" else "refresh"
        if not hint or hint.kind != expected:
            return err()
        application_account = lock_account(db, hint.body["sub"], s)
        identity = lock_identity(db, hint.body["sub"])
        family = lock_family(db, hint.body["family"])
        row = db.scalar(
            select(OAuthRecord)
            .where(OAuthRecord.id == sha(secret))
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if (
            not row
            or row.kind != expected
            or not family
            or family.kind != "family"
            or family.consumed
            or identity.consumed
            or (application_account and application_account.state == "deleted")
        ):
            return err()
        if row.consumed:
            if expected == "refresh":
                revoke_family(db, row.body["family"], application_account)
            return err()
        if row.expires <= now() or row.body.get("family_expires_at", 0) <= now():
            return err()
        if grant_type == "authorization_code":
            if (
                not re.fullmatch(r"[A-Za-z0-9._~-]{43,128}", code_verifier)
                or b64(hashlib.sha256(code_verifier.encode()).digest())
                != row.body["challenge"]
                or redirect_uri != row.body["redirect_uri"]
            ):
                return err()
        revoked = db.get(OAuthRecord, "family-" + sha(row.body["family"]))
        if application_account:
            revoked = revoked or db.get(
                Revocation,
                hashlib.sha256(
                    canonical([application_account.id, row.body["family"]])
                ).hexdigest(),
            )
        if revoked:
            revoke_family(db, row.body["family"], application_account)
            return err()
        row.consumed = True
        refresh = secrets.token_urlsafe(48)
        db.add(
            OAuthRecord(
                id=sha(refresh),
                kind="refresh",
                body=row.body,
                expires=row.body["family_expires_at"],
            )
        )
        current = int(now())
        claims = {
            "iss": s.issuer,
            "sub": row.body["sub"],
            "client_id": s.client_id,
            "token_use": "access",
            "jti": uid(),
            "origin_jti": row.body["family"],
            "auth_time": row.body["auth_time"],
            "iat": current,
            "exp": current + ACCESS_SECONDS,
            "scope": "openid profile",
        }
        access = jwt.encode(
            claims, key(), algorithm="RS256", headers={"kid": "local-v1"}
        )
        return JSONResponse(
            {
                "access_token": access,
                "refresh_token": refresh,
                "token_type": "Bearer",
                "expires_in": ACCESS_SECONDS,
            },
            headers={"Cache-Control": "no-store"},
        )


@app.post("/oauth2/revoke")
def revoke(token: str = Form(...), client_id: str = Form(...)):
    if client_id != s.client_id:
        return err("invalid_client")
    cleanup()
    with factory().begin() as db:
        hint = (
            db.get(OAuthRecord, sha(token))
            if re.fullmatch(r"[A-Za-z0-9_-]{64}", token)
            else None
        )
        if hint and hint.kind == "refresh":
            account = lock_account(db, hint.body["sub"], s)
            lock_identity(db, hint.body["sub"])
            revoke_family(db, hint.body["family"], account)
    return Response(status_code=200)


@app.get("/logout")
def logout(client_id: str = "", logout_uri: str = ""):
    if logout_uri and client_id == s.client_id and logout_uri in s.oauth_redirect_uris:
        return RedirectResponse(logout_uri, status_code=303)
    return HTMLResponse(
        "<h1>Local sign-out</h1><p>Close this browser to return to the application.</p>"
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
    ],
    expose_headers=["ETag", "X-Request-Id", "Retry-After", "Content-Length"],
    max_age=300,
)
