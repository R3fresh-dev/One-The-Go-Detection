"""Independent optical evidence arithmetic; camera callbacks never prove physical onset.

The reviewed native extractor emits data-only ROI statistics. This validator
recomputes every exposed scalar and checks the admitted scientific tuple; it
cannot attest that client camera pixels are anatomically valid or unmodified.
"""

import math
import hashlib
import re
import struct
from datetime import datetime
from uuid import UUID

from pydantic import ValidationError

from .canonical import canonical, digest
from .errors import Problem
from .operator_governance import ExecutableOpticalMaterial

ADAPTER = "optical_roi_v1"
EXTRACTOR = "otgd-dark-component-v1"
FEATURES = "median_diameter_normalized baseline_diameter_normalized baseline_diameter_mm relative_constriction native_callback_latency_ms valid_frames total_frames".split()
SEGMENTATION = "status reason area_pixels perimeter_pixels center_x_normalized center_y_normalized diameter_normalized roundness contrast_delta".split()
FLAGS = {
    "PHYSICAL_ONSET_UNMEASURED",
    "UNQUALIFIED_OPTICAL_EXTRACTOR",
    "UNCALIBRATED_CAMERA_RESPONSE",
}


def reject(code="OPTICAL_EVIDENCE_INVALID"):
    raise Problem(422, code)


def exact(value, keys):
    if not isinstance(value, dict) or set(value) != set(
        keys.split() if isinstance(keys, str) else keys
    ):
        reject("OPTICAL_EVIDENCE_FIELDS")


def number(value, low=0, high=1e15):
    if (
        type(value) not in (int, float)
        or not math.isfinite(value)
        or not low <= value <= high
    ):
        reject("OPTICAL_EVIDENCE_NUMBER")
    return value


def integer(value, low=0, high=300):
    if type(value) is not int or not low <= value <= high:
        reject("OPTICAL_EVIDENCE_NUMBER")
    return value


def close(value, expected):
    if expected is None:
        if value is not None:
            reject("OPTICAL_FEATURE_MISMATCH")
    elif value is None or not math.isclose(
        number(value), expected, rel_tol=1e-9, abs_tol=1e-9
    ):
        reject("OPTICAL_FEATURE_MISMATCH")


def utc(value):
    if not isinstance(value, str) or len(value) > 40 or not value.endswith("Z"):
        reject("OPTICAL_EVIDENCE_CLOCK")
    try:
        return datetime.fromisoformat(value).timestamp()
    except ValueError:
        reject("OPTICAL_EVIDENCE_CLOCK")


