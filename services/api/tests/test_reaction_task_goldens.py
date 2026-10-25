"""Literal task cases admitted by the actual independent 66-trial validator.

These are fictional software records, not native execution or qualified timing.
"""

from copy import deepcopy
from datetime import datetime, timedelta

import pytest
from otgd.canonical import digest, strict_loads
from otgd.config import ROOT
from otgd.errors import Problem
from otgd.native_evidence import validate_native

from .test_cross_language import native_fixture

GOLDENS = strict_loads(
    (ROOT / "apps/mobile/modules/reaction-task/fixtures/golden.json").read_text()
)
VECTORS = {item["case_id"]: item for item in GOLDENS["trial_scoring_vectors"]}
CASES = [
    "first_response_wrong_then_correct",
    "same_time_opposing_targets_left_wins",
    "same_time_opposing_targets_reverse_delivery_left_wins",
    "same_time_same_target_lower_pointer_wins_before_sequence",
    "same_time_same_target_pointer_native_sequence_breaks_tie",
    "last_trial_event_within_dispatch_drain",
    "retained_drain_result_ignores_cutoff_and_later_arrivals",
    "arrival_at_terminal_cutoff_excluded",
]


def literal_case(case_id):
    """Translate one literal relative-time case into the unchanged full schedule.

    All other trials retain their literal baseline 300ms correct responses. Only
    the selected trial, sequence offsets and corresponding factual counts/rates
    change; expected quantiles stay 300/0/300 with at least 47 baseline RTs.
    """
    vector = VECTORS[case_id]
    expected = vector["expected"]
    raw, projection = native_fixture()
    trial = (
        raw["trialEvents"][-1]
        if vector.get("is_final_trial")
        else next(
            t
            for t in raw["trialEvents"]
            if t["phase"] == "scored" and t["stimulus"] == "left"
        )
    )
    assert trial["stimulus"] == vector["stimulus"] == "left"
    original_sequence = trial["selectedInputSequence"]
    retained = [
        item
        for item in vector["inputs"]
        if item["dispatch_timestamp_ms"]
        < vector.get("terminal_cutoff_ms", float("inf"))
    ]
    shift = len(retained) - 1
    raw["inputEvents"] = [
        item for item in raw["inputEvents"] if item["trialIndex"] != trial["index"]
    ]
    for item in raw["inputEvents"]:
        if item["nativeSequence"] > original_sequence:
            item["nativeSequence"] += shift
    for item in raw["trialEvents"]:
        if (
            item["selectedInputSequence"] is not None
            and item["selectedInputSequence"] > original_sequence
        ):
            item["selectedInputSequence"] += shift
    for item in retained:
        native = trial["onsetMs"] + item["native_timestamp_ms"] - vector["onset_ms"]
        dispatch = trial["onsetMs"] + item["dispatch_timestamp_ms"] - vector["onset_ms"]
        raw["inputEvents"].append(
            {
                "nativeTimestampMs": native,
                "dispatchTimestampMs": dispatch,
                "dispatchDelayMs": dispatch - native,
                "target": item["target"],
                "pointerId": item["pointer_id"],
                "nativeSequence": original_sequence + item["native_sequence"],
                "inputKind": item["input_kind"],
                "disposition": "selected"
                if item["native_sequence"] == expected["selected_input_sequence"]
                else "additional_response",
                "trialIndex": trial["index"],
                "anticipatoryForTrialIndex": None,
            }
        )
    # The retained native ledger follows the pinned comparator, not receipt order.
    raw["inputEvents"].sort(
        key=lambda e: (
            e["nativeTimestampMs"],
            ["left", "right", "outside"].index(e["target"]),
            e["pointerId"],
            e["nativeSequence"],
        )
    )
    trial.update(
        outcome=expected["trial_outcome"],
        selectedInputSequence=None
        if expected["selected_input_sequence"] is None
        else original_sequence + expected["selected_input_sequence"],
        responseTimeMs=expected["response_time_ms"],
        correctGoRtMs=expected["correct_go_rt_ms"],
    )
    if expected["trial_outcome"] != "correct":
        raw["counts"]["correctGo"] = projection["valid_correct_go_trials"] = 47
        count, rate, projected = (
            ("wrongGo", "wrongGoRate", "wrong_go_rate")
            if expected["trial_outcome"] == "wrong_choice"
            else ("omissions", "omissionRate", "omission_rate")
        )
        raw["counts"][count] = 1
        raw["features"][rate] = projection["features"][projected] = 1 / 48
    raw["timing"]["maxObservedInputDispatchMs"] = max(
        e["dispatchDelayMs"] for e in raw["inputEvents"]
    )
    return raw, projection, trial, original_sequence


