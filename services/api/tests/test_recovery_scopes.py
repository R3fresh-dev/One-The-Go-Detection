"""Fresh three-principal scope closure and retained seal logic, not live WORM."""

from copy import deepcopy
import io

import pytest

from otgd import recovery_scopes as r
from otgd.canonical import canonical, digest
from otgd.db import Account, SystemState, factory, iso, now
from otgd.domain import save_record
from otgd.errors import Problem
from .governance_fixture import approve, study, STUDY
from .test_model_admission import admitted, model  # noqa: F401 - pytest fixtures


class Retained:
    def __init__(self):
        self.values = {}
        self.replaced = False

    def put(self, bucket, key, raw, **kwargs):
        assert kwargs["conditional"] is True
        self.values[key] = raw
        return "pinned-software-version"

    def get_paginator(self, name):
        assert name == "list_object_versions"
        return self

    def paginate(self, **kwargs):
        rows = [
            {"Key": key, "VersionId": "pinned-software-version", "IsLatest": True}
            for key in self.values
            if key.startswith(kwargs["Prefix"])
        ]
        if self.replaced and rows:
            rows.append({**rows[0], "VersionId": "overwritten", "IsLatest": False})
        return [{"Versions": rows}]

    def get_object(self, **kwargs):
        assert kwargs["VersionId"] == "pinned-software-version"
        raw = self.values[kwargs["Key"]]
        return {
            "VersionId": kwargs["VersionId"],
            "ContentLength": len(raw),
            "Body": io.BytesIO(raw),
        }


@pytest.fixture
def resumed(client, account, monkeypatch):
    s3 = Retained()
    monkeypatch.setattr(r, "authority_client", lambda: s3)
    monkeypatch.setattr(r, "require_authority", lambda db: 0)
    monkeypatch.setattr("otgd.storage.put_versioned", s3.put)
    cutoff = now() - 20
    state = {
        "verified": True,
        "scopes_suspended": True,
        "recovery_id": "fictional-recovery",
        "authentication_cutoff": cutoff,
        "journal_activation": {
            "key": "recovery/fictional.json",
            "version_id": "original",
            "sha256": "a" * 64,
        },
    }
    with factory().begin() as db:
        doc = study(account)
        doc["channels"] = {}
        approve(db, "study", doc)
        db.add(SystemState(key="recovery", body=state))
        save_record(
            db,
            db.get(Account, account),
            "consent",
            STUDY,
            {
                "state": "active",
                "accepted_at": iso(),
                "invitation_id": doc["invitation_id"],
                "document_version": doc["document_version"],
                "document_sha256": doc["document_sha256"],
            },
        )
    return account, s3, state


def test_fresh_registry_reapproval_seal_allows_only_exact_study_and_new_consent(
    resumed,
):
    account, s3, state = resumed
    with factory().begin() as db:
        with pytest.raises(Problem):
            r.require_study_scope(db, STUDY, db.get(Account, account))
        receipt = r.seal_study(db, STUDY, "local:fixture-releaser")
        assert receipt["global_scopes_suspended"] is True
        r.require_study_scope(db, STUDY, db.get(Account, account))
        assert db.get(SystemState, "recovery").body["scopes_suspended"] is True
        with pytest.raises(Problem):
            r.require_study_scope(db, "another-study")
        key = receipt["seal"]["key"]
        assert canonical(__import__("json").loads(s3.values[key])) == s3.values[key]


