# OTGD-029 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/production-mobile-platform/specs/android-offline-sync/spec.md`; SHA256 `388f00c1fab3eb1f905e140b7248ce8e737ae87349eb8a508068becbb51456b9`.

14 cases, 7 requirements: PARTIAL 10, PASS 4. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-029-AND-SYNC-001-01 — PARTIAL

Storage transaction succeeds — - **GIVEN** a completed permitted check - **WHEN** the finalization transaction commits - **THEN** the app shows **Saved on this device** and can reopen the same record after restart.

Current proof: Controlled native storage reopens its test-backed store and app local save keeps immutable evidence/no upload.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).
- `apps/mobile/tests/native-storage.test.ts::concurrent native partition initialization keeps one keystore key and separate handles, then reopened records remain readable` — file SHA `52005beea373ed0bf603dffffc6a20cb2e8fd07371bf5cb0712afa4b3bf208df`, line 128; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual installed native encrypted database process restart, successful save message and same-record reopen are not executed; controlled storage backend is not SQLCipher/OS evidence.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 38b301c062e8b1a86f9135cf121a55851b0ed26f3b650752495791382808b5b5. Actual current source and raw evidence supply this disposition.

## OTGD-029-AND-SYNC-001-02 — PARTIAL

Disk is full — - **GIVEN** the encrypted database write fails - **WHEN** the user finishes the check - **THEN** the app reports the save failure and does not show a success state or queue a nonexistent record.

Current proof: Native terminal write failure remains retryable and transaction/raw rollback guards exist.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/lifecycle.test.ts::failed terminal storage remains retryable using the native cached receipt` — file SHA `a69785a96f7fbe8c6193ba617741db43650cf9ad32a2eb595d92bf04ae9a4099`, line 133; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- No direct finished-check encrypted-write/DISK_FULL failure assertion verifies no success message, no queued nonexistent check and recoverable unchanged draft together. Native raw rollback/terminal handoff failures concern different operations.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 64c908d3919b07f409bb264e49988cdf6543d86256e667f70bf979f52c54e804. Actual current source and raw evidence supply this disposition.

## OTGD-029-AND-SYNC-002-01 — PARTIAL

Customer cancels upload sheet — - **GIVEN** a local-only check - **WHEN** the upload confirmation is canceled - **THEN** no network mutation occurs and the check remains local.

Current proof: Explicit upload queues only after controller action; guest cannot upload; generic confirmation cancellation tested for retries/local clear.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).
- `apps/mobile/e2e/components.spec.ts::confirmation components never enable retry or erase unsynced records on cancellation` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 656; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Actual account upload-sheet Cancel with a local check has no explicit network/queue/local-state assertion in current selected component/controller cases.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 9c6f4f062ad89120a2e55f0c575d91c43ea3a03b0c83b98dabde76921e455c8c. Actual current source and raw evidence supply this disposition.

## OTGD-029-AND-SYNC-002-02 — PARTIAL

Study consent is revoked — - **GIVEN** a previously queued study check - **WHEN** authorization is rechecked after revocation - **THEN** upload is blocked and the app explains the permission change without retrying as another account or study.

Current proof: Withdrawal fences queued/inflight consent and raw preferences; server current consent revocation refuses model/acquisition.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/sync.test.ts::withdrawal fences an in-flight consent against both a late receipt and a late retryable failure` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 77; 1 current observation(s).
- `services/api/tests/test_model_admission.py::test_current_authority_or_bytes_refusal_returns_no_score` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 480; 50 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Exact previously queued ordinary study-check upload after revoked consent must retain original account/study, stop retry and present permission change; existing consent-intent/raw fences are narrower operations.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 723e660ead247f39432c485a66b2af1e599bcc77b660caa10c30a0fcceb6272b. Actual current source and raw evidence supply this disposition.

## OTGD-029-AND-SYNC-003-01 — PASS

Response is lost after server acceptance — - **GIVEN** a finalize request committed remotely but its response was lost - **WHEN** the client retries - **THEN** it receives the same logical result/job and no second specimen/task/session is created.

