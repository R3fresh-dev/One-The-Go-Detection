# OTGD-016 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/independent-recovery-admission/specs/recovery-authority/spec.md`; SHA256 `430fe7dfbfdb117add502c5632150690905d94b3dcb42ddc892bf1e8943f273c`.

6 cases, 2 requirements: PARTIAL 3, PASS 3. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-016-RECOVERY-001-01 — PARTIAL

Consistent retained authority — - **WHEN** the database matches all pinned retained control, identity, generation, deletion and recovery evidence - **THEN** ordinary service admission may proceed subject to current participant and study authority

Current proof: Consistent retained deletion DB returns cutoff 0, correct latest activation+DB returns exact cutoff; missing/corrupt states refused.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_recovery_authority.py::test_retained_deletion_blocks_restored_active_database_even_without_restore_flag` — file SHA `c6f39c45163f8e2c709b5f63094f1c7df83afb094c9905003fee61fc7fa0b638`, line 260; 5 current observation(s).
- `services/api/tests/test_recovery_authority.py::test_recovery_claim_requires_latest_independent_activation_and_suspension` — file SHA `c6f39c45163f8e2c709b5f63094f1c7df83afb094c9905003fee61fc7fa0b638`, line 271; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “ordinary service admission may proceed subject to current participant and study authority”: helper consistency succeeds, but no positive API/worker admission with the retained authority fixture and current participant/study together.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 74dcec7a8ec3ce7cac29b6453c13f5fb8ccdf8e896d4a50c8669082a64bfbd62. Actual current source and raw evidence supply this disposition.

## OTGD-016-RECOVERY-001-02 — PARTIAL

Stale restored active row — - **WHEN** a retained deletion or recovery activation conflicts with an active database row or its queued job - **THEN** API and worker refuse new data work before commit, including when the database recovery row is absent

Current proof: Retained deletion conflicts rejected by validator; retained activation absent from DB blocks claim/execute/commit, leaves pending fence0 and result null; local marker loss blocks API.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_recovery_authority.py::test_retained_deletion_blocks_restored_active_database_even_without_restore_flag` — file SHA `c6f39c45163f8e2c709b5f63094f1c7df83afb094c9905003fee61fc7fa0b638`, line 260; 5 current observation(s).
- `services/api/tests/test_recovery_authority.py::test_worker_claim_and_commit_refuse_retained_activation_missing_in_database` — file SHA `c6f39c45163f8e2c709b5f63094f1c7df83afb094c9905003fee61fc7fa0b638`, line 489; 5 current observation(s).
- `services/api/tests/test_recovery_authority.py::test_running_http_readiness_and_new_account_refuse_lost_local_marker` — file SHA `c6f39c45163f8e2c709b5f63094f1c7df83afb094c9905003fee61fc7fa0b638`, line 462; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “API ... refuse new data work” specifically for retained deletion/recovery-activation conflict with absent DB recovery row: worker test covers this exact conflict, API test covers a different missing-marker condition.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA e53b05ab257cf9b6cd8dd51453d9849ebbc8c9e3a07c4fdd2231b9d61cd1e3c0. Actual current source and raw evidence supply this disposition.

## OTGD-016-RECOVERY-001-03 — PARTIAL

Missing local establishment — - **WHEN** retained PostgreSQL is paired with a missing or replacement emulator journal - **THEN** bootstrap and running service admission refuse silent establishment or account provisioning

Current proof: Bootstrap SQL helper refuses silent establishment with retained account, missing or changed journal binding; HTTP readiness/account provisioning denies lost marker and creates zero accounts.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_journal_continuity.py::test_retained_database_never_automatically_adopts_journal` — file SHA `4ca05e80289e4626c0096814050433fc39077912de8e761135d1aea59ca9b6cb`, line 144; 5 current observation(s).
- `services/api/tests/test_journal_continuity.py::test_empty_database_binds_once_then_requires_exact_version` — file SHA `4ca05e80289e4626c0096814050433fc39077912de8e761135d1aea59ca9b6cb`, line 70; 5 current observation(s).
- `services/api/tests/test_recovery_authority.py::test_running_http_readiness_and_new_account_refuse_lost_local_marker` — file SHA `c6f39c45163f8e2c709b5f63094f1c7df83afb094c9905003fee61fc7fa0b638`, line 462; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Actual retained PostgreSQL paired with a missing/replaced emulator journal must keep nonprivacy admission closed. Current LocalStack worker/recovery gates pass, but the reviewed bootstrap-specific missing/replaced-journal fixture uses SQLite and a journal double; that exact retained-PG/emulator pair is unexecuted.

Prerequisite/evidence type: live_dependency_scenario_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 149ffd6236fb6798420c59d8b7b2c29258cea68e5b5e87aeb30beee699bd2283. Actual current source and raw evidence supply this disposition.

## OTGD-016-RECOVERY-002-01 — PASS

Reapproved study — - **WHEN** every current registry dependency is freshly submitted, independently reviewed and released, and the exact study seal and participant consent are current - **THEN** that study may collect through current qualified configurations while every unsealed study remains suspended

Current proof: Fresh three-principal study approval, consent and exact retained seal permit helper require_study_scope; global suspended flag stays true and other unsealed study refused. Configured fresh closure and genuine typed fixture allow exact scope only; retired/replaced dependency refuses capture/model; accepted privacy cleanup retains journal while nonprivacy fails.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_recovery_scopes.py::test_fresh_registry_reapproval_seal_allows_only_exact_study_and_new_consent` — file SHA `3fe448145c086a5441b96caeffa0fa006f24a0b18396da3ac60462fba4850344`, line 90; 5 current observation(s).
- `services/api/tests/test_recovery_scopes.py::test_configured_reapproved_study_reaches_real_capture_start_and_model_execution` — file SHA `3fe448145c086a5441b96caeffa0fa006f24a0b18396da3ac60462fba4850344`, line 230; 5 current observation(s).
- `services/api/tests/test_recovery_scopes.py::test_prior_configured_seal_refuses_changed_dependency_through_capture_and_model` — file SHA `3fe448145c086a5441b96caeffa0fa006f24a0b18396da3ac60462fba4850344`, line 260; 10 current observation(s).
- `services/api/tests/test_recovery_authority.py::test_failed_nonprivacy_admission_preserves_accepted_cleanup_and_retained_journal` — file SHA `c6f39c45163f8e2c709b5f63094f1c7df83afb094c9905003fee61fc7fa0b638`, line 546; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Retained journal/object transports are named unit doubles; no independent actual cloud recovery/RPO/RTO proof.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA cfbcd1ab54a262cbf7f92e36c7df8c6607f58ec9ed5bec801794509fef944528. Actual current source and raw evidence supply this disposition.

