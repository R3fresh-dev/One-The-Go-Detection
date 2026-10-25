# OTGD-047 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md`; SHA256 `b5523be8de175f257dda911b52b94732ae4e5e838b49cd9c38bea7802d0670c4`.

37 cases, 18 requirements: BLOCKED 5, NOT_RUN 1, PARTIAL 20, PASS 11. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-047-STORE-001-01 — PASS

A real store candidate is planned — - **GIVEN** the selected QA-store or production profile - **WHEN** its platform configuration is resolved - **THEN** device artifact type, environment/package and version policy are explicit.

Current proof: Pure plan tests inspect both qa-store/production AAB/deviceIPA profiles, environment, remote version source/autoIncrement, committed source and preview=false.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_plan_is_pure_and_profiles_cannot_publish_automatically` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 163; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 8ed62b482775f795dc6d0ddf48ea767b70916861ccc738f0a693dbf9687cd268. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-001-02 — PARTIAL

A guest archive is offered for store release — - **GIVEN** a local/guest/simulator artifact or incompatible package - **WHEN** store admission runs - **THEN** it refuses rather than relabeling the artifact.

Current proof: Local/ambiguous configuration, hostedPreview marker, simulator build metadata and incompatible Android package are rejected by actual software admission helpers.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_release_config_rejects_local_guest_or_ambiguous_targets` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 242; 85 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_exact_cloud_metadata_and_embedded_public_origins_bind_store_build` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 303; 10 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_actual_manifest_policy_rejects_guest_debug_cleartext_sdk_and_path_traversal` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 401; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- A full local/guest archive through the store execute/admission path must assert refusal before provider mutation; isolated configuration/manifest throws do not prove that complete operation boundary.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f890ef85a2ae76a3dd2c3d97cf8c91253bc3b16ceee53f7c4e96b7e50f2ef2ed. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-002-01 — PARTIAL

Cloud identity matches the compiled app — - **GIVEN** current project metadata and admitted cloud outputs including the exact callback - **WHEN** build/submit admission runs - **THEN** the candidate uses those exact public identity values.

Current proof: Exact public project/config/origin/callback checks execute under fictional provider/cloud responses, with mismatch rejection and preservation of explicit configured identities.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_exact_cloud_metadata_and_embedded_public_origins_bind_store_build` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 303; 10 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_pinned_tool_package_integrity_and_actual_public_eas_variable_scope` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 767; 5 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_backend_admission_rechecks_signed_release_actual_running_image_and_live_native_callback` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 1168; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Genuine current authenticated Expo project/backend outputs have not been observed; fixtures cannot bind a real compiled store app to a live cloud identity.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 66e89d48062614dc21634722f1a369ad65445158cff900522ab5b8bd4ad676b6. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-002-02 — PARTIAL

Production lists the wrong redirect — - **GIVEN** otgd-prod://oauth/callback or a foreign project/backend/callback - **WHEN** admission checks the production package - **THEN** it fails before build or submission.

Current proof: Production otgd-prod callback, wrong runtime image and incomplete rollout are rejected by backend helper before it returns admission.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_backend_admission_rechecks_signed_release_actual_running_image_and_live_native_callback` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 1168; 5 current observation(s).
- `infra/test/test_store_inputs.py::test_external_paths_and_invalid_store_config_leave_no_staging` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 314; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Execute build/submit with each foreign project/backend/callback response and assert zero provider build/upload commands; standalone verify_backend tests do not observe that end-to-end ordering.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0ecca6245d18455b5f75d2966136080586a142605b2298ed4f3db7079f262ebc. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-003-01 — PARTIAL

Exact source and genuine release evidence agree — - **GIVEN** the allowed trusted GitHub release event and current signed backend/QA binding - **WHEN** source is staged outside the development checkout - **THEN** the provider receives only the admitted immutable tree.

Current proof: Actual temporary Git isolation preserves committed revision, excludes untracked file and refuses dirty source; build path refuses missing backend authority.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_clean_isolated_source_preserves_exact_git_revision_and_excludes_untracked_files` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 934; 5 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_no_backend_release_no_new_store_job_and_immutable_output_refuses_reuse` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 726; 5 current observation(s).
- `infra/test/test_store_inputs.py::test_build_stages_selected_signer_and_backend_scope_without_store_credentials` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 489; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Trusted release-event/gate/QA admission and isolated staged tree must be composed with the provider call, asserting only that exact tree/locks reach upload; flow substitutes isolated_source and backend verifier.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA a6922e23ffbb0c8d568b45d0f1648ce318f3d8cb7b0740546dc16e9113c2ab17. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-003-02 — PARTIAL

