# OTGD-041 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/qualified-participant-acquisition/specs/research-evaluation/spec.md`; SHA256 `f4bef2eee7577e8f57b7cd27b7463d3879dcb1d452c73540d8916f9d6bf41726`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-041/test-plan.md`. External review artifact only; PM controls import.

All 5 stable cases / 1 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-041-EVAL-002-01 | Full report — - **WHEN** the existing evaluation mode runs on supplied qualified data - **THEN** its report names artifact, dataset, split and analysis digests and includes chemical-only, app-only, combined and ECG-removed analyses with complete matched denominators | PASS |
| OTGD-041-EVAL-002-02 | Omitted or changed rows — - **WHEN** invalid or abstaining rows are removed, an ablation uses different rows, or a threshold changes after locking - **THEN** the tooling refuses to attest a valid evaluation report | PARTIAL |
| OTGD-041-EVAL-002-03 | Engineering fixtures — - **WHEN** automated tests use fictional cohort rows - **THEN** their artifacts are labeled engineering evidence and never loaded as an approved study or human model by deployment | PARTIAL |
| OTGD-041-EVAL-002-04 | Explicit restricted HR-only report — - **GIVEN** a prespecified locked server-interval policy with exactly the approved HR predictor and independently bound current/baseline evidence - **WHEN** the separate HR-only mode completes evaluation - **THEN** its strict report names `cardiac_hr_only`, reconciles every cohort/stratum and invalid/abstained row, and retains frozen dataset/split/analysis/artifact digests - **AND** chemical/app/ECG ablation comparisons are explicitly outside that mode and no multimodal superiority claim is emitted | PASS |
| OTGD-041-EVAL-002-05 | Implicit or mismatching reduced report — - **GIVEN** an absent or mismatching HR-only policy, a legacy model, extra predictors or incomplete row accounting - **WHEN** a single-variant report is submitted for model admission - **THEN** the service refuses it - **AND** the caller cannot use the new mode to omit required comparisons from the existing mode | PASS |
