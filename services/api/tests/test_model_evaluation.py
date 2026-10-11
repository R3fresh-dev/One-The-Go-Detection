"""Fictional engineered cohorts qualify software, never a human-study model."""
import math
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
def test_invalid_or_future_source_data_are_rejected_before_fitting(cohort,change):
    dataset,_,_ = cohort;value = dataset.model_dump();row = value['sessions'][0]
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