A local JSON or stale successful run is substituted — - **GIVEN** missing jobs, wrong commit/project, unsupported release event or edited evidence - **WHEN** build/submit admission runs - **THEN** no provider mutation occurs.

Current proof: Gate validator rejects missing/failed/skipped/canceled/old-attempt/wrong-commit jobs; backend failure prevents store build command.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_provenance.py::test_local_claims_cannot_replace_missing_failed_skipped_or_old_attempt_jobs` — file SHA `996ead63b1f3ae3999aa31d81e3de893bbc50b62bfaac6e2a69f88a968d5f6a1`, line 115; 1 current observation(s).
- `infra/test/test_provenance.py::test_latest_attempt_requires_every_nested_job_and_aggregate` — file SHA `996ead63b1f3ae3999aa31d81e3de893bbc50b62bfaac6e2a69f88a968d5f6a1`, line 102; 1 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_no_backend_release_no_new_store_job_and_immutable_output_refuses_reuse` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 726; 5 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_backend_admission_rechecks_signed_release_actual_running_image_and_live_native_callback` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 1168; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Store build/submit operation must integrate unsupported release-event/edited gate evidence and assert no provider mutation for all cases; gate and store tests currently exercise separate helper boundaries.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 58f5786af85c83766e2718d61b2b11661eec4e588bc6ce3885aca0698c0bd35b. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-004-01 — PASS

An operator reviews the intended command — - **GIVEN** a valid nonsecret store configuration - **WHEN** plan runs without service credentials - **THEN** the explicit stages and external requirements are returned without mutation.

Current proof: Pure plan fails the test on source/network/tool/credential reads, returns plan_only/13required gates/public_release=false; wrapper stages only private nonsecret plan inputs.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_plan_is_pure_and_profiles_cannot_publish_automatically` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 163; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 1e859112ababafe9fc54319e78b55126d21e17145fb6ceccb1fb2e26aec7faf2. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-004-02 — PARTIAL

An invalid or ambiguous target is supplied — - **GIVEN** opposite environment, missing platform or placeholder identity - **WHEN** plan runs - **THEN** validation fails before a provider command.

