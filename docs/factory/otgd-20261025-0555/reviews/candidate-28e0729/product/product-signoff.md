# Independent product implementation signoff — initial review

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; baseline `0844868aa543af4ab75ac5065ad48cf807b86bb3`; working-tree SHA-256 `36ed8d800edcb560ac8ca189e98b64518b3342a29458d6e91a8d943085310f8c`.

**Verdict: CHANGES_REQUIRED.** No completed product implementation signoff, APP_VERIFIED or RELEASE_READY is issued. All 47 canonical hashes match inventory and frozen candidate manifest. Each spec has its own judgment below and complete machine-readable bindings in `product-signoff.json`.

Reviewer `/root/review_product`, fresh nonauthor; configured OpenAI `gpt-6.1-sol`, high reasoning (PM dispatch confirmed). Independent effective runtime model attestation is not exposed. Factory pin `4770878e18e9c587c2961b9e2bb13315da31abe9`. Correction 0/2; recovery 0.

ACK AFFECTED: D-001–D-005 v1, D-006 v5 (v1–v4 superseded), D-007 v1, D-008 v1. Measurement defaults, fictional provenance, independent research/eligibility/study controls and separate future calibrated fuel-cell breath-alcohol mg/L scope are preserved. Local reconstructed image proof is neither original/cloud provenance nor scientific qualification.

## Consolidated findings

### PROD-001 — P2: required correction

Affected: OTGD-001, OTGD-002, OTGD-004, OTGD-021, OTGD-028; AND-DASH-001, AND-HIST-003, PRD-020, PRD-036, PRD-041. Source `apps/mobile/src/ui/account.tsx` lines 544–595.

Home service detail is Measurement-only release independent of current capabilities. Shared CheckRow uses check.frozen ? Measurements only for every frozen result. Home lacks conditional admitted research workspace distinction; HistoryScreen uses the same CheckRow for local rows.

Impact: A valid research, invalid or inconclusive saved result receives an incorrect summary and admitted users receive contradictory scope cues.

Required correction: Derive scientific row state from actual retained supported result and delivery separately; derive conditional workspace scope from current authenticated capabilities. Preserve guest/ordinary measurement default, unsupported/legacy/absent result handling and historical time; no cached result or sign-in grants current authority.

Verification: Rendered Home and History cases for ordinary/guest, pending, invalid, inconclusive, unsupported legacy, valid 1.1 research/abstention, and revoked/missing current authority. Refresh/workspace race must not retain stale admitted scope.

### PROD-002 — P2: required correction

Affected: OTGD-001, OTGD-005, OTGD-030; AND-ONB-001, PRD-029, PRD-041. Source `apps/mobile/src/ui/account.tsx` lines 74–140.

Welcome subtitle unconditionally states This release reports measurements only. Introductory scope never explains separately authorized research access, while About correctly describes conditional proof-bound 1.1 support.

Impact: The first-run product description contradicts the authorized software scope and does not distinguish guest practice from separately admitted research.

Required correction: Explain measurement-only guest/ordinary default and separately authenticated independently admitted research; onboarding/sign-in/notice never grant enrollment or model authority. Preserve fictional, no-validated-model and no-driving-clearance boundaries.

Verification: Actual rendered welcome/demo/introduction and account entry must describe conditional research accurately without enabling it; preserve no-prompt and guest isolation behavior.

### PROD-003 — P2: required correction

Affected: OTGD-001, OTGD-003, OTGD-009, OTGD-026, OTGD-034; AND-CHECK-007, MODEL-005, PRD-004, PRD-019, PRD-020, PRD-041. Source `apps/mobile/src/ui/checks.tsx` lines 1567–1628.

Research result card shows endpoint/population/version/probability/threshold but never displays uncertainty_policy_id or verified model_manifest.uncertainty_policy method/band/rationale; no research uncertainty renderer exists in ui. Evidence screen does not expose it either.

Impact: The person sees a numeric research classification without its supplied uncertainty policy or abstention limits, despite explicit qualified-navigation acceptance.

Required correction: Present supplied validated uncertainty policy and meaningful limits from the already verified result/authority. Show explicit no interval supplied when method=none; retain rationale where supplied; show actual band/abstention meaning when present. Never invent confidence intervals, clinical certainty or current authority.

