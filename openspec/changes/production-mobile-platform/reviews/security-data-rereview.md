# Security and data-integrity targeted re-review

Review scope: resolution of SEC-001–SEC-014 from [the preserved independent review](security-data-review.md). This report records specification closure after amendments; it does not replace the original Open findings or represent runtime test results. The root-owned shared/platform/API contracts and other authors’ feature corrections were cross-reviewed; the author’s seven capture-feature amendments were additionally reviewed independently by the product reviewer.

**Disposition: all 14 original findings are resolved in the reviewed specification snapshot. No original Critical/High/Medium design blocker remains open in this lens. Implementation and its required failure-injection tests remain pending.** Qualified human hardware, real studies, retention approvals, physical timing, and impairment inference remain unavailable without their independent evidence. Nothing in this report closes a scientific gate or asserts a shipped mobile/cloud build.

## Resolution evidence

| Finding | Original severity | Corrected sections and enforceable decision | Status |
|---|---|---|---|
| SEC-001 | High | [Shared contracts](../shared-contracts.md) §§2–3 carry server-issued `data_generation` through every protected mutation, queue, job, and evidence record; account-row locking serializes deletion and writes. Stale generations receive 410, cannot replace their generation on old payloads, and cannot replay deleted response bodies. `all_data` requires explicit new-empty-workspace acknowledgment. [Platform contract](../platform-contract.md) §§6–8 add fenced worker commits, a restore-independent versioned deletion journal, post-backup barriers, both-scope keyed issuer/subject references, and fail-closed restore watermarks. Minimal idempotency metadata lasts the writable generation without retaining deleted response content. AND-SYNC-003/004/005, AND-PRIV-005 and AND-PRO-003/004/005 integration clauses apply the same transport rule. | Resolved in specification; concurrency/restore tests pending. |
| SEC-002 | High | Shared §2 checks current application account state and `origin_jti` revocation in addition to RS256/issuer/client/token-use/time verification. Deleted-subject tombstones prohibit implicit recreation; restore requires fresh authentication after its durable cutoff and independently reconciles suspended study/capture permissions. Sign-out revokes the current family and locks the local namespace. A narrow same-family exact-key/body/generation replay returns only the accepted minimal logout receipt, so idempotency does not reopen record access. AND-AUTH-003–006 distinguish offline local logout from confirmed remote revocation and retain only the documented post-deletion receipt path. | Resolved in specification; JWT/revocation tests pending. |
| SEC-003 | High | Shared §§5–6 freeze P-256 SPKI key encoding, DER ECDSA/SHA-256 signatures, exact domain-separated JCS transcripts, server-supplied nonces/transcripts, atomic challenge consumption, registry versions, and a typed capture-attestation endpoint. The signed envelope binds environment/owner/generation/session/attempt/authorization/binding/device/key/boot/sequence/configuration/payload digest. The backend verifies exact normalized-value mapping, not a `source` string. Context/attempt/manifest 1.0.0 preserves proof without weakening strict v0.1. AND-DEV-003–006, AND-SAL-002/005, AND-HR-003 and AND-ECG-003 retain the references. | Resolved in specification; actual provisioning and negative proof tests pending. |
| SEC-004 | High | Shared §7 and AND-EXP-002/004/005 replace direct S3 bearer GET delivery with authenticated `GET /v1/privacy/jobs/{job_id}/download`, checking current ownership/generation/policy/job/expiry at stream admission and reading the pinned version. Copied paths grant no authority. Revocation before admission blocks a new stream; already delivered or admitted bytes are explicitly not recallable. AND-STUDY-004/005 and privacy integration use that same boundary. | Resolved in specification; revoke-before-download and stream-limit tests pending. |
| SEC-005 | High | Shared §7 and platform §5 require versioning in every environment, non-null verified `VersionId`, exact-version bounded hash/media verification, account/policy commit rechecks, and version-pinned reads/exports/copies. Signed conditional PUT creation additionally prevents ordinary repeated overwrite; S3 412 reconciles the existing object. No deletion of its current object before ticket expiry plus the stated margin can reopen conditional reuse. All versions/markers are included in scoped deletion and orphan cleanup. Eye/ECG/PPG artifact clauses reference the same immutable version rule. | Resolved in specification; actual LocalStack and QA S3 race tests pending. |
| SEC-006 | High | Shared §6 deliberately prohibits offline qualified starts in this release. Cached capabilities are display-only. A fresh issued grant must be atomically consumed through `/capture-authorizations/{authorization_id}/start` under current account/authorization locks within its 60-second server start window; the app rejects a receipt round trip over five native-clock seconds and never activates from cached replay. The start window is distinct from the approved channel’s maximum duration. Withdrawal intent stops local capture immediately; backend scope is checked again at attestation/upload/finalization. AND-CHECK-002/006 and all qualified sensor gates apply this rule. | Resolved in specification through the explicit no-offline-qualified-start policy; time/replay/revocation tests pending. |
| SEC-007 | Medium | Shared §1 fixes `inference_available=false` in client/service with no remote override. `research_estimate` is rejected as `UNSUPPORTED_RESEARCH_RESULT` in live/cache/history/import/export paths, even with a valid-shaped signed record. AND-CHECK-007, AND-RES-003, AND-HIST integration and AND-SET-004 consistently retain null probability. Future schema vocabulary does not enable the current product capability. | Resolved in specification; every-entry-path result fixtures pending. |
| SEC-008 | Medium | Shared §5, AND-CHECK-001/002/004, AND-PRO-003 and dashboard creation scenarios choose Start check as the atomic UUID/profile/context freeze; `created_at=target_at=context_confirmed_at`. Profile in the created check is read-only even before first capture. Later profile changes require a linked new check and do not move its original target or evidence. Mutable real-time context is explicitly reviewed before that event. | Resolved in specification; first-check/remote-edit/replacement tests pending. |
| SEC-009 | Medium | Shared §4 freezes 428 missing precondition, 412 stale If-Match, 409 immutable-state/idempotency conflict, and 410 retired generation. Shared §7 defines PrivacyJob 1.0.0 with `kind=export|deletion`; `expired` is export-only and `partially_retained` deletion-only, with precise retained categories. AND-SYNC-005 and privacy/profile/export contracts use the same registry and unknown-state refusal. Technical partial cleanup remains failed rather than policy-complete. | Resolved in specification; shared error/job transition fixtures pending. |
| SEC-010 | Medium | Shared §4, design API inventory, and AND-ONB-003 define same-origin `GET /v1/notices/{version}` returning bounded English plain text, exact UTF-8 SHA-256, version and mandatory state. The app verifies the actually displayed content before acknowledgment, renders no remote HTML, and caches permitted content. The acknowledgment and authorized history/export/deletion/withdrawal/sign-out escape paths are exempt from the old-notice write block. | Resolved in specification; old-bundle/new-notice and hash-failure tests pending. |
| SEC-011 | Medium | AND-TASK-002–008 and the pre-code JSON fixtures fix platform-specific native onset estimates, UInt32 scheduling, half-open response windows, equal-time touch ordering, 100-ms frame/dispatch/lateness limits, a 100-ms final event drain, exclusive terminal input cutoff, and cancel-before-commit precedence. Literal seeds 0/1/4294967295 and 14 input plus 11 aggregate/race vectors retain exact expected behavior. Requested software presentation constants are hashed; physical onset/luminance remains unverified. | Resolved in specification; Kotlin/Swift/native-lifecycle and physical timing tests pending separately. |
| SEC-012 | Medium | Shared §9 and AND-CHECK-005/AND-TASK-006/007 require native stop acknowledgment and terminal invalid settlement in the original namespace before any route/tab/workspace transition or stimulus-hiding overlay, including navigators retaining mounted views. Later Keep draft/Stay cannot resume a run. Late events check epoch/run/hash. Onboarding, settings, profile and sign-out apply the same orchestration guard. | Resolved in specification; mounted-hidden-view and cross-account late-event tests pending. |
| SEC-013 | Medium | Shared §1 and AND-TASK-007 keep actual native taps `prototype_sensor` with native method and `uncalibrated`, allowing mixed provenance only through the explicitly local mobile demo adapter. Actual JS fallback taps retain `javascript_fallback`, never native acquisition. Guest demo never uploads/migrates on sign-in. Separate signed-in local/QA fictional engineering records need explicit Upload check. The Python CLI remains all-fictional. | Resolved in specification; mixed local export/zero-upload and original CLI checks pending. |
| SEC-014 | Medium | Shared §8 and design API inventory explicitly define GET/POST `/v1/sessions/{session_id}/alcohol`, version 1.0.0, owner/generation/idempotency, separate mg/L/provenance, pre-finalization selected attempt/hash, immutability afterward, and linked correction/history/export behavior. AND-ALC-002–005 keep it outside the cannabinoid enum and strict v0.1 snapshot. | Resolved in specification; separate alcohol route, foreign-owner, and immutability tests pending. |