Current proof: Wrong environment, placeholder IDs, invalid selected platform and missing platform in staged command are rejected with no child command or leftover staging.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_release_config_rejects_local_guest_or_ambiguous_targets` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 242; 85 current observation(s).
- `infra/test/test_store_inputs.py::test_external_paths_and_invalid_store_config_leave_no_staging` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 314; 1 current observation(s).
- `infra/test/test_store_inputs.py::test_run_rejects_duplicate_unknown_foreign_and_unscoped_arguments` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 989; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Direct plan action must exercise all opposite-environment/missing-platform/placeholder cases and assert provider command never launched; current checks span config parsing and wrapper-run guards.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 3b49bc4f13fd5972f12bb9e84110971e60f7511bc5f84fbfdec72300f0b1e559. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-005-01 — PARTIAL

Approved credentials and exact CLI are available — - **GIVEN** verified pinned tooling and scoped genuine provider credentials - **WHEN** build/submission starts - **THEN** the child receives only its required authentication and transport.

Current proof: Build environment excludes AWS/GitHub/database/preload/Expo secrets while preserving proxy/CA; CLI fake boundary receives token only for EAS; selected platform credential is0600 and opposite key absent.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_tool_environment_preserves_transport_but_never_builds_with_service_secrets` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 268; 5 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_pinned_tool_package_integrity_and_actual_public_eas_variable_scope` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 767; 5 current observation(s).
- `infra/test/test_store_inputs.py::test_submit_stages_only_selected_platform_credential` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 683; 1 current observation(s).
- `infra/test/test_store_inputs.py::test_build_stages_selected_signer_and_backend_scope_without_store_credentials` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 489; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Actual credential-bearing child invocation must assert complete env whitelist for build versus submit, including no unrelated secrets; current separate helper tests do not inspect the complete real child environment.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8fe6cfb7ce25776517abc8c02bc69ddd2a3b51148fefbfdba4ab62968d70465d. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-005-02 — PARTIAL

Tooling or credential state is unavailable — - **GIVEN** a different CLI, missing genuine signing/account access or a Node preload - **WHEN** the operation starts - **THEN** it refuses or excludes the unapproved setting without inventing a build.

Current proof: Missing EXPO_TOKEN, changed archive/tree integrity, malformed platform credentials and Node preload exclusion are tested.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_pinned_tool_package_integrity_and_actual_public_eas_variable_scope` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 767; 5 current observation(s).
- `infra/test/test_store_inputs.py::test_platform_credentials_reject_wrong_scope_unknown_wrappers_and_bad_content` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 758; 1 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_tool_environment_preserves_transport_but_never_builds_with_service_secrets` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 268; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Wrong EAS version response and absent genuine signing/account access must be driven through execute with zero build receipt/provider build; current version stub always returns the expected version.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA a1a08fb103c8b2df6d85b6f66a89bccc7c731a5b400d5bb28e84ec744c5acd3e. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-006-01 — PARTIAL

The provider completes the selected build — - **GIVEN** matching official finished-build metadata - **WHEN** the completion receipt is written - **THEN** it identifies the actual build UUID/version and admitted project/source.

Current proof: FINISHED metadata validates expected ID, platform/source/package/version shape; flow writes a signed build-purpose receipt with not_submitted state.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_exact_cloud_metadata_and_embedded_public_origins_bind_store_build` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 303; 10 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_exact_build_inspection_then_explicit_draft_submission_and_status_have_signed_distinct_receipts` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 563; 10 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Completion receipt must explicitly assert returned buildUUID/version/project/source fields together; official provider observations and real signed output remain unexecuted.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8bf9a79cd788a5ac075ef51f95bca6fded3a9f09b90ede29e92f4b8e8e505709. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-006-02 — PARTIAL

Build execution merely starts — - **GIVEN** an accepted request with pending/failed/wrong-project output - **WHEN** completion is assessed - **THEN** no finished artifact or downloadable store app is claimed.

Current proof: IN_PROGRESS, wrong source/distribution/simulator/package/version and foreign owner metadata are refused by verify_build.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_exact_cloud_metadata_and_embedded_public_origins_bind_store_build` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 303; 10 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Failed status and wrong projectUUID need explicit operation tests asserting no finished receipt/artifact/download claim; pending metadata throw alone does not assert report/output behavior.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 693e765f31fb335f4b09ef32ae8fff0184b9803897b7ad9e94b402b83d8bd060. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-007-01 — BLOCKED

A genuine exact candidate is submitted — - **GIVEN** the current finished-build UUID and real matching store record - **WHEN** explicit submission is requested - **THEN** that exact candidate is sent and provider observations are recorded.

Current proof: Offline flow constructs exact --id BUILD with no latest/automaticTestFlight and queries submission metadata, then retains signed nonpublic receipt.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_exact_build_inspection_then_explicit_draft_submission_and_status_have_signed_distinct_receipts` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 563; 10 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_actual_submission_receipt_never_means_public_store_availability` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 428; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- No genuine authorized EAS/store submission is performed: real matching store record, provider access/signing credentials and explicit external-action authorization are prerequisites outside this read-only scope.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 1ba955fe6aca3cfc9afca751d960290e69c993e9296ada9b540caf978eace9d1. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-007-02 — PARTIAL

Another build is substituted — - **GIVEN** latest selection, a foreign UUID or altered receipt/metadata - **WHEN** submission admission runs - **THEN** it refuses before upload.

Current proof: Wrong buildUUID, signer/scope, byte-linked receipt, oldsource and foreign submittedBuild are rejected; normal command explicitly uses --id and never --latest.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_store_inputs.py::test_candidate_receipt_scope_signer_and_submission_reuse_are_checked` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 658; 1 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_actual_submission_receipt_never_means_public_store_availability` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 428; 5 current observation(s).
- `infra/test/test_store_inputs.py::test_signed_child_receipts_bind_original_build_bytes_and_logical_configuration` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 637; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Explicit --latest selector and altered finished official build metadata must be tested at submit operation boundary with an upload-call spy remaining zero.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8ec32089fb0d8b8553fd29d2ace5f6888aae8d813a6d39f5b5d2b5b92c867c17. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-008-01 — PASS

An upload request succeeds — - **GIVEN** a successful provider submission request - **WHEN** status is reported - **THEN** it reports only actual observed submission/processing evidence and no public-download claim.

