# OTGD-031: verification results

Canonical: `openspec/changes/production-mobile-platform/specs/android-privacy-controls/spec.md`; SHA-256 `993e7c0f65b5ee4bd9b2f470e2d4111f6329f083e7650a76ab71f78abf5e9f3f`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Owner: `/root/verification`; OpenAI `gpt-6.1-sol/high` requested in PM dispatch; effective model identifier not independently exposed inside this worker. Scope: verification planning and static source inspection only. Relevant acknowledged decisions: D-001–005 v1 and D-006 v3; superseded D-006 v1/v2 retained as history. Execution candidate is not frozen.

Result: **NOT_RUN**. 7 individually identified requirements and 17 canonical acceptance cases are planned in `test-plan.md`. No current-source runtime suite, browser, native, firmware, live-dependency or performance result is claimed by this document. No historical evidence is transferred.

| Evidence class | Actual activity / outcome | Status |
|---|---|---|
| Planning inspection | Read canonical requirements/scenarios and shared contracts; indexed existing test symbols, CI gates and workflow commands. Source hashes appear in test-plan.md and shared report. This is not a passing acceptance test. | EXECUTED inspection only |
| Related automated checks | Commands and named assertions planned; no execution authorized in this assignment. Exit code, execution timestamp and artifact hash therefore absent. | NOT_RUN |
| Complete criterion coverage | Every case requires full acceptance assertions; related symbol matching is not proof of complete coverage. No-match cases are explicitly identified in the plan. | NOT_RUN |
| Browser/native/firmware/real dependencies/performance | Scope-specific prerequisites and commands in plan/shared report; no substitution from unit mocks or historical CI. | NOT_RUN |
| Physical/scientific/release qualification | No actual participant/device/study/assay/deployment/store evidence adopted; external approvals remain separate. | BLOCKED where applicable |

## Current case results

All stable case IDs in test-plan.md are NOT_RUN, except explicitly external-only cases which are BLOCKED on named acceptance evidence. On execution replace this aggregate with one result row per affected case, retaining command/procedure, environment, UTC time, observed outcome, exit code, evidence path/hash and exact candidate/test bindings. Do not turn expected THEN statements into observed results.

No completion, engineering/product signoff or council PASS follows from this planning record.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

Final-candidate acceptance remains **NOT_RUN**; actual focused author executions are preserved below separately and do not establish this whole dossier PASS. Source/content changes after a focused run require fresh admission and affected reruns.

No new focused execution is adopted into this dossier in this audit. New UI/permissions/live/worker sources are WIP until author release and final bound execution; baseline firmware evidence retains its separate source/qualification limits.

Independent source assertion audits for this dossier: Actual-process interruption probe source audit; Authenticated ordinary-web live test source audit. Full assertion/limit details are in test-plan.md.


## Completed historical baseline semantic audit

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`: all 17 stable cases for this dossier were individually adjudicated against actual assertion bodies and named raw evidence. Counts: `{"BLOCKED": 2, "PARTIAL": 13, "PASS": 2}`. The complete case rows, exact remaining clauses and evidence references are in [this dossier's audit index](../../reports/acceptance-baseline-28e0729/OTGD-031-cases.md); full structured bodies and hash bindings are preserved in [acceptance-evidence.zip](../../reports/acceptance-baseline-28e0729/acceptance-evidence.zip). Archive SHA256 `89804264880c9a8e7676fb232eff570ff47921ec74cf11596400329ceb641ff8` was read back and all67member hashes matched.

These are historical scoped decisions, not current replacement acceptance. A PARTIAL case does not automatically establish a production defect or absent test; exact shared assertion evidence and unavailable external prerequisites remain distinct. Current canonical SHA256 at this checkpoint is `993e7c0f65b5ee4bd9b2f470e2d4111f6329f083e7650a76ab71f78abf5e9f3f`. Preserve the old candidate's canonical hash in the archived row. Current corrections require fresh frozen-source gates, affected case binding and independent confirmations; final approval remains pending.


## Final corrected source evidence — e89897cc852a

# OTGD-031 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/production-mobile-platform/specs/android-privacy-controls/spec.md`; SHA256 `993e7c0f65b5ee4bd9b2f470e2d4111f6329f083e7650a76ab71f78abf5e9f3f`.

17 cases, 7 requirements: BLOCKED 2, PARTIAL 9, PASS 6. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-031-AND-PRIV-001-01 — PARTIAL

