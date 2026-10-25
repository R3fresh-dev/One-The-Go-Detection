"""Fictional engineered cohorts qualify software, never a human-study model."""
import math
from copy import deepcopy
from pathlib import Path
import sys

import pytest

from otgd.canonical import canonical, digest
from otgd.model_engine import Artifact, EvaluationReport, score

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools'))
import model_evaluation as m


@pytest.fixture
def cohort():
    versions = {'acquisition_sha256': 'a'*64, 'assay_sha256': 'b'*64, 'task_sha256': 'c'*64,
        'input_contract_version': '0.1.0', 'feature_version': 'otgd.features.v1'}
    rows = []
    for participant in range(8):
        for later in (False, True):
            for outcome in (0, 1):
                date = '2026-02-01' if later else '2026-01-01'
                target = date+f'T12:0{outcome}:00Z'
                capture = date+f'T12:0{outcome+1}:00Z'
                values = {'saliva.THC': 2.+5*outcome+participant/10,
                    'task.features.median_rt_ms': 250.+100*outcome+participant,
                    'cardiac.ecg_rmssd_ms': 20.+10*outcome+participant/10}
                rows.append({'session_id': f'fictional-{participant}-{int(later)}-{outcome}', 'participant_ref': f'fictional-person-{participant}',
                    'target_at': target, 'acquisition_status': 'valid', 'quality_flags': [],
                    'capture_completed_at': capture, 'information_cutoff_at': capture,
                    'features': {name: {'status': 'valid', 'value': value, 'observed_at': target, 'available_at': capture} for name,value in values.items()},
                    'endpoint': {'endpoint_id': 'fictional-functional-endpoint', 'value': outcome, 'assessed_at': date+f'T12:0{outcome}:30Z',
                        'available_at': date+f'T12:0{outcome+1}:00Z', 'source_ref': 'fictional-independent-assessment',
                        'assessor_ref': 'fictional-assessor', 'independently_assessed': True},
                    'strata': {'route': 'fictional-route-a' if participant%2 else 'fictional-route-b',
                        'use_frequency': 'fictional-rare' if participant%2 else 'fictional-frequent', 'co_use': 'fictional-not-reported',
                        'device': 'fictional-device-a' if participant%2 else 'fictional-device-b', 'baseline': 'fictional-first-use', 'population': 'fictional-adults'}})
    dataset = m.Dataset.model_validate({'schema_version': '1.0.0', 'data_kind': 'engineering_synthetic',
        'authorization_ref': 'engineering-fixture-only-no-human-approval', 'endpoint_id': 'fictional-functional-endpoint',
        'endpoint_kind': 'current_functional_impairment', 'endpoint_definition': 'FICTIONAL ENGINEERING ENDPOINT; no clinical validation.',
        'endpoint_source_ref': 'fictional-independent-assessment', 'locked_at': '2026-03-01T00:00:00Z', 'versions': versions, 'sessions': rows})
    plan = m.AnalysisPlan.model_validate({'schema_version': '1.0.0', 'purpose': 'prespecified_logistic_evaluation',
        'dataset_sha256': digest(dataset.model_dump()), 'plan_lock_ref': 'fictional-unverified-plan-lock',
        'independent_endpoint_evidence_ref': 'fictional-unverified-assessment', 'prespecified_at': '2025-12-01T00:00:00Z',
        'training_cutoff': '2026-01-15T00:00:00Z', 'later_session_boundary': '2026-01-31T00:00:00Z',
        'endpoint_id': dataset.endpoint_id, 'endpoint_definition_sha256': digest(dataset.endpoint_definition),
        'comparator_kind': 'prespecified_independent_comparator', 'maximum_endpoint_offset_seconds': 120,
        'max_acquisition_span_ms': 120000, 'max_delivery_delay_ms': 60000,
        'versions': versions, 'seed': 'fictional-frozen-seed', 'training_participant_count': 4,
        'feature_names': list(rows[0]['features']), 'feature_limits': {'saliva.THC': [0.,1000.], 'task.features.median_rt_ms': [0.,2000.], 'cardiac.ecg_rmssd_ms': [0.,500.]},
        'iterations': 100, 'learning_rate': .1, 'l2_penalty': .1, 'calibration_id': 'fictional-identity-calibration',
        'calibration_method': 'prespecified_identity', 'operating_threshold': .5,
        'uncertainty_policy': {'policy_id': 'fictional-prespecified-band', 'method': 'none', 'lower': None, 'upper': None},
        'calibration_bins': 5, 'confidence_level': .95, 'bootstrap_replicates': 200, 'minimum_defined_bootstrap_replicates': 100,
        'denominator_policy': 'all_sessions_invalid_and_abstention_are_failures', 'invalid_score_loss': 1,
        'strata': {'route': ['fictional-route-a','fictional-route-b','fictional-empty-route'], 'use_frequency': ['fictional-rare','fictional-frequent'],
            'co_use': ['fictional-not-reported'], 'device': ['fictional-device-a','fictional-device-b'], 'baseline': ['fictional-first-use'], 'population': ['fictional-adults']}})
    split = m.freeze(m.cohort_index(dataset),plan)
    return dataset,plan,split


def pipeline(cohort):
    dataset,plan,split = cohort
    artifacts,training = m.train(dataset,plan,split,'2026-03-02T00:00:00Z')
    report,evidence = m.evaluate(dataset,plan,split,artifacts,training,'2026-03-03T00:00:00Z')
    return artifacts,training,report,evidence


def rebind(dataset,plan):
    plan = m.AnalysisPlan.model_validate({**plan.model_dump(),'dataset_sha256': digest(dataset.model_dump())})
    return dataset,plan,m.freeze(m.cohort_index(dataset),plan)


