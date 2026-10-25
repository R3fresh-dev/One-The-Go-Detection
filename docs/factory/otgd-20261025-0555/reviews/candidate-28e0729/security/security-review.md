# Independent security council review — frozen candidate

Role: SECURITY. Reviewer: `/root/review_security`, fresh context, independent of implementation authors. Provider OpenAI; configured `gpt-6.1-sol`, reasoning `high`, `fork_turns:none`, confirmed by PM native message. The runtime does not independently expose an exact model attestation; this records the actual dispatch configuration, not an inferred runtime claim.

Observed 2026-10-25T07:43:26.974621+00:00. Verdict: **CHANGES_REQUIRED** for the reviewed implementation because SEC-01 remains open. Final implementation acceptance is additionally **BLOCKED** by pending exact-candidate verification and dossier import. This is a domain report, not product/engineering signoff or final council approval. No release, merge, deployment, participant use or scientific/native qualification is granted.

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; baseline `0844868aa543af4ab75ac5065ad48cf807b86bb3`; Factory `4770878e18e9c587c2961b9e2bb13315da31abe9`. Candidate whole-source SHA-256 `36ed8d800edcb560ac8ca189e98b64518b3342a29458d6e91a8d943085310f8c`. Read-only comparison of every one of the **1014** candidate-manifest file hashes found **zero mismatches**; all **47** actual canonical SHA-256 values match inventory and candidate manifest. `bindings.json` binds each spec, dossier, selected implementation and inspected artifact; it is the detailed evidence index. Hashes are SHA-256 over file bytes, relative to the repository unless explicitly absolute. The reviewer did not change any repository file.

## Decision synchronization

Actual acknowledgment was sent to PM using native agent messaging before dependent review. D-001 v1 **AFFECTED**: approved software/auth/provenance scope and claim limits. D-002 v1 **NOT_AFFECTED**: no supervision/recovery operation. D-003 v1 **AFFECTED**: real local fictional-only test evidence cannot authorize research. D-004 v1 **AFFECTED**: reconcile to authorized scope without weakening requirements. D-005 v1 **AFFECTED**: preserve services, volumes and journal; this review performs no service action. D-006 **v5 AFFECTED**: adopt only its current-source local image disclosure; reconstructed local image does not establish original/cloud provenance. D-007 **v1 AFFECTED**: assess state/CSP repair without weakening state/PKCE/redirect/Origin; stale preflight cannot become final PASS. D-008 **v1 AFFECTED**: whole-source freeze and external output ownership; exact-current final gates required. Superseded D-006 v1–v4 are understood as history, not current admission. Correction **0/2**, recovery **0/3**; no counter changed by this review.

## Checks actually performed

Read AGENTS.md, pinned Factory skill/council/evidence/communication/model-policy, current decisions, inventory and planning/implementation reports. Reviewed security-relevant requirements across all 47 canonical files, shared security contracts, actual diff from baseline and selected unchanged trust-boundary code. Inspected authored tests as assertions only; no test, install, service, Docker, commit or push was run. Independently hashed current source/spec/dossier/artifact bytes and compared every candidate-manifest entry. Reviewed real browser receipts as earlier focused evidence, not final-candidate gate completion. Current CI snapshot and local running-process record are copied into `evidence-snapshot.json`; that is a point-in-time observation, not a passing run.

## Required correction

**SEC-01 — P2 — OAuth metadata does not enforce the configured environment's hosted authentication endpoint allowlist.**

Evidence: `apps/mobile/src/services/api.ts:535` accepts expected environment/issuer/client. Its endpoint loop at **581–602** checks HTTP(S), HTTPS in QA/prod, userinfo and fragment, but compares neither hostname/origin nor endpoint path/query with an independent configured value. `apps/mobile/src/platform/config.ts:6` pins API/issuer/client/callback but contains no independently configured hosted-auth origin. A metadata body retaining its expected issuer/client/environment while replacing `auth.token_endpoint` with `https://foreign.invalid/oauth2/token` satisfies these visible checks. This is a source-derived counterexample, **not an executed exploit**. `apps/mobile/src/services/auth.ts:87` passes the metadata authorization endpoint into the system browser; **153–161** posts authorization code/verifier or refresh token to the supplied token endpoint; **344–364** posts the captured refresh token to the supplied revocation endpoint. `restore()` at **44–60** also validates saved issuer/client but not saved endpoint identities.

Requirement: canonical `android-sign-in/spec.md:21` requires environment-allowlisted metadata; AND-AUTH-001 at **45–47** requires configured issuer/client/redirect/state separation and runtime endpoint override rejection. Primary affected specs OTGD-001 (SEC-004), OTGD-020 (AND-ENV-001), OTGD-037 (AND-AUTH-001); account consumers depend on the same fix.