Current proof: Both platform submission validators retain public_release=false/store_availability=not_verified; status flow records FINISHED while preserving not_verified and draft policy.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_exact_build_inspection_then_explicit_draft_submission_and_status_have_signed_distinct_receipts` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 563; 10 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_actual_submission_receipt_never_means_public_store_availability` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 428; 5 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_plan_is_pure_and_profiles_cannot_publish_automatically` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 163; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 63119e2091e6054267c52fa22a2847a4bd59d4f7a62a990182f0347825521f61. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-008-02 — PASS

Apple or Google has not approved delivery — - **GIVEN** processing/review/tester/enrollment or first-upload work remains - **WHEN** the operator asks for installation - **THEN** documentation names the required platform step without inventing a store URL or completed publication.

Current proof: Pinned runbook states unpublished status, Apple processing/TestFlight groups/external review/public review choices, Play draft enrollment/first-upload/release steps and no manufactured tester/listing URL.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/STORE_RELEASE.md::STATIC_store_prerequisites_and_public_availability` — file SHA `4aeff8438e3423721d93cc2f7fe3e9d4b4379804be7559877f278e737147f48b`, line 1; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/document-inspections/apps/mobile/STORE_RELEASE.md` — SHA256 `4aeff8438e3423721d93cc2f7fe3e9d4b4379804be7559877f278e737147f48b`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 4ec14c480af6f4a2de886ebdc347f6e49e3e17f24cc854fbf1d218b516f21bb5. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-009-01 — PARTIAL

A successful operation is retained — - **GIVEN** actual matching provider observations - **WHEN** a receipt is created - **THEN** it records the performed stage and identity without overwriting earlier evidence.

Current proof: Distinct signed build/submission/intent receipts and status preserve original signed bytes, intent identity and immutable output reuse rejection.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_exact_build_inspection_then_explicit_draft_submission_and_status_have_signed_distinct_receipts` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 563; 10 current observation(s).
- `infra/test/test_store_inputs.py::test_status_preserves_original_receipts_without_staging_private_credentials` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 619; 1 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_no_backend_release_no_new_store_job_and_immutable_output_refuses_reuse` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 726; 5 current observation(s).
- `infra/test/test_store_inputs.py::test_signed_child_receipts_bind_original_build_bytes_and_logical_configuration` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 637; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Assert every receipt's performed stage/platform/project/source/providerUUID/version against observed metadata and unchanged previous receipt bytes in one operation chain; current positive flow checks only a subset of fields.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA c61fafe5dd276d6b1e4953a66cc9f61886d735e7e1d82683ce353ee5e635cafa. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-009-02 — PARTIAL

An external stage fails — - **GIVEN** denied credentials, wrong metadata or failed build/upload - **WHEN** execution stops - **THEN** failure is explicit and earlier provider work is not falsely described as rolled back.

Current proof: Lost submit response raises explicit error, preserves original durable intent and no fabricated success output; retry cannot upload again.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_lost_submission_response_persists_exact_intent_and_reconciles_without_second_upload` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 597; 5 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_no_backend_release_no_new_store_job_and_immutable_output_refuses_reuse` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 726; 5 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_fsync_failure_leaves_fence_and_never_launches_store_upload` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 661; 10 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Denied credential/wrong metadata/failed upload after earlier successful provider work must assert nonzero/report text preserves unknown or completed earlier work and never claims rollback.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 392bc321a74f36ad6a188e6509922c8146ec6f8eb447fd20e699842f58a038f0. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-010-01 — BLOCKED

A genuine device candidate matches authority — - **GIVEN** the exact provider build bytes, reviewed signer and supported verifier - **WHEN** inspection executes - **THEN** the signed receipt binds its actual digest and observed native/configuration/signing metadata.