@pytest.mark.parametrize(
    "change",
    [
        "stale_approval",
        "stale_consent",
        "database_bool",
        "foreign_recovery",
        "scope_hash",
        "foreign_account",
        "latest_scope",
        "overwrite",
        "deleted_seal",
    ],
)
def test_no_stale_or_mutated_authority_reopens_study(resumed, change):
    account, s3, state = resumed
    with factory().begin() as db:
        receipt = r.seal_study(db, STUDY, "local:fixture-releaser")
        key = receipt["seal"]["key"]
        body = __import__("json").loads(s3.values[key])
        if change == "stale_approval":
            db.get(SystemState, "recovery").body = {
                **state,
                "authentication_cutoff": now() + 1,
            }
        elif change == "stale_consent":
            row = db.get(
                __import__("otgd.db", fromlist=["Record"]).Record,
                account + ":consent:" + STUDY,
            )
            row.body = {
                **row.body,
                "accepted_at": iso(state["authentication_cutoff"] - 1),
            }
        elif change == "database_bool":
            db.get(SystemState, "recovery").body = {**state, "scopes_suspended": False}
        elif change == "foreign_recovery":
            body["recovery_id"] = "other"
        elif change == "scope_hash":
            body["references_sha256"] = "0" * 64
        elif change == "foreign_account":
            body["account"] = "other"
        elif change == "latest_scope":
            body = deepcopy(body)
            body.update(seal_id="later", sealed_at=iso(now() + 1), references=[])
            body["references_sha256"] = digest([])
            s3.values[r.prefix(state["recovery_id"], STUDY) + "later.json"] = canonical(
                body
            )
        elif change == "overwrite":
            s3.replaced = True
        else:
            s3.values.clear()
        if change in ("foreign_recovery", "scope_hash", "foreign_account"):
            s3.values[key] = canonical(body)
        with pytest.raises(Problem) as denied:
            r.require_study_scope(db, STUDY, db.get(Account, account))
        assert denied.value.code == "RECOVERED_SCOPE_SUSPENDED"


def test_unrestored_database_needs_no_seal_and_false_claim_cannot_seal(client, account):
    with factory().begin() as db:
        r.require_study_scope(db, STUDY)
        db.add(SystemState(key="recovery", body={"verified": False}))
        with pytest.raises(Problem) as denied:
            r.seal_study(db, STUDY, "local:fixture")
        assert denied.value.code == "RECOVERY_NOT_SUSPENDED"


@pytest.fixture
def configured_reapproval(admitted, monkeypatch):  # noqa: F811 - pytest injects imported fixture
    """Reuse actual task/model approval lifecycle; double retained transport only."""
    retained = Retained()
    monkeypatch.setattr(r, "authority_client", lambda: retained)
    monkeypatch.setattr("otgd.storage.put_versioned", retained.put)
    state = {"verified": True, "scopes_suspended": True,
        "recovery_id": "fictional-configured-recovery", "authentication_cutoff": now() - 300,
        "journal_activation": {"key": "recovery/configured-fictional.json",
            "version_id": "pinned-activation", "sha256": "a" * 64}}
    with factory().begin() as db:
        db.add(SystemState(key="recovery", body=state))
        db.flush()
        receipt = r.seal_study(db, STUDY, "local:fixture-releaser")
        body = __import__('json').loads(retained.values[receipt['seal']['key']])
        assert {'study', 'configuration', 'qualification', 'retention', 'model', 'calibration'} <= {
            ref['kind'] for ref in body['references']}
        assert body['references'] == r.references(db, STUDY, state['authentication_cutoff'])
    return {**admitted, 'retained': retained, 'receipt': receipt, 'state': state}


def configured_capture_arm(client, channel='task'):
    from uuid import uuid4

    from otgd.operator_governance import active_body

    from .conftest import headers
    from .governance_fixture import PROTOCOL

    with factory()() as db:
        study_body = active_body(db, 'study', STUDY)
        config = deepcopy(active_body(db, 'configuration', study_body['channels'][channel]))
    sid, aid, rid = (str(uuid4()) for _ in range(3))
    response = client.post('/v1/sessions', headers=headers(), json={'session_id': sid,
        'mode': 'controlled_research', 'study_id': STUDY, 'protocol_id': PROTOCOL})
    assert response.status_code == 201, response.text
    context = {'schema_version': '1.0.0', 'session_id': sid, 'context_confirmed_at': iso(),
        'profile_version_id': None, 'profile_snapshot_sha256': 'a' * 64,
        'history_snapshot_sha256': 'b' * 64, 'protocol_id': PROTOCOL,
        'configuration_refs': [{'id': config['configuration_id'], 'version': config['version'],
            'sha256': config['sha256'], 'scope': 'measurement_collection'}],
        'baseline_refs': [], 'device_associations': [], 'self_report_context': None}
    response = client.put(f'/v1/sessions/{sid}/context', headers=headers(revision=0), json=context)
    assert response.status_code == 200, response.text
    attempt = {'schema_version': '1.0.0', 'session_id': sid, 'attempt_id': aid,
        'component': channel, 'record_id': rid, 'supersedes_attempt_id': None, 'status': 'started',
        'source': 'prototype_sensor', 'started_at': iso(), 'ended_at': None,
        'configuration_id': config['configuration_id'], 'configuration_hash': config['sha256'],
        'quality_flags': [], 'component_metadata': {}, 'artifact_refs': [], 'attestation_refs': []}
    response = client.put(f'/v1/sessions/{sid}/attempts/{aid}', headers=headers(revision=0), json=attempt)
    assert response.status_code == 200, response.text
    return sid, attempt, config


