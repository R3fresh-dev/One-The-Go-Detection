# OTGD-010 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/authorized-raw-export/specs/raw-export-authorization/spec.md`; SHA256 `6e7ff5b60880e7234eec431ccb702b3e452b6a1d6e76a01720cb60b478782993`.

19 cases, 8 requirements: PARTIAL 8, PASS 11. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-010-RAW-EXP-001-01 — PARTIAL

Recording exists without export approval — - **GIVEN** an owned retained recording and current optional recording consent - **WHEN** a participant requests its raw export without separate released authority - **THEN** raw export is denied and metadata-only export remains available.

Current proof: Retained recording fixture has recording consent but scopes=[] and freeze denied absent released export approval; metadata-only DTO remains valid and separate HTTP metadata export completes.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_export.py::test_recording_upload_approval_never_grants_export` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 184; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_metadata_only_request_remains_default_scope_and_cannot_carry_raw_approval` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 234; 5 current observation(s).
- `services/api/tests/test_api.py::test_export_scope_and_authenticated_download` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 276; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “metadata-only export remains available” in the same owned-retained-recording/no-export-approval state: positive HTTP metadata test has a different fixture; no same-context metadata-only request assertion.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 1fb2b3fc62cdb35f2097554b59247bacd1eece9dcd505348bb622d254d0d55a2. Actual current source and raw evidence supply this disposition.

## OTGD-010-RAW-EXP-001-02 — PASS

The reviewer is also the submitter — - **GIVEN** a submitted raw-export version - **WHEN** the same verified principal tries to approve or release it - **THEN** the registry rejects the transition and no current export grant exists.

Current proof: Same submitting principal approval is rejected, reviewer self-release rejected, and freeze_export refuses the unreleased grant. Fictional principal software logic only.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_export.py::test_distinct_submit_review_release_required` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 205; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA fb65a21ffb462d1f9cc7769f4828a8ceac648f4f6baed5c6e7f58664f3f516fa. Actual current source and raw evidence supply this disposition.

## OTGD-010-RAW-EXP-001-03 — PASS

Three distinct authorized principals release an exact grant — - **GIVEN** current independently approved dependencies and a typed owner/generation grant - **WHEN** distinct submitter, reviewer and releaser complete its real registry lifecycle - **THEN** its immutable version and content hash admit only the exact approved scope.

Current proof: accepted() invokes real typed submit/approve/release under three distinct local principals; validated scope pins source version, notices and bytes digest; changed authority version/hash, notice, owner artifact and acknowledgment clocks are denied. This proves software scope, not actual human/cloud approval.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_export.py::test_actual_distinct_release_freezes_exact_sources_and_public_scope` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 191; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_scope_revision_hash_owner_and_confirmation_clock_rechecked` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 245; 35 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 0f877cac689f1994a198db56a847e8e4002e01068254198ad23cf2d53590a003. Actual current source and raw evidence supply this disposition.

## OTGD-010-RAW-EXP-002-01 — PASS

Nine valid authorities contain maximum-sized notices — - **GIVEN** nine current independently released owned authorities - **WHEN** the client follows each authority cursor - **THEN** all nine are offered across bounded pages without response overflow.

Current proof: Creates nine released grants with 16KiB notices and 4096-character purposes, follows cursors, asserts <=4 scopes and <=512KiB each page, exact nine IDs, exactly three pages.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_export.py::test_current_authority_pages_have_bounded_bytes_and_explicit_complete_cursors` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 662; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 74a380545f74a4c725e10966b1dfc109a3774da976e3ba8be9513d7340036c23. Actual current source and raw evidence supply this disposition.

## OTGD-010-RAW-EXP-002-02 — PASS

A source exceeds the complete export byte cap — - **GIVEN** a retained recording larger than its authority's uncompressed cap - **WHEN** current export choices are requested - **THEN** that source cannot be selected and other eligible choices remain usable.

