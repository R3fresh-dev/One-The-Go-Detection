"""Compilation may be reused; every new value still receives full validation."""
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import pytest
from jsonschema.exceptions import ValidationError
import spec_validation
from otgd.config import ROOT


def test_immutable_compilation_reuse_does_not_cache_payload_acceptance(monkeypatch):
    spec_validation.compiled_validator.cache_clear()
    spec_validation.schema_registry.cache_clear()
    original = spec_validation.read_json
    reads = []

    def counted(path):
        reads.append(path)
        return original(path)

    monkeypatch.setattr(spec_validation, 'read_json', counted)
    valid = original(ROOT / 'examples/synthetic_session.json')
    spec_validation.validate_session(valid)
    first_reads = len(reads)
    assert first_reads > 0
    for _ in range(3):
        spec_validation.validate_session(deepcopy(valid))
    assert len(reads) == first_reads
    assert spec_validation.compiled_validator.cache_info().hits > 0
    invalid = deepcopy(valid)
    invalid['profile']['age_years'] = 'invalid age'
    with pytest.raises(ValidationError):
        spec_validation.validate_session(invalid)
    invalid = deepcopy(valid)
    invalid['profile']['height_cm'] = float('nan')
    with pytest.raises(ValueError, match='Nonfinite'):
        spec_validation.validate_session(invalid)
    invalid = deepcopy(valid)
    invalid['profile']['bmi'] += 10
    with pytest.raises(ValueError, match='BMI'):
        spec_validation.validate_session(invalid)
    assert len(reads) == first_reads
    spec_validation.validate_session(valid)


def test_cached_reference_validation_still_rejects_changed_nested_measurement():
    valid = spec_validation.read_json(ROOT / 'examples/synthetic_session.json')
    spec_validation.validate_session(valid)
    invalid = deepcopy(valid)
    invalid['saliva'][0]['unexpected_field'] = 'not allowed'
    with pytest.raises(ValidationError):
        spec_validation.validate_session(invalid)
    spec_validation.validate_session(valid)


def test_concurrent_cold_requests_compile_immutable_schema_once(monkeypatch):
    spec_validation.compiled_validator.cache_clear()
    spec_validation.schema_registry.cache_clear()
    original = spec_validation.Draft202012Validator.check_schema
    checked = []

    def count(document):
        checked.append(document['$id'])
        original(document)

    monkeypatch.setattr(spec_validation.Draft202012Validator, 'check_schema', count)
    value = spec_validation.read_json(ROOT / 'examples/synthetic_session.json')
    ready = Barrier(8)

    def validate(_):
        ready.wait(timeout=5)
        spec_validation.validate_schema(deepcopy(value), 'session.schema.json')

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(validate, range(8)))
    assert len(checked) == 1
