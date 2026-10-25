# OTGD-011: verification plan

Canonical: `openspec/changes/canonical-operator-governance/specs/operator-authority/spec.md`; SHA-256 `a7bb7170b6fc7c119e8e93eae9783767876a8f861a71588027577172c30a80e2`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001 v1, D-002 v1, D-003 v1, D-004 v1 acknowledged through native messaging. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `services/api/tests/test_capture_policy.py` — `971a808c066b099c4006aab592d052aa3867d08cdfb10fbd0eb2f5288e5febae`
- `services/api/tests/test_capture_signing.py` — `bf0b38a0ec1eafef692a78ccb3d1bb0174d4f81b997a76c840b47ee1d2dc2751`
- `services/api/tests/test_operator_governance.py` — `54e64aca9b9379504922ef67bca4df1f45c518d42746530fec18b97aa58466bf`
- `services/api/tests/test_optical_evidence.py` — `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414`
- `services/api/tests/test_participant_acquisition.py` — `a9113ffb30c7907e12aad494ddfdf7d83afc96ef5f3d8c0668768158c2948b57`
- `services/api/tests/test_raw_capture.py` — `ebedc54a2c384fb5992fb61e1959b61d767ad41afbacd8ecf7aec6729710905e`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### OPERATOR-AUTHORITY-001 — Typed immutable submissions

Normative acceptance source: `openspec/changes/canonical-operator-governance/specs/operator-authority/spec.md` / `OPERATOR-AUTHORITY-001`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-011-OPERATOR-AUTHORITY-001-01 | Alteration of accepted submission — **GIVEN** a submitted version with a recorded canonical digest **WHEN** an administrator attempts to update its JSON, digest, version or submitting identity **THEN** PostgreSQL rejects the update and the original body remains reconstructable | `services/api/tests/test_operator_governance.py:140` — test_strict_bounded_typed_submission_rejects_bad_material<br>`services/api/tests/test_optical_evidence.py:206` — test_positive_reviewed_config_evidence_is_never_physical_or_model_qualification | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-011-OPERATOR-AUTHORITY-001-02 | Normalized submission and same-version retry — **GIVEN** a typed study body and a separately authorized submitter **WHEN** the submitter applies its first immutable version **THEN** the receipt exposes revision one, the exact normalized body and its canonical digest **AND** replaying the same version fails without replacing its body or creating a second submission decision | `services/api/tests/test_raw_capture.py:162` — test_original_device_signatures_and_signed_clock_bounds_verify_without_creating_health_values<br>`services/api/tests/test_operator_governance.py:140` — test_strict_bounded_typed_submission_rejects_bad_material | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `256 KiB`, `8785`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### OPERATOR-AUTHORITY-002 — Independent authenticated decisions

Normative acceptance source: `openspec/changes/canonical-operator-governance/specs/operator-authority/spec.md` / `OPERATOR-AUTHORITY-002`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-011-OPERATOR-AUTHORITY-002-01 | Claimed role paths for one credential — **GIVEN** one verified assumed-role credential and its actual IAM RoleId **WHEN** the caller supplies three different claimed path prefixes for that same role **THEN** every noncanonical path is rejected and it cannot self-approve or self-release | `services/api/tests/test_operator_governance.py:624` — test_cloud_identity_ignores_ambient_sdk_service_endpoints<br>`services/api/tests/test_capture_signing.py:118` — test_cloud_signer_pins_actual_kms_public_material_and_digest_operation | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-011-OPERATOR-AUTHORITY-002-02 | Three authenticated duties release approved material — **GIVEN** a submission under the named submitter role and an independent reviewer role **WHEN** the reviewer approves revision one and the independently authenticated releaser releases revision two **THEN** the active read validates three distinct canonical principals and the same submitted content hash **AND** the accepted history contains the exact request identity and reason for each decision | `services/api/tests/test_operator_governance.py:46` — test_immutable_submission_three_principals_lifecycle_history_and_revision<br>`services/api/tests/test_capture_signing.py:118` — test_cloud_signer_pins_actual_kms_public_material_and_digest_operation | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### OPERATOR-AUTHORITY-003 — Reviewable atomic lifecycle

Normative acceptance source: `openspec/changes/canonical-operator-governance/specs/operator-authority/spec.md` / `OPERATOR-AUTHORITY-003`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-011-OPERATOR-AUTHORITY-003-01 | Stale release or revoked configuration — **GIVEN** a reviewed version whose revision changed or whose approval was revoked **WHEN** an operator releases it using an earlier revision **THEN** the command fails and customer acquisition remains unavailable | `services/api/tests/test_operator_governance.py:579` — test_cli_dry_run_apply_history_and_authenticated_cloud_principal<br>`services/api/tests/test_raw_capture.py:344` — test_relabeling_terminal_evidence_or_revoking_signed_record_authority_fails | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-011-OPERATOR-AUTHORITY-003-02 | Dry-run, applied renewal and terminal history — **GIVEN** a valid typed renewal and its complete current dependencies **WHEN** the CLI runs without --apply **THEN** it displays the validated result and rolls back all registry changes **WHEN** three authorized operators submit, approve and release the renewal with --apply **THEN** the previous active version is atomically retired and both immutable bodies remain in history **AND** retiring the renewal immediately removes current authority while preserving accepted decisions | `services/api/tests/test_operator_governance.py:579` — test_cli_dry_run_apply_history_and_authenticated_cloud_principal<br>`services/api/tests/test_participant_acquisition.py:502` — test_same_material_digest_cannot_approve_changed_participant_instructions | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### OPERATOR-AUTHORITY-004 — Exact scientific and scope identities

