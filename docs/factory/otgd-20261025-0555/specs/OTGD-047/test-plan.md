# OTGD-047: verification plan

Canonical: `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md`; SHA-256 `8dd256054b4cc55a8fe8141b5589fa39cf9a655cf1af16cb28cde8ed0c4622ea`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001 v1, D-002 v1, D-003 v1, D-004 v1 acknowledged through native messaging. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `infra/test/test_hosted_preview.py` — `7d44b7bd8f5482bf65109d9002908eefa2ee480b8eba524ab4fe3a24b240d8ce`
- `infra/test/test_store_inputs.py` — `8fb54f33f66e14f35df22dc56bfb41713f48208a63b5f35ec2e30a48deafeab0`
- `services/api/tests/test_mobile_store_release.py` — `b371b7707c6106868225fc5a00847fc4702c755ef0eb1522eb1fa11776d526d6`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### STORE-001 — Define separate real-device release targets

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md` / `STORE-001`.

Prerequisites and limits: BLOCKED external store: genuine protected EAS/project/signing credentials, Android registered upload signer and complete AAB, macOS codesign/provisioned iOS device IPA, persistent operator submission fence and actual provider observations; no upload/publication authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-047-STORE-001-01 | A real store candidate is planned — **GIVEN** the selected QA-store or production profile **WHEN** its platform configuration is resolved **THEN** device artifact type, environment/package and version policy are explicit. | `infra/test/test_hosted_preview.py:113` — test_ios_device_prod_platform_and_missing_bundle_are_rejected<br>`infra/test/test_store_inputs.py:487` — test_build_stages_selected_signer_and_backend_scope_without_store_credentials | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-047-STORE-001-02 | A guest archive is offered for store release — **GIVEN** a local/guest/simulator artifact or incompatible package **WHEN** store admission runs **THEN** it refuses rather than relabeling the artifact. | `services/api/tests/test_mobile_store_release.py:220` — test_release_config_rejects_local_guest_or_ambiguous_targets<br>`infra/test/test_hosted_preview.py:113` — test_ios_device_prod_platform_and_missing_bundle_are_rejected | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### STORE-002 — Validate actual project and backend identity

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md` / `STORE-002`.

Prerequisites and limits: BLOCKED external store: genuine protected EAS/project/signing credentials, Android registered upload signer and complete AAB, macOS codesign/provisioned iOS device IPA, persistent operator submission fence and actual provider observations; no upload/publication authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-047-STORE-002-01 | Cloud identity matches the compiled app — **GIVEN** current project metadata and admitted cloud outputs including the exact callback **WHEN** build/submit admission runs **THEN** the candidate uses those exact public identity values. | `services/api/tests/test_mobile_store_release.py:281` — test_exact_cloud_metadata_and_embedded_public_origins_bind_store_build<br>`infra/test/test_store_inputs.py:312` — test_external_paths_and_invalid_store_config_leave_no_staging | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-047-STORE-002-02 | Production lists the wrong redirect — **GIVEN** otgd-prod://oauth/callback or a foreign project/backend/callback **WHEN** admission checks the production package **THEN** it fails before build or submission. | `services/api/tests/test_mobile_store_release.py:1144` — test_backend_admission_rechecks_signed_release_actual_running_image_and_live_native_callback<br>`infra/test/test_store_inputs.py:312` — test_external_paths_and_invalid_store_config_leave_no_staging | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### STORE-003 — Stage only admitted immutable source

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md` / `STORE-003`.

Prerequisites and limits: BLOCKED external store: genuine protected EAS/project/signing credentials, Android registered upload signer and complete AAB, macOS codesign/provisioned iOS device IPA, persistent operator submission fence and actual provider observations; no upload/publication authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-047-STORE-003-01 | Exact source and genuine release evidence agree — **GIVEN** the allowed trusted GitHub release event and current signed backend/QA binding **WHEN** source is staged outside the development checkout **THEN** the provider receives only the admitted immutable tree. | `services/api/tests/test_mobile_store_release.py:704` — test_no_backend_release_no_new_store_job_and_immutable_output_refuses_reuse<br>`infra/test/test_store_inputs.py:487` — test_build_stages_selected_signer_and_backend_scope_without_store_credentials | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-047-STORE-003-02 | A local JSON or stale successful run is substituted — **GIVEN** missing jobs, wrong commit/project, unsupported release event or edited evidence **WHEN** build/submit admission runs **THEN** no provider mutation occurs. | `services/api/tests/test_mobile_store_release.py:1144` — test_backend_admission_rechecks_signed_release_actual_running_image_and_live_native_callback<br>`infra/test/test_store_inputs.py:487` — test_build_stages_selected_signer_and_backend_scope_without_store_credentials | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### STORE-004 — Provide a mutation-free plan

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md` / `STORE-004`.

