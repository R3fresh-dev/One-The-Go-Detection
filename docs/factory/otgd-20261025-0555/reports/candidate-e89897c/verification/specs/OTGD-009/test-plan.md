# OTGD-009 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/authorized-model-execution/specs/research-model-execution/spec.md`; SHA256 `a110df0160cb1dfa6b1eb471ebe558eec1af8bcb86c7c883b8795bac2fdf714a`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-009/test-plan.md`. External review artifact only; PM controls import.

All 16 stable cases / 6 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-009-MODEL-006-01 | Qualified diameter-only model — - **WHEN** current independent geometry and acquisition approvals match the exact camera, sampled ROI, extractor and phone build, and the pinned model uses baseline diameter only - **THEN** diameter may enter research execution while physical onset and response latency remain unqualified | PASS |
| OTGD-009-MODEL-006-02 | Geometry cannot qualify response timing — - **WHEN** a model requires eye latency or relative constriction, geometry is missing, the configuration is collection-only, or an additional quality failure exists - **THEN** the geometry-only path refuses research execution | PASS |
| OTGD-009-MODEL-006-03 | Geometry approval withdrawn during computation — - **WHEN** the geometry release is retired or replaced before result commit - **THEN** current authority is resolved again and the old computation cannot commit | PARTIAL |
| OTGD-009-MODEL-001-01 | Admitted artifact — - **WHEN** independently released authority names the exact version, length, SHA-256, feature contract and calibration - **THEN** the worker loads only those bytes and executes bounded finite arithmetic | PASS |
| OTGD-009-MODEL-001-02 | Unsupported or changed artifact — - **WHEN** the artifact is executable, noncanonical, nonfinite, oversized, uses unknown features, has unstable scales or differs from its pinned hash - **THEN** the worker returns a controlled refusal with no research probability | PARTIAL |
| OTGD-009-MODEL-002-01 | Authorized positive path — - **WHEN** all exact authority and acquisition dependencies are active and consistent for a controlled research participant - **THEN** the worker may compute the approved endpoint within its stated population and protocol scope | PASS |
| OTGD-009-MODEL-002-02 | Revocation during computation — - **WHEN** a study, model, method, calibration, device binding or consent changes before commit - **THEN** the result is refused or the operation fails without committing an estimate from stale authority | PARTIAL |
| OTGD-009-MODEL-002-03 | Unqualified demonstration — - **WHEN** a guest, synthetic check, unapproved record or restored suspended study attempts inference - **THEN** it receives no research estimate even if request fields claim approval | PASS |
| OTGD-009-MODEL-003-01 | Missing or censored required chemical feature — - **WHEN** a required analyte is missing, below quantification, incompatible or out of scope - **THEN** the system preserves its qualifier and refuses inference without imputing zero | PARTIAL |
| OTGD-009-MODEL-003-02 | Native timing qualification — - **WHEN** the phone model, OS, native build, input/presentation clocks, implementation and extractor match independently released timing qualification - **THEN** the model uses its approved timing bias and uncertainty bound while retaining the unmodified native timing evidence | PARTIAL |
| OTGD-009-MODEL-003-03 | Unqualified phone timing — - **WHEN** a simulator or unsupported timing tuple supplies native timestamps - **THEN** the system records measurement evidence and refuses model eligibility | PASS |
| OTGD-009-MODEL-004-01 | Valid prior baseline — - **WHEN** the current and historical captures meet all owned evidence and scope checks - **THEN** the model uses their approved feature differences and binds the exact baseline snapshot hash | PARTIAL |
| OTGD-009-MODEL-004-02 | Foreign or stale baseline — - **WHEN** a baseline is foreign, retired, future, stale, incomplete or unqualified - **THEN** the worker refuses personalized inference | PARTIAL |
| OTGD-009-MODEL-005-01 | Admitted research estimate — - **WHEN** a validated authenticated result is outside the abstention band - **THEN** the interface shows the research endpoint, population, version, probability, threshold, limits and supplied measurement context | PASS |
| OTGD-009-MODEL-005-02 | Uncertainty abstention — - **WHEN** the probability lies within the frozen abstention band - **THEN** the result and interface show inconclusive with null score, classification and threshold | PASS |
| OTGD-009-MODEL-005-03 | Relabeled or inconsistent proof — - **WHEN** model version, endpoint, population, authority digest, baseline, uncertainty policy or threshold classification is inconsistent - **THEN** the client refuses the research display | PASS |
