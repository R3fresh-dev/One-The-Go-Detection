"""Explicit fictional raw-export lifecycle; no human authority is provisioned."""
from copy import deepcopy
import asyncio
import hashlib
import io
import json
from pathlib import Path
import time
import zipfile

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, select
from sqlalchemy.pool import StaticPool
from starlette.requests import Request

from otgd import raw_export as export
from otgd import raw_retention as retention
from otgd import worker, main
from otgd.canonical import canonical, digest, strict_loads
from otgd.db import Account, Artifact, Check, Job, Outbox, Record, SystemState, iso
from otgd.domain import rec_id
from otgd.dto import ExportRequest, RawExportScope
from otgd.errors import Problem
from otgd.operator_governance import submit, transition
from otgd.raw_capture import verification_receipt
from . import test_raw_retention as raw_fixture
from .conftest import headers
from .governance_fixture import approve
from .test_optical_evidence import fixture as native_fixture, roi_fixture

TICK = raw_fixture.TICK+10
# Actual bounded ROI codec for the fictional pixel vectors, with no human
# recording or physical/anatomical qualification.
DATA = roi_fixture()[0]
JOB = '70000000-0000-4000-8000-000000000001'


def grant(**changes):
    text = 'FICTIONAL participant-copy export only. Shared copies cannot be recalled.'
    return {
        'schema_version': '1.0.0', 'registry_id': 'FICTIONAL-RAW-EXPORT',
        'authorization_id': 'FICTIONAL-RAW-EXPORT', 'version': 'v1', 'expires_at': TICK+864000,
        'evidence_ref': 'FICTIONAL-SOFTWARE-EVIDENCE-NO-HUMAN-APPROVAL', 'evidence_sha256': 'e'*64,
        'account_ref': raw_fixture.ACCOUNT, 'data_generation': 1, 'study_id': 'FICTIONAL-STUDY',
        'raw_kinds': ['eye_video'], 'purpose': 'participant_requested_raw_export',
        'purpose_id': 'FICTIONAL-PARTICIPANT-COPY', 'purpose_text': 'Fictional participant copy for software tests only.',
        'retention_policy_id': raw_fixture.POLICY['policy_id'], 'retention_policy_version': 'v1',
        'retention_policy_sha256': digest(raw_fixture.POLICY), 'export_notice_version': 'v1',
        'export_notice_text': text, 'export_notice_sha256': hashlib.sha256(text.encode()).hexdigest(),
        'max_export_lifetime_seconds': 3600, 'max_uncompressed_bytes': 50*1024*1024,
        'max_archive_bytes': 64*1024*1024, **changes,
    }


def scope(value=None, **changes):
    value = value or grant()
    return RawExportScope.model_validate({
        'authorization_id': value['authorization_id'], 'authorization_version': value['version'],
        'authorization_sha256': digest(value), 'export_notice_version': value['export_notice_version'],
        'export_notice_sha256': value['export_notice_sha256'], 'acknowledged_at': iso(TICK),
        'confirmed': True, 'artifact_ids': [raw_fixture.ARTIFACT], **changes,
    })


def seed_fictional_verification(db, artifact):
    """Storage/lineage unit proof only, not native codec or hardware acceptance."""
    lifetime = db.get(retention.RawRetention, artifact.id)
    config = retention.active_body(db, 'configuration', lifetime.authority['configuration_id'])
    account = db.get(Account, artifact.account_id)
    attempt = retention.record(db, account, 'attempt', lifetime.authority['attempt_id'])
    native, projection, _ = native_fixture()
    native.update(run_id=attempt.body.get('record_id', raw_fixture.ATTEMPT), configuration_sha256=config['sha256'],
        started_at=iso(raw_fixture.TICK+1), ended_at=iso(raw_fixture.TICK+2))
    projection.update(capture_config_id=config['configuration_id'], started_at=native['started_at'], ended_at=native['ended_at'])
    attempt.body = {**attempt.body, 'attempt_id':lifetime.authority['attempt_id'], 'record_id':native['run_id'],
        'status':'valid', 'source':'prototype_sensor', 'configuration_id':config['configuration_id'],
        'configuration_hash':config['sha256'], 'started_at':native['started_at'], 'ended_at':native['ended_at'],
        'component_metadata':{'native_result':native, 'projection':projection}}
    attempt.sha256 = digest(attempt.body)
    proof = verification_receipt(artifact, config, artifact.version_id,
        {'codec':'otgd_eye_roi_v1', 'evidence_sha256':digest(native)})
    id = rec_id(account, 'raw_verification', artifact.id)
    db.merge(Record(id=id, account_id=account.id, generation=account.generation, kind='raw_verification',
        parent_id=artifact.session_id, body=proof, sha256=digest(proof), created=TICK))