## Targeted consistency checks

The re-review checked the principal requirements and the ID-mapped long contracts together. The short OpenSpec format does not remove field, lifecycle, provenance, or failure rules. Across capture/navigation/storage the selected behavior is local save first, explicit eligible-account upload, default-off automatic retries for already requested uploads, no guest migration, and new assessment identity/time after a finalized invalid check. Before finalization, a retry preserves the same parent and links a new attempt; after finalization, no physical component is carried into the replacement. The selected v0.1 cardiac component remains PPG **or** ECG, while earlier alternatives stay in the companion manifest.

Full native task evidence remains bounded and hashed in the 1.0.0 companion record; the v0.1 result’s `input_sha256` remains its original snapshot hash. The additional manifest digest is separately bound in immutable result metadata and the `X-Evidence-Sha256` header. The shared contract requires consumers to verify both. No raw waveform/frame payload is smuggled into metadata, and absence of uploaded evidence is visible rather than represented as a complete cloud record.

The reaction fixture was further corrected after independent product review to pin requested colors, arrow geometry, font/point-size policy, and native End task hit targets. At the minimum 240×400 logical-point view, the 120-per-mille native End target is at least 48 Android points and 44 iOS points high and is excluded from scoring. These software choices cannot prove equivalent physical luminance, font rasterization, display latency, or touch latency between devices.

