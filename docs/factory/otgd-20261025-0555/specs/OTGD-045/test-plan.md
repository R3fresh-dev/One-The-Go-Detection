# OTGD-045: verification plan

Canonical: `openspec/changes/verified-release-and-browser-access/specs/cloud-release-orchestration/spec.md`; SHA-256 `c62bb011c5e71f177ededaf19e710e2ec40a97618a5b427d144f97bcd67d7a26`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001 v1, D-002 v1, D-003 v1, D-004 v1 acknowledged through native messaging. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `infra/test/test_cloud_endpoints.py` — `786b0d3537e333ffa9d9114c7d946ef8aebfed4213702e7816b2f8cb47726bc4`
- `infra/test/test_provenance.py` — `f4b05e5dc8f58d775cb7055632351b4bfdb819c9cefd74dfe48dd8bb86bff420`
- `infra/test/test_release.py` — `3013213897c8f1721e0f28a2c4610f18b48cb46ed6a5f5900ebb4495f3e3f9d5`
- `infra/test/test_web_deployment.py` — `e0fbb440ac1b32d67b389b1261d3f6f8360e224793c8c4ad94809ea03fabb2d1`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### CLOUD-DEP-007 — Register only the exact deployed UI CNAME

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/cloud-release-orchestration/spec.md` / `CLOUD-DEP-007`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-045-CLOUD-DEP-007-01 | A valid absent public subdomain is registered — **GIVEN** a matching enabled private distribution, issued TLS and absent record **WHEN** apply is explicitly requested **THEN** one CNAME is created; successful change observation must occur within ten minutes, SDK timeouts/retries may delay failure reporting, and failure does not imply cancellation or rollback. | `infra/test/test_web_deployment.py:396` — test_apex_foreign_private_zone_unready_tls_alias_and_existing_record_conflicts_fail_closed | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-045-CLOUD-DEP-007-02 | A foreign record appears after preview — **GIVEN** an absent lookup followed by another actor creating that record **WHEN** CREATE is submitted **THEN** AWS rejects the conflict, the foreign record is preserved and the command reports failure. | `infra/test/test_web_deployment.py:396` — test_apex_foreign_private_zone_unready_tls_alias_and_existing_record_conflicts_fail_closed | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-045-CLOUD-DEP-007-03 | The exact target already exists — **GIVEN** the observed CNAME has the admitted target and supported record form **WHEN** apply is requested **THEN** no write occurs and the receipt identifies an observed equivalent record rather than fabricated propagation evidence. | `infra/test/test_web_deployment.py:396` — test_apex_foreign_private_zone_unready_tls_alias_and_existing_record_conflicts_fail_closed<br>`infra/test/test_provenance.py:92` — test_fifo_evidence_is_rejected_without_waiting_for_a_writer | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-045-CLOUD-DEP-007-04 | Caller supplies apex or foreign authority — **GIVEN** a private/foreign zone, conflicting record, disabled distribution, wrong alias or certificate **WHEN** admission runs **THEN** no DNS mutation or successful registration receipt occurs. ## ADDED Requirements | `infra/test/test_web_deployment.py:396` — test_apex_foreign_private_zone_unready_tls_alias_and_existing_record_conflicts_fail_closed | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### CLOUD-DEP-011 — Bound release authority and evidence inputs

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/cloud-release-orchestration/spec.md` / `CLOUD-DEP-011`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-045-CLOUD-DEP-011-01 | Genuine matching release authority is supplied — **GIVEN** bounded stable regular key/evidence files and the matching independently trusted Ed25519 public key **WHEN** the actual release operation loads them **THEN** signature verification/signing uses those exact bytes and never logs key material. | `infra/test/test_release.py:20` — test_private_signing_key_is_regular_private_bounded_and_single_link<br>`infra/test/test_provenance.py:76` — test_evidence_and_trusted_key_inputs_refuse_links_and_oversize_before_read | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-045-CLOUD-DEP-011-02 | A file is special, replaced or exposed — **GIVEN** a FIFO, symlink, oversized file, changed inode/metadata or broadly readable private key **WHEN** the reader is called **THEN** it refuses promptly before signing or cloud mutation. | `infra/test/test_release.py:20` — test_private_signing_key_is_regular_private_bounded_and_single_link<br>`infra/test/test_provenance.py:76` — test_evidence_and_trusted_key_inputs_refuse_links_and_oversize_before_read | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `000`, `192 bytes`, `48`, `8`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.
