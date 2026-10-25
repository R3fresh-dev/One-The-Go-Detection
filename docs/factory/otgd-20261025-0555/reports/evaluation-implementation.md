# Evaluation and server alcohol dependency assertions

Author role: OpenAI backend assertion builder, subordinate to sole PM `/root`; this is implementation evidence, not independent review or signoff. Branch `factory/one-the-go-detection-20261025`; inspected HEAD `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus the bounded three-test-file diff identified below. Executed 2026-10-25 UTC. Acknowledged D-001 v1, D-002 v1, D-003 v1, D-004 v1, D-005 v1 and D-006 v3 before editing; correction round remains 0/2 and recovery attempts 0/3.

## Delivered assertion bindings

| Requirement / finding | Actual assertions | Execution scope |
|---|---|---|
| OTGD-008 EVAL-007 / ENG-005 / V-SW-001 | `test_model_evaluation.py::test_external_history_references_remain_unverified_through_pipeline` invokes real index/freeze/train/evaluate/verify CLI paths through `external_history_pipeline`; snapshots original input objects, refs, row identities and digests before the CLI; compares exact dataset/analysis/split/training/report/artifact bytes or digests, all training rows and both eight-row evaluation partitions. | One full-mode case; all four original ablations retained. |
| OTGD-041/042 / ENG-005 / V-SW-001 | Same named case in `test_model_evaluation_cardiac.py` reuses actual CLI assertions for ADC/SparkFun × population/personalized fixtures; additionally compares every original custody row hash, source-bundle ref/hash, snapshot/authority/baseline hash, entire original provenance and manifest/report/training bindings. | Four HR-only cases; each has only its prespecified HR artifact. |
| EVAL-007 caller assertions cannot authenticate history | `test_self_asserted_or_extra_approval_fields_do_not_authenticate_history` in both modules: strict dataset/plan/endpoint extra claims refuse; typed HR provenance/custody extra authentication claims refuse. Untyped training/evidence claims (authority, clinical success, historical verification, extra independent review, and even a self-rehashed HR manifest) fail deterministic verification. Original files are restored and verification is repeated. Required `endpoint.independently_assessed=true` remains an input assertion; output authenticity remains false. | Five cases, covering full + four HR fixture variants; five common untyped forgeries per case plus one HR manifest forgery per HR case. |
| Runtime self-approval remains refused | Existing `test_immutable_submission_three_principals_lifecycle_history_and_revision`: submitter cannot approve, approver cannot release, immutable original evidence retained. Existing model-admission tests run unchanged in the focused 185-case command. | Lifecycle denial case also executed separately; no new self-signoff route. |
| OTGD-019 AND-ALC-001/004 / ENG-006 / V-SW-002 | `test_alcohol_configuration_and_calibration_expiry_boundary_preserves_history`: typed fictional alcohol configuration or its calibration at expiry −1 ms / exact expiry / expiry +1 ms. Before expiry the dependency check succeeds; equality and later refuse current authority. Calibration-expired cases prove the configuration itself remains current while its dependency fails. Submitted body/hash and all lifecycle decisions remain identical, with authoritative history reporting expired. | Six direct server cases. Dependency validity does not establish instrument availability. |
| AND-ALC-001/004 absent instrument | `test_alcohol_current_dependencies_do_not_manufacture_an_available_adapter`: actual inventory has no alcohol software adapter/physical driver; exact current capabilities remain unavailable, configuration list empty, `HUMAN_ADAPTER_UNIMPLEMENTED`; real `capture_configuration` refuses despite current fictional scoped dependencies. | One actual-inventory case. Material is explicitly `breath_alcohol` / `mg/L`. |
| AND-ALC-004 grant/start race and stale capability | `test_alcohol_expiry_between_contract_grant_and_start_rejects_cached_authority`: actual HTTP session/context/attempt/grant/start routes; owned binding, consent and exact frozen device association. A test-local hypothetical inventory entry permits only the existing fictional configuration for discovery/grant, then is restored. Advance current server clock to exact expiry or +1 ms for configuration/calibration while the original 60-second grant is still valid. Cached start and fresh grant both return 403 `APPROVED_REGISTRY_VERSION_REQUIRED`; current capability becomes unavailable. | Four explicitly hypothetical contract cases; no driver/hardware is supplied. Existing `sign_start` boundary called zero times; no start token, no accepted alcohol record, original authorization remains exactly issued. Server has no hardware acquisition boundary; actual client adapter-call counts belong to the mobile owner. |

The new evaluation cases pass against unchanged production code: they are explicit existing-behavior assertions, not a claimed production RED→GREEN fix. The first alcohol run observed 7 passes and 4 failures because the new test context omitted its binding/device association (`DEVICE_CONTEXT_MISMATCH`). Inspecting `capture_binding_context` and the existing bound-reader case identified this fixture error. Adding the exact fictional association corrected the fixture; all 11 new cases then passed. No production behavior or assertion was weakened.

Every emitted external-verification/history/authority/clinical-success field is asserted false at its actual contract location. No nonexistent fields were added to reports, artifacts or receipts. Original common refs are `FICTIONAL-UNVERIFIED-AUTHORIZATION-NO-HUMAN-APPROVAL`, `FICTIONAL-UNVERIFIED-HISTORICAL-PLAN-LOCK`, and `FICTIONAL-UNVERIFIED-INDEPENDENT-ENDPOINT-RECORD`; HR adds `FICTIONAL-UNVERIFIED-RETAINED-HR-SOURCE-BUNDLE` and `FICTIONAL-UNVERIFIED-HR-INDEPENDENT-REVIEW`. Required endpoint assertions and copied references prove no real independent history.

## Executed commands and results

Commands ran from repository root, with `UV_CACHE_DIR=/tmp/otgd-uv-cache`. All successful pytest commands emitted one existing FastAPI/Starlette `httpx` TestClient deprecation warning; no skips occurred in the reported focused commands.

| Command following the cache environment prefix | Actual result |
|---|---|
| `uv run --project services/api pytest services/api/tests/test_model_evaluation.py services/api/tests/test_model_evaluation_cardiac.py -q -k 'external_history or self_asserted'` | Exit 0: **10 passed, 160 deselected**, 14.58 s. First execution of the new evaluation assertions; production unchanged. |
| `uv run --project services/api pytest services/api/tests/test_model_evaluation.py services/api/tests/test_model_evaluation_cardiac.py services/api/tests/test_model_admission.py -q` | Exit 0: **185 passed**, 69.15 s. |
| `uv run --project services/api pytest services/api/tests/test_operator_governance.py -q -k alcohol` | Initial fixture-development run exit 1: **7 passed, 4 failed, 32 deselected**, 2.42 s, all four named HTTP contract cases failed at grant with `DEVICE_CONTEXT_MISMATCH`. Corrected-fixture rerun exit 0: **11 passed, 32 deselected**, 1.91 s. |
| `uv run --project services/api pytest services/api/tests/test_operator_governance.py -q` with default isolated SQLite | Exit 1: **41 passed, 2 failed**, 4.60 s. Mandatory PostgreSQL tests refused SQLite as designed: `test_actual_postgresql_retirement_waits_for_current_reference_acceptance_transaction` and `test_actual_postgresql_preserves_registry_content_and_append_only_decisions`. This was not recorded as a full pass. |
| Same unfiltered governance command with PM-approved disposable actual PostgreSQL environment below | Exit 0: **43 passed**, 9.85 s, including both actual PostgreSQL cases and all new alcohol cases. Exclusive database use was released to PM immediately afterward. |
| `uv run --project services/api pytest services/api/tests/test_operator_governance.py -q -k immutable_submission_three_principals_lifecycle_history_and_revision` | Exit 0: **1 passed, 42 deselected**, 0.10 s; existing runtime self-approval denial executed separately. |
| `uv run --project services/api pytest services/api/tests -m 'not postgres' -q` | Exit 0: **1338 passed, 20 deselected**, 151.89 s. The 20 PostgreSQL-marked cases are explicitly deselected from this SQLite unit inventory, not counted as passed. Two of those actual-PG cases passed in the separate 43-case governance execution; the remaining PostgreSQL suite belongs to the PM's live gate. This command is broader API verification, not aggregate coverage/live evidence. |
| `git diff --check -- services/api/tests/test_model_evaluation.py services/api/tests/test_model_evaluation_cardiac.py services/api/tests/test_operator_governance.py` | Exit 0. |

Actual PostgreSQL command environment: `OTGD_DATABASE_URL=postgresql+psycopg://otgd_ci:<PM-provided-disposable-fixture-password>@127.0.0.1:55432/otgd_ci`, `OTGD_DATABASE_NAME=otgd_ci`, `OTGD_DATABASE_POOL_SIZE=5`, `OTGD_DISPOSABLE_DATABASE=true`, `OTGD_ENVIRONMENT=test`, `OTGD_LIVE_S3_ENDPOINT=http://localhost:4566`, `OTGD_APP_DATABASE_USER=otgd_app_ci`, `OTGD_APP_DATABASE_PASSWORD=<PM-provided-disposable-runtime-fixture-password>`, and PM-provided fictional test `OTGD_TOMBSTONE_KEY`. Credentials intentionally omitted from this persisted report; exact supplied environment is in the PM's live task handoff. The existing test client drops/creates tables only in this explicitly disposable `otgd_ci`; canonical `otgd` is untouched. No Docker mutation, retained application data/journal mutation, cloud operation, participant use, commit or push was performed by this author.

