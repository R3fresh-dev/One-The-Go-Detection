# OTGD-039 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/qualified-participant-acquisition/specs/participant-instruction-authority/spec.md`; SHA256 `238b3c329cd79edb4bd57807926311a3bed0c935cf77ef77577fcf79afda02ef`.

22 cases, 8 requirements: PARTIAL 11, PASS 11. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-039-PAI-001-01 — PARTIAL

Current approved pulse instructions — - **GIVEN** an owned check with a currently released PPG configuration and protocol - **WHEN** the participant opens approved capture - **THEN** the app presents the exact approved rest/posture/contact instructions and their version without inventing a default procedure.

Current proof: Setup must be chosen; all required declarations start unchecked; no capture before online prepare and full monotonic rest.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::approved rest begins after online preparation, uses monotonic time, and needs exact unchecked declarations before capture` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 692; 4 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::online preparation persists before rest and current instructions cannot change the prepared acknowledgement` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 666; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- exact approved rest/posture/contact instruction text and version are displayed without defaults: existing assertions inspect controls/protocol digest rather than all rendered text/version.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 79c161ba49b5b66bbf405b077af99adec52f39b1e65bdf512634d5a8fcedd31b. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-001-02 — PASS

Same scientific material with different instruction text — - **GIVEN** unchanged numerical material but a new instruction document or required confirmation - **WHEN** old configuration or acknowledgment identity is used - **THEN** current admission rejects it; matching the material digest alone cannot restore authority.

Current proof: Unchanged material digest cannot release changed instructions without new qualification; changed full envelope refuses capture and resets method acknowledgment.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_same_material_digest_cannot_approve_changed_participant_instructions` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 558; 5 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::a changed submitted instruction envelope cannot reuse the original preparation or stop a newer scope` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1085; 1 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::laboratory method review pins the actual selected method without BLE and resets acknowledgement on document replacement` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 920; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 14f672953e3492c9b95f0558fee197672690bd91d6f6d3c6dec297b42ee13a14. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-002-01 — PASS

Explicit participant acknowledgment — - **GIVEN** the exact current protocol and all its required declarations have been presented for the admitted attempt - **WHEN** the participant confirms them - **THEN** the server returns a scoped immutable receipt retaining the exact request identity and distinct declared-compliance and acceptance times.

Current proof: Accepted instruction receipt matches exact request/session/consent and configuration; positive signed start pins that immutable receipt; client verifies separately retained acknowledgment/acceptance fields and scope.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_positive_collection_without_ble_is_owned_immutable_and_pending` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 264; 5 current observation(s).
- `apps/mobile/tests/participant-acquisition.test.ts::actual Python protocol, immutable acknowledgement, specimen and imported report preserve separate truthful lineage` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 87; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 96ca46d3465355038b533f5a3ba679ded12015109b1c27f75ad4bd8c830724cc. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-002-02 — PARTIAL

Foreign or stale acknowledgment — - **GIVEN** a receipt from another account, retired generation, attempt, study or configuration, or outside admitted freshness - **WHEN** acquisition is requested - **THEN** the service refuses without creating hardware-start authority or rewriting the receipt's scope/time.