## Evidence performed in this document phase

- Structural checks on the seven capture specs found **52 requirements and 126 GIVEN/WHEN/THEN scenarios**, with every principal requirement paragraph under 500 characters.
- Configuration/schedule digest checks verified all fixture hashes, 66-trial counts, practice/scored stimulus counts, and the final onset+1100-ms cutoff relation. The product reviewer independently checked the schedules against the stated LCG/Fisher–Yates rules and reviewed the capture-contract amendments.
- No native application implementation, Android/iOS compile, runtime API test, S3 experiment, or clinical test was performed for these closures. The local `npx --no-install` OpenSpec attempt found no installed package and did not install one; the root’s configured strict validator is the authoritative combined-document check.

Required runtime tests remain the original review’s acceptance targets plus the platform/feature ledgers. A later implementation report must state actual executed environments and unexecuted physical/cloud rows. The native configuration remains `model_eligible=false`, `calibration_status=uncalibrated`, and `physical_onset_verified=false`.

## Reviewed feature coverage

All 20 features from the original review were included in the targeted correction check. This ledger is coverage, not an assertion that they are implemented:

| Feature | Re-review focus |
|---|---|
| android-alcohol-channel | separate typed routes, unit/provenance, immutable manifest selection |
| android-app-environment | issuer/storage separation, deployment inputs, recovery limitations |
| android-dashboard | single session allocation, immutable context, explicit upload |
| android-data-export | scope stability, authenticated gateway, pinned versions, size refusal |
| android-device-pairing | registry trust, signed envelopes, replay, online authorization |
| android-ecg-capture | whole-system gate, immutable waveform versions, one-modality selection |
| android-eye-capture | display-only cached capabilities, immediate stop, versioned raw artifacts |
| android-guided-check | context/evidence, retries, stop-before-overlay, local save and upload |
| android-heart-rate | PPG evidence, current authorization, missing/stale values |
| android-history | owner/generation caches, disabled inference, immutable evidence |
| android-offline-sync | explicit queue action, generation tombstones, error registry, both digests |
| android-onboarding | notice retrieval, mixed-demo provenance, immediate navigation stop |
| android-privacy-controls | deletion generations, recent identity, exact job states and receipts |
| android-profile | Start check freeze, generation and If-Match semantics |
| android-reaction-task | fixed native timing/presentation/ordering/drain fixtures and mixed provenance |
| android-results | disabled inference, immutable hashes, historical target and replacement |
| android-saliva-measurement | signed normalization, complete sample lineage, replacement/correction |
| android-settings-accessibility | release flag limits, fixed task presentation, active route guard |
| android-sign-in | current account/token-family revocation, local partition lock, logout receipt |
| android-study-enrollment | withdrawal intent, online qualified starts, artifact verification authority |

## Snapshot identifiers

Review timestamp (UTC): 2026-10-11T02:35:39.219760+00:00. SHA-256 below covers each complete UTF-8 source file in this re-review snapshot, not its Git object or canonical JSON digest. If a later edit changes a substantive rule, this report’s closure must be reassessed for that edit. JSON configuration/schedule canonical digests are separately stored in the fixture itself.

