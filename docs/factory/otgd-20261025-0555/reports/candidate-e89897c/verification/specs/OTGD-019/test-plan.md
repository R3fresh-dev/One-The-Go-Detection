# OTGD-019 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/production-mobile-platform/specs/android-alcohol-channel/spec.md`; SHA256 `6c423c75ae449e935fe8856f61d70af07aaab582719baba1d1e1bc63d787f45a`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-019/test-plan.md`. External review artifact only; PM controls import.

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
| OTGD-019-AND-ALC-001-01 | Only the starter PPG board is connected — - **GIVEN** a Nano ESP32 and PPG module without a calibrated breath channel - **WHEN** Alcohol is opened - **THEN** the app shows hardware-required guidance and does not start a blow timer or produce an alcohol value. | PARTIAL |
| OTGD-019-AND-ALC-001-02 | Approved configuration is missing — - **GIVEN** a connected device advertises alcohol capability without an approved configuration - **WHEN** sampling is requested - **THEN** the app and server reject the request with a configuration-unavailable reason. | PARTIAL |
| OTGD-019-AND-ALC-002-01 | Combined session has two measured channels — - **GIVEN** independently valid alcohol and cannabis records - **WHEN** session detail is displayed - **THEN** each channel has its own card, units, timing, and validity explanation. | PARTIAL |
| OTGD-019-AND-ALC-002-02 | Cannabis result is unavailable — - **GIVEN** a valid authorized alcohol record and unavailable cannabis inference - **WHEN** results render - **THEN** the alcohol measurement does not manufacture a cannabis estimate. | PARTIAL |
| OTGD-019-AND-ALC-003-01 | Quantified record arrives — - **GIVEN** an in-range qualified measurement in mg/L - **WHEN** the record is validated and displayed - **THEN** its numeric value and mg/L label remain paired. | PARTIAL |
| OTGD-019-AND-ALC-003-02 | Caller submits a BAC percentage — - **GIVEN** a value labeled percent BAC - **WHEN** it is submitted to the breath-alcohol route - **THEN** the service rejects the incompatible unit and performs no conversion. | NOT_RUN |
| OTGD-019-AND-ALC-004-01 | Sampling is inadequate — - **GIVEN** the device reports an inadequate breath sample - **WHEN** acquisition ends - **THEN** the result is invalid with no exact concentration and an actionable retry explanation. | PARTIAL |
| OTGD-019-AND-ALC-004-02 | Calibration expires — - **GIVEN** the instrument calibration is outside its qualified interval - **WHEN** a new record is requested - **THEN** the app blocks qualified sampling and identifies recalibration as the required action. | PARTIAL |
| OTGD-019-AND-ALC-005-01 | Demo is intentionally opened — - **GIVEN** the development demo action - **WHEN** the customer previews the channel - **THEN** every value is labeled fictional and no real measurement claim is made. | PARTIAL |
| OTGD-019-AND-ALC-005-02 | Simulated record targets a participant session — - **GIVEN** a nonsynthetic parent session - **WHEN** a simulated alcohol record is submitted - **THEN** the service rejects the provenance mismatch. | NOT_RUN |
| OTGD-019-AND-ALC-006-01 | Alcohol co-use is present — - **GIVEN** the cannabis model does not support alcohol co-use - **WHEN** a future research request is evaluated - **THEN** the unsupported cohort is handled by the manifest gate rather than a score adjustment in the app. | PARTIAL |
| OTGD-019-AND-ALC-006-02 | A low displayed value — - **GIVEN** a low or censored alcohol result - **WHEN** the result screen is shown - **THEN** no **Safe to drive** or legal-clearance message appears. | PASS |