Current proof: Foreign/missing attempt receipt refuses grant403; foreign account/retired generation cannot write collection; stale exact receipt replay does not restore grant.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_foreign_attempt_receipt_and_missing_receipt_do_not_create_collection_start` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 689; 5 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_foreign_account_and_retired_generation_cannot_record_or_read_collection` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 456; 5 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_instruction_receipt_expiry_uses_declared_time_and_replay_does_not_restore_authority` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 400; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- refusal for each foreign account/generation/study/config receipt at acquisition without rewriting scope/time: entire cross-product not asserted at receipt-admission boundary.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA db3b2f8ca60ae1c9ee21bcd702506a83fe21cd65ceeae00c00fe08492fcb00c7. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-002-03 — PASS

Exact acknowledgment-age boundary — - **GIVEN** the approved maximum age is A seconds and the minimum of the original client acknowledgment and server acceptance times is T - **WHEN** fresh authority is evaluated at T+A and then at any later instant - **THEN** the age check admits the exact boundary subject to all other gates and rejects the later instant; retry or server receipt replay never replaces T.

Current proof: At max120 age+121, grant403 and exact replay returns original receipt. Exactinclusive maxage and attemptminus5seconds boundary/equality/adjacent refusal preserve originalclient/serveracktime.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_instruction_receipt_expiry_uses_declared_time_and_replay_does_not_restore_authority` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 400; 5 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_acknowledgment_time_cannot_be_rebased_onto_new_server_acceptance` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 577; 5 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_acknowledgment_submission_maximum_age_exact_boundary` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 586; 15 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_acknowledgment_submission_attempt_minus_five_seconds_exact_boundary` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 610; 15 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Fictional typed authority only; actual physical eligibility remains separate.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 7942e61356f4171535c43c1181395751808f430a59f7aeea906672314cf6d94a. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-002-04 — PASS

Future or pre-attempt declaration — - **GIVEN** a declaration is over 5 seconds ahead of the service or earlier than its attempt's creation minus 5 seconds - **WHEN** acknowledgment is submitted - **THEN** the service rejects the time claim instead of correcting it into current acceptance.

Current proof: Future+10 and past121 declarations return422 ACKNOWLEDGMENT_TIME_INVALID. Exactinclusive maxage and attemptminus5seconds boundary/equality/adjacent refusal preserve originalclient/serveracktime.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_acknowledgment_time_cannot_be_rebased_onto_new_server_acceptance` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 577; 5 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_acknowledgment_submission_maximum_age_exact_boundary` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 586; 15 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_acknowledgment_submission_attempt_minus_five_seconds_exact_boundary` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 610; 15 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Fictional typed authority only; actual physical eligibility remains separate.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 36f092c1ff5d8f728143cb473e246c13faa6703522f1ee958813a3584e9142bb. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-003-01 — PASS

Exact receipt and current single-use start — - **GIVEN** the current attempt's accepted instruction receipt and independently qualified acquisition prerequisites - **WHEN** its fresh grant is consumed within the admitted interval - **THEN** start authority pins that receipt and permits only the exact channel/context/configuration and device origin where required.

Current proof: Signed fresh start pins exact instruction receipt; online grant/start precede hardware; server/device signatures and exact bound owned cardiac scope are exercised before research execution.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_positive_collection_without_ble_is_owned_immutable_and_pending` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 264; 5 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1448; 1 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_http_signed_hr_only_research_worker_preserves_flags_and_snapshot` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 190; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA d39c0dd72b4c47988eda5283dd9a07dd67ab90fa2ab386a982b7e560933ad88e. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-003-02 — PARTIAL

Withdrawal after acknowledgment — - **GIVEN** instructions were acknowledged before consent withdrawal or configuration retirement - **WHEN** the participant tries the old grant or a new start - **THEN** current admission refuses, and any local pending capture remains stopped.

Current proof: Withdrawal and configuration retirement deny fresh acknowledgment/grant; stopping a deferred-start capture prevents hardware.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_config_retirement_and_withdrawal_after_acknowledgment_refuse_fresh_start` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 418; 5 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::scope-qualified preparation End stops the advanced capture token before a deferred server start reaches hardware` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1583; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- any local pending capture remains stopped specifically after consent withdrawal/configuration retirement while trying an already-issued grant: current tests combine separate operations, not that full transition.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 750bc567d87c43eebf000ba83764a4f5aa3da5e6a4816b9786fa7345cf1496fc. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-003-03 — PARTIAL

Receipt expires before Start — - **GIVEN** accepted instructions expire before grant issuance or consumption - **WHEN** the participant selects Start - **THEN** acquisition remains stopped and the app requires explicit current instruction presentation and new confirmation; historic receipt replay cannot renew its age.

Current proof: Expired historical receipt cannot obtain grant and replay does not refresh it; reconciliation alone never starts hardware.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_instruction_receipt_expiry_uses_declared_time_and_replay_does_not_restore_authority` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 400; 5 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::lost accepted instruction reply is reconciled with its original body and key without restarting hardware` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 624; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- app requires explicit current instruction presentation and new confirmation after receipt expiration before Start: exact UI re-presentation is not asserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA dc9f67bddc0d581c3c7db7780d455012c9e0c76c70b590ff32cf1eddefe33852. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-003-04 — PARTIAL

Declared strict signed wire format — - **GIVEN** the immutable server authorization pins the exact instruction receipt and configuration/context digests - **WHEN** the signed authorization is verified by its matching declared wire schema - **THEN** the authorization ID resolves only that immutable scope; explicitly declared direct receipt fields must match, unknown fields remain refused and an older strict reader cannot be treated as compatible by dropping signed fields.

