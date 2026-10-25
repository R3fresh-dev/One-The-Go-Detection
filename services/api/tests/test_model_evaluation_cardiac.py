"""Fictional HR custody proves offline software; never signature/research approval."""
from datetime import UTC, datetime
from uuid import NAMESPACE_URL, uuid5

import pytest

from otgd import cardiac_authority as c
from otgd.canonical import canonical, digest
from otgd.model_engine import Artifact, EvaluationReport, feature_values, score

from .helpers import session_fixture
from .test_model_evaluation import cohort as legacy_cohort
from .test_model_evaluation import assert_forged_history_refused, external_history_pipeline, m, pipeline, rebind


@pytest.fixture
def cohort():
    return legacy_cohort.__wrapped__()


def identity(value):
    return str(uuid5(NAMESPACE_URL, 'FICTIONAL-HR-TOOLKIT-' + value))


def at(epoch):
    return datetime.fromtimestamp(epoch, UTC).isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def original_snapshot(sid, owner, target, value, baseline_ref=None):
    snapshot = session_fixture(owner)
    snapshot.update(session_id=sid, mode='controlled_research', study_id='fictional-study',
        protocol_id='fictional-protocol', created_at=at(target), target_at=at(target),
        capture_completed_at=at(target+60), acquisition_span_ms=30000.0,
        clock_uncertainty_ms=None, baseline_ref=baseline_ref)
    snapshot['profile'].update(source='study_measurement', recorded_at=at(target))
    snapshot['device'].update(device_id='fictional-reader', boot_id='fictional-boot',
        hardware_revision='fictional-hw', firmware_version='fictional-fw')
    snapshot['sample'].update(status='not_collected', collected_at=None, volume_ml=None, dilution_factor=None)
    snapshot['saliva'] = []
    snapshot['eyes'].update(status='not_collected', source='prototype_sensor', started_at=None, ended_at=None,
        quality_flags=[], frame_rate_hz=None, baseline_diameter_mm=None, relative_constriction=None, latency_ms=None)
    snapshot['task'].update(status='not_collected', source='prototype_sensor', started_at=None, ended_at=None,
        quality_flags=[], practice_trials=0, scored_trials=0, go_trials=0, no_go_trials=0, valid_correct_go_trials=0,
        features={name: None for name in snapshot['task']['features']})
    snapshot['cardiac'].update(status='valid', source='prototype_sensor', modality='ppg',
        started_at=at(target+1), ended_at=at(target+31), acquisition_config_id='fictional-cardiac-config',
        heart_rate_bpm=value, ecg_status='not_collected', ecg_rmssd_ms=None,
        sample_rate_hz=None, quality_flags=sorted(c.FLAGS['otgd_esp32_adc_v1']))
    return snapshot


def interval(snapshot, policy, provenance, adapter):
    target = m.utc_timestamp(snapshot['target_at'])
    snapshot['cardiac']['quality_flags'] = sorted(c.FLAGS[adapter])
    value = dict(schema_version='1.0.0', method=c.METHOD, account_ref=snapshot['subject_ref'], data_generation=1,
        session_id=snapshot['session_id'], attempt_id=identity(snapshot['session_id']+'attempt'),
        authorization_id=identity(snapshot['session_id']+'authorization'), attestation_id=identity(snapshot['session_id']+'attestation'),
        binding_id=identity('binding'), boot_id=snapshot['device']['boot_id'], device_id=snapshot['device']['device_id'],
        key_id='fictional-key', hardware_revision='fictional-hw', firmware_version='fictional-fw', adapter_id=adapter,
        extractor_version=c.EXTRACTORS[adapter], configuration_id='fictional-cardiac-config', configuration_version='fictional-v1',
        configuration_sha256='1'*64, configuration_submitted_sha256=provenance['configuration_submitted_sha256'],
        **{key: provenance[key] for key in ('calibration_registry_sha256', 'calibration_scope_sha256',
            'qualification_registry_sha256', 'device_registry_sha256')}, policy_sha256=digest(policy),
        snapshot_sha256=digest(snapshot), capture_context_sha256='2'*64, evidence_manifest_sha256='3'*64,
        authorization_sha256='4'*64, attestation_sha256='5'*64, issued_epoch=target+1, received_epoch=target+32,
        target_epoch=target, server_utc_error_ms=2.0, signed_acquisition_duration_us=30000000 if adapter.endswith('max32664_v1') else None,
        maximum_monotonic_rate_error_ppm=20 if adapter.endswith('max32664_v1') else None,
        interval_ms=31004, acquisition_bound_ms=32004, preserved_quality_flags=snapshot['cardiac']['quality_flags'])
    return c.IntervalEvidence.model_validate(value).data()


