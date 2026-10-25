# OTGD-045 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/verified-release-and-browser-access/specs/cloud-release-orchestration/spec.md`; SHA256 `c62bb011c5e71f177ededaf19e710e2ec40a97618a5b427d144f97bcd67d7a26`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-045/test-plan.md`. External review artifact only; PM controls import.

All 6 stable cases / 2 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `uv run --project services/api python scripts/ci_gate.py infra-unit`
- `node --import tsx --test --test-reporter=junit test/*.test.ts (cwd: infra)`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-045-CLOUD-DEP-007-01 | A valid absent public subdomain is registered — - **GIVEN** a matching enabled private distribution, issued TLS and absent record - **WHEN** apply is explicitly requested - **THEN** one CNAME is created; successful change observation must occur within ten minutes, SDK timeouts/retries may delay failure reporting, and failure does not imply cancellation or rollback. | PARTIAL |
| OTGD-045-CLOUD-DEP-007-02 | A foreign record appears after preview — - **GIVEN** an absent lookup followed by another actor creating that record - **WHEN** CREATE is submitted - **THEN** AWS rejects the conflict, the foreign record is preserved and the command reports failure. | PARTIAL |
| OTGD-045-CLOUD-DEP-007-03 | The exact target already exists — - **GIVEN** the observed CNAME has the admitted target and supported record form - **WHEN** apply is requested - **THEN** no write occurs and the receipt identifies an observed equivalent record rather than fabricated propagation evidence. | PASS |
| OTGD-045-CLOUD-DEP-007-04 | Caller supplies apex or foreign authority — - **GIVEN** a private/foreign zone, conflicting record, disabled distribution, wrong alias or certificate - **WHEN** admission runs - **THEN** no DNS mutation or successful registration receipt occurs. | PASS |
| OTGD-045-CLOUD-DEP-011-01 | Genuine matching release authority is supplied — - **GIVEN** bounded stable regular key/evidence files and the matching independently trusted Ed25519 public key - **WHEN** the actual release operation loads them - **THEN** signature verification/signing uses those exact bytes and never logs key material. | PASS |
| OTGD-045-CLOUD-DEP-011-02 | A file is special, replaced or exposed — - **GIVEN** a FIFO, symlink, oversized file, changed inode/metadata or broadly readable private key - **WHEN** the reader is called - **THEN** it refuses promptly before signing or cloud mutation. | PASS |
