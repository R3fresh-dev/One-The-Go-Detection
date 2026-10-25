# OTGD-020 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/production-mobile-platform/specs/android-app-environment/spec.md`; SHA256 `6cef683b7ac1b04bdf104e0b87aa36badf61e905580d32223c05a39ce8efac35`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-020/test-plan.md`. External review artifact only; PM controls import.

All 14 stable cases / 7 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`
- `python scripts/ci_gate.py localstack-api`
- `uv run --project services/api python scripts/ci_gate.py infra-unit`
- `node --import tsx --test --test-reporter=junit test/*.test.ts (cwd: infra)`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-020-AND-ENV-001-01 | QA and production are installed together — - **GIVEN** separate configured builds - **WHEN** both run on one phone - **THEN** they have distinct app identities and local namespaces and QA is visibly labeled. | PARTIAL |
| OTGD-020-AND-ENV-001-02 | Cloud service receives local-only configuration — - **GIVEN** APP_ENV=prod - **WHEN** local authentication or an emulator endpoint is configured - **THEN** startup fails before accepting requests. | PASS |
| OTGD-020-AND-ENV-002-01 | Phone launches offline — - **GIVEN** a usable encrypted store - **WHEN** the configuration request times out - **THEN** permitted local functions open with an offline state and no fabricated server result. | PARTIAL |
| OTGD-020-AND-ENV-002-02 | Store cannot be decrypted — - **GIVEN** a missing or invalid local key - **WHEN** startup opens storage - **THEN** the app reports a storage recovery/reset choice and does not fall back to plaintext storage. | PARTIAL |
| OTGD-020-AND-ENV-003-01 | Local prerequisites are present — - **GIVEN** Docker and the pinned community preset, or Docker and an authorized activation token for the explicitly selected licensed preset - **WHEN** the documented local startup command runs - **THEN** resources initialize idempotently and a synthetic session reaches a persisted result through the API/worker path. | PASS |
| OTGD-020-AND-ENV-003-02 | LocalStack prerequisite is absent — - **GIVEN** no Docker daemon, or the explicitly selected licensed preset without its required activation token - **WHEN** local integration is requested - **THEN** the command fails with a clear prerequisite message and no test report calls a mock execution LocalStack validation. | PARTIAL |
| OTGD-020-AND-ENV-004-01 | Synthesized production stack — - **GIVEN** complete deployment inputs - **WHEN** infrastructure is synthesized and checked - **THEN** required encryption, private database/task placement, TLS listener, production capacity, and scoped resource access appear in the template. | PASS |
| OTGD-020-AND-ENV-004-02 | Secret is omitted — - **GIVEN** a required database or identity setting is unavailable - **WHEN** the service starts - **THEN** readiness fails without logging the secret or accepting unauthenticated fallback traffic. | PASS |
| OTGD-020-AND-ENV-005-01 | QA release passes its checks — - **GIVEN** a tested image digest and compatible schema - **WHEN** promoted to production - **THEN** production references that digest and records the migration/release evidence. | PARTIAL |
| OTGD-020-AND-ENV-005-02 | Migration fails — - **GIVEN** a nonzero migration exit - **WHEN** deployment automation evaluates the gate - **THEN** service rollout stops and the previous deployment remains the rollback target. | PARTIAL |
| OTGD-020-AND-ENV-006-01 | Database is unavailable — - **GIVEN** a live API process without a usable database - **WHEN** health is checked - **THEN** liveness may pass while readiness returns 503 and traffic is not represented as healthy. | PASS |
| OTGD-020-AND-ENV-006-02 | Backup contains subsequently deleted data — - **GIVEN** a restore from an older backup - **WHEN** the restore runbook is executed - **THEN** deletion tombstones are reapplied before access is reopened and the drill records whether RPO/RTO objectives were achieved. | PARTIAL |
| OTGD-020-AND-ENV-007-01 | iOS source exists on a Linux runner — - **GIVEN** no Xcode/macOS build toolchain - **WHEN** delivery status is generated - **THEN** iOS native compilation is recorded as unexecuted rather than inferred from a JavaScript bundle. | PARTIAL |
| OTGD-020-AND-ENV-007-02 | Infrastructure synthesis succeeds without AWS credentials — - **GIVEN** a synthesized template but no deployment - **WHEN** the release report is written - **THEN** it states synthesis passed and QA/prod deployment remains unexecuted. | PASS |