def external_history_pipeline(cohort, tmp_path, monkeypatch):
    """Exercise actual CLI reproduction with deliberately unauthenticated history."""
    dataset, plan, _ = cohort
    raw = dataset.model_dump()
    raw['authorization_ref'] = 'FICTIONAL-UNVERIFIED-AUTHORIZATION-NO-HUMAN-APPROVAL'
    analysis = plan.model_dump()
    analysis.update(plan_lock_ref='FICTIONAL-UNVERIFIED-HISTORICAL-PLAN-LOCK',
        independent_endpoint_evidence_ref='FICTIONAL-UNVERIFIED-INDEPENDENT-ENDPOINT-RECORD')
    if plan.cardiac_provenance is not None:
        analysis['cardiac_provenance'].update(
            reviewed_source_bundle_ref='FICTIONAL-UNVERIFIED-RETAINED-HR-SOURCE-BUNDLE',
            independent_review_ref='FICTIONAL-UNVERIFIED-HR-INDEPENDENT-REVIEW')
        for row in raw['sessions']:
            row['cardiac_evidence']['source_bundle_ref'] = analysis['cardiac_provenance']['reviewed_source_bundle_ref']
    dataset, plan, split = rebind(m.Dataset.model_validate(raw), m.AnalysisPlan.model_validate(analysis))
    # Capture originals before any freeze/train/evaluate/verify operation below.
    originals = deepcopy({'dataset': dataset.model_dump(), 'analysis': plan.model_dump(), 'split': split})
    row_hashes = {row['session_id']: digest(row) for row in originals['dataset']['sessions']}
    expected_hashes = {name: digest(value) for name, value in originals.items()}
    index = m.cohort_index(dataset)
    artifacts, training, report, evidence = pipeline((dataset, plan, split))
    expected_hashes.update(training=digest(training), report=digest(report))
    artifact_hashes = {name: digest(value) for name, value in artifacts.items()}
    data, analysis_path, index_path, split_path = [tmp_path / (name + '.json') for name in ('dataset', 'analysis', 'index', 'split')]
    m.store(data, originals['dataset']); m.store(analysis_path, originals['analysis'])
    indexed = m.main(['index', '--dataset', str(data), '--output', str(index_path)])
    assert indexed == {'index_sha256': digest(index.model_dump()), 'outcomes_disclosed': False, 'authority_granted': False}
    frozen = m.main(['freeze', '--index', str(index_path), '--analysis', str(analysis_path), '--output', str(split_path)])
    assert frozen == {'split_sha256': expected_hashes['split'], 'historical_lock_proven': False, 'authority_granted': False}
    common = ['--dataset', str(data), '--analysis', str(analysis_path), '--split', str(split_path)]
    training_dir, evaluation_dir = tmp_path / 'training', tmp_path / 'evaluation'
    times = iter(['2026-03-02T00:00:00Z', '2026-03-02T00:00:00Z', '2026-03-03T00:00:00Z'])
    monkeypatch.setattr(m, 'execution_time', lambda: next(times))
    trained = m.main(['train', *common, '--output', str(training_dir)])
    assert trained == {'training_sha256': expected_hashes['training'], 'artifacts': artifact_hashes,
        'status': 'unvalidated', 'authority_granted': False}
    extra = ['--training-directory', str(training_dir)]
    evaluated = m.main(['evaluate', *common, *extra, '--output', str(evaluation_dir)])
    assert evaluated == {'evaluation_report_sha256': expected_hashes['report'], 'evidence_sha256': digest(evidence),
        'status': 'unvalidated', 'authority_granted': False}
    verify_args = ['verify', *common, *extra, '--evaluation-directory', str(evaluation_dir)]
    assert m.main(verify_args) == {'evaluation_reproduced': True, 'status': 'unvalidated', 'authority_granted': False}
    for name, path in [('dataset', data), ('analysis', analysis_path), ('split', split_path),
        ('training', training_dir / 'training.json'), ('report', evaluation_dir / 'evaluation-report.json')]:
        assert digest(m.load(path)) == expected_hashes[name]
    assert m.load(data) == originals['dataset'] and m.load(analysis_path) == originals['analysis']
    assert {name: digest(m.load(training_dir / (name + '.artifact.json'))) for name in artifacts} == artifact_hashes
    assert m.load(evaluation_dir / 'evaluation-evidence.json') == evidence
    assert evidence['external_assertions'] == {
        'authorization_ref': originals['dataset']['authorization_ref'],
        'plan_lock_ref': originals['analysis']['plan_lock_ref'],
        'independent_endpoint_evidence_ref': originals['analysis']['independent_endpoint_evidence_ref'],
        'verified_by_tool': False, 'historical_lock_or_blinding_proven': False}
    assert training['authority_granted'] is evidence['authority_granted'] is evidence['clinical_success_claimed'] is False
    assert evidence['dataset_sha256'] == training['dataset_sha256'] == report['dataset_sha256'] == expected_hashes['dataset']
    assert evidence['analysis_plan_sha256'] == training['analysis_plan_sha256'] == report['analysis_plan_sha256'] == expected_hashes['analysis']
    assert evidence['split_plan_sha256'] == training['split_plan_sha256'] == report['split_plan_sha256'] == expected_hashes['split']
    assert evidence['training_sha256'] == expected_hashes['training']
    assert evidence['evaluation_report_sha256'] == expected_hashes['report']
    assert evidence['artifact_sha256'] == training['artifact_sha256'] == artifact_hashes
    assert training['eligible_session_ids'] == originals['split']['session_ids']['training']
    assert training['rejected_training_rows'] == []
    assert all(row['endpoint']['independently_assessed'] is True for row in originals['dataset']['sessions'])
    for partition in ('confirmatory', 'later_sessions'):
        assert evidence['matched_evaluation_session_ids'][partition] == originals['split']['session_ids'][partition]
        for predictions in evidence['row_predictions'][partition].values():
            assert [row['session_id'] for row in predictions] == originals['split']['session_ids'][partition]
            assert len(predictions) == 8
    if plan.cardiac_provenance is not None:
        manifest = evidence['cardiac_evidence_manifest']
        assert manifest['provenance'] == originals['analysis']['cardiac_provenance']
        assert manifest['signatures_registry_release_and_independent_review_authenticated'] is False
        assert {row['session_id']: row['session_record_sha256'] for row in manifest['rows']} == row_hashes
        by_id = {row['session_id']: row['cardiac_evidence'] for row in originals['dataset']['sessions']}
        for row in manifest['rows']:
            for name in ('source_bundle_ref', 'source_bundle_sha256', 'snapshot_sha256', 'authority_sha256', 'baseline_snapshot_sha256'):
                assert row[name] == by_id[row['session_id']][name]
        manifest_hash = digest(manifest)
        assert evidence['cardiac_evidence_manifest_sha256'] == training['cardiac_evidence_manifest_sha256'] == report['cardiac_evidence']['evidence_manifest_sha256'] == manifest_hash
    return dataset, plan, training_dir, evaluation_dir, verify_args