Impact: an incorrectly configured or tampered app-config response can redirect credential-bearing OAuth exchanges to a foreign HTTPS endpoint while passing the current identity checks. API TLS is still a prerequisite for such tampering; this finding does not claim an unauthenticated Internet attacker can alter valid TLS responses. The missing independent pin also defeats the specified protection against metadata/configuration mistakes.

Required correction: pin a separate admitted hosted OAuth origin and exact provider endpoint paths into the build, alongside issuer/client/callback. Cognito's hosted domain **differs from its user-pool issuer**; do not derive the former by treating them as the same origin. Apply one validation policy before browser authorization, code exchange, refresh and revocation, and before activating restored credentials. Reject foreign origin, userinfo, query, fragment, unexpected path, protocol or port; retain valid local and configured separate Cognito origins. Preserve current exact callback checks, entropy/state, PKCE S256, one-use/expiry guard, captured-family logout and existing offline namespaces.

Verification criterion: focused tests supply each substituted endpoint with otherwise valid issuer/client/environment, including restored auth metadata, and show refusal before any browser launch or credential-bearing fetch; valid supported local and separate Cognito hosted origins still work. Then re-execute affected exact-source auth/browser and mandatory gates. PM must consolidate with other independent findings before counted repair round.

## Evidence holds and import work

**SEC-E01 — P2 acceptance evidence hold, BLOCKED/pending, not an additional code correction.** At CI snapshot `ci-jobs-0739.json`, run `40173151613` is bound to this candidate and reports 13 currently visible jobs: unit/ATDD/components/PG/contracts/protected-reader/shared-firmware/Fargate runtime success; localstack/native Android+iOS/preview Android+iOS pending. Aggregate merge-gate is not yet visible and all fourteen final success is unproven. Local record `gate-process.json` says running; log snapshot contains only `RUN unit-coverage`. No final unit coverage >80%, full live/browser/worker matrix, native/device or complete local gate success is established by this snapshot. Action: verification owner finishes real gates, supplies raw current-source outputs/coverage and immutable hashes; reviewers re-admit material final evidence. No denied action exists; evidence is **pending**.

**SEC-E02 — P2 dossier acceptance hold, pending PM import; no repository change requested during freeze.** Every council header still identifies the baseline implementation and PENDING, e.g. `specs/OTGD-037/council.md:7` and **11**. The OTGD-001 and OTGD-047 council/product/engineering header hashes are stale (six files), as enumerated in bindings.json. Actual canonical OTGD-001 is `c8f052979fd2a15da2d0bc09c8533bde246cdc559d798696af728378cf5850f7`; OTGD-047 is `b5523be8de175f257dda911b52b94732ae4e5e838b49cd9c38bea7802d0670c4`. Neither a pending header nor a historical implementation revision is a completed current signoff. Action: PM imports independent reports at the coherent D-008 boundary and updates bindings while retaining historical results and tested candidate identity. Independent product/engineering and final approval prerequisites remain required. This expected import work need not consume a code correction round.

## Security observations and limits