Prerequisites and limits: BLOCKED external store: genuine protected EAS/project/signing credentials, Android registered upload signer and complete AAB, macOS codesign/provisioned iOS device IPA, persistent operator submission fence and actual provider observations; no upload/publication authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-047-STORE-004-01 | An operator reviews the intended command — **GIVEN** a valid nonsecret store configuration **WHEN** plan runs without service credentials **THEN** the explicit stages and external requirements are returned without mutation. | `infra/test/test_store_inputs.py:487` — test_build_stages_selected_signer_and_backend_scope_without_store_credentials<br>`services/api/tests/test_mobile_store_release.py:246` — test_tool_environment_preserves_transport_but_never_builds_with_service_secrets | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-047-STORE-004-02 | An invalid or ambiguous target is supplied — **GIVEN** opposite environment, missing platform or placeholder identity **WHEN** plan runs **THEN** validation fails before a provider command. | `infra/test/test_store_inputs.py:487` — test_build_stages_selected_signer_and_backend_scope_without_store_credentials<br>`services/api/tests/test_mobile_store_release.py:541` — test_exact_build_inspection_then_explicit_draft_submission_and_status_have_signed_distinct_receipts | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### STORE-005 — Pin provider tooling and scope credentials

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md` / `STORE-005`.

Prerequisites and limits: BLOCKED external store: genuine protected EAS/project/signing credentials, Android registered upload signer and complete AAB, macOS codesign/provisioned iOS device IPA, persistent operator submission fence and actual provider observations; no upload/publication authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-047-STORE-005-01 | Approved credentials and exact CLI are available — **GIVEN** verified pinned tooling and scoped genuine provider credentials **WHEN** build/submission starts **THEN** the child receives only its required authentication and transport. | `infra/test/test_store_inputs.py:487` — test_build_stages_selected_signer_and_backend_scope_without_store_credentials<br>`services/api/tests/test_mobile_store_release.py:281` — test_exact_cloud_metadata_and_embedded_public_origins_bind_store_build | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-047-STORE-005-02 | Tooling or credential state is unavailable — **GIVEN** a different CLI, missing genuine signing/account access or a Node preload **WHEN** the operation starts **THEN** it refuses or excludes the unapproved setting without inventing a build. | `infra/test/test_store_inputs.py:487` — test_build_stages_selected_signer_and_backend_scope_without_store_credentials<br>`services/api/tests/test_mobile_store_release.py:910` — test_clean_isolated_source_preserves_exact_git_revision_and_excludes_untracked_files | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### STORE-006 — Bind builds to explicit provider records

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md` / `STORE-006`.

