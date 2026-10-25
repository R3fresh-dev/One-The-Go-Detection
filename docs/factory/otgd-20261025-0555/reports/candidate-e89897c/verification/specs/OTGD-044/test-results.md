# OTGD-044 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/verified-release-and-browser-access/specs/cloud-browser-delivery/spec.md`; SHA256 `758f7dd11a72a15750d44a61d49d986b923232ac981fcb9ab304a56526e5bb6c`.

8 cases, 3 requirements: PARTIAL 4, PASS 4. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-044-WEB-DEP-007-01 — PARTIAL

Public transport probes execute — - **GIVEN** a published admitted artifact and the full supported response policy - **WHEN** index, assets and the history route are retrieved over verified HTTPS - **THEN** exact byte digest/size and all required transport/CSP controls verify.

Current proof: Nominal MockTransport index+one JS+history verify expected bytes, strict transport/CSP helper accepts exact/reordered policy. ActualoperatorHTTPfixture checks everyadmittedasset; secondaryscript/otherassetomission/corruption/encoding/redirect/oversize refuse before generalaccesspass.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_https_asset_deep_link_readiness_checks_do_not_claim_signed_in_acceptance` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 233; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_public_policy_rejects_missing_broadened_or_ambiguous_csp_and_transport` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 291; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_every_admitted_asset_is_read_and_checked_before_public_access_passes` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 247; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual published verified-HTTPS index, every admitted asset and history route must meet exact digest/size/transport/CSP policy. Current operator HTTP fixtures now check every admitted asset and fail missing/corrupt/encoded/redirected/oversized members; actual CloudFront/S3/DNS release transport is unexecuted.

Prerequisite/evidence type: deployment_cloud_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Scope limits: Current named operational unit execution is bound for all-asset fixtures. No actual CloudFront/S3/deployed DNS release or general-access approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA b2135db53e5a2343fe34e400a1f01aa44faa4edd188852124cc07ec74f0b6a7d. Actual current source and raw evidence supply this disposition.

## OTGD-044-WEB-DEP-007-02 — PASS

A policy fragment hides a weaker route — - **GIVEN** a missing referrer directive, wildcard script/connect source, duplicate CSP directive or unprotected history response - **WHEN** public verification runs - **THEN** it fails without a verified-access receipt.

Current proof: Weak/ambiguous CSP and referrer/HSTS/frame policy rejected; secure index with unprotected history triggers Gate from complete verify_access before receipt return. Strict expected-directive comparison inspected; no successful receipt returned on these failures. Software response-policy guard, not live CDN observation.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_public_policy_rejects_missing_broadened_or_ambiguous_csp_and_transport` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 291; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_navigation_cannot_omit_required_policy_when_index_is_secure` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 385; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA e584dde99f832f313df0b3809f6882639bf94eabcdf99be0a9e78a84892ff317. Actual current source and raw evidence supply this disposition.

## OTGD-044-WEB-DEP-007-03 — PASS

A public response exceeds the signed file — - **GIVEN** an oversized or unexpectedly encoded HTTP response - **WHEN** verification streams the response - **THEN** it refuses at the expected-size boundary without allocating the full untrusted body.

Current proof: Production response streamer requests identity; encoded response rejected with zero body chunks; overrun rejected after exact body+one sentinel chunk, third trailing chunk unread and stream closed. Exact bounded software allocation behavior observed.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_public_body_overrun_and_unsolicited_compression_stop_before_unbounded_reads` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 395; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA a5c902dbb8ea1478f707d3ecdf12a9a807ed988db0b756e7fa9a14a0733b010a. Actual current source and raw evidence supply this disposition.

## OTGD-044-WEB-DEP-009-01 — PARTIAL

The supplied infrastructure matches the release — - **GIVEN** the actual one-origin OAC distribution and unchanged signed archive - **WHEN** publication or DNS admission runs - **THEN** routing and every archive member match the admitted release before mutation.

