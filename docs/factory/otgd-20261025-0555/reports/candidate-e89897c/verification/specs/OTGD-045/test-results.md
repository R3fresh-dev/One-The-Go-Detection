# OTGD-045 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/verified-release-and-browser-access/specs/cloud-release-orchestration/spec.md`; SHA256 `c62bb011c5e71f177ededaf19e710e2ec40a97618a5b427d144f97bcd67d7a26`.

6 cases, 2 requirements: PARTIAL 2, PASS 4. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-045-CLOUD-DEP-007-01 — PARTIAL

A valid absent public subdomain is registered — - **GIVEN** a matching enabled private distribution, issued TLS and absent record - **WHEN** apply is explicitly requested - **THEN** one CNAME is created; successful change observation must occur within ten minutes, SDK timeouts/retries may delay failure reporting, and failure does not imply cancellation or rollback.

Current proof: Mocked exact TLS/distribution/public absent record emits one CREATE and waiter; deadline601 raises after create/wait without rollback code.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_plan_has_no_dns_mutation_and_apply_waits_for_actual_change` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 429; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_late_dns_success_is_refused_without_claiming_rollback` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 450; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “one CNAME created ... successful actual change observation within ten minutes”: no live Route53 change/propagation or SDK timeout behavior observed; Mock waiter cannot qualify actual DNS.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 48bbde05f617853e46e5c71d037fe6215d6bf90a0f0bdd7953d2e770931c9ff2. Actual current source and raw evidence supply this disposition.

## OTGD-045-CLOUD-DEP-007-02 — PARTIAL

A foreign record appears after preview — - **GIVEN** an absent lookup followed by another actor creating that record - **WHEN** CREATE is submitted - **THEN** AWS rejects the conflict, the foreign record is preserved and the command reports failure.

Current proof: After absent lookup, mocked AWS CREATE raises InvalidChangeBatch; command propagates failure, request Action CREATE and no waiter.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_intervening_dns_record_fails_atomic_create_without_overwrite` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 443; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “AWS rejects conflict, foreign record preserved”: service mock does not store a competing record or exercise real Route53 atomic conflict; preservation is inferred from CREATE contract, not observed live.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 1f9046b7de5dce7f38c74972457a4a82d83704138797bcd00657b953e78bc874. Actual current source and raw evidence supply this disposition.

## OTGD-045-CLOUD-DEP-007-03 — PASS

The exact target already exists — - **GIVEN** the observed CNAME has the admitted target and supported record form - **WHEN** apply is requested - **THEN** no write occurs and the receipt identifies an observed equivalent record rather than fabricated propagation evidence.

Current proof: Matching case/trailing-dot CNAME returns applied=false/unchanged=true with no change API or waiter. Inspected receipt action NONE and unchanged observed record have no fabricated change_id; no propagation claimed. Software no-op semantics only.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_equivalent_existing_dns_case_and_trailing_dot_are_idempotent` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 436; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 40376d086ab305e077ce10e65011004c69fae5c67793b4e27cfe9591b94d54ee. Actual current source and raw evidence supply this disposition.

## OTGD-045-CLOUD-DEP-007-04 — PASS

Caller supplies apex or foreign authority — - **GIVEN** a private/foreign zone, conflicting record, disabled distribution, wrong alias or certificate - **WHEN** admission runs - **THEN** no DNS mutation or successful registration receipt occurs.

Current proof: Every mismatching zone/target/TLS/alias/disabled/private-origin fixture raises before DNS mutation; no successful change receipt returned. Scoped admission guards proven with doubles.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_apex_foreign_private_zone_unready_tls_alias_and_existing_record_conflicts_fail_closed` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 474; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_disabled_foreign_origin_or_non_sigv4_distribution_cannot_publish_dns` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 457; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA ebf555ebbc857961695465d49c44c3d892ab623ea81df9283d0ea5c7f48c8197. Actual current source and raw evidence supply this disposition.

## OTGD-045-CLOUD-DEP-011-01 — PASS

Genuine matching release authority is supplied — - **GIVEN** bounded stable regular key/evidence files and the matching independently trusted Ed25519 public key - **WHEN** the actual release operation loads them - **THEN** signature verification/signing uses those exact bytes and never logs key material.

Current proof: Real regular private Ed25519 bytes round-trip, actual sign_release/verify_release return exact body and trusted public key equality enforced; wrong authority/tampered envelope refused. Inspected key loading/sign/verify code writes signature+public payload only and does not print/log key material. No production signing authority provisioned.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_release.py::test_private_signing_key_is_regular_private_bounded_and_single_link` — file SHA `3013213897c8f1721e0f28a2c4610f18b48cb46ed6a5f5900ebb4495f3e3f9d5`, line 20; 1 current observation(s).
- `infra/test/test_release.py::test_signed_digest_bound_to_account_environment_and_source` — file SHA `3013213897c8f1721e0f28a2c4610f18b48cb46ed6a5f5900ebb4495f3e3f9d5`, line 65; 1 current observation(s).
- `infra/test/test_provenance.py::test_signer_must_match_independently_trusted_key` — file SHA `996ead63b1f3ae3999aa31d81e3de893bbc50b62bfaac6e2a69f88a968d5f6a1`, line 369; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 3978649a946e50c64f0f75e71a26cb7d54bb2f4bcd436ab462f086b066928f29. Actual current source and raw evidence supply this disposition.

## OTGD-045-CLOUD-DEP-011-02 — PASS

A file is special, replaced or exposed — - **GIVEN** a FIFO, symlink, oversized file, changed inode/metadata or broadly readable private key - **WHEN** the reader is called - **THEN** it refuses promptly before signing or cloud mutation.

Current proof: Symlink/directory/hardlink/public-mode/wrong-owner/oversize/malformed key refused; metadata changed during bounded read refused; FIFO key/evidence actual child readers exit0 within5s; evidence oversize fails before os.read; trusted-key link/oversize refused. Offline reader fails before signing/cloud path returns authority.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_release.py::test_private_signing_key_is_regular_private_bounded_and_single_link` — file SHA `3013213897c8f1721e0f28a2c4610f18b48cb46ed6a5f5900ebb4495f3e3f9d5`, line 20; 1 current observation(s).
- `infra/test/test_release.py::test_fifo_key_is_rejected_without_waiting_for_a_writer` — file SHA `3013213897c8f1721e0f28a2c4610f18b48cb46ed6a5f5900ebb4495f3e3f9d5`, line 43; 1 current observation(s).
- `infra/test/test_release.py::test_signing_key_metadata_change_during_read_is_refused` — file SHA `3013213897c8f1721e0f28a2c4610f18b48cb46ed6a5f5900ebb4495f3e3f9d5`, line 53; 1 current observation(s).
- `infra/test/test_provenance.py::test_evidence_and_trusted_key_inputs_refuse_links_and_oversize_before_read` — file SHA `996ead63b1f3ae3999aa31d81e3de893bbc50b62bfaac6e2a69f88a968d5f6a1`, line 77; 1 current observation(s).
- `infra/test/test_provenance.py::test_fifo_evidence_is_rejected_without_waiting_for_a_writer` — file SHA `996ead63b1f3ae3999aa31d81e3de893bbc50b62bfaac6e2a69f88a968d5f6a1`, line 93; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA f05fdfcb4a68ed5b5d83d09c98265194b91c25fd585b2c04b98f3045564800e8. Actual current source and raw evidence supply this disposition.

