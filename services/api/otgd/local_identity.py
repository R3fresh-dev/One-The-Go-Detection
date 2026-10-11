"""Local-only fictional OAuth issuer with durable one-use PKCE codes and refresh rotation."""

import base64
import hashlib
import html
import secrets
from pathlib import Path
from urllib.parse import urlencode

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from sqlalchemy import select

from .config import settings, web_origins
from .db import OAuthRecord, factory, now, uid

s = settings()
if s.environment != "local":
    raise RuntimeError(
        "The fictional identity issuer can only run in the local environment"
    )

app = FastAPI(title="OTGD fictional local identity", docs_url=None, redoc_url=None)


def key():
    path = Path(s.local_signing_key_path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        data = private.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        try:
            import os

            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(fd, "wb") as f:
                f.write(data)
        except FileExistsError:
            pass
    return serialization.load_pem_private_key(path.read_bytes(), password=None)


def sha(v):
    return hashlib.sha256(v.encode()).hexdigest()


def b64(v):
    return base64.urlsafe_b64encode(v).decode().rstrip("=")


def err(code="invalid_grant"):
    return JSONResponse(
        {"error": code}, status_code=400, headers={"Cache-Control": "no-store"}
    )


@app.middleware("http")
async def boundaries(request, call_next):
    response = await call_next(request)
    response.headers.update(
        {
            "Cache-Control": "no-store",
            "Content-Security-Policy": "default-src 'none'; form-action 'self'; frame-ancestors 'none'",
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
        or len(code_challenge) != 43
        or not 16 <= len(state) <= 256
    ):
        return err("invalid_request")
    id = secrets.token_urlsafe(32)
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
                },
                expires=now() + 300,
            )
        )
    token = html.escape(id, quote=True)
    return HTMLResponse(
        '<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Fictional local sign-in</title><h1>Local engineering account</h1><p>These two named accounts contain fictional engineering data. This is not production authentication.</p><form method="post" action="/oauth2/authorize"><input type="hidden" name="authorization_id" value="'
        + token
        + '"><button name="account" value="fixture_a">Use Fictional Account A</button><button name="account" value="fixture_b">Use Fictional Account B</button></form></html>'
    )


@app.post("/oauth2/authorize")
def choose(authorization_id: str = Form(...), account: str = Form(...)):
    if account not in ("fixture_a", "fixture_b"):
        return err("invalid_request")
    with factory().begin() as db:
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
        ):
            return err()
        row.consumed = True
        code = secrets.token_urlsafe(32)
        db.add(
            OAuthRecord(
                id=sha(code),
                kind="code",
                body={
                    **row.body,
                    "sub": "local-" + account,
                    "auth_time": int(now()),
                    "family": uid(),
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
    with factory().begin() as db:
        row = db.scalar(
            select(OAuthRecord)
            .where(OAuthRecord.id == sha(secret))
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        expected = "code" if grant_type == "authorization_code" else "refresh"
        if not row or row.kind != expected or row.consumed or row.expires <= now():
            return err()
        if grant_type == "authorization_code":
            if (
                not 43 <= len(code_verifier) <= 128
                or b64(hashlib.sha256(code_verifier.encode()).digest())
                != row.body["challenge"]
                or redirect_uri != row.body["redirect_uri"]
            ):
                return err()
        revoked = db.get(OAuthRecord, "family-" + sha(row.body["family"]))
        if revoked:
            return err()
        row.consumed = True
        refresh = secrets.token_urlsafe(48)
        db.add(
            OAuthRecord(
                id=sha(refresh),
                kind="refresh",
                body=row.body,
                expires=now() + 30 * 86400,
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
            "exp": current + 900,
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
                "expires_in": 900,
            },
            headers={"Cache-Control": "no-store"},
        )


@app.post("/oauth2/revoke")
def revoke(token: str = Form(...), client_id: str = Form(...)):
    if client_id != s.client_id:
        return err("invalid_client")
    with factory().begin() as db:
        row = db.get(OAuthRecord, sha(token))
        if row:
            id = "family-" + sha(row.body["family"])
            if not db.get(OAuthRecord, id):
                db.add(
                    OAuthRecord(
                        id=id,
                        kind="revoked",
                        body={},
                        expires=now() + 31 * 86400,
                        consumed=True,
                    )
                )
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