priv-enable-queued-upload-retries — - **GIVEN** a signed-in account with one explicitly queued check and another unqueued local check - **WHEN** the user confirms Enable automatic retries - **THEN** only the already queued check is eligible for automatic retry and the other check, raw media, and research data remain unqueued.

Current proof: RetryDue operates existing queue only; preference off suppresses automatic request; Save does not queue.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/sync.test.ts::reconnection does not retry an ordinary explicit queue when preference remains off` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 280; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- One explicitly queued plus one unqueued account check/raw/research context and Enable confirmation is not asserted as a full selection-preservation conjunction.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 096bed96a9d4b6c13dc14bb984cd0b0c91a25e00dbc6dfd08beace1aaf62adc7. Actual current source and raw evidence supply this disposition.

## OTGD-031-AND-PRIV-001-02 — PARTIAL

priv-disable-during-upload — - **GIVEN** a permitted upload is in flight and more operations are queued - **WHEN** the user disables automatic retries - **THEN** no new automatic retry starts, the in-flight outcome is reconciled honestly, and the UI does not claim previously accepted data was deleted.

Current proof: Source cancellation message states accepted data not erased; auto-retry preference controls future retryDue.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/sync.test.ts::reconnection does not retry an ordinary explicit queue when preference remains off` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 280; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Disabling preference during actual in-flight upload, honest reconciliation and no subsequent auto retry require direct same-context assertions.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA ac4fb0217c815702485a6bb67812f5f86f3c6cf716a178d7d079dafcde05debc. Actual current source and raw evidence supply this disposition.

## OTGD-031-AND-PRIV-002-01 — PARTIAL

priv-clear-demo-only — - **GIVEN** demo and account caches coexist - **WHEN** Clear demo records is confirmed - **THEN** demo records disappear, account records remain, and no cloud deletion request is made.

Current proof: ClearLocal replaces only current workspace and preserves deletion/withdrawal/fences; guest/account stores partitioned.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Demo and account caches coexist, clear demo only, untouched account digest and zero cloud deletion in same test context not directly asserted. Native cache partition remains actual OS gap too.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA afd52dc97573adf5d450d08b5bcb732428ba73892617d5edfd61b16d188ec573. Actual current source and raw evidence supply this disposition.

## OTGD-031-AND-PRIV-002-02 — PARTIAL

priv-cancel-unsynced-clear — - **GIVEN** three account records are unsynchronized - **WHEN** the warning shows three and the user selects Cancel - **THEN** all records and queue entries remain unchanged.

Current proof: Actual component cancel after one-unsynced warning retains saved row and does not enable retry.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/components.spec.ts::confirmation components never enable retry or erase unsynced records on cancellation` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 656; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Specified three unsynced records/count3 and unchanged queue+all record digests on Cancel not asserted; current browser fixture has one and checks one visible row only.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5814723de16008fa49874bd90f443626cf305cce5964c4ec6642dea91930b5d3. Actual current source and raw evidence supply this disposition.

## OTGD-031-AND-PRIV-003-01 — PASS

priv-valid-data-deletion — - **GIVEN** an owned account, current policy review, and reauthentication within five minutes - **WHEN** the user confirms deletion of profile and check data - **THEN** one all_data job is accepted and the account identity is retained according to the displayed scope.

Current proof: Real API deletion replay returns one job, account remains awaiting generation ack; auth_time301s rejected; controller requires fresh sign-in and separate confirmation. Actual ordinary production web bundle at mobile/desktop: hosted PKCE local issuer; no cloud session until explicit upload; accepted finalize reply dropped then exact key/receipt replay; persisted worker measurement result; reload memory boundary; exact selected worker ZIP hashes; foreign denial; governed consent/withdrawal; accepted all-data deletion reply dropped and exact pending intent visible; actual completion and retired-generation denial; interactive reauthentication and generation acknowledgment preserve identity and leave empty inventory.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_deletion_barrier_survives_journal_failure_and_same_key_resumes` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 314; 5 current observation(s).
- `services/api/tests/test_api.py::test_reauthentication_required_for_sensitive_jobs` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 362; 5 current observation(s).
- `apps/mobile/e2e/authenticated-live.spec.ts::ordinary web completes owned PKCE, explicit upload, worker export, lost-ack recovery, reload and privacy boundaries` — file SHA `3ec7e636797c30677205c3bde7e9ca64fe919b4c3513b1cf47453d52b87a468d`, line 220; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12597206063/authenticated-live.xml` — SHA256 `9128fd401f1a08b5023fd8cb6faa9ce340538cdeaf65d0addef0d8fc14d2473c`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/authenticated-live.xml` — SHA256 `d077dac5e8315553d8b2e4a574bca04ba3639fc7d2905c0aaec076f7974c8392`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Actual Docker/PostgreSQL/versioned S3/SQS/local-issuer fixtures are fictional. Not public Cognito, native encrypted persistence, physical capture or study approval. Awaiting-generation-ack current-generation write refusal is a separately narrowed residual.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA e544329bd6f4716f2cdef0295ae4bc3b409bd5380a88838242c4847f1343447c. Actual current source and raw evidence supply this disposition.

