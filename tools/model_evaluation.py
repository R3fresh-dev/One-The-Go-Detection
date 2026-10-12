#!/usr/bin/env python3
"""Offline, data-only training and locked evaluation; never grants model authority.

The custodian can produce an index without revealing outcomes to the freeze
step. Historical plan locks, label independence and research authorization are
external evidence, not facts proved by this tool's timestamps or JSON fields.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import math
import os
from pathlib import Path
import random
import stat
import sys
from typing import Annotated, Literal

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'services' / 'api'))
from pydantic import Field, FiniteFloat, field_validator, model_validator
from otgd.canonical import canonical, digest, strict_loads
from otgd.model_engine import Artifact, EvaluationReport, FEATURE_CHANNELS, Strict, score, utc_timestamp
from otgd import cardiac_authority
from otgd.errors import Problem
from spec_validation import validate_session
from jsonschema.exceptions import ValidationError as SchemaError

MAX_BYTES = 16 * 1024 * 1024
MAX_ROWS = 2000
MAX_PARTICIPANTS = 1000
Name = Annotated[str, Field(min_length=1, max_length=256)]
Hash = Annotated[str, Field(pattern=r'^[0-9a-f]{64}$')]
Time = Annotated[str, Field(min_length=20, max_length=40)]
VARIANTS = ('chemical_only', 'app_only', 'combined', 'ecg_removed')
STRATA = ('route','use_frequency','co_use','device','baseline','population')
Stratum = Literal['route','use_frequency','co_use','device','baseline','population']
StratumName = Annotated[str, Field(min_length=1,max_length=64)]


class InvalidEvidence(ValueError):
    pass


class Versions(Strict):
    acquisition_sha256: Hash
    assay_sha256: Hash
    task_sha256: Hash
    input_contract_version: Literal['0.1.0']
    feature_version: Literal['otgd.features.v1']


class Predictor(Strict):
    status: Literal['valid', 'missing', 'censored', 'invalid']
    value: FiniteFloat | None
    observed_at: Time | None
    available_at: Time | None

    @model_validator(mode='after')
    def consistent(self):
        if self.available_at is not None:
            utc_timestamp(self.available_at)
        if self.observed_at is not None:
            utc_timestamp(self.observed_at)
        if self.observed_at and self.available_at and utc_timestamp(self.observed_at) > utc_timestamp(self.available_at):
            raise ValueError('Predictor availability cannot precede observation')
        if self.status == 'valid' and (self.value is None or self.observed_at is None or self.available_at is None):
            raise ValueError('Valid predictors require measured values and availability times')
        if self.status != 'valid' and self.value is not None:
            raise ValueError('Missing/censored/invalid predictors must retain null values')
        return self


class Endpoint(Strict):
    endpoint_id: Name
    value: Literal[0, 1]
    assessed_at: Time
    available_at: Time
    source_ref: Name
    assessor_ref: Name
    independently_assessed: Literal[True]

    @field_validator('value', mode='before')
    @classmethod
    def binary_integer(cls, value):
        if type(value) is not int or value not in (0,1):
            raise ValueError('Endpoint labels must be integer zero or one')
        return value

    @field_validator('independently_assessed', mode='before')
    @classmethod
    def independent_boolean(cls, value):
        if value is not True:
            raise ValueError('Independent assessment assertion must be true')
        return value

    @model_validator(mode='after')
    def consistent(self):
        if type(self.value) is not int or utc_timestamp(self.available_at) < utc_timestamp(self.assessed_at):
            raise ValueError('Independent binary endpoint and assessment availability are required')
        return self


class CardiacProvenance(Strict):
    """References to an independently reviewed retained bundle, not authentication."""
    reviewed_source_bundle_ref: Name
    reviewed_source_bundle_sha256: Hash
    independent_review_ref: Name
    independent_review_sha256: Hash
    calibration_registry_sha256: Hash
    calibration_scope_sha256: Hash
    qualification_registry_sha256: Hash
    device_registry_sha256: Hash
    configuration_submitted_sha256: Hash


class CardiacRowEvidence(Strict):
    snapshot: dict
    snapshot_sha256: Hash
    authority: cardiac_authority.CardiacAuthority
    authority_sha256: Hash
    source_bundle_ref: Name
    source_bundle_sha256: Hash
    baseline_snapshot: dict | None
    baseline_snapshot_sha256: Hash | None


class Session(Strict):
    session_id: Name
    participant_ref: Name
    target_at: Time
    capture_completed_at: Time
    information_cutoff_at: Time
    acquisition_status: Literal['valid', 'invalid']
    quality_flags: Annotated[list[Name], Field(max_length=16)]
    features: Annotated[dict[str, Predictor], Field(max_length=16)]
    endpoint: Endpoint
    strata: dict[Stratum, StratumName]
    cardiac_evidence: CardiacRowEvidence | None = Field(default=None, exclude_if=lambda value: value is None)

    @model_validator(mode='after')
    def current_predictors(self):
        target = utc_timestamp(self.target_at)
        capture, cutoff = utc_timestamp(self.capture_completed_at), utc_timestamp(self.information_cutoff_at)
        if not target <= capture <= cutoff:
            raise ValueError('Original target, capture completion and information cutoff are out of order')
        if any(name not in FEATURE_CHANNELS for name in self.features):
            raise ValueError('Unknown or outcome-derived predictors are forbidden')
        for name,value in self.features.items():
            observation_limit = target if name.startswith('profile.') else capture
            availability_limit = target if name.startswith('profile.') else cutoff
            if ((value.observed_at and utc_timestamp(value.observed_at) > observation_limit)
                or (value.available_at and utc_timestamp(value.available_at) > availability_limit)):
                raise ValueError('Predictors after the original-profile or same-check cutoff are forbidden, including invalid rows')
        if len(set(self.quality_flags)) != len(self.quality_flags):
            raise ValueError('Duplicate quality flags')
        if set(self.strata) != set(STRATA):
            raise ValueError('Every row must retain all six prespecified stratification dimensions')
        return self


class Dataset(Strict):
    schema_version: Literal['1.0.0']
    data_kind: Literal['engineering_synthetic', 'authorized_research']
    authorization_ref: Name
    endpoint_id: Name
    endpoint_kind: Literal['current_functional_impairment']
    endpoint_definition: Annotated[str, Field(min_length=1, max_length=4096)]
    endpoint_source_ref: Name
    locked_at: Time
    versions: Versions
    sessions: Annotated[list[Session], Field(min_length=6, max_length=MAX_ROWS)]

    @model_validator(mode='after')
    def locked(self):
        locked = utc_timestamp(self.locked_at)
        if len({row.session_id for row in self.sessions}) != len(self.sessions):
            raise ValueError('Session identities must be unique')
        if len({row.participant_ref for row in self.sessions}) > MAX_PARTICIPANTS:
            raise ValueError('Participant bound exceeded')
        for row in self.sessions:
            if (row.endpoint.endpoint_id != self.endpoint_id or row.endpoint.source_ref != self.endpoint_source_ref
                or utc_timestamp(row.information_cutoff_at) > locked or utc_timestamp(row.endpoint.available_at) > locked):
                raise ValueError('Rows differ from the locked independent endpoint or contain unlocked observations')
        return self


class IndexRow(Strict):
    session_id: Name
    participant_ref: Name
    target_at: Time
    capture_completed_at: Time
    information_cutoff_at: Time
    endpoint_available_at: Time


class CohortIndex(Strict):
    schema_version: Literal['1.0.0']
    purpose: Literal['outcome_blind_cohort_index']
    dataset_sha256: Hash
    locked_at: Time
    data_kind: Literal['engineering_synthetic', 'authorized_research']
    endpoint_id: Name
    endpoint_definition_sha256: Hash
    versions: Versions
    sessions: Annotated[list[IndexRow], Field(min_length=6, max_length=MAX_ROWS)]


class Uncertainty(Strict):
    policy_id: Name
    method: Literal['none', 'probability_band']
    lower: FiniteFloat | None
    upper: FiniteFloat | None

    @model_validator(mode='after')
    def consistent(self):
        if self.method == 'none':
            if self.lower is not None or self.upper is not None:
                raise ValueError('No-abstention policy must have null bounds')
        elif self.lower is None or self.upper is None or not 0 <= self.lower <= self.upper <= 1:
            raise ValueError('Invalid frozen probability band')
        return self


class AnalysisPlan(Strict):
    schema_version: Literal['1.0.0']
    purpose: Literal['prespecified_logistic_evaluation']
    dataset_sha256: Hash
    plan_lock_ref: Name
    independent_endpoint_evidence_ref: Name
    prespecified_at: Time
    training_cutoff: Time
    later_session_boundary: Time
    endpoint_id: Name
    endpoint_definition_sha256: Hash
    comparator_kind: Literal['accepted_reference_standard','prespecified_independent_comparator']
    maximum_endpoint_offset_seconds: Annotated[int, Field(ge=1, le=86400)]
    max_acquisition_span_ms: Annotated[int, Field(ge=1, le=1800000)]
    max_delivery_delay_ms: Annotated[int, Field(ge=0, le=604800000)]
    versions: Versions
    seed: Name
    training_participant_count: Annotated[int, Field(ge=1, le=MAX_PARTICIPANTS-2)]
    feature_names: Annotated[list[Name], Field(min_length=1, max_length=16)]
    feature_limits: dict[str, list[FiniteFloat]]
    iterations: Annotated[int, Field(ge=1, le=2000)]
    learning_rate: Annotated[FiniteFloat, Field(gt=0, le=0.25)]
    l2_penalty: Annotated[FiniteFloat, Field(gt=0, le=10)]
    calibration_id: Name
    calibration_method: Literal['prespecified_identity']
    operating_threshold: Annotated[FiniteFloat, Field(gt=0, lt=1)]
    uncertainty_policy: Uncertainty
    calibration_bins: Annotated[int, Field(ge=2, le=20)]
    confidence_level: Annotated[FiniteFloat, Field(ge=0.8, lt=1)]
    bootstrap_replicates: Annotated[int, Field(ge=200, le=2000)]
    minimum_defined_bootstrap_replicates: Annotated[int, Field(ge=20, le=2000)]
    denominator_policy: Literal['all_sessions_invalid_and_abstention_are_failures']
    invalid_score_loss: Literal[1]
    strata: dict[Stratum, Annotated[list[StratumName], Field(min_length=1,max_length=12)]]
    cardiac_timing_policy: cardiac_authority.CardiacTimingPolicy | None = Field(default=None, exclude_if=lambda value: value is None)
    cardiac_provenance: CardiacProvenance | None = Field(default=None, exclude_if=lambda value: value is None)
    max_baseline_age_ms: Annotated[int, Field(ge=1, le=604800000)] | None = Field(default=None, exclude_if=lambda value: value is None)

    @field_validator('invalid_score_loss', mode='before')
    @classmethod
    def penalty_integer(cls, value):
        if type(value) is not int or value != 1:
            raise ValueError('Invalid score penalty must be integer one')
        return value

    @model_validator(mode='after')
    def frozen(self):
        utc_timestamp(self.prespecified_at)
        if utc_timestamp(self.training_cutoff) >= utc_timestamp(self.later_session_boundary):
            raise ValueError('Later-session boundary must follow the frozen training cutoff')
        if (len(set(self.feature_names)) != len(self.feature_names) or any(name not in FEATURE_CHANNELS for name in self.feature_names)
            or set(self.feature_limits) != set(self.feature_names)
            or any(len(pair) != 2 or pair[0] >= pair[1] or max(abs(v) for v in pair) > 1e6 for pair in self.feature_limits.values())):
            raise ValueError('Frozen unique features and finite ordered limits are required')
        if self.cardiac_timing_policy is not None:
            if (self.feature_names != ['cardiac.heart_rate_bpm'] or self.cardiac_provenance is None
                or self.cardiac_timing_policy.allow_baseline_delta != (self.max_baseline_age_ms is not None)):
                raise ValueError('HR-only plans require sole HR feature, reviewed provenance and explicit personalized age policy')
        elif (self.cardiac_provenance is not None or self.max_baseline_age_ms is not None or len(self.feature_names) < 3
            or 'cardiac.ecg_rmssd_ms' not in self.feature_names
            or not any(name.startswith('saliva.') for name in self.feature_names)
            or not any(not name.startswith('saliva.') and name != 'cardiac.ecg_rmssd_ms' for name in self.feature_names)):
            raise ValueError('Frozen chemistry/app/combined/ECG-removed feature sets and limits are required')
        if self.minimum_defined_bootstrap_replicates > self.bootstrap_replicates or type(self.invalid_score_loss) is not int:
            raise ValueError('Defined bootstrap replicate requirement exceeds planned draws')
        if set(self.strata) != set(STRATA) or any(len(set(values)) != len(values) for values in self.strata.values()):
            raise ValueError('All six subgroup dimensions and unique frozen categories are required')
        return self


def cohort_index(dataset: Dataset):
    """Custodian stage: no outcomes or predictor values appear in this index."""
    return CohortIndex.model_validate({
        'schema_version': '1.0.0', 'purpose': 'outcome_blind_cohort_index', 'dataset_sha256': digest(dataset.model_dump()),
        'locked_at': dataset.locked_at, 'data_kind': dataset.data_kind, 'endpoint_id': dataset.endpoint_id,
        'endpoint_definition_sha256': digest(dataset.endpoint_definition), 'versions': dataset.versions.model_dump(),
        'sessions': [{'session_id': row.session_id, 'participant_ref': row.participant_ref, 'target_at': row.target_at,
            'capture_completed_at': row.capture_completed_at, 'information_cutoff_at': row.information_cutoff_at,
            'endpoint_available_at': row.endpoint.available_at} for row in sorted(dataset.sessions, key=lambda row: row.session_id)]})


def freeze(index: CohortIndex, plan: AnalysisPlan):
    if (index.dataset_sha256 != plan.dataset_sha256 or index.endpoint_id != plan.endpoint_id
        or index.endpoint_definition_sha256 != plan.endpoint_definition_sha256 or index.versions != plan.versions
        or utc_timestamp(plan.prespecified_at) > utc_timestamp(index.locked_at)):
        raise InvalidEvidence('Dataset, frozen analysis, versions or claimed lock chronology differ')
    participants = sorted({row.participant_ref for row in index.sessions},
        key=lambda value: hashlib.sha256(canonical([plan.seed, value])).hexdigest())
    if len(participants) > MAX_PARTICIPANTS or plan.training_participant_count > len(participants)-2:
        raise InvalidEvidence('At least two entire held-out participants are required')
    if len({row.session_id for row in index.sessions}) != len(index.sessions):
        raise InvalidEvidence('Index session identities are duplicated')
    training = set(participants[:plan.training_participant_count])
    groups = {'training': [], 'confirmatory': [], 'later_sessions': []}
    excluded = []
    cutoff, boundary = utc_timestamp(plan.training_cutoff), utc_timestamp(plan.later_session_boundary)
    for row in index.sessions:
        target, label_available = utc_timestamp(row.target_at), utc_timestamp(row.endpoint_available_at)
        capture, cutoff_at = utc_timestamp(row.capture_completed_at), utc_timestamp(row.information_cutoff_at)
        # HR-only authority uses the independently qualified server interval at
        # row admission. Preserve original client times for custody/splitting;
        # an outcome-blind index cannot substitute them for that interval.
        if (not target <= capture <= cutoff_at or plan.cardiac_timing_policy is None and (
            (capture-target)*1000 > plan.max_acquisition_span_ms
            or (cutoff_at-capture)*1000 > plan.max_delivery_delay_ms)):
            raise InvalidEvidence('Same-check acquisition/delivery cutoff exceeds its frozen plan')
        if max(cutoff_at, label_available) > utc_timestamp(index.locked_at):
            raise InvalidEvidence('Index contains observations after the claimed dataset lock')
        if row.participant_ref in training:
            if max(cutoff_at, label_available) <= cutoff:
                groups['training'].append(row.session_id)
            else:
                excluded.append({'session_id': row.session_id, 'reason': 'TRAIN_PARTICIPANT_AFTER_FROZEN_CUTOFF'})
        else:
            groups['confirmatory' if target <= boundary else 'later_sessions'].append(row.session_id)
    early = {row.participant_ref for row in index.sessions if row.session_id in groups['confirmatory']}
    if any(row.participant_ref not in early for row in index.sessions if row.session_id in groups['later_sessions']):
        raise InvalidEvidence('Later validation requires an earlier locked session for each held-out participant')
    if any(not ids for ids in groups.values()):
        raise InvalidEvidence('Training, confirmatory and later-session partitions must all exist')
    return {'schema_version': '1.0.0', 'purpose': 'frozen_participant_temporal_split', 'dataset_sha256': index.dataset_sha256,
        'cohort_index_sha256': digest(index.model_dump()), 'analysis_plan_sha256': digest(plan.model_dump()),
        'training_participants': sorted(training), 'held_out_participants': sorted(set(participants)-training),
        'session_ids': {key: sorted(value) for key, value in groups.items()}, 'excluded_sessions': sorted(excluded, key=lambda row: row['session_id']),
        'participant_overlap': False, 'assignment': 'sha256_seed_participant_rank_v1'}


def variants(plan):
    if plan.cardiac_timing_policy is not None:
        return {'cardiac_hr_only': ['cardiac.heart_rate_bpm']}
    return {'chemical_only': [name for name in plan.feature_names if name.startswith('saliva.')],
        'app_only': [name for name in plan.feature_names if not name.startswith('saliva.')],
        'combined': list(plan.feature_names), 'ecg_removed': [name for name in plan.feature_names if name != 'cardiac.ecg_rmssd_ms']}


def cardiac_body(plan):
    return {'cardiac_timing_policy': plan.cardiac_timing_policy.data(), 'manifest': {
        'required_channels': ['cardiac_hr'], 'baseline_mode': 'personalized' if plan.cardiac_timing_policy.allow_baseline_delta else 'population',
        'max_clock_uncertainty_ms': plan.cardiac_timing_policy.max_interval_ms,
        'max_acquisition_span_ms': plan.max_acquisition_span_ms, 'max_delivery_delay_ms': plan.max_delivery_delay_ms},
        'quality_policy': {'max_baseline_age_ms': plan.max_baseline_age_ms}}


def cardiac_row_value(row, plan):
    """Verify offline consistency using runtime arithmetic at the historical cutoff.

    Editable JSON cannot verify retained signatures, custody principals, registry
    release or independent review. Those are mandatory external admission work.
    """
    try:
        item, provenance = row.cardiac_evidence, plan.cardiac_provenance
        if item is None or provenance is None:
            raise ValueError()
        snapshot, authority = item.snapshot, item.authority.data()
        validate_session(snapshot)
        body = cardiac_body(plan)
        if (item.snapshot_sha256 != digest(snapshot) or item.authority_sha256 != digest(authority)
            or snapshot['session_id'] != row.session_id or snapshot['subject_ref'] != row.participant_ref
            or snapshot['target_at'] != row.target_at or snapshot['capture_completed_at'] != row.capture_completed_at
            or snapshot['created_at'] != snapshot['target_at'] or snapshot['mode'] != 'controlled_research'
            or row.quality_flags != snapshot['cardiac']['quality_flags']
            or authority['policy'] != plan.cardiac_timing_policy.data()
            or item.source_bundle_ref != provenance.reviewed_source_bundle_ref
            or item.source_bundle_sha256 != provenance.reviewed_source_bundle_sha256):
            raise ValueError()
        current = cardiac_authority.validate_interval(snapshot, body, authority['current'],
            evaluated_epoch=utc_timestamp(row.information_cutoff_at))
        for name in ('calibration_registry_sha256', 'calibration_scope_sha256', 'qualification_registry_sha256',
            'device_registry_sha256', 'configuration_submitted_sha256'):
            if current[name] != getattr(provenance, name):
                raise ValueError()
        if (current['device_id'] != snapshot['device']['device_id']
            or current['boot_id'] != snapshot['device']['boot_id']
            or current['hardware_revision'] != snapshot['device']['hardware_revision']
            or current['firmware_version'] != snapshot['device']['firmware_version']
            or current['configuration_id'] != snapshot['cardiac']['acquisition_config_id']):
            raise ValueError()
        predictor = row.features.get('cardiac.heart_rate_bpm')
        if (predictor is None
            or predictor.observed_at is not None and utc_timestamp(predictor.observed_at) != utc_timestamp(snapshot['cardiac']['ended_at'])
            or predictor.available_at is not None and utc_timestamp(predictor.available_at) < current['received_epoch']):
            raise ValueError()
        baseline = None
        if plan.cardiac_timing_policy.allow_baseline_delta:
            baseline = item.baseline_snapshot
            if baseline is None or item.baseline_snapshot_sha256 != digest(baseline):
                raise ValueError()
            validate_session(baseline)
            old = cardiac_authority.validate_interval(baseline, body, authority['baseline'], baseline=True,
                evaluated_epoch=utc_timestamp(row.information_cutoff_at))
            if (snapshot['baseline_ref'] != baseline['session_id'] or baseline['created_at'] != baseline['target_at']
                or baseline['mode'] != 'controlled_research'
                or any(old[key] == current[key] for key in ('session_id', 'attempt_id', 'authorization_id', 'attestation_id'))
                or any(old[key] != baseline['device'][key] for key in ('device_id', 'boot_id', 'hardware_revision', 'firmware_version'))
                or old['configuration_id'] != baseline['cardiac']['acquisition_config_id']):
                raise ValueError()
            cardiac_authority.validate_baseline(snapshot, body, current, old)
        elif (item.baseline_snapshot is not None or item.baseline_snapshot_sha256 is not None
            or authority['baseline'] is not None or snapshot['baseline_ref'] is not None):
            raise ValueError()
        if cardiac_authority.build_authority(body, current, old if baseline is not None else None) != authority:
            raise ValueError()
        # The same runtime feature projection derives raw HR or its explicit
        # personal-baseline delta, including subject/protocol/study compatibility.
        from otgd.model_engine import feature_values
        prototype = Artifact.model_validate({'schema_version': '1.0.0', 'algorithm': 'logistic_linear_v1',
            'input_contract_version': '0.1.0', 'feature_version': plan.versions.feature_version,
            'feature_names': ['cardiac.heart_rate_bpm'], 'means': [0.0], 'scales': [1.0], 'coefficients': [0.0],
            'intercept': 0.0, 'calibration': {'calibration_id': plan.calibration_id, 'slope': 1.0, 'intercept': 0.0},
            'feature_limits': plan.feature_limits, 'trained_at': plan.prespecified_at})
        return feature_values(snapshot, prototype, baseline)[0]
    except (ValueError, KeyError, TypeError, OverflowError, Problem, SchemaError):
        raise InvalidEvidence('CARDIAC_EVIDENCE_INVALID') from None


def row_values(row, names, plan):
    reasons = []
    if row.acquisition_status != 'valid' or plan.cardiac_timing_policy is None and row.quality_flags:
        reasons.append('INVALID_ACQUISITION')
    derived = None
    if plan.cardiac_timing_policy is not None:
        try:
            derived = cardiac_row_value(row, plan)
        except InvalidEvidence:
            reasons.append('CARDIAC_EVIDENCE_INVALID')
    values = []
    for name in names:
        predictor = row.features.get(name)
        if predictor is None or predictor.status != 'valid':
            reasons.append('MISSING_OR_CENSORED:' + name)
        elif not plan.feature_limits[name][0] <= predictor.value <= plan.feature_limits[name][1]:
            reasons.append('OUTSIDE_PRESPECIFIED_LIMIT:' + name)
        elif plan.cardiac_timing_policy is not None and predictor.value != derived:
            reasons.append('CARDIAC_VALUE_NOT_DERIVED')
        else:
            values.append(float(predictor.value))
    return (None, sorted(reasons)) if reasons else (values, [])


def validate_binding(dataset, plan, split):
    expected = freeze(cohort_index(dataset), plan)
    if canonical(expected) != canonical(split):
        raise InvalidEvidence('Frozen split does not reproduce from this exact dataset and analysis')
    for row in dataset.sessions:
        if plan.cardiac_timing_policy is not None and set(row.features) != {'cardiac.heart_rate_bpm'}:
            raise InvalidEvidence('HR-only evaluation cannot include mixed-channel predictor rows')
        if plan.cardiac_timing_policy is None and row.cardiac_evidence is not None:
            raise InvalidEvidence('Cardiac evidence requires a separately prespecified HR-only analysis')
        if abs(utc_timestamp(row.endpoint.assessed_at)-utc_timestamp(row.target_at)) > plan.maximum_endpoint_offset_seconds:
            raise InvalidEvidence('Independent endpoint lies outside the prespecified target window')
        if any(row.strata[name] not in plan.strata[name] for name in STRATA):
            raise InvalidEvidence('Session stratum is absent from the frozen analysis categories')
    return {row.session_id: row for row in dataset.sessions}


def sigmoid(value):
    return 1 / (1 + math.exp(-value)) if value >= 0 else math.exp(value) / (1 + math.exp(value))


def fit_linear(rows, names, plan, trained_at):
    features = [[float(row.features[name].value) for name in names] for row in rows]
    count = len(rows)
    means = [math.fsum(row[j] for row in features) / count for j in range(len(names))]
    deviations = [math.sqrt(math.fsum((row[j]-means[j])**2 for row in features)/count) for j in range(len(names))]
    scales = [value if value >= 1e-12 else 1.0 for value in deviations]
    x = [[(value-means[j])/scales[j] for j, value in enumerate(row)] for row in features]
    y = [row.endpoint.value for row in rows]
    weights = [0.0] * len(names)
    intercept = 0.0
    for _ in range(plan.iterations):
        errors = [sigmoid(intercept + math.fsum(w*v for w,v in zip(weights,row)))-label for row,label in zip(x,y)]
        updated = [weight-plan.learning_rate*(math.fsum(error*row[j] for error,row in zip(errors,x))/count + plan.l2_penalty*weight)
            for j,weight in enumerate(weights)]
        intercept -= plan.learning_rate * math.fsum(errors)/count
        weights = updated
        if any(not math.isfinite(value) or abs(value) > 1e6 for value in [intercept, *weights]):
            raise InvalidEvidence('Fitting exceeded bounded finite artifact limits')
    return Artifact.model_validate({'schema_version': '1.0.0', 'algorithm': 'logistic_linear_v1',
        'input_contract_version': '0.1.0', 'feature_version': plan.versions.feature_version, 'feature_names': names,
        'means': means, 'scales': scales, 'coefficients': weights, 'intercept': intercept,
        'calibration': {'calibration_id': plan.calibration_id, 'slope': 1.0, 'intercept': 0.0},
        'feature_limits': {name: plan.feature_limits[name] for name in names}, 'trained_at': trained_at})


def cardiac_evidence_manifest(dataset, plan):
    """Cohort custody inventory; distinct from each signed capture's manifest."""
    return {'schema_version': '1.0.0', 'purpose': 'offline_cardiac_cohort_custody_inventory',
        'dataset_sha256': digest(dataset.model_dump()), 'analysis_plan_sha256': digest(plan.model_dump()),
        'provenance': plan.cardiac_provenance.model_dump(), 'cardiac_timing_policy': plan.cardiac_timing_policy.data(),
        'rows': [{'session_id': row.session_id, 'session_record_sha256': digest(row.model_dump()),
            'source_bundle_ref': row.cardiac_evidence.source_bundle_ref if row.cardiac_evidence else None,
            'source_bundle_sha256': row.cardiac_evidence.source_bundle_sha256 if row.cardiac_evidence else None,
            'snapshot_sha256': row.cardiac_evidence.snapshot_sha256 if row.cardiac_evidence else None,
            'authority_sha256': row.cardiac_evidence.authority_sha256 if row.cardiac_evidence else None,
            'baseline_snapshot_sha256': row.cardiac_evidence.baseline_snapshot_sha256 if row.cardiac_evidence else None,
            'captured_session_evidence_manifest_sha256': row.cardiac_evidence.authority.current.evidence_manifest_sha256 if row.cardiac_evidence else None,
            'baseline_captured_session_evidence_manifest_sha256': row.cardiac_evidence.authority.baseline.evidence_manifest_sha256 if row.cardiac_evidence and row.cardiac_evidence.authority.baseline else None,
            'preserved_quality_flags': row.quality_flags}
            for row in sorted(dataset.sessions, key=lambda value: value.session_id)],
        'signatures_registry_release_and_independent_review_authenticated': False}