Current proof: Positive signed start contains pinned receipt; strict client verifies material/context/version and mutations refuse.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_positive_collection_without_ble_is_owned_immutable_and_pending` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 264; 5 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::actual Python HTTP grant/start envelope binds material, frozen context and signed fresh start without simulated clinical authority` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1785; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- unknown/direct instruction-receipt signed fields refuse and older strict reader cannot drop signed fields: task-envelope mutation test does not exercise the complete instruction wire compatibility scenario.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8f70947179d3240bf2859c28d7b4eb9d7439f3878d500d8bc5dee6da88bd5802. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-004-01 — PARTIAL

Declared posture with independent device admission — - **GIVEN** an approved PPG protocol and independently admitted hardware - **WHEN** the participant records its permitted posture/activity declarations - **THEN** evidence labels those values as declared context and preserves separate actual device provenance.

Current proof: Cardiac HTTP flow retains separate instruction receipt and device-signed provenance; client verifies declarations as scoped evidence.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority.py::test_http_signed_hr_only_research_worker_preserves_flags_and_snapshot` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 190; 5 current observation(s).
- `apps/mobile/tests/participant-acquisition.test.ts::actual Python protocol, immutable acknowledgement, specimen and imported report preserve separate truthful lineage` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 87; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- evidence labels posture/activity as declared context while preserving separate actual provenance: exact presentation label is not directly asserted in these bodies.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA dcfe732f5cda62a39d2bc07a735afc6d7442a64f02e06839c12927f7af7f6330. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-004-02 — PASS

Checkbox substitutes for ECG power observation — - **GIVEN** a human ECG setup requires observed USB/charging state but the installed adapter cannot supply it - **WHEN** the participant confirms a power or safety statement - **THEN** human-connected capture remains unavailable with the missing verifier identified; no safety proof is fabricated.

Current proof: Both declared and purported device-attested human ECG configs remain unsupported; client rejects; browser identifies unavailable human ECG and disables preparation/capture despite confirmation controls.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_human_ecg_state_verification_is_unavailable_even_when_declared_verified` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 470; 5 current observation(s).
- `apps/mobile/tests/participant-acquisition.test.ts::document digest, selected method, exact UUID/calendar and electrical setup boundaries are enforced` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 257; 1 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::interruption and a changed instruction envelope discard rest and checks; participant declarations cannot enable human ECG` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 753; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 0c4f868d513171966de850a82b8474ce195868d612af0d2f9338f422b0050ede. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-004-03 — PARTIAL

Bench scope cannot become human scope — - **GIVEN** an explicitly permitted simulator/bench configuration - **WHEN** it is used to claim human-connected eligibility - **THEN** service and client reject the scope substitution even if all participant confirmations are true.

Current proof: Human ECG configuration and client screen refuse regardless of declared verifier.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_human_ecg_state_verification_is_unavailable_even_when_declared_verified` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 470; 5 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::interruption and a changed instruction envelope discard rest and checks; participant declarations cannot enable human ECG` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 753; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- service and client reject actual substitution from an admitted simulator/bench receipt into human scope even with all confirmations true: paired scope-substitution request is not executed.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0de83c522d63da13f86d244b4d9bcc1218cf0f31d8240fc4f06e1de8276e3731. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-005-01 — PARTIAL

Accepted response is lost — - **GIVEN** the server accepted acknowledgment but its response was lost - **WHEN** the client reconnects - **THEN** it retries the original body/key, verifies the matching immutable receipt and separately obtains current start authority.

Current proof: Lost accepted acknowledgment retries unchanged retained body/key and reconciles one receipt; no hardware resumes; replay cannot renew expired age.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/acquisition.test.ts::lost accepted instruction reply is reconciled with its original body and key without restarting hardware` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 624; 1 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_instruction_receipt_expiry_uses_declared_time_and_replay_does_not_restore_authority` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 400; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- separately obtains current start authority after reconciliation: the named lost-response test stops the attempt rather than performing that subsequent current start.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 1c164437c03819edd938c210c11ff057d7d7e105308198151118009179afb556. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-005-02 — PARTIAL

Replacement during receipt persistence — - **GIVEN** an old receipt response is delayed while the owner, attempt or retained intent changes - **WHEN** that callback runs - **THEN** scope and keyed-intent guards preserve the replacement and reject old acceptance; no old timestamp is rewritten as a fresh acknowledgment.

Current proof: Unmount/replacement envelope discards late preparation callback and a stale stop token cannot stop newer scope.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::unmount and a replacement approval envelope stop pending preparation and cannot apply its late receipt` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 872; 4 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::a changed submitted instruction envelope cannot reuse the original preparation or stop a newer scope` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1085; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- scope/keyed-intent guards preserve replacement specifically during delayed instruction receipt persistence; no old acknowledgment timestamp is refreshed: delayed acknowledgment persistence callback is not directly asserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0919b11970a39a0f906a241b4b0f2cd8e7f2b39ce9d7a5edba38b42c7d4ede07. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-006-01 — PARTIAL

Withdrawal while grant is pending — - **GIVEN** current instructions were confirmed and start is awaiting a network response - **WHEN** withdrawal is requested - **THEN** local acceptance stops immediately, privacy intent remains durable and the later grant cannot invoke hardware.

Current proof: Local shutdown is dispatched before delayed start reply and hardware is never invoked; attempt becomes invalid.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/acquisition.test.ts::scope-qualified preparation End stops the advanced capture token before a deferred server start reaches hardware` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1583; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- privacy withdrawal intent remains durable and later grant cannot invoke hardware for that exact withdrawal case: test uses explicit End, not withdrawal.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8e03dfaed56e8fe422580421a5e8aa3332cc09b4d353a3c0d8cf73110cbf8aa2. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-006-02 — PARTIAL