def assert_forged_history_refused(cohort, tmp_path, monkeypatch):
    dataset, plan, training_dir, evaluation_dir, verify_args = external_history_pipeline(cohort, tmp_path, monkeypatch)
    # Reject extra approval claims in actual strict typed inputs, including the
    # endpoint whose required True value is only a caller assertion.
    for target in ('dataset', 'plan', 'endpoint'):
        for flag in ('verified_by_tool', 'authority_granted', 'historical_lock_proven'):
            raw = deepcopy(plan.model_dump() if target == 'plan' else dataset.model_dump())
            (raw['sessions'][0]['endpoint'] if target == 'endpoint' else raw)[flag] = True
            with pytest.raises(ValueError, match='Extra inputs are not permitted'):
                (m.AnalysisPlan if target == 'plan' else m.Dataset).model_validate(raw)
    # Untyped receipts cannot smuggle authority through deterministic verify.
    training_path = training_dir / 'training.json'
    evidence_path = evaluation_dir / 'evaluation-evidence.json'
    for path, mutate in (
        (training_path, lambda value: value.update(authority_granted=True)),
        (training_path, lambda value: value.update(independent_review_authenticated=True)),
        (evidence_path, lambda value: value['external_assertions'].update(verified_by_tool=True)),
        (evidence_path, lambda value: value['external_assertions'].update(historical_lock_or_blinding_proven=True)),
        (evidence_path, lambda value: value.update(authority_granted=True, clinical_success_claimed=True)),
    ):
        original = path.read_bytes()
        forged = m.load(path); mutate(forged); path.write_bytes(canonical(forged))
        with pytest.raises(ValueError):
            m.main(verify_args)
        path.write_bytes(original)
    if plan.cardiac_provenance is not None:
        for target in ('cardiac_provenance', 'cardiac_evidence'):
            raw = deepcopy(plan.model_dump() if target == 'cardiac_provenance' else dataset.model_dump())
            nested = raw[target] if target == 'cardiac_provenance' else raw['sessions'][0][target]
            nested['signatures_registry_release_and_independent_review_authenticated'] = True
            with pytest.raises(ValueError, match='Extra inputs are not permitted'):
                (m.AnalysisPlan if target == 'cardiac_provenance' else m.Dataset).model_validate(raw)
        original = evidence_path.read_bytes(); forged = m.load(evidence_path)
        forged['cardiac_evidence_manifest']['signatures_registry_release_and_independent_review_authenticated'] = True
        forged['cardiac_evidence_manifest_sha256'] = digest(forged['cardiac_evidence_manifest'])
        evidence_path.write_bytes(canonical(forged))
        with pytest.raises(ValueError, match='Evaluation bytes do not reproduce'):
            m.main(verify_args)
        evidence_path.write_bytes(original)
    assert m.main(verify_args)['authority_granted'] is False


def test_external_history_references_remain_unverified_through_pipeline(cohort, tmp_path, monkeypatch):
    external_history_pipeline(cohort, tmp_path, monkeypatch)


def test_self_asserted_or_extra_approval_fields_do_not_authenticate_history(cohort, tmp_path, monkeypatch):
    assert_forged_history_refused(cohort, tmp_path, monkeypatch)


def test_frozen_participant_and_temporal_partitions_reproduce_without_outcomes(cohort):
    dataset,plan,split = cohort
    index = m.cohort_index(dataset).model_dump()
    assert all('endpoint' not in row and 'features' not in row and 'value' not in row for row in index['sessions'])
    assert set(split['training_participants']).isdisjoint(split['held_out_participants'])
    assert len(split['session_ids']['training']) == len(split['session_ids']['confirmatory']) == len(split['session_ids']['later_sessions']) == 8
    assert len(split['excluded_sessions']) == 8
    assigned = [identity for ids in split['session_ids'].values() for identity in ids]+[row['session_id'] for row in split['excluded_sessions']]
    assert set(assigned) == {row.session_id for row in dataset.sessions} and len(set(assigned)) == len(assigned)
    reversed_dataset = m.Dataset.model_validate({**dataset.model_dump(),'sessions': list(reversed(dataset.model_dump()['sessions']))})
    # Reordering input changes the locked dataset digest, while seeded subject
    # assignment and within-cohort order remain deterministic.
    _,_,reversed_split = rebind(reversed_dataset,plan)
    assert reversed_split['session_ids'] == split['session_ids']