@pytest.fixture(params=[('otgd_esp32_adc_v1', False), ('otgd_sparkfun_max32664_v1', False),
    ('otgd_esp32_adc_v1', True), ('otgd_sparkfun_max32664_v1', True)])
def cardiac_cohort(cohort, request):
    dataset, plan, _ = cohort
    adapter, personalized = request.param
    policy = {'method': c.METHOD, 'calibration_id': 'fictional-reviewed-clock', 'max_interval_ms': 60000,
        'allow_baseline_delta': personalized}
    provenance = {'reviewed_source_bundle_ref': 'FICTIONAL-REVIEWED-CUSTODY-NO-HUMAN-APPROVAL',
        'reviewed_source_bundle_sha256': digest('fictional source bundle'), 'independent_review_ref': 'fictional-independent-review',
        'independent_review_sha256': digest('fictional review record'), 'calibration_registry_sha256': '6'*64,
        'calibration_scope_sha256': '7'*64, 'qualification_registry_sha256': '8'*64,
        'device_registry_sha256': '9'*64, 'configuration_submitted_sha256': 'a'*64}
    raw = dataset.model_dump()
    for row in raw['sessions']:
        sid, owner = identity(row['session_id']), identity(row['participant_ref'])
        target = m.utc_timestamp(row['target_at'])
        participant = int(row['participant_ref'].split('-')[-1])
        outcome = row['endpoint']['value']
        old = original_snapshot(identity(sid+'baseline'), owner, target-120, 60.0+participant/10) if personalized else None
        snapshot = original_snapshot(sid, owner, target, 70.0+30*outcome+participant/10,
            old['session_id'] if old else None)
        current = interval(snapshot, policy, provenance, adapter)
        baseline = interval(old, policy, provenance, adapter) if old else None
        authority = c.build_authority({'cardiac_timing_policy': policy, 'manifest': {'required_channels': ['cardiac_hr'],
            'baseline_mode': 'personalized' if personalized else 'population'}}, current, baseline)
        row.update(session_id=sid, participant_ref=owner, target_at=snapshot['target_at'],
            capture_completed_at=snapshot['capture_completed_at'], quality_flags=snapshot['cardiac']['quality_flags'],
            features={'cardiac.heart_rate_bpm': {'status': 'valid',
                'value': snapshot['cardiac']['heart_rate_bpm'] - old['cardiac']['heart_rate_bpm'] if old else snapshot['cardiac']['heart_rate_bpm'],
                'observed_at': snapshot['cardiac']['ended_at'], 'available_at': at(target+32)}},
            cardiac_evidence={'snapshot': snapshot, 'snapshot_sha256': digest(snapshot), 'authority': authority,
                'authority_sha256': digest(authority), 'source_bundle_ref': provenance['reviewed_source_bundle_ref'],
                'source_bundle_sha256': provenance['reviewed_source_bundle_sha256'], 'baseline_snapshot': old,
                'baseline_snapshot_sha256': digest(old) if old else None})
    dataset = m.Dataset.model_validate(raw)
    plan_raw = plan.model_dump()
    plan_raw.update(cardiac_timing_policy=policy, cardiac_provenance=provenance,
        feature_names=['cardiac.heart_rate_bpm'], feature_limits={'cardiac.heart_rate_bpm': [-100.0, 200.0]})
    if personalized:
        plan_raw['max_baseline_age_ms'] = 3600000
    plan = m.AnalysisPlan.model_validate(plan_raw)
    return rebind(dataset, plan)


