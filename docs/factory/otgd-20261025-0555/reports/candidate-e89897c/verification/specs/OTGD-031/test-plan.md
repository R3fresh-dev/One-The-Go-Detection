# OTGD-031 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/production-mobile-platform/specs/android-privacy-controls/spec.md`; SHA256 `993e7c0f65b5ee4bd9b2f470e2d4111f6329f083e7650a76ab71f78abf5e9f3f`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-031/test-plan.md`. External review artifact only; PM controls import.

All 17 stable cases / 7 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`
- `python scripts/ci_gate.py localstack-api`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-031-AND-PRIV-001-01 | priv-enable-queued-upload-retries — - **GIVEN** a signed-in account with one explicitly queued check and another unqueued local check - **WHEN** the user confirms Enable automatic retries - **THEN** only the already queued check is eligible for automatic retry and the other check, raw media, and research data remain unqueued. | PARTIAL |
| OTGD-031-AND-PRIV-001-02 | priv-disable-during-upload — - **GIVEN** a permitted upload is in flight and more operations are queued - **WHEN** the user disables automatic retries - **THEN** no new automatic retry starts, the in-flight outcome is reconciled honestly, and the UI does not claim previously accepted data was deleted. | PARTIAL |
| OTGD-031-AND-PRIV-002-01 | priv-clear-demo-only — - **GIVEN** demo and account caches coexist - **WHEN** Clear demo records is confirmed - **THEN** demo records disappear, account records remain, and no cloud deletion request is made. | PARTIAL |
| OTGD-031-AND-PRIV-002-02 | priv-cancel-unsynced-clear — - **GIVEN** three account records are unsynchronized - **WHEN** the warning shows three and the user selects Cancel - **THEN** all records and queue entries remain unchanged. | PARTIAL |
| OTGD-031-AND-PRIV-003-01 | priv-valid-data-deletion — - **GIVEN** an owned account, current policy review, and reauthentication within five minutes - **WHEN** the user confirms deletion of profile and check data - **THEN** one all_data job is accepted and the account identity is retained according to the displayed scope. | PASS |
| OTGD-031-AND-PRIV-003-02 | priv-forged-owner-or-stale-auth — - **GIVEN** a deletion body contains another owner's ID or authentication is stale - **WHEN** it is submitted - **THEN** the server rejects it and no deletion job affects another account or bypasses reauthentication. | PARTIAL |
| OTGD-031-AND-PRIV-004-01 | priv-deletion-response-lost — - **GIVEN** the server accepted a deletion but its response was lost - **WHEN** the app retries with the same key and scope - **THEN** the same job is returned and the UI remains requested/running until actual completion is reported. | PASS |
| OTGD-031-AND-PRIV-004-02 | priv-retention-exception — - **GIVEN** a kind=deletion job reports partially_retained for a named audit category retained until a stated date - **WHEN** status is shown - **THEN** that exception remains visible and the app does not claim every copy was erased. | PASS |
| OTGD-031-AND-PRIV-004-03 | priv-job-kind-state-discriminator — - **GIVEN** a completed export and a partially_retained deletion are returned by the shared job route - **WHEN** Privacy routes each response - **THEN** export-only expired is never interpreted as deletion state; partially_retained displays the listed exception and no partially_completed fallback is created. | PASS |
| OTGD-031-AND-PRIV-005-01 | priv-offline-device-reconnects — - **GIVEN** device A completed all_data deletion while device B held old queued records offline - **WHEN** B reconnects - **THEN** the server returns 410 for new stale-generation mutations and B quarantines their original operations instead of rebinding or restoring them. | PASS |
| OTGD-031-AND-PRIV-005-02 | priv-late-fetch-after-clear — - **GIVEN** an old-history fetch is in flight when account deletion is accepted - **WHEN** the fetch returns - **THEN** its payload cannot recreate deleted local content. | PARTIAL |
| OTGD-031-AND-PRIV-005-03 | priv-explicit-generation-reset-required — - **GIVEN** an all_data deletion finished and the account remains usable - **WHEN** the user returns to Profile or Check before acknowledging the new generation - **THEN** old queued records remain quarantined and new protected writes stay blocked until Start a new empty workspace is explicitly confirmed. | PARTIAL |
| OTGD-031-AND-PRIV-005-04 | priv-deletion-replay-does-not-create-new-job — - **GIVEN** a deletion was accepted and advanced generation but its response was lost - **WHEN** the exact original idempotent request is replayed under the shared replay policy - **THEN** the original job is returned; a distinct mutation carrying the old generation receives 410 and is quarantined. | PASS |
| OTGD-031-AND-PRIV-006-01 | priv-unconfigured-retention — - **GIVEN** production has no approved policy for raw eye recordings - **WHEN** the privacy and capture availability screens load - **THEN** raw recording is unavailable and no generic consent checkbox enables it. | PARTIAL |
| OTGD-031-AND-PRIV-006-02 | priv-redacted-deletion-log — - **GIVEN** a deletion request fails validation - **WHEN** the event is logged - **THEN** logs include a redacted operation/request reference and reason category without tokens, profile values, or measurements. | PARTIAL |
| OTGD-031-AND-PRIV-007-01 | priv-accessible-confirmation — - **GIVEN** TalkBack and 200% text scaling - **WHEN** the deletion review opens - **THEN** scope, retention exceptions, and both final/cancel actions are reachable before confirmation can occur. | BLOCKED |
| OTGD-031-AND-PRIV-007-02 | priv-ios-account-deletion — - **GIVEN** an authenticated iOS account - **WHEN** the user completes in-app account deletion review and reauthentication - **THEN** the same scoped asynchronous job is requested and its completion status is represented without sending the user to an unrelated website. | BLOCKED |