Normative acceptance source: `openspec/changes/canonical-operator-governance/specs/operator-authority/spec.md` / `OPERATOR-AUTHORITY-004`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-011-OPERATOR-AUTHORITY-004-01 | Changed retention or duration with old proof — **GIVEN** an approved configuration and qualification for version one **WHEN** version two changes duration or retention but retains the task material hash and old proof **THEN** release fails because the qualification does not cover the new submitted version/digest | `services/api/tests/test_operator_governance.py:93` — test_changed_scope_cannot_reuse_scientific_hash_or_old_qualification<br>`services/api/tests/test_participant_acquisition.py:241` — test_protocol_requires_exact_bounded_content_complete_setup_and_method_rules | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-011-OPERATOR-AUTHORITY-004-02 | Exact reviewed configuration and device tuple — **GIVEN** approved study and retention versions, an exact configuration proof, and a device/calibration with matching key, hardware, firmware and channel **WHEN** an independent releaser releases the configuration **THEN** runtime validation resolves the exact active versions and accepts the matching configuration identity **AND** its material hash and complete submitted hash remain separately available for acquisition fencing | `services/api/tests/test_operator_governance.py:93` — test_changed_scope_cannot_reuse_scientific_hash_or_old_qualification<br>`services/api/tests/test_participant_acquisition.py:241` — test_protocol_requires_exact_bounded_content_complete_setup_and_method_rules | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### OPERATOR-AUTHORITY-005 — Current customer capabilities

Normative acceptance source: `openspec/changes/canonical-operator-governance/specs/operator-authority/spec.md` / `OPERATOR-AUTHORITY-005`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-011-OPERATOR-AUTHORITY-005-01 | Current approved task collection — **GIVEN** an active account, current notice and exact consent to an independently released study with approved task configuration **WHEN** capabilities are requested on a build containing the matching native task adapter **THEN** task collection is available with its exact public configuration references **AND** retirement, expiry, changed consent or account generation closes the applicable capability | `services/api/tests/test_operator_governance.py:544` — test_current_device_calibration_binding_and_software_inventory<br>`services/api/tests/test_participant_acquisition.py:400` — test_foreign_account_and_retired_generation_cannot_record_or_read_collection | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-011-OPERATOR-AUTHORITY-005-02 | Authorized configuration without a shipped adapter — **GIVEN** current consent and an independently released device configuration with a matching owned binding **WHEN** its declared transport is absent from the shipped server/client adapter inventory **THEN** authorization availability and software availability are reported separately **AND** acquisition is denied with HUMAN_ADAPTER_UNIMPLEMENTED rather than accepting fabricated measurements | `services/api/tests/test_operator_governance.py:544` — test_current_device_calibration_binding_and_software_inventory<br>`services/api/tests/test_participant_acquisition.py:414` — test_human_ecg_state_verification_is_unavailable_even_when_declared_verified | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### OPERATOR-AUTHORITY-006 — Capture approval fencing

Normative acceptance source: `openspec/changes/canonical-operator-governance/specs/operator-authority/spec.md` / `OPERATOR-AUTHORITY-006`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-011-OPERATOR-AUTHORITY-006-01 | Approval replaced while a grant is outstanding — **GIVEN** an issued acquisition grant for one approved configuration envelope **WHEN** a newly reviewed envelope replaces it before start **THEN** the old grant cannot start even when the scientific task hash is unchanged | `services/api/tests/test_operator_governance.py:229` — test_online_task_start_is_signed_and_old_grant_cannot_survive_envelope_renewal<br>`services/api/tests/test_participant_acquisition.py:502` — test_same_material_digest_cannot_approve_changed_participant_instructions | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-011-OPERATOR-AUTHORITY-006-02 | Current grant starts before an approval retirement — **GIVEN** a current owned started attempt and an issued grant pinned to the active configuration envelope **WHEN** start commits while holding the shared registry authority lock **THEN** the server records its actual start anchor and exact pinned approval identity | `services/api/tests/test_operator_governance.py:653` — test_actual_postgresql_retirement_waits_for_current_reference_acceptance_transaction<br>`services/api/tests/test_participant_acquisition.py:362` — test_config_retirement_and_withdrawal_after_acknowledgment_refuse_fresh_start | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### OPERATOR-AUTHORITY-007 — Signed scoped start

