# OTGD-007 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/authorized-model-execution/specs/android-settings-accessibility/spec.md`; SHA256 `8dc5faf4274edf798f4828bacff599c2c34c5aa6f5cb594481f2ca365ef401f6`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-007/test-plan.md`. External review artifact only; PM controls import.

All 2 stable cases / 1 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-007-AND-SET-004-01 | Authorized new binary — - **WHEN** the authenticated account has current independently released research and qualified channel scope - **THEN** capability screens describe that conditional scope without presenting it as clinical validation | PASS |
| OTGD-007-AND-SET-004-02 | Legacy or unapproved claim — - **WHEN** a legacy result, local preference or valid-looking manifest claims research authority without current complete admission - **THEN** no score is admitted and the historical measurement-only or unsupported-result boundary remains in force | PASS |
