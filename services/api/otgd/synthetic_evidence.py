"""Bounded, independently checked software-peripheral evidence.

This format accepts only the fixed fictional bench fixture. CRC, clock intervals,
Bluetooth connectivity, and these hashes confer no physiological qualification.
"""

from datetime import datetime
from math import isclose
from typing import Annotated, Literal

from pydantic import Field

from .canonical import canonical, digest
from .dto import DTO, SHA, UTC, UUID, Name
from .errors import Problem

Channel = Literal["ppg", "ecg", "saliva"]
Nonnegative = Annotated[float, Field(ge=0, le=9007199254740991)]
SafeInteger = Annotated[int, Field(ge=0, le=9007199254740991)]


class SyntheticCapabilities(DTO):
    protocol_version: Literal[1]
    encodings: Annotated[list[Literal[1]], Field(min_length=1, max_length=1)]
    max_logical_bytes: Literal[8192]
    max_att_bytes: Annotated[int, Field(ge=20, le=512)]
    source: Literal["simulated"]
    device_id: Annotated[str, Field(min_length=1, max_length=64)]
    boot_id: UUID
    hardware_revision: Annotated[str, Field(min_length=1, max_length=64)]
    firmware_version: Annotated[str, Field(min_length=1, max_length=32)]
    channels: Annotated[list[Channel], Field(min_length=1, max_length=3)]
    configuration_id: Literal["synthetic_bench_v1"]
    calibration_status: Literal["not_applicable"]
    timestamp_resolution_ms: Annotated[float, Field(gt=0, le=1000)]


class Association(DTO):
    peripheralId: Name
    deviceId: Name
    bootId: UUID
    hardwareRevision: Name
    firmwareVersion: Name
    protocolVersion: Literal[1]
    source: Literal["simulated"]
    verifiedBindingId: None
    transport: Literal["ble_unprovisioned", "local_simulator"]
    capabilities: SyntheticCapabilities


class SyntheticContext(DTO):
    sessionId: UUID
    attemptId: UUID
    captureId: UUID
    workspaceEpoch: Annotated[str, Field(min_length=1, max_length=128)]


class ClockExchange(DTO):
    phone_send_ms: Nonnegative
    device_receive_ms: Nonnegative
    device_send_ms: Nonnegative
    phone_receive_ms: Nonnegative
    phone_timestamp_resolution_ms: Annotated[float, Field(gt=0, le=1000)]
    device_timestamp_resolution_ms: Annotated[float, Field(gt=0, le=1000)]
    offset_lower_ms: float
    offset_upper_ms: float
    round_trip_ms: Nonnegative


class ClockEvidence(DTO):
    policy_id: Literal["synthetic_interval_v1"]
    source: Literal["simulated"]
    boot_id: UUID
    exchanges: Annotated[list[ClockExchange], Field(min_length=3, max_length=3)]
    selected_exchange: Annotated[int, Field(ge=0, le=2)]
    offset_ms: float
    uncertainty_ms: Nonnegative
    calibrated: Literal[False]


class Ppg(DTO):
    heart_rate_bpm: Nonnegative
    duration_seconds: Nonnegative
    method: Literal["ppg"]


class Ecg(DTO):
    heart_rate_bpm: Nonnegative
    duration_seconds: Nonnegative
    method: Literal["ecg"]
    sample_rate_hz: Nonnegative
    lead_count: Literal[1]
    units: Literal["arbitrary_counts"]
    samples: Annotated[list[float], Field(min_length=200, max_length=200)]


class Analyte(DTO):
    analyte: Literal["delta9_thc", "11_hydroxy_thc", "thc_cooh"]
    qualifier: Literal["quantified", "not_detected"]
    value: Nonnegative | None
    unit: Literal["ng/mL"]
    lod: Nonnegative
    loq: Nonnegative
    uloq: Nonnegative


class Saliva(DTO):
    specimen: Literal["oral_fluid"]
    assay_id: Literal["synthetic_assay_v1"]
    analytes: Annotated[list[Analyte], Field(min_length=3, max_length=3)]


Values = Ppg | Ecg | Saliva


class Ack(DTO):
    ack_message_id: UUID
    status: Literal["accepted"]


class Hello(DTO):
    request_message_id: UUID
    source: Literal["simulated"]
    configuration_id: Literal["synthetic_bench_v1"]


class ClockReply(DTO):
    request_message_id: UUID
    phone_send_ms: Nonnegative
    device_receive_ms: Nonnegative
    device_send_ms: Nonnegative


class Complete(DTO):
    source: Literal["simulated"]
    channel: Channel
    attempt_id: UUID
    capture_id: UUID
    workspace_epoch: Annotated[str, Field(min_length=1, max_length=128)]
    started_monotonic_ms: Nonnegative
    ended_monotonic_ms: Nonnegative
    fixture_id: Literal["synthetic_bench_v1"]
    values: Values


class Message(DTO):
    protocol_version: Literal[1]
    message_id: UUID
    device_id: Name
    boot_id: UUID
    session_id: UUID
    sequence: SafeInteger
    monotonic_ms: Nonnegative
    type: Literal["ack", "hello", "clock_sync", "capture_complete"]
    payload: dict


