# Round 1 backend assertion correction evidence

Builder: `/root/worker_builder`. Formal correction **1 / 2**, recovery **0 / 3**, unchanged. D-009 v3 and v4 acknowledged through actual PM messages before dependent edits. No self-signoff or application/release completion decision. No commit, push, Docker/service operation, installation, participant use, external deployment, or existing data cleanup was performed.

## Source and authority

Inspected the immutable old-candidate adjudication at `/workspace/scratch/otgd-20261025-0555-live/verification-backend/{report.md,case-adjudication.json}`, current normative raw-export/operator/recovery clauses, and existing named tests. The old adjudication's PARTIAL classifications also contain external or integration clauses; the new assertions below do not convert those whole cases to PASS automatically. Old-candidate artifacts were not edited or adopted as current execution.

Initial assignment authorized bounded test additions only. PM's D-009 v4 subsequently corroborated and assigned the sole production correction: `services/api/otgd/main.py::job_view`. Its string-only retained categories did not match the client object representation and omitted policy/reason/expiry detail. The new actual TestClient regression failed against the original strings and passed after the bounded representation repair. No production raw-export, operator, recovery or native-evidence implementation was changed.

Additional test ownership was coordinated before editing. Existing PostgreSQL tests were already in `test_operator_governance.py`; no duplicate `test_operator_postgres.py` was introduced. `test_privacy_receipts.py` was explicitly authorized by PM for the narrow v4 regression. Client object shape and generated response handoff were coordinated directly with `/root/accessibility_builder`.

## Exact case/assertion bindings

