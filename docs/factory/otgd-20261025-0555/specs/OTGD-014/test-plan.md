# OTGD-014: verification plan

Canonical: `openspec/changes/cloud-deployment-customer-access/specs/cloud-browser-delivery/spec.md`; SHA-256 `735f76493e8188925c157347dc22b0a2acad4cb76721f2ea8a7f324629631855`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `infra/test/test_cloud_endpoints.py` — `786b0d3537e333ffa9d9114c7d946ef8aebfed4213702e7816b2f8cb47726bc4`
- `infra/test/test_hosted_preview.py` — `7d44b7bd8f5482bf65109d9002908eefa2ee480b8eba524ab4fe3a24b240d8ce`
- `infra/test/test_provenance.py` — `996ead63b1f3ae3999aa31d81e3de893bbc50b62bfaac6e2a69f88a968d5f6a1`
- `infra/test/test_web_deployment.py` — `e0fbb440ac1b32d67b389b1261d3f6f8360e224793c8c4ad94809ea03fabb2d1`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### WEB-DEP-001 — Deliver public application bytes through a private origin

Normative acceptance source: `openspec/changes/cloud-deployment-customer-access/specs/cloud-browser-delivery/spec.md` / `WEB-DEP-001`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-014-WEB-DEP-001-01 | Customer opens the published HTTPS origin — **GIVEN** an admitted published application artifact **WHEN** a customer opens WebOrigin **THEN** CloudFront serves the application without public S3 access or credentials in the URL. | `infra/test/test_web_deployment.py:379` — test_disabled_foreign_origin_or_non_sigv4_distribution_cannot_publish_dns | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-014-WEB-DEP-001-02 | Caller requests the bucket directly — **GIVEN** an anonymous caller without distribution authority **WHEN** it requests an S3 asset **THEN** bucket policy does not grant public asset access. | `infra/test/test_web_deployment.py:379` — test_disabled_foreign_origin_or_non_sigv4_distribution_cannot_publish_dns | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### WEB-DEP-002 — Preserve browser routing and asset failures

Normative acceptance source: `openspec/changes/cloud-deployment-customer-access/specs/cloud-browser-delivery/spec.md` / `WEB-DEP-002`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-014-WEB-DEP-002-01 | Customer opens a history deep link — **GIVEN** published index.html **WHEN** GET /history reaches the distribution **THEN** the actual application entry point is returned. | `infra/test/test_web_deployment.py:199` — test_https_asset_deep_link_readiness_checks_do_not_claim_signed_in_acceptance | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-014-WEB-DEP-002-02 | A missing script is requested — **GIVEN** no matching .js asset **WHEN** the browser requests that asset **THEN** an origin error is preserved rather than returning a successful HTML body. | `infra/test/test_web_deployment.py:147` — test_public_asset_types_paths_symlinks_and_duplicate_zip_entries_are_rejected<br>`infra/test/test_hosted_preview.py:274` — test_upload_missing_token_changed_artifact_redirect_and_vendor_body_do_not_escape | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### WEB-DEP-003 — Pin secure public browser identity

Normative acceptance source: `openspec/changes/cloud-deployment-customer-access/specs/cloud-browser-delivery/spec.md` / `WEB-DEP-003`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-014-WEB-DEP-003-01 | QA and production are opened together — **GIVEN** separate approved account deployments **WHEN** both applications open **THEN** each uses its own identity/API and QA remains visibly identified. | `infra/test/test_web_deployment.py:42` — test_browser_build_environment_retains_transport_settings_without_deploy_credentials | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-014-WEB-DEP-003-02 | A host environment attempts to override identity — **GIVEN** conflicting APP/EXPO_PUBLIC/EAS inputs on the build host **WHEN** the reviewed artifact builds **THEN** the explicit deployed identity controls the bundle and a mismatching output fails verification. | `infra/test/test_web_deployment.py:42` — test_browser_build_environment_retains_transport_settings_without_deploy_credentials<br>`infra/test/test_hosted_preview.py:194` — test_prepare_requires_guarded_environment_clean_source_and_actual_expo_flag | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### WEB-DEP-004 — Bind all web bytes to reviewed source and authority