def changed_row(cohort, change, partition='confirmatory'):
    dataset, plan, split = cohort
    raw = dataset.model_dump()
    row = next(row for row in raw['sessions'] if row['session_id'] == split['session_ids'][partition][0])
    change(row)
    return rebind(m.Dataset.model_validate(raw), plan)


def rehash(row):
    item = row['cardiac_evidence']
    item['snapshot_sha256'] = digest(item['snapshot'])
    item['authority']['current']['snapshot_sha256'] = item['snapshot_sha256']
    if item['baseline_snapshot'] is not None:
        item['baseline_snapshot_sha256'] = digest(item['baseline_snapshot'])
        item['authority']['baseline']['snapshot_sha256'] = item['baseline_snapshot_sha256']
    item['authority_sha256'] = digest(item['authority'])


def test_external_history_references_remain_unverified_through_pipeline(cardiac_cohort, tmp_path, monkeypatch):
    external_history_pipeline(cardiac_cohort, tmp_path, monkeypatch)


def test_self_asserted_or_extra_approval_fields_do_not_authenticate_history(cardiac_cohort, tmp_path, monkeypatch):
    assert_forged_history_refused(cardiac_cohort, tmp_path, monkeypatch)


def test_raw_and_personalized_hr_training_reproduces_runtime_projection_and_report(cardiac_cohort):
    dataset, plan, _ = cardiac_cohort
    artifacts, training, report, evidence = pipeline(cardiac_cohort)
    assert set(artifacts) == {'cardiac_hr_only'}
    assert canonical(list(pipeline(cardiac_cohort))) == canonical([artifacts, training, report, evidence])
    artifact = Artifact.model_validate(artifacts['cardiac_hr_only'])
    c.validate_features(m.cardiac_body(plan), artifact)
    assert artifact.feature_names == ['cardiac.heart_rate_bpm']
    for row in dataset.sessions:
        item = row.cardiac_evidence
        values, reasons = m.row_values(row, plan.feature_names, plan)
        assert reasons == [] and values == feature_values(item.snapshot, artifact, item.baseline_snapshot)
        assert values == [row.features['cardiac.heart_rate_bpm'].value]
        assert row.quality_flags == item.snapshot['cardiac']['quality_flags']
        assert item.snapshot['clock_uncertainty_ms'] is None
        assert score(artifact, values) >= 0.0
    assert report['analysis_scope'] == 'cardiac_hr_only' and set(report['ablations']) == {'cardiac_hr_only'}
    assert EvaluationReport.model_validate(report).artifact_sha256 == digest(artifacts['cardiac_hr_only'])
    assert report['confirmatory']['invalid'] == report['later_sessions']['invalid'] == 0
    manifest = evidence['cardiac_evidence_manifest']
    assert len(manifest['rows']) == len(dataset.sessions) == 32
    assert report['cardiac_evidence']['evidence_manifest_sha256'] == digest(manifest) == training['cardiac_evidence_manifest_sha256']
    assert manifest['rows'][0]['captured_session_evidence_manifest_sha256'] == '3'*64
    assert manifest['signatures_registry_release_and_independent_review_authenticated'] is False
    assert evidence['paired_ablations'] == {'confirmatory': {}, 'later_sessions': {}}
    assert evidence['authority_granted'] is evidence['clinical_success_claimed'] is False
    assert evidence['subgroups']['confirmatory']['route']['fictional-empty-route']['cardiac_hr_only']['metrics']['total'] == 0
    assert len(training['eligible_session_ids']) == 8


@pytest.mark.parametrize('fault', ['snapshot_hash', 'authority_hash', 'bundle_hash', 'bundle_ref', 'configuration',
    'calibration', 'policy', 'interval', 'target', 'future_receipt', 'device', 'value', 'missing', 'acquisition',
    'fault_flag', 'cleaned_flags', 'outer_flags', 'duration', 'extractor', 'baseline_scope', 'availability', 'observation'])
