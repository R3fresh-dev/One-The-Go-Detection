import base64
import hashlib
import sys
from datetime import datetime

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils
from sqlalchemy import select

from .canonical import canonical, digest
from .config import ROOT, settings
from .db import Check, Record, Registry, RegistryVersion, SystemState, iso, now, uid
from .errors import Problem

sys.path.insert(0, str(ROOT / "tools"))
from spec_validation import validate_manifest as validate_manifest
from spec_validation import validate_measurement, validate_schema, validate_session

NOTICE = "This application records measurements and research practice. Cannabinoid detection, pulse, pupil appearance, and reaction performance do not establish current intoxication. Clinical inference is unavailable. Do not use these results to decide whether to drive. Guest demonstration records remain on this device. Account uploads require your explicit action. Exported copies already shared cannot be recalled. You can review, export, and request deletion of your account data."
NOTICE_SHA = hashlib.sha256(NOTICE.encode()).hexdigest()
NOTICE_VERSION = "v1"


def notice():
    return {
        "version": NOTICE_VERSION,
        "sha256": NOTICE_SHA,
        "locale": "en",
        "content_path": "/v1/notices/" + NOTICE_VERSION,
        "mandatory": True,
    }


def owned_check(db, account, id):
    row = db.scalar(
        select(Check)
        .where(
            Check.id == id,
            Check.account_id == account.id,
            Check.generation == account.generation,
        )
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if not row:
        raise Problem(404, "NOT_FOUND")
    return row


def rec_id(account, kind, key):
    return account.id + ":" + kind + ":" + key


def record(db, account, kind, key):
    row = db.get(Record, rec_id(account, kind, key))
    return row if row and row.generation == account.generation else None


def if_match(request, revision):
    value = request.headers.get("if-match")
    if value is None:
        raise Problem(428, "PRECONDITION_REQUIRED")
    if value != '"' + str(revision) + '"':
        raise Problem(412, "REVISION_CONFLICT", revision=revision)


def save_record(db, account, kind, key, data, parent=None, revision=1):
    row = Record(
        id=rec_id(account, kind, key),
        account_id=account.id,
        generation=account.generation,
        kind=kind,
        parent_id=parent,
        body=data,
        sha256=digest(data),
        revision=revision,
    )
    db.add(row)
    return row


def require_draft(check):
    if check.state != "draft":
        raise Problem(409, "STATE_CONFLICT")


def registry(db, kind, id):
    from .operator_governance import authority_lock, released_version

    authority_lock(db)
    value = db.scalar(
        select(Registry).where(Registry.id == kind + ":" + id)
        .with_for_update(read=True).execution_options(populate_existing=True)
    )
    if not value or not value.active or value.kind != kind:
        raise Problem(403, "CAPABILITY_DENIED")
    if db.scalar(select(RegistryVersion.id).where(RegistryVersion.registry_key == value.id).limit(1)):
        released_version(db, kind, id)
    elif value.body.get("expires_at") is not None and value.body["expires_at"] <= now():
        raise Problem(403, "CAPABILITY_DENIED")
    return value.body


def qualification(
    db, account, check, channel, configuration_id=None, configuration_hash=None
):
    recovery = db.get(SystemState, "recovery")
    if recovery:
        from .recovery_scopes import require_study_scope
        require_study_scope(db,check.study_id,account)
    if not check.study_id:
        raise Problem(403, "QUALIFIED_CHANNEL_UNAVAILABLE")
    study = registry(db, "study", check.study_id)
    if study.get("protocol_id") is not None and check.protocol_id != study["protocol_id"]:
        raise Problem(403, "CONFIGURATION_MISMATCH")
    consent = record(db, account, "consent", check.study_id)
    if (
        not consent
        or consent.body.get("state") != "active"
        or account.id not in study.get("account_refs", [])
    ):
        raise Problem(403, "CAPABILITY_DENIED")
    if any(not isinstance(study.get(field), str) or not study[field]
        or consent.body.get(field) != study[field] for field in (
        "document_sha256", "document_version", "invitation_id"
    )):
        raise Problem(403, "CURRENT_CONSENT_REQUIRED")
    if configuration_id is None:
        configuration_id = study.get("channels", {}).get(channel)
    if not configuration_id:
        raise Problem(403, "QUALIFIED_CHANNEL_UNAVAILABLE")
    config = registry(db, "configuration", configuration_id)
    if (
        config.get("channel") != channel
        or config.get("study_id") != check.study_id
        or not config.get("qualification_evidence_ref")
        or not config.get("retention_policy_id")
        or config.get("expires_at", 0) <= now()
    ):
        raise Problem(403, "QUALIFIED_CHANNEL_UNAVAILABLE")
    evidence = registry(db, "qualification", config["qualification_evidence_ref"])
    if (
        evidence.get("approval_status") != "approved"
        or evidence.get("configuration_sha256") != config.get("sha256")
        or evidence.get("channel") != channel
        or not evidence.get("document_sha256")
        or not evidence.get("reviewed_by")
        or evidence.get("expires_at", 0) <= now()
    ):
        raise Problem(403, "QUALIFICATION_EVIDENCE_UNAVAILABLE")
    if configuration_hash is not None and config.get("sha256") != configuration_hash:
        raise Problem(403, "CONFIGURATION_MISMATCH")
    if config.get("schema_version") == "1.0.0":
        from .operator_governance import validate_dependencies
        validate_dependencies(db, "configuration", config)
    return config


def check_scientific_snapshot(snapshot, account, check):
    validate_session(snapshot)
    if (
        snapshot["session_id"] != check.id
        or snapshot["mode"] != check.mode
        or snapshot["study_id"] != check.study_id
        or snapshot["protocol_id"] != check.protocol_id
        or snapshot["supersedes_session_id"] != check.supersedes_id
    ):
        raise Problem(422, "SNAPSHOT_IDENTITY_MISMATCH")
    if snapshot["subject_ref"] != account.id:
        raise Problem(422, "SUBJECT_MISMATCH")
    if snapshot["created_at"] != snapshot["target_at"]:
        raise Problem(422, "CONTEXT_FREEZE_MISMATCH")
    if snapshot["task"]["status"] == "invalid" and any(
        v is not None for v in snapshot["task"]["features"].values()
    ):
        raise Problem(422, "INVALID_TASK_FEATURES")
    if check.mode == "synthetic":
        if settings().environment == "prod":
            raise Problem(403, "SYNTHETIC_CLOUD_UNAVAILABLE")
        sources = [v["source"] for v in snapshot["saliva"]] + [
            snapshot[v]["source"] for v in ("eyes", "cardiac", "task")
        ]
        if (
            any(v != "simulated" for v in sources)
            or snapshot["profile"]["source"] != "synthetic"
        ):
            raise Problem(422, "SYNTHETIC_PROVENANCE_REQUIRED")


def validate_component(attempt):
    metadata = attempt["component_metadata"]
    component = attempt["component"]
    common = {"projection", "armed_at", "fixture_id", "transport_evidence"}
    fields = {
        "saliva": {
            "collector_id",
            "collector_lot",
            "cartridge_lot",
            "adequacy",
            "volume_ml",
            "dilution_factor",
            "collected_at",
            "analysis_at",
            "source_report_artifact_id",
            "correction_reason",
            "original_report",
            "laboratory_id",
            "lab_import_id",
            "collection_method_version",
            "saliva_volume_ml",
            "buffer_volume_ml",
            "dilution_definition",
            "container_id",
            "cartridge_expiry",
            "operator_ref",
            "collection_attempt_id",
            "analysis_attempt_id",
            "storage_handling_events",
        },
        "eyes": {
            "native_result",
            "camera_id",
            "geometry_id",
            "illumination_id",
            "scale_basis",
            "frame_timing",
            "segmentation_version",
            "capture_config_id",
        },
        "cardiac": {
            "modality",
            "sample_rate_hz",
            "gain",
            "scaling",
            "contact",
            "filter_version",
            "dropped_samples",
            "context",
            "acquisition_config_id",
        },
        "task": {
            "native_result",
            "extractor_version",
            "timing_method",
            "contract_fixture",
        },
        "alcohol": {"measurement_id"},
    }
    if (
        any(k in metadata for k in ("fixture_id", "transport_evidence"))
        and attempt["source"] != "simulated"
    ):
        raise Problem(422, "SYNTHETIC_PROVENANCE_REQUIRED")
    if metadata.get("fixture_id") is not None and (
        not isinstance(metadata["fixture_id"], str)
        or not 1 <= len(metadata["fixture_id"]) <= 128
    ):
        raise Problem(422, "INVALID_COMPONENT_METADATA")
    if metadata.get("armed_at") is not None:
        from .dto import valid_utc

        valid_utc(metadata["armed_at"])
    if set(metadata) - common - fields[component]:
        raise Problem(422, "UNKNOWN_COMPONENT_METADATA")
    if component == "cardiac" and (
        ("modality" in metadata and metadata["modality"] not in ("ppg", "ecg"))
        or (
            attempt["status"] == "started"
            and metadata.get("modality") not in ("ppg", "ecg")
        )
    ):
        raise Problem(422, "CARDIAC_MODALITY_REQUIRED")
    if attempt["status"] == "started":
        if metadata.get("projection") is not None:
            raise Problem(422, "STARTED_HAS_NO_RESULT")
        return
    p = metadata.get("projection")
    if not isinstance(p, dict):
        raise Problem(422, "PROJECTION_REQUIRED")
    if component == "saliva":
        if set(p) != {"sample", "saliva"}:
            raise Problem(422, "INVALID_SALIVA_PROJECTION")
        for m in p["saliva"]:
            validate_measurement(m)
        if any(m["source"] != attempt["source"] for m in p["saliva"]):
            raise Problem(422, "PROVENANCE_MISMATCH")
        if p["sample"]["sample_id"] != attempt["record_id"] or p["sample"][
            "status"
        ] != ("invalid" if attempt["status"] == "canceled" else attempt["status"]):
            raise Problem(422, "PROJECTION_MISMATCH")
    elif component == "alcohol":
        from .dto import Alcohol

        Alcohol.model_validate(p)
        status = (
            "not_collected"
            if p["qualifier"] == "not_measured"
            else "invalid"
            if p["qualifier"] == "invalid"
            else "valid"
        )
        expected_status = (
            "invalid" if attempt["status"] == "canceled" else attempt["status"]
        )
        if (
            p["measurement_id"] != attempt["record_id"]
            or p["session_id"] != attempt["session_id"]
            or p["source"] != attempt["source"]
            or status != expected_status
        ):
            raise Problem(422, "PROJECTION_MISMATCH")
    else:
        import json

        schema = json.loads((ROOT / "contracts/session.schema.json").read_text())[
            "properties"
        ][component]
        from jsonschema import Draft202012Validator, FormatChecker

        Draft202012Validator(schema, format_checker=FormatChecker()).validate(p)
        status = "invalid" if attempt["status"] == "canceled" else attempt["status"]
        if (
            p["source"] != attempt["source"]
            or p["status"] != status
            or p["started_at"] != attempt["started_at"]
            or p["ended_at"] != attempt["ended_at"]
        ):
            raise Problem(422, "PROJECTION_MISMATCH")
        if (component == "eyes" and attempt["status"] in ("invalid", "canceled")
            and metadata.get("native_result") is None
            and any(p[key] is not None for key in ("baseline_diameter_mm", "relative_constriction", "latency_ms"))):
            raise Problem(422, "INVALID_OPTICAL_FEATURES")
        if component == "task" and p["task_id"] != attempt["record_id"]:
            raise Problem(422, "PROJECTION_MISMATCH")
        if (
            component == "task"
            and attempt["configuration_hash"] is not None
            and p["config_sha256"] != attempt["configuration_hash"]
        ):
            raise Problem(422, "TASK_CONFIGURATION_MISMATCH")
        if (
            component == "cardiac"
            and "modality" in metadata
            and metadata["modality"] != p["modality"]
        ):
            raise Problem(422, "CARDIAC_MODALITY_MISMATCH")
    # Metadata is structured and bounded. Never permit raw media or free-form nested streams.
    for key, value in metadata.items():
        if key in (
            "projection",
            "native_result",
            "original_report",
            "frame_timing",
            "storage_handling_events",
            "transport_evidence",
        ):
            continue
        if isinstance(value, (dict, list)):
            raise Problem(422, "INVALID_COMPONENT_METADATA")
        if isinstance(value, str) and len(value) > 256:
            raise Problem(422, "INVALID_COMPONENT_METADATA")
    if "storage_handling_events" in metadata:
        events = metadata["storage_handling_events"]
        if not isinstance(events, list) or len(events) > 64:
            raise Problem(422, "INVALID_HANDLING_EVENTS")
        for event in events:
            if (
                not isinstance(event, dict)
                or set(event)
                - {
                    "event",
                    "occurred_at",
                    "operator_ref",
                    "temperature_c",
                    "duration_min",
                    "configuration_ref",
                }
                or any(
                    isinstance(v, (list, dict)) or isinstance(v, str) and len(v) > 256
                    for v in event.values()
                )
            ):
                raise Problem(422, "INVALID_HANDLING_EVENTS")
    for field in (
        "volume_ml",
        "saliva_volume_ml",
        "buffer_volume_ml",
        "dilution_factor",
    ):
        if metadata.get(field) is not None and (
            isinstance(metadata[field], bool)
            or not isinstance(metadata[field], (int, float))
            or metadata[field] < 0
        ):
            raise Problem(422, "INVALID_VOLUME")
    if "original_report" in metadata and (
        not isinstance(metadata["original_report"], dict)
        or set(metadata["original_report"])
        - {"value", "unit", "qualifier", "report_id"}
    ):
        raise Problem(422, "INVALID_COMPONENT_METADATA")
    if "frame_timing" in metadata and (
        not isinstance(metadata["frame_timing"], dict)
        or set(metadata["frame_timing"])
        - {
            "first_timestamp_ms",
            "last_timestamp_ms",
            "frame_count",
            "dropped_frames",
            "maximum_gap_ms",
        }
    ):
        raise Problem(422, "INVALID_COMPONENT_METADATA")
    if "contract_fixture" in metadata and (
        metadata["contract_fixture"] is not True
        or settings().environment == "prod"
        or not isinstance(metadata.get("native_result"), dict)
        or not isinstance(metadata["native_result"].get("timing"), dict)
        or metadata["native_result"]["timing"].get("simulator") is not True
    ):
        raise Problem(422, "CONTRACT_FIXTURE_SCOPE")
    if metadata.get("transport_evidence") is not None:
        from .synthetic_evidence import validate_synthetic

        validate_synthetic(metadata["transport_evidence"], attempt, p)
    if component == "task" and metadata.get("native_result") is not None:
        from .native_evidence import validate_native

        validate_native(metadata["native_result"], p)


def verify_evidence(db, account, check):
    context = record(db, account, "context", check.id)
    manifest = record(db, account, "manifest", check.id)
    if not context or not manifest or not check.snapshot:
        raise Problem(422, "EVIDENCE_INCOMPLETE")
    snapshot = check.snapshot
    data = manifest.body
    if (
        data["context_sha256"] != context.sha256
        or context.body["profile_snapshot_sha256"] != digest(snapshot["profile"])
        or context.body["history_snapshot_sha256"] != digest(snapshot["history"])
        or context.body["context_confirmed_at"] != snapshot["target_at"]
    ):
        raise Problem(422, "CONTEXT_DIGEST_MISMATCH")
    if context.body["protocol_id"] != snapshot["protocol_id"]:
        raise Problem(422, "CONTEXT_PROTOCOL_MISMATCH")
    if context.body.get("profile_version_id"):
        profile = record(
            db, account, "profile_version", context.body["profile_version_id"]
        )
        if not profile or digest(profile.body["profile"]) != digest(
            snapshot["profile"]
        ):
            raise Problem(422, "PROFILE_VERSION_MISMATCH")
    report = context.body.get("self_report_context")
    if report:
        if report["last_use_status"] == "known":
            target = datetime.fromisoformat(snapshot["target_at"])
            last = datetime.fromisoformat(report["last_use_at"])
            elapsed = (target - last).total_seconds() / 60
            if (
                elapsed < 0
                or snapshot["history"]["time_since_use_min"] is None
                or abs(elapsed - snapshot["history"]["time_since_use_min"]) > 1 / 60
            ):
                raise Problem(422, "SELF_REPORT_TIME_MISMATCH")
        elif snapshot["history"]["time_since_use_min"] is not None:
            raise Problem(422, "SELF_REPORT_TIME_MISMATCH")
    actual = list(
        db.scalars(
            select(Record).where(
                Record.account_id == account.id,
                Record.generation == account.generation,
                Record.kind == "attempt",
                Record.parent_id == check.id,
            )
        )
    )
    ids = {x.body["attempt_id"]: x for x in actual}
    if set(ids) != {x["attempt_id"] for x in data["attempts"]}:
        raise Problem(422, "ATTEMPT_LINEAGE_INCOMPLETE")
    for ref in data["attempts"]:
        item = ids[ref["attempt_id"]]
        if ref["sha256"] != item.sha256 or item.body["status"] == "started":
            raise Problem(422, "ATTEMPT_DIGEST_MISMATCH")
        pred = item.body["supersedes_attempt_id"]
        if pred and (
            pred not in ids
            or ids[pred].body["component"] != item.body["component"]
            or ids[pred].body["status"] not in ("invalid", "canceled")
        ):
            raise Problem(422, "INVALID_ATTEMPT_LINEAGE")
        if pred and item.body["component"] == "cardiac":

            def modality(body):
                metadata = body["component_metadata"]
                return metadata.get("modality") or metadata.get("projection", {}).get(
                    "modality"
                )

            if modality(ids[pred].body) != modality(item.body):
                raise Problem(422, "INVALID_ATTEMPT_LINEAGE")
    for component, selected in data["selected"].items():
        if selected is None:
            if (
                component == "saliva"
                and snapshot["sample"]["status"] != "not_collected"
            ):
                raise Problem(422, "SELECTED_ATTEMPT_REQUIRED")
            if (
                component in ("eyes", "cardiac", "task")
                and snapshot[component]["status"] != "not_collected"
            ):
                raise Problem(422, "SELECTED_ATTEMPT_REQUIRED")
            continue
        item = ids.get(selected)
        if not item or item.body["component"] != component:
            raise Problem(422, "SELECTED_ATTEMPT_MISMATCH")
        expected = (
            {"sample": snapshot["sample"], "saliva": snapshot["saliva"]}
            if component == "saliva"
            else snapshot.get(component)
        )
        if component == "alcohol":
            alcohol = record(db, account, "alcohol", check.id)
            expected = alcohol.body if alcohol else None
        if digest(item.body["component_metadata"]["projection"]) != digest(expected):
            raise Problem(422, "PROJECTION_MISMATCH")
        body = item.body
        if body["status"] == "valid" and body["source"] != "simulated":
            native_optical = False
            if check.mode != "synthetic":
                from .operator_governance import capture_configuration, started_capture, validate_optical_attempt, validate_reader_projection
                approved = capture_configuration(db, account, check,
                    "ecg" if component == "cardiac" and expected.get("modality") == "ecg" else component,
                    body["configuration_id"], body["configuration_hash"])
                if body["source"] != "reference_lab":
                    authorization = started_capture(db, account, check, body, approved)
                    if component == "eyes":
                        validate_optical_attempt(db, account, check, body, approved, authorization)
                        native_optical = (body["source"] == "prototype_sensor"
                            and approved["software_adapter_id"] == "optical_roi_v1"
                            and approved.get("device_id") is None)
                    if approved["software_adapter_id"] == "otgd_signed_reader_v1":
                        validate_reader_projection(db, approved, body["component_metadata"]["projection"])
                if component == "task" and body["component_metadata"].get("native_result", {}).get("timing", {}).get("deviceModel") not in approved["supported_phone_models"]:
                    raise Problem(403, "PHONE_CONFIGURATION_UNAVAILABLE")
            if (
                component == "task"
                and body["source"] == "prototype_sensor"
                and "uncalibrated" in body["quality_flags"]
            ):
                if not body["component_metadata"].get("native_result"):
                    raise Problem(422, "NATIVE_EVIDENCE_REQUIRED")
            elif native_optical:
                # The phone camera has no peripheral-reader key. Its complete
                # ledger and current owned online start were checked above;
                # physical/clinical qualification remains a separate model gate.
                pass
            else:
                qualification(
                    db,
                    account,
                    check,
                    "ecg"
                    if component == "cardiac" and expected.get("modality") == "ecg"
                    else component,
                    body["configuration_id"],
                    body["configuration_hash"],
                )
                if component == "saliva" and body["source"] == "reference_lab":
                    imported = record(
                        db,
                        account,
                        "lab_import",
                        body["component_metadata"].get("lab_import_id", ""),
                    )
                    if (
                        not imported
                        or imported.parent_id != check.id
                        or digest(imported.body["measurements"])
                        != digest(expected["saliva"])
                    ):
                        raise Problem(403, "AUTHORIZED_LAB_IMPORT_REQUIRED")
                elif not body["attestation_refs"] or any(
                    not record(db, account, "attestation", ref)
                    or record(db, account, "attestation", ref).body["envelope"][
                        "attempt_id"
                    ]
                    != body["attempt_id"]
                    for ref in body["attestation_refs"]
                ):
                    raise Problem(403, "ATTESTATION_REQUIRED")
        for ref in body.get("artifact_refs", []):
            from .db import Artifact

            artifact = db.get(Artifact, ref)
            if (
                not artifact
                or artifact.account_id != account.id
                or artifact.generation != account.generation
                or artifact.session_id != check.id
                or artifact.state != "verified"
                or not artifact.version_id
            ):
                raise Problem(403, "VERIFIED_ARTIFACT_REQUIRED")
    return context, manifest


def measurement_result(check):
    s = check.snapshot
    sources = sorted(
        set(
            [x["source"] for x in s["saliva"]]
            + [s[k]["source"] for k in ("eyes", "cardiac", "task")]
        )
    )
    invalid = any(
        s[k]["status"] == "invalid" for k in ("sample", "eyes", "cardiac", "task")
    )
    result = {
        "schema_version": "0.1.0",
        "result_id": uid(),
        "session_id": check.id,
        "state": "invalid" if invalid else "measurement_only",
        "target_at": s["target_at"],
        "evaluated_at": iso(),
        "model_id": None,
        "model_lifecycle": None,
        "endpoint_id": None,
        "probability": None,
        "classification": None,
        "operating_threshold": None,
        "uncertainty_policy_id": None,
        "reason_codes": ["MODEL_UNAVAILABLE", "MODEL_UNVALIDATED"]
        + (["INVALID_ACQUISITION"] if invalid else [])
        + (["SIMULATED_INPUT"] if "simulated" in sources else []),
        "input_sha256": check.snapshot_sha256,
        "provenance_summary": sources,
        "replaces_result_id": None,
    }
    validate_schema(result, "result.schema.json")
    return result


def safe_result(value):
    if value is None:
        return None
    if value.get("schema_version") == "1.1.0":
        from .model_engine import validate_result

        return validate_result(value)
    if value.get("state") == "research_estimate":
        raise Problem(422, "UNSUPPORTED_RESEARCH_RESULT")
    validate_schema(value, "result.schema.json")
    return value


def verify_signature(public_spki, signature, domain, payload):
    try:
        key = serialization.load_der_public_key(
            base64.b64decode(public_spki, validate=True)
        )
        if not isinstance(key, ec.EllipticCurvePublicKey) or not isinstance(
            key.curve, ec.SECP256R1
        ):
            raise ValueError()
        sig = base64.b64decode(signature, validate=True)
        r, s = utils.decode_dss_signature(sig)
        order = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
        if (
            not 0 < r < order
            or not 0 < s < order
            or utils.encode_dss_signature(r, s) != sig
        ):
            raise ValueError()
        key.verify(sig, domain.encode() + canonical(payload), ec.ECDSA(hashes.SHA256()))
    except Exception:
        raise Problem(403, "INVALID_DEVICE_PROOF") from None
