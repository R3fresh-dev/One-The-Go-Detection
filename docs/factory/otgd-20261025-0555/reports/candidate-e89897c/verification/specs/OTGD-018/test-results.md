# OTGD-018 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/optional-raw-recording-lifecycle/specs/raw-recording-customer-flow/spec.md`; SHA256 `a688ab279a337ce745968e41c3d834c1afa8486a45901544cd7f779df2d54218`.

16 cases, 8 requirements: PARTIAL 6, PASS 10. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-018-AND-RAW-001-01 — PARTIAL

Approved terms are independently verified — - **GIVEN** the owned study returns current consent and an approved policy - **WHEN** the participant opens Recording choices & retention - **THEN** exact verified terms appear before any choice can be confirmed.

Current proof: Parser validates full approved policy and exact notice; component initially disables confirmation, displays exact notice content and acquisition-based two-day duration before separate acknowledgment.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/raw-recordings.test.ts::actual Python raw_status envelope verifies complete policy, exact UTF-8 notice, separate receipt and upload/retention states` — file SHA `f2d9a32b5ff0e11ca6aacfb3ea86b246341a1900cfa0042623a0552222900a08`, line 21; 1 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::actual raw choices component defaults both optional purposes off and requires exact policy review before a separate local/upload choice` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1111; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- “exact verified terms appear” in full: rendered assertions cover exact notice and duration but not complete displayed purpose, policy ID/version/digest, expiry, access roles, withdrawal behavior and exceptions. Immutable raw-choices.tsx displays those fields; no demonstrated display defect.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 6d545c12f7650781a43b305d85d29cafb145a2c206b48fa0a8df157b2890a122. Actual current source and raw evidence supply this disposition.

## OTGD-018-AND-RAW-001-02 — PARTIAL

A projected purpose is substituted — - **GIVEN** the server reply contains policy.content for purpose A and displayed purpose B - **WHEN** the client verifies the reply - **THEN** the policy is rejected and acquisition remains unavailable.

Current proof: Policy summary-purpose B against content A is directly mutated and parseRawRecordingStatus throws.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/raw-recordings.test.ts::raw policy or notice substitution, wrong owner, unknown data and inconsistent immutable receipt fail closed` — file SHA `f2d9a32b5ff0e11ca6aacfb3ea86b246341a1900cfa0042623a0552222900a08`, line 37; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “acquisition remains unavailable”: mutation is tested at parser only; no controller/native start attempt verifies zero acquisition after the rejected status.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5681767d9b9319bb57d7dbe2e174d14616eb21393564c0a4cd88af2bcaa0a46c. Actual current source and raw evidence supply this disposition.

## OTGD-018-AND-RAW-002-01 — PASS

Participant chooses local recording only — - **GIVEN** verified terms and both choices off - **WHEN** the participant enables device recording and confirms the separate notice - **THEN** upload remains off and no raw file is queued.

Current proof: UI starts record/upload off, reading exact notice+checking acknowledgment then record yields save event record=true/upload=false; controller local-only ECG fixture retains local state, no upload admission and queue length zero before/after Save. Software orchestration only; actual SQLCipher qualification is assessed separately in AND-RAW-006-01.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::actual raw choices component defaults both optional purposes off and requires exact policy review before a separate local/upload choice` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1111; 4 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::explicit ECG raw choice uses a fresh signed recording receipt and the real bounded encoder before atomic encrypted local save` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1494; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 1980cba94031e661674df1161f170c0a946de0fdbe34f2fd461daa689397688a. Actual current source and raw evidence supply this disposition.

## OTGD-018-AND-RAW-002-02 — PASS

The workspace changes before confirmation — - **GIVEN** unchecked choices were edited in account A generation 1 - **WHEN** account B or a new generation opens the form - **THEN** unfinished choices and notice acknowledgment reset.

Current proof: Component edits account-A:g1, then renders same form under account-B:g2; record and acknowledgment unchecked, confirm disabled, notice review affordance visible. The executed incoming workspace changes both owner and generation; this establishes that exact scenario, not every independent boundary permutation.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::account or generation change resets unfinished choices and notice acknowledgment` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1174; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 0b0b712fa0f8b349b7d5058c1f05ed3cd9d979992a293b46e55b089c2ed179a3. Actual current source and raw evidence supply this disposition.