Keep draft after cancellation — - **GIVEN** an admitted attempt was interrupted before completion - **WHEN** the customer keeps the draft and revisits it - **THEN** prior attempt/instruction evidence remains immutable and any new collection requires a separately admitted current start.

Current proof: Canceled instruction attempt becomes invalid; stored specimen form reopens without active capture/rest.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/acquisition.test.ts::lost accepted instruction reply is reconciled with its original body and key without restarting hardware` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 624; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::reopening the owned workspace preserves the actual collecting form without restoring rest or invoking hardware` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1056; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Keep draft preserves prior instruction/attempt and forces separately admitted new collection start: complete cancel/keep/revisit/new-start transition not asserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 39626f5eaee6756d19bd4ca1003357e8930c5dc2b4b443b269f278442fecf6f6. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-007-01 — PASS

Conditionally admitted optical or ECG evidence — - **GIVEN** the installed adapter has current authority or a saved non-simulated signed measurement - **WHEN** its screen or metric is rendered - **THEN** copy describes that exact capability/source and retains the unresolved physical-onset or safety limitations.

Current proof: Rendered non-simulated eye/ECG source copy retains physical-onset limitation, withholds unmeasured magnitude/latency and explicitly denies diagnostic interpretation; fictional mode changes labels. Healthy signed protocol state/currentboot is distinct from servicebinding and syntheticconnection; actualHome/Device current/revoked/expired/owner/gen/offline observations match; mountedexpiry removesconditionalavailability, no flag grants capture authority.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::eye and ECG descriptions follow the approved observation and actual provenance without claiming measured light onset` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 524; 4 current observation(s).
- `apps/mobile/tests/device-presentation.test.ts::per-channel display uses active matching scope and unexpired admitted configuration independently from connection or binding` — file SHA `b5ef6ea88a473d082e49cf89eb4afa8e50b1bed4d7fe572ebdabdf31062ee733`, line 21; 1 current observation(s).
- `apps/mobile/tests/device-presentation.test.ts::a healthy signed reader connection is physical and retains current boot independently from service binding` — file SHA `b5ef6ea88a473d082e49cf89eb4afa8e50b1bed4d7fe572ebdabdf31062ee733`, line 82; 1 current observation(s).
- `apps/mobile/tests/result-ui.test.ts::actual Home and Device agree on a connected physical reader without synthetic or unconditional unavailable claims` — file SHA `217ae43bfcae4cb9826bafd8ad66bef8e97327c0638400c0e6263c5eb7d66a60`, line 49; 1 current observation(s).
- `apps/mobile/e2e/components.spec.ts::Home and Device distinguish physical/synthetic connection from current, revoked, expired or mismatched channel authority` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 56; 4 current observation(s).
- `apps/mobile/e2e/components.spec.ts::Home expires its current channel observation while mounted and Device retains that expired status` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 130; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Loopback/framed/parsed-capability software fixtures only. Actual BLE handshake/radio/physicalreader/sensing qualification remain explicit; conditionaldisplay cannot independently qualify capture.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 4ef8f9a1a29f97903f98b78a5e0a4959d7fb25a5ef76c1402e7831d64f48e0fe. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-007-02 — PASS

Guest or missing qualification — - **GIVEN** a fictional guest or account without a qualified configuration - **WHEN** acquisition or permission information is displayed - **THEN** fictional/unavailable limits remain explicit and no protocol checkbox or public flag enables participant sensing.

Current proof: Guest/simulated source labels remain fictional; hosted preview with available public flags still shows acquisition/model unavailable and no approved capture offer. Healthy signed protocol state/currentboot is distinct from servicebinding and syntheticconnection; actualHome/Device current/revoked/expired/owner/gen/offline observations match; mountedexpiry removesconditionalavailability, no flag grants capture authority.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::eye and ECG descriptions follow the approved observation and actual provenance without claiming measured light onset` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 524; 4 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::actual service component labels conditional approved channels and model support, while the fictional build refuses both` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1407; 4 current observation(s).
- `apps/mobile/tests/device-presentation.test.ts::per-channel display uses active matching scope and unexpired admitted configuration independently from connection or binding` — file SHA `b5ef6ea88a473d082e49cf89eb4afa8e50b1bed4d7fe572ebdabdf31062ee733`, line 21; 1 current observation(s).
- `apps/mobile/tests/device-presentation.test.ts::a healthy signed reader connection is physical and retains current boot independently from service binding` — file SHA `b5ef6ea88a473d082e49cf89eb4afa8e50b1bed4d7fe572ebdabdf31062ee733`, line 82; 1 current observation(s).
- `apps/mobile/tests/result-ui.test.ts::actual Home and Device agree on a connected physical reader without synthetic or unconditional unavailable claims` — file SHA `217ae43bfcae4cb9826bafd8ad66bef8e97327c0638400c0e6263c5eb7d66a60`, line 49; 1 current observation(s).
- `apps/mobile/e2e/components.spec.ts::Home and Device distinguish physical/synthetic connection from current, revoked, expired or mismatched channel authority` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 56; 4 current observation(s).
- `apps/mobile/e2e/components.spec.ts::Home expires its current channel observation while mounted and Device retains that expired status` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 130; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Loopback/framed/parsed-capability software fixtures only. Actual BLE handshake/radio/physicalreader/sensing qualification remain explicit; conditionaldisplay cannot independently qualify capture.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 9eeadf9f360fae33cb47bcbf0db25fae748a290619e94dc6cdec3037c8d7e953. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-008-01 — PASS

Approved rest interval completes — - **GIVEN** the current cardiac protocol requires R seconds of rest and the current owned attempt has begun - **WHEN** foreground monotonic elapsed time reaches R without interruption and the participant explicitly confirms all approved declarations - **THEN** the app may submit the exact preparation acknowledgment and retains its original UTC rest-start and confirmation times as declared context.

Current proof: Owned attempt persists before rest; full monotonic interval and explicit declarations required; exact protocol digest submitted; helper samples one original UTC acknowledgment/rest interval including0/30seconds.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::approved rest begins after online preparation, uses monotonic time, and needs exact unchecked declarations before capture` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 692; 4 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::online preparation persists before rest and current instructions cannot change the prepared acknowledgement` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 666; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::instruction fixture samples one acknowledgment instant across clock rollover and preserves the approved rest duration` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 460; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 0fb073234aea2c1288b04f96888644ca8a87b4c2633ca502c534d17b5c0b0881. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-008-02 — PASS

