# Consolidated correction round 1

Run `otgd-20261025-0555`; reviewed candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; Factory `4770878e18e9c587c2961b9e2bb13315da31abe9`.

## D-009 v1 — ACCEPTED: first consolidated correction round

Authority: the approved software build scope and six actual independent initial reviews. All reviewers verified the current canonical specification hashes and frozen candidate. Their reports remain unchanged as initial review history. This is correction round **1 of 2**, separate from **0 PM recovery attempts**. No scope expansion, relaxed requirement, deployment or participant authorization follows.

Resolve these verified findings together:

1. SEC-01 / CODE-002: independently pin hosted OAuth origin, supported endpoint paths and callbacks; validate fresh metadata and restored credential-family metadata before browser/token/revocation traffic. Preserve Cognito issuer/hosted-origin distinction, PKCE/state/nonce and the repaired API-before-provider logout order. Reject invalid metadata before credential-bearing calls; test fresh, restored, exchange/refresh/revocation paths.
2. PROD-001 / UX-001: derive saved-record status and research/measurement scope from verified results/current account capabilities; preserve invalid/inconclusive states without fabricating research authority. Correct Home and History labels.
3. PROD-002: explain default measurement mode and separately authorized research access in onboarding without implying enrollment or model authority.
4. PROD-003: display the supplied, verified uncertainty policy/limits for admitted research results; never invent a confidence interval or clinical meaning.
5. UX-002: move accessibility focus to destination headings on navigation with supported web/native behavior and preserve existing scroll/restoration and fixed task stimuli. Actual OS assistive-technology execution remains separately required.
6. UI-001: use a theme-appropriate destructive-button foreground meeting 4.5:1 in both themes, and verify actual rendered destructive states.
7. UI-002: implement the effective system/user reduced-motion preference for ordinary UI animation while preserving fixed scientific task stimuli.

Engineering ENG-SIGN-001/002/003 are evidence prerequisites: current final local and all14 CI jobs, explicit per-case assertion/result reconciliation, and actual native OS/UI integration. They cannot be cleared by implementation or aggregate claims. The verification specialist owns the 782-case reconciliation. External scientific, hardware, participant, native-device and release prerequisites retain explicit gaps.

Before repository edits: stop the reviewed candidate's local test runner at a coherent boundary, preserve all completed/failed/interrupted outputs and exact source binding, and verify no test child remains. Do not stop or reset canonical PostgreSQL/LocalStack/API/identity/worker or their data. Current CI may finish for the reviewed candidate; a new push must receive its own exact-tree CI evidence.

After repairs: freeze a new candidate; execute the unchanged mandatory gate assertions; obtain affected independent rereviews with current hashes and explicit per-spec decisions. Six reviewers cannot sign their own corrections. The fresh final approver remains gated on actual prerequisites, and must not be simulated.

Planned ownership: OAuth builder owns build/environment/auth/API admission plus direct tests and necessary nonsecret packaging plumbing; product builder owns research presentation helpers/account/check screens and direct tests; accessibility builder owns shared UI/theme/motion/navigation and actual component tests. Coordinate any shared file before editing. PM owns journals, gate integration and source freeze.

Verification supplement V-CORR-001: OTGD-008-EVAL-008-02 requires deterministic descriptor-change-during-read regression. Existing source guard is present; add the missing acceptance assertion without changing limits or scientific meaning.