def train(dataset, plan, split, trained_at, pipeline_locked_at=None):
    rows = validate_binding(dataset, plan, split)
    if not utc_timestamp(dataset.locked_at) <= utc_timestamp(trained_at) <= datetime.now(timezone.utc).timestamp():
        raise InvalidEvidence('Training must follow the dataset lock and cannot claim a future execution')
    pipeline_locked_at = pipeline_locked_at or trained_at
    if not utc_timestamp(trained_at) <= utc_timestamp(pipeline_locked_at) <= datetime.now(timezone.utc).timestamp():
        raise InvalidEvidence('Frozen pipeline time must follow fitting and cannot be in the future')
    eligible, rejected = [], []
    for identity in split['session_ids']['training']:
        row = rows[identity]
        values, reasons = row_values(row, plan.feature_names, plan)
        if values is None:
            rejected.append({'session_id': identity, 'reasons': reasons})
        else:
            eligible.append(row)
    if {row.endpoint.value for row in eligible} != {0, 1}:
        raise InvalidEvidence('Identical complete training rows must contain both independent outcome classes')
    artifacts = {name: fit_linear(eligible, names, plan, trained_at).model_dump() for name,names in variants(plan).items()}
    receipt = {'schema_version': '1.0.0', 'purpose': 'offline_training_evidence', 'data_kind': dataset.data_kind,
        'dataset_sha256': digest(dataset.model_dump()), 'analysis_plan_sha256': digest(plan.model_dump()), 'split_plan_sha256': digest(split),
        'artifact_sha256': {name: digest(value) for name,value in artifacts.items()}, 'trained_at': trained_at,
        'dataset_custody_locked_at': dataset.locked_at, 'pipeline_locked_at': pipeline_locked_at,
        'eligible_session_ids': [row.session_id for row in eligible], 'rejected_training_rows': rejected,
        'preprocessing': 'training_only_population_mean_sd_constant_scale_one_v1', 'calibration': 'prespecified_identity',
        'selection': 'all_prespecified_features_no_confirmatory_tuning', 'authority_granted': False}
    if plan.cardiac_timing_policy is not None:
        receipt.update(analysis_scope='cardiac_hr_only', cardiac_evidence_manifest_sha256=digest(cardiac_evidence_manifest(dataset, plan)))
    return artifacts, receipt