- Auth repair preserves PKCE S256 and generates `newId()` state (`auth.ts:77–85`); native uses `Crypto.randomUUID`. Local issuer still requires state 16–256, exact callback and S256; account-choice POST still requires issuer Origin and bound browser cookie (`local_identity.py:188–215`, **239–245**). CSP adds only configured web origins (`124–135`), with exact redirect checks retained. Captured logout revocation checks non-2xx and is attempted even if earlier logout work fails (`controller.ts:4906` onward, `auth.ts:344–379`). Runtime success remains for the verification owner.
- API RS256/issuer/client/token_use/access claims and current family/account checks are present (`auth.py:25–93`, **113–181**). No decoded email selects a local namespace. Native account storage checks SQLCipher and fails without it; keys use SecureStore/Keychain and encrypted workspace initialization has no plaintext fallback (`storage.native.ts:20–115`). Physical secure-storage/keychain inspections and hosted Cognito journeys are still external evidence.
- Download reads owned current generation, exact output version/length/hash and authority before bytes, after delayed S3 read and before each <=64KiB chunk; response cancellation releases its slot (`main.py:1935–2028`). Deletion creates generation/write fence before journal dependency (`1872–1917`). Worker rechecks current lease/authority before commit, clears health/dedup state, retains minimal receipts and sweeps late old-generation versions (`worker.py:59–115`, **371–467**, **679–745**). These are inspected controls, not a replacement for concurrent live tests.
- Research capture rejects simulated required channels and requires current qualified-measurement dependencies (`model_engine.py:714–795`); current publication is rechecked by `worker.py:379–382`. Data-only evaluation explicitly says external approval/custody is unverified (`tools/model_evaluation.py:760–763`) and no-follow/nonblocking bounded file reads exist (**771–785**). HR-only/optical limitations are explicit; no fictional fixture establishes research eligibility.
- Protected reader has secure boot/flash-encryption/encrypted-NVS prerequisites and authenticated secure-connections/MITM/bonded origin checks (`ProtectedSigner.h:36–52`, `ReaderLifecycle.h:47–56`). Signed grants and one-use origin-bound nonces remain required (`nano_esp32_signed_reader.ino:189–219`). Compilation is separate from provisioning, electrical safety, calibration and physical BLE qualification.
- Live defaults now require all fourteen configured jobs (`deploy/provenance.py:26–34`, **130**, **225**); historical thirteen-job signed projection is explicitly separate (**99–112**, **215**). Inspected current release callers retain live checks. Explicit legacy selection is limited to original recovery callsites; no release or recovery was executed.
- Worker fixture refuses canonical/remote/adopted DB/resources, creates a random dedicated DB/buckets/queues, uses restricted runtime DB role and signals only its own spawned child (`worker_interrupt_gate.py:23–53`, **101–167**; `worker_interrupt_probe.py:51–102`, **199–328**, **481–535**). Real SDK calls remain delegated; no timing/assertion bypass was observed. Browser helper uses reserved identities and private ledger, checks preexisting inventory before all-data deletion (`browser_fixture.py:65–103`; authenticated-live.spec.ts:276–309, **711**); tracing/HAR/video are disabled. Local fictional staff principals are clearly labeled and do not establish cloud/scientific independence.

No other confirmed product-security defect was identified in this bounded source review. This is not a formal penetration test or proof of absence of vulnerabilities. Native device, actual QA/prod IAM/KMS/private networking, scientific approvals, store signing and genuine hosted delivery are unverified here and are not authorized actions for this review.

## Explicit per-spec decisions

Each row is an independent security-domain IMPLEMENTATION decision for this candidate. **BLOCKED** means no additional source correction identified for that spec, while SEC-E01/E02 prevent completed implementation acceptance. **CHANGES_REQUIRED** identifies SEC-01's primary requirements; all account-dependent consumers must receive revalidation after its shared fix. Canonical paths and exact hashes for every row are in bindings.json. No aggregate PASS substitutes for these rows.