Verification: Render admitted 1.1 method=none, probability_band with below/inside/above band and null abstention, malformed/mismatched policy refusal, and measurement/guest/legacy cases. Policy text/value must agree with verified authority.

## Evidence and limits

This review executed only read-only source, specification, dossier and hash inspection. It ran no application tests, installs, Docker/services, commits, push, deploy, participant or paid service action. Existing source/tests and focused implementer executions are bounded supporting evidence; dossier NOT_RUN acceptance cases remain NOT_RUN. Current snapshot reports successful CI jobs alongside pending jobs; the local full gate had only begun unit-coverage at the inspected boundary. No aggregate PASS is inferred. Hashes and exact snapshot job states are retained in JSON.

- Final exact-candidate local aggregate and CI job matrix are pending/incomplete in inspected snapshot; successful job status alone does not prove every acceptance case.
- Native supported OS emulators/simulators, physical Android/iPhone, TalkBack/VoiceOver, 200% text, OS permissions/settings, native encrypted storage/restart, camera/BLE and reaction timing matrix remain unexecuted here.
- Governed full UI/API collection/raw/research/export/withdrawal and staff import/recovery journeys need actual exact-case coverage beyond browser ordinary-account and controlled fixtures.
- Physical sensing, clinical/model validity, genuine study/eligibility/independent historical authority, calibrated fuel-cell breath mg/L instrument and human ECG safety verifier are not established.
- Cloud delivery, operational restore RPO/RTO drills, genuine store signing/provider/submission/public hosting remain external; current authorization excludes deployment/publication/participant use.

Every applicable unmet criterion remains blocked/unexecuted, never not-applicable. No scientific/clinical/sensor/participant or fitness-to-drive claim follows from software evidence. Pending native evidence is distinct from an unimplemented required verifier/driver and from unapproved external release actions.

## Per-spec IMPLEMENTATION decisions

### OTGD-001 — CHANGES_REQUIRED

Canonical `specs/FULL_SPECIFICATION.md`; current SHA-256 `c8f052979fd2a15da2d0bc09c8533bde246cdc559d798696af728378cf5850f7`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 92. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-001`.

The reconciled product retains one collection/one task, optional context, measurement defaults, independent research admission, separate fuel-cell breath mg/L scope and open scientific/commercial gates. Shared UI defects affect truthful scope/outcome/uncertainty. Full hardware, analytical, study, usability, commercial and operational acceptance is unproven.

Findings: PROD-001, PROD-002, PROD-003 Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-002 — CHANGES_REQUIRED

Canonical `openspec/changes/authorized-model-execution/specs/android-dashboard/spec.md`; current SHA-256 `c8e2d63aad6f7f973a181d917ef645e8d32b012ca41df1f2abd7d7a0b7525fe4`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 1. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-002`.

Home does not distinguish currently admitted research from ordinary measurement work, and its recent-record row hard-codes every frozen outcome as Measurements only (PROD-001).

Findings: PROD-001 Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-003 — CHANGES_REQUIRED

Canonical `openspec/changes/authorized-model-execution/specs/android-guided-check/spec.md`; current SHA-256 `c171a3fd1d7705d710dd172ebe5d59046cc0023a2ddfedaf162092008703e648`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 1. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-003`.

Save-before-upload and historical research result navigation exist, but the supplied research uncertainty policy is absent from result presentation (PROD-003).

Findings: PROD-003 Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-004 — CHANGES_REQUIRED

Canonical `openspec/changes/authorized-model-execution/specs/android-history/spec.md`; current SHA-256 `b29801322e8700aa11edce8289d84290485834005cba2fa80ee5695dd3d248ce`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 1. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-004`.

Local History reuses CheckRow and labels every frozen invalid/inconclusive/research record Measurements only, despite distinct correct result details (PROD-001).

Findings: PROD-001 Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-005 — CHANGES_REQUIRED

