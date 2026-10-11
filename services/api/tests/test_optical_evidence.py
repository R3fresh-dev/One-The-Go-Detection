"""Independent literal native optical arithmetic; fixtures are fictional pixels only."""

from copy import deepcopy
from pathlib import Path
import struct
import hashlib

import pytest

from otgd import optical_evidence as optical
from otgd.canonical import digest, strict_loads
from otgd.errors import Problem
from otgd.operator_governance import ExecutableOpticalMaterial

FIXTURE = strict_loads(
    (
        Path(__file__).parents[3]
        / "apps/mobile/modules/eye-capture/fixtures/eye-golden-v1.json"
    ).read_text()
)


def fixture(*, display=False, scale=False):
    material = deepcopy(FIXTURE["configuration"])
    if display:
        material.update(
            stimulus_mode="reviewed_display_step",
            display_stimulus=dict(
                baseline_gray_level=20,
                step_gray_level=200,
                onset_ms=200,
                step_duration_ms=200,
                display_brightness_fraction=0.4,
            ),
            response={
                k: FIXTURE["response"][k]
                for k in (
                    "baseline_window_ms",
                    "minimum_baseline_frames",
                    "minimum_post_frames",
                    "latency_fraction_threshold",
                    "maximum_latency_ms",
                )
            },
        )
    if scale:
        material.update(
            scale_basis="millimeters",
            geometry_scale=dict(
                calibration_id="FICTIONAL-GEOMETRY",
                calibration_sha256="a" * 64,
                pixels_to_mm=0.1,
                min_diameter_pixels=2,
                max_diameter_pixels=10,
                max_uncertainty_mm=0.2,
            ),
        )
    material = ExecutableOpticalMaterial.model_validate(material).data()
    config = dict(
        material=material,
        sha256=digest(material),
        software_adapter_id=optical.ADAPTER,
        configuration_id="FICTIONAL-OPTICAL",
        supported_phone_models=["FICTIONAL-PHONE"],
        supported_os_versions=["FICTIONAL-OS"],
        supported_native_builds=["0.1.0:1"],
    )
    seg = optical.extract_pixels(FIXTURE["vectors"][0]["gray"], material)
    frames = [
        dict(
            sequence=i,
            native_timestamp_ms=1000.0 + i * 100,
            dispatch_ms=1001.0 + i * 100,
            exposure_duration_ms=10,
            sensitivity_iso=200.0,
            autoexposure_state="converged",
            roi_luma_sha256=__import__("hashlib")
            .sha256(bytes(FIXTURE["vectors"][0]["gray"]))
            .hexdigest(),
            focus_state="focused",
            exposure_evidence="capture_result_timestamp_match",
            segmentation=deepcopy(seg),
        )
        for i in range(10)
    ]
    flags = sorted(
        optical.FLAGS
        | ({"NO_APPROVED_STIMULUS"} if not display else set())
        | ({"NO_MILLIMETER_GEOMETRY"} if not scale else set())
    )
    onset = 1200 if display else None
    features = optical.compute_features(
        [(f["native_timestamp_ms"], seg["diameter_normalized"]) for f in frames],
        material,
        onset,
    )
    raw = dict(
        schema_version="1.0.0",
        implementation_version=optical.ADAPTER,
        extractor_version=optical.EXTRACTOR,
        run_id="11111111-1111-4111-8111-111111111111",
        workspace_epoch="FICTIONAL-WORKSPACE",
        authorization_id="22222222-2222-4222-8222-222222222222",
        configuration_sha256=config["sha256"],
        status="valid",
        started_at="2026-10-11T00:00:00Z",
        ended_at="2026-10-11T00:00:01Z",
        clock_domain="elapsed_realtime_nanos",
        physical_onset_verified=False,
        model_eligible=False,
        stimulus=dict(
            requested=material["stimulus_mode"],
            requested_onset_ms=200 if display else None,
            native_presented_at_ms=onset,
            native_timestamp_method="choreographer_submission_elapsed_mapping"
            if display
            else None,
            physically_measured_at_ms=None,
        ),
        camera=dict(
            camera_id=material["camera_id"],
            lens_facing="front",
            width=640,
            height=480,
            output_width=640,
            output_height=480,
            output_rotation_degrees=0,
            sensor_orientation_degrees=90,
            exposure_mode="automatic",
            focus_mode="continuous_auto",
            phone_model="FICTIONAL-PHONE",
            os_version="FICTIONAL-OS",
            native_build="0.1.0:1",
        ),
        frame_events=frames,
        features={**features, "valid_frames": 10, "total_frames": 10},
        quality_flags=flags,
    )
    projection = dict(
        status="valid",
        source="prototype_sensor",
        started_at=raw["started_at"],
        ended_at=raw["ended_at"],
        quality_flags=flags,
        capture_config_id=config["configuration_id"],
        camera_id=material["camera_id"],
        frame_rate_hz=10,
        scale_basis="calibrated_mm" if scale else "normalized",
        baseline_diameter_mm=features["baseline_diameter_mm"],
        relative_constriction=None,
        latency_ms=None,
        raw_artifact_id=None,
    )
    return raw, projection, config


