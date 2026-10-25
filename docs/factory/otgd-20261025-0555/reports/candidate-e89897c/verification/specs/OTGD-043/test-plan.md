# OTGD-043 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/qualified-participant-acquisition/specs/selected-vendor-ppg/spec.md`; SHA256 `c6f863bc71ebf167438fbe5cffe07b892da12cc066d0487d21403ff8dd49fa0d`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-043/test-plan.md`. External review artifact only; PM controls import.

All 15 stable cases / 7 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`
- `Exact compiler, executable and arduino-cli commands: immutable .github/workflows/native-build.yml; actual ci-firmware.log and ci-protected-reader.log retained.`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-043-VPPG-001-01 | Exact selected breakout initializes — - **GIVEN** approved/provisioned selected hardware, firmware and SDK material - **WHEN** the current signed PPG start is admitted - **THEN** the actual SDK adapter initializes the declared I2C/reset/MFIO/BPM mode and progresses through bounded warmup without blocking cancellation. | PARTIAL |
| OTGD-043-VPPG-001-02 | Generic ADC or failed hub initialization — - **GIVEN** a configuration expects SEN-15219 but a different adapter or failed I2C hub is present - **WHEN** acquisition is requested - **THEN** it returns a concrete invalid/unavailable disposition and never substitutes ADC counts, a simulator or a fabricated bpm. | PARTIAL |
| OTGD-043-VPPG-002-01 | Fresh FIFO with known invalid records — - **GIVEN** the current capture receives bounded distinct vendor records with valid and poor-contact statuses - **WHEN** the adapter processes them - **THEN** received counts reconcile to valid/invalid dispositions and only fresh permitted records contribute to the summary. | PASS |
| OTGD-043-VPPG-002-02 | No new FIFO data — - **GIVEN** one prior valid heart rate followed by empty FIFO, stale records or truncated responses - **WHEN** polling continues - **THEN** no prior number fills the missing interval, valid count does not advance and insufficient/stale evidence produces null completion. | PASS |
| OTGD-043-VPPG-002-03 | Identical values from genuine fresh dequeues — - **GIVEN** two separately successful current FIFO dequeues contain identical bpm/quality values and the vendor supplies no unique sample timestamp - **WHEN** the driver consumes each once - **THEN** both may count as observations, host sequence remains labeled as host-generated and neither equality nor polling cadence manufactures vendor timing or dropped-sample knowledge. | PASS |
| OTGD-043-VPPG-003-01 | Valid finger and vendor quality — - **GIVEN** enough fresh vendor records meet the approved finger/status/confidence/range criteria - **WHEN** the named extractor completes - **THEN** a finite positive measured bpm and original bounded quality/count evidence are retained; confidence is labeled acquisition quality. | PASS |
| OTGD-043-VPPG-003-02 | Poor finger state or confidence reinterpretation — - **GIVEN** finger absence, insufficient accepted data or a vendor confidence score - **WHEN** output is validated/displayed - **THEN** invalid capture has null bpm and explicit reasons, and confidence cannot be shown as accuracy or cannabis impairment probability. | PARTIAL |
| OTGD-043-VPPG-004-01 | Current signed vendor completion — - **GIVEN** a verified binding and current scoped start token with actual accepted vendor records - **WHEN** completion is signed and consumed by Android/iOS and the API - **THEN** the unchanged normalized evidence and timing/source labels survive exact signature and configuration validation. | PARTIAL |
| OTGD-043-VPPG-004-02 | Foreign boot or configuration — - **GIVEN** a signed completion from another boot, authorization, protocol/configuration or workspace - **WHEN** it is delivered late or replayed - **THEN** current client/server admission rejects it without attaching the old bpm to the replacement attempt. | PARTIAL |
| OTGD-043-VPPG-005-01 | Cancellation during warmup or blocked delivery — - **GIVEN** vendor acquisition is warming up or terminal transport is backpressured - **WHEN** Cancel or the admitted cutoff occurs - **THEN** the actual adapter stops before later delivery, retains the originating terminal identity and performs no resumed sampling. | PARTIAL |
| OTGD-043-VPPG-005-02 | Late old vendor read versus reconnect — - **GIVEN** an old read/result is delayed while another authenticated connection becomes current - **WHEN** it completes or notification is attempted - **THEN** origin fencing rejects its effects and only its own resources may be stopped; no participant payload reaches the replacement peer. | PARTIAL |
| OTGD-043-VPPG-006-01 | Installed and currently admitted vendor PPG — - **GIVEN** the selected adapter is compiled and all its exact current independently released scopes match - **WHEN** Home and PPG capture are opened - **THEN** the supported vendor path and instruction journey are shown while actual acquisition still obtains a fresh start. | PARTIAL |
| OTGD-043-VPPG-006-02 | Approved record names an absent driver or raw codec — - **GIVEN** an operator record names a missing vendor build or unsupported raw encoding - **WHEN** capability/start/recording is evaluated - **THEN** software availability remains refused; an approval cannot manufacture code or raw permission. | PARTIAL |
| OTGD-043-VPPG-007-01 | Actual driver software fixtures — - **GIVEN** the same adapter used by firmware and the pinned vendor commands - **WHEN** fresh/empty/malformed FIFO, reset, quality, cutoff and cancellation cases execute - **THEN** tests verify its actual observable outcomes and both target builds retain source/artifact evidence without claiming sensor execution. | PARTIAL |
| OTGD-043-VPPG-007-02 | Compile mistaken for participant qualification — - **GIVEN** stock/protected compilation and fictional interoperability pass but no genuine reference/device/study evidence exists - **WHEN** participant or model eligibility is evaluated - **THEN** those external gates remain closed and the reports explicitly distinguish software tests from real sensor validation. | PASS |