Background or wall clock advances during rest — - **GIVEN** preparation is incomplete or its wall clock becomes inconsistent with retained monotonic elapsed time - **WHEN** the app backgrounds, the workspace changes or the clock advances enough to appear complete - **THEN** it cannot enable early Start; it clears current preparation authority and requires new foreground guidance and explicit confirmation.

Current proof: Monotonic regression/background reset preparation and declarations; advancing wall clock cannot shorten monotonic wait. 100ms inclusive consistency only;101ms/clockregression or unavailableclock clears preparation; actualDOM declarations/reset/no-capture,zero/maxduration preserved.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/participant-acquisition.test.ts::foreground rest requires monotonic elapsed time and interruption invalidates prior wait` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 460; 1 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::approved rest begins after online preparation, uses monotonic time, and needs exact unchecked declarations before capture` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 692; 4 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::interruption and a changed instruction envelope discard rest and checks; participant declarations cannot enable human ECG` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 753; 4 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::a monotonic regression resets approved rest and declarations until an explicit new preparation` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 806; 4 current observation(s).
- `apps/mobile/tests/preparation-clock.test.ts::preparation accepts inclusive ±100ms sampling disagreement while rest remains monotonic` — file SHA `26e1ae978c239b5ac48bb5b7ceac75114d96e7642fbcffd57623e49c3dc652dc`, line 27; 1 current observation(s).
- `apps/mobile/tests/preparation-clock.test.ts::forward/backward ±101ms discontinuities reset authority until a new start` — file SHA `26e1ae978c239b5ac48bb5b7ceac75114d96e7642fbcffd57623e49c3dc652dc`, line 41; 1 current observation(s).
- `apps/mobile/tests/preparation-clock.test.ts::zero/max approved durations retain their bounds and wall time never shortens rest` — file SHA `26e1ae978c239b5ac48bb5b7ceac75114d96e7642fbcffd57623e49c3dc652dc`, line 74; 1 current observation(s).
- `apps/mobile/e2e/components.spec.ts::preparation wall-clock forward/backward discontinuity clears guidance and declarations until a fresh admitted rest` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 376; 4 current observation(s).
- `apps/mobile/e2e/components.spec.ts::zero and maximum approved rest retain explicit declarations and unshortened monotonic bounds` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 468; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Engineeringguard is not physical rest/timing or participant qualification; approved protocol durations unchanged.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 46706ea401aecc67edc88303630f2f9e56d8e202141c3a0f332c86978ac0a2c9. Actual current source and raw evidence supply this disposition.