## Candidate file identity

| Path | SHA-256 |
|---|---|
| `services/api/tests/test_model_evaluation.py` | `60013323430a0979caeffcef4b2983566a028b0f50e75938df7f053c0498fdc0` |
| `services/api/tests/test_model_evaluation_cardiac.py` | `6ba27142296226c46ec947b7fe5e2a47168faac3baed130da00c364cc85d4ea8` |
| `services/api/tests/test_operator_governance.py` | `4d512a3ad9f7c65b69ee09d94fb471799d1aff63a5bc4c34140526dcac280ae7` |
| `tools/model_evaluation.py` (unchanged) | `80488d36507c7adb49bbf02448eec9f8ab173008f53e82f59c2d5d782194396c` |
| `services/api/otgd/operator_governance.py` (unchanged) | `1e16fc9b3679b1d6abd4cc6bdad1a53d18e8e02c4b759e2c3a950b04286ce971` |

## Limits and handoff

Measurement remains default; future alcohol remains a separate calibrated breath channel in mg/L. These are fictional software fixtures and confer no participant, study, independent scientific, clinical, driving/legal-clearance or release authority. No qualified alcohol adapter exists; a real instrument start and recalibration recovery journey remain **BLOCKED by absent qualified instrument/external evidence**. The actual server expiry code is generic `APPROVED_REGISTRY_VERSION_REQUIRED`; calibration-specific evidence is available in its authoritative registry history. This task does not invent a participant-facing recalibration diagnosis or change absent-adapter messaging.