## OTGD-018-AND-RAW-003-01 — PASS

Accepted response is lost — - **GIVEN** the service accepted a preference but its reply was lost - **WHEN** the customer retries - **THEN** the original body, timestamp and request key are reused and the original receipt is reconciled.

Current proof: Queued payload equals transmitted payload, repeat body and Idempotency-Key equal original and queue reconciles synced receipt. OriginalacceptedreceiptIDoracle retained, exactrenewalbody/persistedepoch observed at request boundary, actual rawscreen quarantine/cleanuppending/purged versus deadline.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/raw-recordings.test.ts::lost optional-choice receipt replays exact durable body, original acknowledgment and idempotency key` — file SHA `f2d9a32b5ff0e11ca6aacfb3ea86b246341a1900cfa0042623a0552222900a08`, line 188; 1 current observation(s).
- `apps/mobile/tests/raw-recordings.test.ts::actual raw receipt screen distinguishes quarantine, retained data, pending cleanup and completed cleanup from retention deadlines` — file SHA `f2d9a32b5ff0e11ca6aacfb3ea86b246341a1900cfa0042623a0552222900a08`, line 415; 1 current observation(s).
- `apps/mobile/tests/raw-upload.test.ts::acknowledged expired tickets advance durable renewal identity, while a lost renewal replays its exact key` — file SHA `90d5120384148e33dd319309f64395cc83057aa1fe500cee90ee906746ad95ef`, line 269; 1 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::actual raw receipt screen keeps quarantine and cleanup confirmation distinct from retention expiry` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1466; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: In-memorycommit/nativeprovider doubles; actual SQLCipherdurability/processrestart/sharecleanup separate.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 1b41ce3c5e085bff37309a2f9376bef8c0437d63287075dba1fc18b909c1447a. Actual current source and raw evidence supply this disposition.

## OTGD-018-AND-RAW-003-02 — PASS

Effective permission exceeds the receipt — - **GIVEN** a receipt confirms upload=false - **WHEN** a status reply says upload=true without a new matching receipt - **THEN** the client rejects the status.

Current proof: Mutation changes immutable preference_receipt.choices.eye_video to record=false/upload=false while effective fixture choices remain enabled; parser throws instead of widening permission without matching receipt.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/raw-recordings.test.ts::raw policy or notice substitution, wrong owner, unknown data and inconsistent immutable receipt fail closed` — file SHA `f2d9a32b5ff0e11ca6aacfb3ea86b246341a1900cfa0042623a0552222900a08`, line 37; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 4b50f60d3eb4f01bfec115a24b76fc478cd2636586d34aa3b0bfaaa31cd1ab6c. Actual current source and raw evidence supply this disposition.

## OTGD-018-AND-RAW-004-01 — PASS

A grant reply arrives after revocation — - **GIVEN** an optional-purpose grant request is in flight - **WHEN** the participant requests revocation before its reply - **THEN** the grant intent remains blocked and the late reply cannot revive it.

Current proof: Actual controller queues preference behind deferred response, requests revocation offline, then delivers old preference reply; preference remains blocked with RAW_REVOCATION_PENDING and eye-video fence remains.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/raw-recordings.test.ts::revocation fences an in-flight preference receipt before any late reply can mark it accepted` — file SHA `f2d9a32b5ff0e11ca6aacfb3ea86b246341a1900cfa0042623a0552222900a08`, line 321; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA ce648f3f5f42c6b1b28ef99dc843a36c8209b72911dc0195888d6ac149a2cb33. Actual current source and raw evidence supply this disposition.

## OTGD-018-AND-RAW-004-02 — PASS

Old cleanup and new pending cleanup coexist — - **GIVEN** completed revocation A and newer cleanup-pending revocation B for eye video - **WHEN** status is refreshed after B was accepted - **THEN** eye recording remains fenced until B is completed.

