# OTGD-008 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/authorized-model-execution/specs/research-evaluation/spec.md`; SHA256 `1307ac2ebe390b58619b599669a9c52773104dded84661be708aa132d95f8626`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-008/test-plan.md`. External review artifact only; PM controls import.

All 19 stable cases / 8 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-008-EVAL-001-01 | Reproducible fitting — - **WHEN** the same bounded data and frozen plans are supplied - **THEN** the tooling emits reproducible finite artifact bytes and exact dataset and plan digests | PASS |
| OTGD-008-EVAL-001-02 | Participant or partition leakage — - **WHEN** a held-out participant enters fitting or a later session crosses its frozen partition boundary - **THEN** the tooling refuses the evaluation rather than reporting performance | PARTIAL |
| OTGD-008-EVAL-002-01 | Full report — - **WHEN** evaluation runs on supplied qualified data - **THEN** its report names artifact, dataset, split and analysis digests and includes chemical-only, app-only, combined and ECG-removed analyses with complete matched denominators | PASS |
| OTGD-008-EVAL-002-02 | Omitted or changed rows — - **WHEN** invalid or abstaining rows are removed, an ablation uses different rows, or a threshold changes after locking - **THEN** the tooling refuses to attest a valid evaluation report | PARTIAL |
| OTGD-008-EVAL-002-03 | Engineering fixtures — - **WHEN** automated tests use fictional cohort rows - **THEN** their artifacts are labeled engineering evidence and never loaded as an approved study or human model by deployment | PARTIAL |
| OTGD-008-EVAL-003-01 | Same-check acquisition — - **WHEN** a chemical or task observation follows the target but falls within the frozen capture and information cutoffs - **THEN** it remains eligible without changing the original target or partition | PARTIAL |
| OTGD-008-EVAL-003-02 | Future information — - **WHEN** a profile predictor follows the target, a same-check observation follows capture completion, availability follows its cutoff, or an interval exceeds its frozen bound - **THEN** the tooling rejects the dataset, including when that row is marked invalid | PASS |
| OTGD-008-EVAL-004-01 | Reconciled categories — - **WHEN** evaluation completes - **THEN** category session identities and counts reconcile to their cohort aggregate independently for each of the six dimensions | PASS |
| OTGD-008-EVAL-004-02 | Sparse or omitted categories — - **WHEN** a frozen category is empty, contains one endpoint class or too few participants - **THEN** counts remain visible and unsupported rates and intervals remain null | PASS |
| OTGD-008-EVAL-004-03 | Unplanned category — - **WHEN** a row omits a dimension or introduces a category outside the frozen plan - **THEN** admission fails before fitting or evaluation | PARTIAL |
| OTGD-008-EVAL-005-01 | Unclassified checks — - **WHEN** checks abstain or fail quality admission - **THEN** they remain in full-row accounting without receiving invented classifications or entering classified predictive-value denominators | PASS |
| OTGD-008-EVAL-005-02 | Undefined predictive value — - **WHEN** no positive or negative classifications exist or too few bootstrap draws define a statistic - **THEN** the affected statistic or interval is null and its denominator and effective draw count remain visible | PASS |
| OTGD-008-EVAL-005-03 | Defined predictive values — - **WHEN** both classified denominators and sufficient participant-cluster draws exist - **THEN** PPV and NPV equal their respective correct classifications divided by classified denominators, with qualified intervals and observed prevalence | PASS |
| OTGD-008-EVAL-006-01 | Server-compatible evidence — - **WHEN** fitting follows dataset custody lock and evaluation follows the post-fit pipeline lock - **THEN** the engine report carries the post-fit lock and admits the exact trained-artifact chronology | PASS |
| OTGD-008-EVAL-006-02 | Altered or premature evidence — - **WHEN** an artifact or denominator changes, evaluation precedes the pipeline lock, or the report substitutes the earlier custody lock for the pipeline lock - **THEN** reproduction or server admission rejects the evidence | PASS |
| OTGD-008-EVAL-007-01 | Supplied historical assertions — - **WHEN** a dataset names an authorization, independent assessor or historical lock - **THEN** output retains those references and labels their authenticity unverified rather than treating JSON assertions as approval | PASS |
| OTGD-008-EVAL-007-02 | Self-approved model — - **WHEN** tooling output is supplied as authority without independently released study, model, calibration and qualification records - **THEN** runtime admission refuses an estimate despite internally consistent artifact and report bytes | PARTIAL |
| OTGD-008-EVAL-008-01 | Stable regular input — - **WHEN** a bounded regular file has unchanged identity, size and metadata throughout reading - **THEN** its exact bytes are parsed and hashed for reproducible evidence | PASS |
| OTGD-008-EVAL-008-02 | Unsafe or changing input — - **WHEN** an input is a symlink, FIFO, oversized file or changes during its descriptor read - **THEN** the CLI refuses it without blocking indefinitely or producing an evaluation | PASS |
