# OTGD-015 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/cloud-deployment-customer-access/specs/cloud-release-orchestration/spec.md`; SHA256 `32e918e2908b70dbf00f7c9533aa462402b71ffc5c5ce9b8f4da499783cc3bc6`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-015/test-plan.md`. External review artifact only; PM controls import.

All 21 stable cases / 10 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`
- `uv run --project services/api python scripts/ci_gate.py infra-unit`
- `node --import tsx --test --test-reporter=junit test/*.test.ts (cwd: infra)`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-015-CLOUD-DEP-001-01 | QA plan is requested — - **GIVEN** a concrete validated QA configuration - **WHEN** qa.py --plan executes - **THEN** it lists infrastructure/code/maintenance/web stages and reports deployment_executed=false. | PASS |
| OTGD-015-CLOUD-DEP-001-02 | Production wrapper receives QA configuration — - **GIVEN** an environment mismatch - **WHEN** the wrapper starts - **THEN** it fails before AWS access or mutation. | PASS |
| OTGD-015-CLOUD-DEP-002-01 | Every required exact-revision gate passes — - **GIVEN** an eligible main/merge-group run and independently trusted signature - **WHEN** release operations execute - **THEN** source/run/attempt/job/image bindings are verified and retained. | PARTIAL |
| OTGD-015-CLOUD-DEP-002-02 | A prior or cancelled run is supplied — - **GIVEN** stale or incomplete evidence - **WHEN** admission executes - **THEN** the operation fails before release authorization. | PASS |
| OTGD-015-CLOUD-DEP-003-01 | Actual approved inputs are present — - **GIVEN** the configured credential chain and resource authority - **WHEN** one environment command executes - **THEN** its actual account/region is verified before infrastructure changes. | PARTIAL |
| OTGD-015-CLOUD-DEP-003-02 | AWS credentials point to another account — - **GIVEN** an STS mismatch - **WHEN** preflight executes - **THEN** no target deployment continues. | NOT_RUN |
| OTGD-015-CLOUD-DEP-003-03 | Local emulation endpoint settings are inherited — - **GIVEN** global, service-specific or profile endpoint overrides - **WHEN** cloud identity or mutation clients are constructed - **THEN** their endpoints resolve to AWS and explicit endpoint overrides are rejected. | PASS |
| OTGD-015-CLOUD-DEP-004-01 | First empty environment is established — - **GIVEN** explicit establish-new and no admitted data - **WHEN** bootstrap/migration succeed - **THEN** actual receipts qualify for the later activation gate. | PARTIAL |
| OTGD-015-CLOUD-DEP-004-02 | Migration or fresh admission verification fails — - **GIVEN** failed maintenance, absent authority or a stale/mismatching admission receipt - **WHEN** deployment reaches the failure - **THEN** activation and web publication do not execute and no success receipt is fabricated. | PASS |
| OTGD-015-CLOUD-DEP-005-01 | Worker dependencies make useful progress — - **GIVEN** dispatcher/cleanup/both consumers qualify - **WHEN** ECS reports the worker container HEALTHY - **THEN** publication may proceed after the remaining gates. | PARTIAL |
| OTGD-015-CLOUD-DEP-005-02 | A worker process runs without qualifying progress — - **GIVEN** UNKNOWN/unhealthy worker status - **WHEN** the bounded health deadline expires - **THEN** public enablement fails and is not called successful deployment. | PARTIAL |
| OTGD-015-CLOUD-DEP-006-01 | Approved QA is promoted — - **GIVEN** source service/web records and actual protected QA evidence - **WHEN** the authority signs and production admission runs - **THEN** production preserves the image/source and binds its separately configured web artifact to the approved QA envelope. | PARTIAL |
| OTGD-015-CLOUD-DEP-006-02 | Web evidence refers to another artifact — - **GIVEN** a foreign/missing web digest or expired QA approval - **WHEN** production starts - **THEN** it fails before target deployment. | PARTIAL |
| OTGD-015-CLOUD-DEP-007-01 | A valid public subdomain is registered — - **GIVEN** a deployed matching distribution and issued TLS - **WHEN** apply is explicitly requested - **THEN** one CNAME targets that distribution and its actual change is awaited for at most ten minutes. | PARTIAL |
| OTGD-015-CLOUD-DEP-007-02 | Caller supplies apex, foreign zone or target — - **GIVEN** a mismatching zone/alias/certificate/record - **WHEN** validation executes - **THEN** no DNS mutation occurs. | PASS |
| OTGD-015-CLOUD-DEP-008-01 | An operator repeats deployment — - **GIVEN** prior reviewed records - **WHEN** another invocation starts - **THEN** a separate attempt retains earlier evidence and same-prefix object conflicts fail closed. | PARTIAL |
| OTGD-015-CLOUD-DEP-008-02 | Public access or invalidation fails — - **GIVEN** incomplete delivery - **WHEN** the bounded operation fails - **THEN** no verified-access receipt is written and cloud acceptance remains unresolved. | PARTIAL |
| OTGD-015-CLOUD-DEP-009-01 | An authorized operator validates registry evidence — - **GIVEN** an approved private operator host with the actual named role and protected database credentials - **WHEN** the typed CLI validates the corresponding command - **THEN** STS/IAM identity and database authority are verified independently of participant API access. | PARTIAL |
| OTGD-015-CLOUD-DEP-009-02 | A deployed application task attempts an approval — - **GIVEN** a runtime database/task identity - **WHEN** it attempts to administer or impersonate a registry operator - **THEN** runtime write/trust permissions do not authorize the operation and no approval is invented. | PARTIAL |
| OTGD-015-CLOUD-DEP-010-01 | Maintenance completes with current independent authority — - **GIVEN** migration and required recovery have completed with services stopped - **WHEN** the exact pinned admission task verifies journal/control versions and database barriers - **THEN** its fresh actual ECS receipt may qualify activation alongside the other release gates. | PARTIAL |
| OTGD-015-CLOUD-DEP-010-02 | Admission proof is stale or uses a no-op command — - **GIVEN** stale completion, mismatching bindings or a command that only mentions the module - **WHEN** activation verifies the receipt against ECS - **THEN** services are not activated using that evidence. | PASS |