Canonical `openspec/changes/authorized-model-execution/specs/android-onboarding/spec.md`; current SHA-256 `1b82b7101ffe6bf0538ffe24b814aea01369f322c9bb8e96808e05f0dd70e369`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 1. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-005`.

Welcome explicitly says This release reports measurements only and never distinguishes the separate authenticated research path; About has the correct conditional scope (PROD-002).

Findings: PROD-002 Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-006 — BLOCKED

Canonical `openspec/changes/authorized-model-execution/specs/android-results/spec.md`; current SHA-256 `e5c8877a4b483fb47aa30fb9811536166d10764d83d15eaef950e0727dc93a8f`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 1. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-006`.

The reader validates 1.1 schema, snapshot/authority digests, provenance and endpoint while refusing simulated/legacy research. This does not establish complete live/native acceptance or externally genuine authority.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-007 — BLOCKED

Canonical `openspec/changes/authorized-model-execution/specs/android-settings-accessibility/spec.md`; current SHA-256 `8dc5faf4274edf798f4828bacff599c2c34c5aa6f5cb594481f2ca365ef401f6`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 1. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-007`.

About and Status describe proof-bound 1.1 support and current conditional inference separately from build/environment. Settings cannot independently create research permission. Native accessibility and capability scenarios remain unexecuted.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-008 — BLOCKED

Canonical `openspec/changes/authorized-model-execution/specs/research-evaluation/spec.md`; current SHA-256 `1307ac2ebe390b58619b599669a9c52773104dded84661be708aa132d95f8626`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 8. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-008`.

The tooling preserves frozen partitions, matched multimodal ablations, subgroup/invalid/abstention accounting and explicit unverified external-history references. Focused author evidence is genuine but cannot authenticate scientific custody or substitute full current gate/criterion evidence.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-009 — CHANGES_REQUIRED

Canonical `openspec/changes/authorized-model-execution/specs/research-model-execution/spec.md`; current SHA-256 `a110df0160cb1dfa6b1eb471ebe558eec1af8bcb86c7c883b8795bac2fdf714a`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 6. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-009`.

Data-only artifact admission, current independent authority, timing/baseline restrictions and null abstention exist; research result presentation omits supplied uncertainty policy and limits context (PROD-003). No independent scientific approval is inferred.

Findings: PROD-003 Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-010 — BLOCKED

Canonical `openspec/changes/authorized-raw-export/specs/raw-export-authorization/spec.md`; current SHA-256 `6e7ff5b60880e7234eec431ccb702b3e452b6a1d6e76a01720cb60b478782993`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 8. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-010`.

Raw export has a separate participant-copy authority, exact selected retained sources, bounded archive/version pins and re-admission. UI defaults exclude raw. Complete current worker/delivery/revocation and native-sharing acceptance is not established.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-011 — BLOCKED

Canonical `openspec/changes/canonical-operator-governance/specs/operator-authority/spec.md`; current SHA-256 `a7bb7170b6fc7c119e8e93eae9783767876a8f861a71588027577172c30a80e2`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 9. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-011`.

Immutable typed registry submissions and three distinct principal transitions protect current capture/model/raw authority. Fictional local aliases remain software-only. Exact PostgreSQL/current-source and independent real-authority gates are required.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-012 — BLOCKED

Canonical `openspec/changes/canonical-optical-native-acquisition/specs/optical-native/spec.md`; current SHA-256 `1e25c5f543b73c2df18741240a266b39716ae17c31bc8b57e2bd91dc699a29c4`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 6. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-012`.

Conditional native optical collection, bounded ROI evidence, physical-onset refusal and encrypted optional handoff are represented. Native frame/lifecycle/brightness/memory behavior lacks actual Android/iOS matrix and physical evidence.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-013 — BLOCKED

Canonical `openspec/changes/canonical-signed-reader-acquisition/specs/signed-reader-acquisition/spec.md`; current SHA-256 `df6d046105c408da0217d264ba7d9ec83e11682c55933c65753c12c196a7fb29`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 11. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-013`.

Signed reader binding, start nonce/expiry, protected credentials, transport-origin isolation and MITM requirements are specified and implemented in dedicated paths. Stock/protected builds and fictional evidence cannot prove provisioned secure physical BLE or sensing.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-014 — BLOCKED

Canonical `openspec/changes/cloud-deployment-customer-access/specs/cloud-browser-delivery/spec.md`; current SHA-256 `735f76493e8188925c157347dc22b0a2acad4cb76721f2ea8a7f324629631855`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 8. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-014`.