Current proof: Creates newer accepted cleanup_pending and older completed eye revocation; after refresh queue accepted but eye fence persists and saving enabled choices rejects revocation. It does not claim physical cleanup completion.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/raw-recordings.test.ts::an older completed revocation cannot clear a newer accepted cleanup-pending stop fence` — file SHA `f2d9a32b5ff0e11ca6aacfb3ea86b246341a1900cfa0042623a0552222900a08`, line 366; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 875818eb9d0cf3175a593fc6e16c1dd57feb594d6af18d28718089ea9c15c979. Actual current source and raw evidence supply this disposition.

## OTGD-018-AND-RAW-005-01 — PASS

An uploaded object is awaiting verification — - **GIVEN** retention state retained and upload_state quarantine - **WHEN** status is displayed - **THEN** quarantine is visible and the app does not claim verified upload or completed deletion.

Current proof: Parser preserves artifact state retained separately from upload_state quarantine; invented verified/deleted state names rejected in separate mutation test. OriginalacceptedreceiptIDoracle retained, exactrenewalbody/persistedepoch observed at request boundary, actual rawscreen quarantine/cleanuppending/purged versus deadline.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/raw-recordings.test.ts::actual Python raw_status envelope verifies complete policy, exact UTF-8 notice, separate receipt and upload/retention states` — file SHA `f2d9a32b5ff0e11ca6aacfb3ea86b246341a1900cfa0042623a0552222900a08`, line 21; 1 current observation(s).
- `apps/mobile/tests/raw-recordings.test.ts::raw policy or notice substitution, wrong owner, unknown data and inconsistent immutable receipt fail closed` — file SHA `f2d9a32b5ff0e11ca6aacfb3ea86b246341a1900cfa0042623a0552222900a08`, line 37; 1 current observation(s).
- `apps/mobile/tests/raw-recordings.test.ts::lost optional-choice receipt replays exact durable body, original acknowledgment and idempotency key` — file SHA `f2d9a32b5ff0e11ca6aacfb3ea86b246341a1900cfa0042623a0552222900a08`, line 188; 1 current observation(s).
- `apps/mobile/tests/raw-recordings.test.ts::actual raw receipt screen distinguishes quarantine, retained data, pending cleanup and completed cleanup from retention deadlines` — file SHA `f2d9a32b5ff0e11ca6aacfb3ea86b246341a1900cfa0042623a0552222900a08`, line 415; 1 current observation(s).
- `apps/mobile/tests/raw-upload.test.ts::acknowledged expired tickets advance durable renewal identity, while a lost renewal replays its exact key` — file SHA `90d5120384148e33dd319309f64395cc83057aa1fe500cee90ee906746ad95ef`, line 269; 1 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::actual raw receipt screen keeps quarantine and cleanup confirmation distinct from retention expiry` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1466; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: In-memorycommit/nativeprovider doubles; actual SQLCipherdurability/processrestart/sharecleanup separate.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 2f96762dfe74b79031024817fc4c0c58726df4ae8a318aa931eb8117eaa4b778. Actual current source and raw evidence supply this disposition.

## OTGD-018-AND-RAW-005-02 — PASS

Physical cleanup has not completed — - **GIVEN** a revoked artifact has cleanup_pending with no cleanup_completed_at - **WHEN** its receipt is displayed - **THEN** pending cleanup remains explicit and is never labeled deleted.

Current proof: Parser preserves cleanup_pending and null cleanup_completed_at; component explicitly warns local stop may leave physical cleanup pending. OriginalacceptedreceiptIDoracle retained, exactrenewalbody/persistedepoch observed at request boundary, actual rawscreen quarantine/cleanuppending/purged versus deadline.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/raw-recordings.test.ts::separate revocation preserves original granted receipt while effective choices turn off and cleanup remains pending` — file SHA `f2d9a32b5ff0e11ca6aacfb3ea86b246341a1900cfa0042623a0552222900a08`, line 137; 1 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::local revocation fence overrides old confirmed grant without claiming cleanup completion` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1230; 4 current observation(s).
- `apps/mobile/tests/raw-recordings.test.ts::lost optional-choice receipt replays exact durable body, original acknowledgment and idempotency key` — file SHA `f2d9a32b5ff0e11ca6aacfb3ea86b246341a1900cfa0042623a0552222900a08`, line 188; 1 current observation(s).
- `apps/mobile/tests/raw-recordings.test.ts::actual raw receipt screen distinguishes quarantine, retained data, pending cleanup and completed cleanup from retention deadlines` — file SHA `f2d9a32b5ff0e11ca6aacfb3ea86b246341a1900cfa0042623a0552222900a08`, line 415; 1 current observation(s).
- `apps/mobile/tests/raw-upload.test.ts::acknowledged expired tickets advance durable renewal identity, while a lost renewal replays its exact key` — file SHA `90d5120384148e33dd319309f64395cc83057aa1fe500cee90ee906746ad95ef`, line 269; 1 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::actual raw receipt screen keeps quarantine and cleanup confirmation distinct from retention expiry` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1466; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: In-memorycommit/nativeprovider doubles; actual SQLCipherdurability/processrestart/sharecleanup separate.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 81b01e089f295a6abd82f37fcfe92d7916500bd7c1738d8b184dd8f84a6dd254. Actual current source and raw evidence supply this disposition.

