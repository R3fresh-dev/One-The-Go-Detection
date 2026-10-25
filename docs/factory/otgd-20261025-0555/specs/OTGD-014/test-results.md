# OTGD-014: verification results

Canonical: `openspec/changes/cloud-deployment-customer-access/specs/cloud-browser-delivery/spec.md`; SHA-256 `735f76493e8188925c157347dc22b0a2acad4cb76721f2ea8a7f324629631855`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Owner: `/root/verification`; OpenAI `gpt-6.1-sol/high` requested in PM dispatch; effective model identifier not independently exposed inside this worker. Scope: verification planning and static source inspection only. Relevant acknowledged decisions: D-001–005 v1 and D-006 v3; superseded D-006 v1/v2 retained as history. Execution candidate is not frozen.

Result: **NOT_RUN**. 8 individually identified requirements and 16 canonical acceptance cases are planned in `test-plan.md`. No current-source runtime suite, browser, native, firmware, live-dependency or performance result is claimed by this document. No historical evidence is transferred.

| Evidence class | Actual activity / outcome | Status |
|---|---|---|
| Planning inspection | Read canonical requirements/scenarios and shared contracts; indexed existing test symbols, CI gates and workflow commands. Source hashes appear in test-plan.md and shared report. This is not a passing acceptance test. | EXECUTED inspection only |
| Related automated checks | Commands and named assertions planned; no execution authorized in this assignment. Exit code, execution timestamp and artifact hash therefore absent. | NOT_RUN |
| Complete criterion coverage | Every case requires full acceptance assertions; related symbol matching is not proof of complete coverage. No-match cases are explicitly identified in the plan. | NOT_RUN |
| Browser/native/firmware/real dependencies/performance | Scope-specific prerequisites and commands in plan/shared report; no substitution from unit mocks or historical CI. | NOT_RUN |
| Physical/scientific/release qualification | No actual participant/device/study/assay/deployment/store evidence adopted; external approvals remain separate. | BLOCKED where applicable |

## Current case results

All stable case IDs in test-plan.md are NOT_RUN, except explicitly external-only cases which are BLOCKED on named acceptance evidence. On execution replace this aggregate with one result row per affected case, retaining command/procedure, environment, UTC time, observed outcome, exit code, evidence path/hash and exact candidate/test bindings. Do not turn expected THEN statements into observed results.

No completion, engineering/product signoff or council PASS follows from this planning record.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

Final-candidate acceptance remains **NOT_RUN**; actual focused author executions are preserved below separately and do not establish this whole dossier PASS. Source/content changes after a focused run require fresh admission and affected reruns.

No new focused execution is adopted into this dossier in this audit. New UI/permissions/live/worker sources are WIP until author release and final bound execution; baseline firmware evidence retains its separate source/qualification limits.

Independent source assertion audits for this dossier: Authenticated ordinary-web live test source audit. Full assertion/limit details are in test-plan.md.


## Completed historical baseline semantic audit

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`: all 16 stable cases for this dossier were individually adjudicated against actual assertion bodies and named raw evidence. Counts: `{"PARTIAL": 10, "PASS": 6}`. The complete case rows, exact remaining clauses and evidence references are in [this dossier's audit index](../../reports/acceptance-baseline-28e0729/OTGD-014-cases.md); full structured bodies and hash bindings are preserved in [acceptance-evidence.zip](../../reports/acceptance-baseline-28e0729/acceptance-evidence.zip). Archive SHA256 `89804264880c9a8e7676fb232eff570ff47921ec74cf11596400329ceb641ff8` was read back and all67member hashes matched.

These are historical scoped decisions, not current replacement acceptance. A PARTIAL case does not automatically establish a production defect or absent test; exact shared assertion evidence and unavailable external prerequisites remain distinct. Current canonical SHA256 at this checkpoint is `735f76493e8188925c157347dc22b0a2acad4cb76721f2ea8a7f324629631855`. Preserve the old candidate's canonical hash in the archived row. Current corrections require fresh frozen-source gates, affected case binding and independent confirmations; final approval remains pending.


## Final corrected source evidence — e89897cc852a

# OTGD-014 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/cloud-deployment-customer-access/specs/cloud-browser-delivery/spec.md`; SHA256 `735f76493e8188925c157347dc22b0a2acad4cb76721f2ea8a7f324629631855`.

16 cases, 8 requirements: PARTIAL 10, PASS 6. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-014-WEB-DEP-001-01 — PARTIAL