Private-origin publication, immutable reviewed bytes and secure browser identity/headers have tooling. No actual authorized cloud delivery or customer authenticated release is established; local byte probes are insufficient for those scenarios.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-015 — BLOCKED

Canonical `openspec/changes/cloud-deployment-customer-access/specs/cloud-release-orchestration/spec.md`; current SHA-256 `32e918e2908b70dbf00f7c9533aa462402b71ffc5c5ce9b8f4da499783cc3bc6`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 10. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-015`.

Environment-specific plans and exact-source/gate/maintenance/health/QA approval admission preserve operator control. Real target accounts, credentials and deployment observations remain external and unexecuted; no deployment is authorized.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-016 — BLOCKED

Canonical `openspec/changes/independent-recovery-admission/specs/recovery-authority/spec.md`; current SHA-256 `430fe7dfbfdb117add502c5632150690905d94b3dcb42ddc892bf1e8943f273c`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 2. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-016`.

Independent retained deletion/recovery authority refuses restored active rows and preserves study suspension until independent reapproval/fresh consent. Full current-source recovery exercises and actual retained-service continuity evidence remain required.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-017 — BLOCKED

Canonical `openspec/changes/optional-raw-recording-lifecycle/specs/fictional-hosted-preview/spec.md`; current SHA-256 `ee9d68e204d40b0500732c19096ce4fc4a362892d09106034678baacde4e961d`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 3. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-017`.

Hosted fictional preview isolates guest data, disables account/acquisition and describes browser memory-only persistence. Browser tests are a subset; native packaging and actual hosted availability are separately unverified.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-018 — BLOCKED

Canonical `openspec/changes/optional-raw-recording-lifecycle/specs/raw-recording-customer-flow/spec.md`; current SHA-256 `a688ab279a337ce745968e41c3d834c1afa8486a45901544cd7f779df2d54218`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 8. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-018`.

Optional recording, upload and export are distinct default-off choices; receipts, local privacy fences and cleanup states remain separate. End-to-end native encrypted handoff/retention/restart plus live current cleanup proof remain missing.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-019 — BLOCKED

Canonical `openspec/changes/production-mobile-platform/specs/android-alcohol-channel/spec.md`; current SHA-256 `6c423c75ae449e935fe8856f61d70af07aaab582719baba1d1e1bc63d787f45a`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 6. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-019`.

Separate mg/L alcohol record, qualifier, source and own timestamp are visible and co-use claims are bounded. No calibrated breath driver exists; calibration-specific participant start/recovery and real sampling remain BLOCKED, not N/A.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-020 — BLOCKED

Canonical `openspec/changes/production-mobile-platform/specs/android-app-environment/spec.md`; current SHA-256 `7cd3451fd8c13cd25bdc66403e879de3f9fe0e127e3655f2ed40017869916f76`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 7. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-020`.

Build identities, secure startup, LocalStack path and truthful recovery/source-image boundaries are represented. Current final local/CI matrix remains incomplete at review, with native/physical/cloud/RPO-RTO evidence separately unavailable.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-021 — CHANGES_REQUIRED

Canonical `openspec/changes/production-mobile-platform/specs/android-dashboard/spec.md`; current SHA-256 `c756e1eb65e8b3e9929a58c4c191e7c179529f8cd238da6e9cd6b5403439105e`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 7. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-021`.

Home and shared latest rows hard-code measurement-only labels even for admitted research and other scientific outcomes (PROD-001). Start/context/device/queue control paths exist; full native navigation/accessibility acceptance remains unexecuted.

Findings: PROD-001 Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-022 — BLOCKED

Canonical `openspec/changes/production-mobile-platform/specs/android-data-export/spec.md`; current SHA-256 `2e02ae2e4ea75c4e789b29399dee2b6e4206f12ecb81630b04ca54c4a6e1ef30`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 7. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-022`.

Exact selection and confirmation, current owned downloads, digest verification and cleanup are implemented. Live ordinary web export is planned/current gate pending, and native share-file cleanup/restart remains unexecuted.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-023 — BLOCKED