Normative acceptance source: `openspec/changes/cloud-deployment-customer-access/specs/cloud-browser-delivery/spec.md` / `WEB-DEP-004`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-014-WEB-DEP-004-01 | The reviewed artifact is published — **GIVEN** matching signed service/web records, archive and deployed identity **WHEN** publication is admitted **THEN** exact file SHA-256/size/path/type and runtime bindings verify before upload. | `infra/test/test_web_deployment.py:117` — test_signature_source_environment_runtime_and_archive_bytes_are_bound<br>`infra/test/test_provenance.py:382` — test_cloud_image_manifest_and_local_config_must_bind_signed_source | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-014-WEB-DEP-004-02 | An archive is altered after approval — **GIVEN** a replaced file, duplicate entry or foreign identity **WHEN** the artifact is verified **THEN** publication fails before any byte is uploaded. | `infra/test/test_web_deployment.py:117` — test_signature_source_environment_runtime_and_archive_bytes_are_bound<br>`infra/test/test_provenance.py:382` — test_cloud_image_manifest_and_local_config_must_bind_signed_source | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### WEB-DEP-005 — Bound public artifact content

Normative acceptance source: `openspec/changes/cloud-deployment-customer-access/specs/cloud-browser-delivery/spec.md` / `WEB-DEP-005`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-014-WEB-DEP-005-01 | A normal Expo export is packaged — **GIVEN** reviewed HTML, JavaScript, metadata and supported assets **WHEN** limits hold **THEN** a deterministic ZIP and canonical manifest are created. | `infra/test/test_web_deployment.py:147` — test_public_asset_types_paths_symlinks_and_duplicate_zip_entries_are_rejected<br>`infra/test/test_hosted_preview.py:156` — test_unsafe_paths_duplicates_symlinks_and_expansion_limits_are_rejected | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-014-WEB-DEP-005-02 | Export contains a secret or traversal path — **GIVEN** .env, ../, absolute paths or a symlink **WHEN** packaging or archive admission occurs **THEN** the artifact is rejected. | `infra/test/test_web_deployment.py:147` — test_public_asset_types_paths_symlinks_and_duplicate_zip_entries_are_rejected<br>`infra/test/test_hosted_preview.py:156` — test_unsafe_paths_duplicates_symlinks_and_expansion_limits_are_rejected | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `128 MiB`, `16 MiB`, `256`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### WEB-DEP-006 — Publish immutably with an entry-point barrier

Normative acceptance source: `openspec/changes/cloud-deployment-customer-access/specs/cloud-browser-delivery/spec.md` / `WEB-DEP-006`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-014-WEB-DEP-006-01 | An identical approved release is retried — **GIVEN** existing same-prefix identical bytes **WHEN** publication repeats **THEN** those bytes verify and are preserved. | `infra/test/test_web_deployment.py:379` — test_disabled_foreign_origin_or_non_sigv4_distribution_cannot_publish_dns<br>`infra/test/test_hosted_preview.py:247` — test_upload_exact_bytes_authentication_disabled_permissions_and_safe_response | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-014-WEB-DEP-006-02 | A dependency conflicts or fails — **GIVEN** a different existing file or failed upload **WHEN** publication runs **THEN** it fails before committing index.html or reporting publication success. | `infra/test/test_web_deployment.py:396` — test_apex_foreign_private_zone_unready_tls_alias_and_existing_record_conflicts_fail_closed<br>`infra/test/test_hosted_preview.py:247` — test_upload_exact_bytes_authentication_disabled_permissions_and_safe_response | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### WEB-DEP-007 — Enforce browser security headers