def test_invalid_custody_or_faults_remain_in_all_row_denominators(cardiac_cohort, fault):
    def corrupt(row):
        item = row['cardiac_evidence']; proof = item['authority']['current']
        if fault == 'snapshot_hash': item['snapshot_sha256'] = '0'*64
        elif fault == 'authority_hash': item['authority_sha256'] = '0'*64
        elif fault == 'bundle_hash': item['source_bundle_sha256'] = '0'*64
        elif fault == 'bundle_ref': item['source_bundle_ref'] = 'unreviewed bundle'
        elif fault == 'configuration': proof['configuration_submitted_sha256'] = '0'*64; rehash(row)
        elif fault == 'calibration': proof['calibration_scope_sha256'] = '0'*64; rehash(row)
        elif fault == 'policy': proof['policy_sha256'] = '0'*64; rehash(row)
        elif fault == 'interval': proof['interval_ms'] -= 1; rehash(row)
        elif fault == 'target': proof['target_epoch'] -= 1; rehash(row)
        elif fault == 'future_receipt': proof['received_epoch'] += 60; rehash(row)
        elif fault == 'device': item['snapshot']['device']['device_id'] = 'other-device'; rehash(row)
        elif fault == 'value': row['features']['cardiac.heart_rate_bpm']['value'] += 1
        elif fault == 'missing': row['cardiac_evidence'] = None
        elif fault == 'acquisition': row['acquisition_status'] = 'invalid'
        elif fault == 'fault_flag': item['snapshot']['cardiac']['quality_flags'][0] = 'CONTACT_LOST'; row['quality_flags'] = item['snapshot']['cardiac']['quality_flags']; rehash(row)
        elif fault == 'cleaned_flags': item['snapshot']['cardiac']['quality_flags'] = []; row['quality_flags'] = []; rehash(row)
        elif fault == 'outer_flags': row['quality_flags'] = []
        elif fault == 'duration': proof['signed_acquisition_duration_us'] = 60000000; rehash(row)
        elif fault == 'extractor': proof['extractor_version'] = 'adc_peak_intervals_v1' if proof['extractor_version'].startswith('sparkfun') else 'sparkfun_sensor_bpm_v1'; rehash(row)
        elif fault == 'baseline_scope':
            if item['authority']['baseline']:
                item['authority']['baseline']['key_id'] = 'foreign-baseline-key'; rehash(row)
            else:
                item['snapshot']['baseline_ref'] = identity('unavailable-baseline'); rehash(row)
        elif fault == 'availability': row['features']['cardiac.heart_rate_bpm']['available_at'] = at(proof['received_epoch']-.5)
        elif fault == 'observation': row['features']['cardiac.heart_rate_bpm']['observed_at'] = row['target_at']
    result = changed_row(cardiac_cohort, corrupt)
    _, _, report, evidence = pipeline(result)
    assert report['confirmatory']['total'] == 8 and report['confirmatory']['invalid'] == 1
    assert report['confirmatory']['brier'] >= 1/8 and report['confirmatory']['calibration_error'] >= 1/8
    assert evidence['metric_details']['confirmatory']['cardiac_hr_only']['invalid_rate'] == 1/8
    output = evidence['row_predictions']['confirmatory']['cardiac_hr_only']
    assert [row['session_id'] for row in output] == result[2]['session_ids']['confirmatory']
    assert sum(row['probability'] is None for row in output) == 1


def test_held_out_hr_values_and_outcomes_cannot_affect_training(cardiac_cohort):
    dataset, plan, split = cardiac_cohort
    artifacts, _ = m.train(dataset, plan, split, '2026-03-02T00:00:00Z')
    raw = dataset.model_dump()
    for row in raw['sessions']:
        if row['participant_ref'] in split['held_out_participants']:
            row['cardiac_evidence']['snapshot']['cardiac']['heart_rate_bpm'] += 10
            row['features']['cardiac.heart_rate_bpm']['value'] += 10
            row['endpoint']['value'] = 1-row['endpoint']['value']
            rehash(row)
    changed, _ = m.train(*rebind(m.Dataset.model_validate(raw), plan), '2026-03-02T00:00:00Z')
    assert changed == artifacts