## OTGD-018-AND-RAW-006-01 — PARTIAL

Participant saves approved local recording — - **GIVEN** an approved codec and separately confirmed record=true, upload=false - **WHEN** native acquisition completes and its immutable evidence matches the fresh start - **THEN** bytes and metadata commit together to SQLCipher, native handoff memory is released, and the upload queue remains empty.

Current proof: Controller local-only approved ECG encodes bytes, invokes saveWithRaw once, wipes handed buffer, saves with empty upload queue; native-storage boundary test rolls back BLOB+index together.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/acquisition.test.ts::explicit ECG raw choice uses a fresh signed recording receipt and the real bounded encoder before atomic encrypted local save` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1494; 1 current observation(s).
- `apps/mobile/tests/native-storage.test.ts::raw bytes and index rollback together on a workspace switch and expiry/orphan reconciliation completes before reopened reads` — file SHA `52005beea373ed0bf603dffffc6a20cb2e8fd07371bf5cb0712afa4b3bf208df`, line 219; 1 current observation(s).
- `apps/mobile/tests/raw-artifacts.test.ts::native ROI bytes validate exact codec, frame geometry, sequence, timing, digest and bounded memory handoff` — file SHA `80522a5edec7a841cdaf1ed5257ce336ea1ababb4d2a4001d1c7a443fe7e94b3`, line 39; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “commit together to SQLCipher, native handoff memory is released”: acquisition test stubs saveWithRaw and reader, native-storage test replaces expo-sqlite with in-memory Map/transaction double and fictional cipher_version; no actual SQLCipher transaction/native handoff lifecycle executed. Native production support must be validated separately.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA ed58d2e9f5ede2d5f5d014137732fbc68ec4321dcb4090209017f642295535d9. Actual current source and raw evidence supply this disposition.

## OTGD-018-AND-RAW-006-02 — PARTIAL

Consent was revoked on another device — - **GIVEN** a cached optional receipt appears to permit recording - **WHEN** fresh capture start refuses or narrows the receipt - **THEN** native raw recording never starts and cached permission cannot override the fresh decision.

Current proof: verifyRawPermission rejects changed/narrowed fresh flags, receipt/policy/notice identity, local fence and revoked effective receipt.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/raw-artifacts.test.ts::fresh acquisition authority must match exact current optional receipt and cannot bypass offline or cross-device stop` — file SHA `80522a5edec7a841cdaf1ed5257ce336ea1ababb4d2a4001d1c7a443fe7e94b3`, line 70; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “native raw recording never starts ... cached permission cannot override fresh decision”: helper rejection is direct; no raw-recording controller test supplies a formerly enabled cached receipt plus freshly refused/narrowed start and asserts zero native raw invocation.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA ba1c00b560d0e1a5778b70ccb0d454a13fac4d7c8c21fdfa2d750170bec867eb. Actual current source and raw evidence supply this disposition.