def predictions(rows, artifact, plan):
    result = []
    for row in rows:
        values, reasons = row_values(row, artifact.feature_names, plan)
        probability = None if values is None else score(artifact, values)
        abstained = probability is not None and plan.uncertainty_policy.method == 'probability_band' and plan.uncertainty_policy.lower <= probability <= plan.uncertainty_policy.upper
        result.append({'session_id': row.session_id, 'participant_ref': row.participant_ref, 'target_at': row.target_at,
            'capture_completed_at': row.capture_completed_at, 'information_cutoff_at': row.information_cutoff_at,
            'strata': row.strata,
            'endpoint': row.endpoint.value, 'state': 'invalid' if probability is None else 'abstained' if abstained else 'classified',
            'probability': probability, 'predicted_positive': None if probability is None or abstained else probability >= plan.operating_threshold,
            'reason_codes': reasons if probability is None else ['PRESPECIFIED_UNCERTAINTY_ABSTENTION'] if abstained else []})
        if plan.cardiac_timing_policy is not None:
            item = row.cardiac_evidence
            result[-1].update(preserved_quality_flags=row.quality_flags,
                snapshot_sha256=item.snapshot_sha256 if item else None,
                authority_sha256=item.authority_sha256 if item else None)
    return result


def quantile(values, q):
    ordered = sorted(values)
    location = (len(ordered)-1)*q
    low = math.floor(location)
    return ordered[low] + (ordered[math.ceil(location)]-ordered[low])*(location-low)


