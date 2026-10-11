from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OTGD_", extra="ignore")
    environment: Literal["local", "qa", "prod", "test"] = "local"
    database_url: str | None = None
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "otgd"
    database_user: str = "otgd_app"
    database_password: str = ""
    database_pool_size: int = 5
    database_sslmode: str = "prefer"
    database_sslrootcert: str | None = None
    app_database_user: str = "otgd_app"
    app_database_password: str | None = None
    issuer: str = "http://localhost:8081"
    client_id: str = "otgd-local-mobile"
    jwks_url: str = "http://localhost:8081/.well-known/jwks.json"
    api_origin: str = "http://localhost:8000"
    identity_origin: str = "http://localhost:8081"
    oauth_redirect_uris: list[str] = [
        "otgd-local://oauth/callback",
        "http://localhost:8082/",
    ]
    aws_region: str = "us-east-2"
    aws_endpoint_url: str | None = None
    s3_public_endpoint_url: str | None = None
    artifact_bucket: str = "otgd-local-artifacts"
    export_bucket: str = "otgd-local-exports"
    journal_bucket: str = "otgd-local-deletion-journal"
    queue_url: str = ""
    dlq_url: str = ""
    tombstone_key: str = ""
    tombstone_key_id: str = "v1"
    user_pool_id: str = ""
    local_signing_key_path: str = ".local/identity-key.pem"
    storage_kms_key_id: str | None = None
    journal_kms_key_id: str | None = None
    recovery_required: bool = False
    maintenance: bool = False
    minimum_app_version: str = "0.2.0"
    supported_app_versions: list[str] = ["0.2.0"]

    @model_validator(mode="after")
    def isolation(self):
        import re

        if (
            not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", self.minimum_app_version)
            or not self.supported_app_versions
            or len(self.supported_app_versions) > 32
            or any(
                not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", v)
                for v in self.supported_app_versions
            )
        ):
            raise ValueError(
                "A bounded explicit supported application version policy is required"
            )
        if not 1 <= self.database_pool_size <= 5:
            raise ValueError("Database pool outside reviewed capacity")
        if self.environment in ("qa", "prod"):
            if self.database_sslmode != "verify-full" or not self.database_sslrootcert:
                raise ValueError(
                    "Cloud PostgreSQL requires verified TLS and an RDS CA path"
                )
            if self.aws_endpoint_url or self.s3_public_endpoint_url:
                raise ValueError("Cloud cannot use endpoint overrides")
            for value in [
                self.issuer,
                self.jwks_url,
                self.api_origin,
                self.identity_origin,
            ]:
                p = urlparse(value)
                if (
                    p.scheme != "https"
                    or not p.hostname
                    or p.hostname in ("localhost", "127.0.0.1")
                ):
                    raise ValueError(
                        "Cloud identity/API requires configured HTTPS origins"
                    )
            if (
                not self.journal_kms_key_id
                or not self.storage_kms_key_id
                or self.journal_kms_key_id == self.storage_kms_key_id
            ):
                raise ValueError("Independent journal and data KMS keys are required")
            if not self.user_pool_id or not self.queue_url or not self.dlq_url:
                raise ValueError("Cloud identity and queues must be provisioned")
        if self.environment != "test" and (
            len(self.tombstone_key) != 64
            or any(c not in "0123456789abcdefABCDEF" for c in self.tombstone_key)
        ):
            raise ValueError("A separate 256-bit identity tombstone key is required")
        return self

    def db_url(self):
        return self.database_url or URL.create(
            "postgresql+psycopg",
            username=self.database_user,
            password=self.database_password,
            host=self.database_host,
            port=self.database_port,
            database=self.database_name,
        )


@lru_cache
def settings():
    return Settings()


def web_origins(config):
    """CORS is only for exact configured browser callback origins; native clients do not need it."""
    origins = set()
    for callback in config.oauth_redirect_uris:
        parsed = urlparse(callback)
        if parsed.scheme in ("http", "https") and parsed.netloc:
            origins.add(parsed.scheme + "://" + parsed.netloc)
    return sorted(origins)