Current proof: Over-cap sole source is omitted and selecting it raises EXPORT_TOO_LARGE. Eligible surviving source usable, acceptedPOSTreplay denied after exportauthorityretirement, exactno-storeattachment and fullcombinedbudget fail/nooutput asserted.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_export.py::test_individually_over_export_budget_source_is_not_offered` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 685; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_over_budget_source_does_not_hide_or_disable_an_eligible_owned_choice` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 695; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_accepted_post_replay_after_export_authority_retirement_hides_original_scope` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 488; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_actual_http_async_worker_zip_download_replay_expiry_and_foreign_denial` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 418; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_raw_members_fit_but_complete_structured_manifest_archive_exceeds_grant` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 511; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Explicit SQLite/storage double fixture; realS3/LocalStack and whole raw selection clauses remain distinct. Final numeric export positive/refusal controls are mapped separately under FINAL_NUMERIC_EXPORT.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA e140d094b11c90e3da0beba18f8f34d25c9d8b3161e6ac6198d735900fc3fa00. Actual current source and raw evidence supply this disposition.

## OTGD-010-RAW-EXP-003-01 — PARTIAL

Consent to recording is reused as export confirmation — - **GIVEN** the participant approved optional recording earlier - **WHEN** raw export is requested without its separate confirmed export notice - **THEN** the request fails without creating a raw job.

Current proof: DTO rejects include_raw without scope and malformed/nonboolean confirmation.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_export.py::test_metadata_only_request_remains_default_scope_and_cannot_carry_raw_approval` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 234; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_explicit_participant_scope_has_no_truthy_or_arbitrary_storage_escape` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 229; 20 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “without creating a raw job”: no raw HTTP request with existing recording consent but absent separate notice/confirmation followed by DB job-count/state assertion.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8bcc45f82622477a3bf96d64335cc4e65771d0cd0ab960d03e5999937bd92eb9. Actual current source and raw evidence supply this disposition.

## OTGD-010-RAW-EXP-003-02 — PASS

An accepted reply was lost and the grant is later retired — - **GIVEN** an accepted raw export and its original request key/body - **WHEN** the request is retried after authority retirement - **THEN** current admission denies it rather than disclosing the stale approved scope.

Current proof: Exact accepted POST replay denied after raw consent revocation; delayed download denied for retired authority. Eligible surviving source usable, acceptedPOSTreplay denied after exportauthorityretirement, exactno-storeattachment and fullcombinedbudget fail/nooutput asserted.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_export.py::test_http_accepted_raw_replay_and_new_download_are_denied_after_revocation` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 470; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_delayed_http_download_discloses_no_bytes_after_current_authority_loss` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 565; 20 current observation(s).
- `services/api/tests/test_raw_export.py::test_over_budget_source_does_not_hide_or_disable_an_eligible_owned_choice` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 695; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_accepted_post_replay_after_export_authority_retirement_hides_original_scope` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 488; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_actual_http_async_worker_zip_download_replay_expiry_and_foreign_denial` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 418; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_raw_members_fit_but_complete_structured_manifest_archive_exceeds_grant` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 511; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Explicit SQLite/storage double fixture; realS3/LocalStack and whole raw selection clauses remain distinct. Final numeric export positive/refusal controls are mapped separately under FINAL_NUMERIC_EXPORT.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA ba3f35665f54f0786b950b7936f2b3278fb2fded97b3b6d3ef1605b1807554f2. Actual current source and raw evidence supply this disposition.

## OTGD-010-RAW-EXP-003-03 — PARTIAL

A separately confirmed owned selection creates a stable job — - **GIVEN** exact current authority and an explicitly acknowledged export notice - **WHEN** the customer submits selected owned artifacts and retries the identical body/key - **THEN** one pending job preserves the original selected sources and acknowledgement.

Current proof: Real HTTP identical body/key returns same pending job ID; controller lost-receipt retry preserves exact body/key and single queued raw item.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_export.py::test_actual_http_async_worker_zip_download_replay_expiry_and_foreign_denial` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 418; 5 current observation(s).
- `apps/mobile/tests/raw-export.test.ts::cloud export defaults raw off; explicit separate scope persists original acknowledgment and key through a lost receipt` — file SHA `c68c9146811b6261e384bef9759f0bde4a8a08f3be26391c888da40700d09359`, line 225; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “one pending job preserves the original selected sources and acknowledgement”: HTTP test asserts receipt purpose/selection and reused ID but does not assert persisted job raw_scope/acknowledgment and DB pending-job cardinality.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 897e871c7d7ce6e3f4af3a77aee4b99765f7c9b36a9e865b15345d71d8e867d2. Actual current source and raw evidence supply this disposition.

## OTGD-010-RAW-EXP-004-01 — PARTIAL

The current key has a new S3 version — - **GIVEN** an accepted pinned original source version - **WHEN** a different current object version appears - **THEN** worker reads only the verified accepted version and checks its actual bytes.

Current proof: SourceStore asserts explicit accepted VersionId and actual bounded bytes; wrong returned version/hash/size refused.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_export.py::test_bounded_exact_version_read_and_raw_member_manifest` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 271; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_version_length_type_hash_and_read_limit_failure_never_returns_partial_file` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 283; 30 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “WHEN a different current object version appears”: storage double has one payload and never models a separate newer current version alongside the retained original.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA e589d99cb5f7aef6be29288eb9a238514629d2af0eee18dad3513cc76e286888. Actual current source and raw evidence supply this disposition.

## OTGD-010-RAW-EXP-004-02 — PARTIAL

Withdrawal occurs during source retrieval — - **GIVEN** a raw job reading outside a database transaction - **WHEN** its participant consent is withdrawn before the read completes - **THEN** post-read admission rejects publication and no current ZIP is exposed.

Current proof: Withdrawal callback after external read makes read_sources raise CURRENT_CONSENT_REQUIRED.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_export.py::test_consent_revoked_during_storage_read_blocks_publication` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 291; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “no current ZIP is exposed”: test does not execute fenced worker/commit or check absence of published output/download after the mid-read withdrawal.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5ac51cc6e8e774f896baea97c7eb762d6a0847767e2c662b74750e43b3471e2d. Actual current source and raw evidence supply this disposition.