Normative acceptance source: `openspec/changes/cloud-deployment-customer-access/specs/cloud-browser-delivery/spec.md` / `WEB-DEP-007`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-014-WEB-DEP-007-01 | Public transport probes execute — **GIVEN** a published release **WHEN** index.html is retrieved over HTTPS **THEN** byte integrity and required security headers verify. | `infra/test/test_web_deployment.py:213` — test_public_policy_rejects_missing_broadened_or_ambiguous_csp_and_transport | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-014-WEB-DEP-007-02 | The response lacks its security policy — **GIVEN** missing CSP/HSTS/no-sniff/frame denial **WHEN** public verification runs **THEN** deployment exits nonzero without a verified-access receipt. | `infra/test/test_web_deployment.py:213` — test_public_policy_rejects_missing_broadened_or_ambiguous_csp_and_transport | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### WEB-DEP-008 — Keep customer access claims accurate

Normative acceptance source: `openspec/changes/cloud-deployment-customer-access/specs/cloud-browser-delivery/spec.md` / `WEB-DEP-008`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-014-WEB-DEP-008-01 | A customer experiments in the browser — **GIVEN** the actual shared web application **WHEN** a guest or authorized customer uses its UI **THEN** browser storage/hardware limits and fictional data remain explicit. | `infra/test/test_web_deployment.py:42` — test_browser_build_environment_retains_transport_settings_without_deploy_credentials | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-014-WEB-DEP-008-02 | A deployment command succeeds — **GIVEN** only public HTTPS and worker health were checked **WHEN** the receipt is written **THEN** it does not claim signed-in browser, real-device, App Store or clinical validation. | `infra/test/test_web_deployment.py:199` — test_https_asset_deep_link_readiness_checks_do_not_claim_signed_in_acceptance<br>`infra/test/test_provenance.py:382` — test_cloud_image_manifest_and_local_config_must_bind_signed_source | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

### Authenticated ordinary-web live test source audit

Mapped existing cases: Related actual paths: AND-AUTH-001/003/005/006; AND-SYNC-002/003/004/007; AND-HIST-001/005/006; AND-EXP-001/002/003/006; AND-PRIV-003/004/005; WEB-DEP-003/008; complete full canonical scenarios remain separately assessed.

Assertion adequacy inspected: Read authenticated-live.spec.ts ordinary account test and helpers. Real issuer PKCE/token responses, notice/profile/context and deliberate synthetic-account Save then Upload. route.fetch sends actual finalize and validates202 before connection-reset abort; no fake success. Actual queued measurement-only result, reload clears account memory and reauthentication retrieves server history, actual export job/ZIP manifest/hash/single-check bytes, foreign404, reauthenticated deletion/current generation barrier, explicit new empty workspace and logout refresh-family refusal. Two actual viewport projects and private bounded fixture inventory; unknown records stop all-data deletion. Network receipts redacted; live config disables OAuth/token-bearing traces/HAR/screenshots.

Remaining limits: Writer active; planned final gate NOT_RUN. Current inspected ordinary case does not establish all governed consent/withdrawal, raw, pending-lab or research UI/API journeys; later governed work is WIP. No native encrypted persistence, public CloudFront delivery or physical sensing inferred. Need actual raw JUnit/redacted receipts/archive hashes and final gate wiring after freeze.


## Final corrected source evidence — e89897cc852a

# OTGD-014 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/cloud-deployment-customer-access/specs/cloud-browser-delivery/spec.md`; SHA256 `735f76493e8188925c157347dc22b0a2acad4cb76721f2ea8a7f324629631855`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-014/test-plan.md`. External review artifact only; PM controls import.

