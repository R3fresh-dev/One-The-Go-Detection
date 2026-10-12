"""Bounded SDK metadata verification, without inventing sensor time or waveform."""
from typing import Annotated, Literal
from pydantic import Field, model_validator
from .dto import DTO
from .errors import Problem

SDK_COMMIT = "91575258e5e2c47f0f4b8ec97b651381671f4637"
Count = Annotated[int, Field(ge=0, le=120000)]
Tick = Annotated[int, Field(ge=0, le=9007199254740991)]


class SparkFunMaterial(DTO):
    schema_version: Literal["1.0.0"]
    channel: Literal["cardiac"]
    modality: Literal["ppg"]
    adapter_id: Literal["otgd_sparkfun_max32664_v1"]
    protocol_version: Literal[1]
    duration_ms: Annotated[int, Field(ge=3000, le=60000)]
    end_guard_ms: Annotated[int, Field(ge=100, le=500)]
    poll_interval_ms: Annotated[int, Field(ge=50, le=1000)]
    i2c_timeout_ms: Annotated[int, Field(ge=1, le=20)]
    i2c_address: Literal[85]
    bus_frequency_hz: Literal[100000]
    sda_gpio: Literal[11]
    scl_gpio: Literal[12]
    reset_gpio: Literal[5]
    mfio_gpio: Literal[6]
    algorithm_mode: Literal[1, 2]
    sdk_commit: Literal[SDK_COMMIT]
    sdk_version: Literal["1.1"]
    extractor_version: Literal["sparkfun_sensor_bpm_v1"]
    warmup_ms: Annotated[int, Field(ge=1000, le=10000)]
    max_no_data_ms: Annotated[int, Field(ge=50, le=5000)]
    minimum_valid_samples: Annotated[int, Field(ge=1, le=256)]
    minimum_confidence: Annotated[int, Field(ge=0, le=100)]
    minimum_heart_rate_bpm: Annotated[int, Field(ge=1, le=300)]
    maximum_heart_rate_bpm: Annotated[int, Field(ge=1, le=300)]
    hub_firmware_major: Annotated[int, Field(ge=0, le=255)]
    hub_firmware_minor: Annotated[int, Field(ge=0, le=255)]
    hub_firmware_revision: Annotated[int, Field(ge=0, le=255)]

    @model_validator(mode="after")
    def coherent(self):
        if (self.minimum_heart_rate_bpm >= self.maximum_heart_rate_bpm
            or self.max_no_data_ms < self.poll_interval_ms
            or self.duration_ms <= 10 + 1000 + self.warmup_ms + self.end_guard_ms + 250):
            raise ValueError("Vendor acquisition budget or thresholds are inconsistent")
        return self


class HubFirmware(DTO):
    major: Annotated[int, Field(ge=0, le=255)]
    minor: Annotated[int, Field(ge=0, le=255)]
    revision: Annotated[int, Field(ge=0, le=255)]


class Observation(DTO):
    sequence: Count
    host_received_monotonic_us: Tick
    heart_rate_bpm: Annotated[int, Field(ge=0, le=65535)]
    confidence_percent: Annotated[int, Field(ge=0, le=255)]
    finger_status: Annotated[int, Field(ge=0, le=255)]
    extended_status: Annotated[int, Field(ge=-128, le=127)] | None


class PPGEvidence(DTO):
    schema_version: Literal["1.0.0"]
    adapter_id: Literal["otgd_sparkfun_max32664_v1"]
    sdk_commit: Literal[SDK_COMMIT]
    sdk_version: Literal["1.1"]
    algorithm_mode: Literal[1, 2]
    hub_firmware: HubFirmware | None
    configured_sensor_rate_hz: Annotated[int, Field(ge=50, le=3200)] | None
    actual_sensor_cadence_hz: Literal[None]
    host_poll_interval_ms: Annotated[int, Field(ge=50, le=1000)]
    sample_timestamp_source: Literal["host_i2c_receive_unqualified_sensor_time"]
    acquisition_started_monotonic_us: Tick
    acquisition_ended_monotonic_us: Tick
    observed_samples: Count
    valid_samples: Count
    invalid_samples: Count
    missed_poll_intervals: Count
    fifo_empty_polls: Count
    fifo_backlog_peak: Annotated[int, Field(ge=0, le=255)]
    sensor_dropped_samples: Literal[None]
    last_observation: Observation | None


def validate_ppg(projection, raw, material):
    from pydantic import ValidationError
    try:
        evidence = PPGEvidence.model_validate(raw).data()
        config = SparkFunMaterial.model_validate(material).data()
    except (ValidationError, TypeError):
        raise Problem(422, "VENDOR_EVIDENCE_INVALID") from None
    start, end = evidence["acquisition_started_monotonic_us"], evidence["acquisition_ended_monotonic_us"]
    last = evidence["last_observation"]
    if (end < start or end - start > config["duration_ms"] * 1000
        or evidence["algorithm_mode"] != config["algorithm_mode"]
        or evidence["host_poll_interval_ms"] != config["poll_interval_ms"]
        or evidence["valid_samples"] + evidence["invalid_samples"] != evidence["observed_samples"]
        or (last is None) != (evidence["observed_samples"] == 0)
        or last is not None and (not start <= last["host_received_monotonic_us"] < end or last["sequence"] != evidence["observed_samples"] - 1)):
        raise Problem(422, "VENDOR_CONFIGURATION_MISMATCH")
    if projection["status"] == "valid":
        if (last is None or evidence["hub_firmware"] != {x: config["hub_firmware_" + x] for x in ("major", "minor", "revision")} or evidence["configured_sensor_rate_hz"] is None or evidence["invalid_samples"] != 0 or evidence["missed_poll_intervals"] != 0
            or end <= start or evidence["valid_samples"] < config["minimum_valid_samples"]
            or last["finger_status"] != 3 or last["confidence_percent"] > 100 or last["confidence_percent"] < config["minimum_confidence"]
            or not config["minimum_heart_rate_bpm"] <= last["heart_rate_bpm"] <= config["maximum_heart_rate_bpm"]
            or (end - last["host_received_monotonic_us"]) / 1000 > config["max_no_data_ms"]
            or projection["heart_rate_bpm"] != last["heart_rate_bpm"]
            or projection["ecg_rmssd_ms"] is not None or projection["ecg_status"] != "not_collected"
            or projection["sample_rate_hz"] is not None or projection["raw_artifact_id"] is not None):
            raise Problem(422, "VENDOR_MEASUREMENT_INVALID")
    elif projection["heart_rate_bpm"] is not None:
        raise Problem(422, "INVALID_VENDOR_HEART_RATE")
    if not {"SERVER_WALL_ANCHOR_UNQUALIFIED", "SPARKFUN_SENSOR_BPM_V1", "HOST_I2C_RECEIVE_TIMESTAMPS_UNQUALIFIED"}.issubset(set(projection.get("quality_flags", []))):
        raise Problem(422, "VENDOR_UNQUALIFIED_EVIDENCE_REQUIRED")
    if projection["source"] != "prototype_sensor" or projection["modality"] != "ppg":
        raise Problem(422, "VENDOR_PROVENANCE_INVALID")
    return evidence
