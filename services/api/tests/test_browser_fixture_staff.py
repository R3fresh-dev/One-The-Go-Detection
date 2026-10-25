"""Fixture identity routing only; actual governed setup runs against local PostgreSQL."""
from contextlib import contextmanager
from pathlib import Path
import sys

import pytest


@pytest.mark.parametrize("override,expected", [
    ({}, "local-participant_probe_staff"),
    ({"staff_subject": "local-browser_staff"}, "local-browser_staff"),
])
def test_governed_fixture_locks_only_the_selected_staff_identity(monkeypatch, override, expected):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[3] / "infra/local"))
    import participant_probe as probe

    class ReachedIdentityBoundary(Exception):
        pass

    class Transaction:
        def execute(self, statement):
            pass  # SET LOCAL timeout; no database or registry write in this routing test.

    class Factory:
        @contextmanager
        def begin(self):
            yield Transaction()

    seen = []
    def lock(db, subject, cfg):
        seen.append(subject)
        raise ReachedIdentityBoundary

    monkeypatch.setattr(probe, "factory", lambda: Factory())
    monkeypatch.setattr(probe, "require_maintenance_db", lambda db, cfg: None)
    monkeypatch.setattr(probe, "lock_account", lock)
    with pytest.raises(ReachedIdentityBoundary):
        probe.provision(object(), "fictional-subject", "fictional-staff", "a" * 16, **override)
    assert seen == [expected]