@pytest.mark.parametrize("case_id", CASES)
def test_literal_task_cases_through_actual_reference_validator(case_id):
    raw, projection, trial, sequence = literal_case(case_id)
    before = deepcopy(raw)
    payload_sha256 = digest(raw)
    validate_native(raw, projection)
    assert raw == before and digest(raw) == payload_sha256
    assert len(raw["trialEvents"]) == 66
    expected = VECTORS[case_id]["expected"]
    ledger = [e for e in raw["inputEvents"] if e["trialIndex"] == trial["index"]]
    assert len(ledger) == expected.get("retained_input_count", 2)
    if "sorted_native_sequences" in expected:
        assert [e["nativeSequence"] - sequence for e in ledger] == expected[
            "sorted_native_sequences"
        ]
    if "retained_inputs" in expected:
        for actual, literal in zip(ledger, expected["retained_inputs"]):
            assert (
                actual["nativeTimestampMs"] - trial["onsetMs"]
                == literal["native_timestamp_ms"] - VECTORS[case_id]["onset_ms"]
            )
            assert (
                actual["dispatchTimestampMs"] - trial["onsetMs"]
                == literal["dispatch_timestamp_ms"] - VECTORS[case_id]["onset_ms"]
            )
            assert actual["dispatchDelayMs"] == literal["dispatch_delay_ms"]
            assert actual["target"] == literal["target"]
            assert actual["disposition"] == literal["disposition"]
    # Mutate the claimed selected sequence while preserving a fresh payload hash.
    if ledger:
        trial["selectedInputSequence"] = 999
        assert digest(raw) != payload_sha256
        with pytest.raises(Problem) as exc:
            validate_native(raw, projection)
        assert exc.value.code == "NATIVE_SCORE_MISMATCH"


def test_wrong_then_correct_preserves_both_touches_without_correct_go_rt():
    raw, projection, trial, _ = literal_case("first_response_wrong_then_correct")
    validate_native(raw, projection)
    ledger = [e for e in raw["inputEvents"] if e["trialIndex"] == trial["index"]]
    assert len(raw["inputEvents"]) == 53 and len(ledger) == 2
    assert [e["target"] for e in ledger] == ["right", "left"]
    assert [e["disposition"] for e in ledger] == ["selected", "additional_response"]
    assert trial["outcome"] == "wrong_choice" and trial["correctGoRtMs"] is None
    assert raw["counts"]["correctGo"] == 47 and raw["counts"]["wrongGo"] == 1


def test_reference_rejects_forged_retained_dispatch_delay():
    raw, projection, trial, _ = literal_case("last_trial_event_within_dispatch_drain")
    validate_native(raw, projection)
    event = next(e for e in raw["inputEvents"] if e["trialIndex"] == trial["index"])
    assert event["dispatchDelayMs"] == 80 and trial["responseTimeMs"] == 999
    before = digest(raw)
    event["dispatchDelayMs"] = 79
    assert digest(raw) != before
    with pytest.raises(Problem) as exc:
        validate_native(raw, projection)
    assert exc.value.code == "NATIVE_TIMING_FAULT"


@pytest.mark.parametrize("after_cutoff", [0, 1])
def test_reference_rejects_retained_handler_at_or_after_cutoff(after_cutoff):
    raw, projection, _, _ = literal_case("last_trial_event_within_dispatch_drain")
    validate_native(raw, projection)
    cutoff = raw["timing"]["terminalCutoffMs"]
    raw["inputEvents"].append(
        {
            "nativeTimestampMs": cutoff - 80 + after_cutoff,
            "dispatchTimestampMs": cutoff + after_cutoff,
            "dispatchDelayMs": 80,
            "target": "outside",
            "pointerId": 1,
            "nativeSequence": 52,
            "inputKind": "direct_touch",
            "disposition": "outside",
            "trialIndex": None,
            "anticipatoryForTrialIndex": None,
        }
    )
    assert len(digest(raw)) == 64
    with pytest.raises(Problem) as exc:
        validate_native(raw, projection)
    assert exc.value.code == "NATIVE_TIMING_FAULT"


@pytest.mark.parametrize("cutoff_change", [None, 1])
def test_reference_cannot_move_or_omit_the_pinned_valid_cutoff(cutoff_change):
    raw, projection, _, _ = literal_case("last_trial_event_within_dispatch_drain")
    validate_native(raw, projection)
    raw["timing"]["terminalCutoffMs"] = (
        None
        if cutoff_change is None
        else raw["timing"]["terminalCutoffMs"] + cutoff_change
    )
    with pytest.raises(Problem) as exc:
        validate_native(raw, projection)
    assert exc.value.code == "NATIVE_TIMING_FAULT"


