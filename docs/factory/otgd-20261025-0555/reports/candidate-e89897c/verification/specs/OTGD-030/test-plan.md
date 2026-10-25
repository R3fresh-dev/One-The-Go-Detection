# OTGD-030 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/production-mobile-platform/specs/android-onboarding/spec.md`; SHA256 `da9837761a2034853336456f15dc249daf23aed73a9808bbdf4b1b690eda53ee`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-030/test-plan.md`. External review artifact only; PM controls import.

All 14 stable cases / 6 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-030-AND-ONB-001-01 | onb-first-launch-demo — - **GIVEN** a fresh installation without preferences - **WHEN** the user selects Explore the demo - **THEN** the introduction identifies synthetic sample/sensor values and does not display a probability or create a research enrollment. | PARTIAL |
| OTGD-030-AND-ONB-001-02 | onb-signed-in-still-measurement-only — - **GIVEN** an authenticated account with no study authorization - **WHEN** onboarding completes - **THEN** the dashboard shows measurement-only availability and no study capability is inferred from the account or notice receipt. | PARTIAL |
| OTGD-030-AND-ONB-001-03 | onb-research-configuration-cannot-change-release — - **GIVEN** an authenticated account and a valid-looking research manifest - **WHEN** onboarding or public configuration reports research availability - **THEN** the release retains inference_available=false and displays no probability or research-estimate capability. | PARTIAL |
| OTGD-030-AND-ONB-002-01 | onb-demo-does-not-upload — - **GIVEN** a completed demo check and a subsequently authenticated account - **WHEN** the user opens the account workspace - **THEN** demo history is absent from account history and no upload request for the demo check is enqueued. | PARTIAL |
| OTGD-030-AND-ONB-002-02 | onb-cancel-workspace-switch — - **GIVEN** an unfinished demo check - **WHEN** the user selects Sign in and then Stay in check - **THEN** the check remains visible with unchanged identity and no authentication browser is opened; if a native run had already ended to leave capture, it remains ended with that fact displayed. | NOT_RUN |
| OTGD-030-AND-ONB-002-03 | onb-guest-demo-never-has-upload-path — - **GIVEN** a guest demo check and an authenticated local/QA synthetic project both exist - **WHEN** the user opens the guest check, signs in, or reconnects - **THEN** the guest check remains local and has no upload action; a separate account-owned synthetic fixture requires its own creation and upload choice. | PARTIAL |
| OTGD-030-AND-ONB-003-01 | onb-notice-accepted-once — - **GIVEN** the current notice is visible and its checkbox is initially unchecked - **WHEN** the user checks it and selects Continue - **THEN** one dated receipt is saved, the dashboard opens, and repeating the submission creates no duplicate receipt. | PARTIAL |
| OTGD-030-AND-ONB-003-02 | onb-stale-notice-write — - **GIVEN** the server requires a newer notice than the bundled accepted version - **WHEN** the app attempts an account write - **THEN** the write remains pending, the app offers the newer notice, and neither a fabricated acknowledgment nor a research-consent record is sent. | PARTIAL |
| OTGD-030-AND-ONB-004-01 | onb-airplane-mode-demo — - **GIVEN** the phone is offline on first launch - **WHEN** the user completes demo onboarding - **THEN** the dashboard and synthetic check are usable and the UI describes their local state. | PASS |
| OTGD-030-AND-ONB-004-02 | onb-no-permission-prompts — - **GIVEN** every OS permission is denied - **WHEN** all onboarding screens are traversed - **THEN** no permission dialog appears and onboarding is not blocked by those denials. | PARTIAL |
| OTGD-030-AND-ONB-005-01 | onb-kill-before-commit — - **GIVEN** acknowledgment persistence has not completed - **WHEN** the process is terminated and relaunched - **THEN** the notice remains unacknowledged and no account write is sent. | BLOCKED |
| OTGD-030-AND-ONB-005-02 | onb-kill-after-commit — - **GIVEN** the acknowledgment transaction completed before process termination - **WHEN** the app relaunches - **THEN** the chosen workspace opens with the existing receipt and no duplicate onboarding event. | BLOCKED |
| OTGD-030-AND-ONB-006-01 | onb-talkback-and-large-text — - **GIVEN** TalkBack and 200% font scaling are enabled on a 360 dp-wide Android screen - **WHEN** the user traverses welcome and the notice - **THEN** each action is reachable, its role/label is announced, and scrolling exposes the entire notice and Continue control. | BLOCKED |
| OTGD-030-AND-ONB-006-02 | onb-ios-parity — - **GIVEN** a fresh iOS installation with Reduce Motion enabled - **WHEN** demo onboarding completes using VoiceOver - **THEN** the same workspace and notice states are stored without required animation or a camera/Bluetooth prompt. | BLOCKED |