Full required coverage strictly greater than 80%, remaining live PostgreSQL suite, native/OS/physical/scientific checks, Docker/LocalStack/browser/performance checks and all independent per-spec reviews belong to the PM's exact final candidate gate. No self-signoff is supplied. No action was approval-denied, pending approval or left with an uncertain external outcome by this author. PM alone commits/pushes and may create only a draft PR; no merge/deployment/publication is authorized here.

## Reproduced fictional pipeline hash bindings

The following complete recorded refs/hashes were reproduced by invoking the same actual `external_history_pipeline` helper for full mode and all four HR modes with fixed software execution timestamps (`2026-03-02T00:00:00Z` training/pipeline lock, `2026-03-03T00:00:00Z` evaluation). Original dataset/plan/split hashes are captured before CLI execution, and original in-memory training/report/artifact hashes before CLI reproduction. Every input and output binding is compared by the assertions above. `row_accounting_sha256` is a supplementary digest of both partitions' complete prediction rows; the tests assert exact row membership/count and exact complete evidence equality. Local supporting generated files remain at `/tmp/otgd-evaluation-bindings-20261025/`; its `bindings.json` SHA-256 is `6d991b265ba2fa9b561b61a9127115832f437746beb57ee489b35cd3797f4f63`. The source-bound summary is preserved below.