## OTGD-031-AND-PRIV-003-02 — PARTIAL

priv-forged-owner-or-stale-auth — - **GIVEN** a deletion body contains another owner's ID or authentication is stale - **WHEN** it is submitted - **THEN** the server rejects it and no deletion job affects another account or bypasses reauthentication.

Current proof: Actual stale auth_time301s sensitive deletion request refuses401.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_reauthentication_required_for_sensitive_jobs` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 362; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- No direct deletion request body foreign-ownerID test and unchanged foreign-job/account inventory assertion is located; generic typed-body/owner-derived implementation alone is not that exact execution.

Prerequisite/evidence type: software_assertion_or_integration_evidence, independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 24da2adc96e25e3c2d5e5588e694048432a9ee91fd93567a64bcb9d3aab3c975. Actual current source and raw evidence supply this disposition.

## OTGD-031-AND-PRIV-004-01 — PASS

priv-deletion-response-lost — - **GIVEN** the server accepted a deletion but its response was lost - **WHEN** the app retries with the same key and scope - **THEN** the same job is returned and the UI remains requested/running until actual completion is reported.

Current proof: API original deletion key resumes after journal failure and replays same job; client preserves exact original deletion key/gen. Actual ordinary production web bundle at mobile/desktop: hosted PKCE local issuer; no cloud session until explicit upload; accepted finalize reply dropped then exact key/receipt replay; persisted worker measurement result; reload memory boundary; exact selected worker ZIP hashes; foreign denial; governed consent/withdrawal; accepted all-data deletion reply dropped and exact pending intent visible; actual completion and retired-generation denial; interactive reauthentication and generation acknowledgment preserve identity and leave empty inventory.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_deletion_barrier_survives_journal_failure_and_same_key_resumes` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 314; 5 current observation(s).
- `apps/mobile/tests/sync.test.ts::accepted deletion intent may reconcile with its old generation and original key` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 322; 1 current observation(s).
- `apps/mobile/e2e/authenticated-live.spec.ts::ordinary web completes owned PKCE, explicit upload, worker export, lost-ack recovery, reload and privacy boundaries` — file SHA `3ec7e636797c30677205c3bde7e9ca64fe919b4c3513b1cf47453d52b87a468d`, line 220; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12597206063/authenticated-live.xml` — SHA256 `9128fd401f1a08b5023fd8cb6faa9ce340538cdeaf65d0addef0d8fc14d2473c`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/authenticated-live.xml` — SHA256 `d077dac5e8315553d8b2e4a574bca04ba3639fc7d2905c0aaec076f7974c8392`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Actual Docker/PostgreSQL/versioned S3/SQS/local-issuer fixtures are fictional. Not public Cognito, native encrypted persistence, physical capture or study approval. Awaiting-generation-ack current-generation write refusal is a separately narrowed residual.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 620243afd35739a6dbff3ac1fcbe38f7b24575a6d0f14414ce0dcd061e6d3ff2. Actual current source and raw evidence supply this disposition.

## OTGD-031-AND-PRIV-004-02 — PASS

priv-retention-exception — - **GIVEN** a kind=deletion job reports partially_retained for a named audit category retained until a stated date - **WHEN** status is shown - **THEN** that exception remains visible and the app does not claim every copy was erased.

