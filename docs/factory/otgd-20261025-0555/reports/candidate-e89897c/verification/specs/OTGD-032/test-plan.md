# OTGD-032 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/production-mobile-platform/specs/android-profile/spec.md`; SHA256 `b90bbf657f3c8e8a24eab7ab93f04c680018bbe2179131c1b8aa70c6d3d67a43`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-032/test-plan.md`. External review artifact only; PM controls import.

All 16 stable cases / 7 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-032-AND-PRO-001-01 | pro-empty-profile-save — - **GIVEN** an account profile with no provided fields - **WHEN** the user saves without entering optional context - **THEN** numeric values remain null and no default cannabis exposure or baseline is created. | PARTIAL |
| OTGD-032-AND-PRO-001-02 | pro-declined-history — - **GIVEN** last use is set to Prefer not to say - **WHEN** the profile is saved and reloaded - **THEN** the declined marker persists and its timestamp remains null. | PARTIAL |
| OTGD-032-AND-PRO-002-01 | pro-imperial-bmi — - **GIVEN** the user enters 5 feet 10 inches and 180 pounds - **WHEN** the draft is validated and saved - **THEN** canonical height is 177.8 cm, weight is 81.6466266 kg before contract precision handling, and displayed BMI is 25.8 with no category label. | PARTIAL |
| OTGD-032-AND-PRO-002-02 | pro-invalid-number — - **GIVEN** height is zero, weight is non-finite, or age contains a fraction - **WHEN** Save profile is pressed - **THEN** the relevant inline errors appear, BMI is unavailable, and no invalid profile is submitted. | PARTIAL |
| OTGD-032-AND-PRO-003-01 | pro-edit-after-check — - **GIVEN** a finalized check records weight 80 kg and profile version A - **WHEN** the user saves weight 82 kg as version B - **THEN** the historical check retains version A and 80 kg while the next check may use B. | PASS |
| OTGD-032-AND-PRO-003-02 | pro-edit-during-open-draft — - **GIVEN** a check draft has already copied version A - **WHEN** another device changes the profile - **THEN** the open check does not silently acquire the new context and displays its saved profile version on review. | PARTIAL |
| OTGD-032-AND-PRO-003-03 | pro-edit-before-first-acquisition-still-frozen — - **GIVEN** Start check created session A with profile revision P1 and no capture yet - **WHEN** the user saves revision P2 on this or another device - **THEN** A still displays P1 and its original target time; using P2 requires a new linked check created after that save. | PARTIAL |
| OTGD-032-AND-PRO-004-01 | pro-two-device-conflict — - **GIVEN** two devices edit the same base revision - **WHEN** the first save succeeds and the second receives 412 - **THEN** the second displays both versions and retains its draft until the user chooses. | PARTIAL |
| OTGD-032-AND-PRO-004-02 | pro-save-timeout-retry — - **GIVEN** the server saved a revision but the response was lost - **WHEN** the app retries with the original key and payload - **THEN** one revision is returned and no duplicate change is recorded. | PARTIAL |
| OTGD-032-AND-PRO-004-03 | pro-stale-generation-is-quarantined — - **GIVEN** a queued profile Save carries an earlier data generation - **WHEN** the service returns 410 after accepted all-data deletion - **THEN** the operation is quarantined without rewriting its generation; new saves wait for the explicit reset acknowledgment. | PARTIAL |
| OTGD-032-AND-PRO-005-01 | pro-offline-edit — - **GIVEN** an account profile is cached and the network is unavailable - **WHEN** the user saves valid changes - **THEN** the local revision is labeled pending and reconciliation later applies the original ETag rather than pretending a server save occurred. | PARTIAL |
| OTGD-032-AND-PRO-005-02 | pro-guest-to-account — - **GIVEN** a fictional demo profile exists - **WHEN** the user opens a newly authenticated account - **THEN** the account profile is fetched or shown empty and the demo profile is not imported automatically. | PARTIAL |
| OTGD-032-AND-PRO-006-01 | pro-future-use-time — - **GIVEN** a last-use timestamp is later than the current device time - **WHEN** the user saves - **THEN** the app asks the user to review the date/time or select unknown and does not silently clamp the timestamp. | PASS |
| OTGD-032-AND-PRO-006-02 | pro-demographics-do-not-score — - **GIVEN** a complete profile with daily use and all demographics - **WHEN** the dashboard or result is displayed - **THEN** no metabolic-rate calculation, baseline qualification, or intoxication probability is created from those fields. | PARTIAL |
| OTGD-032-AND-PRO-007-01 | pro-accessible-errors — - **GIVEN** screen-reader navigation and 200% text scaling - **WHEN** two fields fail validation - **THEN** the error summary is announced, the first invalid field receives focus, and Save/Cancel remain reachable without overlapping controls. | PARTIAL |
| OTGD-032-AND-PRO-007-02 | pro-ios-unit-roundtrip — - **GIVEN** an iOS profile contains canonical values with more precision than display - **WHEN** the user toggles units twice without editing - **THEN** stored values and BMI are unchanged and no new profile revision is created. | PARTIAL |
