# OTGD-020 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/production-mobile-platform/specs/android-app-environment/spec.md`; SHA256 `6cef683b7ac1b04bdf104e0b87aa36badf61e905580d32223c05a39ce8efac35`.

14 cases, 7 requirements: PARTIAL 8, PASS 6. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-020-AND-ENV-001-01 — PARTIAL

QA and production are installed together — - **GIVEN** separate configured builds - **WHEN** both run on one phone - **THEN** they have distinct app identities and local namespaces and QA is visibly labeled.

Current proof: Build configuration rejects hosted-fictional preview in QA/prod; inspected app.config.ts gives distinct bundle/package suffix, name and scheme; controller/storage namespace logic is environment-scoped source.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/hosted-preview.test.ts::the hosted preview build flag is local-only and cannot alter QA or production account behavior` — file SHA `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb`, line 93; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “both run on one phone ... distinct identities/local namespaces and QA visibly labeled”: no co-installed QA+prod native execution or same-phone namespace/UI observation. Build-source declarations and dev infrastructure templates are not this phone scenario.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 995e54f5732bd01381614c3e299d0bccec5623f34ab7d012806d227f5490740b. Actual current source and raw evidence supply this disposition.

## OTGD-020-AND-ENV-001-02 — PASS

Cloud service receives local-only configuration — - **GIVEN** APP_ENV=prod - **WHEN** local authentication or an emulator endpoint is configured - **THEN** startup fails before accepting requests.

Current proof: Related constructor tests reject invalid cloud-runtime settings; mobile build rejects fictional hosted preview in prod. Inspected API config.py:146-177 rejects cloud emulator endpoints/non-HTTPS local identity before FastAPI settings construction. Actual API production selector OTGD_ENVIRONMENT=prod (the backend variable injected by the production platform; canonical APP_ENV describes the production build/deployment state) rejects local identity and emulator endpoints before listening. Literal APP_ENV-only is not claimed as an API selector.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_serverless_lifecycle.py::test_serverless_configuration_requires_real_control_resume_and_queue_bounds` — file SHA `5e1ee8d32ff49f6b1182028681e0f27a5c3315f87b3eda45a8b427722cc059bd`, line 404; 5 current observation(s).
- `apps/mobile/tests/hosted-preview.test.ts::the hosted preview build flag is local-only and cannot alter QA or production account behavior` — file SHA `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb`, line 93; 1 current observation(s).
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/supplemental/operations/probe.py::probe[prod-emulator-rejected]` — file SHA `3dfdac3de484521910f34c0fee5233cd68ca2a1ee8d0b4284135e145f069a42e`, line 33; 1 current observation(s).
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/supplemental/operations/probe.py::probe[prod-local-identity-rejected]` — file SHA `3dfdac3de484521910f34c0fee5233cd68ca2a1ee8d0b4284135e145f069a42e`, line 33; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/supplemental/operations/prod-emulator-rejected.json` — SHA256 `1a634e7b681d0cfc123085a6e7bf02df6e0ee7ae6e7345f4c482ae0eadb602c6`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/supplemental/operations/prod-local-identity-rejected.json` — SHA256 `52c4105f7e839121b2b77c14663335f434fd9c1c3969120ecd66a687a70c9b9d`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Isolated actual process and real refused local database connection; no shared service outage, public cloud deployment or participant/scientific approval. Driver initial /v1/me404 harness failure is historical and preserved; final actual protected /v1/me/profile rerun passed.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA d2b7105c099fcc64a23b44f32dbf382730dfd3c6874ca6f314038833be5fdd3a. Actual current source and raw evidence supply this disposition.

## OTGD-020-AND-ENV-002-01 — PARTIAL

Phone launches offline — - **GIVEN** a usable encrypted store - **WHEN** the configuration request times out - **THEN** permitted local functions open with an offline state and no fabricated server result.

Current proof: Offline fetch fixture still opens local guest notice/home, saves frozen measurements with empty upload queue and blocks guest upload.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “usable encrypted store ... configuration request times out ... offline state and no fabricated server result”: controller test uses runtime memory store and immediate thrown fetch, not bounded timeout with retained encrypted data; it does not assert offline flag or absence of fabricated SERVER result. Guest fictional simulation is explicitly separate.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 340ff74fbff4b90e7b05a7c3af9c77fb44457e5ccf20cf37b708b986b06323cf. Actual current source and raw evidence supply this disposition.