def test_real_logistic_fitting_is_train_only_deterministic_and_engine_compatible(cohort):
    dataset,plan,split = cohort
    artifacts,training,report,evidence = pipeline(cohort)
    assert set(artifacts) == set(m.VARIANTS)
    assert canonical(list(pipeline(cohort))) == canonical([artifacts,training,report,evidence])
    model = Artifact.model_validate(artifacts['combined'])
    assert model.calibration.slope == 1 and model.calibration.intercept == 0
    rows = {row.session_id: row for row in dataset.sessions}
    for j,name in enumerate(model.feature_names):
        expected = math.fsum(rows[identity].features[name].value for identity in training['eligible_session_ids'])/len(training['eligible_session_ids'])
        assert model.means[j] == expected
    loss = sum((score(model,[rows[identity].features[name].value for name in model.feature_names])-rows[identity].endpoint.value)**2 for identity in training['eligible_session_ids'])/len(training['eligible_session_ids'])
    assert loss < .25  # Demonstrates fitting on this deliberately learnable fixture.
    assert EvaluationReport.model_validate(report).artifact_sha256 == digest(artifacts['combined'])
    assert m.utc_timestamp(artifacts['combined']['trained_at']) <= m.utc_timestamp(report['locked_at']) <= m.utc_timestamp(report['evaluated_at'])
    assert training['dataset_custody_locked_at'] != report['locked_at']
    assert evidence['evaluation_report_sha256'] == digest(report)
    assert evidence['data_kind'] == 'engineering_synthetic' and evidence['authority_granted'] is False
    assert evidence['external_assertions']['verified_by_tool'] is False
    changed = dataset.model_dump()
    for row in changed['sessions']:
        if row['participant_ref'] in split['held_out_participants']:
            row['features']['saliva.THC']['value'] += 100
            row['features']['task.features.median_rt_ms']['value'] += 500
            row['endpoint']['value'] = 1-row['endpoint']['value']
    new = rebind(m.Dataset.model_validate(changed),plan)
    changed_artifacts,_ = m.train(*new,'2026-03-02T00:00:00Z')
    assert changed_artifacts == artifacts  # No test-feature or test-label preprocessing/calibration leak.


def test_censored_invalid_and_abstaining_rows_stay_in_every_matched_denominator(cohort):
    dataset,plan,split = cohort
    changed = dataset.model_dump();identity = split['session_ids']['confirmatory'][0]
    for row in changed['sessions']:
        if row['session_id'] == identity:
            row['features']['saliva.THC'].update(status='censored',value=None)
    plan = m.AnalysisPlan.model_validate({**plan.model_dump(),'uncertainty_policy': {'policy_id': 'fictional-all-abstain','method': 'probability_band','lower': 0.,'upper': 1.}})
    artifacts,training,report,evidence = pipeline(rebind(m.Dataset.model_validate(changed),plan))
    assert report['confirmatory']['total'] == 8 and report['confirmatory']['invalid'] == 1
    assert report['confirmatory']['valid'] == report['confirmatory']['abstained'] == 7
    assert report['confirmatory']['sensitivity'] == report['confirmatory']['specificity'] == 0
    assert report['confirmatory']['brier'] >= 1/8 and report['confirmatory']['calibration_error'] >= 1/8
    for variant in m.VARIANTS:
        metric = report['ablations'][variant]
        assert metric['total'] == 8 and metric['positives'] == metric['negatives'] == 4
        assert [row['session_id'] for row in evidence['row_predictions']['confirmatory'][variant]] == split['session_ids']['confirmatory']
        assert evidence['metric_details']['confirmatory'][variant]['defined_sensitivity_draws'] == 200
    assert report['ablations']['app_only']['invalid'] == 0
    assert evidence['paired_ablations']['confirmatory']['combined_minus_app_only']['total'] == 8
    invalid = next(row for row in evidence['row_predictions']['confirmatory']['combined'] if row['session_id'] == identity)
    assert invalid['probability'] is None and invalid['predicted_positive'] is None
    predictive = evidence['metric_details']['confirmatory']['combined']['predictive_values']
    assert predictive['positive_predictive_value'] is None and predictive['negative_predictive_value'] is None
    assert predictive['observed_endpoint_prevalence'] == .5 and predictive['decision_coverage'] == 0


def test_invalid_training_rows_are_shared_by_every_ablation_and_constant_scaling_is_train_only(cohort):
    dataset,plan,split = cohort
    value = dataset.model_dump()
    for row in value['sessions']:
        if row['session_id'] == split['session_ids']['training'][0]:
            row['acquisition_status'] = 'invalid';row['quality_flags'] = ['fictional-interruption']
        if row['session_id'] in split['session_ids']['training']:
            row['features']['cardiac.ecg_rmssd_ms']['value'] = 30.
    artifacts,training = m.train(*rebind(m.Dataset.model_validate(value),plan),'2026-03-02T00:00:00Z')
    assert len(training['eligible_session_ids']) == 7 and len(training['rejected_training_rows']) == 1
    combined = Artifact.model_validate(artifacts['combined']);j = combined.feature_names.index('cardiac.ecg_rmssd_ms')
    assert combined.means[j] == 30. and combined.scales[j] == 1.


@pytest.mark.parametrize('change',['future','future_observation','future_profile','unknown_feature','nonfinite','false_independence','boolean_label','unlocked_label','missing_time','foreign_endpoint','cutoff_order'])
@pytest.mark.parametrize('acquisition_status', ['valid', 'invalid'])
def test_invalid_or_future_source_data_are_rejected_before_fitting(cohort,change,acquisition_status):
    dataset,_,_ = cohort;value = dataset.model_dump();row = value['sessions'][0]
    row['acquisition_status'] = acquisition_status
    if acquisition_status == 'invalid':
        row['quality_flags'] = ['fictional-interruption']
    # An invalid acquisition is a retained row, not a bypass of input custody.
    # Establish that the unchanged row is admissible before corrupting it.
    assert m.Dataset.model_validate(value).sessions[0].acquisition_status == acquisition_status
    if change == 'future':row['features']['saliva.THC']['available_at'] = '2026-01-02T12:00:00Z'
    elif change == 'future_observation':row['features']['saliva.THC']['observed_at'] = '2026-01-01T12:01:01Z'
    elif change == 'future_profile':row['features']['profile.age_years'] = {'status': 'valid','value': 30.,'observed_at': '2026-01-01T11:59:00Z','available_at': row['capture_completed_at']}
    elif change == 'unknown_feature':row['features']['outcome.label'] = row['features'].pop('saliva.THC')
    elif change == 'nonfinite':row['features']['saliva.THC']['value'] = float('nan')
    elif change == 'false_independence':row['endpoint']['independently_assessed'] = False
    elif change == 'boolean_label':row['endpoint']['value'] = True
    elif change == 'unlocked_label':row['endpoint']['available_at'] = '2026-04-01T00:00:00Z'
    elif change == 'missing_time':row['features']['saliva.THC']['available_at'] = None
    elif change == 'cutoff_order':row['information_cutoff_at'] = '2026-01-01T11:59:00Z'
    else:row['endpoint']['endpoint_id'] = 'foreign-exposure-label'
    with pytest.raises(ValueError):m.Dataset.model_validate(value)