@pytest.mark.parametrize("vector", FIXTURE["vectors"], ids=lambda x: x["name"])
def test_literal_pixel_goldens(vector):
    s = optical.extract_pixels(vector["gray"], FIXTURE["configuration"])
    assert s["status"] == vector["status"] and s["reason"] == vector["reason"]
    if s["status"] == "valid":
        for actual, golden in (
            ("area_pixels", "area"),
            ("perimeter_pixels", "perimeter"),
            ("center_x_normalized", "center_x"),
            ("center_y_normalized", "center_y"),
            ("diameter_normalized", "diameter"),
            ("roundness", "roundness"),
            ("contrast_delta", "contrast"),
        ):
            assert s[actual] == pytest.approx(vector[golden], abs=1e-12)


def test_response_and_scale_reference_match_literal_vector_and_raw_codec():
    _, _, c = fixture(display=True, scale=True)
    r = FIXTURE["response"]
    f = optical.compute_features(
        list(zip(r["timestamps"], r["diameters"])), c["material"], r["onset"]
    )
    assert f["baseline_diameter_normalized"] == 0.5
    assert f["baseline_diameter_mm"] == 0.8
    assert f["relative_constriction"] == pytest.approx(r["constriction"])
    assert f["native_callback_latency_ms"] == r["latency"]
    assert (
        optical.compute_features([], c["material"], None)["baseline_diameter_mm"]
        is None
    )
    gray = bytes(FIXTURE["vectors"][0]["gray"])
    b = (
        b"OTGD-EYE-ROI-v1\n"
        + struct.pack("<HHI", 16, 16, 2)
        + struct.pack("<dI", 1000, 0)
        + gray
        + struct.pack("<dI", 1100, 1)
        + gray
    )
    assert (
        len(b) == FIXTURE["raw_size"]
        and hashlib.sha256(b).hexdigest() == FIXTURE["raw_sha256"]
    )


@pytest.mark.parametrize(
    "display,scale", [(False, False), (False, True), (True, False), (True, True)]
)
def test_positive_reviewed_config_evidence_is_never_physical_or_model_qualification(
    display, scale
):
    raw, projection, config = fixture(display=display, scale=scale)
    result = optical.validate_optical(raw, projection, config)
    assert (
        result["model_eligible"] is False and result["physical_onset_verified"] is False
    )
    assert result["calibration_status"] == (
        "geometry_only" if scale else "normalized_only"
    )