Current proof: Real JDK signature verification protects a fictional JAR and mocked-native inspections create scoped fixture receipts.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_android_signed_jar_integrity_and_trusted_upload_certificate_reject_changed_bytes` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 972; 5 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_ios_fixture_checks_actual_platform_identity_provisioning_and_runtime_tuple` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 1088; 5 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_exact_build_inspection_then_explicit_draft_submission_and_status_have_signed_distinct_receipts` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 563; 10 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- No genuine provider AAB/deviceIPA with independently reviewed platform signer is inspected; bundletool output and macOS code signing are substituted in the existing tests.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 317f320421ee656f9e200d435fef9290bb0abdd301f018e83be054fa11a3e124. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-010-02 — PARTIAL

Metadata describes a different binary — - **GIVEN** a simulator IPA, unsigned/foreign AAB, wrong package/version/backend/guest marker or different signer - **WHEN** binary inspection runs - **THEN** metadata alone cannot admit it and no submission occurs.

Current proof: Changed Android signature/signer/unsigned entries and guest/debug/cleartext/package manifest mutations reject; iOS debug/ad-hoc/unsupported host refuse.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_android_signed_jar_integrity_and_trusted_upload_certificate_reject_changed_bytes` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 972; 5 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_ios_fixture_checks_actual_platform_identity_provisioning_and_runtime_tuple` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 1088; 5 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_actual_manifest_policy_rejects_guest_debug_cleartext_sdk_and_path_traversal` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 401; 5 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_exact_cloud_metadata_and_embedded_public_origins_bind_store_build` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 303; 10 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Foreign Apple signer, simulator Mach-O/platform mismatch, backend/runtime mismatch and wrong native version need exact native archive mutations plus assertion no submit call; hosted-preview reverse-platform checks are unrelated.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4e60b7e3a069b8db0b8356a282147c4a25dbedfb840e7e3e2215a353aa21cfe0. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-011-01 — PARTIAL

The provider accepted a request before interruption — - **GIVEN** a durable signed intent and an uncertain CLI outcome - **WHEN** the operator supplies the actual submission UUID for reconciliation - **THEN** the tool queries that exact matching provider record without another upload.

Current proof: Durable signed intent survives lost response; reconciliation supplied UUID causes one original upload total and preserves exact intent bytes.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_lost_submission_response_persists_exact_intent_and_reconciles_without_second_upload` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 597; 5 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_submission_persists_signed_owner_only_fence_before_provider_call` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 621; 5 current observation(s).
- `infra/test/test_store_inputs.py::test_submit_reconciliation_requires_original_intent_and_exact_identifier` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 698; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- FakeEas submit:view returns same metadata regardless of argument; assert queried command UUID equals supplied original submissionUUID and rejects a mismatched returned UUID, not only that no second upload occurs.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 78858c4ebd06312f34bb66c451a3ca2ac28bffc36f4a20c99b3a9f6fd5fb4ae8. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-011-02 — PASS

The operator repeats an unknown upload without identity — - **GIVEN** an existing pending intent and no matching provider submission record - **WHEN** submission is retried - **THEN** it refuses duplicate mutation and preserves the uncertainty.

Current proof: Unknown first upload leaves intent/output-absent; second submit without submissionUUID raises earlier-submission error; original intent bytes unchanged and total submit calls remain one.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_lost_submission_response_persists_exact_intent_and_reconciles_without_second_upload` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 597; 5 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_fsync_failure_leaves_fence_and_never_launches_store_upload` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 661; 10 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA edc2446adb976ee0938f9a21bbe7c7e34da52c2b7422650d888595e35afcb9f9. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-012-01 — BLOCKED

A complete registered-upload candidate is supplied — - **GIVEN** an AAB with the expected upload certificate and all payload entries signed - **WHEN** actual signature and manifest inspection runs - **THEN** the admitted digest/package/version/signer are recorded.

Current proof: Actual JDK signs/verifies every meaningful fictional archive entry and trusted certificate digest; manifest/runtime policy is tested separately.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_android_signed_jar_integrity_and_trusted_upload_certificate_reject_changed_bytes` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 972; 5 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_actual_manifest_policy_rejects_guest_debug_cleartext_sdk_and_path_traversal` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 401; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- A real Android app bundle with independently registered upload certificate and actual pinned bundletool native manifest decoding is absent; fake manifest extraction cannot establish this genuine candidate scenario.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA eafe4d1016c9851070588869f52f359a65af6fd03557d2fb223e6b452e39049a. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-012-02 — PASS

Unsigned payload is appended to a signed archive — - **GIVEN** a previously signed JAR/AAB containing newly appended unsigned payload - **WHEN** jarsigner returns a general success with incomplete entry coverage - **THEN** admission still rejects the candidate before submission.

Current proof: Actual cryptographically signed JAR fixture gets an unsigned payload appended; inspect_android rejects unsigned entries despite generally successful signature verification; mutated signed bytes also reject.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_android_signed_jar_integrity_and_trusted_upload_certificate_reject_changed_bytes` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 972; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 9847d2fe3702279d38420fef3258c4fdc01d288a8dfd5a6efe28cd3089cf114b. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-013-01 — BLOCKED