def cluster_draws(rows, plan, cohort):
    participants = sorted({row['participant_ref'] for row in rows})
    if len(participants) < 2:
        raise InvalidEvidence('Participant-cluster intervals require at least two held-out participants')
    generator = random.Random(int(hashlib.sha256(canonical([plan.seed, cohort, 'participant_cluster_v1'])).hexdigest(), 16))
    for _ in range(plan.bootstrap_replicates):
        yield Counter(generator.choices(participants, k=len(participants)))


def confusion(rows, weights=None):
    counts = dict(positives=0, negatives=0, true_positive=0, true_negative=0, classified_false_positive=0, classified_false_negative=0)
    for row in rows:
        weight = 1 if weights is None else weights[row['participant_ref']]
        counts['positives' if row['endpoint'] else 'negatives'] += weight
        if row['state'] == 'classified' and row['predicted_positive'] == bool(row['endpoint']):
            counts['true_positive' if row['endpoint'] else 'true_negative'] += weight
        elif row['state'] == 'classified':
            counts['classified_false_negative' if row['endpoint'] else 'classified_false_positive'] += weight
    return counts


def metrics(rows, plan, cohort, allow_unestimable=False):
    counts = confusion(rows)
    if not allow_unestimable and (not counts['positives'] or not counts['negatives']):
        raise InvalidEvidence('Every frozen evaluation cohort must retain both outcome classes')
    sensitivity_draws, specificity_draws, ppv_draws, npv_draws = [], [], [], []
    participant_count = len({row['participant_ref'] for row in rows})
    draws = cluster_draws(rows, plan, cohort) if participant_count >= 2 or not allow_unestimable else []
    for weights in draws:
        draw = confusion(rows, weights)
        if draw['positives']:
            sensitivity_draws.append(draw['true_positive']/draw['positives'])
        if draw['negatives']:
            specificity_draws.append(draw['true_negative']/draw['negatives'])
        if draw['true_positive']+draw['classified_false_positive']:
            ppv_draws.append(draw['true_positive']/(draw['true_positive']+draw['classified_false_positive']))
        if draw['true_negative']+draw['classified_false_negative']:
            npv_draws.append(draw['true_negative']/(draw['true_negative']+draw['classified_false_negative']))
    if not allow_unestimable and min(len(sensitivity_draws), len(specificity_draws)) < plan.minimum_defined_bootstrap_replicates:
        raise InvalidEvidence('Too few defined participant-cluster draws for the frozen uncertainty plan')
    tail = (1-plan.confidence_level)/2
    interval = lambda values: [quantile(values,tail),quantile(values,1-tail)] if len(values) >= plan.minimum_defined_bootstrap_replicates else None
    eligible = [row for row in rows if row['probability'] is not None]
    invalid = len(rows)-len(eligible)
    losses = [(row['probability']-row['endpoint'])**2 for row in eligible]
    bins = []
    calibration_total = 0.0
    for index in range(plan.calibration_bins):
        selected = [row for row in eligible if min(int(row['probability']*plan.calibration_bins),plan.calibration_bins-1) == index]
        observed = math.fsum(row['endpoint'] for row in selected)/len(selected) if selected else None
        predicted = math.fsum(row['probability'] for row in selected)/len(selected) if selected else None
        if selected:
            calibration_total += len(selected)*abs(observed-predicted)
        bins.append({'index': index, 'count': len(selected), 'observed_fraction': observed, 'mean_probability': predicted})
    summary = {'total': len(rows), 'valid': len(eligible), 'invalid': invalid,
        'abstained': sum(row['state'] == 'abstained' for row in rows), 'positives': counts['positives'], 'negatives': counts['negatives'],
        'sensitivity': counts['true_positive']/counts['positives'] if counts['positives'] else None,
        'specificity': counts['true_negative']/counts['negatives'] if counts['negatives'] else None,
        'brier': (math.fsum(losses)+invalid)/len(rows) if rows else None, 'calibration_error': (calibration_total+invalid)/len(rows) if rows else None,
        'sensitivity_interval': interval(sensitivity_draws), 'specificity_interval': interval(specificity_draws)}
    predicted_positive = counts['true_positive']+counts['classified_false_positive']
    predicted_negative = counts['true_negative']+counts['classified_false_negative']
    detail = {'confusion': counts, 'calibration_bins': bins,
        'eligible_only_brier': math.fsum(losses)/len(eligible) if eligible else None,
        'eligible_only_calibration_error': calibration_total/len(eligible) if eligible else None,
        'invalid_rate': invalid/len(rows) if rows else None, 'abstention_rate': summary['abstained']/len(rows) if rows else None,
        'participants': participant_count,
        'classification_rate_labels': ['sensitivity','specificity'] if plan.comparator_kind == 'accepted_reference_standard' else ['positive_percent_agreement','negative_percent_agreement'],
        'predictive_values': {'positive_predictive_value': counts['true_positive']/predicted_positive if predicted_positive else None,
            'negative_predictive_value': counts['true_negative']/predicted_negative if predicted_negative else None,
            'positive_interval': interval(ppv_draws), 'negative_interval': interval(npv_draws),
            'defined_positive_draws': len(ppv_draws), 'defined_negative_draws': len(npv_draws),
            'classified_positive_denominator': predicted_positive, 'classified_negative_denominator': predicted_negative,
            'observed_endpoint_prevalence': counts['positives']/len(rows) if rows else None,
            'decision_coverage': (predicted_positive+predicted_negative)/len(rows) if rows else None,
            'probability_coverage': len(eligible)/len(rows) if rows else None,
            'qualification': 'conditional_on_classification_and_observed_locked_cohort_prevalence_not_target_population'},
        'interval_method': 'participant_cluster_percentile_bootstrap_v1', 'confidence_level': plan.confidence_level,
        'draws': plan.bootstrap_replicates, 'defined_sensitivity_draws': len(sensitivity_draws), 'defined_specificity_draws': len(specificity_draws),
        'undefined_draw_handling': 'omit_only_undefined_ratio_and_report_count',
        'score_denominator': 'all_rows_invalid_score_penalty_one_abstentions_keep_probability',
        'classification_denominator': 'all_endpoint_positive_or_negative_rows_invalid_and_abstention_count_as_failure',
        'reason_counts': dict(sorted(Counter(reason for row in rows for reason in row['reason_codes']).items()))}
    detail['unestimable_reasons'] = (['EMPTY_PRESPECIFIED_STRATUM'] if not rows else []) + (['INSUFFICIENT_PARTICIPANTS_FOR_CLUSTER_INTERVAL'] if participant_count < 2 else [])
    if not counts['positives']:detail['unestimable_reasons'].append('NO_ENDPOINT_POSITIVES')
    if not counts['negatives']:detail['unestimable_reasons'].append('NO_ENDPOINT_NEGATIVES')
    if summary['sensitivity_interval'] is None or summary['specificity_interval'] is None:
        detail['unestimable_reasons'].append('INSUFFICIENT_DEFINED_CLASSIFICATION_BOOTSTRAP_DRAWS')
    return summary, detail