Canonical `openspec/changes/production-mobile-platform/specs/android-device-pairing/spec.md`; current SHA-256 `c772a370e6d80b6568ad3d210081934ac57ecb9e7449e7e776efeb776cdd98c4`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 8. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-023`.

Simulator versus verified physical binding, explicit discovery, origin/replay guards and stop/forget paths exist. Actual Android/iOS permission/radio/bonding/disconnect/MTU journeys and protected reader physical evidence are absent.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-024 — BLOCKED

Canonical `openspec/changes/production-mobile-platform/specs/android-ecg-capture/spec.md`; current SHA-256 `c75f24b4beeda893b780af0d924747c0cd7ca599ead627d3d265f21ec3772895`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 7. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-024`.

Optional ECG, one-modality selection and source/null restrictions exist. Human ECG correctly refuses an unimplemented operating-state verifier; declaration cannot qualify electrical safety. Native waveform/lifecycle and whole-system evidence remain blocked.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-025 — BLOCKED

Canonical `openspec/changes/production-mobile-platform/specs/android-eye-capture/spec.md`; current SHA-256 `bfb351373c6c3c2d33fd74fa1537ed0c610aa65624e5ce0e8c07fa8f5d1a6cf8`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 7. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-025`.

Passive preview is separate from admitted optical capture; scale and physical onset limits remain explicit. Actual permission/camera lifecycle, opt-in raw storage and platform parity require native/physical acceptance evidence.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-026 — CHANGES_REQUIRED

Canonical `openspec/changes/production-mobile-platform/specs/android-guided-check/spec.md`; current SHA-256 `cef15148de295ecabe3b38d6f9b2d45530b60993c1aacf1b41e1b4fc495c6562`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 8. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-026`.

Frozen context, immutable attempts/replacements, local-first save, explicit upload and interruption fences are present. Research navigation omits uncertainty (PROD-003); complete offline/restart/native parity and current live evidence remain unverified.

Findings: PROD-003 Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-027 — BLOCKED

Canonical `openspec/changes/production-mobile-platform/specs/android-heart-rate/spec.md`; current SHA-256 `e9288b9fbec177d7287962239555b7633a0cfbf80ecf3e1e350158da607f5139`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 7. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-027`.

PPG modality/quality, null invalid values and fresh online capture are bounded separately from ECG. Shipped ADC/vendor source does not prove contact/motion/clock/calibration or actual phone/reader lifecycle.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-028 — CHANGES_REQUIRED

Canonical `openspec/changes/production-mobile-platform/specs/android-history/spec.md`; current SHA-256 `eb9f89e04620ed296b248ce076e2c5447df6c5fb2c9da0eb9fa90725f2bd99a2`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 7. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-028`.

History ownership/pagination/export selection are represented, but local rows reuse CheckRow hard-coded Measurements only for every finalized outcome (PROD-001). Native back position, text/accessibility and restart evidence remain missing.

Findings: PROD-001 Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-029 — BLOCKED

Canonical `openspec/changes/production-mobile-platform/specs/android-offline-sync/spec.md`; current SHA-256 `388f00c1fab3eb1f905e140b7248ce8e737ae87349eb8a508068becbb51456b9`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 7. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-029`.

Encrypted transaction precedes save, explicit owned upload uses durable identities, and workspace/generation fences preserve source/time. Browser memory persistence and mocked storage cannot demonstrate native SQLCipher restart/disk failure behavior.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-030 — CHANGES_REQUIRED

Canonical `openspec/changes/production-mobile-platform/specs/android-onboarding/spec.md`; current SHA-256 `da9837761a2034853336456f15dc249daf23aed73a9808bbdf4b1b690eda53ee`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 6. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-030`.

Workspace/notice boundaries exist but introductory scope omits separate conditional research and says this release only reports measurements (PROD-002). Native no-prompt progression, restart and accessible first-run evidence remain unexecuted.

Findings: PROD-002 Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-031 — BLOCKED

Canonical `openspec/changes/production-mobile-platform/specs/android-privacy-controls/spec.md`; current SHA-256 `993e7c0f65b5ee4bd9b2f470e2d4111f6329f083e7650a76ab71f78abf5e9f3f`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 7. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-031`.

Local clear preserves privacy intents, deletion requires fresh authentication and second scope confirmation, and generation reset is explicit. Live deletion/recovery and native retained signed-out cache must be proven on current candidate.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-032 — BLOCKED

Canonical `openspec/changes/production-mobile-platform/specs/android-profile/spec.md`; current SHA-256 `b90bbf657f3c8e8a24eab7ab93f04c680018bbe2179131c1b8aa70c6d3d67a43`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 7. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-032`.