## OTGD-020-AND-ENV-002-02 — PARTIAL

Store cannot be decrypted — - **GIVEN** a missing or invalid local key - **WHEN** startup opens storage - **THEN** the app reports a storage recovery/reset choice and does not fall back to plaintext storage.

Current proof: Native-storage boundary rejects unavailable key storage with no-plaintext-fallback error, missing cipher and missing backup exclusion. Expo native modules are doubles.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/native-storage.test.ts::native account storage fails closed when key storage, cipher support or backup exclusion is unavailable` — file SHA `52005beea373ed0bf603dffffc6a20cb2e8fd07371bf5cb0712afa4b3bf208df`, line 199; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “missing/invalid key ... app reports recovery/reset choice”: storage-unit rejection does not exercise a retained encrypted database/key-loss or controller/UI recovery/reset affordance; actual SQLCipher failure and native UI remain unexecuted.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 40a1970bd8ba7c8cc8d0ab477e5de48d0aff3957c6384a97c91740af791e67ad. Actual current source and raw evidence supply this disposition.

## OTGD-020-AND-ENV-003-01 — PASS

Local prerequisites are present — - **GIVEN** Docker and the pinned community preset, or Docker and an authorized activation token for the explicitly selected licensed preset - **WHEN** the documented local startup command runs - **THEN** resources initialize idempotently and a synthetic session reaches a persisted result through the API/worker path.

Current proof: Health software requires all five long services plus two successful initializers and inspects only safe Docker fields. CI context records actual dependency build/start and repeated bootstrap steps successful before later cancellation. Actual ordinary production web bundle at mobile/desktop: hosted PKCE local issuer; no cloud session until explicit upload; accepted finalize reply dropped then exact key/receipt replay; persisted worker measurement result; reload memory boundary; exact selected worker ZIP hashes; foreign denial; governed consent/withdrawal; accepted all-data deletion reply dropped and exact pending intent visible; actual completion and retired-generation denial; interactive reauthentication and generation acknowledgment preserve identity and leave empty inventory. Current exact-tree CI/local startup and repeat resource bootstrap complete; actual production web upload/result and worker interruption reports establish persisted synthetic API/worker results. Both full worker reports have92 exact current source hashes,5 export and2 result recoveries, unchanged120-second leases/visibility and5claim/receive budgets. Community LocalStack token-free preset is preserved.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_canonical_health.py::test_all_five_long_services_and_two_successful_initializers_required` — file SHA `5ef6623480bf0056aef21d0a97ff2e90c0be15c44003b12bebb6f4d308bc828e`, line 22; 1 current observation(s).
- `infra/test/test_canonical_health.py::test_filtered_inspect_never_reads_environment_or_health_log` — file SHA `5ef6623480bf0056aef21d0a97ff2e90c0be15c44003b12bebb6f4d308bc828e`, line 35; 1 current observation(s).
- `apps/mobile/e2e/authenticated-live.spec.ts::ordinary web completes owned PKCE, explicit upload, worker export, lost-ack recovery, reload and privacy boundaries` — file SHA `3ec7e636797c30677205c3bde7e9ca64fe919b4c3513b1cf47453d52b87a468d`, line 220; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12597206063/authenticated-live.xml` — SHA256 `9128fd401f1a08b5023fd8cb6faa9ce340538cdeaf65d0addef0d8fc14d2473c`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/authenticated-live.xml` — SHA256 `d077dac5e8315553d8b2e4a574bca04ba3639fc7d2905c0aaec076f7974c8392`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Actual Docker/PostgreSQL/versioned S3/SQS/local-issuer fixtures are fictional. Not public Cognito, native encrypted persistence, physical capture or study approval. Awaiting-generation-ack current-generation write refusal is a separately narrowed residual.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4cc5b13a2be0411e9ad1814edacc9278a5da4c48e99b13ad54126cd9547d64ed. Actual current source and raw evidence supply this disposition.

## OTGD-020-AND-ENV-003-02 — PARTIAL

