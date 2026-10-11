"""Export maintenance-only schemas; these are not participant approval routes."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services/api"))


def generate():
    from otgd.operator_governance import SCHEMAS, inline_material_schema
    from otgd.capture_signing import StartGrant
    from otgd.raw_capture import ECGRecording

    output = ROOT / "contracts/operator"
    output.mkdir(exist_ok=True)
    for kind, schema in SCHEMAS.items():
        value = schema.model_json_schema()
        if kind == "model":
            value["properties"]["manifest"] = {"$ref": "../model_manifest.schema.json"}
        value["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        value["$id"] = "https://one-the-go-detection.invalid/contracts/operator/" + kind + ".schema.json"
        value["description"] = "Maintenance submission only. Semantic identity, independent review, current dependencies and expiry are additionally enforced by otgd.operator_governance. This schema is not approval."
        (output / (kind + ".schema.json")).write_text(json.dumps(value, indent=2) + "\n")
    token = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object",
        "additionalProperties": False, "required": ["grant", "signature", "key_id", "domain"],
        "properties": {"grant": inline_material_schema(StartGrant),
            "signature": {"type": "string", "minLength": 1, "maxLength": 256},
            "key_id": {"type": "string", "minLength": 1, "maxLength": 256},
            "domain": {"const": "OTGD capture grant v1\u0000"}}}
    (ROOT / "contracts/application/ServerStartToken.schema.json").write_text(json.dumps(token, indent=2) + "\n")
    recording = ECGRecording.model_json_schema()
    recording["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    recording["description"] = "After OTGD-ECG-SAMPLES-v1 newline magic, RFC 8785 canonical JSON. Device signatures, current owned accepted evidence and independent scope/bounds verification remain mandatory."
    (ROOT / "contracts/application/ECGRecording.schema.json").write_text(json.dumps(recording, indent=2) + "\n")


if __name__ == "__main__":
    generate()
