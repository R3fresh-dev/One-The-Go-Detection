# OTGD-029 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/production-mobile-platform/specs/android-offline-sync/spec.md`; SHA256 `388f00c1fab3eb1f905e140b7248ce8e737ae87349eb8a508068becbb51456b9`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-029/test-plan.md`. External review artifact only; PM controls import.

All 14 stable cases / 7 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

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
| OTGD-029-AND-SYNC-001-01 | Storage transaction succeeds — - **GIVEN** a completed permitted check - **WHEN** the finalization transaction commits - **THEN** the app shows **Saved on this device** and can reopen the same record after restart. | PARTIAL |
| OTGD-029-AND-SYNC-001-02 | Disk is full — - **GIVEN** the encrypted database write fails - **WHEN** the user finishes the check - **THEN** the app reports the save failure and does not show a success state or queue a nonexistent record. | PARTIAL |
| OTGD-029-AND-SYNC-002-01 | Customer cancels upload sheet — - **GIVEN** a local-only check - **WHEN** the upload confirmation is canceled - **THEN** no network mutation occurs and the check remains local. | PARTIAL |
| OTGD-029-AND-SYNC-002-02 | Study consent is revoked — - **GIVEN** a previously queued study check - **WHEN** authorization is rechecked after revocation - **THEN** upload is blocked and the app explains the permission change without retrying as another account or study. | PARTIAL |
| OTGD-029-AND-SYNC-003-01 | Response is lost after server acceptance — - **GIVEN** a finalize request committed remotely but its response was lost - **WHEN** the client retries - **THEN** it receives the same logical result/job and no second specimen/task/session is created. | PASS |
| OTGD-029-AND-SYNC-003-02 | Queue body is changed under the same key — - **GIVEN** an existing accepted idempotency key - **WHEN** different content is submitted under that key - **THEN** the service returns 409 and the app exposes a conflict rather than changing the frozen record. | PARTIAL |
| OTGD-029-AND-SYNC-004-01 | Two accounts use one phone — - **GIVEN** account A has unsynced records - **WHEN** A signs out and B signs in - **THEN** B cannot list or upload A's records. | PARTIAL |
| OTGD-029-AND-SYNC-004-02 | Production build receives local configuration — - **GIVEN** a production app/backend configuration - **WHEN** a local issuer or AWS-emulator endpoint is supplied - **THEN** startup fails closed; the configuration cannot silently redirect participant data. | PARTIAL |
| OTGD-029-AND-SYNC-005-01 | Another device finalized the session — - **GIVEN** a stale local ETag - **WHEN** PUT snapshot returns 412 for its stale precondition or 409 for a frozen-state conflict - **THEN** the app fetches the server state and does not overwrite it. | PASS |
| OTGD-029-AND-SYNC-005-02 | Correcting an accepted value — - **GIVEN** a finalized session requires correction - **WHEN** a correction is created - **THEN** reacquisition uses a new session UUID/target time and supersedes reference with no earlier physical components copied; an administrative report correction remains a distinct authorized workflow. | PARTIAL |
| OTGD-029-AND-SYNC-006-01 | Rate limit response — - **GIVEN** HTTP 429 with a valid Retry-After - **WHEN** scheduling the next attempt - **THEN** the queue honors the delay within a documented bound and shows a waiting state. | PASS |
| OTGD-029-AND-SYNC-006-02 | Invalid snapshot — - **GIVEN** HTTP 422 - **WHEN** the client classifies the failure - **THEN** automatic retry stops and the customer can inspect the reported field error. | PASS |
| OTGD-029-AND-SYNC-007-01 | Upload occurs after a day offline — - **GIVEN** a previously captured record - **WHEN** it reaches the service the next day - **THEN** history retains the original check time and separately records synchronization/evaluation time. | PARTIAL |
| OTGD-029-AND-SYNC-007-02 | Reboot during scored game — - **GIVEN** an interrupted reaction run in a restored draft - **WHEN** the application restarts - **THEN** it marks that attempt invalid and cannot submit it as a completed uninterrupted task. | PARTIAL |