## OTGD-018-AND-RAW-007-01 — PARTIAL

A stopped app resumes after retention expiry — - **GIVEN** local raw bytes expired while the app was stopped - **WHEN** the owner unlocks the workspace - **THEN** expired and unindexed bytes are removed before exposure, failed removal remains pending, no expired read or upload is admitted, and the stopped app makes no exact-time physical cleanup claim.

Current proof: Mocked native store explicit reconcileRaw removes expired/orphan BLOBs, marks index deleted before reopened read; UI disables expired raw upload; screen explicitly states stopped app cannot run deletion timer.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/native-storage.test.ts::raw bytes and index rollback together on a workspace switch and expiry/orphan reconciliation completes before reopened reads` — file SHA `52005beea373ed0bf603dffffc6a20cb2e8fd07371bf5cb0712afa4b3bf208df`, line 219; 1 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::raw upload selection is explicit per file and local-only, expired or revoked recordings cannot join a check upload` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1339; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- “expired while stopped ... owner unlocks ... before exposure, failed removal remains pending, no expired read or upload admitted”: test manually reconciles future expiry BEFORE closing/reopening and never injects removal failure. Actual stopped-app reopen reconciliation and failed cleanup state/exposure barrier remain unexecuted, with SQLCipher/OS still doubled.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution, independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 677bf8e9840c2469d0b0c3a93b5a71566279b9acbad50add050fac9dc9a2458f. Actual current source and raw evidence supply this disposition.

## OTGD-018-AND-RAW-007-02 — PASS

Renewal response is lost — - **GIVEN** a ticket renewal has an unknown response - **WHEN** explicit upload is retried - **THEN** its exact key and body are reused; after an acknowledged ticket later expires, a new bounded renewal epoch is persisted before requesting a replacement, and decrypted buffers are wiped on success, failure or cancellation.

Current proof: Lost renewal reuses first key; after acknowledged ticket expires replacement gets different key; single admission request, success/failure-read buffers wiped; revocation during deferred decrypt wipes bytes and sends no admission. OriginalacceptedreceiptIDoracle retained, exactrenewalbody/persistedepoch observed at request boundary, actual rawscreen quarantine/cleanuppending/purged versus deadline. Meaningful shared proof: actual cancellation rejects the awaited objectPUT; actual privacy-fenced decrypted buffer is zeroed; uploadRaw finally unconditionally fills the same bytes with0 after all awaited success/error paths. Combined with exactrenewalepoch/body assertions, this proves software intent/buffer handling without a duplicate implementation-shaped test.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/raw-upload.test.ts::acknowledged expired tickets advance durable renewal identity, while a lost renewal replays its exact key` — file SHA `90d5120384148e33dd319309f64395cc83057aa1fe500cee90ee906746ad95ef`, line 269; 1 current observation(s).
- `apps/mobile/tests/raw-upload.test.ts::revocation arriving during decryption wipes returned bytes and cannot send or revive the fenced intent` — file SHA `90d5120384148e33dd319309f64395cc83057aa1fe500cee90ee906746ad95ef`, line 349; 1 current observation(s).
- `apps/mobile/tests/raw-upload.test.ts::Save and metadata-only upload never read or queue raw; explicit selection is immutable and exact` — file SHA `90d5120384148e33dd319309f64395cc83057aa1fe500cee90ee906746ad95ef`, line 227; 1 current observation(s).
- `apps/mobile/tests/raw-recordings.test.ts::lost optional-choice receipt replays exact durable body, original acknowledgment and idempotency key` — file SHA `f2d9a32b5ff0e11ca6aacfb3ea86b246341a1900cfa0042623a0552222900a08`, line 188; 1 current observation(s).
- `apps/mobile/tests/raw-recordings.test.ts::actual raw receipt screen distinguishes quarantine, retained data, pending cleanup and completed cleanup from retention deadlines` — file SHA `f2d9a32b5ff0e11ca6aacfb3ea86b246341a1900cfa0042623a0552222900a08`, line 415; 1 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::actual raw receipt screen keeps quarantine and cleanup confirmation distinct from retention expiry` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1466; 4 current observation(s).
- `apps/mobile/tests/raw-upload.test.ts::object PUT has a real 60-second deadline and privacy cancellation aborts transport without late success` — file SHA `90d5120384148e33dd319309f64395cc83057aa1fe500cee90ee906746ad95ef`, line 445; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: In-memorycommit/nativeprovider doubles; actual SQLCipherdurability/processrestart/sharecleanup separate. Controlled storage/transport; real SQLCipher durability, OS memory and physical cleanup are separately unexecuted. Control-flow source snippet retained independently.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0f7c92726d2061d172294e926999cb937a015a20ea777a339838f6f937a392d2. Actual current source and raw evidence supply this disposition.

