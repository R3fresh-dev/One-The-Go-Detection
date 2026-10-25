# OTGD-003 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/authorized-model-execution/specs/android-guided-check/spec.md`; SHA256 `c171a3fd1d7705d710dd172ebe5d59046cc0023a2ddfedaf162092008703e648`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-003/test-plan.md`. External review artifact only; PM controls import.

All 2 stable cases / 1 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-003-AND-CHECK-007-01 | Qualified research check — - **WHEN** an explicitly uploaded authorized check completes the independently admitted research pipeline - **THEN** result navigation presents the linked research outcome and its actual acquisition time separately from synchronization status | PARTIAL |
| OTGD-003-AND-CHECK-007-02 | Legacy or unapproved claim — - **WHEN** a legacy result, local preference or valid-looking manifest claims research authority without current complete admission - **THEN** no score is admitted and the historical measurement-only or unsupported-result boundary remains in force | PASS |