Current proof: Real archive+signature/member verification uses one captured snapshot, mocked actual distribution/OAC checked before put and index written last.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_signature_source_environment_runtime_and_archive_bytes_are_bound` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 149; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_publish_checks_actual_private_origin_and_commits_entrypoint_last` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 192; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_archive_bound_precedes_hashing_and_admission_uses_one_stable_snapshot` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 162; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “actual one-origin OAC distribution ... publication/DNS admission ... before mutation”: runtime route metadata is fixture SDK responses; no actual deployed CloudFront/private-S3 route with release artifact exercised.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 6ce65d26d8b448d76f6e20e6d94333809fbbbcf5239914da8fdb965d4b5f74f6. Actual current source and raw evidence supply this disposition.

## OTGD-044-WEB-DEP-009-02 — PASS

A secondary route escapes the admitted origin — - **GIVEN** a foreign assets behavior, extra origin/group, wrong prefix, disabled distribution or non-always-signing OAC - **WHEN** admission runs - **THEN** it refuses publication and DNS changes.

Current proof: Foreign behavior, extra origin/group make publish refuse with zero put/invalidation; DNS mutation matrix additionally rejects wrong bucket/region/prefix, disabled distribution and non-always OAC with zero Route53 change. Software admission negative cases proven.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_unreviewed_cache_routes_origins_and_failover_groups_block_all_publication` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 220; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_disabled_foreign_origin_or_non_sigv4_distribution_cannot_publish_dns` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 457; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 21a43f3c55a13bb03a2a2bdbb511fdc512f273588d58f633fc077b42ffdc9949. Actual current source and raw evidence supply this disposition.

## OTGD-044-WEB-DEP-009-03 — PARTIAL

An archive changes during verification — - **GIVEN** a special/oversized/replaced archive or mismatching member/digest - **WHEN** bounded verification executes - **THEN** it fails before any public bytes are published.

Current proof: Oversized archive rejected before signer called; changed/injected ZIP or duplicate member rejected. Deliberate replacement AFTER bounded snapshot returns original accepted bytes, not replacement.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_archive_bound_precedes_hashing_and_admission_uses_one_stable_snapshot` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 162; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_signature_source_environment_runtime_and_archive_bytes_are_bound` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 149; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_public_asset_types_paths_symlinks_and_duplicate_zip_entries_are_rejected` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 181; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “special/replaced archive ... fails before public bytes published”: file-reader archive-specific special/inode-change-during-read rejection and publication-not-called are not asserted together; post-snapshot replacement test intentionally succeeds with verified original snapshot. That safe snapshot behavior is distinguished from the stricter scenario wording; no malicious replacement-byte publication demonstrated.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 36e9f9c588e730df5b9a8d748c5dbf396eac4f0368280c2e549ebc8aafabea60. Actual current source and raw evidence supply this disposition.

## OTGD-044-WEB-DEP-010-01 — PARTIAL

The public release returns its exact artifact — - **GIVEN** the admitted published index/assets and matching identity responses - **WHEN** the bounded transport probe executes - **THEN** signed byte sizes and digests match, including the history fallback.

Current proof: Existing nominal probe verifies exact index/first JS and history fixture bytes. ActualoperatorHTTPfixture checks everyadmittedasset; secondaryscript/otherassetomission/corruption/encoding/redirect/oversize refuse before generalaccesspass.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_https_asset_deep_link_readiness_checks_do_not_claim_signed_in_acceptance` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 233; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_every_admitted_asset_is_read_and_checked_before_public_access_passes` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 247; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- The actual admitted public release must return all exact asset/index/history bytes under current identity. All-asset operator fixture assertions are now proved; public deployment identity/HTTPS execution remains unexecuted.

Prerequisite/evidence type: deployment_cloud_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Scope limits: Current named operational unit execution is bound for all-asset fixtures. No actual CloudFront/S3/deployed DNS release or general-access approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 2d0a211e84aaff9cd1e697aaa11ddd99c3c56cb47e44182213aebfbb5fd84995. Actual current source and raw evidence supply this disposition.

## OTGD-044-WEB-DEP-010-02 — PASS

The public response is unexpectedly encoded or oversized — - **GIVEN** compression or more bytes than the signed artifact - **WHEN** the response is streamed - **THEN** verification refuses at its bound without buffering the untrusted body.

Current proof: Actual streaming verifier rejects unsolicited gzip before reading and unencoded overrun at expected-size sentinel, closes stream and does not consume trailing untrusted bytes. Host-side software proof, not CDN test.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_public_body_overrun_and_unsolicited_compression_stop_before_unbounded_reads` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 395; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 2395e00859c4cf75b4d959b8912cc969028206128a401c03b0ee82891f076db3. Actual current source and raw evidence supply this disposition.

