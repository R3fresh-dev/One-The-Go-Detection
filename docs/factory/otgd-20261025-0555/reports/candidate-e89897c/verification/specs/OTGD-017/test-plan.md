# OTGD-017 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/optional-raw-recording-lifecycle/specs/fictional-hosted-preview/spec.md`; SHA256 `ee9d68e204d40b0500732c19096ce4fc4a362892d09106034678baacde4e961d`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-017/test-plan.md`. External review artifact only; PM controls import.

All 6 stable cases / 3 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-017-AND-PREV-001-01 | Production enables the preview flag — - **GIVEN** APP_ENV=prod - **WHEN** the hosted preview flag is true - **THEN** configuration fails before building application code. | PASS |
| OTGD-017-AND-PREV-001-02 | An isolated local preview is packaged — - **GIVEN** APP_ENV=local and the matching compiled public environment - **WHEN** the hosted flag is accepted and the reviewed workflow packages the app - **THEN** its bundle and platform metadata identify fictional hosted mode and account and real acquisition services remain disabled. | PARTIAL |
| OTGD-017-AND-PREV-002-01 | A customer saves a browser example — - **GIVEN** the standalone fictional preview - **WHEN** the customer acknowledges the notice, confirms context and saves a check - **THEN** the UI shows a measurement-only fictional record with no account, sensor or upload calls. | PASS |
| OTGD-017-AND-PREV-002-02 | A credential or hardware path is invoked directly — - **GIVEN** the standalone fictional preview - **WHEN** a caller attempts sign-in, credential recovery, API download, Bluetooth discovery or native reaction acquisition - **THEN** the request is refused before network or hardware access and no fictional record is promoted to a measurement. | PASS |
| OTGD-017-AND-PREV-003-01 | The browser reloads after saving an example — - **GIVEN** a fictional saved browser check - **WHEN** the page reloads - **THEN** its records and acknowledgment disappear and the first-use fictional flow returns. | PASS |
| OTGD-017-AND-PREV-003-02 | A guest example is selected for account upload — - **GIVEN** a saved check in the isolated fictional guest namespace - **WHEN** a caller attempts account migration, import or upload - **THEN** the operation is refused and the account namespace receives no guest data. | PARTIAL |
