"""Independent server checks of uncalibrated native structured evidence; no physical trust claim."""

import re
from datetime import datetime
from math import isclose, isfinite

from .canonical import digest, strict_loads
from .config import ROOT
from .errors import Problem

CONFIG = strict_loads(
    (
        ROOT
        / "openspec/changes/production-mobile-platform/fixtures/reaction-task-config-v1.json"
    ).read_text()
)
CONFIG_SHA = digest(CONFIG)


def schedule(seed):
    state = seed

    def next_int():
        nonlocal state
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        return state

    def shuffled(n):
        values = ["left"] * n[0] + ["right"] * n[1] + ["no_go"] * n[2]
        for i in range(len(values) - 1, 0, -1):
            j = next_int() % (i + 1)
            values[i], values[j] = values[j], values[i]
        return values

    values = shuffled([2, 2, 2]) + shuffled([24, 24, 12])
    onset = 2000
    trials = []
    for i, stim in enumerate(values):
        interval = 1500 + next_int() % 401
        trials.append(
            {
                "index": i,
                "phase": "practice" if i < 6 else "scored",
                "stimulus": stim,
                "planned_onset_ms": onset,
                "onset_interval_ms": interval,
            }
        )
        onset += interval
    return {
        "schema_version": "1.0.0",
        "configuration_sha256": CONFIG_SHA,
        "seed": seed,
        "trials": trials,
    }


def exact(obj, keys):
    if not isinstance(obj, dict) or set(obj) != set(keys.split()):
        raise Problem(422, "NATIVE_EVIDENCE_FIELDS")


def number(x):
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not isfinite(x):
        raise Problem(422, "NATIVE_EVIDENCE_NUMBER")


def integer(x, low=0, high=9007199254740991):
    if type(x) is not int or not low <= x <= high:
        raise Problem(422, "NATIVE_EVIDENCE_NUMBER")


def bounded_text(x, limit=256):
    if not isinstance(x, str) or not 1 <= len(x) <= limit:
        raise Problem(422, "NATIVE_EVIDENCE_TEXT")


def utc(x):
    bounded_text(x, 64)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", x):
        raise Problem(422, "NATIVE_EVIDENCE_TIME")
    return datetime.fromisoformat(x)


def quantile(data, p):
    if not data:
        return None
    data = sorted(data)
    index = (len(data) - 1) * p
    lo = int(index)
    return data[lo] + (data[min(lo + 1, len(data) - 1)] - data[lo]) * (index - lo)