Current proof: Client replays same registration identity/body and server finalization idempotency exists; actual browser preflight drops accepted finalization reply. Actual ordinary production web bundle at mobile/desktop: hosted PKCE local issuer; no cloud session until explicit upload; accepted finalize reply dropped then exact key/receipt replay; persisted worker measurement result; reload memory boundary; exact selected worker ZIP hashes; foreign denial; governed consent/withdrawal; accepted all-data deletion reply dropped and exact pending intent visible; actual completion and retired-generation denial; interactive reauthentication and generation acknowledgment preserve identity and leave empty inventory.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/sync.test.ts::a lost accepted response replays the same identity and unchanged bytes` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 290; 1 current observation(s).
- `apps/mobile/e2e/authenticated-live.spec.ts::ordinary web completes owned PKCE, explicit upload, worker export, lost-ack recovery, reload and privacy boundaries` — file SHA `3ec7e636797c30677205c3bde7e9ca64fe919b4c3513b1cf47453d52b87a468d`, line 220; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12597206063/authenticated-live.xml` — SHA256 `9128fd401f1a08b5023fd8cb6faa9ce340538cdeaf65d0addef0d8fc14d2473c`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/authenticated-live.xml` — SHA256 `d077dac5e8315553d8b2e4a574bca04ba3639fc7d2905c0aaec076f7974c8392`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Actual Docker/PostgreSQL/versioned S3/SQS/local-issuer fixtures are fictional. Not public Cognito, native encrypted persistence, physical capture or study approval. Awaiting-generation-ack current-generation write refusal is a separately narrowed residual.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 74d2fb4743057c8159c028b4442d28471b3dd0f8927b81242b168fe08af15621. Actual current source and raw evidence supply this disposition.

## OTGD-029-AND-SYNC-003-02 — PARTIAL

Queue body is changed under the same key — - **GIVEN** an existing accepted idempotency key - **WHEN** different content is submitted under that key - **THEN** the service returns 409 and the app exposes a conflict rather than changing the frozen record.

Current proof: Real API changed profile body under accepted key returns409; client queue409 preserves snapshot hash and conflict state.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_profile_initial_missing_stale_etag_and_replay` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 158; 5 current observation(s).
- `apps/mobile/tests/sync.test.ts::conflict and stale generation stop automatic replay without changing frozen evidence` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 305; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Same check-upload queued body changed under its own accepted key, conflict state and original frozen evidence preserved in one context not directly asserted; generic profile-key/client409 tests are different contexts.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA dd2796affe2071071586eabccea1ab4c6dd1c5ddf27799ebe927fb70cf56e389. Actual current source and raw evidence supply this disposition.

## OTGD-029-AND-SYNC-004-01 — PARTIAL

Two accounts use one phone — - **GIVEN** account A has unsynced records - **WHEN** A signs out and B signs in - **THEN** B cannot list or upload A's records.

Current proof: Epoch/account changes reject late sync and reset current workspace.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/sync.test.ts::a new account epoch prevents late network results writing into its workspace` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 352; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual same phone locked native account cache A signout/B login/list/upload isolation is not executed on installed OS; controlled epoch tests supply partial software evidence.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4db021eaea15f29924671e115cefe2c828dc7d2f74b725de25b1736b841c60e3. Actual current source and raw evidence supply this disposition.

## OTGD-029-AND-SYNC-004-02 — PARTIAL

Production build receives local configuration — - **GIVEN** a production app/backend configuration - **WHEN** a local issuer or AWS-emulator endpoint is supplied - **THEN** startup fails closed; the configuration cannot silently redirect participant data.

Current proof: Configured issuer/client mismatches and hosted-preview production rejection are tested; no current local app fallback is claimed.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/hosted-preview.test.ts::the hosted preview build flag is local-only and cannot alter QA or production account behavior` — file SHA `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb`, line 93; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Exact startup tuple of production app AND backend with local issuer/emulator endpoint needs complete mapped config assertions; OAuth endpoint pinning independently remains a known defect in other auth cases.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 7ff710e1e3fbd2f351ec1bceb2acdb8ae4c88a826b7066aa4744c7d78a13be74. Actual current source and raw evidence supply this disposition.

## OTGD-029-AND-SYNC-005-01 — PASS

Another device finalized the session — - **GIVEN** a stale local ETag - **WHEN** PUT snapshot returns 412 for its stale precondition or 409 for a frozen-state conflict - **THEN** the app fetches the server state and does not overwrite it.