## OTGD-018-AND-RAW-008-01 — PARTIAL

Participant explicitly includes an authorized recording — - **GIVEN** a distinct current export purpose and eligible retained source for the selected check - **WHEN** the participant reads the exact notice, selects the source and confirms the separate export - **THEN** recording or upload consent alone grants no export scope, the service job retains the exact authority, source selection, notice and acknowledgment timestamp, a lost receipt reuses the same key and body, and the archive verifies against that receipt before sharing.

Current proof: Raw default off and UI source/ack initially off; exact separate notice gates selection; recording approval alone freeze denied; controller lost receipt reuses body/key; backend completes exact raw worker archive.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/raw-export.test.ts::cloud export defaults raw off; explicit separate scope persists original acknowledgment and key through a lost receipt` — file SHA `c68c9146811b6261e384bef9759f0bde4a8a08f3be26391c888da40700d09359`, line 225; 1 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::actual raw export component keeps every source and separate acknowledgment off until exact purpose review, then resets for another owner` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1260; 4 current observation(s).
- `services/api/tests/test_raw_export.py::test_recording_upload_approval_never_grants_export` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 184; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_actual_http_async_worker_zip_download_replay_expiry_and_foreign_denial` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 418; 5 current observation(s).

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

Exact unproved clause(s):

- “service job retains exact authority, source selection, notice and acknowledgment timestamp ... archive verifies ... before sharing”: backend accepted job test compares job ID/purpose/selection but not persisted raw_scope+original timestamp; controller lost receipt test does not run archive download/inspector/share path for its reconciled receipt.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA a6839f9be58aef81bdde61fa75355e407c6d0568ed9316e16113d4895d593a62. Actual current source and raw evidence supply this disposition.

## OTGD-018-AND-RAW-008-02 — PASS

A raw member is substituted — - **GIVEN** a downloaded ZIP has internally rehashed files but a changed raw source version or an unselected binary member - **WHEN** the app compares the archive with the authenticated job receipt - **THEN** exact source ID, version, kind, SHA-256, size and retained lifetime are compared with the owned frozen job; substituted, unknown or orphan paths refuse sharing, and no broadened permission is inferred from recording consent.

Current proof: Inspector compares complete raw manifest with owned frozen receipt, including source tuple and lifetime (services/export.ts exact expected raw identity); direct tests rehash changed version/size/hash and orphan binary, all rejected. Same archive without separately authorized raw scope is rejected. Controller shareJob statically invokes inspector before shareArchive; no OS share delivery is inferred.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/raw-export.test.ts::rehashed raw version, size, digest, omitted-scope and orphan substitutions never expand the authenticated job scope` — file SHA `c68c9146811b6261e384bef9759f0bde4a8a08f3be26391c888da40700d09359`, line 104; 1 current observation(s).
- `apps/mobile/tests/raw-export.test.ts::actual authenticated Python scope, completed job and worker ZIP verify exact independent raw authority and versioned binary sources` — file SHA `c68c9146811b6261e384bef9759f0bde4a8a08f3be26391c888da40700d09359`, line 65; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 574993190ec2ace4fb1209ef1f837dcda270a2b85eb374d0f2329c5f0e44a2f3. Actual current source and raw evidence supply this disposition.