Current proof: JobCard warns partially_retained is not complete erasure; server emits actual named retained categories as strings. Actual handler receipt fixture→real parser→realJobCard names/basis/reason/null or suppliedexpiry, boundedlegacytruthfulcopy and browserupdate assertions.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::privacy jobs keep deletion-only and export-only terminal states separate` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 454; 1 current observation(s).
- `services/api/tests/test_privacy_receipts.py::test_deletion_api_receipt_keeps_named_retention_basis_reason_and_unspecified_expiry` — file SHA `84efc2d18bd0bcced419d82a6877e619b2bc1924a06118333b74cbe0f3c0c1d7`, line 12; 5 current observation(s).
- `apps/mobile/tests/privacy-receipt.test.ts::actual Python API deletion receipt survives client admission and JobCard rendering with all factual retention details` — file SHA `064fd7d4007a4a2f9752a98c557b35af90e1958145d1326bf047b91144c4d6f3`, line 45; 1 current observation(s).
- `apps/mobile/tests/privacy-receipt.test.ts::legacy category strings retain their real names and honestly disclose missing policy, reason and expiry` — file SHA `064fd7d4007a4a2f9752a98c557b35af90e1958145d1326bf047b91144c4d6f3`, line 61; 1 current observation(s).
- `apps/mobile/tests/privacy-receipt.test.ts::supplied category expiry is displayed exactly and separately from the overall job expiry` — file SHA `064fd7d4007a4a2f9752a98c557b35af90e1958145d1326bf047b91144c4d6f3`, line 77; 1 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::actual API privacy receipt renders category policy reason and supplied or absent expiry without generic legacy names` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1526; 4 current observation(s).

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

Scope limits: No universalphysicalerasure/changedretention/scientific/legalauthority implied.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA e9cc324ed4cc20cd96d939464e96466d9461246aafafe02d4384342fd462053e. Actual current source and raw evidence supply this disposition.

## OTGD-031-AND-PRIV-004-03 — PASS

priv-job-kind-state-discriminator — - **GIVEN** a completed export and a partially_retained deletion are returned by the shared job route - **WHEN** Privacy routes each response - **THEN** export-only expired is never interpreted as deletion state; partially_retained displays the listed exception and no partially_completed fallback is created.

Current proof: Parser rejects expired deletion, partially_retained export and invented partially_completed. Actual handler receipt fixture→real parser→realJobCard names/basis/reason/null or suppliedexpiry, boundedlegacytruthfulcopy and browserupdate assertions.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::privacy jobs keep deletion-only and export-only terminal states separate` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 454; 1 current observation(s).
- `services/api/tests/test_privacy_receipts.py::test_deletion_api_receipt_keeps_named_retention_basis_reason_and_unspecified_expiry` — file SHA `84efc2d18bd0bcced419d82a6877e619b2bc1924a06118333b74cbe0f3c0c1d7`, line 12; 5 current observation(s).
- `apps/mobile/tests/privacy-receipt.test.ts::actual Python API deletion receipt survives client admission and JobCard rendering with all factual retention details` — file SHA `064fd7d4007a4a2f9752a98c557b35af90e1958145d1326bf047b91144c4d6f3`, line 45; 1 current observation(s).
- `apps/mobile/tests/privacy-receipt.test.ts::legacy category strings retain their real names and honestly disclose missing policy, reason and expiry` — file SHA `064fd7d4007a4a2f9752a98c557b35af90e1958145d1326bf047b91144c4d6f3`, line 61; 1 current observation(s).
- `apps/mobile/tests/privacy-receipt.test.ts::supplied category expiry is displayed exactly and separately from the overall job expiry` — file SHA `064fd7d4007a4a2f9752a98c557b35af90e1958145d1326bf047b91144c4d6f3`, line 77; 1 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::actual API privacy receipt renders category policy reason and supplied or absent expiry without generic legacy names` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1526; 4 current observation(s).

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

Scope limits: No universalphysicalerasure/changedretention/scientific/legalauthority implied.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4f4b236941363af9b862091510bdc25d33659915bffb1613a5711f43809d508d. Actual current source and raw evidence supply this disposition.

## OTGD-031-AND-PRIV-005-01 — PASS

priv-offline-device-reconnects — - **GIVEN** device A completed all_data deletion while device B held old queued records offline - **WHEN** B reconnects - **THEN** the server returns 410 for new stale-generation mutations and B quarantines their original operations instead of rebinding or restoring them.

