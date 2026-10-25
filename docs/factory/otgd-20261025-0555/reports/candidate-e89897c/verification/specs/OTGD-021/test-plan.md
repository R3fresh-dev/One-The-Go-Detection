# OTGD-021 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/production-mobile-platform/specs/android-dashboard/spec.md`; SHA256 `c756e1eb65e8b3e9929a58c4c191e7c179529f8cd238da6e9cd6b5403439105e`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-021/test-plan.md`. External review artifact only; PM controls import.

All 17 stable cases / 7 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-021-AND-DASH-001-01 | dash-demo-home — - **GIVEN** an isolated demo workspace with a synthetic check - **WHEN** Home is displayed - **THEN** the demo badge and synthetic source description remain visible and no intoxication percentage appears. | PARTIAL |
| OTGD-021-AND-DASH-001-02 | dash-old-check — - **GIVEN** the latest check was collected yesterday - **WHEN** the dashboard opens today - **THEN** its collection date/time is shown and the card does not claim to represent the user's present state. | PARTIAL |
| OTGD-021-AND-DASH-002-01 | dash-double-start-tap — - **GIVEN** no active draft and an enabled start action - **WHEN** two rapid taps occur before navigation completes - **THEN** one logical session is created and both navigation events resolve to that session. | PARTIAL |
| OTGD-021-AND-DASH-002-02 | dash-gated-capture — - **GIVEN** pupil capture is unavailable because its approved protocol is not configured - **WHEN** View availability is selected - **THEN** the app explains that channel's unavailability and does not open the camera/flash or replace it with a fabricated account measurement. | PARTIAL |
| OTGD-021-AND-DASH-002-03 | dash-frozen-profile-at-creation — - **GIVEN** profile revision P1 is selected when Start check is pressed - **WHEN** P2 arrives before the first acquisition - **THEN** the draft retains P1, target_at equals its created_at, and its review identifies P1. | PARTIAL |
| OTGD-021-AND-DASH-003-01 | dash-resume-saliva-draft — - **GIVEN** a draft with one retained saliva attempt and no completed task - **WHEN** Continue check is selected - **THEN** the same draft opens at its next eligible step with the original sample identity. | PARTIAL |
| OTGD-021-AND-DASH-003-02 | dash-task-interruption-return — - **GIVEN** the app was backgrounded during the native task - **WHEN** Home is opened and the draft resumed - **THEN** the interruption is shown and no task completion is inferred from elapsed wall time. | PARTIAL |
| OTGD-021-AND-DASH-004-01 | dash-reader-disconnect — - **GIVEN** a connected reader with a recent battery value - **WHEN** its BLE link drops - **THEN** Home changes to Not connected and the battery value cannot remain labeled live. | PARTIAL |
| OTGD-021-AND-DASH-004-02 | dash-reader-reboot — - **GIVEN** a reader reconnects with a different boot identity - **WHEN** readiness is recalculated - **THEN** unfinished capture readiness resets and old monotonic readings are not presented as belonging to the new boot. | PARTIAL |
| OTGD-021-AND-DASH-005-01 | dash-offline-check-list — - **GIVEN** cached permitted history and no network - **WHEN** Home opens - **THEN** cached rows remain available with an offline indicator and the latest refresh time. | PARTIAL |
| OTGD-021-AND-DASH-005-02 | dash-lost-finalization-response — - **GIVEN** a session finalization request timed out - **WHEN** Home renders its recent row - **THEN** the row remains pending until the server is reconciled using the original identity/idempotency key. | PARTIAL |
| OTGD-021-AND-DASH-005-03 | dash-reconnect-respects-manual-retry — - **GIVEN** an explicitly queued account check has automatic retries disabled - **WHEN** the network reconnects - **THEN** Home shows the waiting item and manual Upload/Retry action without beginning a network mutation. | PARTIAL |
| OTGD-021-AND-DASH-006-01 | dash-account-switch-race — - **GIVEN** an account-A refresh is in flight - **WHEN** the user switches to demo before the response returns - **THEN** A's response is discarded and no account data appears in demo. | PARTIAL |
| OTGD-021-AND-DASH-006-02 | dash-out-of-order-refresh — - **GIVEN** refresh B returns a newer session revision before refresh A - **WHEN** A completes later - **THEN** the displayed revision does not regress. | NOT_RUN |
| OTGD-021-AND-DASH-007-01 | dash-accessible-status — - **GIVEN** TalkBack is enabled and the reader disconnects - **WHEN** the status changes - **THEN** “Reader, not connected” is announced once without an unbounded repeating alert. | BLOCKED |
| OTGD-021-AND-DASH-007-02 | dash-ios-check-tab — - **GIVEN** an existing draft on iOS - **WHEN** the Check tab is selected using VoiceOver - **THEN** the same draft decision used by the primary CTA appears with its correct focus and no duplicate session allocation. | BLOCKED |
| OTGD-021-AND-DASH-007-03 | dash-alcohol-route-is-reachable — - **GIVEN** no alcohol instrument or approved configuration exists - **WHEN** the user selects Alcohol measurement on Home - **THEN** the alcohol availability screen opens with Hardware required, its requirements action, and working Back navigation. | PARTIAL |