def test_truthful_exact_dispatch_budget_remains_valid_before_cutoff():
    raw, projection, trial, _ = literal_case("last_trial_event_within_dispatch_drain")
    event = next(e for e in raw["inputEvents"] if e["trialIndex"] == trial["index"])
    event["dispatchTimestampMs"] += 20
    event["dispatchDelayMs"] = raw["timing"]["maxObservedInputDispatchMs"] = 100
    assert event["dispatchTimestampMs"] == raw["timing"]["terminalCutoffMs"] - 1
    assert trial["responseTimeMs"] == 999
    validate_native(raw, projection)


@pytest.mark.parametrize("delay", [-1, 101])
@pytest.mark.parametrize("cutoff_kind", ["planned_final", "partial_end", "null"])
def test_invalid_ledger_retains_truthful_fault_and_partial_cutoff(delay, cutoff_kind):
    raw, projection = native_fixture()
    trial = raw["trialEvents"][-1]
    event = raw["inputEvents"][-1]
    event["dispatchTimestampMs"] = event["nativeTimestampMs"] + delay
    event["dispatchDelayMs"] = delay
    event["disposition"] = "timing_fault"
    trial.update(
        outcome="unresolved",
        selectedInputSequence=None,
        responseTimeMs=None,
        correctGoRtMs=None,
    )
    raw["status"] = projection["status"] = "invalid"
    raw["features"] = None
    projection["features"] = {key: None for key in projection["features"]}
    raw["counts"]["correctGo"] = projection["valid_correct_go_trials"] = 47
    raw["counts"]["completedScored"] = 59
    raw["durationMs"] = event["dispatchTimestampMs"]
    raw["nativeEndMs"] = raw["nativeStartMs"] + raw["durationMs"]
    ended = datetime.fromisoformat(raw["startedAt"]) + timedelta(
        milliseconds=raw["durationMs"]
    )
    raw["endedAt"] = projection["ended_at"] = ended.isoformat(
        timespec="milliseconds"
    ).replace("+00:00", "Z")
    raw["timing"]["observedEndedAt"] = raw["endedAt"]
    raw["timing"]["maxObservedInputDispatchMs"] = max(5, delay)
    raw["qualityFlags"].append(
        "NATIVE_CLOCK_INCONSISTENCY" if delay < 0 else "INPUT_DISPATCH_DELAY_EXCEEDED"
    )
    if cutoff_kind != "planned_final":
        raw["timing"]["terminalCutoffMs"] = (
            raw["durationMs"] if cutoff_kind == "partial_end" else None
        )
    before = deepcopy(raw)
    validate_native(raw, projection)
    assert raw == before and event in raw["inputEvents"]
    assert raw["features"] is None


@pytest.mark.parametrize("delta,accepted", [(0.0000005, True), (0.000002, False)])
def test_reference_preserves_fixed_dispatch_arithmetic_tolerance(delta, accepted):
    raw, projection, trial, _ = literal_case("last_trial_event_within_dispatch_drain")
    event = next(e for e in raw["inputEvents"] if e["trialIndex"] == trial["index"])
    event["dispatchDelayMs"] += delta
    if accepted:
        validate_native(raw, projection)
    else:
        with pytest.raises(Problem) as exc:
            validate_native(raw, projection)
        assert exc.value.code == "NATIVE_TIMING_FAULT"


def test_drain_handler_just_before_cutoff_is_retained_but_metadata_cannot_extend_it():
    raw, projection, _, _ = literal_case("last_trial_event_within_dispatch_drain")
    cutoff = raw["timing"]["terminalCutoffMs"]
    event = {
        "nativeTimestampMs": cutoff - 80 - 0.000001,
        "dispatchTimestampMs": cutoff - 0.000001,
        "dispatchDelayMs": 80,
        "target": "outside",
        "pointerId": 1,
        "nativeSequence": 52,
        "inputKind": "direct_touch",
        "disposition": "outside",
        "trialIndex": None,
        "anticipatoryForTrialIndex": None,
    }
    raw["inputEvents"].append(event)
    validate_native(raw, projection)
    raw["timing"]["terminalCutoffMs"] += 0.0000005
    event["nativeTimestampMs"] = cutoff - 80
    event["dispatchTimestampMs"] = cutoff
    with pytest.raises(Problem) as exc:
        validate_native(raw, projection)
    assert exc.value.code == "NATIVE_TIMING_FAULT"