def test_exact_interval_limit_uses_outward_rounding_not_zero_error(cardiac_cohort):
    dataset, plan, _ = cardiac_cohort
    row = dataset.sessions[0]
    assert row.cardiac_evidence.authority.current.interval_ms == 31004
    exact = m.AnalysisPlan.model_validate({**plan.model_dump(), 'cardiac_timing_policy': {
        **plan.cardiac_timing_policy.data(), 'max_interval_ms': 31004}})
    # A policy hash must match the whole changed policy; no client re-labeling
    # of historical authority can make the old-policy evidence eligible.
    assert m.row_values(row, exact.feature_names, exact)[0] is None
    proof = row.cardiac_evidence.authority.current.data()
    assert c.bounds(proof['issued_epoch'], proof['received_epoch'], proof['target_epoch'], 2.0, proof['received_epoch'])['interval_ms'] == 31004


def test_original_unqualified_times_are_preserved_with_runtime_span_and_delivery_gates(cardiac_cohort):
    dataset, plan, _ = cardiac_cohort
    raw = plan.model_dump()
    raw.update(max_acquisition_span_ms=32004, max_delivery_delay_ms=59004)
    exact = rebind(dataset, m.AnalysisPlan.model_validate(raw))
    _, _, report, _ = pipeline(exact)
    assert report['confirmatory']['invalid'] == 0
    assert m.utc_timestamp(dataset.sessions[0].capture_completed_at)-m.utc_timestamp(dataset.sessions[0].target_at) == 60
    for key in ('max_acquisition_span_ms', 'max_delivery_delay_ms'):
        smaller = m.AnalysisPlan.model_validate({**raw, key: raw[key]-1})
        assert m.row_values(dataset.sessions[0], smaller.feature_names, smaller)[0] is None
        with pytest.raises(m.InvalidEvidence, match='both independent outcome classes'):
            m.train(*rebind(dataset, smaller), '2026-03-02T00:00:00Z')


def test_personalized_baseline_uses_explicit_historical_proof_and_conservative_age(cardiac_cohort):
    dataset, plan, _ = cardiac_cohort
    if not plan.cardiac_timing_policy.allow_baseline_delta:
        with pytest.raises(ValueError, match='explicit personalized age policy'):
            m.AnalysisPlan.model_validate({**plan.model_dump(), 'max_baseline_age_ms': 119004})
        return
    exact = m.AnalysisPlan.model_validate({**plan.model_dump(), 'max_baseline_age_ms': 119004})
    assert m.row_values(dataset.sessions[0], exact.feature_names, exact)[0] is not None
    expired = m.AnalysisPlan.model_validate({**exact.model_dump(), 'max_baseline_age_ms': 119003})
    assert m.row_values(dataset.sessions[0], expired.feature_names, expired)[0] is None
    for fault in ('missing', 'hash', 'subject', 'protocol', 'same_session', 'same_attempt', 'wrong_ref', 'wrong_device', 'fault_flag'):
        def corrupt(row, fault=fault):
            item = row['cardiac_evidence']; old = item['baseline_snapshot']; proof = item['authority']['baseline']
            if fault == 'missing': item['baseline_snapshot'] = None
            elif fault == 'hash': item['baseline_snapshot_sha256'] = '0'*64
            elif fault == 'subject': old['subject_ref'] = identity('foreign-owner'); proof['account_ref'] = old['subject_ref']; rehash(row)
            elif fault == 'protocol': old['protocol_id'] = 'different-protocol'; rehash(row)
            elif fault == 'same_session':
                old['session_id'] = row['session_id']; proof['session_id'] = row['session_id']; item['snapshot']['baseline_ref'] = row['session_id']; rehash(row)
            elif fault == 'same_attempt': proof['attempt_id'] = item['authority']['current']['attempt_id']; rehash(row)
            elif fault == 'wrong_ref': item['snapshot']['baseline_ref'] = identity('arbitrary-earlier-row'); rehash(row)
            elif fault == 'wrong_device': old['device']['device_id'] = 'other-reader'; rehash(row)
            elif fault == 'fault_flag': old['cardiac']['quality_flags'][0] = 'CONTACT_LOST'; rehash(row)
        result = changed_row(cardiac_cohort, corrupt)
        row = next(value for value in result[0].sessions if value.session_id == result[2]['session_ids']['confirmatory'][0])
        assert m.row_values(row, plan.feature_names, plan)[0] is None, fault