LocalStack prerequisite is absent — - **GIVEN** no Docker daemon, or the explicitly selected licensed preset without its required activation token - **WHEN** local integration is requested - **THEN** the command fails with a clear prerequisite message and no test report calls a mock execution LocalStack validation.

Current proof: Related health CLI rejects Docker inspection failure and reports safe nonzero prerequisite code. local-platform.py source rejects missing Docker; licensed Compose explicitly requires token.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_canonical_health.py::test_docker_failure_missing_inventory_and_invalid_json_are_explicit_failures` — file SHA `5ef6623480bf0056aef21d0a97ff2e90c0be15c44003b12bebb6f4d308bc828e`, line 46; 1 current observation(s).
- `infra/test/test_canonical_health.py::test_cli_preserves_failure_exit_without_vendor_secret_output` — file SHA `5ef6623480bf0056aef21d0a97ff2e90c0be15c44003b12bebb6f4d308bc828e`, line 53; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- An actual missing-Docker prerequisite and an explicitly selected licensed LocalStack mode without its authorized token must produce the documented clear refusal and no mocked-validation claim. Current community mode is qualified and token-free; no community activation token is required. These missing-prerequisite startup scenarios are not directly executed.

Prerequisite/evidence type: software_startup_scenario_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA 5128530fdaeaa0149015f9f33b0fcd9ef7a51fad3c1e8be4d56d9927713b6e51. Actual current source and raw evidence supply this disposition.

## OTGD-020-AND-ENV-004-01 — PASS

Synthesized production stack — - **GIVEN** complete deployment inputs - **WHEN** infrastructure is synthesized and checked - **THEN** required encryption, private database/task placement, TLS listener, production capacity, and scoped resource access appear in the template.

Current proof: Inspected real CDK test asserts encrypted retained buckets, private encrypted MultiAZ prod RDS, private ECS networking, TLS listener and scoped IAM. Old contracts/synthesis log confirms a nonzero infra-node.xml was validated. Current actual unfiltered Node/CDK test prod: synthesized network, identity, storage and queue boundaries asserts active DesiredCount>=2 and scaling MinCapacity>=2 alongside encryption/private placement/TLS/scoped access. Six actual named JUnit methods passed with real installed CDK dependencies; source fingerprint unchanged.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/platform.test.ts::prod: synthesized network, identity, storage and queue boundaries` — file SHA `0e949874e8b8c86b6f4ae1075222dc65383648b0b66dcc14b20669eedc92878c`, line 17; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-local/infra-node.xml` — SHA256 `a5b74683ea4cfaacaf3b37d820722d94f82afbad0394396e464130a20bc7b5b5`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 98392e2adee4f06d04a1d8557a84c4fe4091a804096720b16ff0836b62e0d4bc. Actual current source and raw evidence supply this disposition.

## OTGD-020-AND-ENV-004-02 — PASS

Secret is omitted — - **GIVEN** a required database or identity setting is unavailable - **WHEN** the service starts - **THEN** readiness fails without logging the secret or accepting unauthenticated fallback traffic.

Current proof: Secret-provider malformed/foreign/wrong-user/bad-key/provider failures publish no partial passwords/tombstone key and expose only fixed safe error; loaded-password validation error suppresses private context. Actual missing required database-secret reference fails initialization/readiness before listen; no secret sentinel or unauthenticated fallback accepted. The canonical Then requires readiness failure, not a running HTTP503 server or all omitted-setting permutations.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_serverless_lifecycle.py::test_failed_secret_initialization_does_not_publish_partial_password_or_secret_error` — file SHA `5e1ee8d32ff49f6b1182028681e0f27a5c3315f87b3eda45a8b427722cc059bd`, line 202; 25 current observation(s).
- `services/api/tests/test_serverless_lifecycle.py::test_serverless_settings_validation_cannot_dump_loaded_password_values` — file SHA `5e1ee8d32ff49f6b1182028681e0f27a5c3315f87b3eda45a8b427722cc059bd`, line 425; 5 current observation(s).
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/supplemental/operations/probe.py::probe[missing-database-secret-rejected]` — file SHA `3dfdac3de484521910f34c0fee5233cd68ca2a1ee8d0b4284135e145f069a42e`, line 33; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/supplemental/operations/missing-database-secret-rejected.json` — SHA256 `06caff405f180fb66955542e9c177b44016ced9638829da0f5dbb27466692f58`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Isolated actual process and real refused local database connection; no shared service outage, public cloud deployment or participant/scientific approval. Driver initial /v1/me404 harness failure is historical and preserved; final actual protected /v1/me/profile rerun passed.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA e60823f450165b2156f7eeac1d0f10939020977d739335799348f8e9200e2efa. Actual current source and raw evidence supply this disposition.