def median(values):
    if not values:
        return None
    a = sorted(values)
    return a[len(a) // 2] if len(a) % 2 else (a[len(a) // 2 - 1] + a[len(a) // 2]) / 2


def compute_features(values, material, onset):
    overall = median([d for _, d in values])
    baseline, constriction, latency = overall, None, None
    stimulus, response, geometry = (
        material.get(k) for k in ("display_stimulus", "response", "geometry_scale")
    )
    if stimulus and response:
        baseline = None
        if onset is not None:
            prior = [
                d
                for t, d in values
                if onset - response["baseline_window_ms"] <= t < onset
            ]
            after = [
                (t, d)
                for t, d in values
                if onset <= t < onset + stimulus["step_duration_ms"]
            ]
            if (
                len(prior) >= response["minimum_baseline_frames"]
                and len(after) >= response["minimum_post_frames"]
            ):
                baseline = median(prior)
                if baseline and baseline > 0:
                    constriction = min(
                        1, max(0, (baseline - min(d for _, d in after)) / baseline)
                    )
                    latency = next(
                        (
                            t - onset
                            for t, d in after
                            if t - onset <= response["maximum_latency_ms"]
                            and (baseline - d) / baseline
                            >= response["latency_fraction_threshold"]
                        ),
                        None,
                    )
    pixels = (
        baseline * min(material["roi_sample_width"], material["roi_sample_height"])
        if baseline is not None
        else None
    )
    mm = (
        pixels * geometry["pixels_to_mm"]
        if geometry
        and pixels is not None
        and geometry["min_diameter_pixels"] <= pixels <= geometry["max_diameter_pixels"]
        else None
    )
    return dict(
        median_diameter_normalized=overall,
        baseline_diameter_normalized=baseline,
        baseline_diameter_mm=mm,
        relative_constriction=constriction,
        native_callback_latency_ms=latency,
    )


def extract_pixels(gray, material):
    """Server reference for literal pixel goldens; production proof still needs retained source pixels."""
    w, h = material["roi_sample_width"], material["roi_sample_height"]
    if len(gray) != w * h or any(type(v) is not int or not 0 <= v <= 255 for v in gray):
        reject("OPTICAL_PIXEL_BOUND")
    seen, candidates, rejected = set(), [], "NO_DARK_COMPONENT"
    outside = [v for v in gray if v > material["dark_threshold"]]
    for start in range(len(gray)):
        if start in seen or gray[start] > material["dark_threshold"]:
            continue
        queue, head = [start], 0
        seen.add(start)
        area = perimeter = total = 0
        sx = sy = 0.0
        edge = False
        while head < len(queue):
            p = queue[head]
            head += 1
            x, y = p % w, p // w
            area += 1
            sx += x + 0.5
            sy += y + 0.5
            total += gray[p]
            e = material["edge_margin_pixels"]
            edge |= x < e or y < e or x >= w - e or y >= h - e
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if (
                    not 0 <= nx < w
                    or not 0 <= ny < h
                    or gray[ny * w + nx] > material["dark_threshold"]
                ):
                    perimeter += 1
                elif ny * w + nx not in seen:
                    seen.add(ny * w + nx)
                    queue.append(ny * w + nx)
        fraction, roundness = area / len(gray), 4 * math.pi * area / perimeter**2
        contrast = sum(outside) / len(outside) - total / area if outside else 0
        reason = (
            "EDGE_COMPONENT"
            if edge
            else "AREA_OUT_OF_RANGE"
            if not material["min_area_fraction"]
            <= fraction
            <= material["max_area_fraction"]
            else "ROUNDNESS_LOW"
            if roundness < material["min_roundness"]
            else "CONTRAST_LOW"
            if contrast < material["min_contrast_delta"]
            else None
        )
        if reason:
            rejected = reason
        else:
            candidates.append(
                dict(
                    status="valid",
                    reason=None,
                    area_pixels=area,
                    perimeter_pixels=perimeter,
                    center_x_normalized=sx / area / w,
                    center_y_normalized=sy / area / h,
                    diameter_normalized=2 * math.sqrt(area / math.pi) / min(w, h),
                    roundness=roundness,
                    contrast_delta=contrast,
                )
            )
    return (
        candidates[0]
        if len(candidates) == 1
        else dict(
            status="invalid",
            reason="AMBIGUOUS_COMPONENTS" if candidates else rejected,
            area_pixels=0,
            perimeter_pixels=0,
            center_x_normalized=None,
            center_y_normalized=None,
            diameter_normalized=None,
            roundness=None,
            contrast_delta=None,
        )
    )


def validate_optical(raw, projection, config):
    exact(
        raw,
        "schema_version implementation_version extractor_version run_id workspace_epoch authorization_id configuration_sha256 status started_at ended_at clock_domain physical_onset_verified model_eligible stimulus camera frame_events features quality_flags",
    )
    try:
        encoded_size = len(canonical(raw))
    except (ValueError, TypeError, UnicodeError):
        reject("OPTICAL_EVIDENCE_INVALID")
    if encoded_size > 256 * 1024:
        reject("OPTICAL_EVIDENCE_BOUND")
    try:
        material = ExecutableOpticalMaterial.model_validate(config["material"]).data()
    except (ValidationError, KeyError):
        reject("OPTICAL_CONFIGURATION_INVALID")
    if (
        config.get("software_adapter_id") != ADAPTER
        or raw["schema_version"] != "1.0.0"
        or raw["implementation_version"] != ADAPTER
        or raw["extractor_version"] != EXTRACTOR
        or digest(material) != config["sha256"]
        or raw["configuration_sha256"] != config["sha256"]
    ):
        reject("OPTICAL_CONFIGURATION_MISMATCH")
    for key in ("run_id", "authorization_id"):
        try:
            UUID(raw[key])
        except (ValueError, TypeError, AttributeError):
            reject("OPTICAL_IDENTITY_INVALID")
    if (
        not isinstance(raw["workspace_epoch"], str)
        or not 1 <= len(raw["workspace_epoch"]) <= 128
    ):
        reject("OPTICAL_IDENTITY_INVALID")
    if (
        raw["physical_onset_verified"] is not False
        or raw["model_eligible"] is not False
        or raw["clock_domain"]
        not in ("elapsed_realtime_nanos", "avfoundation_host_clock_seconds")
    ):
        reject("OPTICAL_PHYSICAL_QUALIFICATION_UNSUPPORTED")
    start, end = utc(raw["started_at"]), utc(raw["ended_at"])
    if (
        end < start
        or end - start > material["duration_ms"] / 1000 + 5
        or start < utc(projection["started_at"]) - 0.005
        or end > utc(projection["ended_at"]) + 0.005
    ):
        reject("OPTICAL_EVIDENCE_CLOCK")
    camera = raw["camera"]
    exact(
        camera,
        "camera_id lens_facing width height output_width output_height output_rotation_degrees sensor_orientation_degrees exposure_mode focus_mode phone_model os_version native_build",
    )
    for actual, expected in (
        ("camera_id", "camera_id"),
        ("lens_facing", "lens_facing"),
        ("width", "capture_width"),
        ("height", "capture_height"),
        ("output_rotation_degrees", "expected_output_rotation_degrees"),
        ("exposure_mode", "exposure_mode"),
        ("focus_mode", "focus_mode"),
    ):
        if camera[actual] != material[expected]:
            reject("OPTICAL_CAMERA_MISMATCH")
    expected_output = (
        (material["capture_width"], material["capture_height"])
        if material["expected_output_rotation_degrees"] % 180 == 0
        else (material["capture_height"], material["capture_width"])
    )
    if (camera["output_width"], camera["output_height"]) != expected_output:
        reject("OPTICAL_CAMERA_MISMATCH")
    sensor = camera["sensor_orientation_degrees"]
    if sensor is not None and (
        type(sensor) is not int or sensor not in (0, 90, 180, 270)
    ):
        reject("OPTICAL_CAMERA_MISMATCH")
    if (
        material["expected_sensor_orientation_degrees"] is not None
        and sensor != material["expected_sensor_orientation_degrees"]
    ):
        reject("OPTICAL_CAMERA_MISMATCH")
    for key, allowed in (
        ("phone_model", "supported_phone_models"),
        ("os_version", "supported_os_versions"),
        ("native_build", "supported_native_builds"),
    ):
        if camera[key] not in config.get(allowed, []):
            reject("OPTICAL_BUILD_UNSUPPORTED")
    frames = raw["frame_events"]
    if not isinstance(frames, list) or len(frames) > material["max_frames"]:
        reject("OPTICAL_FRAME_BOUND")
    values, last = [], None
    for index, frame in enumerate(frames):
        exact(
            frame,
            "sequence native_timestamp_ms dispatch_ms exposure_duration_ms focus_state sensitivity_iso autoexposure_state exposure_evidence roi_luma_sha256 segmentation",
        )
        if not isinstance(frame["roi_luma_sha256"], str) or not re.fullmatch(
            r"[a-f0-9]{64}", frame["roi_luma_sha256"]
        ):
            reject("OPTICAL_ROI_DIGEST_INVALID")
        if integer(frame["sequence"]) != index:
            reject("OPTICAL_FRAME_ORDER")
        timestamp, dispatch = (
            number(frame["native_timestamp_ms"]),
            number(frame["dispatch_ms"]),
        )
        if (
            dispatch < timestamp
            or dispatch - timestamp > material["maximum_frame_gap_ms"]
            or last is not None
            and (
                timestamp <= last or timestamp - last > material["maximum_frame_gap_ms"]
            )
        ):
            reject("OPTICAL_FRAME_CLOCK")
        last = timestamp
        expected_exposure = (
            "capture_result_timestamp_match"
            if raw["clock_domain"] == "elapsed_realtime_nanos"
            else "device_state_at_callback"
        )
        if frame["exposure_evidence"] != expected_exposure:
            reject("OPTICAL_CAMERA_METADATA")
        if frame["exposure_duration_ms"] is not None:
            number(frame["exposure_duration_ms"], 0.000000001, 10000)
        if frame["focus_state"] not in ("focused", "adjusting_or_unknown", "unknown"):
            reject("OPTICAL_CAMERA_METADATA")
        if frame["sensitivity_iso"] is not None:
            number(frame["sensitivity_iso"], 0.000000001, 10000000)
        ae = frame["autoexposure_state"]
        ae_states = (
            {
                "inactive",
                "searching",
                "converged",
                "locked",
                "flash_required",
                "unknown",
            }
            if expected_exposure == "capture_result_timestamp_match"
            else {"stable_at_callback", "adjusting_at_callback", "unknown"}
        )
        if type(ae) is not str or ae not in ae_states:
            reject("OPTICAL_CAMERA_METADATA")
        seg = frame["segmentation"]
        exact(seg, SEGMENTATION)
        area, perimeter = (
            integer(
                seg["area_pixels"],
                0,
                material["roi_sample_width"] * material["roi_sample_height"],
            ),
            integer(seg["perimeter_pixels"], 0, 65536),
        )
        if seg["status"] == "valid":
            if (
                seg["reason"] is not None
                or area <= 0
                or perimeter <= 0
                or perimeter > 4 * area
                or frame["focus_state"] != "focused"
                or frame["exposure_duration_ms"] is None
                or ae not in ("converged", "locked", "stable_at_callback")
                or not material["min_area_fraction"]
                <= area / (material["roi_sample_width"] * material["roi_sample_height"])
                <= material["max_area_fraction"]
            ):
                reject("OPTICAL_SEGMENTATION_INVALID")
            for key in ("center_x_normalized", "center_y_normalized"):
                number(seg[key], 0, 1)
            expected_diameter = (
                2
                * math.sqrt(area / math.pi)
                / min(material["roi_sample_width"], material["roi_sample_height"])
            )
            close(seg["diameter_normalized"], expected_diameter)
            close(seg["roundness"], 4 * math.pi * area / perimeter**2)
            if (
                seg["roundness"] < material["min_roundness"]
                or number(seg["contrast_delta"], 0, 255)
                < material["min_contrast_delta"]
            ):
                reject("OPTICAL_SEGMENTATION_INVALID")
            values.append((timestamp, expected_diameter))
        elif seg["status"] == "invalid":
            if (
                area
                or perimeter
                or any(seg[key] is not None for key in SEGMENTATION[4:])
                or seg["reason"]
                not in (
                    "NO_DARK_COMPONENT",
                    "EDGE_COMPONENT",
                    "AREA_OUT_OF_RANGE",
                    "ROUNDNESS_LOW",
                    "CONTRAST_LOW",
                    "AMBIGUOUS_COMPONENTS",
                    "CAMERA_METADATA_UNQUALIFIED",
                )
            ):
                reject("OPTICAL_SEGMENTATION_INVALID")
        else:
            reject("OPTICAL_SEGMENTATION_INVALID")
    if (
        frames
        and frames[-1]["native_timestamp_ms"] - frames[0]["native_timestamp_ms"]
        > material["duration_ms"] + material["maximum_frame_gap_ms"]
    ):
        reject("OPTICAL_FRAME_DURATION")
    stimulus = raw["stimulus"]
    exact(
        stimulus,
        "requested requested_onset_ms native_presented_at_ms native_timestamp_method physically_measured_at_ms",
    )
    if (
        stimulus["requested"] != material["stimulus_mode"]
        or stimulus["physically_measured_at_ms"] is not None
    ):
        reject("OPTICAL_STIMULUS_MISMATCH")
    onset = stimulus["native_presented_at_ms"]
    if material["display_stimulus"]:
        planned = material["display_stimulus"]["onset_ms"]
        if stimulus["requested_onset_ms"] != planned:
            reject("OPTICAL_STIMULUS_MISMATCH")
        if onset is not None:
            number(onset)
            method = (
                "choreographer_submission_elapsed_mapping"
                if raw["clock_domain"] == "elapsed_realtime_nanos"
                else "cadisplaylink_target_timestamp"
            )
            if (
                not frames
                or not frames[0]["native_timestamp_ms"] + planned
                <= onset
                <= frames[0]["native_timestamp_ms"]
                + planned
                + material["maximum_frame_gap_ms"]
                or stimulus["native_timestamp_method"] != method
            ):
                reject("OPTICAL_STIMULUS_CLOCK")
    elif any(
        stimulus[k] is not None
        for k in (
            "requested_onset_ms",
            "native_presented_at_ms",
            "native_timestamp_method",
        )
    ):
        reject("OPTICAL_STIMULUS_MISMATCH")
    valid = raw["status"] == "valid"
    if (
        raw["status"] not in ("valid", "invalid")
        or valid
        and (
            len(values) < material["minimum_valid_frames"]
            or not frames
            or len(values) / len(frames) < material["minimum_valid_frame_fraction"]
        )
    ):
        reject("OPTICAL_QUALITY_MISMATCH")
    flags = raw["quality_flags"]
    required = (
        FLAGS
        | (
            {"NO_APPROVED_STIMULUS"}
            if material["stimulus_mode"] == "passive_ambient_no_modulation"
            else set()
        )
        | (
            {"NO_MILLIMETER_GEOMETRY"}
            if material["scale_basis"] == "normalized"
            else set()
        )
    )
    if (
        not isinstance(flags, list)
        or not required.issubset(flags)
        or len(flags) > 32
        or any(not isinstance(f, str) or not 1 <= len(f) <= 64 for f in flags)
    ):
        reject("OPTICAL_QUALITY_FLAGS")
    features = raw["features"]
    exact(features, FEATURES)
    if integer(features["valid_frames"]) != len(values) or integer(
        features["total_frames"]
    ) != len(frames):
        reject("OPTICAL_FEATURE_MISMATCH")
    computed = compute_features(values if valid else [], material, onset)
    for key, expected in computed.items():
        close(features[key], expected)
    if (
        projection["status"] != raw["status"]
        or projection["source"] != "prototype_sensor"
        or projection["capture_config_id"] != config["configuration_id"]
        or projection["camera_id"] != camera["camera_id"]
        or projection["scale_basis"]
        != (
            "calibrated_mm"
            if material["scale_basis"] == "millimeters"
            else "normalized"
        )
        or not set(flags).issubset(projection["quality_flags"])
    ):
        reject("OPTICAL_PROJECTION_MISMATCH")
    close(projection["frame_rate_hz"], material["frame_rate_hz"])
    close(projection["baseline_diameter_mm"], computed["baseline_diameter_mm"])
    if projection["relative_constriction"] is not None:
        reject("OPTICAL_ANATOMICAL_RESPONSE_UNQUALIFIED")
    if projection["latency_ms"] is not None:
        reject("OPTICAL_PHYSICAL_LATENCY_UNQUALIFIED")
    return {
        **computed,
        "model_eligible": False,
        "physical_onset_verified": False,
        "calibration_status": "geometry_only"
        if material["geometry_scale"]
        else "normalized_only",
    }


ROI_MAGIC = b"OTGD-EYE-ROI-v1\n"
ROI_MAX_BYTES = 5 * 1024 * 1024


def validate_roi_artifact(rawbytes, attemptbody, config):
    """Bind bounded decoded luminance to the accepted owned native frame ledger.

    This establishes codec and immutable software provenance, never anatomical
    identity, physical camera timing, or an authenticated sensor attestation.
    """
    if (
        not isinstance(rawbytes, bytes)
        or not len(ROI_MAGIC) + 8 <= len(rawbytes) <= ROI_MAX_BYTES
    ):
        reject("OPTICAL_ROI_BOUND")
    if (
        not isinstance(attemptbody, dict)
        or attemptbody.get("component") != "eyes"
        or attemptbody.get("status") != "valid"
        or attemptbody.get("source") != "prototype_sensor"
    ):
        reject("OWNED_OPTICAL_ROI_ATTEMPT_REQUIRED")
    metadata = attemptbody.get("component_metadata", {})
    if not isinstance(metadata, dict):
        reject("OWNED_OPTICAL_ROI_ATTEMPT_REQUIRED")
    native, projection = metadata.get("native_result"), metadata.get("projection")
    if not isinstance(native, dict) or not isinstance(projection, dict):
        reject("OWNED_OPTICAL_ROI_ATTEMPT_REQUIRED")
    if (
        native.get("run_id") != attemptbody.get("record_id")
        or native.get("configuration_sha256") != attemptbody.get("configuration_hash")
        or attemptbody.get("configuration_id") != config.get("configuration_id")
        or native.get("started_at") != attemptbody.get("started_at")
        or native.get("ended_at") != attemptbody.get("ended_at")
    ):
        reject("OPTICAL_ROI_ACQUISITION_MISMATCH")
    validate_optical(native, projection, config)
    material = config["material"]
    if material.get("raw_encoding") != "otgd_eye_roi_v1" or not rawbytes.startswith(
        ROI_MAGIC
    ):
        reject("OPTICAL_ROI_CODEC_INVALID")
    width, height, count = struct.unpack_from("<HHI", rawbytes, len(ROI_MAGIC))
    if (
        width != material["roi_sample_width"]
        or height != material["roi_sample_height"]
        or not 1 <= count <= material["max_frames"]
        or count != len(native["frame_events"])
        or len(rawbytes) != len(ROI_MAGIC) + 8 + count * (12 + width * height)
    ):
        reject("OPTICAL_ROI_GEOMETRY_MISMATCH")
    offset, frame_digests = len(ROI_MAGIC) + 8, []
    for index, frame in enumerate(native["frame_events"]):
        timestamp, sequence = struct.unpack_from("<dI", rawbytes, offset)
        if (
            not math.isfinite(timestamp)
            or sequence != index
            or timestamp != frame["native_timestamp_ms"]
        ):
            reject("OPTICAL_ROI_FRAME_MISMATCH")
        gray = rawbytes[offset + 12 : offset + 12 + width * height]
        sha = hashlib.sha256(gray).hexdigest()
        if sha != frame["roi_luma_sha256"]:
            reject("OPTICAL_ROI_CONTENT_MISMATCH")
        extracted = extract_pixels(gray, material)
        qualified = (
            frame["exposure_duration_ms"] is not None
            and frame["focus_state"] == "focused"
            and frame["autoexposure_state"]
            in ("converged", "locked", "stable_at_callback")
        )
        if not qualified:
            extracted = dict(
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
        actual = frame["segmentation"]
        for key, expected in extracted.items():
            if type(expected) in (int, float):
                close(actual[key], expected)
            elif actual[key] != expected:
                reject("OPTICAL_ROI_SEGMENTATION_MISMATCH")
        frame_digests.append(sha)
        offset += 12 + width * height
    proof = dict(
        codec="otgd_eye_roi_v1",
        attempt_id=attemptbody.get("attempt_id"),
        record_id=attemptbody["record_id"],
        authorization_id=native["authorization_id"],
        configuration_sha256=config["sha256"],
        frame_count=count,
        roi_width=width,
        roi_height=height,
        sha256=hashlib.sha256(rawbytes).hexdigest(),
        frame_content_sha256=digest(frame_digests),
        physical_onset_verified=False,
    )
    return {**proof, "verification_sha256": digest(proof)}