def validate_native(v, projection):
    exact(
        v,
        "schemaVersion taskVersion implementationVersion extractorVersion status source platform runId workspaceEpoch seed configurationId configurationSha256 scheduleSha256 startedAt endedAt nativeStartMs nativeEndMs durationMs trialEvents inputEvents counts features qualityFlags timing",
    )
    for key in ("runId", "workspaceEpoch"):
        bounded_text(v[key], 128)
    if not isinstance(v["trialEvents"], list) or not isinstance(v["inputEvents"], list):
        raise Problem(422, "NATIVE_EVIDENCE_FIELDS")
    if not isinstance(v["qualityFlags"], list) or not 1 <= len(v["qualityFlags"]) <= 64:
        raise Problem(422, "NATIVE_EVIDENCE_FIELDS")
    for flag in v["qualityFlags"]:
        bounded_text(flag, 128)
    for key in ("nativeStartMs", "nativeEndMs", "durationMs"):
        number(v[key])
    if (
        v["nativeStartMs"] < 0
        or v["durationMs"] < 0
        or not isclose(
            v["nativeEndMs"] - v["nativeStartMs"],
            v["durationMs"],
            abs_tol=0.01,
            rel_tol=0,
        )
    ):
        raise Problem(422, "NATIVE_EVIDENCE_TIME")
    if (
        abs(
            (utc(v["endedAt"]) - utc(v["startedAt"])).total_seconds() * 1000
            - v["durationMs"]
        )
        > 2
    ):
        raise Problem(422, "NATIVE_EVIDENCE_TIME")
    if (
        v["schemaVersion"],
        v["taskVersion"],
        v["implementationVersion"],
        v["extractorVersion"],
        v["source"],
    ) != (
        "1.0.0",
        "choice_inhibit_v0",
        "1.0.0",
        "choice_inhibit_features_1",
        "native_task",
    ):
        raise Problem(422, "NATIVE_EVIDENCE_VERSION")
    if (
        v["configurationId"] != CONFIG["configuration_id"]
        or v["configurationSha256"] != CONFIG_SHA
        or projection["config_sha256"] != CONFIG_SHA
    ):
        raise Problem(422, "NATIVE_CONFIGURATION_MISMATCH")
    if type(v["seed"]) is not int or not 0 <= v["seed"] <= 0xFFFFFFFF:
        raise Problem(422, "NATIVE_SEED_INVALID")
    expected = schedule(v["seed"])
    if (
        v["scheduleSha256"] != digest(expected)
        or len(v["trialEvents"]) != 66
        or len(v["inputEvents"]) > 1024
    ):
        raise Problem(422, "NATIVE_SCHEDULE_MISMATCH")
    if (
        v["status"] not in ("valid", "invalid")
        or v["platform"] not in ("android", "ios")
        or v["status"] != projection["status"]
        or projection["source"] != "prototype_sensor"
        or v["runId"] != projection["task_id"]
        or v["startedAt"] != projection["started_at"]
        or v["endedAt"] != projection["ended_at"]
    ):
        raise Problem(422, "NATIVE_PROJECTION_MISMATCH")
    timing = v["timing"]
    exact(
        timing,
        "clockDomain inputTimestampMethod inputTimestampResolutionMs presentationEvidenceMethod calibrationStatus physicalOnsetVerified modelEligible simulator deviceModel osVersion nativeBuild viewWidthPoints viewHeightPoints viewWidthPixels viewHeightPixels pixelDensity orientation fontFamily textScale nominalRefreshHz maxObservedFrameGapMs maxObservedFrameDispatchMs maxObservedInputDispatchMs terminalCutoffMs finalDrainMs overflowTriggerCount utcAnchorMethod observedEndedAt observedWallClockDeltaMs physicalLuminance",
    )
    if (
        timing["calibrationStatus"] != "uncalibrated"
        or timing["modelEligible"] is not False
        or timing["physicalOnsetVerified"] is not False
        or timing["physicalLuminance"] != "unmeasured"
        or timing["finalDrainMs"] != 100
    ):
        raise Problem(422, "NATIVE_UNSUPPORTED_QUALIFICATION")
    for key in ("deviceModel", "osVersion", "nativeBuild", "fontFamily"):
        bounded_text(timing[key])
    utc(timing["observedEndedAt"])
    if (
        type(timing["simulator"]) is not bool
        or timing["orientation"] != "portrait"
        or timing["textScale"] != 1
        or timing["utcAnchorMethod"] != "start_utc_plus_monotonic_elapsed"
    ):
        raise Problem(422, "NATIVE_EVIDENCE_FIELDS")
    expected_clock = "android_uptime" if v["platform"] == "android" else "ios_uptime"
    expected_presentation = (
        "choreographer_frame_time_nanos"
        if v["platform"] == "android"
        else "cadisplaylink_target_timestamp"
    )
    input_methods = (
        ("motion_event_uptime_ms", "motion_event_uptime_nanos")
        if v["platform"] == "android"
        else ("uitouch_timestamp",)
    )
    if (
        timing["clockDomain"] != expected_clock
        or timing["presentationEvidenceMethod"] != expected_presentation
        or timing["inputTimestampMethod"] not in input_methods
    ):
        raise Problem(422, "NATIVE_TIMING_METHOD")
    for key in ("inputTimestampResolutionMs", "terminalCutoffMs"):
        if timing[key] is not None:
            number(timing[key])
    if (
        timing["inputTimestampResolutionMs"] is not None
        and timing["inputTimestampResolutionMs"] <= 0
    ):
        raise Problem(422, "NATIVE_EVIDENCE_NUMBER")
    for key in (
        "viewWidthPoints",
        "viewHeightPoints",
        "viewWidthPixels",
        "viewHeightPixels",
        "pixelDensity",
        "nominalRefreshHz",
        "maxObservedFrameGapMs",
        "maxObservedFrameDispatchMs",
        "maxObservedInputDispatchMs",
        "observedWallClockDeltaMs",
    ):
        number(timing[key])
    integer(timing["overflowTriggerCount"])
    if any(
        timing[key] < 0
        for key in (
            "viewWidthPoints",
            "viewHeightPoints",
            "viewWidthPixels",
            "viewHeightPixels",
            "pixelDensity",
            "nominalRefreshHz",
        )
    ):
        raise Problem(422, "NATIVE_GEOMETRY")
    if v["status"] == "valid" and (
        timing["viewWidthPoints"] < 240
        or timing["viewHeightPoints"] < 400
        or timing["pixelDensity"] <= 0
        or timing["overflowTriggerCount"] != 0
    ):
        raise Problem(422, "NATIVE_GEOMETRY")
    for i, t in enumerate(v["trialEvents"]):
        exact(
            t,
            "index phase stimulus plannedOnsetMs onsetIntervalMs presented frameTimestampMs callbackTimestampMs onsetMs onsetLatenessMs outcome selectedInputSequence responseTimeMs correctGoRtMs",
        )
        e = expected["trials"][i]
        if [
            t[k]
            for k in ("index", "phase", "stimulus", "plannedOnsetMs", "onsetIntervalMs")
        ] != [
            e[k]
            for k in (
                "index",
                "phase",
                "stimulus",
                "planned_onset_ms",
                "onset_interval_ms",
            )
        ]:
            raise Problem(422, "NATIVE_SCHEDULE_MISMATCH")
        integer(t["index"], 0, 65)
        if t["outcome"] not in (
            "correct",
            "wrong_choice",
            "omission",
            "commission",
            "correct_withhold",
            "unresolved",
        ):
            raise Problem(422, "NATIVE_SCORE_MISMATCH")
        if t["selectedInputSequence"] is not None:
            integer(t["selectedInputSequence"])
        if type(t["presented"]) is not bool:
            raise Problem(422, "NATIVE_EVIDENCE_NUMBER")
        for field in (
            "frameTimestampMs",
            "callbackTimestampMs",
            "onsetMs",
            "onsetLatenessMs",
            "responseTimeMs",
            "correctGoRtMs",
        ):
            if t[field] is not None:
                number(t[field])
    seq = set()
    for e in v["inputEvents"]:
        exact(
            e,
            "nativeTimestampMs dispatchTimestampMs dispatchDelayMs target pointerId nativeSequence inputKind disposition trialIndex anticipatoryForTrialIndex",
        )
        for f in (
            "nativeTimestampMs",
            "dispatchTimestampMs",
            "dispatchDelayMs",
            "pointerId",
            "nativeSequence",
        ):
            number(e[f])
        if not isclose(
            e["dispatchDelayMs"],
            e["dispatchTimestampMs"] - e["nativeTimestampMs"],
            abs_tol=1e-6,
            rel_tol=0,
        ):
            raise Problem(422, "NATIVE_TIMING_FAULT")
        if (
            e["nativeSequence"] in seq
            or e["target"] not in ("left", "right", "outside")
            or e["inputKind"] not in ("direct_touch", "unsupported")
        ):
            raise Problem(422, "NATIVE_INPUT_INVALID")
        integer(e["nativeSequence"])
        integer(e["pointerId"])
        for key in ("trialIndex", "anticipatoryForTrialIndex"):
            if e[key] is not None:
                integer(e[key], 0, 65)
        if e["disposition"] not in (
            "selected",
            "additional_response",
            "outside",
            "anticipatory",
            "late",
            "unsupported",
            "timing_fault",
        ):
            raise Problem(422, "NATIVE_INPUT_INVALID")
        seq.add(e["nativeSequence"])
    exact(
        v["counts"],
        "presentedPractice presentedScored presentedGo presentedNoGo completedScored correctGo omissions wrongGo noGoErrors correctWithholds",
    )
    for count in v["counts"].values():
        integer(count, 0, 66)
    for key, native_key in {
        "practice_trials": "presentedPractice",
        "scored_trials": "presentedScored",
        "go_trials": "presentedGo",
        "no_go_trials": "presentedNoGo",
        "valid_correct_go_trials": "correctGo",
    }.items():
        if projection[key] != v["counts"][native_key]:
            raise Problem(422, "NATIVE_COUNT_MISMATCH")
    scored = [t for t in v["trialEvents"] if t["phase"] == "scored"]
    count_expected = {
        "presentedPractice": sum(
            t["presented"] for t in v["trialEvents"] if t["phase"] == "practice"
        ),
        "presentedScored": sum(t["presented"] for t in scored),
        "presentedGo": sum(t["presented"] and t["stimulus"] != "no_go" for t in scored),
        "presentedNoGo": sum(
            t["presented"] and t["stimulus"] == "no_go" for t in scored
        ),
        # A tap can resolve an outcome before the response window finishes.
        # Native Kotlin/Swift count completed windows, including at equality,
        # so cancellation after a tap must retain the distinct terminal counts.
        "completedScored": sum(
            t["presented"]
            and t["onsetMs"] is not None
            and v["durationMs"] >= t["onsetMs"] + 1000
            for t in scored
        ),
        "correctGo": sum(t["outcome"] == "correct" for t in scored),
        "omissions": sum(t["outcome"] == "omission" for t in scored),
        "wrongGo": sum(t["outcome"] == "wrong_choice" for t in scored),
        "noGoErrors": sum(t["outcome"] == "commission" for t in scored),
        "correctWithholds": sum(t["outcome"] == "correct_withhold" for t in scored),
    }
    if v["counts"] != count_expected:
        raise Problem(422, "NATIVE_COUNT_MISMATCH")
    if v["status"] == "invalid":
        if (
            v["features"] is not None
            or any(x is not None for x in projection["features"].values())
            or not v["qualityFlags"]
        ):
            raise Problem(422, "INVALID_TASK_FEATURES")
        return
    # Only complete valid runs have the fixed final drain cutoff. Interrupted
    # ledgers may retain their fault-triggering event and partial/null timing.
    last_onset = v["trialEvents"][-1]["onsetMs"]
    cutoff = timing["terminalCutoffMs"]
    expected_cutoff = (
        None
        if last_onset is None
        else last_onset
        + CONFIG["timing"]["response_window_ms"]
        + CONFIG["timing"]["final_event_drain_ms"]
    )
    if (
        last_onset is None
        or cutoff is None
        or not isclose(
            cutoff,
            expected_cutoff,
            abs_tol=1e-6,
            rel_tol=0,
        )
        or any(e["dispatchTimestampMs"] >= expected_cutoff for e in v["inputEvents"])
    ):
        raise Problem(422, "NATIVE_TIMING_FAULT")
    if any(
        timing[k] > 100
        for k in (
            "maxObservedFrameGapMs",
            "maxObservedFrameDispatchMs",
            "maxObservedInputDispatchMs",
        )
    ):
        raise Problem(422, "NATIVE_TIMING_FAULT")
    correct = []
    omissions = wrong = commissions = 0
    inputs = sorted(
        v["inputEvents"],
        key=lambda e: (
            e["nativeTimestampMs"],
            ["left", "right", "outside"].index(e["target"]),
            e["pointerId"],
            e["nativeSequence"],
        ),
    )
    if any(
        e["inputKind"] != "direct_touch" or not 0 <= e["dispatchDelayMs"] <= 100
        for e in inputs
    ):
        raise Problem(422, "NATIVE_TIMING_FAULT")
    for t in v["trialEvents"]:
        if (
            not t["presented"]
            or t["onsetMs"] is None
            or not 0 <= t["onsetLatenessMs"] <= 100
        ):
            raise Problem(422, "NATIVE_TIMING_FAULT")
        eligible = [
            e
            for e in inputs
            if e["target"] != "outside"
            and t["onsetMs"] <= e["nativeTimestampMs"] < t["onsetMs"] + 1000
        ]
        first = eligible[0] if eligible else None
        outcome = (
            ("commission" if first else "correct_withhold")
            if t["stimulus"] == "no_go"
            else (
                "omission"
                if first is None
                else ("correct" if first["target"] == t["stimulus"] else "wrong_choice")
            )
        )
        response = None if first is None else first["nativeTimestampMs"] - t["onsetMs"]
        correct_rt = response if outcome == "correct" else None
        for expected_time, actual_time in (
            (response, t["responseTimeMs"]),
            (correct_rt, t["correctGoRtMs"]),
        ):
            if (
                (expected_time is None) != (actual_time is None)
                or expected_time is not None
                and not isclose(expected_time, actual_time, abs_tol=1e-6, rel_tol=0)
            ):
                raise Problem(422, "NATIVE_SCORE_MISMATCH")
        if t["outcome"] != outcome or t["selectedInputSequence"] != (
            first["nativeSequence"] if first else None
        ):
            raise Problem(422, "NATIVE_SCORE_MISMATCH")
        if t["phase"] == "scored":
            if outcome == "correct":
                correct.append(first["nativeTimestampMs"] - t["onsetMs"])
            elif outcome == "omission":
                omissions += 1
            elif outcome == "wrong_choice":
                wrong += 1
            elif outcome == "commission":
                commissions += 1
    values = {
        "median_rt_ms": quantile(correct, 0.5),
        "iqr_rt_ms": None
        if not correct
        else quantile(correct, 0.75) - quantile(correct, 0.25),
        "p90_rt_ms": quantile(correct, 0.9),
        "omission_rate": omissions / 48,
        "wrong_go_rate": wrong / 48,
        "no_go_error_rate": commissions / 12,
    }
    native_names = [
        "medianRtMs",
        "iqrRtMs",
        "p90RtMs",
        "omissionRate",
        "wrongGoRate",
        "noGoErrorRate",
    ]
    exact(v["features"], " ".join(native_names))
    for (k, x), nk in zip(values.items(), native_names):
        for actual in (projection["features"][k], v["features"][nk]):
            if actual is not None:
                number(actual)
            if (
                (x is None) != (actual is None)
                or x is not None
                and not isclose(x, actual, abs_tol=1e-6, rel_tol=0)
            ):
                raise Problem(422, "NATIVE_FEATURE_MISMATCH")
    if projection["valid_correct_go_trials"] != len(correct):
        raise Problem(422, "NATIVE_COUNT_MISMATCH")