A genuine store-signed device IPA is inspected — - **GIVEN** the independently expected Apple distribution identity and matching profile - **WHEN** actual macOS signing/platform inspection runs - **THEN** the device artifact and observed signing metadata bind the receipt.

Current proof: Bounded device Mach-O/plist/profile parser accepts a fictional envelope and denies debug/ad-hoc/unsupported host.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_ios_fixture_checks_actual_platform_identity_provisioning_and_runtime_tuple` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 1088; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Genuine Apple distribution certificate/profile and actual macOS codesign/security verification on a real deviceIPA have not executed; current subprocess outputs are mocked.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 9a330a245b8097cb95582130f10ecfa6faedb6e6c4da3a73b0837fbf6f2bd085. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-013-02 — PARTIAL

A simulator or unsupported signing path is used — - **GIVEN** an iOS simulator ZIP, foreign/development identity or unsupported verifier - **WHEN** admission executes - **THEN** no store upload or successful Apple-signing claim occurs.

Current proof: iOS fixture rejects get-task-allow debug, provisioned-device ad-hoc profile and unsupported Linux verifier.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_ios_fixture_checks_actual_platform_identity_provisioning_and_runtime_tuple` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 1088; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Explicit simulator Mach-O/platform, foreign distribution certificate/team and development identity mutations are not all tested through store admission with zero upload.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 10c1f03b4e4ecf36ae6ebe64f033b3ca7a7ae45c28f9788861e0b49c5c7fcbdf. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-014-01 — PARTIAL

Pinned verified CLI installation matches the lock — - **GIVEN** the reviewed exact EAS archive integrity and matching isolated toolchain tree - **WHEN** the provider CLI is executed - **THEN** that inspected installation supplies the command.

Current proof: Toolchain unit test binds verified archive contents, lock integrity, exact installed bin/run path and token-free npm install; six selected CLI calls use that path.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_pinned_tool_package_integrity_and_actual_public_eas_variable_scope` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 767; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Official pinned EAS package installation/real CLI execution is not established by a fictional tarball, replaced integrity constant and mocked command runner.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 473232489f848e3acc0afbc06bbc6b89cbf74b6c432b7e8e2cc15b82e2c5a16e. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-014-02 — PARTIAL

Execution selects different CLI bytes — - **GIVEN** changed package integrity, substituted tree or a separate unchecked fetch - **WHEN** toolchain admission runs - **THEN** no provider operation or credential-bearing CLI execution occurs.

Current proof: Altered tarball integrity and installed bin/run bytes are refused by integrity/tree verifiers.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_pinned_tool_package_integrity_and_actual_public_eas_variable_scope` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 767; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Drive substituted tree/wrong lock/unchecked-refetch through Eas construction and assert no credential-bearing CLI/provider command executes; current changed-tree case calls verifier directly.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA ae3a26efce88d907d7e633a4c6932382a724e602ecbcf63754a39e8415bb2c9e. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-015-01 — PARTIAL

A CLI child exceeds its deadline — - **GIVEN** an owned local process tree with scoped provider authentication - **WHEN** timeout or output overflow occurs - **THEN** the group is terminated/reaped and the unknown remote state is preserved.

Current proof: Real local spawned child stops before delayed side effect after output overflow; parent-exits-first orphan is stopped; finished-after-deadline rejects in mocked clock test.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_mobile_store_release.py::test_owned_tool_process_group_stops_spawned_child_on_bounded_failure` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 872; 5 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_owned_child_is_stopped_even_when_tool_parent_exits_before_cleanup` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 889; 5 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_completed_parent_is_still_rejected_after_original_monotonic_deadline` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 907; 5 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_lost_submission_response_persists_exact_intent_and_reconciles_without_second_upload` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 597; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Actual active-child timeout plus process reaping and signed unknown-remote-state preservation must be asserted together; output-overflow absence of side effect alone does not prove all terminal/reaping clauses.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 33cd9d3059ab8919dafc5e5f28bb8f7c709811328d43626cb55818d9feafe304. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-015-02 — NOT_RUN

Another local process is running — - **GIVEN** an unrelated process outside the owned group - **WHEN** provider cleanup runs - **THEN** that process remains untouched.

Current proof: Existing process tests launch only owned descendants; none creates an independent unrelated process.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Launch unrelated process outside owned group, force timeout/overflow cleanup and assert it remains alive/untouched; this is unblocked host software work.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA 0e8cbf55f954f04b7ccdf3555423fbd766be1996cd314026a2ec52833730119b. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-016-01 — BLOCKED