| Current normative clause | Source assertion / actual check | Observation and scope |
|---|---|---|
| `OTGD-010-RAW-EXP-002-02`: over-cap source omitted while another eligible choice remains usable | `test_raw_export.py::test_over_budget_source_does_not_hide_or_disable_an_eligible_owned_choice` | Same current authority contains an over-cap source and eligible original. Discovery exposes only the original; freezing that surviving selection succeeds, selecting the large source raises `EXPORT_TOO_LARGE`. SQLite/codec-receipt unit fixture; no actual S3 byte claim. |
| `OTGD-010-RAW-EXP-003-02`: identical accepted POST replay denied after **export-authority** retirement | `test_raw_export.py::test_accepted_post_replay_after_export_authority_retirement_hides_original_scope` | Actual POST returns 202, real registry transition retires the `raw_export` version, consent stays active, same body/key replay returns 403 `APPROVED_REGISTRY_VERSION_REQUIRED`; error exposes no job/grant/download/scope fields. Exactly one unchanged pending export remains. This is distinct from consent withdrawal. |
| `OTGD-010-RAW-EXP-006-03`: successful verified no-store attachment | Extended `test_raw_export.py::test_actual_http_async_worker_zip_download_replay_expiry_and_foreign_denial` | Existing whole-file/hash/manifest assertions now also require exact `Cache-Control: private, no-store`, `Content-Disposition: attachment; filename="otgd-<job>.zip"`, and `application/zip` on the actual HTTP response. Storage remains its explicitly declared unit double. |
| `OTGD-010-RAW-EXP-008-01`: raw files fit but complete payload overflows narrower authority cap | `test_raw_export.py::test_raw_members_fit_but_complete_structured_manifest_archive_exceeds_grant` | Frozen raw sum is strictly below authority cap; structured record remains <=512 KiB and structured+raw exceeds cap. Actual worker reads source then fails the whole job with `EXPORT_TOO_LARGE`, no output/completion or written ZIP, and unchanged cap. SQLite/storage unit fixture. |
| `OTGD-011-OPERATOR-AUTHORITY-001-01`: PostgreSQL immutable JSON, digest, version, identity and reconstructable original | Extended `test_operator_governance.py::test_actual_postgresql_preserves_registry_content_and_append_only_decisions` | Actual PostgreSQL trigger rejects JSON, SHA-256, version, submitter, submission-time updates, submission deletion, decision update/deletion. Each rejected transaction is followed by a fresh session requiring the entire history equal the original and recomputed body digest equal its original digest. Actual dedicated PostgreSQL run passed; schema preserved. |
| `OTGD-011-OPERATOR-AUTHORITY-008-02`: later optical settlement cannot reuse retired approval or rewrite accepted snapshot | `test_operator_governance.py::test_retired_optical_approval_refuses_later_settlement_without_rewriting_snapshot[optical]` | Reuses current fully approved optical fixture; a new owned grant is issued and started. The run/authorization evidence passes the real pre-retirement validator. Real configuration retirement then causes HTTP settlement 403 `CAPABILITY_DENIED`; saved arm/revision remain unchanged, new check snapshot stays null, prior accepted snapshot and digest stay byte-equivalent. Native/physical optical qualification is not established. |
| `OTGD-016-RECOVERY-002-01`: freshly approved configured closure can collect while unsealed scope stays suspended | `test_recovery_scopes.py::test_configured_reapproved_study_reaches_real_capture_start_and_model_execution` and `configured_reapproval` | Reuses the existing actual three-principal task/model fixture. Seal closure explicitly contains study/configuration/qualification/retention/model/calibration references and equals current closure. Actual HTTP capture grant/start succeeds under exact submitted digest; actual model computation returns ResearchResult 1.1.0 with execution authority. Global suspension remains true and another unsealed scope is denied. No `require_authority` success patch was added. Unit `environment=test` admission and retained-seal storage double remain explicit prerequisites, not independent retained cloud proof or physical collection. |
| `OTGD-016-RECOVERY-002-02`: configured dependency retirement/change denies capture and model under the original seal | `test_recovery_scopes.py::test_prior_configured_seal_refuses_changed_dependency_through_capture_and_model[retired_retention/replaced_configuration]` | Real retention retirement or independently submitted/reviewed/released configuration replacement occurs after the original seal. Actual HTTP capture authorization and model execution authority refuse `RECOVERED_SCOPE_SUSPENDED`; resulting model response is inconclusive with null probability/classification and no execution tuple. Original retained seal bytes/count and global suspension stay unchanged; no snapshot is introduced. Same stated unit authority/transport limits. |
| `OTGD-016-RECOVERY-002-03`: failed nonprivacy admission allows accepted privacy cleanup without reopening or erasing independent evidence | `test_recovery_authority.py::test_failed_nonprivacy_admission_preserves_accepted_cleanup_and_retained_journal` | Retained activation absent from DB makes nonprivacy claim fail 503 before and after cleanup. Actual `worker.run_job` completes an accepted deletion, purges owned object versions/marker and generation records, preserves a neighboring owner's version, preserves every independent journal object/version byte-for-byte, and leaves nonprivacy job pending/fence zero. Explicit versioned unit transport; not actual hosted S3/Object Lock or provider account deletion proof. |
| D-009 v4 / shared `PrivacyJob` 1.0.0 category/policy/reason/expiry contract | New `test_privacy_receipts.py::test_deletion_api_receipt_keeps_named_retention_basis_reason_and_unspecified_expiry` | Actual TestClient accepted deletion POST202 and subsequent status GET200 preserve six named objects, exact known keys, `privacy-v1` basis, bounded factual reasons and explicit null expiry; existing job schema/kind/state/minimal fields remain. RED old strings → GREEN bounded objects. Journal acceptance is an explicit unit transport fixture. |

The optical test's initial expected error code was an oracle error: `domain.registry()` correctly denies the retired inactive projection with `CAPABILITY_DENIED`, before its later version guard. The normative clause requires refusal, not `APPROVED_REGISTRY_VERSION_REQUIRED`. The corrected exact oracle retained the 403 and unchanged-state assertions. This was not a demonstrated production optical defect.

## Production receipt representation

Only `job_view` changed. A deletion receipt now supplies exactly six bounded category objects:

```text
{ category: string, policy_basis: "privacy-v1", reason: string, expires_at: null }
```