def test_same_check_observations_and_later_assay_delivery_preserve_original_target(cohort):
    dataset,plan,_ = cohort;value = dataset.model_dump()
    for row in value['sessions']:
        row['information_cutoff_at'] = row['capture_completed_at'].replace(':00Z',':30Z')
        row['features']['saliva.THC']['observed_at'] = row['target_at'].replace(':00Z',':10Z')
        row['features']['saliva.THC']['available_at'] = row['information_cutoff_at']
        row['features']['task.features.median_rt_ms']['observed_at'] = row['capture_completed_at']
    new = rebind(m.Dataset.model_validate(value),plan)
    _,_,_,evidence = pipeline(new)
    originals = {row.session_id: row.target_at for row in dataset.sessions}
    for row in evidence['row_predictions']['confirmatory']['combined']:
        assert row['target_at'] == originals[row['session_id']]
        assert m.utc_timestamp(row['target_at']) < m.utc_timestamp(row['capture_completed_at']) < m.utc_timestamp(row['information_cutoff_at'])
    for field,amount in [('max_acquisition_span_ms',59999),('max_delivery_delay_ms',29999)]:
        changed = m.AnalysisPlan.model_validate({**new[1].model_dump(),field: amount})
        with pytest.raises(ValueError):m.freeze(m.cohort_index(new[0]),changed)


@pytest.mark.parametrize('change',['split','weights','receipt','threshold','versions','dataset','before_lock','before_train','endpoint_time','strata','pipeline_lock'])
def test_report_cannot_rebind_tampered_training_plans_or_temporal_order(cohort,change):
    dataset,plan,split = cohort
    artifacts,training,_,_ = pipeline(cohort)
    evaluated = '2026-03-03T00:00:00Z'
    if change == 'split':split = {**split,'training_participants': split['held_out_participants']}
    elif change == 'weights':artifacts['combined']['coefficients'][0] += .01
    elif change == 'receipt':training['eligible_session_ids'].pop()
    elif change == 'threshold':plan = m.AnalysisPlan.model_validate({**plan.model_dump(),'operating_threshold': .6})
    elif change == 'versions':plan = m.AnalysisPlan.model_validate({**plan.model_dump(),'versions': {**plan.versions.model_dump(),'task_sha256': 'f'*64}})
    elif change == 'dataset':
        value = dataset.model_dump();value['sessions'][0]['features']['saliva.THC']['value'] += .1;dataset = m.Dataset.model_validate(value)
    elif change == 'before_lock':training['trained_at'] = '2026-02-01T00:00:00Z'
    elif change == 'before_train':evaluated = '2026-03-01T12:00:00Z'
    elif change == 'pipeline_lock':training['pipeline_locked_at'] = '2026-03-01T00:00:00Z'
    elif change == 'strata':
        value = dataset.model_dump();value['sessions'][0]['strata']['route'] = 'unprespecified-route'
        dataset,plan,split = rebind(m.Dataset.model_validate(value),plan)
    else:
        value = dataset.model_dump();value['sessions'][0]['endpoint']['assessed_at'] = '2026-01-01T11:00:00Z'
        dataset,plan,split = rebind(m.Dataset.model_validate(value),plan)
    with pytest.raises(ValueError):m.evaluate(dataset,plan,split,artifacts,training,evaluated)


def test_later_validation_without_prior_held_out_session_and_single_class_cohort_fail(cohort):
    dataset,plan,split = cohort;value = dataset.model_dump()
    late_participant = next(row.participant_ref for row in dataset.sessions if row.session_id in split['session_ids']['later_sessions'])
    value['sessions'] = [row for row in value['sessions'] if not (row['participant_ref'] == late_participant and row['target_at'].startswith('2026-01'))]
    with pytest.raises(ValueError):rebind(m.Dataset.model_validate(value),plan)
    value = dataset.model_dump()
    for row in value['sessions']:
        if row['session_id'] in split['session_ids']['later_sessions']:row['endpoint']['value'] = 1
    with pytest.raises(ValueError):pipeline(rebind(m.Dataset.model_validate(value),plan))


def test_cli_private_canonical_pipeline_and_full_reproduction_detect_corruption(cohort,tmp_path):
    dataset,plan,_ = cohort
    schemas = tmp_path/'schemas'
    assert m.main(['schemas','--output',str(schemas)])['schemas'] == ['analysis-plan','cohort-index','dataset']
    assert m.load(schemas/'dataset.schema.json')['additionalProperties'] is False
    data,analysis,index,split = [tmp_path/name for name in ('data.json','analysis.json','index.json','split.json')]
    m.store(data,dataset.model_dump());m.store(analysis,plan.model_dump())
    assert m.main(['index','--dataset',str(data),'--output',str(index)])['outcomes_disclosed'] is False
    m.main(['freeze','--index',str(index),'--analysis',str(analysis),'--output',str(split)])
    common = ['--dataset',str(data),'--analysis',str(analysis),'--split',str(split)]
    training,evaluation = tmp_path/'training',tmp_path/'evaluation'
    m.main(['train',*common,'--output',str(training)])
    extra = ['--training-directory',str(training)]
    m.main(['evaluate',*common,*extra,'--output',str(evaluation)])
    assert m.main(['verify',*common,*extra,'--evaluation-directory',str(evaluation)])['evaluation_reproduced'] is True
    for directory in (training,evaluation):
        assert directory.stat().st_mode & 0o777 == 0o700
        for path in directory.iterdir():
            assert path.read_bytes() == canonical(m.load(path)) and path.stat().st_mode & 0o777 == 0o600
    with pytest.raises(FileExistsError):m.main(['train',*common,'--output',str(training)])
    report = m.load(evaluation/'evaluation-report.json');report['confirmatory']['brier'] += .001
    (evaluation/'evaluation-report.json').write_bytes(canonical(report))
    with pytest.raises(ValueError):m.main(['verify',*common,*extra,'--evaluation-directory',str(evaluation)])