Prerequisites and limits: BLOCKED external store: genuine protected EAS/project/signing credentials, Android registered upload signer and complete AAB, macOS codesign/provisioned iOS device IPA, persistent operator submission fence and actual provider observations; no upload/publication authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-047-STORE-006-01 | The provider completes the selected build — **GIVEN** matching official finished-build metadata **WHEN** the completion receipt is written **THEN** it identifies the actual build UUID/version and admitted project/source. | `infra/test/test_store_inputs.py:756` — test_platform_credentials_reject_wrong_scope_unknown_wrappers_and_bad_content<br>`services/api/tests/test_mobile_store_release.py:228` — test_selected_platform_only_and_private_files_are_bounded | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-047-STORE-006-02 | Build execution merely starts — **GIVEN** an accepted request with pending/failed/wrong-project output **WHEN** completion is assessed **THEN** no finished artifact or downloadable store app is claimed. | `infra/test/test_store_inputs.py:756` — test_platform_credentials_reject_wrong_scope_unknown_wrappers_and_bad_content<br>`services/api/tests/test_mobile_store_release.py:281` — test_exact_cloud_metadata_and_embedded_public_origins_bind_store_build | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### STORE-007 — Submit only the exact verified candidate

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md` / `STORE-007`.

Prerequisites and limits: BLOCKED external store: genuine protected EAS/project/signing credentials, Android registered upload signer and complete AAB, macOS codesign/provisioned iOS device IPA, persistent operator submission fence and actual provider observations; no upload/publication authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-047-STORE-007-01 | A genuine exact candidate is submitted — **GIVEN** the current finished-build UUID and real matching store record **WHEN** explicit submission is requested **THEN** that exact candidate is sent and provider observations are recorded. | `services/api/tests/test_mobile_store_release.py:406` — test_actual_submission_receipt_never_means_public_store_availability<br>`infra/test/test_store_inputs.py:656` — test_candidate_receipt_scope_signer_and_submission_reuse_are_checked | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-047-STORE-007-02 | Another build is substituted — **GIVEN** latest selection, a foreign UUID or altered receipt/metadata **WHEN** submission admission runs **THEN** it refuses before upload. | `services/api/tests/test_mobile_store_release.py:406` — test_actual_submission_receipt_never_means_public_store_availability<br>`infra/test/test_store_inputs.py:1244` — test_protected_package_refuses_artifact_conflicts_invalid_json_and_oversize_before_staging | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### STORE-008 — Separate submission from public availability

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md` / `STORE-008`.

Prerequisites and limits: BLOCKED external store: genuine protected EAS/project/signing credentials, Android registered upload signer and complete AAB, macOS codesign/provisioned iOS device IPA, persistent operator submission fence and actual provider observations; no upload/publication authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-047-STORE-008-01 | An upload request succeeds — **GIVEN** a successful provider submission request **WHEN** status is reported **THEN** it reports only actual observed submission/processing evidence and no public-download claim. | `services/api/tests/test_mobile_store_release.py:541` — test_exact_build_inspection_then_explicit_draft_submission_and_status_have_signed_distinct_receipts<br>`infra/test/test_store_inputs.py:817` — test_artifact_download_auth_is_sent_only_to_github_and_bytes_are_bounded | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-047-STORE-008-02 | Apple or Google has not approved delivery — **GIVEN** processing/review/tester/enrollment or first-upload work remains **WHEN** the operator asks for installation **THEN** documentation names the required platform step without inventing a store URL or completed publication. | `services/api/tests/test_mobile_store_release.py:541` — test_exact_build_inspection_then_explicit_draft_submission_and_status_have_signed_distinct_receipts<br>`infra/test/test_store_inputs.py:617` — test_status_preserves_original_receipts_without_staging_private_credentials | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### STORE-009 — Preserve bounded operation receipts

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md` / `STORE-009`.

Prerequisites and limits: BLOCKED external store: genuine protected EAS/project/signing credentials, Android registered upload signer and complete AAB, macOS codesign/provisioned iOS device IPA, persistent operator submission fence and actual provider observations; no upload/publication authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-047-STORE-009-01 | A successful operation is retained — **GIVEN** actual matching provider observations **WHEN** a receipt is created **THEN** it records the performed stage and identity without overwriting earlier evidence. | `services/api/tests/test_mobile_store_release.py:1064` — test_ios_fixture_checks_actual_platform_identity_provisioning_and_runtime_tuple<br>`infra/test/test_store_inputs.py:635` — test_signed_child_receipts_bind_original_build_bytes_and_logical_configuration | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-047-STORE-009-02 | An external stage fails — **GIVEN** denied credentials, wrong metadata or failed build/upload **WHEN** execution stops **THEN** failure is explicit and earlier provider work is not falsely described as rolled back. | `infra/test/test_store_inputs.py:635` — test_signed_child_receipts_bind_original_build_bytes_and_logical_configuration<br>`services/api/tests/test_mobile_store_release.py:541` — test_exact_build_inspection_then_explicit_draft_submission_and_status_have_signed_distinct_receipts | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### STORE-010 — Inspect the actual signed device artifact

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md` / `STORE-010`.