@pytest.fixture
def fixture(monkeypatch):
    # The real HTTP app uses another thread; keep this disposable SQLite engine
    # shared across threads. PostgreSQL behavior is qualified in the live gate.
    monkeypatch.setattr(raw_fixture, 'create_engine', lambda _: create_engine('sqlite://',
        connect_args={'check_same_thread': False}, poolclass=StaticPool))
    setup = raw_fixture.fixture.__wrapped__(monkeypatch)
    fixture = next(setup)
    monkeypatch.setattr(export, 'now', lambda: TICK)
    monkeypatch.setattr(main, 'now', lambda: TICK)
    monkeypatch.setattr(worker, 'now', lambda: TICK)
    with fixture.sessions.begin() as db:
        account, check, request = raw_fixture.consent_and_attempt(db)
        request = request.model_copy(update={'sha256': hashlib.sha256(DATA).hexdigest(), 'size_bytes':len(DATA)})
        artifact, retained = raw_fixture.attach(db, account, check, request)
        artifact.size = len(DATA)
        artifact.state = 'verified'; artifact.version_id = 'fictional-source-version-1'
        monkeypatch.setattr('otgd.db.now', lambda: TICK)
        monkeypatch.setattr(retention, 'now', lambda: TICK)
        seed_fictional_verification(db, artifact)
        from otgd.optical_evidence import validate_roi_artifact
        native_attempt = retention.record(db, account, 'attempt', raw_fixture.ATTEMPT)
        config = retention.active_body(db, 'configuration', retained.authority['configuration_id'])
        assert validate_roi_artifact(DATA, native_attempt.body, config)['codec']=='otgd_eye_roi_v1'
        check.state = 'completed'
    monkeypatch.setattr('otgd.db.now', lambda: TICK)
    yield fixture
    try:
        next(setup)
    except StopIteration:
        pass


def accepted(db, value=None):
    value = value or grant()
    approve(db, 'raw_export', value)
    account = db.get(Account, raw_fixture.ACCOUNT)
    selected = scope(value)
    frozen = export.freeze_export(db, account, selected, [raw_fixture.CHECK])
    job = Job(id=JOB, account_id=account.id, generation=1, kind='export', state='pending',
        body={'include_raw': True, 'format': 'json_zip', 'raw_scope': selected.data(),
            'selection': {'kind': 'single', 'session_ids': [raw_fixture.CHECK]},
            'session_ids': [raw_fixture.CHECK], 'profile_version_ids': [],
            'current_profile_version_id': None, 'report_revision_heads': {}, 'raw_export': frozen['raw_export']},
        accepted=TICK, expires=frozen['expires_at'], attempts=0, fence=0)
    db.add(job); db.flush(); db.add(Outbox(job_id=job.id))
    return account, job


class SourceStore:
    def __init__(self, *, data=DATA, after_read=None, **changes):
        self.data = data; self.after_read = after_read; self.changes = changes
        self.reads = []; self.streams = []; self.versions = {}; self.deleted = []

    def get_object(self, **request):
        self.reads.append(request)
        parent = self
        class Stream(io.BytesIO):
            def read(self, count=-1):
                parent.read_bound = count
                data = super().read(count)
                if parent.after_read:
                    parent.after_read(); parent.after_read = None
                return data
        stream = Stream(self.data); self.streams.append(stream)
        return {'VersionId': 'fictional-source-version-1', 'ContentLength': len(DATA),
            'ContentType': 'application/octet-stream', 'Body': stream, **self.changes}

    def get_paginator(self, name):
        assert name == 'list_object_versions'
        return self

    def paginate(self, **request):
        yield {'Versions': [{'Key': key, 'VersionId': version} for key, versions in self.versions.items()
            for version in versions if key.startswith(request['Prefix']) and not version.startswith('marker')],
            'DeleteMarkers': [{'Key': key, 'VersionId': version} for key, versions in self.versions.items()
            for version in versions if key.startswith(request['Prefix']) and version.startswith('marker')]}

    def delete_object(self, **request):
        self.deleted.append(request)
        self.versions[request['Key']].remove(request['VersionId'])


def current(db, claim):
    account, job = db.get(Account, claim.account_id), db.get(Job, claim.id)
    if job.state != 'running' or job.fence != claim.fence:
        raise worker.LeaseLost()
    return account, job


def claim_for(db):
    account, job = accepted(db)
    job.state = 'running'; job.fence = 1; job.started = TICK; job.lease_until = TICK+120
    return worker.Claim(job.id, job.account_id, job.generation, job.kind, 1, TICK, deepcopy(job.body))


def test_recording_upload_approval_never_grants_export(fixture):
    with fixture.sessions.begin() as db:
        assert export.available_scopes(db, db.get(Account, raw_fixture.ACCOUNT))['scopes'] == []
        with pytest.raises(Problem, match='APPROVED_REGISTRY_VERSION_REQUIRED'):
            export.freeze_export(db, db.get(Account, raw_fixture.ACCOUNT), scope(), [raw_fixture.CHECK])


def test_actual_distinct_release_freezes_exact_sources_and_public_scope(fixture):
    with fixture.sessions.begin() as db:
        account, job = accepted(db)
        frozen = export.validate_job(db, account, job)
        assert job.expires == TICK+3600
        assert frozen['sources'][0]['version_id'] == 'fictional-source-version-1'
        public = export.available_scopes(db, account)['scopes'][0]
        assert public['artifacts'][0]['artifact_id'] == raw_fixture.ARTIFACT
        assert public['export_notice']['sha256'] == hashlib.sha256(public['export_notice']['content'].encode()).hexdigest()
        assert not {'bucket','key','version_id','sha256'} & set(public['artifacts'][0])
        assert export.public_job_scope(job)['sources'][0]['sha256'] == hashlib.sha256(DATA).hexdigest()
        assert not {'bucket','key'} & set(export.public_job_scope(job)['sources'][0])