| Source | File SHA-256 |
|---|---|
| [proposal.md](../proposal.md) | `c8085ebaef0b795339b1a9f0623a895c85d6dfd16e65f0c730e9e94e6a02dade` |
| [design.md](../design.md) | `cee76281c243bb125e81e8bd04700c8f230ca6d4bf387f4aa9a9527394bfc166` |
| [shared-contracts.md](../shared-contracts.md) | `942449a03f2135147cef934ffafad5757906e27923ebeef20aca507e0f4fd0df` |
| [platform-contract.md](../platform-contract.md) | `f346c783b13604f9c86221c47cb592250d05c719a68ea5c7cac2db0d27cb5936` |
| [specs/android-alcohol-channel/spec.md](../specs/android-alcohol-channel/spec.md) | `6c423c75ae449e935fe8856f61d70af07aaab582719baba1d1e1bc63d787f45a` |
| [specs/android-app-environment/spec.md](../specs/android-app-environment/spec.md) | `7cd3451fd8c13cd25bdc66403e879de3f9fe0e127e3655f2ed40017869916f76` |
| [specs/android-dashboard/spec.md](../specs/android-dashboard/spec.md) | `c756e1eb65e8b3e9929a58c4c191e7c179529f8cd238da6e9cd6b5403439105e` |
| [specs/android-data-export/spec.md](../specs/android-data-export/spec.md) | `2e02ae2e4ea75c4e789b29399dee2b6e4206f12ecb81630b04ca54c4a6e1ef30` |
| [specs/android-device-pairing/spec.md](../specs/android-device-pairing/spec.md) | `c772a370e6d80b6568ad3d210081934ac57ecb9e7449e7e776efeb776cdd98c4` |
| [specs/android-ecg-capture/spec.md](../specs/android-ecg-capture/spec.md) | `c75f24b4beeda893b780af0d924747c0cd7ca599ead627d3d265f21ec3772895` |
| [specs/android-eye-capture/spec.md](../specs/android-eye-capture/spec.md) | `bfb351373c6c3c2d33fd74fa1537ed0c610aa65624e5ce0e8c07fa8f5d1a6cf8` |
| [specs/android-guided-check/spec.md](../specs/android-guided-check/spec.md) | `cef15148de295ecabe3b38d6f9b2d45530b60993c1aacf1b41e1b4fc495c6562` |
| [specs/android-heart-rate/spec.md](../specs/android-heart-rate/spec.md) | `e9288b9fbec177d7287962239555b7633a0cfbf80ecf3e1e350158da607f5139` |
| [specs/android-history/spec.md](../specs/android-history/spec.md) | `eb9f89e04620ed296b248ce076e2c5447df6c5fb2c9da0eb9fa90725f2bd99a2` |
| [specs/android-offline-sync/spec.md](../specs/android-offline-sync/spec.md) | `388f00c1fab3eb1f905e140b7248ce8e737ae87349eb8a508068becbb51456b9` |
| [specs/android-onboarding/spec.md](../specs/android-onboarding/spec.md) | `da9837761a2034853336456f15dc249daf23aed73a9808bbdf4b1b690eda53ee` |
| [specs/android-privacy-controls/spec.md](../specs/android-privacy-controls/spec.md) | `993e7c0f65b5ee4bd9b2f470e2d4111f6329f083e7650a76ab71f78abf5e9f3f` |
| [specs/android-profile/spec.md](../specs/android-profile/spec.md) | `b90bbf657f3c8e8a24eab7ab93f04c680018bbe2179131c1b8aa70c6d3d67a43` |
| [specs/android-reaction-task/spec.md](../specs/android-reaction-task/spec.md) | `1c5bfceae8b4e2b5e1bd8c9edd7f19fd73908cde1fb804af4e9530700d3ea317` |
| [specs/android-results/spec.md](../specs/android-results/spec.md) | `dadd53ea7fd8027bb76d17c26e51d4910cc3c8763bfd8a838434fbf8112397ba` |
| [specs/android-saliva-measurement/spec.md](../specs/android-saliva-measurement/spec.md) | `6edc6d7603b66733858b1f7fe42dc93d22712dd8cadbac29121a65f2ffd23610` |
| [specs/android-settings-accessibility/spec.md](../specs/android-settings-accessibility/spec.md) | `2be76edc1d36d1f4471c8fbfa4e15e1e416fc078c9e6ca522c230d3cfe4dd63b` |
| [specs/android-sign-in/spec.md](../specs/android-sign-in/spec.md) | `b20292aa0a4f47fa00fa5e652eafd1dffdd75e2a710ac2b0165f5f2ae4e2a1bd` |
| [specs/android-study-enrollment/spec.md](../specs/android-study-enrollment/spec.md) | `e0c8f1f81be37cbe775f274e6c2aa81d3f3eacc64da92f01bcdd1c31adfb9ee8` |
| [fixtures/reaction-task-config-v1.json](../fixtures/reaction-task-config-v1.json) | `62bdf0bf1115c267269654d0f438ac14e6c5b1c97587c72e1d1d88ad4c7528ea` |
| [fixtures/reaction-task-golden-v1.json](../fixtures/reaction-task-golden-v1.json) | `0d4d25e24b812a90eb81715c53e3314740a71823531c5f2eaac93beda78897d7` |
| [fixtures/README.md](../fixtures/README.md) | `e40e8695adb63e889721779f3a3449d38fbbf2487425fc7c10238f808aa80c2d` |
