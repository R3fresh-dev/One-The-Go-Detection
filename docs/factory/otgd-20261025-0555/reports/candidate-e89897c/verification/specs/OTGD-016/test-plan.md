# OTGD-016 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/independent-recovery-admission/specs/recovery-authority/spec.md`; SHA256 `430fe7dfbfdb117add502c5632150690905d94b3dcb42ddc892bf1e8943f273c`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-016/test-plan.md`. External review artifact only; PM controls import.

All 6 stable cases / 2 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-016-RECOVERY-001-01 | Consistent retained authority — - **WHEN** the database matches all pinned retained control, identity, generation, deletion and recovery evidence - **THEN** ordinary service admission may proceed subject to current participant and study authority | PARTIAL |
| OTGD-016-RECOVERY-001-02 | Stale restored active row — - **WHEN** a retained deletion or recovery activation conflicts with an active database row or its queued job - **THEN** API and worker refuse new data work before commit, including when the database recovery row is absent | PARTIAL |
| OTGD-016-RECOVERY-001-03 | Missing local establishment — - **WHEN** retained PostgreSQL is paired with a missing or replacement emulator journal - **THEN** bootstrap and running service admission refuse silent establishment or account provisioning | PARTIAL |
| OTGD-016-RECOVERY-002-01 | Reapproved study — - **WHEN** every current registry dependency is freshly submitted, independently reviewed and released, and the exact study seal and participant consent are current - **THEN** that study may collect through current qualified configurations while every unsealed study remains suspended | PASS |
| OTGD-016-RECOVERY-002-02 | Boolean or stale approval override — - **WHEN** a database flag changes, old approval or consent is reused, a seal disappears or a dependency is retired or changed - **THEN** study capture and model execution refuse resumption | PASS |
| OTGD-016-RECOVERY-002-03 | Privacy cleanup during suspension — - **WHEN** nonprivacy admission fails while an accepted deletion needs safe object cleanup - **THEN** privacy cleanup may continue without reopening data or removing independently retained deletion evidence | PASS |