## OTGD-020-AND-ENV-005-01 — PARTIAL

QA release passes its checks — - **GIVEN** a tested image digest and compatible schema - **WHEN** promoted to production - **THEN** production references that digest and records the migration/release evidence.

Current proof: Real Ed25519 production record binds exact QA image/source/provenance and QA envelope; maintenance validator accepts matching zero-exit/source/image/task receipt and rejects mutations.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_provenance.py::test_production_activation_rechecks_signed_git_and_exact_qa_envelopes` — file SHA `996ead63b1f3ae3999aa31d81e3de893bbc50b62bfaac6e2a69f88a968d5f6a1`, line 330; 1 current observation(s).
- `infra/test/test_maintenance.py::test_exact_task_definition_container_command_and_receipt_required` — file SHA `f7222dcd026bcbe70c73279fbb8c75a65bef166e311e93e0729f3d3570b356bf`, line 39; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “promoted to production ... records migration/release evidence”: mocked GitHub/ECR/ECS and generated keys do not execute QA-to-prod promotion or actual compatible-schema migration; external deployment remains unexecuted and outside draft-PR-only action scope.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA d576d554dfe9e5e6e91e3214d219b3acd14d01b361acb53e437d1d89e1908753. Actual current source and raw evidence supply this disposition.

## OTGD-020-AND-ENV-005-02 — PARTIAL

Migration fails — - **GIVEN** a nonzero migration exit - **WHEN** deployment automation evaluates the gate - **THEN** service rollout stops and the previous deployment remains the rollback target.

Current proof: Injected migration failure stops orchestration before activation/web build/publication; actual validator rejects modeled migration task exit1.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_failed_migration_never_activates_or_uploads_web` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 506; 1 current observation(s).
- `infra/test/test_maintenance.py::test_exact_task_definition_container_command_and_receipt_required` — file SHA `f7222dcd026bcbe70c73279fbb8c75a65bef166e311e93e0729f3d3570b356bf`, line 39; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “previous deployment remains rollback target”: no failed-migration test retains/asserts exact prior release/task-definition rollback reference after stopping new rollout. Template circuit-breaker settings or journal rollback_executed=false are not that retained-target assertion.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0a2c966bb6433486fb3cbefd2892b8ebd9a669f149ec8fe51831b9a8c9302346. Actual current source and raw evidence supply this disposition.

## OTGD-020-AND-ENV-006-01 — PASS

Database is unavailable — - **GIVEN** a live API process without a usable database - **WHEN** health is checked - **THEN** liveness may pass while readiness returns 503 and traffic is not represented as healthy.