@pytest.mark.parametrize(
    "mutate,code",
    [
        (lambda r, p, c: r.update(hidden=True), "OPTICAL_EVIDENCE_FIELDS"),
        (
            lambda r, p, c: r.update(configuration_sha256="0" * 64),
            "OPTICAL_CONFIGURATION_MISMATCH",
        ),
        (lambda r, p, c: r.update(run_id="not-uuid"), "OPTICAL_IDENTITY_INVALID"),
        (
            lambda r, p, c: r.update(model_eligible=True),
            "OPTICAL_PHYSICAL_QUALIFICATION_UNSUPPORTED",
        ),
        (
            lambda r, p, c: r["camera"].update(phone_model="UNAPPROVED"),
            "OPTICAL_BUILD_UNSUPPORTED",
        ),
        (
            lambda r, p, c: r["camera"].update(output_rotation_degrees=90),
            "OPTICAL_CAMERA_MISMATCH",
        ),
        (
            lambda r, p, c: r["frame_events"][1].update(sequence=0),
            "OPTICAL_FRAME_ORDER",
        ),
        (
            lambda r, p, c: r["frame_events"][1].update(native_timestamp_ms=1000),
            "OPTICAL_FRAME_CLOCK",
        ),
        (
            lambda r, p, c: r["frame_events"][0].update(dispatch_ms=2000),
            "OPTICAL_FRAME_CLOCK",
        ),
        (
            lambda r, p, c: r["frame_events"][0].update(exposure_duration_ms=None),
            "OPTICAL_SEGMENTATION_INVALID",
        ),
        (
            lambda r, p, c: r["frame_events"][0]["segmentation"].update(
                diameter_normalized=0.5
            ),
            "OPTICAL_FEATURE_MISMATCH",
        ),
        (
            lambda r, p, c: r["features"].update(valid_frames=9),
            "OPTICAL_FEATURE_MISMATCH",
        ),
        (
            lambda r, p, c: r["features"].update(baseline_diameter_mm=2),
            "OPTICAL_FEATURE_MISMATCH",
        ),
        (
            lambda r, p, c: p.update(latency_ms=150),
            "OPTICAL_PHYSICAL_LATENCY_UNQUALIFIED",
        ),
        (
            lambda r, p, c: r["stimulus"].update(physically_measured_at_ms=1000),
            "OPTICAL_STIMULUS_MISMATCH",
        ),
        (lambda r, p, c: r.update(quality_flags=[]), "OPTICAL_QUALITY_FLAGS"),
    ],
)
def test_changed_evidence_is_rejected(mutate, code):
    raw, p, c = fixture()
    mutate(raw, p, c)
    with pytest.raises(Problem) as error:
        optical.validate_optical(raw, p, c)
    assert error.value.code == code


def test_invalid_capture_counts_and_null_features_do_not_become_positive():
    raw, p, c = fixture()
    raw["status"] = p["status"] = "invalid"
    raw["features"].update({k: None for k in optical.FEATURES[:-2]})
    p["relative_constriction"] = p["baseline_diameter_mm"] = None
    assert optical.validate_optical(raw, p, c)["median_diameter_normalized"] is None
    raw["frame_events"][0]["segmentation"] = dict(
        status="invalid",
        reason="EDGE_COMPONENT",
        area_pixels=0,
        perimeter_pixels=0,
        center_x_normalized=None,
        center_y_normalized=None,
        diameter_normalized=None,
        roundness=None,
        contrast_delta=None,
    )
    raw["features"]["valid_frames"] = 9
    assert optical.validate_optical(raw, p, c)["model_eligible"] is False


def test_material_fields_phone_build_sensor_and_stimulus_are_all_bound():
    raw, p, c = fixture(display=True)
    raw["stimulus"]["native_presented_at_ms"] = 1900
    with pytest.raises(Problem) as e:
        optical.validate_optical(raw, p, c)
    assert e.value.code == "OPTICAL_STIMULUS_CLOCK"
    raw, p, c = fixture()
    c["material"]["expected_sensor_orientation_degrees"] = 180
    c["sha256"] = digest(c["material"])
    raw["configuration_sha256"] = c["sha256"]
    with pytest.raises(Problem) as e:
        optical.validate_optical(raw, p, c)
    assert e.value.code == "OPTICAL_CAMERA_MISMATCH"
    with pytest.raises(Problem):
        optical.extract_pixels([True], FIXTURE["configuration"])