| Spec | Security decision | Evidence-backed rationale |
|---|---|---|
| OTGD-001 | CHANGES_REQUIRED | Requirement register SEC-001–007, claim boundaries, identity and release traceability; SEC-01 applies. |
| OTGD-002 | BLOCKED | Dashboard research/guest provenance and server-admitted scope; ordinary results remain measurement-only. |
| OTGD-003 | BLOCKED | Explicit local save versus authorized upload; original result/target times and no driving clearance. |
| OTGD-004 | BLOCKED | Historical research schema/ownership and immutable qualifier/time display. |
| OTGD-005 | BLOCKED | Onboarding and sign-in cannot create enrollment, sensing or model authority. |
| OTGD-006 | BLOCKED | Legacy estimate rejection; independently linked ResearchResult 1.1.0 admission. |
| OTGD-007 | BLOCKED | Capability/environment settings cannot grant authorization or bypass qualified capture. |
| OTGD-008 | BLOCKED | Bounded data-only evaluation input custody, partition locks and unverified external research assertions. |
| OTGD-009 | BLOCKED | Current independently released model/capture authority, nonsynthetic required channels and publication recheck. |
| OTGD-010 | BLOCKED | Raw export grant/purpose separation; exact source versions; authenticated bounded chunk re-admission and recurring erasure. |
| OTGD-011 | BLOCKED | Typed immutable registries, three distinct principals, current capabilities, signed capture and raw evidence. |
| OTGD-012 | BLOCKED | Current scoped optical start; bounded ephemeral ROI; originating lifecycle and encrypted persistence. |
| OTGD-013 | BLOCKED | Protected provisioned P-256 signer, one-use signed starts, origin-bound authenticated encrypted BLE; physical qualification separate. |
| OTGD-014 | BLOCKED | Private immutable web origin, exact public identity, provenance and browser security headers. |
| OTGD-015 | BLOCKED | Current live fourteen-job release admission, distinct roles and immutable cloud attempts; no deployment claimed. |
| OTGD-016 | BLOCKED | Independent journal recovery admission and exact fresh reapproval; database flags alone insufficient. |
| OTGD-017 | BLOCKED | Local-only fictional hosted mode, no account/network/acquisition, isolated guest records. |
| OTGD-018 | BLOCKED | Default-off raw consent and upload, durable revocation fence, encrypted commit, retention and separate raw export. |
| OTGD-019 | BLOCKED | Synthetic alcohol remains separate and measurement-only; mg/L calibration/quality provenance. |
| OTGD-020 | CHANGES_REQUIRED | Compiled environment identity and protected deployment/recovery boundary; SEC-01 endpoint pinning gap. |
| OTGD-021 | BLOCKED | Current capability and source display; workspace-race fencing and explicit uploads. |
| OTGD-022 | BLOCKED | Owned selected export, explicit raw exclusion/authorization, bounded versioned archive and protected delivery. |
| OTGD-023 | BLOCKED | Untrusted advertisement, registry-owned binding, bounded framing and lifecycle; real hardware qualification remains external. |
| OTGD-024 | BLOCKED | Human ECG safety gate, scoped authorization and encrypted optional waveform; no participant qualification claimed. |
| OTGD-025 | BLOCKED | Optical preview versus qualified capture, ephemeral images, current authorizations and separate retention/upload. |
| OTGD-026 | BLOCKED | Immutable context/attempt identities, stop-before-navigation, durable local save and separate explicit upload. |
| OTGD-027 | BLOCKED | PPG source/quality preserved, fresh scoped starts and no synthetic/ECG substitution. |
| OTGD-028 | BLOCKED | Active workspace ownership, pagination, immutable evidence and deletion reconciliation prevent resurrection. |
| OTGD-029 | BLOCKED | Durable encrypted queue, stable idempotency and owner/environment isolation; original acquisition time retained. |
| OTGD-030 | BLOCKED | Notice receipt and workspace separation; onboarding/OS permissions do not create scientific authority. |
| OTGD-031 | BLOCKED | Reauthenticated owned deletion, immediate generation fence, truthful async completion and recurring version erasure. |
| OTGD-032 | BLOCKED | Optional/declined profile values, owned revisioned drafts and immutable frozen context. |
| OTGD-033 | BLOCKED | Native originating attempt/timing, bounded raw events and stop-on-interruption; no sensing validity implied. |
| OTGD-034 | BLOCKED | Exact result/session/digest linkage, null/provenance handling and bounded cancelable polling. |
| OTGD-035 | BLOCKED | Participant collection versus independently authorized lab import; exact specimen, units, source and role. |
| OTGD-036 | BLOCKED | Permissions read without prompt and epoch-fenced responses; diagnostics allowlist and capability integrity. |
| OTGD-037 | CHANGES_REQUIRED | PKCE/state/single-use and logout improved; missing OAuth endpoint allowlist is SEC-01. |
| OTGD-038 | BLOCKED | Owned invitation and exact consent; fresh starts, withdrawal fence and no seeded genuine membership. |
| OTGD-039 | BLOCKED | Immutable fresh instruction receipt and stop-before-privacy transition; declarations never safety proof. |
| OTGD-040 | BLOCKED | Exact owned specimen/configuration and independent staff import/report custody; collection cannot self-authorize analytics. |
| OTGD-041 | BLOCKED | Prespecified HR-only evaluation keeps missing comparisons explicit and does not grant external authority. |
| OTGD-042 | BLOCKED | Restricted HR timing/calibration/quality/baseline policy; numeric output re-admits current authority. |
| OTGD-043 | BLOCKED | Pinned selected SDK, fresh bounded FIFO and signed current origin; software success does not qualify physiology. |
| OTGD-044 | BLOCKED | Complete exact security headers/private route and bounded signed public response bytes. |
| OTGD-045 | BLOCKED | Exact CNAME ownership and immutable DNS creation; bounded private release authority input. |
| OTGD-046 | BLOCKED | Fixed unavailable public API/issuer in guest export, verified private forwarded service and accurate hosting claims. |
| OTGD-047 | BLOCKED | Current source/live gate and actual signed artifact/store submission safety; all release execution remains external. |

Prior review disposition: this reviewer issued no earlier signoff; earlier author-focused passes are not adopted as complete candidate gates. The PM has the initial independent finding through native messaging. Reaffirmation of unchanged code is limited to the specific inspected trust boundaries above, with current byte hashes, and does not carry historical runtime PASS forward.

Remaining blockers: SEC-01 requires consolidated code correction; SEC-E01 final execution evidence is pending; SEC-E02 current dossier import and independent approvals are pending. No tool action was denied and no external mutation has an uncertain outcome in this review.
