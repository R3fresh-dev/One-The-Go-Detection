# OTGD-018 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/optional-raw-recording-lifecycle/specs/raw-recording-customer-flow/spec.md`; SHA256 `a688ab279a337ce745968e41c3d834c1afa8486a45901544cd7f779df2d54218`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-018/test-plan.md`. External review artifact only; PM controls import.

All 16 stable cases / 8 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-018-AND-RAW-001-01 | Approved terms are independently verified — - **GIVEN** the owned study returns current consent and an approved policy - **WHEN** the participant opens Recording choices & retention - **THEN** exact verified terms appear before any choice can be confirmed. | PARTIAL |
| OTGD-018-AND-RAW-001-02 | A projected purpose is substituted — - **GIVEN** the server reply contains policy.content for purpose A and displayed purpose B - **WHEN** the client verifies the reply - **THEN** the policy is rejected and acquisition remains unavailable. | PARTIAL |
| OTGD-018-AND-RAW-002-01 | Participant chooses local recording only — - **GIVEN** verified terms and both choices off - **WHEN** the participant enables device recording and confirms the separate notice - **THEN** upload remains off and no raw file is queued. | PASS |
| OTGD-018-AND-RAW-002-02 | The workspace changes before confirmation — - **GIVEN** unchecked choices were edited in account A generation 1 - **WHEN** account B or a new generation opens the form - **THEN** unfinished choices and notice acknowledgment reset. | PASS |
| OTGD-018-AND-RAW-003-01 | Accepted response is lost — - **GIVEN** the service accepted a preference but its reply was lost - **WHEN** the customer retries - **THEN** the original body, timestamp and request key are reused and the original receipt is reconciled. | PASS |
| OTGD-018-AND-RAW-003-02 | Effective permission exceeds the receipt — - **GIVEN** a receipt confirms upload=false - **WHEN** a status reply says upload=true without a new matching receipt - **THEN** the client rejects the status. | PASS |
| OTGD-018-AND-RAW-004-01 | A grant reply arrives after revocation — - **GIVEN** an optional-purpose grant request is in flight - **WHEN** the participant requests revocation before its reply - **THEN** the grant intent remains blocked and the late reply cannot revive it. | PASS |
| OTGD-018-AND-RAW-004-02 | Old cleanup and new pending cleanup coexist — - **GIVEN** completed revocation A and newer cleanup-pending revocation B for eye video - **WHEN** status is refreshed after B was accepted - **THEN** eye recording remains fenced until B is completed. | PASS |
| OTGD-018-AND-RAW-005-01 | An uploaded object is awaiting verification — - **GIVEN** retention state retained and upload_state quarantine - **WHEN** status is displayed - **THEN** quarantine is visible and the app does not claim verified upload or completed deletion. | PASS |
| OTGD-018-AND-RAW-005-02 | Physical cleanup has not completed — - **GIVEN** a revoked artifact has cleanup_pending with no cleanup_completed_at - **WHEN** its receipt is displayed - **THEN** pending cleanup remains explicit and is never labeled deleted. | PASS |
| OTGD-018-AND-RAW-006-01 | Participant saves approved local recording — - **GIVEN** an approved codec and separately confirmed record=true, upload=false - **WHEN** native acquisition completes and its immutable evidence matches the fresh start - **THEN** bytes and metadata commit together to SQLCipher, native handoff memory is released, and the upload queue remains empty. | PARTIAL |
| OTGD-018-AND-RAW-006-02 | Consent was revoked on another device — - **GIVEN** a cached optional receipt appears to permit recording - **WHEN** fresh capture start refuses or narrows the receipt - **THEN** native raw recording never starts and cached permission cannot override the fresh decision. | PARTIAL |
| OTGD-018-AND-RAW-007-01 | A stopped app resumes after retention expiry — - **GIVEN** local raw bytes expired while the app was stopped - **WHEN** the owner unlocks the workspace - **THEN** expired and unindexed bytes are removed before exposure, failed removal remains pending, no expired read or upload is admitted, and the stopped app makes no exact-time physical cleanup claim. | PARTIAL |
| OTGD-018-AND-RAW-007-02 | Renewal response is lost — - **GIVEN** a ticket renewal has an unknown response - **WHEN** explicit upload is retried - **THEN** its exact key and body are reused; after an acknowledged ticket later expires, a new bounded renewal epoch is persisted before requesting a replacement, and decrypted buffers are wiped on success, failure or cancellation. | PASS |
| OTGD-018-AND-RAW-008-01 | Participant explicitly includes an authorized recording — - **GIVEN** a distinct current export purpose and eligible retained source for the selected check - **WHEN** the participant reads the exact notice, selects the source and confirms the separate export - **THEN** recording or upload consent alone grants no export scope, the service job retains the exact authority, source selection, notice and acknowledgment timestamp, a lost receipt reuses the same key and body, and the archive verifies against that receipt before sharing. | PARTIAL |
| OTGD-018-AND-RAW-008-02 | A raw member is substituted — - **GIVEN** a downloaded ZIP has internally rehashed files but a changed raw source version or an unselected binary member - **WHEN** the app compares the archive with the authenticated job receipt - **THEN** exact source ID, version, kind, SHA-256, size and retained lifetime are compared with the owned frozen job; substituted, unknown or orphan paths refuse sharing, and no broadened permission is inferred from recording consent. | PASS |