def test_checked_in_python_dto_fixture_tracks_actual_server_scalar_contract():
    raw, projection, config = fixture()
    path = (
        Path(__file__).parents[3]
        / "apps/mobile/testfixtures/backend-optical-result.json"
    )
    value = strict_loads(path.read_text())
    assert value["native_result"] == raw
    assert value["projection"] == projection
    assert value["configuration"] == config
    optical.validate_optical(
        value["native_result"], value["projection"], value["configuration"]
    )


def test_actual_kotlin_production_factory_fixture_passes_independent_server_validation():
    p = (
        Path(__file__).parents[3]
        / "apps/mobile/modules/eye-capture/fixtures/native-optical-result-v1.json"
    )
    native = strict_loads(p.read_text())
    assert native["notice"].startswith("FICTIONAL NATIVE FACTORY")
    result = optical.validate_optical(
        native["native_result"], native["projection"], native["configuration"]
    )
    assert result["model_eligible"] is False
    assert result["median_diameter_normalized"] == pytest.approx(
        FIXTURE["vectors"][0]["diameter"]
    )


def test_descriptive_native_change_cannot_become_unqualified_pupil_response():
    raw, p, c = fixture(display=True)
    p["relative_constriction"] = raw["features"]["relative_constriction"]
    with pytest.raises(Problem) as error:
        optical.validate_optical(raw, p, c)
    assert error.value.code == "OPTICAL_ANATOMICAL_RESPONSE_UNQUALIFIED"


@pytest.mark.parametrize("iso", [-1, True, float("nan"), 10000001, "200"])
def test_sensor_sensitivity_metadata_is_bounded_observed_number(iso):
    raw, p, c = fixture()
    raw["frame_events"][0]["sensitivity_iso"] = iso
    with pytest.raises(Problem):
        optical.validate_optical(raw, p, c)


def test_observed_autoexposure_cannot_relabel_searching_or_platform_callback():
    raw, p, c = fixture()
    raw["frame_events"][0]["autoexposure_state"] = "searching"
    with pytest.raises(Problem) as error:
        optical.validate_optical(raw, p, c)
    assert error.value.code == "OPTICAL_SEGMENTATION_INVALID"
    raw["frame_events"][0]["autoexposure_state"] = "stable_at_callback"
    with pytest.raises(Problem) as error:
        optical.validate_optical(raw, p, c)
    assert error.value.code == "OPTICAL_CAMERA_METADATA"
    raw, p, c = fixture()
    for frame in raw["frame_events"]:
        frame["sensitivity_iso"] = None  # retained unknown; no guessed gain
    assert optical.validate_optical(raw, p, c)["physical_onset_verified"] is False
    raw["clock_domain"] = "avfoundation_host_clock_seconds"
    raw["camera"]["sensor_orientation_degrees"] = None
    raw["quality_flags"].append("EXPOSURE_NOT_FRAME_MATCHED")
    p["quality_flags"].append("EXPOSURE_NOT_FRAME_MATCHED")
    for frame in raw["frame_events"]:
        frame["exposure_evidence"] = "device_state_at_callback"
        frame["autoexposure_state"] = "stable_at_callback"
    assert optical.validate_optical(raw, p, c)["physical_onset_verified"] is False


def roi_fixture():
    import struct

    raw, projection, config = fixture()
    material = config["material"]
    gray = bytes(FIXTURE["vectors"][0]["gray"])
    payload = optical.ROI_MAGIC + struct.pack(
        "<HHI",
        material["roi_sample_width"],
        material["roi_sample_height"],
        len(raw["frame_events"]),
    )
    payload += b"".join(
        struct.pack("<dI", frame["native_timestamp_ms"], frame["sequence"]) + gray
        for frame in raw["frame_events"]
    )
    attempt = dict(
        component="eyes",
        status="valid",
        source="prototype_sensor",
        attempt_id="33333333-3333-4333-8333-333333333333",
        record_id=raw["run_id"],
        configuration_id=config["configuration_id"],
        configuration_hash=config["sha256"],
        started_at=raw["started_at"],
        ended_at=raw["ended_at"],
        component_metadata=dict(native_result=raw, projection=projection),
    )
    return payload, attempt, config