Current proof: 409/412 conflicts pause replay and retain frozen hash. Actual ApiClient error parsing and SyncEngine guardedreadback preserves local evidence/key, holds conflict, rejects changed scope/foreign response; actual saved JSX presents verified comparison and linked correction.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/sync.test.ts::conflict and stale generation stop automatic replay without changing frozen evidence` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 305; 1 current observation(s).
- `apps/mobile/tests/sync-conflict.test.ts::snapshot 412 and frozen 409 read back one authoritative revision without changing or replaying pending evidence` — file SHA `d07ac22260034e8b944704a194419121035b2ac3c56992f4b3e6fe80fd7d997f`, line 107; 1 current observation(s).
- `apps/mobile/tests/sync-conflict.test.ts::conflict readback cannot publish after epoch, generation, owner or cancellation changes` — file SHA `d07ac22260034e8b944704a194419121035b2ac3c56992f4b3e6fe80fd7d997f`, line 155; 1 current observation(s).
- `apps/mobile/tests/sync-conflict.test.ts::unavailable or foreign authoritative readback stays a preserved conflict and never substitutes local data` — file SHA `d07ac22260034e8b944704a194419121035b2ac3c56992f4b3e6fe80fd7d997f`, line 200; 1 current observation(s).
- `apps/mobile/tests/result-ui.test.ts::actual saved conflict offers a verified server comparison and linked correction while keeping upload stopped` — file SHA `217ae43bfcae4cb9826bafd8ad66bef8e97327c0638400c0e6263c5eb7d66a60`, line 351; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Controlled HTTP/component transport; complete live dependencies/current native storage not established.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 437081a25ee80518ff9149d802873a4394c6691a7ad034a3a4953cfd2d879b30. Actual current source and raw evidence supply this disposition.

## OTGD-029-AND-SYNC-005-02 — PARTIAL

Correcting an accepted value — - **GIVEN** a finalized session requires correction - **WHEN** a correction is created - **THEN** reacquisition uses a new session UUID/target time and supersedes reference with no earlier physical components copied; an administrative report correction remains a distinct authorized workflow.

Current proof: Replacement controller allocates newUUID, supersedes link and zero attempts; replacement pure test verifies new target/sample and immutable old hashes; report-revision parser verifies separate correction/reanalysis identities.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).
- `apps/mobile/tests/replacements.test.ts::local original and replacement links are bidirectional without changing either snapshot` — file SHA `5942e7dddc7b8e7c403b71d242c7168c28f64890db69543091331e89bea60233`, line 47; 1 current observation(s).
- `apps/mobile/tests/report-revisions.test.ts::actual backend correction and delayed reanalysis preserve immutable original evidence and exact carried-forward readings` — file SHA `4d1d9f5becc44e8d716ab339de02cdd5c3afde155d2afbbdec5957c33114c3fb`, line 46; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- A finalized physical prior capture reset and authorized administrative workflow are not exercised together here; retain separate physical/role integration scope rather than claim full correction journey.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4aa9dc8e9f7a01f2133a9e59763082916f7e75a2ea8fc146aa8bab499cb3f304. Actual current source and raw evidence supply this disposition.

## OTGD-029-AND-SYNC-006-01 — PASS

Rate limit response — - **GIVEN** HTTP 429 with a valid Retry-After - **WHEN** scheduling the next attempt - **THEN** the queue honors the delay within a documented bound and shows a waiting state.

Current proof: Source schedules Retry-After or bounded exponential delay and records retry_wait. Exact bounded retry deadlines/control and terminal422safe path/code allowlist with actual JSX inspection; sensitive arbitrary payload never displayed.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::HTTP concurrency and generation errors never force overwrite` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 477; 1 current observation(s).
- `apps/mobile/tests/sync-conflict.test.ts::HTTP 429 Retry-After waits even on explicit retry and becomes eligible at its boundary` — file SHA `d07ac22260034e8b944704a194419121035b2ac3c56992f4b3e6fe80fd7d997f`, line 227; 1 current observation(s).
- `apps/mobile/tests/sync-conflict.test.ts::HTTP 422 retains terminal field errors for inspection without retrying immutable snapshot` — file SHA `d07ac22260034e8b944704a194419121035b2ac3c56992f4b3e6fe80fd7d997f`, line 256; 1 current observation(s).
- `apps/mobile/tests/sync-conflict.test.ts::422 field inspection retains bounded paths and safe codes rather than response inputs or arbitrary values` — file SHA `d07ac22260034e8b944704a194419121035b2ac3c56992f4b3e6fe80fd7d997f`, line 277; 1 current observation(s).
- `apps/mobile/tests/sync-conflict.test.ts::Retry-After beyond one hour requires manual same-intent retry after the full server deadline` — file SHA `d07ac22260034e8b944704a194419121035b2ac3c56992f4b3e6fe80fd7d997f`, line 316; 1 current observation(s).
- `apps/mobile/tests/result-ui.test.ts::actual saved-check upload issue shows bounded validation paths and redacted codes without sensitive response values` — file SHA `217ae43bfcae4cb9826bafd8ad66bef8e97327c0638400c0e6263c5eb7d66a60`, line 326; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Software queue/render scope; shared cases may reuse these meaningful assertions rather than duplicate.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 50899392e1b8d07e1fb4c8b7a4e834b5c8c772e3571d9b368f224d74cb470a6d. Actual current source and raw evidence supply this disposition.

