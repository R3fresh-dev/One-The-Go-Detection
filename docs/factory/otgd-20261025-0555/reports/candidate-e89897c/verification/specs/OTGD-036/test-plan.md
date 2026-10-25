# OTGD-036 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/production-mobile-platform/specs/android-settings-accessibility/spec.md`; SHA256 `2768fdfbe5ff0b1971d6aad04101ea2fa17db6f6c3012848aa3aa3f490e654c8`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-036/test-plan.md`. External review artifact only; PM controls import.

All 17 stable cases / 7 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-036-AND-SET-001-01 | set-signed-out-navigation — - **GIVEN** demo is active and no account is authenticated - **WHEN** Settings is opened - **THEN** Sign in is available, cloud deletion is unavailable with its account requirement, and local demo clearing remains reachable. | PARTIAL |
| OTGD-036-AND-SET-001-02 | set-active-check-switch — - **GIVEN** a check is active - **WHEN** Switch workspace is selected - **THEN** any active native run ends once before the decision; the UI explains that it cannot resume, the broader draft may be retained, and no record is moved between workspaces. | PARTIAL |
| OTGD-036-AND-SET-001-03 | set-research-access-visible-empty-state — - **GIVEN** a fresh account has no study memberships - **WHEN** the user selects Settings then Research access - **THEN** the feature opens its empty-state explanation and a working Back route without creating an invitation or enabling capture. | PARTIAL |
| OTGD-036-AND-SET-002-01 | set-theme-restart — - **GIVEN** Dark theme was saved - **WHEN** the process is terminated and relaunched - **THEN** Dark theme is restored without a prolonged light-screen flash or record mutation. | BLOCKED |
| OTGD-036-AND-SET-002-02 | set-units-do-not-rewrite — - **GIVEN** finalized checks contain canonical ng/mL and profile cm/kg values - **WHEN** US customary display is selected - **THEN** profile presentation may convert units, saliva units remain qualified as reported, and stored measurements/record hashes do not change. | PARTIAL |
| OTGD-036-AND-SET-003-01 | set-camera-denied — - **GIVEN** camera permission is denied - **WHEN** Permissions opens - **THEN** the camera row shows Denied with its feature explanation and Open app settings, without launching another prompt. | PASS |
| OTGD-036-AND-SET-003-02 | set-permission-changed-outside-app — - **GIVEN** the user grants Bluetooth permission in OS settings - **WHEN** the app returns to foreground - **THEN** the displayed state refreshes and the reader feature decides whether a new scan is needed; an old scan is not assumed successful. | PARTIAL |
| OTGD-036-AND-SET-004-01 | set-tampered-model-toggle — - **GIVEN** a modified preference file contains `inference_enabled:true` - **WHEN** Settings and the result workflow load - **THEN** the unsupported key grants no capability and probability remains unavailable in this release. | PARTIAL |
| OTGD-036-AND-SET-004-02 | set-qa-build-visible — - **GIVEN** the installed app uses QA services - **WHEN** Home or About is displayed - **THEN** QA is visible and the app cannot describe itself as a production clinical release. | PARTIAL |
| OTGD-036-AND-SET-004-03 | set-authorized-looking-research-output-still-disabled — - **GIVEN** a server response or local record advertises an active research model - **WHEN** Settings or result navigation evaluates it - **THEN** inference_available remains false and no current surface displays an impairment probability. | PASS |
| OTGD-036-AND-SET-005-01 | set-diagnostics-copy — - **GIVEN** a connection error has a support request ID - **WHEN** the user reviews and copies diagnostics - **THEN** only allowlisted build/environment/error-reference fields reach the clipboard. | PARTIAL |
| OTGD-036-AND-SET-005-02 | set-error-with-sensitive-payload — - **GIVEN** an internal exception includes a server payload with profile fields - **WHEN** diagnostics are generated - **THEN** the payload is excluded rather than serialized or truncated into the copy text. | PASS |
| OTGD-036-AND-SET-006-01 | set-large-text-navigation — - **GIVEN** 200% system font scale on a 360 dp Android display - **WHEN** Settings and Privacy are traversed - **THEN** labels wrap, controls remain reachable by scrolling, and no essential action is hidden behind navigation or keyboard. | BLOCKED |
| OTGD-036-AND-SET-006-02 | set-screen-reader-task-boundary — - **GIVEN** a timing-task configuration does not support the active input/accommodation - **WHEN** the user attempts that task - **THEN** the task feature explains the unsupported configuration and records unavailability rather than claiming equivalent measured timing. | PARTIAL |
| OTGD-036-AND-SET-006-03 | set-active-task-navigation-ends-before-dialog — - **GIVEN** a native reaction run is active - **WHEN** the user initiates a Settings/workspace route or End task - **THEN** the run ends once before an overlay, retained partial evidence is marked invalid, and subsequent draft choices never resume it. | PARTIAL |
| OTGD-036-AND-SET-007-01 | set-ios-dynamic-type — - **GIVEN** a large accessibility Dynamic Type size and VoiceOver - **WHEN** the user changes theme and opens privacy controls - **THEN** each label/action remains reachable with correct state announcements and preferences persist across launch. | BLOCKED |
| OTGD-036-AND-SET-007-02 | set-ios-restricted-permission — - **GIVEN** iOS reports camera access restricted by device policy - **WHEN** the permission row is opened - **THEN** it shows Restricted, does not promise that an ordinary permission prompt will fix it, and preserves access to other permitted features. | PARTIAL |