def test_roi_codec_verification_binds_actual_luminance_native_ledger_and_attempt():
    raw, attempt, config = roi_fixture()
    proof = optical.validate_roi_artifact(raw, attempt, config)
    assert proof["codec"] == "otgd_eye_roi_v1" and proof["frame_count"] == 10
    assert (
        proof["record_id"] == attempt["record_id"]
        and proof["physical_onset_verified"] is False
    )
    changed = deepcopy(attempt)
    for frame in changed["component_metadata"]["native_result"]["frame_events"]:
        frame["focus_state"] = "unknown"
        frame["segmentation"] = dict(
            status="invalid",
            reason="CAMERA_METADATA_UNQUALIFIED",
            area_pixels=0,
            perimeter_pixels=0,
            center_x_normalized=None,
            center_y_normalized=None,
            diameter_normalized=None,
            roundness=None,
            contrast_delta=None,
        )
    # Metadata changes cannot leave the overall accepted valid count intact.
    with pytest.raises(Problem):
        optical.validate_roi_artifact(raw, changed, config)


@pytest.mark.parametrize(
    "fault",
    [
        "magic",
        "width",
        "count",
        "timestamp",
        "sequence",
        "pixels",
        "extra",
        "truncated",
        "large",
        "run",
        "clock",
        "config",
        "missing",
        "invalid",
    ],
)
def test_roi_codec_rejects_relabeling_or_changed_binary_content(fault):
    import struct

    payload, attempt, config = roi_fixture()
    raw = bytearray(payload)
    if fault == "magic":
        raw[0] ^= 1
    elif fault == "width":
        struct.pack_into("<H", raw, 16, 15)
    elif fault == "count":
        struct.pack_into("<I", raw, 20, 9)
    elif fault == "timestamp":
        struct.pack_into("<d", raw, 24, 999.0)
    elif fault == "sequence":
        struct.pack_into("<I", raw, 32, 1)
    elif fault == "pixels":
        raw[40] ^= 1
    elif fault == "extra":
        raw += b"hidden"
    elif fault == "truncated":
        raw = raw[:-1]
    elif fault == "large":
        raw += b"x" * optical.ROI_MAX_BYTES
    elif fault == "run":
        attempt["record_id"] = "44444444-4444-4444-8444-444444444444"
    elif fault == "clock":
        attempt["started_at"] = "2026-10-11T00:00:00.001Z"
    elif fault == "config":
        attempt["configuration_hash"] = "f" * 64
    elif fault == "missing":
        attempt["component_metadata"] = {}
    elif fault == "invalid":
        attempt["status"] = "invalid"
    with pytest.raises(Problem):
        optical.validate_roi_artifact(bytes(raw), attempt, config)


def test_roi_same_pixel_summary_cannot_hide_changed_content_and_statistics_cannot_be_forged():
    import hashlib

    payload, attempt, config = roi_fixture()
    raw = bytearray(payload)
    raw[36] ^= 1  # changes an outside luminance pixel without changing component area
    with pytest.raises(Problem) as error:
        optical.validate_roi_artifact(bytes(raw), attempt, config)
    assert error.value.code == "OPTICAL_ROI_CONTENT_MISMATCH"
    attempt["component_metadata"]["native_result"]["frame_events"][0][
        "roi_luma_sha256"
    ] = hashlib.sha256(raw[36 : 36 + 256]).hexdigest()
    with pytest.raises(Problem):
        optical.validate_roi_artifact(bytes(raw), attempt, config)