All 16 stable cases / 8 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`
- `uv run --project services/api python scripts/ci_gate.py infra-unit`
- `node --import tsx --test --test-reporter=junit test/*.test.ts (cwd: infra)`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-014-WEB-DEP-001-01 | Customer opens the published HTTPS origin — - **GIVEN** an admitted published application artifact - **WHEN** a customer opens WebOrigin - **THEN** CloudFront serves the application without public S3 access or credentials in the URL. | PARTIAL |
| OTGD-014-WEB-DEP-001-02 | Caller requests the bucket directly — - **GIVEN** an anonymous caller without distribution authority - **WHEN** it requests an S3 asset - **THEN** bucket policy does not grant public asset access. | PARTIAL |
| OTGD-014-WEB-DEP-002-01 | Customer opens a history deep link — - **GIVEN** published index.html - **WHEN** GET /history reaches the distribution - **THEN** the actual application entry point is returned. | PARTIAL |
| OTGD-014-WEB-DEP-002-02 | A missing script is requested — - **GIVEN** no matching .js asset - **WHEN** the browser requests that asset - **THEN** an origin error is preserved rather than returning a successful HTML body. | PARTIAL |
| OTGD-014-WEB-DEP-003-01 | QA and production are opened together — - **GIVEN** separate approved account deployments - **WHEN** both applications open - **THEN** each uses its own identity/API and QA remains visibly identified. | PARTIAL |
| OTGD-014-WEB-DEP-003-02 | A host environment attempts to override identity — - **GIVEN** conflicting APP/EXPO_PUBLIC/EAS inputs on the build host - **WHEN** the reviewed artifact builds - **THEN** the explicit deployed identity controls the bundle and a mismatching output fails verification. | PARTIAL |
| OTGD-014-WEB-DEP-004-01 | The reviewed artifact is published — - **GIVEN** matching signed service/web records, archive and deployed identity - **WHEN** publication is admitted - **THEN** exact file SHA-256/size/path/type and runtime bindings verify before upload. | PASS |
| OTGD-014-WEB-DEP-004-02 | An archive is altered after approval — - **GIVEN** a replaced file, duplicate entry or foreign identity - **WHEN** the artifact is verified - **THEN** publication fails before any byte is uploaded. | PASS |
| OTGD-014-WEB-DEP-005-01 | A normal Expo export is packaged — - **GIVEN** reviewed HTML, JavaScript, metadata and supported assets - **WHEN** limits hold - **THEN** a deterministic ZIP and canonical manifest are created. | PARTIAL |
| OTGD-014-WEB-DEP-005-02 | Export contains a secret or traversal path — - **GIVEN** .env, ../, absolute paths or a symlink - **WHEN** packaging or archive admission occurs - **THEN** the artifact is rejected. | PASS |
| OTGD-014-WEB-DEP-006-01 | An identical approved release is retried — - **GIVEN** existing same-prefix identical bytes - **WHEN** publication repeats - **THEN** those bytes verify and are preserved. | PARTIAL |
| OTGD-014-WEB-DEP-006-02 | A dependency conflicts or fails — - **GIVEN** a different existing file or failed upload - **WHEN** publication runs - **THEN** it fails before committing index.html or reporting publication success. | PASS |
| OTGD-014-WEB-DEP-007-01 | Public transport probes execute — - **GIVEN** a published release - **WHEN** index.html is retrieved over HTTPS - **THEN** byte integrity and required security headers verify. | PARTIAL |
| OTGD-014-WEB-DEP-007-02 | The response lacks its security policy — - **GIVEN** missing CSP/HSTS/no-sniff/frame denial - **WHEN** public verification runs - **THEN** deployment exits nonzero without a verified-access receipt. | PARTIAL |
| OTGD-014-WEB-DEP-008-01 | A customer experiments in the browser — - **GIVEN** the actual shared web application - **WHEN** a guest or authorized customer uses its UI - **THEN** browser storage/hardware limits and fictional data remain explicit. | PASS |
| OTGD-014-WEB-DEP-008-02 | A deployment command succeeds — - **GIVEN** only public HTTPS and worker health were checked - **WHEN** the receipt is written - **THEN** it does not claim signed-in browser, real-device, App Store or clinical validation. | PASS |