The operator has configured actual protected inputs — - **GIVEN** reviewed main source, protected store environment and genuine provider/cloud/signing access - **WHEN** the deliberate browser workflow is dispatched - **THEN** it builds/inspects, reads status or reconciles the exact original intent/submission without a local Mac or clone; initial upload remains a separate persistent operator operation.

Current proof: Manual workflow uses explicit main/platform/environment, protected store environment, macOS toolchain, account-bound OIDC and reconcile-only selectors; offline wrapper tests enforce original intent/UUID.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `.github/workflows/mobile-store-release.yml::STATIC_manual_workflow_prerequisites` — file SHA `5404c7aaca64553e897f5831e460832b5b3e2234ebd8c05aba47e74d5b2890d9`, line 1; 1 current observation(s).
- `infra/test/test_store_inputs.py::test_browser_submit_cannot_stage_or_authorize_a_fresh_submission` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 715; 1 current observation(s).
- `infra/test/test_store_inputs.py::test_submit_reconciliation_requires_original_intent_and_exact_identifier` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 698; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/document-inspections/.github/workflows/mobile-store-release.yml` — SHA256 `5404c7aaca64553e897f5831e460832b5b3e2234ebd8c05aba47e74d5b2890d9`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Default-main registration, configured environment protection, genuine provider/cloud/signing inputs and deliberate browser dispatch remain absent and external action is outside read-only scope.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 4c0f391dceaf3fa0381211e2a859e70cfc560a444d98cd61ef5935bf1ddf7f3d. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-016-02 — PASS

A fresh upload is requested from ephemeral Actions — - **GIVEN** only a signed build receipt or a missing original pending intent/submission UUID - **WHEN** a fresh submit or incomplete reconcile operation is requested - **THEN** it refuses before private credential staging or AWS/EAS/store action rather than losing an upload fence on runner failure; GitHub artifact metadata reads may precede refusal.

Current proof: Fresh/incomplete browser submission refuses before new_directory/subprocess/httpx calls; tampered staged guards cannot launch helper; conflicting artifact/package selectors reject before download/staging.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_store_inputs.py::test_browser_submit_cannot_stage_or_authorize_a_fresh_submission` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 715; 1 current observation(s).
- `infra/test/test_store_inputs.py::test_run_cannot_remove_reconciliation_guards_to_launch_a_fresh_submit` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 1007; 1 current observation(s).
- `infra/test/test_store_inputs.py::test_protected_package_refuses_artifact_conflicts_invalid_json_and_oversize_before_staging` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 1246; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA f5d72fb8c38e23d192150a547b69a2cbe7be7b6a3b5994a8053fb55ae280e6d0. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-016-03 — PASS

The workflow exists only on an unmerged branch — - **GIVEN** missing default-main registration/protection/credentials - **WHEN** delivery is reported - **THEN** it describes supplied automation and prerequisites without claiming execution.

Current proof: Immutable runbook/workflow explicitly describe optional supplied automation, main-only protected environment prerequisites and no genuine account-authenticated execution/public availability.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/STORE_RELEASE.md::STATIC_store_prerequisites_and_public_availability` — file SHA `4aeff8438e3423721d93cc2f7fe3e9d4b4379804be7559877f278e737147f48b`, line 1; 1 current observation(s).
- `.github/workflows/mobile-store-release.yml::STATIC_manual_workflow_prerequisites` — file SHA `5404c7aaca64553e897f5831e460832b5b3e2234ebd8c05aba47e74d5b2890d9`, line 1; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/document-inspections/apps/mobile/STORE_RELEASE.md` — SHA256 `4aeff8438e3423721d93cc2f7fe3e9d4b4379804be7559877f278e737147f48b`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/document-inspections/.github/workflows/mobile-store-release.yml` — SHA256 `5404c7aaca64553e897f5831e460832b5b3e2234ebd8c05aba47e74d5b2890d9`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 5db1b3992015192e2e59d382b80cef6709d2c2bb8b60b19f8b746b3742bb7e66. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-017-01 — PASS

A later operation consumes the same exact candidate — - **GIVEN** a same-repository encrypted artifact and matching protected key/scope - **WHEN** the workflow authenticates and stages it - **THEN** original receipt bytes and cross-receipt hashes survive for normal signed/provider admission.

Current proof: Actual AES-GCM roundtrip preserves original noncanonical signed wires, correct source/repository/environment/platform authenticated scope, exact child byte hashes and private fixed-name staging for status/reconciliation.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_store_inputs.py::test_aead_roundtrip_preserves_exact_signed_receipt_and_intent_bytes` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 550; 1 current observation(s).
- `infra/test/test_store_inputs.py::test_status_preserves_original_receipts_without_staging_private_credentials` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 619; 1 current observation(s).
- `infra/test/test_store_inputs.py::test_signed_child_receipts_bind_original_build_bytes_and_logical_configuration` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 637; 1 current observation(s).
- `infra/test/test_store_inputs.py::test_submit_reconciliation_requires_original_intent_and_exact_identifier` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 698; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 8b01a6619f1c93bdf9a10683601d7af8f151b34f204fe4a7f208534196712b6c. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-017-02 — PASS