Prerequisites and limits: BLOCKED external store: genuine protected EAS/project/signing credentials, Android registered upload signer and complete AAB, macOS codesign/provisioned iOS device IPA, persistent operator submission fence and actual provider observations; no upload/publication authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-047-STORE-010-01 | A genuine device candidate matches authority — **GIVEN** the exact provider build bytes, reviewed signer and supported verifier **WHEN** inspection executes **THEN** the signed receipt binds its actual digest and observed native/configuration/signing metadata. | `infra/test/test_store_inputs.py:656` — test_candidate_receipt_scope_signer_and_submission_reuse_are_checked<br>`services/api/tests/test_mobile_store_release.py:541` — test_exact_build_inspection_then_explicit_draft_submission_and_status_have_signed_distinct_receipts | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-047-STORE-010-02 | Metadata describes a different binary — **GIVEN** a simulator IPA, unsigned/foreign AAB, wrong package/version/backend/guest marker or different signer **WHEN** binary inspection runs **THEN** metadata alone cannot admit it and no submission occurs. | `infra/test/test_store_inputs.py:656` — test_candidate_receipt_scope_signer_and_submission_reuse_are_checked<br>`services/api/tests/test_mobile_store_release.py:1144` — test_backend_admission_rechecks_signed_release_actual_running_image_and_live_native_callback | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### STORE-011 — Fence uncertain submission outcomes

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md` / `STORE-011`.

Prerequisites and limits: BLOCKED external store: genuine protected EAS/project/signing credentials, Android registered upload signer and complete AAB, macOS codesign/provisioned iOS device IPA, persistent operator submission fence and actual provider observations; no upload/publication authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-047-STORE-011-01 | The provider accepted a request before interruption — **GIVEN** a durable signed intent and an uncertain CLI outcome **WHEN** the operator supplies the actual submission UUID for reconciliation **THEN** the tool queries that exact matching provider record without another upload. | `services/api/tests/test_mobile_store_release.py:599` — test_submission_persists_signed_owner_only_fence_before_provider_call<br>`infra/test/test_store_inputs.py:1183` — test_pack_rejects_completed_outcome_for_different_build_or_original_intent | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-047-STORE-011-02 | The operator repeats an unknown upload without identity — **GIVEN** an existing pending intent and no matching provider submission record **WHEN** submission is retried **THEN** it refuses duplicate mutation and preserves the uncertainty. | `services/api/tests/test_mobile_store_release.py:599` — test_submission_persists_signed_owner_only_fence_before_provider_call<br>`infra/test/test_store_inputs.py:922` — test_seal_preserves_pending_submission_intent_and_completed_submission | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### STORE-012 — Verify the complete Android upload signature

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md` / `STORE-012`.

Prerequisites and limits: BLOCKED external store: genuine protected EAS/project/signing credentials, Android registered upload signer and complete AAB, macOS codesign/provisioned iOS device IPA, persistent operator submission fence and actual provider observations; no upload/publication authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-047-STORE-012-01 | A complete registered-upload candidate is supplied — **GIVEN** an AAB with the expected upload certificate and all payload entries signed **WHEN** actual signature and manifest inspection runs **THEN** the admitted digest/package/version/signer are recorded. | `services/api/tests/test_mobile_store_release.py:948` — test_android_signed_jar_integrity_and_trusted_upload_certificate_reject_changed_bytes<br>`infra/test/test_store_inputs.py:656` — test_candidate_receipt_scope_signer_and_submission_reuse_are_checked | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-047-STORE-012-02 | Unsigned payload is appended to a signed archive — **GIVEN** a previously signed JAR/AAB containing newly appended unsigned payload **WHEN** jarsigner returns a general success with incomplete entry coverage **THEN** admission still rejects the candidate before submission. | `services/api/tests/test_mobile_store_release.py:948` — test_android_signed_jar_integrity_and_trusted_upload_certificate_reject_changed_bytes<br>`infra/test/test_store_inputs.py:656` — test_candidate_receipt_scope_signer_and_submission_reuse_are_checked | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### STORE-013 — Verify genuine iOS device signing and provisioning

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md` / `STORE-013`.

Prerequisites and limits: BLOCKED external store: genuine protected EAS/project/signing credentials, Android registered upload signer and complete AAB, macOS codesign/provisioned iOS device IPA, persistent operator submission fence and actual provider observations; no upload/publication authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-047-STORE-013-01 | A genuine store-signed device IPA is inspected — **GIVEN** the independently expected Apple distribution identity and matching profile **WHEN** actual macOS signing/platform inspection runs **THEN** the device artifact and observed signing metadata bind the receipt. | `services/api/tests/test_mobile_store_release.py:1064` — test_ios_fixture_checks_actual_platform_identity_provisioning_and_runtime_tuple<br>`infra/test/test_hosted_preview.py:113` — test_ios_device_prod_platform_and_missing_bundle_are_rejected | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-047-STORE-013-02 | A simulator or unsupported signing path is used — **GIVEN** an iOS simulator ZIP, foreign/development identity or unsupported verifier **WHEN** admission executes **THEN** no store upload or successful Apple-signing claim occurs. | `services/api/tests/test_mobile_store_release.py:1064` — test_ios_fixture_checks_actual_platform_identity_provisioning_and_runtime_tuple<br>`infra/test/test_hosted_preview.py:113` — test_ios_device_prod_platform_and_missing_bundle_are_rejected | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### STORE-014 — Execute the exact verified provider toolchain

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md` / `STORE-014`.