Optional/null/declined values, exact units, field errors, profile revisions and frozen contexts are represented. No demographics grant study/model authority. Native keyboard/locale/large-text/offline conflict acceptance remains unverified.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-033 — BLOCKED

Canonical `openspec/changes/production-mobile-platform/specs/android-reaction-task/spec.md`; current SHA-256 `1c5bfceae8b4e2b5e1bd8c9edd7f19fd73908cde1fb804af4e9530700d3ea317`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 8. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-033`.

Native deterministic task contract preserves practice/scored events, missingness, stop and uncalibrated timing. Portable/core tests and source do not prove actual device presentation/input clocks, OS interruptions or timing qualification.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-034 — CHANGES_REQUIRED

Canonical `openspec/changes/production-mobile-platform/specs/android-results/spec.md`; current SHA-256 `dadd53ea7fd8027bb76d17c26e51d4910cc3c8763bfd8a838434fbf8112397ba`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 7. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-034`.

Result detail distinguishes scientific outcome/delivery and shows historical research endpoint/population/threshold. It omits supplied research uncertainty policy (PROD-003), and full polling/native/claim boundary acceptance is not proven.

Findings: PROD-003 Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-035 — BLOCKED

Canonical `openspec/changes/production-mobile-platform/specs/android-saliva-measurement/spec.md`; current SHA-256 `6edc6d7603b66733858b1f7fe42dc93d22712dd8cadbac29121a65f2ffd23610`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 7. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-035`.

One identified specimen, qualifiers/units/basis/original reports and failed-attempt lineage are preserved. No portable assay exists; real collection/analytical accuracy and native field/recovery journeys remain unqualified.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-036 — BLOCKED

Canonical `openspec/changes/production-mobile-platform/specs/android-settings-accessibility/spec.md`; current SHA-256 `2768fdfbe5ff0b1971d6aad04101ea2fa17db6f6c3012848aa3aa3f490e654c8`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 7. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-036`.

Settings destinations, no-prompt permission refresh, redacted diagnostics and workspace guards exist with focused rendered tests. Controlled OS observations do not establish genuine Settings return, 200% text, TalkBack/VoiceOver or iOS parity.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-037 — BLOCKED

Canonical `openspec/changes/production-mobile-platform/specs/android-sign-in/spec.md`; current SHA-256 `b20292aa0a4f47fa00fa5e652eafd1dffdd75e2a710ac2b0165f5f2ae4e2a1bd`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 7. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-037`.

Current PKCE state fix and exact issuer callback CSP address reproduced web blockers. Credential/partition/refresh/sign-out control exists. Real native system browser, Keychain/Keystore and locked-cache offline recovery remain unexecuted.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-038 — BLOCKED

Canonical `openspec/changes/production-mobile-platform/specs/android-study-enrollment/spec.md`; current SHA-256 `e0c8f1f81be37cbe775f274e6c2aa81d3f3eacc64da92f01bcdd1c31adfb9ee8`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 6. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-038`.

Invitation ownership, exact consent, separate qualification/fresh starts and durable withdrawal are explicit. Actual governed consent/withdrawal browser gate is pending; no fictional study is accepted as real research authorization.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-039 — BLOCKED

Canonical `openspec/changes/qualified-participant-acquisition/specs/participant-instruction-authority/spec.md`; current SHA-256 `238b3c329cd79edb4bd57807926311a3bed0c935cf77ef77577fcf79afda02ef`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 8. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-039`.

Exact released instructions, immutable acknowledgment, monotonic rest, scope and immediate stop are represented. Participant declaration remains distinct from measured safety. Full native preparation/background/accessibility and genuine authority evidence remain missing.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-040 — BLOCKED

Canonical `openspec/changes/qualified-participant-acquisition/specs/reference-lab-collection/spec.md`; current SHA-256 `09cbf8dccec136a1ec7895fc553c62160b63fa1e2133f5b5864d7d3aed13547a`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 8. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-040`.

