# OTGD-044: verification plan

Canonical: `openspec/changes/verified-release-and-browser-access/specs/cloud-browser-delivery/spec.md`; SHA-256 `758f7dd11a72a15750d44a61d49d986b923232ac981fcb9ab304a56526e5bb6c`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `infra/test/test_cloud_endpoints.py` — `786b0d3537e333ffa9d9114c7d946ef8aebfed4213702e7816b2f8cb47726bc4`
- `infra/test/test_provenance.py` — `996ead63b1f3ae3999aa31d81e3de893bbc50b62bfaac6e2a69f88a968d5f6a1`
- `infra/test/test_web_deployment.py` — `e0fbb440ac1b32d67b389b1261d3f6f8360e224793c8c4ad94809ea03fabb2d1`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### WEB-DEP-007 — Enforce browser security headers

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/cloud-browser-delivery/spec.md` / `WEB-DEP-007`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-044-WEB-DEP-007-01 | Public transport probes execute — **GIVEN** a published admitted artifact and the full supported response policy **WHEN** index, assets and the history route are retrieved over verified HTTPS **THEN** exact byte digest/size and all required transport/CSP controls verify. | `infra/test/test_web_deployment.py:213` — test_public_policy_rejects_missing_broadened_or_ambiguous_csp_and_transport<br>`infra/test/test_provenance.py:274` — test_gate_file_rejects_duplicate_json_keys_oversize_and_missing_file | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-044-WEB-DEP-007-02 | A policy fragment hides a weaker route — **GIVEN** a missing referrer directive, wildcard script/connect source, duplicate CSP directive or unprotected history response **WHEN** public verification runs **THEN** it fails without a verified-access receipt. | `infra/test/test_web_deployment.py:213` — test_public_policy_rejects_missing_broadened_or_ambiguous_csp_and_transport<br>`infra/test/test_provenance.py:382` — test_cloud_image_manifest_and_local_config_must_bind_signed_source | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-044-WEB-DEP-007-03 | A public response exceeds the signed file — **GIVEN** an oversized or unexpectedly encoded HTTP response **WHEN** verification streams the response **THEN** it refuses at the expected-size boundary without allocating the full untrusted body. ## ADDED Requirements | `infra/test/test_web_deployment.py:199` — test_https_asset_deep_link_readiness_checks_do_not_claim_signed_in_acceptance<br>`infra/test/test_provenance.py:274` — test_gate_file_rejects_duplicate_json_keys_oversize_and_missing_file | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### WEB-DEP-009 — Verify the actual complete private release route

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/cloud-browser-delivery/spec.md` / `WEB-DEP-009`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-044-WEB-DEP-009-01 | The supplied infrastructure matches the release — **GIVEN** the actual one-origin OAC distribution and unchanged signed archive **WHEN** publication or DNS admission runs **THEN** routing and every archive member match the admitted release before mutation. | `infra/test/test_web_deployment.py:128` — test_archive_bound_precedes_hashing_and_admission_uses_one_stable_snapshot | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-044-WEB-DEP-009-02 | A secondary route escapes the admitted origin — **GIVEN** a foreign assets behavior, extra origin/group, wrong prefix, disabled distribution or non-always-signing OAC **WHEN** admission runs **THEN** it refuses publication and DNS changes. | `infra/test/test_web_deployment.py:379` — test_disabled_foreign_origin_or_non_sigv4_distribution_cannot_publish_dns<br>`infra/test/test_provenance.py:317` — test_build_refuses_local_json_gate_claim_before_docker_or_signing | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-044-WEB-DEP-009-03 | An archive changes during verification — **GIVEN** a special/oversized/replaced archive or mismatching member/digest **WHEN** bounded verification executes **THEN** it fails before any public bytes are published. | `infra/test/test_web_deployment.py:186` — test_unreviewed_cache_routes_origins_and_failover_groups_block_all_publication | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `128-MiB`, `16-MiB`, `256`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### WEB-DEP-010 — Bound public response verification by signed bytes

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/cloud-browser-delivery/spec.md` / `WEB-DEP-010`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-044-WEB-DEP-010-01 | The public release returns its exact artifact — **GIVEN** the admitted published index/assets and matching identity responses **WHEN** the bounded transport probe executes **THEN** signed byte sizes and digests match, including the history fallback. | `infra/test/test_web_deployment.py:317` — test_public_body_overrun_and_unsolicited_compression_stop_before_unbounded_reads | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-044-WEB-DEP-010-02 | The public response is unexpectedly encoded or oversized — **GIVEN** compression or more bytes than the signed artifact **WHEN** the response is streamed **THEN** verification refuses at its bound without buffering the untrusted body. | `infra/test/test_web_deployment.py:317` — test_public_body_overrun_and_unsolicited_compression_stop_before_unbounded_reads | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.