```json
{
  "full": {
    "dataset_sha256": "541dd88316d42113f946804f3d03c1c76945476dfc81e8c8cd4630cb87ed4369",
    "analysis_plan_sha256": "09be957f2c87ff48e0782f26189ebdbac97af5691e26689ae5d62ac19e4e14ed",
    "split_plan_sha256": "d77cf30228ce7125a2d17288d0172a74270ab127c0a29f2b8e85bc954d846711",
    "training_sha256": "46af324725ebaf0fbd37fd0c435d6657f9561e8c22732c637124001dc9dcf1ec",
    "evaluation_report_sha256": "9cccbe31983302fdf89e5362447836feb9d987f0d3c60091ca545843eaaa1c0f",
    "artifact_sha256": {
      "app_only": "2ff6ec167af1ed88edd78facb64938d878044e2b48bbac2ddb81c7a58de76408",
      "chemical_only": "e6796f320637bccc6a6014bfdab8705b70ff2ec7ac329fd40abcb4bdd2f67415",
      "combined": "9122f3e7dc3d5297497ec902abf225014d6b8d549f009ff1591ec03b8d214035",
      "ecg_removed": "80e83ad1dcfcd37baa4b8cf52cc3dfc6906988aebd9e91134b83b8d0d3df6e4c"
    },
    "external_assertions": {
      "authorization_ref": "FICTIONAL-UNVERIFIED-AUTHORIZATION-NO-HUMAN-APPROVAL",
      "historical_lock_or_blinding_proven": false,
      "independent_endpoint_evidence_ref": "FICTIONAL-UNVERIFIED-INDEPENDENT-ENDPOINT-RECORD",
      "plan_lock_ref": "FICTIONAL-UNVERIFIED-HISTORICAL-PLAN-LOCK",
      "verified_by_tool": false
    },
    "row_accounting_sha256": "e2c74a90e8f65f14fc553f63013e7bd232d6b272d8f590cbe5963afaa147f8a8"
  },
  "otgd_esp32_adc_v1-population": {
    "dataset_sha256": "882ca5f8866228c4bd91bf7765e43594d8c1f76a001785f171d2181c1a35ef22",
    "analysis_plan_sha256": "c8303add5ad12c642099a1bce529742c4ec5e3deda32a8ddc1101a69f516cd65",
    "split_plan_sha256": "f5b1f363c6c174de0bf994de5237ff033b273281d2c48ff26b8b8bc763f9849b",
    "training_sha256": "eaa749cfd43281214d05d60ea61b855f10667ba9711ce7dde061e1a154559fb3",
    "evaluation_report_sha256": "13bf71d0ed52762a83d26a72c0d0b3f7fcd1ea7c67f1b792ea8b5512f8b65244",
    "artifact_sha256": {
      "cardiac_hr_only": "e143769b60f7b01ad54be1b6b03d49c27a68edc1c690987281b962a2f0060f84"
    },
    "external_assertions": {
      "authorization_ref": "FICTIONAL-UNVERIFIED-AUTHORIZATION-NO-HUMAN-APPROVAL",
      "historical_lock_or_blinding_proven": false,
      "independent_endpoint_evidence_ref": "FICTIONAL-UNVERIFIED-INDEPENDENT-ENDPOINT-RECORD",
      "plan_lock_ref": "FICTIONAL-UNVERIFIED-HISTORICAL-PLAN-LOCK",
      "verified_by_tool": false
    },
    "row_accounting_sha256": "fddbc3f3ac84374f61ff3cdc55be48f46008a6a60eb5d0cb6d841c54a8337293",
    "cardiac_evidence_manifest_sha256": "37549720298c05e1c434e406f32eab129eda249754320e71f0596339a57334f5"
  },
  "otgd_esp32_adc_v1-personalized": {
    "dataset_sha256": "f7a8b4177e24b61dd5f251688d992a4b4b1743a6c3839bf374f03fc1e9f333cf",
    "analysis_plan_sha256": "8a5e43170f7446c778eb641a84f6c74b58b8665045fc45e30d2c9d9e41dc7deb",
    "split_plan_sha256": "a12a034e80b269d0ef99541fbdb464d81b3a601174d5ee0e8daf3116a9150635",
    "training_sha256": "a82a6b9d7d72cbf8f0846eb8737784149deed8348381f1c7eee579a7fb0a23e3",
    "evaluation_report_sha256": "afe0e7721d7209b3aa1ea88cc14db67acbd379a5f7d3b5ac470da2f120cd2e61",
    "artifact_sha256": {
      "cardiac_hr_only": "964aff872caacfef8bd8e6ef75ca289c753ab8264904803d552fcfdc8af31fac"
    },
    "external_assertions": {
      "authorization_ref": "FICTIONAL-UNVERIFIED-AUTHORIZATION-NO-HUMAN-APPROVAL",
      "historical_lock_or_blinding_proven": false,
      "independent_endpoint_evidence_ref": "FICTIONAL-UNVERIFIED-INDEPENDENT-ENDPOINT-RECORD",
      "plan_lock_ref": "FICTIONAL-UNVERIFIED-HISTORICAL-PLAN-LOCK",
      "verified_by_tool": false
    },
    "row_accounting_sha256": "c4f6a07a4024e547b9e0aaf17f9fb50af14a176854f599decb9db583ca64cc75",
    "cardiac_evidence_manifest_sha256": "1d06c544adde3edd3fe2a0f2de944309cbfb3a2cb89050ecf86e2898c203ff52"
  },
  "otgd_sparkfun_max32664_v1-population": {
    "dataset_sha256": "53931ac8f97098d4c0efe9d37a644ee50bc66a554a94a836e755206346a3062b",
    "analysis_plan_sha256": "140e7c86c1cdd53dec7f30377b4b25a37c8497ed32103697c2a55f0edec17df4",
    "split_plan_sha256": "ac6c8e51f833e53bf2829d99d95a06660c81b00376ed532210934be72961e804",
    "training_sha256": "2276216768a8c8bca185dbc274df9843aa77dff9c88f8470fa9d4217eaabaf4a",
    "evaluation_report_sha256": "50f3656e02178d0616e37df76dd362968424b5dac5c1c6208b8df4666ec29c06",
    "artifact_sha256": {
      "cardiac_hr_only": "e143769b60f7b01ad54be1b6b03d49c27a68edc1c690987281b962a2f0060f84"
    },
    "external_assertions": {
      "authorization_ref": "FICTIONAL-UNVERIFIED-AUTHORIZATION-NO-HUMAN-APPROVAL",
      "historical_lock_or_blinding_proven": false,
      "independent_endpoint_evidence_ref": "FICTIONAL-UNVERIFIED-INDEPENDENT-ENDPOINT-RECORD",
      "plan_lock_ref": "FICTIONAL-UNVERIFIED-HISTORICAL-PLAN-LOCK",
      "verified_by_tool": false
    },
    "row_accounting_sha256": "e8743d5097004b24aa44b81c471bc80e683d9666e89b6bc2b74b4ee7cdbaf25e",
    "cardiac_evidence_manifest_sha256": "32e43bb103446303f6fda3918e6366644ad184483906d6c31df7b474a0169d0c"
  },
  "otgd_sparkfun_max32664_v1-personalized": {
    "dataset_sha256": "834ee4d57c94d40163778b94221b01a2f29455ef687960bb9f069c8f49c9da0f",
    "analysis_plan_sha256": "eb5e18dde74b9eb07b2573ddc15c0f0470117b10b265a6a6e0ad7f44cab98faf",
    "split_plan_sha256": "c117e224d8cbe53fca320c5b58852e41fb4d7ba71d53dad66d2dd89a54220768",
    "training_sha256": "d0b1dde61b41332c492f3e11c280256c046c877327deb68ceb7549d1d1120f26",
    "evaluation_report_sha256": "e07d427ebe82d43da44bdec6acdc8b1f4af40c931f9a0ba6a3bd32a0ce48be69",
    "artifact_sha256": {
      "cardiac_hr_only": "964aff872caacfef8bd8e6ef75ca289c753ab8264904803d552fcfdc8af31fac"
    },
    "external_assertions": {
      "authorization_ref": "FICTIONAL-UNVERIFIED-AUTHORIZATION-NO-HUMAN-APPROVAL",
      "historical_lock_or_blinding_proven": false,
      "independent_endpoint_evidence_ref": "FICTIONAL-UNVERIFIED-INDEPENDENT-ENDPOINT-RECORD",
      "plan_lock_ref": "FICTIONAL-UNVERIFIED-HISTORICAL-PLAN-LOCK",
      "verified_by_tool": false
    },
    "row_accounting_sha256": "f83dd35892c06ce3c6b0747ef1d7cc1a63b825c8e03a613bbba7a343f44aaacf",
    "cardiac_evidence_manifest_sha256": "0ffa59ffca950b849961f3f27796901eec6c9dd90c5e31d506d7d14777610eab"
  }
}
```