Customer opens the published HTTPS origin — - **GIVEN** an admitted published application artifact - **WHEN** a customer opens WebOrigin - **THEN** CloudFront serves the application without public S3 access or credentials in the URL.

Current proof: Publication accepts mocked enabled private one-origin OAC distribution, verifies stored bytes and HTTPS probe verifies fixture index.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_publish_checks_actual_private_origin_and_commits_entrypoint_last` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 192; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_https_asset_deep_link_readiness_checks_do_not_claim_signed_in_acceptance` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 233; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “CloudFront serves application without public S3 access or credentials in URL”: no admitted deployment/actual CloudFront GET/private-S3 denial execution; HTTP/CloudFront/S3 are doubles.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 56f94a4aeeadd1107a1a5153d214042b0296a4868208fa7ab1ccb63ad05790fb. Actual current source and raw evidence supply this disposition.

## OTGD-014-WEB-DEP-001-02 — PARTIAL

Caller requests the bucket directly — - **GIVEN** an anonymous caller without distribution authority - **WHEN** it requests an S3 asset - **THEN** bucket policy does not grant public asset access.

Current proof: Admission rejects missing OAC before put_object; inspected CDK synth source blocks public bucket policy and permits exact CloudFront source ARN.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_publish_checks_actual_private_origin_and_commits_entrypoint_last` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 192; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “anonymous caller ... requests S3 asset ... bucket policy does not grant public access”: no actual anonymous direct-S3 access attempt or deployed policy evidence. Synthesized policy source is not deployed IAM execution.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 57bb14fb8aa670b171ae8a2e97f8913a4a5aed5e533a0073a7b59ab32a432344. Actual current source and raw evidence supply this disposition.

## OTGD-014-WEB-DEP-002-01 — PARTIAL

Customer opens a history deep link — - **GIVEN** published index.html - **WHEN** GET /history reaches the distribution - **THEN** the actual application entry point is returned.

Current proof: MockTransport serves /history exact index bytes and production verify_access accepts them; inspected CDK function source rewrites extensionless GET navigation only.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_https_asset_deep_link_readiness_checks_do_not_claim_signed_in_acceptance` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 233; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “GET /history reaches distribution ... actual entry point returned”: mock response supplies entry directly; no actual deployed CloudFront navigation execution.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4c2211fc23372035f3cec9b1a392762892b95eb3abf851b0867d3be4d9dea7df. Actual current source and raw evidence supply this disposition.

## OTGD-014-WEB-DEP-002-02 — PARTIAL

A missing script is requested — - **GIVEN** no matching .js asset - **WHEN** the browser requests that asset - **THEN** an origin error is preserved rather than returning a successful HTML body.

Current proof: MockTransport missing-script sentinel404 is accepted by production probe; inspected CDK function source preserves extensioned asset path.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_https_asset_deep_link_readiness_checks_do_not_claim_signed_in_acceptance` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 233; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “origin error preserved rather than successful HTML”: existing probe fixture returns404 itself; no executed negative response200/HTML sentinel case proving deployer rejection, nor actual CDN missing-script response.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 1db7d7836345d3a4bb33b686305aa08f4989328bb19000d572606c4e15b89e89. Actual current source and raw evidence supply this disposition.

## OTGD-014-WEB-DEP-003-01 — PARTIAL

QA and production are opened together — - **GIVEN** separate approved account deployments - **WHEN** both applications open - **THEN** each uses its own identity/API and QA remains visibly identified.

Current proof: QA/prod build-orchestration double serializes each explicit environment/API/issuer into synthetic app.js; --clear required twice; host secrets removed.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_each_signed_environment_export_rebuilds_stale_hosted_metro_cache` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 85; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_browser_build_environment_retains_transport_settings_without_deploy_credentials` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 42; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “both applications open ... own identity/API and QA visibly identified”: subprocess emits synthetic JS, not actual Expo browser apps; no two deployed origins/customer UI identity-label test.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA e41b9bb18d6a11d026c780823f7223101a29b27b2f4c6f161495eccf01be7acc. Actual current source and raw evidence supply this disposition.

## OTGD-014-WEB-DEP-003-02 — PARTIAL

A host environment attempts to override identity — - **GIVEN** conflicting APP/EXPO_PUBLIC/EAS inputs on the build host - **WHEN** the reviewed artifact builds - **THEN** the explicit deployed identity controls the bundle and a mismatching output fails verification.

Current proof: Explicit public identity overwrites hostile host EXPO values; build clears modeled Metro cache; signed envelope runtime mismatch against output ClientId rejects.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_browser_build_environment_retains_transport_settings_without_deploy_credentials` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 42; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_each_signed_environment_export_rebuilds_stale_hosted_metro_cache` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 85; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_signature_source_environment_runtime_and_archive_bytes_are_bound` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 149; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- A generated compiled JS bundle that ignores the selected environment identity tuple must fail output verification. Current OAuth pins, clean source rebuild and Metro cache clearing are asserted; the signed runtime metadata and fake exporter do not directly prove detection of a mismatching compiled bundle. This is an evidence limit, not a newly reproduced deployment defect.