def test_distinct_submit_review_release_required(fixture):
    with fixture.sessions.begin() as db:
        value = grant(); submit(db, 'raw_export', value, 'local:submitter')
        with pytest.raises(Problem, match='INDEPENDENT_REVIEW_REQUIRED'):
            transition(db, 'raw_export', value['registry_id'], 'v1', 'approve', 'local:submitter', 'Fictional review', 1)
        transition(db, 'raw_export', value['registry_id'], 'v1', 'approve', 'local:reviewer', 'Fictional review', 1)
        with pytest.raises(Problem, match='INDEPENDENT_RELEASE_REQUIRED'):
            transition(db, 'raw_export', value['registry_id'], 'v1', 'release', 'local:reviewer', 'Fictional release', 2)
        with pytest.raises(Problem):
            export.freeze_export(db, db.get(Account, raw_fixture.ACCOUNT), scope(value), [raw_fixture.CHECK])


@pytest.mark.parametrize('change', [
    {'purpose': 'measurement_collection'}, {'raw_kinds': ['source_lab_report']}, {'raw_kinds': ['eye_video','eye_video']},
    {'max_uncompressed_bytes': export.MAX_UNCOMPRESSED+1}, {'max_archive_bytes': export.MAX_ARCHIVE+1},
    {'max_export_lifetime_seconds': 86401}, {'export_notice_sha256': '0'*64}, {'authorization_id': 'different'},
])
def test_typed_authority_rejects_unapproved_purpose_and_unbounded_scope(change):
    with pytest.raises(ValidationError):
        export.RawExportAuthorization.model_validate(grant(**change))


@pytest.mark.parametrize('change', [{'confirmed': 1}, {'artifact_ids': []}, {'artifact_ids': [raw_fixture.ARTIFACT]*2},
    {'bucket': 'caller-supplied'}])
def test_explicit_participant_scope_has_no_truthy_or_arbitrary_storage_escape(change):
    with pytest.raises(ValidationError):
        scope(**change)


def test_metadata_only_request_remains_default_scope_and_cannot_carry_raw_approval():
    body = {'selection': {'kind': 'single','session_ids':[raw_fixture.CHECK]}, 'format':'json_zip', 'include_raw':False}
    assert ExportRequest.model_validate(body).raw_scope is None
    for changed in ({**body, 'include_raw':True}, {**body, 'raw_scope':scope().data()}, {**body, 'include_raw':1}):
        with pytest.raises(ValidationError):
            ExportRequest.model_validate(changed)


@pytest.mark.parametrize('change', [{'authorization_version':'v2'}, {'authorization_sha256':'0'*64},
    {'export_notice_version':'v2'}, {'export_notice_sha256':'0'*64}, {'artifact_ids':['50000000-0000-4000-8000-000000000002']},
    {'acknowledged_at':iso(TICK-601)}, {'acknowledged_at':iso(TICK+6)}])
def test_scope_revision_hash_owner_and_confirmation_clock_rechecked(fixture, change):
    with fixture.sessions.begin() as db:
        approve(db, 'raw_export', grant())
        with pytest.raises(Problem):
            export.freeze_export(db, db.get(Account, raw_fixture.ACCOUNT), scope(**change), [raw_fixture.CHECK])


@pytest.mark.parametrize('mutate', ['generation','foreign_account','unselected_check','quarantine','no_version','null_version','retention_closed','raw_revoke','withdraw'])
def test_live_sources_and_consent_reject_scope_changes(fixture, mutate):
    with fixture.sessions.begin() as db:
        account, job = accepted(db)
        artifact = db.get(Artifact, raw_fixture.ARTIFACT)
        if mutate == 'generation': account.generation = 2
        if mutate == 'foreign_account': artifact.account_id = '10000000-0000-4000-8000-000000000002'
        if mutate == 'unselected_check': artifact.session_id = '20000000-0000-4000-8000-000000000002'
        if mutate == 'quarantine': artifact.state = 'quarantine'
        if mutate == 'no_version': artifact.version_id = None
        if mutate == 'null_version': artifact.version_id = 'null'
        if mutate == 'retention_closed': db.get(retention.RawRetention, artifact.id).state = 'cleanup_pending'
        if mutate == 'raw_revoke': retention.revoke_raw(db, account, 'FICTIONAL-STUDY', retention.RawRevocation(confirmation=True,artifact_kinds=['eye_video']))
        if mutate == 'withdraw':
            consent = db.get(Record, rec_id(account, 'consent', 'FICTIONAL-STUDY'))
            consent.body = {**consent.body,'state':'withdrawn'}
        with pytest.raises(Problem): export.validate_job(db, account, job)


def test_bounded_exact_version_read_and_raw_member_manifest(fixture):
    with fixture.sessions.begin() as db: claim = claim_for(db)
    storage = SourceStore()
    files, manifest = export.read_sources(claim, fixture.sessions, current, storage)
    path = f'raw/eye_video/{raw_fixture.ARTIFACT}.bin'
    assert files == {path:DATA}
    assert storage.reads == [{'Bucket':'fictional-raw-bucket','Key':'quarantine/fictional/'+raw_fixture.ARTIFACT,'VersionId':'fictional-source-version-1'}]
    assert storage.read_bound == len(DATA)+1 and storage.streams[0].closed
    assert manifest['sources'][0]['path'] == path


@pytest.mark.parametrize('change', [{'VersionId':'other'}, {'ContentLength':127}, {'ContentType':'text/plain'}, {'data':DATA[:-1]}, {'data':b'x'*128}, {'data':DATA+b'excess'}])
def test_version_length_type_hash_and_read_limit_failure_never_returns_partial_file(fixture, change):
    with fixture.sessions.begin() as db: claim = claim_for(db)
    storage = SourceStore(**change)
    with pytest.raises(Problem, match='RAW_EXPORT_SOURCE_INVALID'):
        export.read_sources(claim, fixture.sessions, current, storage)
    assert storage.streams[0].closed