Current proof: API real current suite accepts all_data deletion, advances generation and rejects distinct stale-generation mutation410; client sync410 quarantines queue without changing frozen hash, generation-quarantine preserves original request generation and deletion intent. This proves software multi-client generation protocol, not installed-phone storage lifecycle.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_deletion_barrier_survives_journal_failure_and_same_key_resumes` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 314; 5 current observation(s).
- `apps/mobile/tests/sync.test.ts::conflict and stale generation stop automatic replay without changing frozen evidence` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 305; 1 current observation(s).
- `apps/mobile/tests/generation-cache.test.ts::generation quarantine clears cached history, selections and consent without discarding exact deletion receipts` — file SHA `2a30b7da6606d73d185be5efed38968469e3fcde816063890f8e63bd7b32d756`, line 34; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 7ee32b8251bd7f70803d09bb6a0d2d6c5cf9ee84bd6e8d50cf20224d356b0e6f. Actual current source and raw evidence supply this disposition.

## OTGD-031-AND-PRIV-005-02 — PARTIAL

priv-late-fetch-after-clear — - **GIVEN** an old-history fetch is in flight when account deletion is accepted - **WHEN** the fetch returns - **THEN** its payload cannot recreate deleted local content.

Current proof: Controller rejects delayed history after signout; workspace scope rejects delayed exports on generation/fence/epoch change.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::delayed history cannot enter another account or reopen a signed-out workspace` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 777; 1 current observation(s).
- `apps/mobile/tests/workspace-scope.test.ts::a delayed export download never reaches sharing after generation change or local clear` — file SHA `d009b00717789b980a437f76ee379dbf1f3771aac46021d718f649b30544339d`, line 51; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Direct account-deletion accepted or ClearLocal history-fetch race is not executed in these contexts; prove old history response cannot repopulate after the actual destructive controller action.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA d3ab6533f4b8cba2343ec97b37f1849bdd644e6eab2d97ce5bc4b84f5bad59ed. Actual current source and raw evidence supply this disposition.

## OTGD-031-AND-PRIV-005-03 — PARTIAL

priv-explicit-generation-reset-required — - **GIVEN** an all_data deletion finished and the account remains usable - **WHEN** the user returns to Profile or Check before acknowledging the new generation - **THEN** old queued records remain quarantined and new protected writes stay blocked until Start a new empty workspace is explicitly confirmed.

Current proof: Controller quarantines current retired check, blocks beginCheck while deleting, requires awaiting_generation_ack for action and resets profile/checks after explicit ack. Actual ordinary production web bundle at mobile/desktop: hosted PKCE local issuer; no cloud session until explicit upload; accepted finalize reply dropped then exact key/receipt replay; persisted worker measurement result; reload memory boundary; exact selected worker ZIP hashes; foreign denial; governed consent/withdrawal; accepted all-data deletion reply dropped and exact pending intent visible; actual completion and retired-generation denial; interactive reauthentication and generation acknowledgment preserve identity and leave empty inventory.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::server generation retirement quarantines prior checks and a new empty workspace requires separate acknowledgment` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 806; 1 current observation(s).
- `apps/mobile/e2e/authenticated-live.spec.ts::ordinary web completes owned PKCE, explicit upload, worker export, lost-ack recovery, reload and privacy boundaries` — file SHA `3ec7e636797c30677205c3bde7e9ca64fe919b4c3513b1cf47453d52b87a468d`, line 220; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12597206063/authenticated-live.xml` — SHA256 `9128fd401f1a08b5023fd8cb6faa9ce340538cdeaf65d0addef0d8fc14d2473c`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/authenticated-live.xml` — SHA256 `d077dac5e8315553d8b2e4a574bca04ba3639fc7d2905c0aaec076f7974c8392`.

Exact unproved clause(s):

- Before explicit acknowledgment in awaiting_generation_ack, current-generation protected writes must remain blocked and original queues quarantined. Current actual browser proves retired-generation refusal, retained identity, interactive generation acknowledgment and an empty fresh workspace; it does not issue a new-generation protected write before acknowledgment.

Prerequisite/evidence type: software_authority_boundary_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Scope limits: Actual Docker/PostgreSQL/versioned S3/SQS/local-issuer fixtures are fictional. Not public Cognito, native encrypted persistence, physical capture or study approval. Awaiting-generation-ack current-generation write refusal is a separately narrowed residual.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA b71a01a2170d21edc98dd74d1e4e3383382cea42fb1b16c941bbb07212623d11. Actual current source and raw evidence supply this disposition.

## OTGD-031-AND-PRIV-005-04 — PASS

priv-deletion-replay-does-not-create-new-job — - **GIVEN** a deletion was accepted and advanced generation but its response was lost - **WHEN** the exact original idempotent request is replayed under the shared replay policy - **THEN** the original job is returned; a distinct mutation carrying the old generation receives 410 and is quarantined.

Current proof: Same real API test replays original deletion key/body after generation advancement and gets original jobID, while distinct stale mutation returns410; client deletion intent keeps old generation/key and ordinary stale operations quarantine. Scope is idempotency/anti-resurrection software protocol.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_deletion_barrier_survives_journal_failure_and_same_key_resumes` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 314; 5 current observation(s).
- `apps/mobile/tests/sync.test.ts::accepted deletion intent may reconcile with its old generation and original key` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 322; 1 current observation(s).
- `apps/mobile/tests/sync.test.ts::conflict and stale generation stop automatic replay without changing frozen evidence` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 305; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 6e6e6219eb724e919f7220ac301a7671f2f6b4ebf72fbf086f3d4b0763de347f. Actual current source and raw evidence supply this disposition.