Prerequisite/evidence type: software_compiled_artifact_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA ca6ac7269a6c3b99752c1f62e5e9f052359b725b48bdc79ac884debfa8ccd339. Actual current source and raw evidence supply this disposition.

## OTGD-014-WEB-DEP-004-01 — PASS

The reviewed artifact is published — - **GIVEN** matching signed service/web records, archive and deployed identity - **WHEN** publication is admitted - **THEN** exact file SHA-256/size/path/type and runtime bindings verify before upload.

Current proof: Real Ed25519-signed web record, canonical manifest and normal ZIP verified; returned exact index/app files; source/account/environment/image/runtime mismatch denied. Production verify reuses one bounded archive snapshot, file_record checks exact path/type/size/SHA before admitted files can enter publish. Software admission, not actual public upload.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_signature_source_environment_runtime_and_archive_bytes_are_bound` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 149; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 8f4c183752912637c768c1fcddd2e6cd4dfbf09a65f111120909ce0f213f55fb. Actual current source and raw evidence supply this disposition.

## OTGD-014-WEB-DEP-004-02 — PASS

An archive is altered after approval — - **GIVEN** a replaced file, duplicate entry or foreign identity - **WHEN** the artifact is verified - **THEN** publication fails before any byte is uploaded.

Current proof: Real signed archive mutation/injected member, duplicate index and foreign deployed identity raise Gate in offline verifier before returning files. Verification does not call cloud uploader, so these failures precede byte publication.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_signature_source_environment_runtime_and_archive_bytes_are_bound` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 149; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_public_asset_types_paths_symlinks_and_duplicate_zip_entries_are_rejected` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 181; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 9709f5b8ba8cad0dacad676cfd145757e84360976ccbaa37efc708f22c7830ee. Actual current source and raw evidence supply this disposition.

## OTGD-014-WEB-DEP-005-01 — PARTIAL

A normal Expo export is packaged — - **GIVEN** reviewed HTML, JavaScript, metadata and supported assets - **WHEN** limits hold - **THEN** a deterministic ZIP and canonical manifest are created.

Current proof: Real package() creates and verifies ZIP/canonical manifest for index.html+app.js fixture; source uses sorted paths/fixed ZIP timestamps.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_signature_source_environment_runtime_and_archive_bytes_are_bound` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 149; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_each_signed_environment_export_rebuilds_stale_hosted_metro_cache` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 85; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “normal Expo ... metadata and supported assets ... deterministic ZIP”: exporter is subprocess double with two files; no repeated independent packaging byte-equality assertion or normal Expo metadata/asset fixture coverage. This is not a demonstrated nondeterminism bug.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 3d9059cdd4182a762ebb1483914c4ccda36990398cd68e7af095c600258f3fab. Actual current source and raw evidence supply this disposition.

## OTGD-014-WEB-DEP-005-02 — PASS

Export contains a secret or traversal path — - **GIVEN** .env, ../, absolute paths or a symlink - **WHEN** packaging or archive admission occurs - **THEN** the artifact is rejected.

Current proof: Direct file_record refuses traversal, absolute/backslash/double-separator paths, secret.env and source-map types; packaging symlink refused; duplicate archive entry refused. .env has no permitted suffix under inspected allowlist. Local artifact software proof.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_public_asset_types_paths_symlinks_and_duplicate_zip_entries_are_rejected` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 181; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA f2880e40f70785e93b8c2e26ce4e0d407e80620b42a8d0092a5260a8b5682287. Actual current source and raw evidence supply this disposition.

## OTGD-014-WEB-DEP-006-01 — PARTIAL

An identical approved release is retried — - **GIVEN** existing same-prefix identical bytes - **WHEN** publication repeats - **THEN** those bytes verify and are preserved.