def test_json_ingestion_is_bounded_duplicate_safe_and_data_only(tmp_path):
    bad = tmp_path/'bad.json';bad.write_text('{"threshold":0.5,"threshold":0.9}')
    with pytest.raises(ValueError):m.load(bad)
    linked = tmp_path/'linked.json';linked.symlink_to(bad)
    with pytest.raises((ValueError,OSError)):m.load(linked)
    bad.write_bytes(b' '*(m.MAX_BYTES+1))
    with pytest.raises(ValueError):m.load(bad)


def test_input_snapshot_uses_bounded_read_and_rejects_nonregular_files(tmp_path,monkeypatch):
    regular = tmp_path/'bounded.json';regular.write_text('{"safe":true}')
    original = m.os.fdopen;limits = []
    class TrackedReader:
        def __init__(self,descriptor):self.opened = original(descriptor,'rb')
        def __enter__(self):return self
        def __exit__(self,*_):self.opened.close()
        def fileno(self):return self.opened.fileno()
        def read(self,limit):limits.append(limit);return self.opened.read(limit)
    monkeypatch.setattr(m.os,'fdopen',lambda descriptor,*_: TrackedReader(descriptor))
    assert m.load(regular) == {'safe': True} and limits == [m.MAX_BYTES+1]
    fifo = tmp_path/'named-pipe';m.os.mkfifo(fifo)
    with pytest.raises(ValueError):m.load(fifo)


@pytest.mark.parametrize('change', ['same_size_metadata', 'size'])
def test_descriptor_change_during_actual_bounded_read_refuses_training_without_output(cohort, tmp_path, monkeypatch, change):
    dataset, plan, split = cohort
    data, analysis, frozen = [tmp_path / name for name in ('dataset.json', 'analysis.json', 'split.json')]
    m.store(data, dataset.model_dump()); m.store(analysis, plan.model_dump()); m.store(frozen, split)
    original_bytes = data.read_bytes()
    original_stat = data.stat()
    original_fdopen = m.os.fdopen
    reads = []
    mutated = []

    class ChangingReader:
        def __init__(self, opened):self.opened = opened
        def __enter__(self):return self
        def __exit__(self, *_):self.opened.close()
        def fileno(self):return self.opened.fileno()
        def read(self, limit):
            reads.append(limit)
            raw = self.opened.read(limit)
            # load() already took its first real fstat. Change the same inode
            # through a second descriptor before load() takes its second fstat.
            if not mutated:
                changed = (original_bytes.replace(b'engineering-fixture-only', b'ENGINEERING-fixture-only')
                    if change == 'same_size_metadata' else original_bytes + b' ')
                data.write_bytes(changed)
                m.os.utime(data, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns + 1_000_000_000))
                mutated.append(changed)
            return raw

    def tracked_fdopen(descriptor, *args, **kwargs):
        opened = original_fdopen(descriptor, *args, **kwargs)
        return ChangingReader(opened) if m.os.fstat(descriptor).st_ino == original_stat.st_ino else opened

    monkeypatch.setattr(m.os, 'fdopen', tracked_fdopen)
    output = tmp_path / 'training'
    with pytest.raises(ValueError, match='Input changed during bounded snapshot admission'):
        m.main(['train', '--dataset', str(data), '--analysis', str(analysis), '--split', str(frozen), '--output', str(output)])
    assert not output.exists() and not list(tmp_path.glob('*.artifact.json'))
    assert reads == [m.MAX_BYTES + 1] and len(mutated) == 1
    assert data.stat().st_ino == original_stat.st_ino
    assert data.stat().st_mtime_ns != original_stat.st_mtime_ns
    assert len(mutated[0]) == len(original_bytes) + (1 if change == 'size' else 0)
    # The adjacent stable read of this very same file still admits its exact
    # current bytes; the reader does not manufacture a blanket refusal.
    assert m.load(data, m.Dataset).model_dump() == m.strict_loads(mutated[0])
    assert reads == [m.MAX_BYTES + 1, m.MAX_BYTES + 1]
    assert not output.exists()