Current proof: Liveness middleware path skips database/lease; unrelated metadata lease failure returns503 without secret; healthy API readiness baseline returns ready. Inspected /health/live is DB-free, readiness SELECT1 and SQLAlchemyError handler503 exist. One actual API PID with real unavailable loopback database returns live200/ready503 twice, safe SERVICE_UNAVAILABLE and401 for missing/invalid protected-route auth; no secret logged.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_serverless_lifecycle.py::test_legacy_mode_lwa_live_probe_and_non_http_do_not_open_database_or_acquire` — file SHA `5e1ee8d32ff49f6b1182028681e0f27a5c3315f87b3eda45a8b427722cc059bd`, line 111; 15 current observation(s).
- `services/api/tests/test_serverless_lifecycle.py::test_lease_acquisition_failure_denies_before_app_and_publishes_no_provider_detail` — file SHA `5e1ee8d32ff49f6b1182028681e0f27a5c3315f87b3eda45a8b427722cc059bd`, line 76; 5 current observation(s).
- `services/api/tests/test_api.py::test_health_and_compile_time_inference` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 83; 5 current observation(s).
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/supplemental/operations/probe.py::probe[unavailable-database-live-readiness]` — file SHA `3dfdac3de484521910f34c0fee5233cd68ca2a1ee8d0b4284135e145f069a42e`, line 33; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/supplemental/operations/unavailable-database-live-readiness.json` — SHA256 `74b1bafb8c26ce65eb0491dcd1611aa9ffd68c178aa96bc43bc77ef1818381a7`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Isolated actual process and real refused local database connection; no shared service outage, public cloud deployment or participant/scientific approval. Driver initial /v1/me404 harness failure is historical and preserved; final actual protected /v1/me/profile rerun passed.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 42d0b183cdb6b62188e02c02595a942d015947a905290d7a0f49833759735bc0. Actual current source and raw evidence supply this disposition.

## OTGD-020-AND-ENV-006-02 — PARTIAL

Backup contains subsequently deleted data — - **GIVEN** a restore from an older backup - **WHEN** the restore runbook is executed - **THEN** deletion tombstones are reapplied before access is reopened and the drill records whether RPO/RTO objectives were achieved.

Current proof: SQLite barrier unit test replays accepted/completed deletion, restores original owner/generation barrier, disables old registry trust and scrubs restored health rows.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_recovery.py::test_backup_predating_account_restores_original_id_and_generation` — file SHA `598881481a5ab8561446d64b3d949c8f883f52ee4d1d9cc3120a909a383c737c`, line 49; 1 current observation(s).
- `infra/test/test_recovery.py::test_completed_barrier_scrubs_restored_health_data` — file SHA `598881481a5ab8561446d64b3d949c8f883f52ee4d1d9cc3120a909a383c737c`, line 69; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “restore runbook ... tombstones before reopening ... drill records RPO/RTO”: no actual older-backup restore/independent retained journal/API reopening drill or measured RPO<=24h/RTO<=4h result. SQLite plan application cannot establish these operational objectives.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA ef9dde959b9386ae43a39f9d619cd0214887fbbf4ba8738e98e25df662213376. Actual current source and raw evidence supply this disposition.

## OTGD-020-AND-ENV-007-01 — PARTIAL

iOS source exists on a Linux runner — - **GIVEN** no Xcode/macOS build toolchain - **WHEN** delivery status is generated - **THEN** iOS native compilation is recorded as unexecuted rather than inferred from a JavaScript bundle.

Current proof: Immutable OTGD020 test-results explicitly says no runtime/browser/native/firmware execution claimed; verification-plan C-IOS requires macOS26/Xcode26.4.1 and says Linux cannot substitute. Current oldCI native macOS evidence remains separate from Linux JavaScript execution.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- “Linux without toolchain ... delivery status generated ... iOS compilation recorded unexecuted”: truthful static planning/report statements exist but no toolchain-absent delivery-status generation execution is source-bound to this case. No iOS compile is inferred from JS; no missing automated generator is invented.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8ea4fc509bc6f7042673faecdbdfe80c6b0cf23f12a178c857a773ee340a1360. Actual current source and raw evidence supply this disposition.

## OTGD-020-AND-ENV-007-02 — PASS

Infrastructure synthesis succeeds without AWS credentials — - **GIVEN** a synthesized template but no deployment - **WHEN** the release report is written - **THEN** it states synthesis passed and QA/prod deployment remains unexecuted.

Current proof: Immutable adversarial-review report explicitly labels historical actual CDK fixture5passed as synthesis, not AWS deployment; verification-plan says cloud external actions unexecuted/not authorized and source workflow is not execution proof. Current prod/QA synthesis actual named XML passed. This generated evidence report explicitly records QA/prod AWS deployment unexecuted; local Docker/current CI are not a deployed-cloud claim.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/platform.test.ts::prod: synthesized network, identity, storage and queue boundaries` — file SHA `0e949874e8b8c86b6f4ae1075222dc65383648b0b66dcc14b20669eedc92878c`, line 17; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-local/infra-node.xml` — SHA256 `a5b74683ea4cfaacaf3b37d820722d94f82afbad0394396e464130a20bc7b5b5`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 26970cde0e1f3719b88a851e063b8d37ffccc4c83224478041223f516739b102. Actual current source and raw evidence supply this disposition.