## OTGD-010-RAW-EXP-005-01 — PARTIAL

A ZIP contains a rehashed unselected recording — - **GIVEN** an authenticated job permits only recording A - **WHEN** a well-formed rehashed ZIP includes recording B instead - **THEN** the client rejects the archive rather than importing or sharing it.

Current proof: Inspector rejects rehashed orphan raw member, changed raw bytes and source metadata; authenticated scope cannot be omitted.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/raw-export.test.ts::rehashed raw version, size, digest, omitted-scope and orphan substitutions never expand the authenticated job scope` — file SHA `c68c9146811b6261e384bef9759f0bde4a8a08f3be26391c888da40700d09359`, line 104; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “well-formed rehashed ZIP includes recording B instead [of selected A]”: test adds an orphan or changes descriptor version/hash; it does not replace A with B and consistently rehash B member and raw descriptor while preserving authenticated job scope A.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4b3b1dd30edf8c6073696a29bcc883e0a5b7a7344c0f459e14686e358dd96d05. Actual current source and raw evidence supply this disposition.

## OTGD-010-RAW-EXP-005-02 — PASS

An exact selected archive verifies against its authenticated job — - **GIVEN** a completed job with exact approved source descriptors - **WHEN** its ZIP preserves all selected structured lineage and raw versions/hashes/bytes - **THEN** the archive inspector validates it and exposes only the approved selected contents.

Current proof: Worker-built fixture archive hash/size and each manifest member hash/size checked; inspector accepts exact authenticated selection, raw authority, source descriptors and all archive members. Fixture uses fictional pixels and software storage.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/raw-export.test.ts::actual authenticated Python scope, completed job and worker ZIP verify exact independent raw authority and versioned binary sources` — file SHA `c68c9146811b6261e384bef9759f0bde4a8a08f3be26391c888da40700d09359`, line 65; 1 current observation(s).
- `services/api/tests/test_raw_export.py::test_actual_http_async_worker_zip_download_replay_expiry_and_foreign_denial` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 418; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA fdd91d14e8c624016a163594c8642c6ce42f5036690eaba93877469e0d10283c. Actual current source and raw evidence supply this disposition.

## OTGD-010-RAW-EXP-006-01 — PASS

Expiry occurs while S3 download is delayed — - **GIVEN** a currently approved completed export - **WHEN** it expires before the storage read returns - **THEN** post-read admission returns a denial with no ZIP bytes disclosed.

Current proof: expiry parameter advances to TICK+3600 inside archive read callback; HTTP returns 403/410 with non-ZIP content type, stream closes and slot releases. Software delayed-read boundary, not live S3.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_export.py::test_delayed_http_download_discloses_no_bytes_after_current_authority_loss` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 565; 20 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 3797e73a02fd7ae0227c5a61fb09d297aecd8957c03c87725ddb377768b9dbb9. Actual current source and raw evidence supply this disposition.

## OTGD-010-RAW-EXP-006-02 — PASS

Revocation follows the first delivery chunk — - **GIVEN** a verified archive larger than 64 KiB - **WHEN** raw permission is revoked after its first admitted chunk - **THEN** the next admission fails and no second chunk is sent.

Current proof: Worker ZIP exceeds 64KiB; ASGI send revokes after first nonempty body, next boundary raises Problem, exactly one 64KiB body sent and buffer slot released.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_export.py::test_admitted_asgi_download_stops_at_next_64k_chunk_after_revocation` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 618; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 1b7b61e9920dcee3c6a78a2e3f837588520bb33db6b3033291743c18b4165329. Actual current source and raw evidence supply this disposition.

## OTGD-010-RAW-EXP-006-03 — PASS

An uninterrupted verified download succeeds — - **GIVEN** current authority and a completed exact-version ZIP - **WHEN** storage bytes and every delivery-boundary admission remain valid - **THEN** the signed-in owner receives the complete hash-matching no-store attachment.