def subgroup_report(prediction_sets, plan, cohort):
    result = {}
    for dimension in STRATA:
        result[dimension] = {}
        for category in plan.strata[dimension]:
            result[dimension][category] = {}
            for variant,rows in prediction_sets.items():
                selected = [row for row in rows if row['strata'][dimension] == category]
                summary, detail = metrics(selected,plan,cohort+':'+dimension+':'+category,allow_unestimable=True)
                result[dimension][category][variant] = {'session_ids': [row['session_id'] for row in selected], 'metrics': summary, 'details': detail}
    return result


def paired_comparisons(prediction_sets, plan, cohort):
    """Paired all-session score differences using identical cluster draws."""
    if plan.cardiac_timing_policy is not None:
        return {}
    combined = prediction_sets['combined']
    tail = (1-plan.confidence_level)/2
    results = {}
    for name in ('chemical_only','app_only','ecg_removed'):
        reference = prediction_sets[name]
        if [row['session_id'] for row in reference] != [row['session_id'] for row in combined]:
            raise InvalidEvidence('Ablations changed the locked evaluation rows')
        differences = []
        for left,right in zip(combined,reference):
            loss = lambda row: 1.0 if row['probability'] is None else (row['probability']-row['endpoint'])**2
            differences.append((left['participant_ref'],loss(left)-loss(right)))
        draws = []
        for weights in cluster_draws(combined,plan,cohort):
            total = sum(weights[participant] for participant,_ in differences)
            draws.append(math.fsum(weights[participant]*difference for participant,difference in differences)/total)
        results['combined_minus_'+name] = {'failure_penalized_brier_difference': math.fsum(value for _,value in differences)/len(differences),
            'interval': [quantile(draws,tail),quantile(draws,1-tail)], 'confidence_level': plan.confidence_level,
            'method': 'paired_participant_cluster_percentile_bootstrap_v1', 'negative_favors_combined': True,
            'total': len(differences), 'draws': plan.bootstrap_replicates}
    return results