Prerequisites and limits: BLOCKED external store: genuine protected EAS/project/signing credentials, Android registered upload signer and complete AAB, macOS codesign/provisioned iOS device IPA, persistent operator submission fence and actual provider observations; no upload/publication authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-047-STORE-014-01 | Pinned verified CLI installation matches the lock — **GIVEN** the reviewed exact EAS archive integrity and matching isolated toolchain tree **WHEN** the provider CLI is executed **THEN** that inspected installation supplies the command. | `services/api/tests/test_mobile_store_release.py:745` — test_pinned_tool_package_integrity_and_actual_public_eas_variable_scope | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-047-STORE-014-02 | Execution selects different CLI bytes — **GIVEN** changed package integrity, substituted tree or a separate unchecked fetch **WHEN** toolchain admission runs **THEN** no provider operation or credential-bearing CLI execution occurs. | `services/api/tests/test_mobile_store_release.py:745` — test_pinned_tool_package_integrity_and_actual_public_eas_variable_scope<br>`infra/test/test_store_inputs.py:1215` — test_cli_pack_to_protected_ciphertext_reconciliation_preserves_inner_bytes | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### STORE-015 — Bound local provider subprocesses

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md` / `STORE-015`.

Prerequisites and limits: BLOCKED external store: genuine protected EAS/project/signing credentials, Android registered upload signer and complete AAB, macOS codesign/provisioned iOS device IPA, persistent operator submission fence and actual provider observations; no upload/publication authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-047-STORE-015-01 | A CLI child exceeds its deadline — **GIVEN** an owned local process tree with scoped provider authentication **WHEN** timeout or output overflow occurs **THEN** the group is terminated/reaped and the unknown remote state is preserved. | `services/api/tests/test_mobile_store_release.py:848` — test_owned_tool_process_group_stops_spawned_child_on_bounded_failure<br>`infra/test/test_store_inputs.py:942` — test_seal_refuses_signed_child_output_for_foreign_build_or_intent | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-047-STORE-015-02 | Another local process is running — **GIVEN** an unrelated process outside the owned group **WHEN** provider cleanup runs **THEN** that process remains untouched. | `services/api/tests/test_mobile_store_release.py:848` — test_owned_tool_process_group_stops_spawned_child_on_bounded_failure<br>`infra/test/test_store_inputs.py:1183` — test_pack_rejects_completed_outcome_for_different_build_or_original_intent | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### STORE-016 — Supply a deliberate cloud operator workflow

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md` / `STORE-016`.

