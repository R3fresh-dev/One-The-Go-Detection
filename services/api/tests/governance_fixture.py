"""Fictional software approvals ONLY; never loaded by deployment or the CLI."""

import base64
import hashlib

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from otgd.db import now
from otgd.canonical import digest
from otgd.native_evidence import CONFIG
from otgd.operator_governance import Configuration, submit, transition

STUDY = "fictional-governance-study"
PROTOCOL = "fictional-governance-protocol"
POLICY = "fictional-governance-retention"
CONFIGURATION = "fictional-governance-task"
PROOF = "fictional-governance-qualification"
DEVICE = "fictional-device"
KEY = "fixture-key"
CALIBRATION = "fictional-calibration"


def common(id, **fields):
    return {"schema_version": "1.0.0", "registry_id": id, "version": "v1",
        "expires_at": now() + 86400, "evidence_ref": "FICTIONAL-SOFTWARE-FIXTURE-NO-HUMAN-APPROVAL",
        "evidence_sha256": "1" * 64, **fields}


def study(account, channels=None):
    text = "Fictional consent software fixture; this is not a real approved study."
    return common(STUDY, study_id=STUDY, protocol_id=PROTOCOL, name="Fictional study",
        account_refs=[account], invitation_id="fictional-invitation", document_version="v1",
        document_text=text, document_sha256=hashlib.sha256(text.encode()).hexdigest(),
        retention_summary="Fictional software test policy", channels=channels or {"task": CONFIGURATION})


def retention(**changes):
    text = "Fictional optional raw recording notice for software tests only."
    value = common(POLICY, policy_id=POLICY, study_id=STUDY,
        raw_kinds=["eye_video", "ecg_waveform", "source_lab_report"], max_retention_days=30,
        access_roles=["study_operator"], withdrawal_behavior="delete_live_data", exceptions=[],
        purpose_id="fictional-software-purpose", purpose_text="Fictional software recording",
        raw_notice_version="v1", raw_notice_sha256=hashlib.sha256(text.encode()).hexdigest(),
        raw_notice_text=text)
    value.update(changes)
    return value


def proof(channel="task", config_body=None):
    config = Configuration.model_validate(config_body or configuration(channel)).data()
    return common(PROOF + "-" + channel, channel=channel, configuration_sha256=config["sha256"],
        document_sha256="2" * 64, reviewed_by="Fictional independent evidence scientist",
        approval_status="approved", purpose="measurement_collection",
        configuration_registry_id=config["registry_id"], configuration_version=config["version"],
        configuration_submitted_sha256=digest(config))


def configuration(channel="task", **changes):
    id = CONFIGURATION if channel == "task" else "fictional-" + channel + "-configuration"
    material = CONFIG if channel == "task" else {
        "schema_version": "1.0.0", "channel": channel, "modality": "ppg" if channel == "cardiac" else "ecg" if channel == "ecg" else "breath_alcohol",
        "protocol_version": 1, "duration_ms": 150000, "sample_rate_hz": 100.0,
        "raw_unit": "counts" if channel == "cardiac" else "mV" if channel == "ecg" else "mg/L",
        "extractor_version": "fictional-software-extractor",
    }
    if channel == "eyes":
        material = {"schema_version": "1.0.0", "channel": "eyes", "duration_ms": 150000,
            "camera_id": "fixture-camera", "stimulus_policy_id": "fixture-stimulus", "illumination_policy_id": "fixture-illumination",
            "geometry_id": "fixture-geometry", "frame_rate_hz": 30.0, "extractor_version": "fixture-optical-extractor"}
    value = common(id, configuration_id=id, study_id=STUDY, protocol_id=PROTOCOL,
        channel=channel, sha256=digest(material), material=material, qualification_evidence_ref=PROOF + "-" + channel,
        retention_policy_id=POLICY, max_duration_ms=150000,
        software_adapter_id="task_native_v1" if channel == "task" else "unimplemented-" + channel,
        supported_phone_models=["FICTIONAL-PHONE"] if channel in ("task", "eyes") else [])
    value.update(changes)
    return value


def device(account, private_key=None):
    key = private_key or ec.generate_private_key(ec.SECP256R1())
    spki = key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    return common(DEVICE + ":" + KEY, device_id=DEVICE, key_id=KEY,
        public_key_spki=base64.b64encode(spki).decode(), hardware_revision="fixture-hw",
        firmware_version="fixture-fw", approved_protocol_ids=[PROTOCOL], account_refs=[account])


def calibration():
    return common(CALIBRATION, calibration_id=CALIBRATION, purpose="device",
        device_id=DEVICE, key_id=KEY, hardware_revision="fixture-hw",
        firmware_versions=["fixture-fw"], channels=["cardiac", "ecg", "saliva"],
        calibration_sha256="3" * 64)


def adc_material(channel="cardiac"):
    """Fictional electrical fixture values, never a sensor recommendation."""
    return {"schema_version": "1.0.0", "channel": channel, "modality": "ppg" if channel == "cardiac" else "ecg",
        "adapter_id": "otgd_esp32_adc_v1", "protocol_version": 1, "duration_ms": 15000,
        "end_guard_ms": 50, "sample_rate_hz": 100, "raw_unit": "counts",
        "raw_sample_limit": 0, "raw_encoding": None,
        "extractor_version": "adc_peak_intervals_v1", "input_gpio": 1, "contact_gpio": 4,
        "contact_active_high": True, "adc_resolution_bits": 12, "attenuation_db": 11,
        "reference_mv": 3300.0, "gain": 1.0, "offset_mv": 0.0, "threshold_adc": 2048,
        "minimum_peak_interval_ms": 250, "maximum_peak_interval_ms": 2000, "minimum_amplitude_adc": 100}


def approve(db, kind, body):
    """Execute the real typed lifecycle under explicit fictional principals."""
    submitted = submit(db, kind, body, "local:fixture-submitter")
    transition(db, kind, body["registry_id"], body["version"], "approve",
        "local:fixture-reviewer", "Fictional software fixture review", submitted["revision"])
    db.flush()
    return transition(db, kind, body["registry_id"], body["version"], "release",
        "local:fixture-releaser", "Fictional software fixture release", 2)


def approve_task(db, account):
    config = configuration()
    for kind, body in (("study", study(account)), ("retention", retention()),
        ("qualification", proof(config_body=config)), ("configuration", config)):
        approve(db, kind, body)
