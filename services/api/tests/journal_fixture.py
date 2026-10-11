"""Explicit versioned, independent marker double for migration unit checks."""

from io import BytesIO

from otgd.canonical import canonical
from otgd.config import settings
from otgd.journal_continuity import bind_migration, read_establishment


def inject_marker(monkeypatch):
    cfg = settings()
    body = {"schema_version": "1.0.0", "environment": cfg.environment,
        "established_at": "2026-10-11T00:00:00Z", "minimum_retention_days": 90,
        "maximum_recovery_age_days": 35}
    raw = canonical(body)

    class Marker:
        def head_object(self, **kwargs):
            return {"VersionId": "fictional-unit-marker-original-version"}

        def get_object(self, **kwargs):
            return {"VersionId": "fictional-unit-marker-original-version", "ContentLength": len(raw), "Body": BytesIO(raw)}

    marker = Marker()
    receipt = read_establishment(cfg, marker)["binding"]
    monkeypatch.setenv("OTGD_JOURNAL_ESTABLISHMENT_VERSION_ID", receipt["version_id"])
    monkeypatch.setenv("OTGD_JOURNAL_ESTABLISHMENT_SHA256", receipt["sha256"])
    monkeypatch.setattr("otgd.migrate.bind_migration", lambda connection, config: bind_migration(connection, config, marker))