class SyntheticDeviceCapture(DTO):
    source: Literal["simulated"]
    channel: Channel
    context: SyntheticContext
    association: Association
    clockEvidence: ClockEvidence
    startedAt: UTC
    endedAt: UTC
    deviceStartedMonotonicMs: Nonnegative
    deviceEndedMonotonicMs: Nonnegative
    values: Values
    fixtureId: Literal["synthetic_bench_v1"]
    messages: Annotated[list[Message], Field(min_length=10, max_length=32)]
    evidenceSha256: SHA
    qualityFlags: Annotated[
        list[Literal["SIMULATED", "UNVERIFIED_DEVICE"]],
        Field(min_length=2, max_length=2),
    ]
    modelEligible: Literal[False]


def synthetic_values(channel):
    if channel == "ppg":
        return dict(heart_rate_bpm=72, duration_seconds=3, method="ppg")
    if channel == "ecg":

        def sample(i):
            p = i % 42
            return (
                800
                if p == 10
                else -250
                if p == 11
                else ((p - 19 if p <= 22 else 26 - p) * 25)
                if 20 <= p <= 25
                else 30
                if 4 <= p <= 6
                else 0
            )

        return dict(
            heart_rate_bpm=72,
            duration_seconds=4,
            method="ecg",
            sample_rate_hz=50,
            lead_count=1,
            units="arbitrary_counts",
            samples=[sample(i) for i in range(200)],
        )
    return dict(
        specimen="oral_fluid",
        assay_id="synthetic_assay_v1",
        analytes=[
            dict(
                analyte=name,
                qualifier="quantified" if i == 0 else "not_detected",
                value=12 if i == 0 else None,
                unit="ng/mL",
                lod=1,
                loq=2,
                uloq=100,
            )
            for i, name in enumerate(("delta9_thc", "11_hydroxy_thc", "thc_cooh"))
        ],
    )


def same_number(a, b):
    if not isclose(a, b, rel_tol=0, abs_tol=1e-6):
        raise Problem(422, "SYNTHETIC_CLOCK_MISMATCH")