## OTGD-016-RECOVERY-002-02 — PASS

Boolean or stale approval override — - **WHEN** a database flag changes, old approval or consent is reused, a seal disappears or a dependency is retired or changed - **THEN** study capture and model execution refuse resumption

Current proof: Nine helper mutations (stale approval/consent, database bool, wrong recovery/scope/owner, changed/latest/overwritten/deleted seal) denied; model recovery=true returns inconclusive/no probability. Configured fresh closure and genuine typed fixture allow exact scope only; retired/replaced dependency refuses capture/model; accepted privacy cleanup retains journal while nonprivacy fails.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_recovery_scopes.py::test_no_stale_or_mutated_authority_reopens_study` — file SHA `3fe448145c086a5441b96caeffa0fa006f24a0b18396da3ac60462fba4850344`, line 121; 45 current observation(s).
- `services/api/tests/test_model_admission.py::test_current_authority_or_bytes_refusal_returns_no_score` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 480; 50 current observation(s).
- `services/api/tests/test_recovery_scopes.py::test_configured_reapproved_study_reaches_real_capture_start_and_model_execution` — file SHA `3fe448145c086a5441b96caeffa0fa006f24a0b18396da3ac60462fba4850344`, line 230; 5 current observation(s).
- `services/api/tests/test_recovery_scopes.py::test_prior_configured_seal_refuses_changed_dependency_through_capture_and_model` — file SHA `3fe448145c086a5441b96caeffa0fa006f24a0b18396da3ac60462fba4850344`, line 260; 10 current observation(s).
- `services/api/tests/test_recovery_authority.py::test_failed_nonprivacy_admission_preserves_accepted_cleanup_and_retained_journal` — file SHA `c6f39c45163f8e2c709b5f63094f1c7df83afb094c9905003fee61fc7fa0b638`, line 546; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Retained journal/object transports are named unit doubles; no independent actual cloud recovery/RPO/RTO proof.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA a2f7c8acbafdd8f2c601a2af98c40c0e14f4591710bb35cef8ddea38211ee899. Actual current source and raw evidence supply this disposition.

## OTGD-016-RECOVERY-002-03 — PASS

Privacy cleanup during suspension — - **WHEN** nonprivacy admission fails while an accepted deletion needs safe object cleanup - **THEN** privacy cleanup may continue without reopening data or removing independently retained deletion evidence

Current proof: Nonprivacy worker refusal is executed; immutable worker.py has deletion-specific admission exceptions. Configured fresh closure and genuine typed fixture allow exact scope only; retired/replaced dependency refuses capture/model; accepted privacy cleanup retains journal while nonprivacy fails.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_recovery_authority.py::test_worker_claim_and_commit_refuse_retained_activation_missing_in_database` — file SHA `c6f39c45163f8e2c709b5f63094f1c7df83afb094c9905003fee61fc7fa0b638`, line 489; 5 current observation(s).
- `services/api/tests/test_recovery_scopes.py::test_configured_reapproved_study_reaches_real_capture_start_and_model_execution` — file SHA `3fe448145c086a5441b96caeffa0fa006f24a0b18396da3ac60462fba4850344`, line 230; 5 current observation(s).
- `services/api/tests/test_recovery_scopes.py::test_prior_configured_seal_refuses_changed_dependency_through_capture_and_model` — file SHA `3fe448145c086a5441b96caeffa0fa006f24a0b18396da3ac60462fba4850344`, line 260; 10 current observation(s).
- `services/api/tests/test_recovery_authority.py::test_failed_nonprivacy_admission_preserves_accepted_cleanup_and_retained_journal` — file SHA `c6f39c45163f8e2c709b5f63094f1c7df83afb094c9905003fee61fc7fa0b638`, line 546; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Retained journal/object transports are named unit doubles; no independent actual cloud recovery/RPO/RTO proof.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA 407c3c47a1d16746559c059b93ad308fff8f57e892190a412d9fc415f3512e9f. Actual current source and raw evidence supply this disposition.