An artifact or ciphertext is substituted — - **GIVEN** a wrong repository/source/platform, altered ciphertext or arbitrary archive path - **WHEN** handoff admission runs - **THEN** it refuses before credentials or receipt data are exposed.

Current proof: Wrong repo/source/environment/platform/key/nonce/ciphertext and arbitrary ZIP paths/extra entries reject; bad signature or byte linkage refuses before private staging, without exposing plaintext receipt contents.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_store_inputs.py::test_aead_refuses_wrong_key_scope_metadata_nonce_and_ciphertext` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 566; 1 current observation(s).
- `infra/test/test_store_inputs.py::test_public_artifact_allows_one_bounded_ciphertext_entry_only` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 774; 1 current observation(s).
- `infra/test/test_store_inputs.py::test_artifact_metadata_and_redirect_targets_cannot_change_scope_or_leak_token` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 835; 1 current observation(s).
- `infra/test/test_store_inputs.py::test_reconciliation_signature_authority_is_verified_before_staging` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 729; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 0e8e5798a0be3c76169bbad25894011429d6711005bc918bbb938a1844ce8a1f. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-018-01 — PARTIAL

A persistent operator transfers an uncertain existing submission — - **GIVEN** the original signed build and pending intent, trusted public key and protected encryption key - **WHEN** pack completes and its ciphertext is supplied for browser reconciliation - **THEN** the exact original byte links survive; the existing provider UUID is queried without another upload.

Current proof: Pack leaves input bytes/inode/mode unchanged, calls no process/network, emits only private ciphertext; CLI protected-package reconciliation preserves original build/intent bytes and original selector.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_store_inputs.py::test_pack_preserves_inputs_and_writes_only_private_scope_and_ciphertext` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 1099; 1 current observation(s).
- `infra/test/test_store_inputs.py::test_cli_pack_to_protected_ciphertext_reconciliation_preserves_inner_bytes` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 1217; 1 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_lost_submission_response_persists_exact_intent_and_reconciles_without_second_upload` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 597; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Connect that exact packaged handoff to store helper reconciliation and assert submit:view queries the existing providerUUID with zero upload; current packCLI stops after prepare, and helper test does not assert query argument.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 3c9c13732f7d0501fe92a076d3a291feeceae908a0ad324ff8aecfce9c66028a. Actual current source and raw evidence supply this disposition.

## OTGD-047-STORE-018-02 — PASS

A transfer replaces or ambiguously selects evidence — - **GIVEN** changed receipt bytes, wrong signature/scope, a foreign pending intent or both input selectors - **WHEN** packing or browser admission is attempted - **THEN** it refuses without a provider mutation or private credential staging.

Current proof: Wrong scope/config/signer/raw-byte links/foreign intent reject before new_directory; ambiguous protected-package+artifact selection returns1 with no download/staging; optional completed result links are checked.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_store_inputs.py::test_pack_refuses_foreign_scope_config_signer_and_changed_receipt_bytes_before_staging` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 1138; 1 current observation(s).
- `infra/test/test_store_inputs.py::test_protected_package_refuses_artifact_conflicts_invalid_json_and_oversize_before_staging` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 1246; 1 current observation(s).
- `infra/test/test_store_inputs.py::test_pack_rejects_completed_outcome_for_different_build_or_original_intent` — file SHA `4ddb98039e08fa6b0475ffca32c46932d85d1c476ea4028c1cd5c186f987034c`, line 1185; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 6150aa2caec793d25eeafd272de3e288eb948bc134b73778d467624d23273628. Actual current source and raw evidence supply this disposition.