def validate_synthetic(raw, attempt, projection):
    value = SyntheticDeviceCapture.model_validate(raw)
    if attempt["source"] != "simulated" or attempt["status"] != "valid":
        raise Problem(422, "SYNTHETIC_PROVENANCE_REQUIRED")
    if (
        digest({k: v for k, v in raw.items() if k != "evidenceSha256"})
        != value.evidenceSha256
    ):
        raise Problem(422, "SYNTHETIC_DIGEST_MISMATCH")
    context, association = value.context, value.association
    caps, clock = association.capabilities, value.clockEvidence
    expected_component = "saliva" if value.channel == "saliva" else "cardiac"
    if (
        context.sessionId,
        context.attemptId,
        context.captureId,
        expected_component,
    ) != (
        attempt["session_id"],
        attempt["attempt_id"],
        attempt["record_id"],
        attempt["component"],
    ):
        raise Problem(422, "SYNTHETIC_IDENTITY_MISMATCH")
    if attempt["configuration_id"] != value.fixtureId or attempt[
        "configuration_hash"
    ] != digest({"fixture": value.fixtureId, "channel": value.channel}):
        raise Problem(422, "SYNTHETIC_CONFIGURATION_MISMATCH")
    if (
        association.deviceId,
        association.bootId,
        association.hardwareRevision,
        association.firmwareVersion,
    ) != (
        caps.device_id,
        caps.boot_id,
        caps.hardware_revision,
        caps.firmware_version,
    ) or clock.boot_id != caps.boot_id:
        raise Problem(422, "SYNTHETIC_ASSOCIATION_MISMATCH")
    if (
        len(set(caps.channels)) != len(caps.channels)
        or value.channel not in caps.channels
        or value.qualityFlags != ["SIMULATED", "UNVERIFIED_DEVICE"]
    ):
        raise Problem(422, "SYNTHETIC_CAPABILITY_MISMATCH")
    if digest(raw["values"]) != digest(synthetic_values(value.channel)):
        raise Problem(422, "SYNTHETIC_FIXTURE_MISMATCH")
    if (
        not 0
        <= (
            datetime.fromisoformat(value.endedAt)
            - datetime.fromisoformat(value.startedAt)
        ).total_seconds()
        <= 120
        or not 0
        <= value.deviceEndedMonotonicMs - value.deviceStartedMonotonicMs
        <= 30000
        or value.endedAt != attempt["ended_at"]
    ):
        raise Problem(422, "SYNTHETIC_CAPTURE_TIME")
    for exchange in clock.exchanges:
        if (
            exchange.phone_receive_ms < exchange.phone_send_ms
            or exchange.device_send_ms < exchange.device_receive_ms
            or exchange.offset_upper_ms < exchange.offset_lower_ms
        ):
            raise Problem(422, "SYNTHETIC_CLOCK_MISMATCH")
        pad = (
            exchange.phone_timestamp_resolution_ms
            + exchange.device_timestamp_resolution_ms
        )
        same_number(
            exchange.offset_lower_ms,
            exchange.device_send_ms - exchange.phone_receive_ms - pad,
        )
        same_number(
            exchange.offset_upper_ms,
            exchange.device_receive_ms - exchange.phone_send_ms + pad,
        )
        same_number(
            exchange.round_trip_ms, exchange.phone_receive_ms - exchange.phone_send_ms
        )
        same_number(
            exchange.device_timestamp_resolution_ms, caps.timestamp_resolution_ms
        )
    selected = min(
        range(3),
        key=lambda i: (
            clock.exchanges[i].offset_upper_ms - clock.exchanges[i].offset_lower_ms
        ),
    )
    if selected != clock.selected_exchange:
        raise Problem(422, "SYNTHETIC_CLOCK_MISMATCH")
    exchange = clock.exchanges[selected]
    same_number(
        clock.offset_ms, (exchange.offset_lower_ms + exchange.offset_upper_ms) / 2
    )
    same_number(
        clock.uncertainty_ms, (exchange.offset_upper_ms - exchange.offset_lower_ms) / 2
    )
    ids, last_sequence, acknowledgments, replies = set(), -1, set(), []
    hello_count = 0
    for raw_message, message in zip(raw["messages"], value.messages):
        if (
            len(canonical(raw_message)) + 4 > 8192
            or message.message_id in ids
            or message.sequence <= last_sequence
            or (message.device_id, message.boot_id, message.session_id)
            != (caps.device_id, caps.boot_id, context.sessionId)
        ):
            raise Problem(422, "SYNTHETIC_MESSAGE_IDENTITY")
        ids.add(message.message_id)
        last_sequence = message.sequence
        payload_type = {
            "ack": Ack,
            "hello": Hello,
            "clock_sync": ClockReply,
            "capture_complete": Complete,
        }[message.type]
        p = payload_type.model_validate(message.payload)
        if message.type == "ack":
            if p.ack_message_id in acknowledgments:
                raise Problem(422, "SYNTHETIC_ACK_REPLAY")
            acknowledgments.add(p.ack_message_id)
        elif message.type in ("hello", "clock_sync"):
            if p.request_message_id not in acknowledgments:
                raise Problem(422, "SYNTHETIC_REPLY_WITHOUT_ACK")
            if message.type == "hello":
                hello_count += 1
            else:
                replies.append(p)
        else:
            if (
                message is not value.messages[-1]
                or (
                    p.channel,
                    p.attempt_id,
                    p.capture_id,
                    p.workspace_epoch,
                    p.started_monotonic_ms,
                    p.ended_monotonic_ms,
                )
                != (
                    value.channel,
                    context.attemptId,
                    context.captureId,
                    context.workspaceEpoch,
                    value.deviceStartedMonotonicMs,
                    value.deviceEndedMonotonicMs,
                )
                or digest(message.payload["values"]) != digest(raw["values"])
            ):
                raise Problem(422, "SYNTHETIC_COMPLETION_MISMATCH")
    if (
        hello_count != 1
        or len(replies) != 3
        or len(acknowledgments) != 5
        or value.messages[-1].type != "capture_complete"
    ):
        raise Problem(422, "SYNTHETIC_TRANSCRIPT_INCOMPLETE")
    for reply, exchange in zip(replies, clock.exchanges):
        for key in ("phone_send_ms", "device_receive_ms", "device_send_ms"):
            same_number(getattr(reply, key), getattr(exchange, key))
    if value.channel == "saliva":
        names = {
            "delta9_thc": "THC",
            "11_hydroxy_thc": "OH11_THC",
            "thc_cooh": "THC_COOH",
        }
        expected = synthetic_values("saliva")["analytes"]
        if (
            projection["sample"]["collected_at"] != value.startedAt
            or len(projection["saliva"]) != 3
        ):
            raise Problem(422, "SYNTHETIC_PROJECTION_MISMATCH")
        for result, analyte in zip(projection["saliva"], expected):
            if (
                result["analyte"],
                result["qualifier"],
                result["value_ng_ml"],
                result["collected_at"],
                result["measured_at"],
                result["instrument_id"],
            ) != (
                names[analyte["analyte"]],
                analyte["qualifier"],
                analyte["value"],
                value.startedAt,
                value.endedAt,
                association.deviceId,
            ) or result["limits"] != {
                "lod_ng_ml": analyte["lod"],
                "loq_ng_ml": analyte["loq"],
                "upper_ng_ml": analyte["uloq"],
            }:
                raise Problem(422, "SYNTHETIC_PROJECTION_MISMATCH")
    else:
        if (
            projection["modality"],
            projection["heart_rate_bpm"],
            projection["started_at"],
            projection["ended_at"],
            projection["ecg_rmssd_ms"],
        ) != (value.channel, 72, value.startedAt, value.endedAt, None) or projection[
            "sample_rate_hz"
        ] != (50 if value.channel == "ecg" else None):
            raise Problem(422, "SYNTHETIC_PROJECTION_MISMATCH")