def test_consent_revoked_during_storage_read_blocks_publication(fixture):
    with fixture.sessions.begin() as db: claim = claim_for(db)
    def revoke():
        with fixture.sessions.begin() as db:
            row = db.get(Record, raw_fixture.ACCOUNT+':consent:FICTIONAL-STUDY')
            row.body = {**row.body,'state':'withdrawn'}
    storage = SourceStore(after_read=revoke)
    with pytest.raises(Problem, match='CURRENT_CONSENT_REQUIRED'):
        export.read_sources(claim, fixture.sessions, current, storage)


def test_late_export_versions_and_markers_are_recurring_scoped_cleanup(fixture, monkeypatch):
    with fixture.sessions.begin() as db:
        account, job = accepted(db)
        retention.revoke_raw(db, account, 'FICTIONAL-STUDY', retention.RawRevocation(confirmation=True,artifact_kinds=['eye_video']))
    storage = SourceStore(); prefix = f'exports/{raw_fixture.ACCOUNT}/1/{JOB}/'
    storage.versions = {prefix+'1.zip':['v1','marker1'], prefix+'2.zip':['v2'], 'exports/neighbor/1/other/1.zip':['neighbor']}
    first = export.cleanup_once(fixture.sessions, storage, tick=TICK)
    assert first == {'processed':1,'purged':1,'failures':0}
    assert storage.versions['exports/neighbor/1/other/1.zip'] == ['neighbor']
    with fixture.sessions.begin() as db:
        job = db.get(Job, JOB)
        assert job.state == 'revoked' and job.fence == 1 and job.output is None
    storage.versions[prefix+'stale.zip'] = ['late-version']
    export.cleanup_once(fixture.sessions, storage, tick=TICK+901)
    assert storage.versions[prefix+'stale.zip'] == []


def test_expiry_and_retention_are_hard_caps_and_generation_deletion_denies(fixture, monkeypatch):
    with fixture.sessions.begin() as db:
        account, job = accepted(db, grant(expires_at=float(TICK+120)))
        assert job.expires == TICK+120
        monkeypatch.setattr(export, 'now', lambda:TICK+120)
        assert export.public_job_scope(job) is None
        with pytest.raises(Problem): export.validate_job(db, account, job)
        account.generation += 1; account.state = 'deleting'
        with pytest.raises(Problem): export.validate_job(db, account, job)


def install_full_evidence(db):
    """Reuse the independently verified fictional wire record, rehashing IDs."""
    root = Path(__file__).resolve().parents[3]
    original = strict_loads((root/'apps/mobile/testfixtures/fictional-check-contract.json').read_bytes())
    eye = next(attempt for attempt in original['attempts'] if attempt['component']=='eyes')
    document = json.dumps(original).replace(original['id'], raw_fixture.CHECK).replace(eye['attempt_id'], raw_fixture.ATTEMPT)
    full = json.loads(document)
    account = db.get(Account, raw_fixture.ACCOUNT)
    eye = next(attempt for attempt in full['attempts'] if attempt['component']=='eyes')
    eye.update(deepcopy(retention.record(db,account,'attempt',raw_fixture.ATTEMPT).body))
    snapshot = full['snapshot']; snapshot['subject_ref'] = raw_fixture.ACCOUNT
    snapshot['mode'] = 'analytical'
    snapshot['eyes'] = deepcopy(eye['component_metadata']['projection'])
    snapshot['capture_completed_at'] = eye['ended_at']
    snapshot['acquisition_span_ms'] = 2000
    check = db.get(Check, raw_fixture.CHECK)
    snapshot['study_id'] = check.study_id; snapshot['protocol_id'] = check.protocol_id
    full['context']['protocol_id'] = check.protocol_id
    full['manifest']['context_sha256'] = digest(full['context'])
    full['manifest']['attempts'] = [{'attempt_id':attempt['attempt_id'],'sha256':digest(attempt)} for attempt in full['attempts']]
    account = db.get(Account, raw_fixture.ACCOUNT)
    for kind, id, body in [('context',raw_fixture.CHECK,full['context']),('manifest',raw_fixture.CHECK,full['manifest']),
        ('alcohol',raw_fixture.CHECK,full['alcohol'])]+[('attempt',attempt['attempt_id'],attempt) for attempt in full['attempts']]:
        row = db.get(Record, rec_id(account, kind, id))
        if row:
            row.body = body; row.sha256 = digest(body)
        else:
            db.add(Record(id=rec_id(account,kind,id),account_id=account.id,generation=1,kind=kind,parent_id=raw_fixture.CHECK,
                body=body,sha256=digest(body),created=TICK))
    check.mode = snapshot['mode']
    check.created = retention.timestamp(snapshot['created_at'])
    check.snapshot = snapshot; check.snapshot_sha256 = digest(snapshot)
    check.evidence_sha256 = digest(full['manifest'])
    result = full['result']; result['input_sha256'] = check.snapshot_sha256
    result['evaluated_at'] = iso(TICK)
    result['provenance_summary'] = sorted({attempt['source'] for attempt in full['attempts']} | {snapshot['task']['source']})
    check.result = result


@pytest.fixture
def http(fixture, client, monkeypatch):
    # Real JWT verification/HTTP DTO/worker code; only storage/SQLite are unit
    # dependencies. No ephemeral API fixture creates a production authority.
    from otgd import auth, db as database
    with database.factory()() as db:
        state = [(row.key, deepcopy(row.body)) for row in db.scalars(select(SystemState))]
    with fixture.sessions.begin() as db:
        account = db.get(Account, raw_fixture.ACCOUNT)
        account.subject_hash = auth.subject_hash({'sub':'a'})
        for key, body in state:
            db.merge(SystemState(key=key,body=body))
        install_full_evidence(db)
        approve(db, 'raw_export', grant())
    monkeypatch.setattr(main, 'factory', lambda: fixture.sessions)
    monkeypatch.setattr(worker, 'factory', lambda: fixture.sessions)
    return client


