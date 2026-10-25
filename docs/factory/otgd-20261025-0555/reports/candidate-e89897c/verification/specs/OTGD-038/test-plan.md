# OTGD-038 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/production-mobile-platform/specs/android-study-enrollment/spec.md`; SHA256 `e0c8f1f81be37cbe775f274e6c2aa81d3f3eacc64da92f01bcdd1c31adfb9ee8`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-038/test-plan.md`. External review artifact only; PM controls import.

All 12 stable cases / 6 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-038-AND-STUDY-001-01 | Invited customer opens research access — - **GIVEN** one operator-provisioned invitation for the signed-in account - **WHEN** memberships are requested - **THEN** the app displays that invitation and its actual status. | PARTIAL |
| OTGD-038-AND-STUDY-001-02 | Customer guesses another study UUID — - **GIVEN** no membership in the requested study - **WHEN** its consent or capability route is requested - **THEN** access is refused without disclosing another participant's data. | PARTIAL |
| OTGD-038-AND-STUDY-002-01 | Current approved consent is accepted — - **GIVEN** an eligible active invitation and complete approved document - **WHEN** the participant explicitly accepts - **THEN** a durable receipt records the version, digest, authenticated subject, client time, and server receipt time. | PASS |
| OTGD-038-AND-STUDY-002-02 | Protocol changes while the page is open — - **GIVEN** the displayed consent version is no longer current - **WHEN** acceptance is submitted - **THEN** the server rejects the stale version and the app loads the updated document without transferring the old acceptance. | PARTIAL |
| OTGD-038-AND-STUDY-003-01 | Consent exists but optics remain unqualified — - **GIVEN** accepted consent and no approved optical configuration - **WHEN** the app requests eye capture - **THEN** passive guidance or an unavailable state is shown and no participant stimulus is emitted. | PARTIAL |
| OTGD-038-AND-STUDY-003-02 | Client edits capability JSON — - **GIVEN** a locally modified available flag - **WHEN** an upload or research request reaches the backend - **THEN** server-owned qualification and membership checks still prevent unauthorized operation. | PARTIAL |
| OTGD-038-AND-STUDY-004-01 | Cached scope cannot authorize offline capture — - **GIVEN** a cached available scope covering the device/configuration/channel - **WHEN** qualified capture is requested offline - **THEN** the app requires reconnection; local uncalibrated practice remains a separately labeled permitted path. | PARTIAL |
| OTGD-038-AND-STUDY-004-02 | Authorization expires offline — - **GIVEN** the phone was restarted or its wall clock was rolled back - **WHEN** new qualified capture is requested - **THEN** the app asks for reconnection and preserves existing records without acquiring under stale permission. | PARTIAL |
| OTGD-038-AND-STUDY-005-01 | Participant withdraws — - **GIVEN** active study access - **WHEN** the participant confirms withdrawal while offline - **THEN** local capture stops, the exact request is retained pending, and server completion is not claimed; later acceptance blocks verified uploads and returns the receipt. | PASS |
| OTGD-038-AND-STUDY-005-02 | Old upload ticket is used after withdrawal — - **GIVEN** an artifact ticket issued before withdrawal - **WHEN** upload completion is requested afterward - **THEN** authorization is rechecked and the object cannot become a verified research artifact through the stale ticket. | PARTIAL |
| OTGD-038-AND-STUDY-006-01 | Fresh production environment — - **GIVEN** no approved study records - **WHEN** research access opens - **THEN** no research capture or prediction is offered. | PARTIAL |
| OTGD-038-AND-STUDY-006-02 | Synthetic local fixture — - **GIVEN** a local development study fixture - **WHEN** it is displayed - **THEN** its synthetic identity and environment are explicit and its permissions cannot be reused in QA/prod. | PARTIAL |