def test_configured_reapproved_study_reaches_real_capture_start_and_model_execution(client, configured_reapproval):
    from otgd import model_engine
    from otgd.db import Check

    from .conftest import headers

    value = configured_reapproval
    sid, attempt, config = configured_capture_arm(client)
    response = client.post(f'/v1/sessions/{sid}/capture-authorizations', headers=headers(), json={
        'attempt_id': attempt['attempt_id'], 'channel': 'task', 'binding_id': None, 'device_id': None,
        'configuration_id': config['configuration_id'], 'configuration_hash': config['sha256']})
    assert response.status_code == 201, response.text
    authorization = response.json()
    started = client.post(f"/v1/sessions/{sid}/capture-authorizations/{authorization['authorization_id']}/start",
        headers=headers(), json={'attempt_id': attempt['attempt_id'], 'device_boot_id': 'FICTIONAL-RECOVERY-BOOT',
            'device_nonce': None})
    assert started.status_code == 200, started.text
    assert started.json()['server_start']['grant']['configuration_submitted_sha256'] == digest(config)
    with factory()() as db:
        owner = db.get(Account, value['account'])
        check = db.get(Check, value['sid'])
        output = model_engine.result_for_check(db, owner, check)
        assert output['state'] == 'research_estimate' and output['schema_version'] == '1.1.0'
        assert output['model_execution']['authority_manifest']
        assert db.get(SystemState, 'recovery').body['scopes_suspended'] is True
        with pytest.raises(Problem, match='RECOVERED_SCOPE_SUSPENDED'):
            r.require_study_scope(db, 'fictional-unsealed-study', owner)


@pytest.mark.parametrize('change', ['retired_retention', 'replaced_configuration'])
def test_prior_configured_seal_refuses_changed_dependency_through_capture_and_model(
    client, configured_reapproval, change
):
    from otgd import model_engine
    from otgd.db import Check
    from otgd.operator_governance import transition

    from .conftest import headers
    from .governance_fixture import POLICY, proof

    value = configured_reapproval
    sid, attempt, config = configured_capture_arm(client)
    key = value['receipt']['seal']['key']
    original_seal = value['retained'].values[key]
    with factory().begin() as db:
        if change == 'retired_retention':
            transition(db, 'retention', POLICY, 'v1', 'retire', 'local:fixture-releaser',
                'Fictional dependency retirement under existing seal', 3)
        else:
            changed = {**config, 'version': 'v2', 'max_duration_ms': config['max_duration_ms'] + 1000,
                'qualification_evidence_ref': 'fictional-new-recovery-configuration-proof'}
            qualification = proof(config_body=changed)
            qualification['registry_id'] = changed['qualification_evidence_ref']
            approve(db, 'qualification', qualification)
            approve(db, 'configuration', changed)
    response = client.post(f'/v1/sessions/{sid}/capture-authorizations', headers=headers(), json={
        'attempt_id': attempt['attempt_id'], 'channel': 'task', 'binding_id': None, 'device_id': None,
        'configuration_id': config['configuration_id'], 'configuration_hash': config['sha256']})
    assert response.status_code == 403 and response.json()['code'] == 'RECOVERED_SCOPE_SUSPENDED', response.text
    with factory()() as db:
        owner, check = db.get(Account, value['account']), db.get(Check, value['sid'])
        with pytest.raises(Problem, match='RECOVERED_SCOPE_SUSPENDED'):
            model_engine.execution_authority(db, owner, check)
        result = model_engine.result_for_check(db, owner, check)
        assert result['state'] == 'inconclusive' and result['probability'] is None
        assert result['classification'] is None and 'model_execution' not in result
        assert db.get(SystemState, 'recovery').body['scopes_suspended'] is True
        assert db.get(Check, sid).snapshot is None
    assert value['retained'].values[key] == original_seal
    assert len(value['retained'].values) == 1