## OTGD-039-PAI-008-03 — PASS

Zero-duration approved preparation — - **GIVEN** the independently released protocol explicitly requires zero seconds of rest - **WHEN** the owned attempt and exact setup instructions are presented - **THEN** the timer introduces no invented delay but every required participant declaration and independent hardware/safety gate remains mandatory.

Current proof: Zero-second approved input validates without an invented interval; human ECG independent verifier still refuses. 100ms inclusive consistency only;101ms/clockregression or unavailableclock clears preparation; actualDOM declarations/reset/no-capture,zero/maxduration preserved.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/acquisition.test.ts::instruction fixture samples one acknowledgment instant across clock rollover and preserves the approved rest duration` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 460; 1 current observation(s).
- `apps/mobile/tests/participant-acquisition.test.ts::document digest, selected method, exact UUID/calendar and electrical setup boundaries are enforced` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 257; 1 current observation(s).
- `apps/mobile/tests/preparation-clock.test.ts::preparation accepts inclusive ±100ms sampling disagreement while rest remains monotonic` — file SHA `26e1ae978c239b5ac48bb5b7ceac75114d96e7642fbcffd57623e49c3dc652dc`, line 27; 1 current observation(s).
- `apps/mobile/tests/preparation-clock.test.ts::forward/backward ±101ms discontinuities reset authority until a new start` — file SHA `26e1ae978c239b5ac48bb5b7ceac75114d96e7642fbcffd57623e49c3dc652dc`, line 41; 1 current observation(s).
- `apps/mobile/tests/preparation-clock.test.ts::zero/max approved durations retain their bounds and wall time never shortens rest` — file SHA `26e1ae978c239b5ac48bb5b7ceac75114d96e7642fbcffd57623e49c3dc652dc`, line 74; 1 current observation(s).
- `apps/mobile/e2e/components.spec.ts::preparation wall-clock forward/backward discontinuity clears guidance and declarations until a fresh admitted rest` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 376; 4 current observation(s).
- `apps/mobile/e2e/components.spec.ts::zero and maximum approved rest retain explicit declarations and unshortened monotonic bounds` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 468; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Engineeringguard is not physical rest/timing or participant qualification; approved protocol durations unchanged.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4481223831a3207acaf142bcd6a5de2a684b19605575d74a1df5e126e8c8e0c7. Actual current source and raw evidence supply this disposition.