## OTGD-029-AND-SYNC-006-02 — PASS

Invalid snapshot — - **GIVEN** HTTP 422 - **WHEN** the client classifies the failure - **THEN** automatic retry stops and the customer can inspect the reported field error.

Current proof: Source classifies422 blocked. ApiClient retains fields, but queue error mapper discards them. Exact bounded retry deadlines/control and terminal422safe path/code allowlist with actual JSX inspection; sensitive arbitrary payload never displayed.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::HTTP concurrency and generation errors never force overwrite` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 477; 1 current observation(s).
- `apps/mobile/tests/sync-conflict.test.ts::HTTP 429 Retry-After waits even on explicit retry and becomes eligible at its boundary` — file SHA `d07ac22260034e8b944704a194419121035b2ac3c56992f4b3e6fe80fd7d997f`, line 227; 1 current observation(s).
- `apps/mobile/tests/sync-conflict.test.ts::HTTP 422 retains terminal field errors for inspection without retrying immutable snapshot` — file SHA `d07ac22260034e8b944704a194419121035b2ac3c56992f4b3e6fe80fd7d997f`, line 256; 1 current observation(s).
- `apps/mobile/tests/sync-conflict.test.ts::422 field inspection retains bounded paths and safe codes rather than response inputs or arbitrary values` — file SHA `d07ac22260034e8b944704a194419121035b2ac3c56992f4b3e6fe80fd7d997f`, line 277; 1 current observation(s).
- `apps/mobile/tests/sync-conflict.test.ts::Retry-After beyond one hour requires manual same-intent retry after the full server deadline` — file SHA `d07ac22260034e8b944704a194419121035b2ac3c56992f4b3e6fe80fd7d997f`, line 316; 1 current observation(s).
- `apps/mobile/tests/result-ui.test.ts::actual saved-check upload issue shows bounded validation paths and redacted codes without sensitive response values` — file SHA `217ae43bfcae4cb9826bafd8ad66bef8e97327c0638400c0e6263c5eb7d66a60`, line 326; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Software queue/render scope; shared cases may reuse these meaningful assertions rather than duplicate.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8ad03c6598145d24d80a638aa61e82131981a4da0670b0c08a68ea82a20a6845. Actual current source and raw evidence supply this disposition.

## OTGD-029-AND-SYNC-007-01 — PARTIAL

Upload occurs after a day offline — - **GIVEN** a previously captured record - **WHEN** it reaches the service the next day - **THEN** history retains the original check time and separately records synchronization/evaluation time.

Current proof: History helper uses acquisition time/stable IDs and report revisions preserve original target.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/support-history.test.ts::mixed local and synced history uses acquisition time and stable identity ties` — file SHA `69eb3cea0dd3adba88f964c5b9fedd872f60b0488d53aad4fd242320aecf5f69`, line 115; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Exact record uploaded after one-day offline period lacks a combined assertion of original history time plus distinct sync/evaluation time. Old laboratory correction/row sorting contexts are narrower.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 522993ec5ab99dcd19b3d67edb6c0f7710010400ae2396450e0c34882d9a679c. Actual current source and raw evidence supply this disposition.

## OTGD-029-AND-SYNC-007-02 — PARTIAL

Reboot during scored game — - **GIVEN** an interrupted reaction run in a restored draft - **WHEN** the application restarts - **THEN** it marks that attempt invalid and cannot submit it as a completed uninterrupted task.

Current proof: Pure domain process interruption yields invalid task and null aggregate features.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::process interruption preserves invalid task evidence with null aggregate features` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 270; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual installed-app process death/restart retaining draft and refusing uninterrupted completion remains native OS integration evidence gap.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 3891176bcd03db71d981fb393eb9c427bd69472c0fa6295c2781ca59819e7774. Actual current source and raw evidence supply this disposition.