def evaluate(dataset, plan, split, artifacts, training, evaluated_at):
    rows = validate_binding(dataset, plan, split)
    if not utc_timestamp(training.get('pipeline_locked_at', '')) <= utc_timestamp(evaluated_at) <= datetime.now(timezone.utc).timestamp():
        raise InvalidEvidence('Evaluation must follow training and cannot claim a future execution')
    # Re-fitting is deliberate: neither a mutable receipt nor unbound weights can
    # substitute for the exact prescribed training rows/algorithm.
    expected_artifacts, expected_training = train(dataset, plan, split, training['trained_at'],training['pipeline_locked_at'])
    if canonical(artifacts) != canonical(expected_artifacts) or canonical(training) != canonical(expected_training):
        raise InvalidEvidence('Artifacts or training receipt differ from deterministic frozen fitting')
    models = {name: Artifact.model_validate(value) for name,value in artifacts.items()}
    all_metrics, details, output_rows = {}, {}, {}
    for cohort in ('confirmatory', 'later_sessions'):
        selected = [rows[identity] for identity in split['session_ids'][cohort]]
        for variant in variants(plan):
            values = predictions(selected, models[variant], plan)
            metric, detail = metrics(values, plan, cohort)
            all_metrics.setdefault(cohort, {})[variant] = metric
            details.setdefault(cohort, {})[variant] = detail
            output_rows.setdefault(cohort, {})[variant] = values
    primary = 'cardiac_hr_only' if plan.cardiac_timing_policy is not None else 'combined'
    report_value = {'schema_version': '1.0.0', 'artifact_sha256': digest(artifacts[primary]),
        'dataset_sha256': digest(dataset.model_dump()), 'split_plan_sha256': digest(split), 'analysis_plan_sha256': digest(plan.model_dump()),
        'prespecified_at': plan.prespecified_at, 'locked_at': training['pipeline_locked_at'], 'evaluated_at': evaluated_at, 'endpoint_id': plan.endpoint_id,
        'operating_threshold': plan.operating_threshold, 'confirmatory': all_metrics['confirmatory'][primary],
        'later_sessions': all_metrics['later_sessions'][primary], 'ablations': all_metrics['confirmatory'],
        'participant_overlap': False, 'future_predictors': False}
    if plan.cardiac_timing_policy is not None:
        inventory = cardiac_evidence_manifest(dataset, plan)
        report_value.update(analysis_scope='cardiac_hr_only', cardiac_evidence={
            **{key: getattr(plan.cardiac_provenance, key) for key in ('calibration_registry_sha256',
                'calibration_scope_sha256', 'qualification_registry_sha256', 'device_registry_sha256', 'configuration_submitted_sha256')},
            'cardiac_timing_policy_sha256': digest(plan.cardiac_timing_policy.data()), 'evidence_manifest_sha256': digest(inventory)})
    report = EvaluationReport.model_validate(report_value).model_dump()
    evidence = {'schema_version': '1.0.0', 'purpose': 'offline_locked_evaluation_evidence', 'status': 'unvalidated',
        'data_kind': dataset.data_kind, 'dataset_sha256': report['dataset_sha256'], 'analysis_plan_sha256': report['analysis_plan_sha256'],
        'split_plan_sha256': report['split_plan_sha256'], 'training_sha256': digest(training), 'evaluation_report_sha256': digest(report),
        'artifact_sha256': {name: digest(value) for name,value in artifacts.items()}, 'uncertainty_policy': plan.uncertainty_policy.model_dump(),
        'all_metrics': all_metrics, 'metric_details': details, 'row_predictions': output_rows,
        'paired_ablations': {cohort: paired_comparisons(values,plan,cohort) for cohort,values in output_rows.items()},
        'subgroups': {cohort: subgroup_report(values,plan,cohort) for cohort,values in output_rows.items()},
        'comparator_kind': plan.comparator_kind, 'dataset_custody_locked_at': dataset.locked_at, 'pipeline_locked_at': training['pipeline_locked_at'],
        'matched_evaluation_session_ids': {key: split['session_ids'][key] for key in ('confirmatory','later_sessions')},
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'external_assertions': {'authorization_ref': dataset.authorization_ref, 'plan_lock_ref': plan.plan_lock_ref,
            'independent_endpoint_evidence_ref': plan.independent_endpoint_evidence_ref,
            'verified_by_tool': False, 'historical_lock_or_blinding_proven': False},
        'authority_granted': False, 'clinical_success_claimed': False}
    if plan.cardiac_timing_policy is not None:
        evidence.update(analysis_scope='cardiac_hr_only', cardiac_evidence_manifest=inventory,
            cardiac_evidence_manifest_sha256=digest(inventory),
            paired_ablations_qualification='not_applicable_to_prespecified_hr_only_analysis')
    return report, evidence


