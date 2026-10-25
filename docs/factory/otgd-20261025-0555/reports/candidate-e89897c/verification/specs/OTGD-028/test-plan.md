# OTGD-028 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/production-mobile-platform/specs/android-history/spec.md`; SHA256 `eb9f89e04620ed296b248ce076e2c5447df6c5fb2c9da0eb9fa90725f2bd99a2`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-028/test-plan.md`. External review artifact only; PM controls import.

All 17 stable cases / 7 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-028-AND-HIST-001-01 | hist-demo-isolation — - **GIVEN** both demo and account checks exist on the device - **WHEN** account History opens - **THEN** only authorized account checks are listed and demo rows require an explicit switch. | PARTIAL |
| OTGD-028-AND-HIST-001-02 | hist-cross-account-id — - **GIVEN** an account receives a deep link to another account's session ID - **WHEN** detail is requested - **THEN** no snapshot, profile, existence-revealing title, or measurement is disclosed. | PARTIAL |
| OTGD-028-AND-HIST-002-01 | hist-new-record-between-pages — - **GIVEN** page one has loaded and a new check is finalized - **WHEN** page two is requested with the original cursor - **THEN** existing rows are neither duplicated nor skipped and the new check appears after refresh. | PASS |
| OTGD-028-AND-HIST-002-02 | hist-local-server-same-check — - **GIVEN** a local pending row is later returned by the server with the same UUID - **WHEN** reconciliation completes - **THEN** one row remains with updated sync status and unchanged source identity. | PARTIAL |
| OTGD-028-AND-HIST-003-01 | hist-below-loq — - **GIVEN** THC-COOH has qualifier below_loq with no quantified value - **WHEN** detail is opened - **THEN** it reads “Below quantification limit” with the reported limit when available, and no 0 ng/mL or inferred detection claim appears. | PARTIAL |
| OTGD-028-AND-HIST-003-02 | hist-delayed-laboratory-result — - **GIVEN** a sample collected Monday was analyzed Wednesday - **WHEN** its result is viewed Thursday - **THEN** all relevant dates are distinct and the laboratory result is not described as a Thursday physiological assessment. | PARTIAL |
| OTGD-028-AND-HIST-003-03 | hist-linked-research-estimate-is-still-unsupported — - **GIVEN** an authenticated account receives a schema-valid research_estimate with matching session and digest - **WHEN** History renders its detail - **THEN** the app shows the unsupported-result state without displaying probability, classification, or a research-estimate card. | PASS |
| OTGD-028-AND-HIST-004-01 | hist-profile-edited-later — - **GIVEN** a historical check contains profile revision A - **WHEN** current profile revision B is saved - **THEN** historical detail continues to display A's values and acquisition context. | PARTIAL |
| OTGD-028-AND-HIST-004-02 | hist-correction-linked — - **GIVEN** a reviewed correction supersedes a finalized record - **WHEN** either version is opened - **THEN** the original remains readable and a labeled link identifies the other version without overwriting it. | PARTIAL |
| OTGD-028-AND-HIST-005-01 | hist-offline-cached-detail — - **GIVEN** an encrypted cached snapshot and no network - **WHEN** its row is selected after local unlock - **THEN** the stored snapshot is displayed with its cached state and no remote result is invented. | PARTIAL |
| OTGD-028-AND-HIST-005-02 | hist-offline-uncached-detail — - **GIVEN** only a list summary is cached - **WHEN** the user opens detail offline - **THEN** the app explains unavailability and does not fill the screen from unrelated fixtures or another check. | NOT_RUN |
| OTGD-028-AND-HIST-005-03 | hist-signed-out-device-unlock-is-insufficient — - **GIVEN** A retained encrypted history when signing out - **WHEN** the user opens the app offline and passes device unlock - **THEN** A's history stays locked until the same issuer and subject reauthenticate; other workspaces remain separate. | BLOCKED |
| OTGD-028-AND-HIST-006-01 | hist-pending-filter — - **GIVEN** two locally queued checks and three synchronized checks - **WHEN** Pending sync is selected - **THEN** only the two queue-owned checks appear and the label states that this is this device's queue. | PARTIAL |
| OTGD-028-AND-HIST-006-02 | hist-delete-race — - **GIVEN** a detail request is in flight when its deletion is accepted - **WHEN** the old response arrives - **THEN** it is discarded according to the deletion generation/tombstone and cannot repopulate History. | PARTIAL |
| OTGD-028-AND-HIST-006-03 | hist-single-check-export-scope-survives-source-change — - **GIVEN** History starts Export this check for A while unrelated checks B and C exist - **WHEN** the user changes This device to Synced records or resumes after reauthentication - **THEN** the selected scope remains only A and related authorized evidence; B and C cannot enter the archive without a new expanded-scope summary and confirmation. | PARTIAL |
| OTGD-028-AND-HIST-007-01 | hist-large-text-detail — - **GIVEN** 200% font scaling and a narrow Android display - **WHEN** a saliva detail section contains all three analytes - **THEN** names, values, units, and qualifiers remain legible and reachable without clipped columns. | BLOCKED |
| OTGD-028-AND-HIST-007-02 | hist-ios-back-position — - **GIVEN** the iOS user opens a row after loading three pages - **WHEN** they navigate back - **THEN** the same selected row and list position are restored with no duplicated page fetch. | BLOCKED |