Current proof: Initial create-if-absent publication and returned-byte verification executed on S3 double; conflicting existing bytes rejected.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_conflicting_immutable_object_and_asset_upload_failure_block_entrypoint` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 209; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_publish_checks_actual_private_origin_and_commits_entrypoint_last` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 192; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “existing same-prefix identical bytes ... retry verifies/preserves”: no positive PreconditionFailed/412 retry with identical existing bytes and unchanged version/write state assertion. Hosted-preview service upload is a different transport.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 2b89b110bdf63637600d2a6b9a1f5d47020160712e84c46d866eae0ea6d4bfcf. Actual current source and raw evidence supply this disposition.

## OTGD-014-WEB-DEP-006-02 — PASS

A dependency conflicts or fails — - **GIVEN** a different existing file or failed upload - **WHEN** publication runs - **THEN** it fails before committing index.html or reporting publication success.

Current proof: Existing conflicting immutable object raises Gate; dependency put failure occurs at app.js before index, publish raises and no invalidation called. Production loop orders index last; no publication success returned.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_conflicting_immutable_object_and_asset_upload_failure_block_entrypoint` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 209; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 9023b0a401636f314a647908e65e3f0924ff7b9f1677ce231094a2faaeedac21. Actual current source and raw evidence supply this disposition.

## OTGD-014-WEB-DEP-007-01 — PARTIAL

Public transport probes execute — - **GIVEN** a published release - **WHEN** index.html is retrieved over HTTPS - **THEN** byte integrity and required security headers verify.

Current proof: Mock HTTPS probe validates fixture index hash/size and supported headers; header parser accepts correct/reordered exact policy.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_https_asset_deep_link_readiness_checks_do_not_claim_signed_in_acceptance` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 233; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_public_policy_rejects_missing_broadened_or_ambiguous_csp_and_transport` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 291; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “published release ... retrieved over HTTPS”: MockTransport provides no real TLS/public-origin/header observation; actual CloudFront/public release prerequisite unexecuted.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8c2628d8fc83bdb7e383998a4a45547dc1dc4ee7a297531f70fa3eb800ad9793. Actual current source and raw evidence supply this disposition.

## OTGD-014-WEB-DEP-007-02 — PARTIAL

The response lacks its security policy — - **GIVEN** missing CSP/HSTS/no-sniff/frame denial - **WHEN** public verification runs - **THEN** deployment exits nonzero without a verified-access receipt.

Current proof: Bad CSP/HSTS/frame/referrer policy rejected; unprotected deep-link fixture makes verify_access raise.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_public_policy_rejects_missing_broadened_or_ambiguous_csp_and_transport` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 291; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_navigation_cannot_omit_required_policy_when_index_is_secure` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 385; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “deployment exits nonzero without verified-access receipt”: helper exceptions are observed, not failing one-shot CLI/public-verification stage with nonzero exit and absent deployment.json assertion. Missing header fields themselves are not each exercised by this header mutation table.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 678c13891c97611e244a3dbd315f9f499c77d2c34ed19b4524ee26ba5ba6c8da. Actual current source and raw evidence supply this disposition.

## OTGD-014-WEB-DEP-008-01 — PASS

A customer experiments in the browser — - **GIVEN** the actual shared web application - **WHEN** a guest or authorized customer uses its UI - **THEN** browser storage/hardware limits and fictional data remain explicit.

Current proof: Actual browser shared app guest flow labels fictional/synthetic data, disables native reaction adapter, saves measurement-only null probability; reload returns to memory-only browser preview and explicit browser persistence limitation. No CloudFront/native/scientific qualification inferred.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).
- `apps/mobile/e2e/mobile.spec.ts::profile errors remain actionable and browser reload never pretends encrypted persistence` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 227; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 5231c6be6fcd8a9d10842f81f3bf5f63d07e8c57d622c1650132e9eceb55507d. Actual current source and raw evidence supply this disposition.

## OTGD-014-WEB-DEP-008-02 — PASS

A deployment command succeeds — - **GIVEN** only public HTTPS and worker health were checked - **WHEN** the receipt is written - **THEN** it does not claim signed-in browser, real-device, App Store or clinical validation.

Current proof: Probe receipt explicitly authenticated_customer_acceptance=not_executed. Inspected orchestration receipt labels status public_transport_verified and cloud_operational_acceptance not_inferred; fixed probe result/receipt makes no native/AppStore/clinical validation claim. This judges receipt software semantics only.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_https_asset_deep_link_readiness_checks_do_not_claim_signed_in_acceptance` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 233; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA a30b80ae892968cd55e6234de53aa0e46645b749cef582278b991295d1712f1f. Actual current source and raw evidence supply this disposition.