Current proof: Owned uninterrupted HTTP response completes with hash equal completed job and verified member bytes. Eligible surviving source usable, acceptedPOSTreplay denied after exportauthorityretirement, exactno-storeattachment and fullcombinedbudget fail/nooutput asserted.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_export.py::test_actual_http_async_worker_zip_download_replay_expiry_and_foreign_denial` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 418; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_over_budget_source_does_not_hide_or_disable_an_eligible_owned_choice` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 695; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_accepted_post_replay_after_export_authority_retirement_hides_original_scope` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 488; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_raw_members_fit_but_complete_structured_manifest_archive_exceeds_grant` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 511; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Explicit SQLite/storage double fixture; realS3/LocalStack and whole raw selection clauses remain distinct. Final numeric export positive/refusal controls are mapped separately under FINAL_NUMERIC_EXPORT.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA c72e39470c07500386f67d9a4054e1dd8d69ac3d13e1ec550598c7ec343070c3. Actual current source and raw evidence supply this disposition.

## OTGD-010-RAW-EXP-007-01 — PARTIAL

A stale worker uploads after the first cleanup sweep — - **GIVEN** revoked logical delivery and a completed first prefix sweep - **WHEN** an older worker's output arrives later - **THEN** the recurring sweep deletes its exact version and delivery remains denied.

Current proof: First sweep marks revoked, fences and clears output; late exact version added after sweep is removed at TICK+901, neighbor untouched.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_export.py::test_late_export_versions_and_markers_are_recurring_scoped_cleanup` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 302; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “delivery remains denied” after recurring sweep: no post-second-sweep status/download assertion or state re-read after late arrival.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 7c49e896aef238f1169600a9d3925a5298b20cc63b2519c44caf60ac2256c400. Actual current source and raw evidence supply this disposition.

## OTGD-010-RAW-EXP-007-02 — PASS

The customer refreshes after raw-copy cleanup — - **GIVEN** an owned revoked export after cleanup - **WHEN** its status is refreshed - **THEN** the terminal revoked receipt remains visible without grant or download metadata.

Current proof: After cleanup owned HTTP status is revoked; raw_export/download_path/sha256/size_bytes absent and download denied 403/409.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_export.py::test_http_revoked_cleanup_has_minimal_terminal_receipt` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 535; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 4e13639ed05311287197263698969ce3e4fde99b669acd876e942385568faeee. Actual current source and raw evidence supply this disposition.

## OTGD-010-RAW-EXP-008-01 — PASS

Raw sources fit but their structured evidence exceeds the cap — - **GIVEN** raw files fit within the approved uncompressed byte limit - **WHEN** adding selected structured records and the manifest exceeds that limit - **THEN** the entire job fails without producing a partial downloadable archive.

Current proof: Different existing limits exercised: raw source alone over cap, and combined structured record >512KiB refuses before write. Eligible surviving source usable, acceptedPOSTreplay denied after exportauthorityretirement, exactno-storeattachment and fullcombinedbudget fail/nooutput asserted.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_export.py::test_individually_over_export_budget_source_is_not_offered` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 685; 5 current observation(s).
- `services/api/tests/test_report_revisions.py::test_combined_check_record_over_512k_refuses_whole_export_before_object_write` — file SHA `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`, line 1282; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_over_budget_source_does_not_hide_or_disable_an_eligible_owned_choice` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 695; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_accepted_post_replay_after_export_authority_retirement_hides_original_scope` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 488; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_actual_http_async_worker_zip_download_replay_expiry_and_foreign_denial` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 418; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_raw_members_fit_but_complete_structured_manifest_archive_exceeds_grant` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 511; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Explicit SQLite/storage double fixture; realS3/LocalStack and whole raw selection clauses remain distinct. Final numeric export positive/refusal controls are mapped separately under FINAL_NUMERIC_EXPORT.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 06c7b1d8e2c982afd7dc9ea62ecce344e511a748e6e53035eaf2b30243f85dee. Actual current source and raw evidence supply this disposition.

## OTGD-010-RAW-EXP-008-02 — PARTIAL

The complete selected archive fits all approved bounds — - **GIVEN** selected structured records, manifest and explicit raw sources within the narrower caps - **WHEN** the fenced worker assembles and publishes the exact verified archive - **THEN** the complete job succeeds without omitting a selected record or widening the limits.

Current proof: Normal selected worker archive completes and every manifest member matches bytes/hash; raw selected source retained.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_export.py::test_actual_http_async_worker_zip_download_replay_expiry_and_foreign_denial` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 418; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “within the narrower caps ... without omitting a selected record or widening limits”: nominal grant uses global byte maxima; test does not tighten caps around complete combined size and assert unchanged approved limits and complete selected structured set.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA cd4565e07b3cae0fa3841c192806bdb564b58211e06bbebc7bb39d74a16967ca. Actual current source and raw evidence supply this disposition.

