# OTGD-046 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/verified-release-and-browser-access/specs/fictional-browser-preview/spec.md`; SHA256 `1a331132cf6b66413d1705dc09d0c7f885b8fe1375ea72250dcd5a451162e241`.

6 cases, 3 requirements: BLOCKED 1, PARTIAL 4, PASS 1. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-046-PREVIEW-001-01 — PARTIAL

Ambient production values are present — - **GIVEN** a host or dotenv containing production API/OAuth configuration - **WHEN** the preview is prepared - **THEN** only explicit guest configuration enters its separate bundle.

Current proof: Build-preview source overrides API/OAuth/app environment with local unavailable.invalid guest configuration and EXPO_NO_DOTENV1; executed browser has no external calls.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/hosted-preview.spec.ts::standalone fictional guest UI saves a check with zero account, upload, camera or Bluetooth calls and reload clears browser records` — file SHA `8862cec87ea3ab0121502d9d5a6da7faca0d70a5dab77b4914f2448ee5659e1d`, line 3; 4 current observation(s).
- `apps/mobile/tests/hosted-preview.test.ts::hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service` — file SHA `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb`, line 11; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/hosted-preview.xml` — SHA256 `374044d14f7d671489e6a5e364841c09bbff43fc2ec9a338e00e74139b465f6c`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/hosted-preview.xml` — SHA256 `374044d14f7d671489e6a5e364841c09bbff43fc2ec9a338e00e74139b465f6c`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/hosted-preview.xml` — SHA256 `c416ab04fd7865c331eb9dfb7287e5f3d8933e422590fa2ddce38c7905702434`.

Exact unproved clause(s):

- No current test injects ambient production env/dotenv then inspects every exported bundle/manifest for exclusive guest values; source override plus clean build is narrower than hostile-ambient scenario.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA b3cd46bc8fc38ff19eacbe57811b8a4f511d4da08d1841c21c278284bf86154a. Actual current source and raw evidence supply this disposition.

## OTGD-046-PREVIEW-001-02 — PARTIAL

An ordinary export also exists — - **GIVEN** dist and dist-preview from different modes - **WHEN** the preview starts - **THEN** the guest server uses only dist-preview and its matching manifest.

Current proof: Preview hook fixture uses dist-preview and matching manifest; source-only preparation hashes source/output and rejects drift.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_codespaces_preview.py::test_current_export_is_accepted_and_repeat_start_reuses_only_matching_guest` — file SHA `e604e7fc0a6fa84e329ff5baa9127c9e14c2b4fe13af7c5c8d01b13380f50691`, line 136; 1 current observation(s).
- `infra/test/test_codespaces_preview.py::test_changed_export_tracked_source_and_new_source_require_repreparation` — file SHA `e604e7fc0a6fa84e329ff5baa9127c9e14c2b4fe13af7c5c8d01b13380f50691`, line 153; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Current fixture has only dist-preview, not distinct ordinary dist plus guest dist-preview. Need both modes with distinct bytes and actual server response path/manifest assertion.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4c1c9dc1cb4e344b0eaeed77b938d5c95d411df067e4c03cf0f53434511ae0ea. Actual current source and raw evidence supply this disposition.

## OTGD-046-PREVIEW-002-01 — PASS

A correct private guest server is already running — - **GIVEN** matching prepared guest bytes/manifest on the forwarded port - **WHEN** post-start runs again - **THEN** it reuses the verified server without duplicate processes.

Current proof: Real hook subprocess probes a private fixture HTTP server, repeat start exits0, ready rechecks and no server.pid/new process recorded. Exact export bytes/manifest are checked by actual hook, not generic HTTP200.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_codespaces_preview.py::test_current_export_is_accepted_and_repeat_start_reuses_only_matching_guest` — file SHA `e604e7fc0a6fa84e329ff5baa9127c9e14c2b4fe13af7c5c8d01b13380f50691`, line 136; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 62f42ae8e9954eecc3e7e7a00989fd94f02a5999fc74a19871a1e2fda5882c0a. Actual current source and raw evidence supply this disposition.

## OTGD-046-PREVIEW-002-02 — PARTIAL

A foreign service occupies the port — - **GIVEN** ordinary/unrelated HTTP 200 content or a missing guest export - **WHEN** post-start runs - **THEN** it refuses readiness and preserves the unrelated service.

Current proof: Actual foreign HTTP200 fixture is refused with unexpected-content exit1; original server remains queryable and no new server.pid. Non-guest manifest, drift, redirect and bounded oversized probes reject.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_codespaces_preview.py::test_generic_http_200_is_not_reused_or_stopped_by_startup` — file SHA `e604e7fc0a6fa84e329ff5baa9127c9e14c2b4fe13af7c5c8d01b13380f50691`, line 183; 1 current observation(s).
- `infra/test/test_codespaces_preview.py::test_non_guest_marker_cannot_be_prepared_or_admitted` — file SHA `e604e7fc0a6fa84e329ff5baa9127c9e14c2b4fe13af7c5c8d01b13380f50691`, line 177; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Missing guest export alternative is not directly tested by deleting dist-preview before post-start; admission source exists but this negative is not bound to an executed assertion.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 6ed7d05f398a7c6735db3e71243fb73252571b99d6c7dac2ce0ffd1590833444. Actual current source and raw evidence supply this disposition.

## OTGD-046-PREVIEW-003-01 — BLOCKED

A user has the supported service account — - **GIVEN** the reviewed branch and successful source-bound guest artifacts - **WHEN** the documented browser hosting steps are followed - **THEN** no local clone/build commands are needed to explore the fictional UI.

Current proof: Reviewed setup/docs and source-bound guest build are available; local exported browser UI is exercised.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/hosted-preview.spec.ts::standalone fictional guest UI saves a check with zero account, upload, camera or Bluetooth calls and reload clears browser records` — file SHA `8862cec87ea3ab0121502d9d5a6da7faca0d70a5dab77b4914f2448ee5659e1d`, line 3; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/hosted-preview.xml` — SHA256 `374044d14f7d671489e6a5e364841c09bbff43fc2ec9a338e00e74139b465f6c`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/hosted-preview.xml` — SHA256 `374044d14f7d671489e6a5e364841c09bbff43fc2ec9a338e00e74139b465f6c`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/hosted-preview.xml` — SHA256 `c416ab04fd7865c331eb9dfb7287e5f3d8933e422590fa2ddce38c7905702434`.

Exact unproved clause(s):

- Actual supported hosting account/Codespace/Appetize session and documented no-local-clone user path are unexecuted; no authorized external hosting session is inferred.

Prerequisite/evidence type: independent_prerequisite_or_exact_scenario_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 0a5fb7e3f92c9523aa7a67bb4f77fdb5e3fdf66ee5d37e1fef134246623c65b6. Actual current source and raw evidence supply this disposition.

## OTGD-046-PREVIEW-003-02 — PARTIAL

No hosting access exists — - **GIVEN** no managed forwarding capability, existing Codespace or Appetize credentials - **WHEN** delivery is reported - **THEN** it supplies setup/artifacts and concrete account steps without claiming a launched session.

Current proof: Report already distinguishes exported local browser artifacts from absent external hosted session and documents setup steps.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- This delivery-report criterion needs PM final artifact/setup report review at actual handoff; no test symbol can establish the factual absence/presence of user hosting access or launch. No launched session is claimed here.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 2483c8accb378fbeecaa401b8cce2d11d8c9998f8a97dec8ab5cb760efa5933b. Actual current source and raw evidence supply this disposition.