Prerequisites and limits: BLOCKED external store: genuine protected EAS/project/signing credentials, Android registered upload signer and complete AAB, macOS codesign/provisioned iOS device IPA, persistent operator submission fence and actual provider observations; no upload/publication authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-047-STORE-016-01 | The operator has configured actual protected inputs — **GIVEN** reviewed main source, protected store environment and genuine provider/cloud/signing access **WHEN** the deliberate browser workflow is dispatched **THEN** it builds/inspects, reads status or reconciles the exact original intent/submission without a local Mac or clone; initial upload remains a separate persistent operator operation. | `services/api/tests/test_mobile_store_release.py:575` — test_lost_submission_response_persists_exact_intent_and_reconciles_without_second_upload<br>`infra/test/test_store_inputs.py:713` — test_browser_submit_cannot_stage_or_authorize_a_fresh_submission | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-047-STORE-016-02 | A fresh upload is requested from ephemeral Actions — **GIVEN** only a signed build receipt or a missing original pending intent/submission UUID **WHEN** a fresh submit or incomplete reconcile operation is requested **THEN** it refuses before private credential staging or AWS/EAS/store action rather than losing an upload fence on runner failure; GitHub artifact metadata reads may precede refusal. | `services/api/tests/test_mobile_store_release.py:639` — test_fsync_failure_leaves_fence_and_never_launches_store_upload<br>`infra/test/test_store_inputs.py:1244` — test_protected_package_refuses_artifact_conflicts_invalid_json_and_oversize_before_staging | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-047-STORE-016-03 | The workflow exists only on an unmerged branch — **GIVEN** missing default-main registration/protection/credentials **WHEN** delivery is reported **THEN** it describes supplied automation and prerequisites without claiming execution. | `services/api/tests/test_mobile_store_release.py:541` — test_exact_build_inspection_then_explicit_draft_submission_and_status_have_signed_distinct_receipts<br>`infra/test/test_store_inputs.py:487` — test_build_stages_selected_signer_and_backend_scope_without_store_credentials | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### STORE-017 — Encrypt operator handoffs in public repositories

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md` / `STORE-017`.

Prerequisites and limits: BLOCKED external store: genuine protected EAS/project/signing credentials, Android registered upload signer and complete AAB, macOS codesign/provisioned iOS device IPA, persistent operator submission fence and actual provider observations; no upload/publication authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-047-STORE-017-01 | A later operation consumes the same exact candidate — **GIVEN** a same-repository encrypted artifact and matching protected key/scope **WHEN** the workflow authenticates and stages it **THEN** original receipt bytes and cross-receipt hashes survive for normal signed/provider admission. | `infra/test/test_store_inputs.py:635` — test_signed_child_receipts_bind_original_build_bytes_and_logical_configuration<br>`services/api/tests/test_mobile_store_release.py:281` — test_exact_cloud_metadata_and_embedded_public_origins_bind_store_build | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-047-STORE-017-02 | An artifact or ciphertext is substituted — **GIVEN** a wrong repository/source/platform, altered ciphertext or arbitrary archive path **WHEN** handoff admission runs **THEN** it refuses before credentials or receipt data are exposed. | `infra/test/test_store_inputs.py:635` — test_signed_child_receipts_bind_original_build_bytes_and_logical_configuration<br>`services/api/tests/test_mobile_store_release.py:281` — test_exact_cloud_metadata_and_embedded_public_origins_bind_store_build | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `32`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### STORE-018 — Transfer an operator-held pending intent without upload mutation

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md` / `STORE-018`.

Prerequisites and limits: BLOCKED external store: genuine protected EAS/project/signing credentials, Android registered upload signer and complete AAB, macOS codesign/provisioned iOS device IPA, persistent operator submission fence and actual provider observations; no upload/publication authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-047-STORE-018-01 | A persistent operator transfers an uncertain existing submission — **GIVEN** the original signed build and pending intent, trusted public key and protected encryption key **WHEN** pack completes and its ciphertext is supplied for browser reconciliation **THEN** the exact original byte links survive; the existing provider UUID is queried without another upload. | `infra/test/test_store_inputs.py:1215` — test_cli_pack_to_protected_ciphertext_reconciliation_preserves_inner_bytes<br>`services/api/tests/test_mobile_store_release.py:599` — test_submission_persists_signed_owner_only_fence_before_provider_call | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-047-STORE-018-02 | A transfer replaces or ambiguously selects evidence — **GIVEN** changed receipt bytes, wrong signature/scope, a foreign pending intent or both input selectors **WHEN** packing or browser admission is attempted **THEN** it refuses without a provider mutation or private credential staging. | `infra/test/test_store_inputs.py:1136` — test_pack_refuses_foreign_scope_config_signer_and_changed_receipt_bytes_before_staging<br>`services/api/tests/test_mobile_store_release.py:948` — test_android_signed_jar_integrity_and_trusted_upload_certificate_reject_changed_bytes | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.