Normative acceptance source: `openspec/changes/canonical-operator-governance/specs/operator-authority/spec.md` / `OPERATOR-AUTHORITY-007`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-011-OPERATOR-AUTHORITY-007-01 | Owned reader starts under current signed authority — **GIVEN** current independent approvals and an owned signature-proven reader binding in the frozen context **WHEN** start supplies the exact frozen boot and fresh reader nonce **THEN** the server emits a verifiable domain-separated token for the approved channel and duration **AND** feature-only collection has signed raw-recording permission null | `services/api/tests/test_operator_governance.py:347` — test_bound_reader_start_token_comes_from_real_owned_proof_and_exact_frozen_boot<br>`services/api/tests/test_capture_signing.py:57` — test_signed_raw_recording_choice_is_not_an_unsigned_start_hint | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-011-OPERATOR-AUTHORITY-007-02 | Signing authority fails or unsigned raw choice changes — **GIVEN** a bound signing key and an issued current acquisition grant **WHEN** the key is missing, replaced, unavailable or produces an invalid signature **THEN** readiness or start fails closed and no acquisition authority is published **WHEN** a caller changes signed raw permission, channel or duration in a valid token **THEN** the signature fails and the reader cannot acquire under the changed scope | `services/api/tests/test_capture_signing.py:57` — test_signed_raw_recording_choice_is_not_an_unsigned_start_hint<br>`services/api/tests/test_operator_governance.py:347` — test_bound_reader_start_token_comes_from_real_owned_proof_and_exact_frozen_boot | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### OPERATOR-AUTHORITY-008 — Optical accepted-run identity

Normative acceptance source: `openspec/changes/canonical-operator-governance/specs/operator-authority/spec.md` / `OPERATOR-AUTHORITY-008`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-011-OPERATOR-AUTHORITY-008-01 | Current optical run retains descriptive evidence — **GIVEN** an owned started optical authorization under an independently released configuration **WHEN** the matching actual native run settles with bounded camera/frame evidence **THEN** the server binds its run and authorization identities and independently checks its arithmetic **AND** callback-relative response metadata remains separate from physically qualified projection fields | `services/api/tests/test_operator_governance.py:311` — test_prestart_invalid_optical_attempt_retains_arm_lineage_without_invented_camera_evidence<br>`services/api/tests/test_capture_policy.py:84` — test_cardiac_metadata_must_match_projection_and_start_requires_modality | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-011-OPERATOR-AUTHORITY-008-02 | Pre-start failure or relabeled camera run — **GIVEN** a saved arm attempt and a camera that fails before acquisition clocks or frames exist **WHEN** the client settles a reason-bearing invalid attempt with native evidence absent **THEN** the server preserves its original arm time and null acquisition features **WHEN** valid evidence claims another run, authorization or acquisition interval **THEN** acceptance fails rather than assigning that evidence to the current attempt **WHEN** an operator subsequently retires or replaces that approval **THEN** later settlement cannot use the stale grant and no accepted scientific snapshot is silently rewritten | `services/api/tests/test_operator_governance.py:311` — test_prestart_invalid_optical_attempt_retains_arm_lineage_without_invented_camera_evidence<br>`services/api/tests/test_optical_evidence.py:358` — test_descriptive_native_change_cannot_become_unqualified_pupil_response | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### OPERATOR-AUTHORITY-009 — Authenticated raw publication

Normative acceptance source: `openspec/changes/canonical-operator-governance/specs/operator-authority/spec.md` / `OPERATOR-AUTHORITY-009`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-011-OPERATOR-AUTHORITY-009-01 | Original device samples are published under current permission — **GIVEN** exact released configuration, explicit current recording/upload consent and an owned started authorization **WHEN** the original signed ECG chunks or optical ROI bytes match the accepted acquisition ledger **THEN** completion records the exact immutable object version, codec and evidence digests before marking the artifact verified **AND** research eligibility remains separate from raw transport verification | `services/api/tests/test_raw_capture.py:162` — test_original_device_signatures_and_signed_clock_bounds_verify_without_creating_health_values<br>`services/api/tests/test_optical_evidence.py:429` — test_roi_codec_verification_binds_actual_luminance_native_ledger_and_attempt | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-011-OPERATOR-AUTHORITY-009-02 | Matching file hash contains forged or relabeled samples — **GIVEN** a raw artifact whose uploaded bytes match its declared file hash and length **WHEN** a sample signature, signed clock, owner, capture identity, frame digest or approved sample budget is invalid **THEN** completion fails and the artifact remains quarantined without a verification receipt **AND** a historical verified state without an owned matching codec receipt cannot authorize raw export | `services/api/tests/test_raw_capture.py:162` — test_original_device_signatures_and_signed_clock_bounds_verify_without_creating_health_values<br>`services/api/tests/test_participant_acquisition.py:414` — test_human_ecg_state_verification_is_unavailable_even_when_declared_verified | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.
