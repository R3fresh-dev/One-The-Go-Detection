from datetime import datetime, timezone
from functools import lru_cache
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import settings


def now():
    return datetime.now(timezone.utc).timestamp()


def iso(value=None):
    return (
        datetime.fromtimestamp(now() if value is None else value, timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def uid():
    return str(uuid4())


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    subject_hash: Mapped[str] = mapped_column(String(64), unique=True)
    generation: Mapped[int] = mapped_column(Integer, default=1)
    state: Mapped[str] = mapped_column(String(32), default="active")
    notice: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created: Mapped[float] = mapped_column(Float, default=now)
    __table_args__ = (CheckConstraint("generation > 0"),)


class Record(Base):
    """Bounded, typed immutable application records; ownership never comes from JSON."""

    __tablename__ = "records"
    id: Mapped[str] = mapped_column(String(512), primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    generation: Mapped[int] = mapped_column(Integer, index=True)
    kind: Mapped[str] = mapped_column(String(32), index=True)
    parent_id: Mapped[str | None] = mapped_column(String(36), index=True)
    revision: Mapped[int] = mapped_column(Integer, default=1)
    body: Mapped[dict] = mapped_column(JSON)
    sha256: Mapped[str] = mapped_column(String(64))
    created: Mapped[float] = mapped_column(Float, default=now)


class Check(Base):
    __tablename__ = "checks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    generation: Mapped[int] = mapped_column(Integer, index=True)
    state: Mapped[str] = mapped_column(String(24), default="draft")
    revision: Mapped[int] = mapped_column(Integer, default=1)
    mode: Mapped[str] = mapped_column(String(32))
    study_id: Mapped[str | None] = mapped_column(String(256))
    protocol_id: Mapped[str | None] = mapped_column(String(256))
    supersedes_id: Mapped[str | None] = mapped_column(String(36))
    snapshot: Mapped[dict | None] = mapped_column(JSON)
    snapshot_sha256: Mapped[str | None] = mapped_column(String(64))
    evidence_sha256: Mapped[str | None] = mapped_column(String(64))
    result: Mapped[dict | None] = mapped_column(JSON)
    created: Mapped[float] = mapped_column(Float, default=now, index=True)


class Dedup(Base):
    __tablename__ = "idempotency"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    generation: Mapped[int] = mapped_column(Integer)
    digest: Mapped[str] = mapped_column(String(64))
    route: Mapped[str] = mapped_column(String(512))
    family: Mapped[str] = mapped_column(String(128))
    status: Mapped[int] = mapped_column(Integer)
    body: Mapped[dict | None] = mapped_column(JSON)
    headers: Mapped[dict] = mapped_column(JSON, default=dict)
    operation_id: Mapped[str | None] = mapped_column(String(36))
    created: Mapped[float] = mapped_column(Float, default=now)


class Revocation(Base):
    __tablename__ = "revocations"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    created: Mapped[float] = mapped_column(Float, default=now)


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    generation: Mapped[int] = mapped_column(Integer)
    kind: Mapped[str] = mapped_column(String(16))
    state: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    body: Mapped[dict] = mapped_column(JSON)
    output: Mapped[dict | None] = mapped_column(JSON)
    accepted: Mapped[float] = mapped_column(Float, default=now)
    started: Mapped[float | None] = mapped_column(Float)
    completed: Mapped[float | None] = mapped_column(Float)
    expires: Mapped[float | None] = mapped_column(Float)
    lease_until: Mapped[float | None] = mapped_column(Float)
    fence: Mapped[int] = mapped_column(Integer, default=0)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    failure: Mapped[str | None] = mapped_column(String(64))
    journal_accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    cleanup_next_at: Mapped[float] = mapped_column(
        Float, default=0, server_default="0", index=True
    )
    cleanup_last_success: Mapped[float | None] = mapped_column(Float)


class Outbox(Base):
    __tablename__ = "outbox"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), unique=True)
    published: Mapped[float | None] = mapped_column(Float)
    available: Mapped[float] = mapped_column(Float, default=now)
    lease_until: Mapped[float | None] = mapped_column(Float)


class Artifact(Base):
    __tablename__ = "artifacts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    generation: Mapped[int] = mapped_column(Integer)
    session_id: Mapped[str] = mapped_column(String(36))
    bucket: Mapped[str] = mapped_column(String(128))
    key: Mapped[str] = mapped_column(String(300))
    version_id: Mapped[str | None] = mapped_column(String(1024))
    sha256: Mapped[str] = mapped_column(String(64))
    size: Mapped[int] = mapped_column(Integer)
    media_type: Mapped[str] = mapped_column(String(80))
    kind: Mapped[str] = mapped_column(String(32))
    state: Mapped[str] = mapped_column(String(24), default="quarantine")
    expires: Mapped[float] = mapped_column(Float)
    scope: Mapped[dict] = mapped_column(JSON)
    cleanup_next_at: Mapped[float] = mapped_column(
        Float, default=0, server_default="0", index=True
    )
    cleanup_last_success: Mapped[float | None] = mapped_column(Float)


class Registry(Base):
    """Only operator/migration identity provisions qualification, study and key records."""

    __tablename__ = "operator_registry"
    id: Mapped[str] = mapped_column(String(512), primary_key=True)
    kind: Mapped[str] = mapped_column(String(32), index=True)
    body: Mapped[dict] = mapped_column(JSON)
    active: Mapped[bool] = mapped_column(Boolean, default=False)


class SystemState(Base):
    __tablename__ = "system_state"
    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    body: Mapped[dict] = mapped_column(JSON)


class RateBucket(Base):
    __tablename__ = "rate_buckets"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    tokens: Mapped[float] = mapped_column(Float)
    updated: Mapped[float] = mapped_column(Float)


class OAuthRecord(Base):
    __tablename__ = "local_oauth"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    kind: Mapped[str] = mapped_column(String(16))
    body: Mapped[dict] = mapped_column(JSON)
    expires: Mapped[float] = mapped_column(Float)
    consumed: Mapped[bool] = mapped_column(Boolean, default=False)


class Audit(Base):
    __tablename__ = "audit"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    account_id: Mapped[str] = mapped_column(String(36), index=True)
    generation: Mapped[int] = mapped_column(Integer)
    action: Mapped[str] = mapped_column(String(640))
    request_id: Mapped[str] = mapped_column(String(36))
    created: Mapped[float] = mapped_column(Float, default=now)


@lru_cache
def engine():
    s = settings()
    url = s.db_url()
    kw = {"pool_pre_ping": True}
    if str(url).startswith("sqlite"):
        if s.environment != "test":
            raise ValueError("SQLite is unit-test only; local requires PostgreSQL")
        kw.update(connect_args={"check_same_thread": False}, poolclass=StaticPool)
    else:
        args = {"connect_timeout": 5, "sslmode": s.database_sslmode}
        if s.database_sslrootcert:
            args["sslrootcert"] = s.database_sslrootcert
        kw.update(
            pool_size=s.database_pool_size,
            max_overflow=0,
            pool_timeout=5,
            connect_args=args,
        )
    return create_engine(url, **kw)


@lru_cache
def factory():
    return sessionmaker(bind=engine(), expire_on_commit=False)