def load(path, model=None):
    if not hasattr(os,'O_NOFOLLOW'):
        raise InvalidEvidence('This platform cannot provide required no-follow input admission')
    descriptor = os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    with os.fdopen(descriptor,'rb') as opened:
        before = os.fstat(opened.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_BYTES:
            raise InvalidEvidence('Input must be a bounded regular JSON file')
        raw = opened.read(MAX_BYTES+1)
        after = os.fstat(opened.fileno())
        if (len(raw) > MAX_BYTES or len(raw) != before.st_size
            or (before.st_ino,before.st_size,before.st_mtime_ns) != (after.st_ino,after.st_size,after.st_mtime_ns)):
            raise InvalidEvidence('Input changed during bounded snapshot admission')
    value = strict_loads(raw)
    return model.model_validate(value) if model else value


def store(path, value):
    raw = canonical(value)
    if len(raw) > MAX_BYTES:
        raise InvalidEvidence('Output exceeds supported JSON size')
    descriptor = path.open('xb')
    try:
        os.fchmod(descriptor.fileno(),0o600)
        descriptor.write(raw)
    finally:
        descriptor.close()


def execution_time():
    return datetime.now(timezone.utc).isoformat(timespec='microseconds').replace('+00:00', 'Z')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['schemas', 'index', 'freeze', 'train', 'evaluate', 'verify'])
    parser.add_argument('--dataset', type=Path)
    parser.add_argument('--index', type=Path)
    parser.add_argument('--analysis', type=Path)
    parser.add_argument('--split', type=Path)
    parser.add_argument('--training-directory', type=Path)
    parser.add_argument('--evaluation-directory', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    if args.operation == 'schemas':
        if not args.output:
            raise InvalidEvidence('schemas requires a new --output directory')
        args.output.mkdir(mode=0o700,parents=False,exist_ok=False)
        models = {'dataset': Dataset, 'cohort-index': CohortIndex, 'analysis-plan': AnalysisPlan}
        for name,model in models.items():
            store(args.output/(name+'.schema.json'),model.model_json_schema())
        return {'schemas': sorted(models), 'authority_granted': False}
    if args.operation == 'index':
        if not args.dataset or not args.output:
            raise InvalidEvidence('index requires --dataset and new --output file')
        value = cohort_index(load(args.dataset, Dataset)).model_dump()
        store(args.output, value)
        return {'index_sha256': digest(value), 'outcomes_disclosed': False, 'authority_granted': False}
    if not args.analysis:
        raise InvalidEvidence('Supply the independently prespecified --analysis plan')
    plan = load(args.analysis, AnalysisPlan)
    if args.operation == 'freeze':
        if not args.index or not args.output:
            raise InvalidEvidence('freeze requires outcome-blind --index and new --output file')
        value = freeze(load(args.index, CohortIndex), plan)
        store(args.output, value)
        return {'split_sha256': digest(value), 'historical_lock_proven': False, 'authority_granted': False}
    if not args.dataset or not args.split:
        raise InvalidEvidence('Supply exact locked --dataset and frozen --split')
    dataset, split = load(args.dataset, Dataset), load(args.split)
    if args.operation == 'train':
        if not args.output:
            raise InvalidEvidence('train requires a new --output directory')
        artifacts, training = train(dataset, plan, split, execution_time())
        training['pipeline_locked_at'] = execution_time()
        args.output.mkdir(mode=0o700, parents=False, exist_ok=False)
        for name,value in artifacts.items():
            store(args.output/(name+'.artifact.json'), value)
        store(args.output/'training.json', training)
        return {'training_sha256': digest(training), 'artifacts': training['artifact_sha256'], 'status': 'unvalidated', 'authority_granted': False}
    if not args.training_directory:
        raise InvalidEvidence('Supply --training-directory containing the exact frozen artifacts and receipt')
    artifacts = {name: load(args.training_directory/(name+'.artifact.json'), Artifact).model_dump() for name in variants(plan)}
    training = load(args.training_directory/'training.json')
    if args.operation == 'evaluate':
        if not args.output:
            raise InvalidEvidence('evaluate requires a new --output directory')
        report, evidence = evaluate(dataset, plan, split, artifacts, training, execution_time())
        args.output.mkdir(mode=0o700, parents=False, exist_ok=False)
        store(args.output/'evaluation-report.json', report)
        store(args.output/'evaluation-evidence.json', evidence)
        return {'evaluation_report_sha256': digest(report), 'evidence_sha256': digest(evidence), 'status': 'unvalidated', 'authority_granted': False}
    if not args.evaluation_directory:
        raise InvalidEvidence('verify requires --evaluation-directory')
    report = load(args.evaluation_directory/'evaluation-report.json', EvaluationReport).model_dump()
    evidence = load(args.evaluation_directory/'evaluation-evidence.json')
    expected_report, expected_evidence = evaluate(dataset, plan, split, artifacts, training, report['evaluated_at'])
    if canonical(report) != canonical(expected_report) or canonical(evidence) != canonical(expected_evidence):
        raise InvalidEvidence('Evaluation bytes do not reproduce from locked inputs, plans and training')
    return {'evaluation_reproduced': True, 'status': 'unvalidated', 'authority_granted': False}


if __name__ == '__main__':
    try:
        import json
        print(json.dumps(main(), sort_keys=True))
    except (ValueError, OSError, KeyError, TypeError) as error:
        print('BLOCKED: '+(str(error) if isinstance(error,InvalidEvidence) else type(error).__name__+'; inspect protected inputs'), file=sys.stderr)
        raise SystemExit(2)
