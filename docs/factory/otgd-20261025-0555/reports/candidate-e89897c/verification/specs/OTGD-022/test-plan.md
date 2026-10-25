# OTGD-022 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/production-mobile-platform/specs/android-data-export/spec.md`; SHA256 `2e02ae2e4ea75c4e789b29399dee2b6e4206f12ecb81630b04ca54c4a6e1ef30`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-022/test-plan.md`. External review artifact only; PM controls import.

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
| OTGD-022-AND-EXP-001-01 | Local single-check export — - **GIVEN** History selects one check while unrelated records also exist - **WHEN** the customer confirms This device for that exact selection - **THEN** only the selected check, its frozen profile/context, attempts, alcohol, and linked results are exported locally, with no cloud mutation or unrelated profile revision. | PARTIAL |
| OTGD-022-AND-EXP-001-02 | Confirmation is canceled — - **GIVEN** the export summary sheet - **WHEN** the customer cancels - **THEN** no job/file/share action is created. | NOT_RUN |
| OTGD-022-AND-EXP-002-01 | Own synced records — - **GIVEN** a signed-in owner selecting their records - **WHEN** the export completes - **THEN** the archive contains only the authorized selected records. | PASS |
| OTGD-022-AND-EXP-002-02 | Another user's session is injected — - **GIVEN** an export selection containing a foreign UUID - **WHEN** the request is validated - **THEN** it is rejected without including or disclosing the foreign record. | NOT_RUN |
| OTGD-022-AND-EXP-003-01 | Censored saliva result — - **GIVEN** a below_loq measurement - **WHEN** exported - **THEN** value remains null and the qualifier/limit/original report remain available. | PASS |
| OTGD-022-AND-EXP-003-02 | Historical reanalysis — - **GIVEN** multiple linked results for one session - **WHEN** selected for export - **THEN** their immutable IDs, versions, and replacement relationship are preserved. | PASS |
| OTGD-022-AND-EXP-004-01 | Default export — - **GIVEN** an ordinary export request - **WHEN** the job is assembled - **THEN** raw eye/ECG files are excluded and the manifest records the exclusion. | PASS |
| OTGD-022-AND-EXP-004-02 | Raw consent is revoked during processing — - **GIVEN** raw inclusion was initially allowed - **WHEN** permission is revoked before delivery - **THEN** the gateway blocks a subsequently initiated download and reports the changed scope or failed job; it makes no promise to recall bytes already authorized/delivered. | PASS |
| OTGD-022-AND-EXP-005-01 | Expired export is reopened — - **GIVEN** an export past expires_at - **WHEN** the customer opens it - **THEN** no new valid ticket is issued and a new export action is offered. | PARTIAL |
| OTGD-022-AND-EXP-005-02 | Share sheet is canceled — - **GIVEN** a downloaded temporary export - **WHEN** the share sheet returns without sharing - **THEN** the app schedules immediate cleanup and does not claim it sent the file anywhere. | NOT_RUN |
| OTGD-022-AND-EXP-006-01 | Export request response is lost — - **GIVEN** a created cloud job - **WHEN** the same request is retried - **THEN** the same job ID is returned. | PASS |
| OTGD-022-AND-EXP-006-02 | Artifact verification fails — - **GIVEN** a selected permitted artifact whose bytes fail the stored hash - **WHEN** the worker assembles the export - **THEN** the job fails with a safe reason and no complete-download state is exposed. | PARTIAL |
| OTGD-022-AND-EXP-007-01 | Profile text resembles a path — - **GIVEN** text containing ../ or absolute-path characters in user data - **WHEN** an export is generated - **THEN** it remains JSON content and cannot control an archive entry name. | NOT_RUN |
| OTGD-022-AND-EXP-007-02 | Export exceeds its configured bound — - **GIVEN** selected data larger than the supported single-export limit - **WHEN** the job validates size - **THEN** it reports an explicit size failure and never silently omits records or invents an unimplemented partitioning workflow. | PARTIAL |
