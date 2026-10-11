# Adversarial review resolution ledger

The independent review snapshots are preserved unchanged as findings at issue. This ledger and the targeted re-review reports record their disposition. **Resolved in specification** means the normative contract is corrected; it is not a claim that code, a physical device, or an AWS deployment has passed testing. All 20 features were covered by three review perspectives.

## Findings and corrective contracts

| Finding | Severity | Normative correction | Re-review |
|---|---|---|---|
| UX-001 | High | Shared §1; Results/History/Guided Check reject current-release research estimates | [Resolved in specification](product-domain-rereview.md) |
| UX-002 | High | Shared §5 companion context/attempt/manifest/attestation DTOs, routes, hash and projection binding | [Resolved in specification](product-domain-rereview.md) |
| UX-003 | High | Shared §5; finalized retry becomes a new replacement check/time without copied physical acquisitions | [Resolved in specification](product-domain-rereview.md) |
| UX-004 | High | Shared §1 workspace/upload matrix and explicit local-save/upload/retry precedence | [Resolved in specification](product-domain-rereview.md) |
| UX-005 | High | Shared §2 explicit keep/remove logout choices, same-account reauthentication, OS local unlock | [Resolved in specification](product-domain-rereview.md) |
| UX-006 | High | Shared §6 online-only qualified starts, immediate local withdrawal intent, server acceptance checks | [Resolved in specification](product-domain-rereview.md) |
| UX-007 | High | Shared §7 authenticated gateway and explicit already-authorized-stream limit | [Resolved in specification](product-domain-rereview.md) |
| UX-008 | High | Shared §7 kind-discriminated job states and retained/failed semantics | [Resolved in specification](product-domain-rereview.md) |
| UX-009 | High | Shared §4 428/412/409/410 and exact idempotency/revision handling | [Resolved in specification](product-domain-rereview.md) |
| UX-010 | High | Native task engineering configuration, event-drain/tie/deadline rules and golden fixtures | [Resolved in specification](product-domain-rereview.md) |
| UX-011 | Medium | Shared §5 Start check freezes context and target time; later edits need a new check | [Resolved in specification](product-domain-rereview.md) |
| UX-012 | High | Shared §7 typed single/selected/all export, fixed associated profile/attempt/result scope | [Resolved in specification](product-domain-rereview.md) |
| UX-013 | Medium | Shared §9; Home Alcohol measurement and Settings Research access entries | [Resolved in specification](product-domain-rereview.md) |
| UX-014 | High | Shared §9 immediate native stop before overlay/navigation; no invalid-run resume | [Resolved in specification](product-domain-rereview.md) |
| UX-015 | Medium | Shared §9 SDK/OS targets and explicit simulator/device/accessibility evidence matrix | [Resolved in specification](product-domain-rereview.md) |
| SEC-001 | High | Shared §3 account generation, queue/header/worker barriers, limited deletion replay, sensitive replay erasure | [Resolved in specification](security-data-rereview.md) |
| SEC-002 | High | Shared §2 per-request account state/tombstone/origin_jti revocation beyond JWT validity | [Resolved in specification](security-data-rereview.md) |
| SEC-003 | High | Shared §§5–6 exact domain-separated signed envelopes, key format, atomic challenge/start, value linkage | [Resolved in specification](security-data-rereview.md) |
| SEC-004 | High | Shared §7 authenticated download gateway with current policy admission | [Resolved in specification](security-data-rereview.md) |
| SEC-005 | High | Shared §7 and Platform §5 pin VersionId before verification and all later reads | [Resolved in specification](security-data-rereview.md) |
| SEC-006 | High | Shared §6 fresh online qualified start; cached availability never grants offline authority | [Resolved in specification](security-data-rereview.md) |
| SEC-007 | Medium | Shared §1 immutable inference_available=false across all current result paths | [Resolved in specification](security-data-rereview.md) |
| SEC-008 | Medium | Shared §5 single context-freeze event and immutable profile/history hashes | [Resolved in specification](security-data-rereview.md) |
| SEC-009 | Medium | Shared §§4/7 common HTTP and privacy-job vocabulary | [Resolved in specification](security-data-rereview.md) |
| SEC-010 | Medium | Shared §4 bounded versioned plain-text notice retrieval, digest verification and privacy escape paths | [Resolved in specification](security-data-rereview.md) |
| SEC-011 | Medium | Native task engineering configuration and final-window drain/tie/budget fixtures | [Resolved in specification](security-data-rereview.md) |
| SEC-012 | Medium | Shared §9 orchestration visibility/namespace-epoch guard and immediate native cancellation | [Resolved in specification](security-data-rereview.md) |
| SEC-013 | Medium | Shared §1 interactive mobile demo preserves actual tap provenance; CLI fixture remains all fictional | [Resolved in specification](security-data-rereview.md) |
| SEC-014 | Medium | Shared §8 explicit separate alcohol DTO/routes and pre-finalization evidence selection | [Resolved in specification](security-data-rereview.md) |
| OPS-001 | High | Shared §7; Platform §§5/8 gateway, no bearer GET, private/no-store delivery | [Resolved in specification](platform-rereview.md) |
| OPS-002 | High | Platform §7 independent durable journal, acceptance handoff, retention and restore watermark | [Resolved in specification](platform-rereview.md) |
| OPS-003 | High | Platform §6 120-second lease/visibility, 30-second heartbeat, fencing, five-claim budget and recovery | [Resolved in specification](platform-rereview.md) |
| OPS-004 | High | Platform §5 version-pinned completion, downstream access and version cleanup | [Resolved in specification](platform-rereview.md) |
| OPS-005 | Medium | Platform §8 separate logical expiry, physical cleanup objectives, version/delete-marker handling | [Resolved in specification](platform-rereview.md) |
| OPS-006 | Medium | Platform §4 concrete byte/job/account/rate limits and reservation reclamation | [Resolved in specification](platform-rereview.md) |
| OPS-007 | Medium | Platform §§1–3 private network egress/bootstrap, pool/capacity budgets and migration lifecycle | [Resolved in specification](platform-rereview.md) |
| OPS-008 | Medium | Shared §§3–8 consolidated routes, generation, error/job and evidence contracts | [Resolved in specification](platform-rereview.md) |
| OPS-009 | Medium | Platform §9 budget/tag/retention/estimate inputs and explicitly unexecuted operator delivery | [Resolved in specification](platform-rereview.md) |

## Review exit

The 38 findings comprise 22 High and 16 Medium issues; no Critical issue was identified in these review snapshots. All 38 original findings are resolved in specification in the three targeted re-reviews. Two additional product re-review findings, RER-001 and RER-002, were corrected and independently rechecked. Platform follow-up counterexamples covering conditional PUT replay, pre-account restore identity, idempotency lifetime, and restored revocations were also corrected and rechecked. There is no remaining Critical/High specification blocker for application implementation. Later code verification must exercise the failure examples and identify externally unexecuted evidence. No scientific gate is closed by this document review.
