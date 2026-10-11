"""Signed test identities retain coherent timestamps across a clock rollover."""

import time

import pytest

from otgd import db
from otgd.auth import Verifier
from otgd.errors import Problem

from .conftest import KEY, token


def test_fixture_token_samples_one_issue_time_and_real_verifier_rejects_future_auth(monkeypatch):
    issued = int(db.now()) - 2
    clock_values = iter((issued + .999, issued + 1.001, issued + 1.002))
    sampled = []

    def crossing_clock():
        value = next(clock_values)
        sampled.append(value)
        return value

    monkeypatch.setattr(db, "now", crossing_clock)
    verifier = Verifier()
    verifier.keys = {"test": KEY.public_key()}
    verifier.expires = time.monotonic() + 60
    claims = verifier.verify(token())
    assert sampled == [issued + .999]
    assert claims["iat"] == claims["auth_time"] == issued
    assert claims["exp"] == issued + 900

    # Claim overrides remain available for adversarial fixtures; the real
    # verifier must still refuse auth_time later than the signed issue time.
    monkeypatch.setattr(db, "now", lambda: issued)
    with pytest.raises(Problem) as denied:
        verifier.verify(token(auth_time=issued + 1))
    assert denied.value.status == 401 and denied.value.code == "AUTH_REQUIRED"

    overridden = verifier.verify(token(iat=issued - 1, auth_time=issued - 5, exp=issued + 120))
    assert (overridden["iat"], overridden["auth_time"], overridden["exp"]) == (
        issued - 1, issued - 5, issued + 120,
    )
