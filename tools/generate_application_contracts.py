#!/usr/bin/env python3
"""Regenerate the application API and companion schemas from locked source DTOs.

Run with: uv run --project services/api python tools/generate_application_contracts.py
The test environment here is for schema loading only; no database or cloud call occurs.
"""

import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("OTGD_ENVIRONMENT", "test")
os.environ.setdefault("OTGD_DATABASE_URL", "sqlite://")
sys.path.insert(0, str(ROOT / "services/api"))
from otgd.main import app
from otgd import dto
from otgd.synthetic_evidence import SyntheticDeviceCapture

OUTPUT = ROOT / "contracts/application"
MODELS = [
    "ProfileWrite",
    "CaptureContext",
    "CaptureAttempt",
    "EvidenceManifest",
    "Alcohol",
    "ExportRequest",
    "Attestation",
    "CaptureAuthorization",
    "StartAuthorization",
]


def main():
    OUTPUT.mkdir(exist_ok=True)
    api = app.openapi()
    api["info"]["description"] = (
        "Versioned measurement-only application API. Clinical inference is compiled unavailable. See shared-contracts.md for state, idempotency, owner/generation and native evidence invariants. Unknown nested component metadata is rejected at runtime; CaptureAttempt carries a strict v0.1 projection plus the named typed companion evidence."
    )
    synthetic = SyntheticDeviceCapture.model_json_schema()

    def refs(value):
        if isinstance(value, dict):
            return {
                k: ("#/components/schemas/Synthetic" + v[len("#/$defs/") :])
                if k == "$ref" and isinstance(v, str) and v.startswith("#/$defs/")
                else refs(v)
                for k, v in value.items()
            }
        if isinstance(value, list):
            return [refs(v) for v in value]
        return value

    definitions = synthetic.pop("$defs", {})
    for name, value in definitions.items():
        api["components"]["schemas"]["Synthetic" + name] = refs(value)
    api["components"]["schemas"]["SyntheticDeviceCapture"] = refs(synthetic)
    api["components"]["securitySchemes"] = {
        "BearerAccess": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT access token",
            "description": "Pinned issuer/client, access token_use, current token family and owner generation are verified on every operation.",
        }
    }
    for path, item in api["paths"].items():
        for method, operation in item.items():
            if method not in ("get", "post", "put", "patch", "delete"):
                continue
            public = (
                path.startswith("/health/")
                or path == "/v1/app-config"
                or path.startswith("/v1/notices/")
            )
            if public:
                continue
            operation["security"] = [{"BearerAccess": []}]
            if method in ("post", "put", "patch", "delete"):
                parameters = operation.setdefault("parameters", [])
                for name, description in [
                    (
                        "X-App-Version",
                        "Supported semantic app version; required for ordinary QA/prod writes. Minimum or support-policy mismatch receives 426. Privacy reconciliation remains available.",
                    ),
                    (
                        "X-Data-Generation",
                        "Current writable account generation; stale ordinary writes receive410.",
                    ),
                    (
                        "Idempotency-Key",
                        "Stable key for this exact operation, persisted across retries. Changed body with the same key receives409.",
                    ),
                ]:
                    parameters.append(
                        {
                            "name": name,
                            "in": "header",
                            "required": name != "X-App-Version",
                            "schema": {"type": "string"},
                            "description": description,
                        }
                    )
                if method in ("put", "patch") or path.endswith("/finalize"):
                    parameters.append(
                        {
                            "name": "If-Match",
                            "in": "header",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": 'Quoted integer revision; use "0" for first creation of an immutable context/attempt/manifest.',
                        }
                    )
            for status, description in {
                "401": "Authentication required.",
                "403": "Current account, notice, consent or capability does not permit the operation.",
                "404": "No currently owned record.",
                "409": "Immutable state or idempotency conflict.",
                "410": "Retired generation or expired data.",
                "412": "Revision conflict.",
                "422": "Typed validation failed; no input values echoed.",
                "426": "Application update required before ordinary writes.",
                "429": "Bounded capacity exceeded; honor Retry-After.",
                "503": "Required dependency unavailable; no success implied.",
            }.items():
                operation.setdefault("responses", {}).setdefault(
                    status, {"description": description}
                )
    (OUTPUT / "openapi.json").write_text(
        json.dumps(api, indent=2, ensure_ascii=False) + "\n"
    )
    for name in MODELS:
        (OUTPUT / f"{name}.schema.json").write_text(
            json.dumps(
                getattr(dto, name).model_json_schema(), indent=2, ensure_ascii=False
            )
            + "\n"
        )
    (OUTPUT / "SyntheticDeviceCapture.schema.json").write_text(
        json.dumps(
            SyntheticDeviceCapture.model_json_schema(), indent=2, ensure_ascii=False
        )
        + "\n"
    )
    print(
        f"Generated OpenAPI with {len(api['paths'])} paths and {len(MODELS) + 1} companion schemas."
    )


if __name__ == "__main__":
    main()
