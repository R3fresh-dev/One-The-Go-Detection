# OTGD-014 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/cloud-deployment-customer-access/specs/cloud-browser-delivery/spec.md`; SHA256 `735f76493e8188925c157347dc22b0a2acad4cb76721f2ea8a7f324629631855`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-014/test-plan.md`. External review artifact only; PM controls import.

All 16 stable cases / 8 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`
- `uv run --project services/api python scripts/ci_gate.py infra-unit`
- `node --import tsx --test --test-reporter=junit test/*.test.ts (cwd: infra)`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-014-WEB-DEP-001-01 | Customer opens the published HTTPS origin — - **GIVEN** an admitted published application artifact - **WHEN** a customer opens WebOrigin - **THEN** CloudFront serves the application without public S3 access or credentials in the URL. | PARTIAL |
| OTGD-014-WEB-DEP-001-02 | Caller requests the bucket directly — - **GIVEN** an anonymous caller without distribution authority - **WHEN** it requests an S3 asset - **THEN** bucket policy does not grant public asset access. | PARTIAL |
| OTGD-014-WEB-DEP-002-01 | Customer opens a history deep link — - **GIVEN** published index.html - **WHEN** GET /history reaches the distribution - **THEN** the actual application entry point is returned. | PARTIAL |
| OTGD-014-WEB-DEP-002-02 | A missing script is requested — - **GIVEN** no matching .js asset - **WHEN** the browser requests that asset - **THEN** an origin error is preserved rather than returning a successful HTML body. | PARTIAL |
| OTGD-014-WEB-DEP-003-01 | QA and production are opened together — - **GIVEN** separate approved account deployments - **WHEN** both applications open - **THEN** each uses its own identity/API and QA remains visibly identified. | PARTIAL |
| OTGD-014-WEB-DEP-003-02 | A host environment attempts to override identity — - **GIVEN** conflicting APP/EXPO_PUBLIC/EAS inputs on the build host - **WHEN** the reviewed artifact builds - **THEN** the explicit deployed identity controls the bundle and a mismatching output fails verification. | PARTIAL |
| OTGD-014-WEB-DEP-004-01 | The reviewed artifact is published — - **GIVEN** matching signed service/web records, archive and deployed identity - **WHEN** publication is admitted - **THEN** exact file SHA-256/size/path/type and runtime bindings verify before upload. | PASS |
| OTGD-014-WEB-DEP-004-02 | An archive is altered after approval — - **GIVEN** a replaced file, duplicate entry or foreign identity - **WHEN** the artifact is verified - **THEN** publication fails before any byte is uploaded. | PASS |
| OTGD-014-WEB-DEP-005-01 | A normal Expo export is packaged — - **GIVEN** reviewed HTML, JavaScript, metadata and supported assets - **WHEN** limits hold - **THEN** a deterministic ZIP and canonical manifest are created. | PARTIAL |
| OTGD-014-WEB-DEP-005-02 | Export contains a secret or traversal path — - **GIVEN** .env, ../, absolute paths or a symlink - **WHEN** packaging or archive admission occurs - **THEN** the artifact is rejected. | PASS |
| OTGD-014-WEB-DEP-006-01 | An identical approved release is retried — - **GIVEN** existing same-prefix identical bytes - **WHEN** publication repeats - **THEN** those bytes verify and are preserved. | PARTIAL |
| OTGD-014-WEB-DEP-006-02 | A dependency conflicts or fails — - **GIVEN** a different existing file or failed upload - **WHEN** publication runs - **THEN** it fails before committing index.html or reporting publication success. | PASS |
| OTGD-014-WEB-DEP-007-01 | Public transport probes execute — - **GIVEN** a published release - **WHEN** index.html is retrieved over HTTPS - **THEN** byte integrity and required security headers verify. | PARTIAL |
| OTGD-014-WEB-DEP-007-02 | The response lacks its security policy — - **GIVEN** missing CSP/HSTS/no-sniff/frame denial - **WHEN** public verification runs - **THEN** deployment exits nonzero without a verified-access receipt. | PARTIAL |
| OTGD-014-WEB-DEP-008-01 | A customer experiments in the browser — - **GIVEN** the actual shared web application - **WHEN** a guest or authorized customer uses its UI - **THEN** browser storage/hardware limits and fictional data remain explicit. | PASS |
| OTGD-014-WEB-DEP-008-02 | A deployment command succeeds — - **GIVEN** only public HTTPS and worker health were checked - **WHEN** the receipt is written - **THEN** it does not claim signed-in browser, real-device, App Store or clinical validation. | PASS |