def test_invalid_training_custody_is_rejected_without_cleaning_flags_or_losing_manifest_rows(cardiac_cohort):
    def corrupt(row): row['cardiac_evidence']['authority_sha256'] = '0'*64
    result = changed_row(cardiac_cohort, corrupt, 'training')
    _, training, report, evidence = pipeline(result)
    assert len(training['eligible_session_ids']) == 7 and len(training['rejected_training_rows']) == 1
    assert 'CARDIAC_EVIDENCE_INVALID' in training['rejected_training_rows'][0]['reasons']
    assert report['confirmatory']['total'] == 8
    assert len(evidence['cardiac_evidence_manifest']['rows']) == 32
    assert all(row['preserved_quality_flags'] for row in evidence['cardiac_evidence_manifest']['rows'])


def test_hr_scope_rejects_mixed_rows_and_unprespecified_legacy_evidence(cardiac_cohort, cohort):
    def mixed(row):
        row['features']['saliva.THC'] = {'status': 'valid', 'value': 1.0, 'observed_at': row['target_at'], 'available_at': row['capture_completed_at']}
    result = changed_row(cardiac_cohort, mixed)
    with pytest.raises(m.InvalidEvidence, match='mixed-channel'):
        m.train(*result, '2026-03-02T00:00:00Z')
    legacy_dataset, legacy_plan, _ = cohort
    raw = legacy_dataset.model_dump()
    raw['sessions'][0]['cardiac_evidence'] = cardiac_cohort[0].sessions[0].cardiac_evidence.model_dump()
    with pytest.raises(m.InvalidEvidence, match='separately prespecified'):
        m.train(*rebind(m.Dataset.model_validate(raw), legacy_plan), '2026-03-02T00:00:00Z')


def test_legacy_absent_optional_fields_do_not_change_dataset_or_plan_bytes(cohort):
    dataset, plan, _ = cohort
    assert all('cardiac_evidence' not in row for row in dataset.model_dump()['sessions'])
    assert not {'cardiac_timing_policy', 'cardiac_provenance', 'max_baseline_age_ms'} & plan.model_dump().keys()
    assert set(m.variants(plan)) == set(m.VARIANTS)
    with pytest.raises(ValueError, match='chemistry/app'):
        m.AnalysisPlan.model_validate({**plan.model_dump(), 'feature_names': ['cardiac.heart_rate_bpm'],
            'feature_limits': {'cardiac.heart_rate_bpm': [0.0, 300.0]}})


def test_hr_cli_freeze_train_evaluate_verify_and_tamper_refusal(cardiac_cohort, tmp_path):
    dataset, plan, _ = cardiac_cohort
    data, analysis, index, split = [tmp_path/name for name in ('dataset.json', 'plan.json', 'index.json', 'split.json')]
    m.store(data, dataset.model_dump()); m.store(analysis, plan.model_dump())
    m.main(['index', '--dataset', str(data), '--output', str(index)])
    assert 'cardiac_evidence' not in m.load(index)['sessions'][0]
    m.main(['freeze', '--index', str(index), '--analysis', str(analysis), '--output', str(split)])
    common = ['--dataset', str(data), '--analysis', str(analysis), '--split', str(split)]
    training, evaluation = tmp_path/'training', tmp_path/'evaluation'
    m.main(['train', *common, '--output', str(training)])
    assert {path.name for path in training.iterdir()} == {'cardiac_hr_only.artifact.json', 'training.json'}
    m.main(['evaluate', *common, '--training-directory', str(training), '--output', str(evaluation)])
    args = ['verify', *common, '--training-directory', str(training), '--evaluation-directory', str(evaluation)]
    assert m.main(args)['evaluation_reproduced'] is True
    raw = m.load(evaluation/'evaluation-evidence.json')
    raw['cardiac_evidence_manifest']['provenance']['independent_review_sha256'] = '0'*64
    (evaluation/'evaluation-evidence.json').write_bytes(canonical(raw))
    with pytest.raises(m.InvalidEvidence, match='do not reproduce'):
        m.main(args)
