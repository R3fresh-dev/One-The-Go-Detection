# OTGD-046 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/verified-release-and-browser-access/specs/fictional-browser-preview/spec.md`; SHA256 `1a331132cf6b66413d1705dc09d0c7f885b8fe1375ea72250dcd5a451162e241`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-046/test-plan.md`. External review artifact only; PM controls import.

All 6 stable cases / 3 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`
- `uv run --project services/api python scripts/ci_gate.py infra-unit`
- `node --import tsx --test --test-reporter=junit test/*.test.ts (cwd: infra)`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-046-PREVIEW-001-01 | Ambient production values are present — - **GIVEN** a host or dotenv containing production API/OAuth configuration - **WHEN** the preview is prepared - **THEN** only explicit guest configuration enters its separate bundle. | PARTIAL |
| OTGD-046-PREVIEW-001-02 | An ordinary export also exists — - **GIVEN** dist and dist-preview from different modes - **WHEN** the preview starts - **THEN** the guest server uses only dist-preview and its matching manifest. | PARTIAL |
| OTGD-046-PREVIEW-002-01 | A correct private guest server is already running — - **GIVEN** matching prepared guest bytes/manifest on the forwarded port - **WHEN** post-start runs again - **THEN** it reuses the verified server without duplicate processes. | PASS |
| OTGD-046-PREVIEW-002-02 | A foreign service occupies the port — - **GIVEN** ordinary/unrelated HTTP 200 content or a missing guest export - **WHEN** post-start runs - **THEN** it refuses readiness and preserves the unrelated service. | PARTIAL |
| OTGD-046-PREVIEW-003-01 | A user has the supported service account — - **GIVEN** the reviewed branch and successful source-bound guest artifacts - **WHEN** the documented browser hosting steps are followed - **THEN** no local clone/build commands are needed to explore the fictional UI. | BLOCKED |
| OTGD-046-PREVIEW-003-02 | No hosting access exists — - **GIVEN** no managed forwarding capability, existing Codespace or Appetize credentials - **WHEN** delivery is reported - **THEN** it supplies setup/artifacts and concrete account steps without claiming a launched session. | PARTIAL |
