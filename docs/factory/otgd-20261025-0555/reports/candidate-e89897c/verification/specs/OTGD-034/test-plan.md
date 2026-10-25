# OTGD-034 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/production-mobile-platform/specs/android-results/spec.md`; SHA256 `dadd53ea7fd8027bb76d17c26e51d4910cc3c8763bfd8a838434fbf8112397ba`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-034/test-plan.md`. External review artifact only; PM controls import.

All 14 stable cases / 7 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-034-AND-RES-001-01 | Completed offline measurement check — - **GIVEN** a locally finalized check with no server result - **WHEN** the result screen opens - **THEN** it shows the local measurement record and **Not synced**, with no claim that cloud analysis finished. | PARTIAL |
| OTGD-034-AND-RES-001-02 | Pending server computation — - **GIVEN** GET result returns HTTP 202 - **WHEN** polling completes that request - **THEN** the app keeps **Analysis pending** and offers navigation without inventing a terminal result. | NOT_RUN |
| OTGD-034-AND-RES-002-01 | Correctly linked measurement result — - **GIVEN** the expected session and frozen digest - **WHEN** a schema-valid measurement_only response arrives with matching references - **THEN** it is saved once and displayed for that check. | PARTIAL |
| OTGD-034-AND-RES-002-02 | Stale response after another check — - **GIVEN** a response references an earlier session - **WHEN** the current check screen receives it - **THEN** the response cannot replace the current check's result and the mismatch is recorded without raw health payloads. | PARTIAL |
| OTGD-034-AND-RES-003-01 | Demo completes all steps — - **GIVEN** every simulated channel contains a plausible value - **WHEN** the check is finalized - **THEN** its result remains measurement_only with null probability and a demo badge. | PASS |
| OTGD-034-AND-RES-003-02 | Client requests research by changing a field — - **GIVEN** an otherwise valid-shaped research_estimate or an operator record claiming an active model - **WHEN** any current result path evaluates it - **THEN** the service executes no model and the app rejects the unsupported estimate without displaying its probability. | PASS |
| OTGD-034-AND-RES-004-01 | Below quantification — - **GIVEN** THC_COOH has qualifier below_loq and a stated LOQ - **WHEN** its card renders - **THEN** it shows below-quantification wording and the limit, with no exact numeric concentration or inferred detection claim. | PARTIAL |
| OTGD-034-AND-RES-004-02 | Unrun channel — - **GIVEN** OH11_THC is not_measured - **WHEN** measurements are expanded - **THEN** the app shows **Not measured**, not **Negative**. | PASS |
| OTGD-034-AND-RES-005-01 | Delayed laboratory result — - **GIVEN** analysis finishes the following day - **WHEN** the result arrives - **THEN** the original collection date remains the check's date and the later analysis time is visible. | PARTIAL |
| OTGD-034-AND-RES-005-02 | Linked reanalysis — - **GIVEN** a permitted newer result replaces an earlier result - **WHEN** history is opened - **THEN** both result identities remain reconstructable and the current display identifies the newer result's version. | PARTIAL |
| OTGD-034-AND-RES-006-01 | Interrupted reaction task — - **GIVEN** a required task is invalid due to backgrounding - **WHEN** the completion summary opens - **THEN** it names the interrupted task and, if already finalized, offers Start replacement check with a new UUID/time and no carried-forward physical acquisitions; the original result/hash remain unchanged. | PARTIAL |
| OTGD-034-AND-RES-006-02 | Unknown server reason — - **GIVEN** a newer service returns an unknown reason code - **WHEN** the app displays the result - **THEN** it shows a generic unavailable explanation and diagnostic request ID without silently treating the result as valid. | NOT_RUN |
| OTGD-034-AND-RES-007-01 | Temporary server outage — - **GIVEN** the result endpoint returns 503 - **WHEN** automatic retries exhaust the configured budget - **THEN** the record remains pending and a retry action appears; the local check is preserved. | NOT_RUN |
| OTGD-034-AND-RES-007-02 | Account changes during polling — - **GIVEN** an outstanding result request for account A - **WHEN** the app signs into account B - **THEN** A's request is canceled or ignored and its result never enters B's visible state. | PARTIAL |