def live_headers(sub='a', **kwargs):
    current = int(time.time())
    return headers(sub, iat=current, auth_time=current, exp=current+900, **kwargs)


class ArchiveStore(SourceStore):
    def __init__(self):
        super().__init__(); self.archives = {}; self.archive_changes = {}; self.after_archive_read = None

    def put_versioned(self, bucket, key, data, media_type, **kwargs):
        version = 'fictional-export-version-1'
        self.archives[(bucket,key,version)] = (data,media_type)
        return version

    def get_object(self, **request):
        if request['Key'].startswith('exports/'):
            data, media = self.archives[(request['Bucket'],request['Key'],request['VersionId'])]
            parent = self
            class Stream(io.BytesIO):
                def read(self, count=-1):
                    parent.archive_read_bound = count
                    result = super().read(count)
                    if parent.after_archive_read:
                        parent.after_archive_read(); parent.after_archive_read = None
                    return result
            stream = Stream(data); self.streams.append(stream)
            return {'VersionId':request['VersionId'],'ContentLength':len(data),'ContentType':media,'Body':stream, **self.archive_changes}
        return super().get_object(**request)


def test_actual_http_async_worker_zip_download_replay_expiry_and_foreign_denial(http, fixture, monkeypatch, tmp_path):
    monkeypatch.setattr(main, 'uid', lambda: JOB)
    store = ArchiveStore()
    monkeypatch.setattr(worker.storage,'client',lambda service:store)
    monkeypatch.setattr(worker.storage,'put_versioned',store.put_versioned)
    public = http.get('/v1/privacy/raw-export-scopes',headers=live_headers())
    assert public.status_code == 200, public.text
    assert public.json()['scopes'][0]['authorization_sha256'] == digest(grant())
    body = {'selection':{'kind':'single','session_ids':[raw_fixture.CHECK]},'format':'json_zip','include_raw':True,'raw_scope':scope().data()}
    request_headers = live_headers(key='80000000-0000-4000-8000-000000000001')
    accepted = http.post('/v1/privacy/exports',headers=request_headers,json=body)
    assert accepted.status_code == 202, accepted.text
    id = accepted.json()['job_id']; path = '/v1/privacy/jobs/'+id
    assert accepted.json()['scope'] == body['selection'] and accepted.json()['raw_export']['purpose'] == 'participant_requested_raw_export'
    assert http.post('/v1/privacy/exports',headers=request_headers,json=body).json()['job_id'] == id
    assert http.get(path,headers=live_headers()).json()['state'] == 'pending'
    assert worker.run_job(id) == 'completed'
    done = http.get(path,headers=live_headers())
    assert done.status_code == 200 and done.json()['state'] == 'completed', done.text
    download = http.get(path+'/download',headers=live_headers())
    assert download.status_code == 200, download.text
    assert download.headers['cache-control'] == 'private, no-store'
    assert download.headers['content-disposition'] == f'attachment; filename="otgd-{id}.zip"'
    assert download.headers['content-type'] == 'application/zip'
    assert store.archive_read_bound == len(download.content)+1 and store.streams[-1].closed
    assert hashlib.sha256(download.content).hexdigest() == done.json()['sha256']
    with zipfile.ZipFile(io.BytesIO(download.content)) as archive:
        manifest = strict_loads(archive.read('manifest.json'))
        assert manifest['raw_export'] == done.json()['raw_export']
        assert manifest['omitted_categories'] == ['unselected_raw_artifacts','source_lab_reports']
        for item in manifest['files']:
            data = archive.read(item['path'])
            assert len(data) == item['size_bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
        assert archive.read(f'raw/eye_video/{raw_fixture.ARTIFACT}.bin') == DATA
    assert http.get(path+'/download').status_code == 401
    assert http.get(path+'/download',headers=live_headers('b')).status_code == 404
    assert http.get(path+'/download',headers={**live_headers(),'Range':'bytes=0-1'}).status_code == 416
    # These exact worker-produced fictional wire/ZIP files qualify the mobile
    # reader against backend output; writing fixtures is a separate explicit run.
    fixture_dir = tmp_path/'fixture'
    fixture_dir.mkdir()
    (fixture_dir/'raw-export-scopes.json').write_bytes(canonical(public.json()))
    (fixture_dir/'raw-export-job.json').write_bytes(canonical(done.json()))
    (fixture_dir/'raw-export.zip').write_bytes(download.content)
    monkeypatch.setattr(export,'now',lambda:TICK+3600)
    monkeypatch.setattr(main,'now',lambda:TICK+3600)
    expired = http.get(path,headers=live_headers())
    assert expired.status_code == 200 and expired.json()['state']=='expired'
    assert 'raw_export' not in expired.json() and 'download_path' not in expired.json()
    assert http.get(path+'/download',headers=live_headers()).status_code == 410


def test_http_accepted_raw_replay_and_new_download_are_denied_after_revocation(http, fixture, monkeypatch):
    store = ArchiveStore()
    monkeypatch.setattr(worker.storage,'client',lambda service:store)
    monkeypatch.setattr(worker.storage,'put_versioned',store.put_versioned)
    body = {'selection':{'kind':'single','session_ids':[raw_fixture.CHECK]},'format':'json_zip','include_raw':True,'raw_scope':scope().data()}
    request_headers = live_headers(key='80000000-0000-4000-8000-000000000002')
    accepted = http.post('/v1/privacy/exports',headers=request_headers,json=body)
    assert accepted.status_code == 202, accepted.text
    id = accepted.json()['job_id']; assert worker.run_job(id)=='completed'
    with fixture.sessions.begin() as db:
        account = db.get(Account,raw_fixture.ACCOUNT)
        retention.revoke_raw(db,account,'FICTIONAL-STUDY',retention.RawRevocation(confirmation=True,artifact_kinds=['eye_video']))
    replay = http.post('/v1/privacy/exports',headers=request_headers,json=body)
    assert replay.status_code == 403
    assert http.get('/v1/privacy/jobs/'+id+'/download',headers=live_headers()).status_code == 403
    assert http.get('/v1/privacy/raw-export-scopes',headers=live_headers()).json()['scopes'][0]['artifacts'] == []


def test_accepted_post_replay_after_export_authority_retirement_hides_original_scope(http, fixture):
    body = {'selection': {'kind': 'single', 'session_ids': [raw_fixture.CHECK]},
        'format': 'json_zip', 'include_raw': True, 'raw_scope': scope().data()}
    original_headers = live_headers(key='80000000-0000-4000-8000-000000000003')
    accepted_response = http.post('/v1/privacy/exports', headers=original_headers, json=body)
    assert accepted_response.status_code == 202, accepted_response.text
    job_id = accepted_response.json()['job_id']
    with fixture.sessions.begin() as db:
        original = deepcopy(db.get(Job, job_id).body)
        transition(db, 'raw_export', grant()['registry_id'], 'v1', 'retire',
            'local:fixture-releaser', 'Fictional export authority retirement, not consent withdrawal', 3)
        owner = db.get(Account, raw_fixture.ACCOUNT)
        assert retention.record(db, owner, 'consent', 'FICTIONAL-STUDY').body['state'] == 'active'
    replay = http.post('/v1/privacy/exports', headers=original_headers, json=body)
    assert replay.status_code == 403, replay.text
    assert replay.json()['code'] == 'APPROVED_REGISTRY_VERSION_REQUIRED'
    assert not {'raw_export', 'download_path', 'scope', 'job_id'} & replay.json().keys()
    with fixture.sessions() as db:
        jobs = list(db.scalars(select(Job).where(Job.kind == 'export')))
        assert len(jobs) == 1 and jobs[0].id == job_id
        assert jobs[0].body == original and jobs[0].state == 'pending'


def test_raw_members_fit_but_complete_structured_manifest_archive_exceeds_grant(fixture, monkeypatch):
    cap = len(DATA) + 1
    store = ArchiveStore()
    monkeypatch.setattr(worker, 'factory', lambda: fixture.sessions)
    monkeypatch.setattr(worker.storage, 'client', lambda service: store)
    monkeypatch.setattr(worker.storage, 'put_versioned', store.put_versioned)
    with fixture.sessions.begin() as db:
        install_full_evidence(db)
        owner, job = accepted(db, grant(max_uncompressed_bytes=cap))
        frozen = export.validate_job(db, owner, job)
        assert sum(source['size_bytes'] for source in frozen['sources']) == len(DATA) < cap
        structured = canonical(main.detail(db.get(Check, raw_fixture.CHECK)))
        assert len(structured) <= 512 * 1024
        assert len(structured) + len(DATA) > cap
    assert worker.run_job(JOB) == 'failed'
    with fixture.sessions() as db:
        job = db.get(Job, JOB)
        assert job.state == 'failed' and job.failure == 'EXPORT_TOO_LARGE'
        assert job.output is None and job.completed is None
        assert job.body['raw_export']['authorization']['max_uncompressed_bytes'] == cap
    assert store.reads and store.streams[-1].closed
    assert store.archives == {}, 'Overflow must not publish a partial ZIP'


def test_http_revoked_cleanup_has_minimal_terminal_receipt(http, fixture, monkeypatch, tmp_path):
    store, path = completed_http_export(http, monkeypatch)
    with fixture.sessions.begin() as db:
        account = db.get(Account, raw_fixture.ACCOUNT)
        retention.revoke_raw(db, account, 'FICTIONAL-STUDY', retention.RawRevocation(confirmation=True, artifact_kinds=['eye_video']))
        job = db.get(Job, path.split('/')[-2])
        prefix = f'exports/{account.id}/{account.generation}/{job.id}/'
    store.versions[prefix+'1.zip'] = ['fictional-export-version-1']
    assert export.cleanup_once(fixture.sessions, store)['purged']==1
    response = http.get(path.removesuffix('/download'), headers=live_headers())
    assert response.status_code==200 and response.json()['state']=='revoked', response.text
    assert not {'raw_export','download_path','sha256','size_bytes'} & response.json().keys()
    assert http.get(path, headers=live_headers()).status_code in (403,409)
    (tmp_path/'raw-export-revoked-job.json').write_bytes(canonical(response.json()))


def completed_http_export(http, monkeypatch, store=None):
    store = store or ArchiveStore()
    monkeypatch.setattr(worker.storage, 'client', lambda service: store)
    monkeypatch.setattr(worker.storage, 'put_versioned', store.put_versioned)
    body = {'selection': {'kind': 'single', 'session_ids': [raw_fixture.CHECK]},
        'format': 'json_zip', 'include_raw': True, 'raw_scope': scope().data()}
    accepted = http.post('/v1/privacy/exports', headers=live_headers(), json=body)
    assert accepted.status_code == 202, accepted.text
    id = accepted.json()['job_id']
    assert worker.run_job(id) == 'completed'
    return store, '/v1/privacy/jobs/'+id+'/download'


@pytest.mark.parametrize('boundary', ['raw_revocation', 'expiry', 'account_deletion', 'authority_retirement'])
def test_delayed_http_download_discloses_no_bytes_after_current_authority_loss(http, fixture, monkeypatch, boundary):
    store, path = completed_http_export(http, monkeypatch)
    def change():
        if boundary == 'expiry':
            monkeypatch.setattr(export, 'now', lambda: TICK+3600)
            monkeypatch.setattr(main, 'now', lambda: TICK+3600)
            return
        with fixture.sessions.begin() as db:
            account = db.get(Account, raw_fixture.ACCOUNT)
            if boundary == 'raw_revocation':
                retention.revoke_raw(db, account, 'FICTIONAL-STUDY', retention.RawRevocation(confirmation=True, artifact_kinds=['eye_video']))
            elif boundary == 'account_deletion':
                account.generation += 1; account.state = 'deleting'
            else:
                transition(db, 'raw_export', grant()['registry_id'], 'v1', 'retire',
                    'local:fixture-releaser', 'Fictional retirement', 3)
    store.after_archive_read = change
    response = http.get(path, headers=live_headers())
    assert response.status_code in (403, 410), response.text
    assert 'application/zip' not in response.headers['content-type']
    assert store.streams[-1].closed
    assert export.DOWNLOAD_SLOTS.acquire(blocking=False)
    export.DOWNLOAD_SLOTS.release()


@pytest.mark.parametrize('changes', [{'VersionId':'foreign-version'}, {'VersionId':'null'},
    {'ContentLength':1}, {'Body':io.BytesIO(b'forged archive')}])
def test_http_download_requires_exact_version_size_and_digest_and_releases_capacity(http, monkeypatch, changes):
    store, path = completed_http_export(http, monkeypatch)
    store.archive_changes = changes
    denied = http.get(path, headers=live_headers())
    assert denied.status_code == 503, denied.text
    assert 'application/zip' not in denied.headers['content-type']
    store.archive_changes = {}
    assert http.get(path, headers=live_headers()).status_code == 200


def test_http_download_capacity_is_bounded_and_busy_is_retryable(http, monkeypatch):
    _, path = completed_http_export(http, monkeypatch)
    assert export.DOWNLOAD_SLOTS.acquire(blocking=False)
    try:
        denied = http.get(path, headers=live_headers())
        assert denied.status_code == 429 and denied.headers['retry-after']=='1'
    finally:
        export.DOWNLOAD_SLOTS.release()
    assert http.get(path, headers=live_headers()).status_code == 200


def download_request(path):
    return Request({'type':'http','asgi':{'version':'3.0','spec_version':'2.4'}, 'method':'GET',
        'path':path,'headers':[(key.lower().encode(), value.encode()) for key,value in live_headers().items()]})


def test_admitted_asgi_download_stops_at_next_64k_chunk_after_revocation(http, fixture, monkeypatch):
    # Deterministic fictional, incompressible bytes make the actual worker ZIP
    # cross more than one delivery boundary. No human waveform is introduced.
    data = b''.join(hashlib.sha256(str(n).encode()).digest() for n in range(4096))
    with fixture.sessions.begin() as db:
        artifact = db.get(Artifact, raw_fixture.ARTIFACT)
        artifact.size = len(data); artifact.sha256 = hashlib.sha256(data).hexdigest()
        row = db.get(retention.RawRetention, artifact.id)
        row.authority = {**row.authority, 'artifact_sha256':artifact.sha256}
        seed_fictional_verification(db, artifact)
    store = ArchiveStore(); store.data = data; store.changes = {'ContentLength':len(data)}
    store, path = completed_http_export(http, monkeypatch, store)
    request = download_request(path)
    response = main.privacy_download(request, path.split('/')[-2])
    sent = []
    async def send(message):
        if message['type']=='http.response.body' and message.get('body'):
            sent.append(message['body'])
            with fixture.sessions.begin() as db:
                retention.revoke_raw(db, db.get(Account, raw_fixture.ACCOUNT), 'FICTIONAL-STUDY',
                    retention.RawRevocation(confirmation=True, artifact_kinds=['eye_video']))
    async def receive():
        return {'type':'http.request'}
    with pytest.raises(Problem):
        asyncio.run(response(request.scope, receive, send))
    assert len(sent)==1 and len(sent[0])==64*1024
    assert export.DOWNLOAD_SLOTS.acquire(blocking=False)
    export.DOWNLOAD_SLOTS.release()


def test_download_cancelled_before_first_generator_iteration_releases_buffer_slot(http, monkeypatch):
    _, path = completed_http_export(http, monkeypatch)
    request = download_request(path)
    response = main.privacy_download(request, path.split('/')[-2])
    async def send(_):
        raise asyncio.CancelledError()
    async def receive():
        return {'type':'http.request'}
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(response(request.scope, receive, send))
    assert export.DOWNLOAD_SLOTS.acquire(blocking=False)
    export.DOWNLOAD_SLOTS.release()


def test_current_authority_pages_have_bounded_bytes_and_explicit_complete_cursors(fixture):
    with fixture.sessions.begin() as db:
        account = db.get(Account, raw_fixture.ACCOUNT)
        ids = set()
        for n in range(9):
            name = f'FICTIONAL-RAW-EXPORT-{n}'
            text = 'F'*16384
            value = grant(registry_id=name, authorization_id=name, purpose_text='P'*4096,
                export_notice_text=text, export_notice_sha256=hashlib.sha256(text.encode()).hexdigest())
            approve(db, 'raw_export', value); ids.add(name)
        found = set(); cursor = None; pages = 0
        while True:
            response = export.available_scopes(db, account, authorization_cursor=cursor)
            assert len(response['scopes']) <= 4 and len(canonical(response)) <= 512*1024
            found.update(item['authorization_id'] for item in response['scopes'])
            pages += 1; cursor = response['next_cursor']
            if cursor is None:
                break
        assert found == ids and pages == 3
        with pytest.raises(Problem, match='CURSOR_MISMATCH'):
            export.available_scopes(db, account, artifact_cursor=raw_fixture.ARTIFACT)


def test_individually_over_export_budget_source_is_not_offered(fixture):
    with fixture.sessions.begin() as db:
        approve(db, 'raw_export', grant(max_uncompressed_bytes=127))
        account = db.get(Account, raw_fixture.ACCOUNT)
        response = export.available_scopes(db, account)
        assert response['scopes'][0]['artifacts'] == []
        with pytest.raises(Problem, match='EXPORT_TOO_LARGE'):
            export.freeze_export(db, account, scope(grant(max_uncompressed_bytes=127)), [raw_fixture.CHECK])


def test_over_budget_source_does_not_hide_or_disable_an_eligible_owned_choice(fixture):
    cap = len(DATA)
    too_large_id = '50000000-0000-4000-8000-000000000130'
    with fixture.sessions.begin() as db:
        value = grant(max_uncompressed_bytes=cap)
        approve(db, 'raw_export', value)
        account = db.get(Account, raw_fixture.ACCOUNT)
        original = db.get(Artifact, raw_fixture.ARTIFACT)
        retained = db.get(retention.RawRetention, original.id)
        large = Artifact(**{column.name: deepcopy(getattr(original, column.name))
            for column in Artifact.__table__.columns})
        large.id = too_large_id
        large.key = 'quarantine/fictional/' + too_large_id
        large.size = cap + 1
        lifetime = retention.RawRetention(**{column.name: deepcopy(getattr(retained, column.name))
            for column in retention.RawRetention.__table__.columns})
        lifetime.artifact_id = large.id
        lifetime.key = large.key
        db.add_all([large, lifetime])
        db.flush()
        seed_fictional_verification(db, large)
        page = export.available_scopes(db, account)['scopes'][0]
        assert [item['artifact_id'] for item in page['artifacts']] == [original.id]
        frozen = export.freeze_export(db, account, scope(value), [raw_fixture.CHECK])
        assert [item['artifact_id'] for item in frozen['raw_export']['sources']] == [original.id]
        with pytest.raises(Problem, match='EXPORT_TOO_LARGE'):
            export.freeze_export(db, account, scope(value, artifact_ids=[large.id]), [raw_fixture.CHECK])


def test_source_cursor_lists_every_eligible_source_without_truncation(fixture):
    with fixture.sessions.begin() as db:
        approve(db, 'raw_export', grant())
        account = db.get(Account, raw_fixture.ACCOUNT)
        original = db.get(Artifact, raw_fixture.ARTIFACT)
        retained = db.get(retention.RawRetention, original.id)
        ids = {original.id}
        for n in range(2,130):
            id = f'50000000-0000-4000-8000-{n:012d}'
            artifact = Artifact(**{column.name:deepcopy(getattr(original,column.name)) for column in Artifact.__table__.columns})
            artifact.id = id; artifact.key = 'quarantine/fictional/'+id
            row = retention.RawRetention(**{column.name:deepcopy(getattr(retained,column.name)) for column in retention.RawRetention.__table__.columns})
            row.artifact_id = id; row.key = artifact.key
            db.add_all([artifact,row]); db.flush()
            seed_fictional_verification(db,artifact); ids.add(id)
        page = export.available_scopes(db,account,authorization_id=grant()['authorization_id'])
        first = page['scopes'][0]
        assert len(first['artifacts'])==128 and first['artifacts_next_cursor'] is not None
        final = export.available_scopes(db,account,authorization_id=grant()['authorization_id'],
            artifact_cursor=first['artifacts_next_cursor'])['scopes'][0]
        assert len(final['artifacts'])==1 and final['artifacts_next_cursor'] is None
        assert {item['artifact_id'] for item in first['artifacts']+final['artifacts']}==ids


@pytest.mark.parametrize('change', ['missing','version','evidence','parent','generation'])
def test_verified_status_never_substitutes_for_exact_owned_accepted_codec_receipt(fixture, change):
    with fixture.sessions.begin() as db:
        account, job = accepted(db)
        receipt = retention.record(db, account, 'raw_verification', raw_fixture.ARTIFACT)
        if change=='missing':
            db.delete(receipt)
        elif change=='parent':
            receipt.parent_id = '20000000-0000-4000-8000-000000000002'
        elif change=='generation':
            receipt.generation = 2
        else:
            field = 'version_id' if change=='version' else 'evidence_sha256'
            receipt.body = {**receipt.body, field:'foreign-version' if change=='version' else 'f'*64}
            receipt.sha256 = digest(receipt.body)  # A self-consistent forged proof still fails.
        db.flush()
        with pytest.raises(Problem, match='AUTHENTICATED_RAW_VERIFICATION_REQUIRED'):
            export.validate_job(db,account,job)
