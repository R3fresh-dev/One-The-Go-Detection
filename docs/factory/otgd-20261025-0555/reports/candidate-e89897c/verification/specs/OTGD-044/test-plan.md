# OTGD-044 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/verified-release-and-browser-access/specs/cloud-browser-delivery/spec.md`; SHA256 `758f7dd11a72a15750d44a61d49d986b923232ac981fcb9ab304a56526e5bb6c`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-044/test-plan.md`. External review artifact only; PM controls import.

All 8 stable cases / 3 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `uv run --project services/api python scripts/ci_gate.py infra-unit`
- `node --import tsx --test --test-reporter=junit test/*.test.ts (cwd: infra)`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-044-WEB-DEP-007-01 | Public transport probes execute — - **GIVEN** a published admitted artifact and the full supported response policy - **WHEN** index, assets and the history route are retrieved over verified HTTPS - **THEN** exact byte digest/size and all required transport/CSP controls verify. | PARTIAL |
| OTGD-044-WEB-DEP-007-02 | A policy fragment hides a weaker route — - **GIVEN** a missing referrer directive, wildcard script/connect source, duplicate CSP directive or unprotected history response - **WHEN** public verification runs - **THEN** it fails without a verified-access receipt. | PASS |
| OTGD-044-WEB-DEP-007-03 | A public response exceeds the signed file — - **GIVEN** an oversized or unexpectedly encoded HTTP response - **WHEN** verification streams the response - **THEN** it refuses at the expected-size boundary without allocating the full untrusted body. | PASS |
| OTGD-044-WEB-DEP-009-01 | The supplied infrastructure matches the release — - **GIVEN** the actual one-origin OAC distribution and unchanged signed archive - **WHEN** publication or DNS admission runs - **THEN** routing and every archive member match the admitted release before mutation. | PARTIAL |
| OTGD-044-WEB-DEP-009-02 | A secondary route escapes the admitted origin — - **GIVEN** a foreign assets behavior, extra origin/group, wrong prefix, disabled distribution or non-always-signing OAC - **WHEN** admission runs - **THEN** it refuses publication and DNS changes. | PASS |
| OTGD-044-WEB-DEP-009-03 | An archive changes during verification — - **GIVEN** a special/oversized/replaced archive or mismatching member/digest - **WHEN** bounded verification executes - **THEN** it fails before any public bytes are published. | PARTIAL |
| OTGD-044-WEB-DEP-010-01 | The public release returns its exact artifact — - **GIVEN** the admitted published index/assets and matching identity responses - **WHEN** the bounded transport probe executes - **THEN** signed byte sizes and digests match, including the history fallback. | PARTIAL |
| OTGD-044-WEB-DEP-010-02 | The public response is unexpectedly encoded or oversized — - **GIVEN** compression or more bytes than the signed artifact - **WHEN** the response is streamed - **THEN** verification refuses at its bound without buffering the untrusted body. | PASS |