## OTGD-031-AND-PRIV-006-01 — PARTIAL

priv-unconfigured-retention — - **GIVEN** production has no approved policy for raw eye recordings - **WHEN** the privacy and capture availability screens load - **THEN** raw recording is unavailable and no generic consent checkbox enables it.

Current proof: Missing/invalid raw-purpose terms reject; defaults record/upload off and explicit purpose receipt required.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/raw-recordings.test.ts::default off, local-only opt-in, upload dependency, policy expiry and pending stop fences remain distinct` — file SHA `f2d9a32b5ff0e11ca6aacfb3ea86b246341a1900cfa0042623a0552222900a08`, line 77; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Production unconfigured-retention screen with generic consent checkbox attempted needs actual rendered unavailable/no recording assertion; default-off with approved fixture is narrower.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4520783d69c7ccdee43539674e70d73ce67fe7c453db50d0bcf31a6b58953594. Actual current source and raw evidence supply this disposition.

## OTGD-031-AND-PRIV-006-02 — PARTIAL

priv-redacted-deletion-log — - **GIVEN** a deletion request fails validation - **WHEN** the event is logged - **THEN** logs include a redacted operation/request reference and reason category without tokens, profile values, or measurements.

Current proof: Diagnostics helper filters health/token/error payload; API errors use request IDs/reason codes.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/support-history.test.ts::support diagnostics copy only bounded explicit fields, never an error payload` — file SHA `69eb3cea0dd3adba88f964c5b9fedd872f60b0488d53aad4fd242320aecf5f69`, line 10; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual deletion-validation failure log emission/content is not captured in mapped tests; diagnostics clipboard sanitization is not server application-log evidence. Bind sanitized failure logs or add logger capture assertion, without tokens/profile/measurements.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0c0ffea9e8b9a4bc983bdf7a580d162d71fd215db13f59b1db24fb1779ad1bcc. Actual current source and raw evidence supply this disposition.

## OTGD-031-AND-PRIV-007-01 — BLOCKED

priv-accessible-confirmation — - **GIVEN** TalkBack and 200% text scaling - **WHEN** the deletion review opens - **THEN** scope, retention exceptions, and both final/cancel actions are reachable before confirmation can occur.

Current proof: Actual OS/accessibility or physical prerequisite absent; controlled fixtures/builds may provide partial software support only.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/workspace-scope.test.ts::scope checks reject a stale error and a previously opened destructive confirmation` — file SHA `d009b00717789b980a437f76ee379dbf1f3771aac46021d718f649b30544339d`, line 73; 1 current observation(s).
- `apps/mobile/e2e/components.spec.ts::confirmation components never enable retry or erase unsynced records on cancellation` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 656; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- priv-accessible-confirmation — - **GIVEN** TalkBack and 200% text scaling - **WHEN** the deletion review opens - **THEN** scope, retention exceptions, and both final/cancel actions are reachable before confirmation can occur.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA dfa5ed7d004529a5af1aa5b9ec76f6ccb267a839cb6be8f911bba13e45b6093c. Actual current source and raw evidence supply this disposition.

## OTGD-031-AND-PRIV-007-02 — BLOCKED

priv-ios-account-deletion — - **GIVEN** an authenticated iOS account - **WHEN** the user completes in-app account deletion review and reauthentication - **THEN** the same scoped asynchronous job is requested and its completion status is represented without sending the user to an unrelated website.

Current proof: In-app deletion controller constructs scoped asynchronous account job after reauth.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_reauthentication_required_for_sensitive_jobs` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 362; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Actual installed iOS account deletion review, reauthentication and completion presentation is not executed; browser/controlled callbacks do not establish native in-app route.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 2d80c04ab599c581dea589fd5936dad405470722c11803818bca8915e75acd35. Actual current source and raw evidence supply this disposition.
