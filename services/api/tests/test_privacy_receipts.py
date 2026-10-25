"""Actual HTTP receipt representation; journal transport remains a unit fixture."""
import json
import os
from pathlib import Path

from otgd import storage
from otgd.db import Account, Job, factory

from .conftest import headers


def test_deletion_api_receipt_keeps_named_retention_basis_reason_and_unspecified_expiry(
    client, account, monkeypatch
):
    monkeypatch.setattr(storage, 'journal_accept', lambda *_: {
        'version_id': 'fictional-accepted-journal-version', 'sha256': 'a' * 64})
    accepted = client.post('/v1/privacy/deletion-requests', headers=headers(),
        json={'scope': 'all_data', 'confirmation': True})
    assert accepted.status_code == 202, accepted.text
    receipt = accepted.json()
    expected = {'identity_and_generation_barriers', 'audit_and_security_metadata',
        'minimal_operation_receipts', 'operator_membership_references',
        'private_cleanup_references', 'deletion_journal'}
    entries = receipt['retained_categories']
    assert len(entries) == len(expected)
    assert all(isinstance(entry, dict) for entry in entries)
    assert {entry['category'] for entry in entries} == expected
    for entry in entries:
        assert set(entry) == {'category', 'policy_basis', 'reason', 'expires_at'}
        assert 0 < len(entry['category']) <= 256 and entry['policy_basis'] == 'privacy-v1'
        assert 0 < len(entry['reason']) <= 1000
        assert entry['expires_at'] is None, 'No configured destruction date must be invented'
    refreshed = client.get('/v1/privacy/jobs/' + receipt['job_id'], headers=headers(gen=2))
    assert refreshed.status_code == 200, refreshed.text
    assert refreshed.json()['retained_categories'] == entries
    assert receipt['schema_version'] == '1.0.0' and receipt['kind'] == 'deletion'
    assert receipt['state'] == 'pending' and receipt['policy_version'] == 'privacy-v1'
    assert 'download_path' not in receipt and 'raw_export' not in receipt
    with factory()() as db:
        assert db.get(Account, account).state == 'deleting'
        assert db.get(Job, receipt['job_id']).journal_accepted is True
    # Explicit opt-in captures an actual fictional HTTP response for the client
    # parser/renderer regression, without editing static fixtures on normal runs.
    if destination := os.environ.get('OTGD_WRITE_PRIVACY_RECEIPT_FIXTURE'):
        Path(destination).write_text(json.dumps(receipt, indent=2) + '\n')