The names remain `identity_and_generation_barriers`, `audit_and_security_metadata`, `minimal_operation_receipts`, `operator_membership_references`, `private_cleanup_references`, and `deletion_journal`. Reasons describe the existing technical function. No exact destruction date is configured for these references, so each expiry is explicitly null; a 90-day minimum journal retention is not represented as an expiry date. No legal authority, retention rule, deletion scope, external erasure, new state, or schema version was invented. Export categories remain empty. The client owner separately handles bounded legacy strings and displays unspecified expiry truthfully.

Actual fictional API response handed to the client owner: `reports/correction-deletion-receipt.json`, SHA-256 `a237d6c027633bd537e187930149dca08a91bffba75eca38642c3e1f135445ca`. It contains no credentials or private participant data and is ignored runtime evidence, not a deployment seed.

The client owner subsequently reported passing parse-to-actual-JobCard assertions using an exact-byte tracked copy at `apps/mobile/testfixtures/backend-privacy-deletion-receipt.json` with that same hash. Names/basis/reasons/null-expiry display, bounded legacy strings, supplied expiry and malformed-object refusals are client-owned checks; their raw execution/report must be consulted separately rather than treating this backend report as their independent verification.

## Executed commands and results

All commands ran from `/workspace/One-The-Go-Detection` using the already installed API environment and `UV_CACHE_DIR=/tmp/otgd-uv-cache`; no installation or full gate runner was invoked.

```sh
uv run --project services/api pytest services/api/tests/test_raw_export.py -q --junitxml=/tmp/correction-raw-export.xml
uv run --project services/api pytest services/api/tests/test_recovery_scopes.py -q --junitxml=/tmp/correction-recovery-scopes.xml
uv run --project services/api pytest services/api/tests/test_recovery_authority.py -q --junitxml=/tmp/correction-recovery-authority.xml
uv run --project services/api pytest services/api/tests/test_operator_governance.py -q -m 'not postgres' --junitxml=/tmp/correction-operator-sqlite.xml
OTGD_WRITE_PRIVACY_RECEIPT_FIXTURE=/workspace/One-The-Go-Detection/reports/correction-deletion-receipt.json uv run --project services/api pytest services/api/tests/test_privacy_receipts.py -q --junitxml=/tmp/correction-privacy-receipts-green.xml
uv run --project services/api pytest services/api/tests/test_raw_export.py services/api/tests/test_operator_governance.py services/api/tests/test_recovery_authority.py services/api/tests/test_recovery_scopes.py services/api/tests/test_privacy_receipts.py services/api/tests/test_identity_barriers.py services/api/tests/test_api.py -m 'not postgres' -q --junitxml=/tmp/correction-backend-focused.xml
```

Observed individual results: raw **67 passed**; configured recovery **14 passed**; authority recovery **27 passed**; operator SQLite **42 passed / 2 PostgreSQL tests deselected for separate execution**; privacy API **1 passed**. Final combined regression **200 passed / 2 PostgreSQL tests deselected**, 19.24 seconds, exit 0. Deselection is stated scope, not a claim that mandatory live gates passed. Existing Starlette/httpx deprecation warning appeared; no dependency change was made.

Real PostgreSQL command:

```sh
UV_CACHE_DIR=/tmp/otgd-uv-cache uv run --project services/api python /tmp/otgd-correction-operator-postgres.py > /tmp/correction-operator-postgres.log 2>&1
```

The retained launcher privately reads `OTGD_LOCAL_MIGRATION_PASSWORD` from `infra/local/.env`, never prints it, connects only to `127.0.0.1:55432/otgd_ci` as `otgd_migrator`, verifies the actual database/user, and creates a previously absent unique schema. Its child pytest command is:

```sh
python -m pytest services/api/tests/test_operator_governance.py::test_actual_postgresql_preserves_registry_content_and_append_only_decisions -q --junitxml=/tmp/correction-operator-postgres.xml
```