Reference-lab collection avoids unrelated BLE, preserves sample/receipt/time/null reasons and pending draft, and restricts import to staff. Complete actual participant-form/staff-import UI/API/restart/abandonment journey is unproven.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-041 — BLOCKED

Canonical `openspec/changes/qualified-participant-acquisition/specs/research-evaluation/spec.md`; current SHA-256 `f4bef2eee7577e8f57b7cd27b7463d3879dcb1d452c73540d8916f9d6bf41726`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 1. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-041`.

HR-only reduced report requires explicit frozen policy and absent comparisons are disclosed; full mode retains all four matched ablations. Focused fictional CLI evidence cannot authenticate historical/source/endpoint authority.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-042 — BLOCKED

Canonical `openspec/changes/qualified-participant-acquisition/specs/scoped-cardiac-authority/spec.md`; current SHA-256 `277f1727d50ffc6c0ee8717d1c77541bca64139ea78ffe032795ebf8a0c2b0a7`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 8. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-042`.

Restricted HR-only interval and independent current/baseline calibration preserve original custody endpoints and quality limits. Editable fixture consistency proves no physical timing, genuine baseline/authority or clinical validity.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-043 — BLOCKED

Canonical `openspec/changes/qualified-participant-acquisition/specs/selected-vendor-ppg/spec.md`; current SHA-256 `c6f863bc71ebf167438fbe5cffe07b892da12cc066d0487d21403ff8dd49fa0d`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 7. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-043`.

Selected SparkFun driver and fresh FIFO semantics are distinct from ADC/simulation and preserve vendor quality/unknown timing. Actual protected-target compilation and current gates plus physical sensor evidence remain required, never inferred from source.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-044 — BLOCKED

Canonical `openspec/changes/verified-release-and-browser-access/specs/cloud-browser-delivery/spec.md`; current SHA-256 `758f7dd11a72a15750d44a61d49d986b923232ac981fcb9ab304a56526e5bb6c`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 3. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-044`.

Private complete CloudFront route, bounded signed bytes and stricter CSP verification are represented. Actual public HTTPS/history/asset delivery and target authority are unexecuted and unauthorized in this run.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-045 — BLOCKED

Canonical `openspec/changes/verified-release-and-browser-access/specs/cloud-release-orchestration/spec.md`; current SHA-256 `c62bb011c5e71f177ededaf19e710e2ec40a97618a5b427d144f97bcd67d7a26`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 2. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-045`.

Atomic DNS create/no-op and bounded private authority inputs preserve deliberate operator action. No DNS/account verification or propagation execution is adopted; current full tooling tests remain pending.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-046 — BLOCKED

Canonical `openspec/changes/verified-release-and-browser-access/specs/fictional-browser-preview/spec.md`; current SHA-256 `1a331132cf6b66413d1705dc09d0c7f885b8fe1375ea72250dcd5a451162e241`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 3. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-046`.

Fixed-origin fictional browser export/reuse checks preserve guest-only memory semantics and ordinary export. Genuine Codespaces/Appetize hosted launch and account access remain unexecuted; no user-facing hosted URL is claimed.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

### OTGD-047 — BLOCKED

Canonical `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md`; current SHA-256 `b5523be8de175f257dda911b52b94732ae4e5e838b49cd9c38bea7802d0670c4`. Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; criteria 18. Full relevant implementation/evidence SHA-256 mappings: JSON entry `OTGD-047`.

Plan/build/status/submit tooling separates signed device artifacts, exact provider identities, encrypted handoff and unknown outcomes from publication. Genuine Android/iOS signing/provider/store observations are absent and no submission is authorized.

Findings: No additional source-confirmed product defect identified in targeted review. Acceptance: full exact-candidate criterion execution remains BLOCKED/NOT_RUN. Native/physical/external limits named above remain required where applicable.

## Remaining action

PM should consolidate these three product corrections into the first counted correction round, freeze the next candidate, rerun affected meaningful assertions and required current gates, and obtain fresh product reaffirmation. Remaining native/physical/release evidence requires its actual prerequisites; scope cannot be relaxed merely to gain PASS. This reviewer remains independent and available for reassessment.

Blocker state: pending corrections/evidence. No denied operation, approval request or uncertain external mutation occurred. All writes were confined to the assigned scratch product-review directory.