def assert_sparse_subgroups_preserve_rows_and_unsupported_statistics(cohort):
    dataset, plan, split = cohort
    original = deepcopy([dataset.model_dump(), plan.model_dump(), split])
    original_artifacts, _ = m.train(dataset, plan, split, '2026-03-02T00:00:00Z')
    people = sorted(split['held_out_participants'])
    raw, analysis = dataset.model_dump(), plan.model_dump()
    analysis['strata']['route'] = ['fictional-only-positive', 'fictional-only-negative', 'fictional-empty']
    analysis['strata']['population'] = ['fictional-single-participant', 'fictional-two-participants', 'fictional-other']
    for row in raw['sessions']:
        row['strata']['route'] = 'fictional-only-positive' if row['endpoint']['value'] else 'fictional-only-negative'
        row['strata']['population'] = ('fictional-single-participant' if row['participant_ref'] == people[0]
            else 'fictional-two-participants' if row['participant_ref'] in people[1:3] else 'fictional-other')
    sparse = rebind(m.Dataset.model_validate(raw), m.AnalysisPlan.model_validate(analysis))
    expected_dataset_hash, expected_plan_hash, expected_split_hash = (digest(sparse[0].model_dump()),
        digest(sparse[1].model_dump()), digest(sparse[2]))
    assert sparse[2]['session_ids'] == split['session_ids']
    for source, current in zip(original[0]['sessions'], sparse[0].model_dump()['sessions']):
        assert {key: value for key, value in current.items() if key != 'strata'} == {key: value for key, value in source.items() if key != 'strata'}
    artifacts, training, report, evidence = pipeline(sparse)
    assert artifacts == original_artifacts
    expected_variants = {'cardiac_hr_only'} if plan.cardiac_timing_policy is not None else set(m.VARIANTS)
    assert set(artifacts) == set(report['ablations']) == expected_variants
    for bound in (training, report, evidence):
        assert bound['dataset_sha256'] == expected_dataset_hash
        assert bound['analysis_plan_sha256'] == expected_plan_hash
        assert bound['split_plan_sha256'] == expected_split_hash
    assert evidence['artifact_sha256'] == {name: digest(value) for name, value in original_artifacts.items()}
    for partition in ('confirmatory', 'later_sessions'):
        assert set(evidence['row_predictions'][partition]) == expected_variants
        for dimension, categories in sparse[1].strata.items():
            groups = evidence['subgroups'][partition][dimension]
            assert set(groups) == set(categories)
            for variant in expected_variants:
                members = [identity for category in groups.values() for identity in category[variant]['session_ids']]
                assert sorted(members) == split['session_ids'][partition] and len(set(members)) == 8
                assert sum(category[variant]['metrics']['total'] for category in groups.values()) == 8
                assert sum(category[variant]['metrics']['positives'] for category in groups.values()) == 4
                assert sum(category[variant]['metrics']['negatives'] for category in groups.values()) == 4
                assert sum(category[variant]['metrics']['valid'] for category in groups.values()) == 8
                assert sum(category[variant]['metrics']['invalid'] for category in groups.values()) == 0
                assert sum(category[variant]['metrics']['abstained'] for category in groups.values()) == 0
        for variant in expected_variants:
            route = evidence['subgroups'][partition]['route']
            for category, positive in [('fictional-only-positive', True), ('fictional-only-negative', False)]:
                group = route[category][variant]; summary, detail = group['metrics'], group['details']
                expected_ids = [row.session_id for row in sparse[0].sessions
                    if row.session_id in split['session_ids'][partition] and row.endpoint.value == int(positive)]
                assert group['session_ids'] == sorted(expected_ids)
                assert summary['total'] == summary['valid'] == detail['participants'] == 4
                assert summary['positives'] == (4 if positive else 0)
                assert summary['negatives'] == (0 if positive else 4)
                assert summary['sensitivity'] == (1.0 if positive else None)
                assert summary['specificity'] == (None if positive else 1.0)
                assert summary['sensitivity_interval'] == ([1.0, 1.0] if positive else None)
                assert summary['specificity_interval'] == (None if positive else [1.0, 1.0])
                assert detail['defined_sensitivity_draws'] == (200 if positive else 0)
                assert detail['defined_specificity_draws'] == (0 if positive else 200)
                assert detail['unestimable_reasons'] == [('NO_ENDPOINT_NEGATIVES' if positive else 'NO_ENDPOINT_POSITIVES'),
                    'INSUFFICIENT_DEFINED_CLASSIFICATION_BOOTSTRAP_DRAWS']
                predictive = detail['predictive_values']
                assert predictive['classified_positive_denominator'] == (4 if positive else 0)
                assert predictive['classified_negative_denominator'] == (0 if positive else 4)
                assert predictive['positive_predictive_value'] == (1.0 if positive else None)
                assert predictive['negative_predictive_value'] == (None if positive else 1.0)
                assert predictive['positive_interval'] == ([1.0, 1.0] if positive else None)
                assert predictive['negative_interval'] == (None if positive else [1.0, 1.0])
                assert predictive['defined_positive_draws'] == (200 if positive else 0)
                assert predictive['defined_negative_draws'] == (0 if positive else 200)
                assert predictive['observed_endpoint_prevalence'] == float(positive)
                assert predictive['decision_coverage'] == predictive['probability_coverage'] == 1.0
            population = evidence['subgroups'][partition]['population']
            for category, participants in [('fictional-single-participant', 1), ('fictional-two-participants', 2)]:
                group = population[category][variant]; summary, detail = group['metrics'], group['details']
                assert summary['total'] == summary['valid'] == 2 * participants
                assert summary['positives'] == summary['negatives'] == participants
                assert summary['sensitivity'] == summary['specificity'] == 1.0
                assert detail['participants'] == participants and detail['draws'] == 200
                assert detail['defined_sensitivity_draws'] == detail['defined_specificity_draws'] == (0 if participants == 1 else 200)
                assert summary['sensitivity_interval'] == summary['specificity_interval'] == (None if participants == 1 else [1.0, 1.0])
                assert detail['unestimable_reasons'] == (['INSUFFICIENT_PARTICIPANTS_FOR_CLUSTER_INTERVAL',
                    'INSUFFICIENT_DEFINED_CLASSIFICATION_BOOTSTRAP_DRAWS'] if participants == 1 else [])
                predictive = detail['predictive_values']
                assert predictive['classified_positive_denominator'] == predictive['classified_negative_denominator'] == participants
                assert predictive['positive_predictive_value'] == predictive['negative_predictive_value'] == 1.0
                assert predictive['positive_interval'] == predictive['negative_interval'] == (None if participants == 1 else [1.0, 1.0])
                assert predictive['defined_positive_draws'] == predictive['defined_negative_draws'] == (0 if participants == 1 else 200)
                assert predictive['observed_endpoint_prevalence'] == 0.5
                assert predictive['decision_coverage'] == predictive['probability_coverage'] == 1.0
    assert [dataset.model_dump(), plan.model_dump(), split] == original


def test_sparse_one_class_and_participant_boundary_subgroups_preserve_all_rows(cohort):
    assert_sparse_subgroups_preserve_rows_and_unsupported_statistics(cohort)


@pytest.mark.parametrize('label,positive_draws,negative_draws', [
    ('fictional-sparse-boundary-1', 149, 163), ('fictional-sparse-boundary-5', 150, 146)])