The connection sets explicit `search_path=correction_operator_aadc32e13ee24c22` with no public fallback. The existing fixture's unqualified metadata and migration SQL therefore create only this owned fresh schema's objects; it does not reset the existing public test schema or the canonical database. **1 passed**, 0.36 seconds, exit 0. The schema remains preserved. A separate read-only check confirmed database `otgd_ci`, runtime search path/current schema exactly `correction_operator_aadc32e13ee24c22`, role `otgd_migrator`, one original submitted version still present, and immutable triggers on both owned registry tables. Evidence: `/tmp/correction-operator-postgres-isolation.json`. No role privileges, canonical database, services, volumes, queues or journals were changed.

Whitespace diff check passed. Ruff passes for the new `test_privacy_receipts.py`. An optional broad Ruff check initially reported 80 findings versus HEAD's 73. PM explicitly authorized removal of only the seven newly introduced test-style findings; four local import groupings, two legitimate pytest imported-fixture argument annotations and one redundant f-string prefix were corrected. Final Ruff count is **73**, with per-file counts identical to HEAD: main 50, raw export 3, operator 10, recovery authority 8, recovery scopes 2. Baseline findings were not changed, and this is not represented as a clean broad lint run or required-gate PASS.

The affected imports/fixtures were then reexecuted on the final released source:

```sh
UV_CACHE_DIR=/tmp/otgd-uv-cache uv run --project services/api pytest services/api/tests/test_operator_governance.py services/api/tests/test_recovery_authority.py services/api/tests/test_recovery_scopes.py -m 'not postgres' -q --junitxml=/tmp/correction-backend-style-recheck.xml
```

Observed **83 passed / 2 PostgreSQL tests deselected**, 6.66 seconds, exit 0. The PostgreSQL assertion body and production source were unchanged by this test-only hygiene. Its earlier actual PostgreSQL result is scoped to that unchanged assertion, not a replacement for PM's final exact-candidate PostgreSQL gate.

## Released content identity and remaining verification

Scoped source handoff at approximately 2026-10-25 08:23 UTC, renewed after authorized test-only hygiene; unrelated authors' working files are not asserted frozen:

| Path | SHA-256 |
|---|---|
| `services/api/otgd/main.py` | `572dcc6b91bbfa1ef17bb71da6cde9c571f5b56cd07e990eb0c4f6ec632875e2` |
| `services/api/tests/test_raw_export.py` | `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014` |
| `services/api/tests/test_operator_governance.py` | `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600` |
| `services/api/tests/test_recovery_authority.py` | `c6f39c45163f8e2c709b5f63094f1c7df83afb094c9905003fee61fc7fa0b638` |
| `services/api/tests/test_recovery_scopes.py` | `3fe448145c086a5441b96caeffa0fa006f24a0b18396da3ac60462fba4850344` |
| `services/api/tests/test_privacy_receipts.py` | `84efc2d18bd0bcced419d82a6877e619b2bc1924a06118333b74cbe0f3c0c1d7` |

Final combined JUnit SHA-256: `ea7d63fa4874913f3640b6f688840769626cdca349ee2d8bfd449e52d5eef21f`; real PostgreSQL JUnit SHA-256: `48d7ecb93ffc4f0084abc288496e8c29b6d8b13db4d041e9213123de3e0874da`.

Durable copies of fourteen command/JUnit/isolation/launcher artifacts and a SHA-256 manifest are retained at `/workspace/scratch/otgd-20261025-0555-live/correction-backend-assertions/`. `manifest.json` binds the seven released source/response files and records a stable AST hash of the actual PostgreSQL assertion. The parent directory's immutable old-candidate adjudication remains untouched.

The full mandatory exact-candidate local/CI gates, >80% independent coverage, fresh complete 782-case reconciliation, independent affected reviews/signoffs and final approval remain PM-owned prerequisites. Configured recovery tests deliberately retain explicit unit admission/retained-storage limits; native OS, independent retained cloud authority, hardware, participant and scientific criteria remain unclosed. No auto-review denial occurred and no external action has an uncertain outcome.