def test_predictive_intervals_require_frozen_minimum_defined_cluster_draws(cohort, label, positive_draws, negative_draws):
    _, original_plan, _ = cohort
    # One fixed prespecified minimum in both cases; actual seeded resampling
    # produces minimum - 1 and exact minimum. No fabricated bootstrap provider.
    plan = m.AnalysisPlan.model_validate({**original_plan.model_dump(), 'minimum_defined_bootstrap_replicates': 150})
    rows = [{'session_id': 'fictional-positive-session', 'participant_ref': 'fictional-positive', 'endpoint': 1,
        'state': 'classified', 'probability': 0.9, 'predicted_positive': True, 'reason_codes': []},
        {'session_id': 'fictional-negative-session', 'participant_ref': 'fictional-negative', 'endpoint': 0,
        'state': 'classified', 'probability': 0.1, 'predicted_positive': False, 'reason_codes': []}]
    original = deepcopy(rows)
    summary, detail = m.metrics(rows, plan, label, allow_unestimable=True)
    assert rows == original
    assert summary['total'] == summary['valid'] == detail['participants'] == 2
    assert summary['positives'] == summary['negatives'] == 1 and summary['invalid'] == summary['abstained'] == 0
    assert summary['sensitivity'] == summary['specificity'] == 1.0
    assert detail['draws'] == 200 and detail['defined_sensitivity_draws'] == positive_draws
    assert detail['defined_specificity_draws'] == negative_draws
    assert summary['sensitivity_interval'] == (None if positive_draws == 149 else [1.0, 1.0])
    assert summary['specificity_interval'] == ([1.0, 1.0] if negative_draws == 163 else None)
    assert detail['unestimable_reasons'] == ['INSUFFICIENT_DEFINED_CLASSIFICATION_BOOTSTRAP_DRAWS']
    predictive = detail['predictive_values']
    assert predictive['classified_positive_denominator'] == predictive['classified_negative_denominator'] == 1
    assert predictive['positive_predictive_value'] == predictive['negative_predictive_value'] == 1.0
    assert predictive['defined_positive_draws'] == positive_draws and predictive['defined_negative_draws'] == negative_draws
    assert predictive['positive_interval'] == summary['sensitivity_interval']
    assert predictive['negative_interval'] == summary['specificity_interval']
    assert predictive['observed_endpoint_prevalence'] == 0.5
    assert predictive['decision_coverage'] == predictive['probability_coverage'] == 1.0
    assert predictive['qualification'] == 'conditional_on_classification_and_observed_locked_cohort_prevalence_not_target_population'


def test_subgroups_reconcile_all_rows_and_predictive_values_are_prevalence_qualified(cohort):
    _,plan,split = cohort
    _,_,_,evidence = pipeline(cohort)
    for cohort_name in ('confirmatory','later_sessions'):
        for dimension in m.STRATA:
            groups = evidence['subgroups'][cohort_name][dimension]
            assert set(groups) == set(plan.strata[dimension])
            for variant in m.VARIANTS:
                identities = [identity for group in groups.values() for identity in group[variant]['session_ids']]
                assert sorted(identities) == split['session_ids'][cohort_name]
                assert sum(group[variant]['metrics']['total'] for group in groups.values()) == len(identities)
        empty = evidence['subgroups'][cohort_name]['route']['fictional-empty-route']['combined']
        assert empty['metrics']['total'] == 0 and empty['metrics']['sensitivity'] is None
        assert empty['metrics']['specificity_interval'] is None and 'EMPTY_PRESPECIFIED_STRATUM' in empty['details']['unestimable_reasons']
        details = evidence['metric_details'][cohort_name]['combined']
        assert details['classification_rate_labels'] == ['positive_percent_agreement','negative_percent_agreement']
        predictive = details['predictive_values']
        assert predictive['observed_endpoint_prevalence'] == .5 and predictive['decision_coverage'] == 1
        assert predictive['positive_predictive_value'] == predictive['negative_predictive_value'] == 1
        assert predictive['positive_interval'] == predictive['negative_interval'] == [1.,1.]
        assert 'not_target_population' in predictive['qualification']


def test_actual_toolkit_artifact_and_postfit_lock_pass_server_chronology_guard(cohort,monkeypatch):
    """Source contract regression; authorization/storage here are unit doubles."""
    from types import SimpleNamespace
    from unittest.mock import Mock
    from otgd import domain, model_engine, storage
    artifacts,_,report,_ = pipeline(cohort)
    artifact = artifacts['combined'];raw = canonical(artifact);artifact_hash = digest(artifact)
    body = {'manifest': {'feature_version': 'otgd.features.v1','input_contract_version': '0.1.0',
        'calibration_id': artifact['calibration']['calibration_id'], 'artifact_sha256': artifact_hash,
        'required_channels': sorted({model_engine.FEATURE_CHANNELS[name] for name in artifact['feature_names'] if model_engine.FEATURE_CHANNELS[name]})},
        'evaluation_report': report}
    resolved = {'body': body, 'ref': {'sha256': artifact_hash,'size_bytes': len(raw),'bucket': 'fictional-model-bucket','key': 'models/fictional.json','version_id': 'fictional-version'},
        'calibration': {'calibration_sha256': digest(artifact['calibration'])}, 'proof': {}, 'baseline': None,'timing_qualified': True,'timing_bias_ms': 0.,'optical_qualified': False}
    monkeypatch.setattr(model_engine,'execution_authority',lambda *_: resolved)
    monkeypatch.setattr(storage,'versioned_read',lambda *_: raw)
    execute = Mock(return_value={'state': 'unit-chronology-admitted'})
    monkeypatch.setattr(model_engine,'execute',execute)
    monkeypatch.setattr(domain,'measurement_result',lambda _: {'state': 'measurement_only','reason_codes': []})
    check = SimpleNamespace(mode='controlled_research',snapshot={})
    assert model_engine.result_for_check(None,None,check)['state'] == 'unit-chronology-admitted'
    execute.assert_called_once();execute.reset_mock()
    body['evaluation_report'] = {**report,'locked_at': '2026-03-01T00:00:00Z'}
    assert model_engine.result_for_check(None,None,check)['state'] == 'inconclusive'
    execute.assert_not_called()


@pytest.mark.parametrize('arguments',[['schemas'],['index'],['freeze'],['train'],['evaluate'],['verify']])
def test_cli_missing_inputs_do_not_create_authority(arguments):
    with pytest.raises(ValueError):m.main(arguments)
