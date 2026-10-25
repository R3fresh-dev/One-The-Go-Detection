# Verification plan — otgd-20261025-0555

Owner: /root/verification, verification specialist. PM dispatch explicitly requested OpenAI gpt-6.1-sol/high; effective model identity is not independently exposed inside this worker. D-001 v1 through D-004 v1 acknowledged through actual messages. PM owns source freeze, dependencies, runtime, coordination and commits. Correction round 0; recovery attempts 0.

**PLANNING ONLY / NOT_RUN.** All 47 dossiers contain populated test-plan.md and test-results.md. Planning maps 411 individually identified requirements to 782 canonical cases: 86 full-spec IDs, PRD-001–042, and 283 OpenSpec requirements, including independently scoped amendments with intentionally reused IDs. PRD-029–042 trace approved behavior rather than expanding scope. Each case preserves canonical expectations, existing related test symbols or an honest no-test-found entry, prerequisites, boundary/negative/recovery supplements and status. Related symbols are partial source mappings, not a completed assertion audit or executed coverage. Every full scenario requires actual acceptance evidence before PASS.

Audits are still changing sources. These hashes identify a mutable planning snapshot, not a frozen implementation candidate. Read final product, engineering and reconciliation reports and refresh affected bindings before execution. No final stable implementation fingerprint or current runtime acceptance evidence is adopted by this planning report. No historical CI/report is adopted. No signoff follows from planning.

## Inspection and binding

Executed: read AGENTS.md; pinned Factory skill and spec-council/evidence/communication references; run/decisions/impact/inventory; canonical requirements/scenarios, PRD and shared contracts; CI_GATES, ci_gate.py, run_all_gates.py, workflows, test symbols and selected assertion bodies. These are source inspections, not passing tests. Read-only PATH inspection at 2026-10-25T06:03:36Z reported Linux x86_64, uv/npm/node/docker/g++/java available; arduino-cli/swift/xcodebuild/adb/sdkmanager/pod absent from PATH. Presence does not establish runtime health. PM later reported setup disk exhaustion and paused repository writes; an attempted /tmp report write failed before shell startup with bwrap no-space error. No test failed or ran because of that attempt.

Before execution, PM freezes all tracked/untracked implementation, tests, contracts and nonignored documentation. run_all_gates.py fingerprints every nonignored file, so concurrent dossier edits invalidate source stability. Record HEAD, git status, relevant dirty/untracked SHA-256 manifest, UTC start/end, exact command, tool versions/environment, observed result/exit code and actual artifact hashes. Keep private local env, keys and tokens out of evidence. Use /tmp/otgd-uv-cache and /tmp/otgd-npm-cache. Preserve each attempt before retries; never relabel historical reports.

## Exact command catalog

All commands below are NOT_RUN. Repository-root working directory unless stated otherwise. Setup is PM-owned; D-003 authorizes fresh fictional local runtime and a separate disposable PostgreSQL database, with retained state preserved thereafter. The application database must never become the disposable test target. No mock substitutes for required live transport.

| ID | Command | Required outcome/evidence |
|---|---|---|
| C-UNIT | python scripts/ci_gate.py unit-coverage | reports/unit.xml, unit-coverage.json, coverage.xml; API/scientific/evaluation/store helpers and infrastructure plus mobile business modules. Independent Python/TypeScript coverage >80%; each store helper >80% with no excluded statements. No skips/xfail/zero tests. |
| C-MOBILE | npm run typecheck --prefix apps/mobile; npm run test:coverage --prefix apps/mobile; in apps/mobile: node modules/scripts/verify-native-assets.mjs | Business-module inventory includes unloaded native adapters. apps/mobile/reports/mobile-unit-coverage.json and mobile-unit-events.log; TSX has separate browser coverage. |
| C-ATDD | npm run export:web --prefix apps/mobile; python scripts/ci_gate.py atdd | Fresh ordinary plus separate export:preview; actual Chromium at Pixel7 and 1440x1000. reports/atdd.xml, hosted-preview.xml, Playwright traces/screenshots and HTML reports. |
| C-COMP | python scripts/ci_gate.py components | components.spec.ts and raw-recordings.spec.ts actual DOM. reports/components.xml and actual traces/screenshots. |
| C-PG | python scripts/ci_gate.py live-dependencies | Entire API suite plus migrations/runtime-role denial checks on separate explicitly disposable PostgreSQL16. reports/postgres.xml and privilege probe log. Privately supply test environment/database/role/tombstone settings exactly as CI_GATES requires. |
| C-DOCKER | python scripts/ci_gate.py docker-health | Five long-running services healthy; initializers exit0; recent progress on every worker channel. reports/docker-health.log via combined runner. |
| C-LOCAL | python scripts/ci_gate.py localstack-api | Real canonical S3/SQS/PostgreSQL/worker/OAuth; check, check-app, raw exact-version and participant/delegated-staff/lab probes. reports/localstack-api.log via combined runner. Preserve existing local state. |
| C-PERF | python scripts/ci_gate.py performance | Forty workflows/twenty fictional identities/all400 writes; p95<1000ms, p99<2000ms; every queued result<=15s. reports/performance.json and actual log. |
| C-ALL | python scripts/run_all_gates.py | Seven local gates on unchanged full source; reports/local-gates.json and named logs. Stops on first failure; records only completed checks. Does not include all native/firmware/contracts jobs below. |
| C-SPEC | uv run --project services/api python tools/verify_specs.py; uv run --project services/api python tools/verify_openspec.py; strict OpenSpec loop in appendix | All11 active changes/document/schema/requirement inventory; documentation checks prove no scientific approval. |
| C-SCHEMA | uv run --project services/api python tools/generate_application_contracts.py; uv run --project services/api python tools/generate_operator_contracts.py; platform.yml schema/OpenAPI snippet; git diff --exit-code -- contracts/application contracts/operator contracts/research | Every schema valid, generated drift zero, mobile research schema exact. Record drift as FAIL rather than hiding generated edits. |
| C-CDK | in infra: npm run build; node --import tsx --test --test-reporter=junit test/*.test.ts > ../reports/infra-node.xml; root: python scripts/ci_gate.py verify-junit reports/infra-node.xml; uv run --project services/api python scripts/ci_gate.py infra-unit; uv run --project services/api python -m compileall -q scripts deploy infra/local | Actual CDK and infrastructure assertions, no skipped/expected failures. reports/infra-node.xml, secure-sdk.xml and bound logs. Synthesis is not actual AWS behavior. |
| C-FARGATE | python scripts/verify-fargate-backend.py --revision <exact-frozen-commit> | Actual backend images, exact source and digests, actual verifier output. Do not label changed code with baseline hash. |
| C-ANDROID | native-build.yml android run blocks, reproduced in appendix | SDK36/build-tools36.0.0/JDK17/native dependencies; actual Kotlin reaction+eye suites, both APK builds and signer/identity/bundle inspection. Module XML/reports and native-build APK hashes. |
| C-IOS | native-build.yml ios run blocks, reproduced in appendix | macOS26/Xcode26.4.1; both Swift core suites and real verbose lifecycle/XML validation plus full simulator app compile. reports/ios-native.xml/.log and ios-optical.xml/.log, simulator ZIP hash. Linux cannot substitute. |
| C-FW | native-build.yml shared-and-firmware run blocks in appendix | g++ actual protocol/acquisition/driver/core/grant tests; pinned ArduinoCLI1.5.1/core2.0.18-arduino.5/ArduinoJson7.4.2; actual simulator and signed NanoESP32 targets. Literal SparkFun output cmp and artifact hashes. |
| C-SECURE | native-build.yml protected-reader run blocks in appendix | Verified SDK/submodules/hash-locked dependencies/official toolchain, ephemeral fictional RSA3072 boot key; actual encrypted-NVS/secure-boot/authenticated-BLE branch and manifest. No flash/eFuse/provisioning. |
| C-HOSTED-NATIVE | hosted-native-preview.yml android/ios run blocks in appendix | Fixed local guest origins/flags; actual native fixtures, inspected APK/simulator ZIP, clean committed-source prepare/review manifests and exact workflow provenance. No hosted upload/session claim. |

The appendix preserves actual workflow command blocks, with working directories and environment references. Execute with those reviewed pins. PM may relocate caches/scratch tools into authorized writable paths, recording actual resolution. All shell/process failures propagate; Swift pipelines require pipefail and comparison of XML cases with actual verbose lifecycle logs. Existing XML must be removed before execution as the workflow requires.

## Concrete software gaps

These are separate from the external-only requirements below. No direct assertion located means exact acceptance coverage was not found in inspected sources, not that no related code exists.

| Gap | Criterion/source observation | Required correction or verification |
|---|---|---|
| V-SW-001 | OTGD-008 EVAL-007 Supplied historical assertions: model_evaluation.py emits verified_by_tool:false, historical_lock_or_blinding_proven:false and independent-authentication false; test_model_evaluation.py uses fictional-unverified refs but no direct output-flag/unchanged-reference assertion located. | Assert exact references retained across freeze/train/evaluate/verify; no injected boolean or internally consistent JSON authenticates independent approval/lock/blinding. Existing runtime self-approval refusal remains separate. |
| V-SW-002 | OTGD-019 AND-ALC-004 Calibration expires: schemas/censoring/generic reader checks exist, no direct qualified-alcohol expiry start assertion located. | Fictional admitted configuration at exact expiry and adjacent instants: client/server deny expired start, do not invoke hardware/emit concentration, show recalibration. Physical fuel-cell qualification remains external. |
| V-SW-003 | OTGD-019 AND-ALC-006 A low displayed value: test_every_acquisition_gate_has_rejection change=co_use covers cohort refusal; no direct alcohol UI driving/legal-clearance exclusion assertion located. | Render low/zero/censored/invalid/simulated values with mg/L/qualifiers; assert no driving/legal clearance across result/error/notification surfaces. |
| V-SW-004 | OTGD-036 AND-SET-003 set-camera-denied: device-presentation tests cover Bluetooth blocked/radio recovery, not camera Settings/Open app settings/no reprompt. | Controlled denied/restricted/permanently-denied component states and exact action/Back behavior, no automatic prompt; separately execute real Android/iOS OS round trip. |
| V-SW-005 | Shared platform-contract §§6/10 actual worker kill matrix absent from LocalStack probes; raw_version_probe explicitly excludes restart. Unit lease/interleaving checks are related only. | Actual-process kill before claim, after claim, after object write, after DB commit, before queue delete on dedicated fictional fixtures; resume same identity, verify fences/no lost or duplicate result/current authority/cleanup/DLQ budget; never reset volumes. |
| V-SW-006 | mobile.spec.ts is guest; raw-recordings.spec.ts uses component harnesses. No complete signed-in browser/live OAuth/API/worker journey established. | Actual fictional PKCE, consent/current authority, upload/result/history/export/deletion/logout and reload/ownership/revocation/recovery against live dependencies; capture origin/viewport/network/receipts. |
| V-SW-007 | Native core fixtures/builds and controlled native-storage support do not execute real phone UI/OS resource lifecycle. | Supported Android/iOS device/simulator permission/radio/camera/native touch/SQLCipher restart/process kill/denied unlock/background/cancel/account-generation journeys. Physical timing/sensing qualification remains separate. |
| V-SW-008 | Related-symbol mappings are partial; no current suite or full assertion audit executed. | Inspect every full canonical case vs actual assertions, add meaningful missing tests, execute frozen candidate and bind per-case results. File-level green does not silently close every case. |

Six unmatched cases require planned manual/process review: OTGD-001 OPS-001 architecture/private-storage review with C-LOCAL/C-PG/C-CDK support; DOC-001 current/historical claims review; DOC-003 versioned impact/drift review; PRD-026 economics; OTGD-020 AND-ENV-007 both honest-evidence-reporting scenarios. They are not counted as uncovered executable feature assertions.

Historical specs/VERIFICATION_REPORT.md is explicitly dated October11, describes 41 old tests, says no API/mobile/BLE implementation included and Arduino uncompiled. Treat those as historical scope, never the current execution record. Current claims need fresh review and binding.

## External-only prerequisites

Twenty-four full-spec acceptance requirements deliberately have no software substitute: HW-005/006/008/010/011; ANA-002/003/004/005/009/013; MOD-001/012; ALC-002/004; VAL-001/002/003/006/008; BUS-001/002/003; DOC-002. Each case names real evidence/accountable function. These are not missing automated tests. Mixed requirements preserve both software and external portions.

Physical gates require approved whole-system ECG power/USB/isolation safety; optical exposure/positioning/scale/onset; contamination/mechanical/battery evidence; qualified sensor freshness/contact/calibration/protected provisioning/BLE; supported physical-device timing. Signatures, declarations, compilation and fake-driver outputs establish none of them.

Analytical gates require real SOP/handling/identity/basis/reference-method challenges/paired samples/precision/bias/recovery/stability/selectivity and genuine authorized staff. Scientific gates require independent endpoint, ethics/protocol/eligibility/consent/oversight, named independent principals, prespecified sample size/strata/error limits, locked genuine dataset and prospective/external evaluation. HR-only fixtures preserve restricted semantics, not model validity.

Future alcohol stays a separate calibrated fuel-cell breath-alcohol channel in mg/L with controlled sampling and independent hygiene/environment/cross-sensitivity/calibration qualification. No generic gas sensor, unapproved blood conversion or cannabis score averaging.

Cloud execution requires authorized actual AWS IAM/KMS/private-network/JWKS/TLS/DNS/public bytes, budgets/alarm delivery/incident ownership/restore/rotation/rollout and independent QA evidence. Store execution requires genuine protected provider/signing/project inputs, complete signed AAB or macOS-inspected provisioned device IPA, persistent submission fence and actual provider observation; separate platform approval/public availability. None of those external actions is authorized by this run or claimed complete.

## Shared contract and source appendices

Every dossier inherits the shared normative contracts below. Their section-level maps identify related checks, not complete execution coverage. RRAW/JRNL and companion contracts are included even outside the 47 canonical filenames. All applicable execution is NOT_RUN; genuine external requirements remain BLOCKED.


## Subsequent shared evidence and runtime handoff

Read final product-audit.md: PRD SHA-256 e2e1a44fbed61941f1b06d5fc7b3e18c45bea399b027a7cd7f1f957b65b06592; product author preserved all47 canonical source hashes and clarified legacy0.1.0 versus conditional1.1.0 precedence. PROD-004 stale ADC raw design wording and PROD-005 historical task/status reconciliation remain engineering/reconciler handoffs. PRD-001–042 are individually mapped.

A separate firmware-validation.md now records actual baseline portable/Arduino/protected-build executions by /root/firmware_validation. This planning report does not transfer those PASS outcomes into current dossier results: exact source, test and raw artifact bindings must be rechecked after engineering/reconciliation. Retain its initial resource failures and successful retries. All planned final-candidate C-FW/C-SECURE checks remain NOT_RUN here pending that admission.

PM capacity-restored notice: PostgreSQL+LocalStack healthy; full canonical application Docker stack remains capacity-blocked pending platform storage remedy. No verification-agent cleanup, migration, runtime creation or suite execution performed. Earlier report-write attempt failed before shell start; report now durably persisted after restoration.

## Canonical dossier snapshot

Planning HEAD: 33901a1ff785cd28e351d935be510d184fb7f8e2. SHA-256; source paths are repository-relative. Counts are requirements/canonical cases. No execution candidate is frozen.

| Dossier | Canonical path | SHA-256 | Requirements | Cases |
|---|---|---|---:|---:|
| OTGD-001 | `specs/FULL_SPECIFICATION.md` | `f8c4cd46f9b3e2e7fb24b5940f3a876d2f0e16d94aa29d1bedec21e1516def7a` | 128 | 128 |
| OTGD-002 | `openspec/changes/authorized-model-execution/specs/android-dashboard/spec.md` | `c8e2d63aad6f7f973a181d917ef645e8d32b012ca41df1f2abd7d7a0b7525fe4` | 1 | 2 |
| OTGD-003 | `openspec/changes/authorized-model-execution/specs/android-guided-check/spec.md` | `c171a3fd1d7705d710dd172ebe5d59046cc0023a2ddfedaf162092008703e648` | 1 | 2 |
| OTGD-004 | `openspec/changes/authorized-model-execution/specs/android-history/spec.md` | `b29801322e8700aa11edce8289d84290485834005cba2fa80ee5695dd3d248ce` | 1 | 2 |
| OTGD-005 | `openspec/changes/authorized-model-execution/specs/android-onboarding/spec.md` | `1b82b7101ffe6bf0538ffe24b814aea01369f322c9bb8e96808e05f0dd70e369` | 1 | 2 |
| OTGD-006 | `openspec/changes/authorized-model-execution/specs/android-results/spec.md` | `e5c8877a4b483fb47aa30fb9811536166d10764d83d15eaef950e0727dc93a8f` | 1 | 2 |
| OTGD-007 | `openspec/changes/authorized-model-execution/specs/android-settings-accessibility/spec.md` | `8dc5faf4274edf798f4828bacff599c2c34c5aa6f5cb594481f2ca365ef401f6` | 1 | 2 |
| OTGD-008 | `openspec/changes/authorized-model-execution/specs/research-evaluation/spec.md` | `1307ac2ebe390b58619b599669a9c52773104dded84661be708aa132d95f8626` | 8 | 19 |
| OTGD-009 | `openspec/changes/authorized-model-execution/specs/research-model-execution/spec.md` | `a110df0160cb1dfa6b1eb471ebe558eec1af8bcb86c7c883b8795bac2fdf714a` | 6 | 16 |
| OTGD-010 | `openspec/changes/authorized-raw-export/specs/raw-export-authorization/spec.md` | `6e7ff5b60880e7234eec431ccb702b3e452b6a1d6e76a01720cb60b478782993` | 8 | 19 |
| OTGD-011 | `openspec/changes/canonical-operator-governance/specs/operator-authority/spec.md` | `a7bb7170b6fc7c119e8e93eae9783767876a8f861a71588027577172c30a80e2` | 9 | 18 |
| OTGD-012 | `openspec/changes/canonical-optical-native-acquisition/specs/optical-native/spec.md` | `1e25c5f543b73c2df18741240a266b39716ae17c31bc8b57e2bd91dc699a29c4` | 6 | 13 |
| OTGD-013 | `openspec/changes/canonical-signed-reader-acquisition/specs/signed-reader-acquisition/spec.md` | `df6d046105c408da0217d264ba7d9ec83e11682c55933c65753c12c196a7fb29` | 11 | 23 |
| OTGD-014 | `openspec/changes/cloud-deployment-customer-access/specs/cloud-browser-delivery/spec.md` | `735f76493e8188925c157347dc22b0a2acad4cb76721f2ea8a7f324629631855` | 8 | 16 |
| OTGD-015 | `openspec/changes/cloud-deployment-customer-access/specs/cloud-release-orchestration/spec.md` | `32e918e2908b70dbf00f7c9533aa462402b71ffc5c5ce9b8f4da499783cc3bc6` | 10 | 21 |
| OTGD-016 | `openspec/changes/independent-recovery-admission/specs/recovery-authority/spec.md` | `430fe7dfbfdb117add502c5632150690905d94b3dcb42ddc892bf1e8943f273c` | 2 | 6 |
| OTGD-017 | `openspec/changes/optional-raw-recording-lifecycle/specs/fictional-hosted-preview/spec.md` | `ee9d68e204d40b0500732c19096ce4fc4a362892d09106034678baacde4e961d` | 3 | 6 |
| OTGD-018 | `openspec/changes/optional-raw-recording-lifecycle/specs/raw-recording-customer-flow/spec.md` | `a688ab279a337ce745968e41c3d834c1afa8486a45901544cd7f779df2d54218` | 8 | 16 |
| OTGD-019 | `openspec/changes/production-mobile-platform/specs/android-alcohol-channel/spec.md` | `6c423c75ae449e935fe8856f61d70af07aaab582719baba1d1e1bc63d787f45a` | 6 | 12 |
| OTGD-020 | `openspec/changes/production-mobile-platform/specs/android-app-environment/spec.md` | `7cd3451fd8c13cd25bdc66403e879de3f9fe0e127e3655f2ed40017869916f76` | 7 | 14 |
| OTGD-021 | `openspec/changes/production-mobile-platform/specs/android-dashboard/spec.md` | `c756e1eb65e8b3e9929a58c4c191e7c179529f8cd238da6e9cd6b5403439105e` | 7 | 17 |
| OTGD-022 | `openspec/changes/production-mobile-platform/specs/android-data-export/spec.md` | `2e02ae2e4ea75c4e789b29399dee2b6e4206f12ecb81630b04ca54c4a6e1ef30` | 7 | 14 |
| OTGD-023 | `openspec/changes/production-mobile-platform/specs/android-device-pairing/spec.md` | `c772a370e6d80b6568ad3d210081934ac57ecb9e7449e7e776efeb776cdd98c4` | 8 | 19 |
| OTGD-024 | `openspec/changes/production-mobile-platform/specs/android-ecg-capture/spec.md` | `c75f24b4beeda893b780af0d924747c0cd7ca599ead627d3d265f21ec3772895` | 7 | 16 |
| OTGD-025 | `openspec/changes/production-mobile-platform/specs/android-eye-capture/spec.md` | `bfb351373c6c3c2d33fd74fa1537ed0c610aa65624e5ce0e8c07fa8f5d1a6cf8` | 7 | 16 |
| OTGD-026 | `openspec/changes/production-mobile-platform/specs/android-guided-check/spec.md` | `cef15148de295ecabe3b38d6f9b2d45530b60993c1aacf1b41e1b4fc495c6562` | 8 | 21 |
| OTGD-027 | `openspec/changes/production-mobile-platform/specs/android-heart-rate/spec.md` | `e9288b9fbec177d7287962239555b7633a0cfbf80ecf3e1e350158da607f5139` | 7 | 16 |
| OTGD-028 | `openspec/changes/production-mobile-platform/specs/android-history/spec.md` | `eb9f89e04620ed296b248ce076e2c5447df6c5fb2c9da0eb9fa90725f2bd99a2` | 7 | 17 |
| OTGD-029 | `openspec/changes/production-mobile-platform/specs/android-offline-sync/spec.md` | `388f00c1fab3eb1f905e140b7248ce8e737ae87349eb8a508068becbb51456b9` | 7 | 14 |
| OTGD-030 | `openspec/changes/production-mobile-platform/specs/android-onboarding/spec.md` | `da9837761a2034853336456f15dc249daf23aed73a9808bbdf4b1b690eda53ee` | 6 | 14 |
| OTGD-031 | `openspec/changes/production-mobile-platform/specs/android-privacy-controls/spec.md` | `993e7c0f65b5ee4bd9b2f470e2d4111f6329f083e7650a76ab71f78abf5e9f3f` | 7 | 17 |
| OTGD-032 | `openspec/changes/production-mobile-platform/specs/android-profile/spec.md` | `b90bbf657f3c8e8a24eab7ab93f04c680018bbe2179131c1b8aa70c6d3d67a43` | 7 | 16 |
| OTGD-033 | `openspec/changes/production-mobile-platform/specs/android-reaction-task/spec.md` | `1c5bfceae8b4e2b5e1bd8c9edd7f19fd73908cde1fb804af4e9530700d3ea317` | 8 | 22 |
| OTGD-034 | `openspec/changes/production-mobile-platform/specs/android-results/spec.md` | `dadd53ea7fd8027bb76d17c26e51d4910cc3c8763bfd8a838434fbf8112397ba` | 7 | 14 |
| OTGD-035 | `openspec/changes/production-mobile-platform/specs/android-saliva-measurement/spec.md` | `6edc6d7603b66733858b1f7fe42dc93d22712dd8cadbac29121a65f2ffd23610` | 7 | 16 |
| OTGD-036 | `openspec/changes/production-mobile-platform/specs/android-settings-accessibility/spec.md` | `2768fdfbe5ff0b1971d6aad04101ea2fa17db6f6c3012848aa3aa3f490e654c8` | 7 | 17 |
| OTGD-037 | `openspec/changes/production-mobile-platform/specs/android-sign-in/spec.md` | `b20292aa0a4f47fa00fa5e652eafd1dffdd75e2a710ac2b0165f5f2ae4e2a1bd` | 7 | 17 |
| OTGD-038 | `openspec/changes/production-mobile-platform/specs/android-study-enrollment/spec.md` | `e0c8f1f81be37cbe775f274e6c2aa81d3f3eacc64da92f01bcdd1c31adfb9ee8` | 6 | 12 |
| OTGD-039 | `openspec/changes/qualified-participant-acquisition/specs/participant-instruction-authority/spec.md` | `238b3c329cd79edb4bd57807926311a3bed0c935cf77ef77577fcf79afda02ef` | 8 | 22 |
| OTGD-040 | `openspec/changes/qualified-participant-acquisition/specs/reference-lab-collection/spec.md` | `09cbf8dccec136a1ec7895fc553c62160b63fa1e2133f5b5864d7d3aed13547a` | 8 | 26 |
| OTGD-041 | `openspec/changes/qualified-participant-acquisition/specs/research-evaluation/spec.md` | `f4bef2eee7577e8f57b7cd27b7463d3879dcb1d452c73540d8916f9d6bf41726` | 1 | 5 |
| OTGD-042 | `openspec/changes/qualified-participant-acquisition/specs/scoped-cardiac-authority/spec.md` | `277f1727d50ffc6c0ee8717d1c77541bca64139ea78ffe032795ebf8a0c2b0a7` | 8 | 23 |
| OTGD-043 | `openspec/changes/qualified-participant-acquisition/specs/selected-vendor-ppg/spec.md` | `c6f863bc71ebf167438fbe5cffe07b892da12cc066d0487d21403ff8dd49fa0d` | 7 | 15 |
| OTGD-044 | `openspec/changes/verified-release-and-browser-access/specs/cloud-browser-delivery/spec.md` | `758f7dd11a72a15750d44a61d49d986b923232ac981fcb9ab304a56526e5bb6c` | 3 | 8 |
| OTGD-045 | `openspec/changes/verified-release-and-browser-access/specs/cloud-release-orchestration/spec.md` | `c62bb011c5e71f177ededaf19e710e2ec40a97618a5b427d144f97bcd67d7a26` | 2 | 6 |
| OTGD-046 | `openspec/changes/verified-release-and-browser-access/specs/fictional-browser-preview/spec.md` | `1a331132cf6b66413d1705dc09d0c7f885b8fe1375ea72250dcd5a451162e241` | 3 | 6 |
| OTGD-047 | `openspec/changes/verified-release-and-browser-access/specs/mobile-store-delivery/spec.md` | `8dd256054b4cc55a8fe8141b5589fa39cf9a655cf1af16cb28cde8ed0c4622ea` | 18 | 37 |

## Shared normative sections

| Source / sections | Related checks and remaining execution | SHA-256 |
|---|---|---|
| `openspec/changes/production-mobile-platform/shared-contracts.md` — 1. Release and workspace policy; 2. Identity, account lifecycle, and local access; 3. Data generation and anti-resurrection protocol; 4. HTTP consistency and notices; 5. Context, attempts, and immutable evidence; 6. Device proof and qualified acquisition; 7. Export, artifact versions, and privacy jobs; 8. Separate alcohol API; 9. Navigation and software verification matrix | identity_barriers, local_oauth_security, consent_versions, api, capture_signing; mobile controller/auth/domain/sync/workspace-scope/research-result; C-PG/C-LOCAL/C-ANDROID/C-IOS; all NOT_RUN in this dossier planning scope | `ed03b4787520b5b54c2f8f8415c27f9b48b290905a28c80966465b2049b5c8dd` |
| `openspec/changes/production-mobile-platform/platform-contract.md` — 1. Environment and deployment inputs; 2. LocalStack startup and phone connectivity; 3. Capacity, network paths, and deployment lifecycle; 4. Mandatory bounds and rate controls; 5. Artifact upload, verification, and immutable reads; 6. Durable outbox, SQS leases, and worker recovery; 7. Restore-independent deletion journal; 8. Logical expiry, cleanup, and exceptional retention; 9. Observability, costs, and operator ownership; 10. Acceptance evidence and review mapping | storage, worker_health, interleavings, recovery_authority/scopes, journal_continuity, raw_retention; C-PG/C-DOCKER/C-LOCAL/C-PERF/C-CDK; real kill matrix V-SW-005 and cloud network/restore remain open; all NOT_RUN in this dossier planning scope | `5458569763f9c1954cb4912dbf3aad8a80d6966ebd1efe9b56bc09b44794d050` |
| `openspec/changes/production-mobile-platform/synthetic-signal-contract.md` — Scope and immutable evidence; Fixed engineering configuration; Capture options and states; Event validation and bounds; Durable failure and privacy; Required verification; Specification adversarial review | apps/mobile/src/device/tests/signal.test.ts and protocol.test.ts; mobile export-evidence/export-projection; C-ATDD/C-COMP; no physical sensor qualification; all NOT_RUN in this dossier planning scope | `724e3806bb38a1d26d4ff0de04f6f3cc059f8eda542bf0a7dcad6759814118e4` |
| `openspec/changes/production-mobile-platform/raw-recording-retention-contract.md` — RRAW-001: separately reviewed optional purpose; RRAW-002: immutable receipt and acquisition-bound lifetime; RRAW-003: immediate authority retirement and safe write-window cleanup; RRAW-004: bounded lifecycle status and metadata erasure; JRNL-001: independently established journal binding; JRNL-002: explicit one-time administrator upgrade | RRAW-001–004: raw_capture/raw_retention/raw_export/replica_cleanup tests; JRNL-001–002: journal_continuity/recovery_authority/capture_guard_upgrade; real raw-version probe under C-LOCAL, old-backup study/cloud drills separate; all NOT_RUN in this dossier planning scope | `79bd5352377cd1e65ad4f2f1dc539b23877b3c7363b0f8a0d8b32276f34192be` |
| `openspec/changes/production-mobile-platform/report-revision-contract.md` — 1. Scope and immutability; 2. API boundary; 3. Authorization and verified source report; 4. Strict request and canonical evidence; 5. Persisted report and result versions; 6. Concurrency, replay and errors; 7. History, export and deletion integration; 8. Required implementation evidence | test_report_revisions.py, test_lab_handoff.py; mobile report-revisions/export-scope/export-projection; C-PG/C-LOCAL staff authority and immutable version custody; all NOT_RUN in this dossier planning scope | `216b3630f825df005b49368a50b2d567288927ae219af28ba2a9e3c8c98e4bb5` |
| `openspec/changes/production-mobile-platform/replacement-links-contract.md` — Customer experience and scope; HTTP contract; Integrity, pagination and bounded work; Acceptance evidence; Adversarial review disposition | test_replacement_links.py; mobile replacements/controller/export-scope; browser mobile.spec.ts; C-PG/C-ATDD/native navigation; all NOT_RUN in this dossier planning scope | `b1f675ae83bf3fe260a1f17a21b1d19ac29ece539cf7012bd81664f43a1880b9` |

## Existing test source identity

Related assertion source SHA-256 at planning; not executed evidence.

| Path | SHA-256 |
|---|---|
| `apps/mobile/e2e/components.spec.ts` | `e4dca99731e7bbfd19a17818900ad8a2e1e8f46fa3d7ab4a269fa907bac5e26f` |
| `apps/mobile/e2e/hosted-preview.spec.ts` | `8862cec87ea3ab0121502d9d5a6da7faca0d70a5dab77b4914f2448ee5659e1d` |
| `apps/mobile/e2e/mobile.spec.ts` | `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b` |
| `apps/mobile/e2e/raw-recordings.spec.ts` | `0d2a3a316e8c1b4eadadaef61e57dde071bf7a94b7a6bad8820d1e54619383af` |
| `apps/mobile/modules/eye-capture/android/src/test/java/expo/modules/otgdeye/EyeCoreTest.kt` | `8699039fb6bd8673ba07cd7ea601c219b296ca4bf44573caab299aab3b4042c6` |
| `apps/mobile/modules/eye-capture/tests/swift/EyeCoreTests.swift` | `5efcf344d7a09069f312fa3e89b08cfca833293b955fb781a31b947813b38bac` |
| `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/NativeEventSerializationTest.kt` | `55e01ae96993ce1b3071f9a8a202c4247a87b444dadaa718b783c189362e726e` |
| `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt` | `a78bd28ecae75464e21e29726bce544c6aa6a6c216c7395f6e4b34bb1d600365` |
| `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift` | `f7658f6df0d7f7bbc6a85bd74c33763357a2805faa6d6b48918032acfb8153b2` |
| `apps/mobile/src/device/tests/physical.test.ts` | `23d4938d5015dc6cca7f978a44c3d823f0e9aef3f52631a87898ae5d28c82d9d` |
| `apps/mobile/src/device/tests/protocol.test.ts` | `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c` |
| `apps/mobile/src/device/tests/signal.test.ts` | `6081eb0c7c2681f0520d69962d494c2dd14bfc60cd51bceed79209c9e862fba5` |
| `apps/mobile/tests/acquisition.test.ts` | `5a87445ae4174cdf15eccd8ec0b6b67105fea10d338aec183d1362ae6f8bfb9b` |
| `apps/mobile/tests/api-deadline.test.ts` | `b570f5df8f75273390e4493f48d02ecf99c7fa2941ea7d9580b88224e9b61c1d` |
| `apps/mobile/tests/auth.test.ts` | `f1ded241cdf9d531fb4ab27dc3657e5377ccb0f8f5e3a5ba0f8c0df66b47f047` |
| `apps/mobile/tests/cardiac-selection.test.ts` | `f4dd04b4e81fd3770810da46fd0c22ecb130c524cbb1da4a091621c6388a0bb7` |
| `apps/mobile/tests/controller.test.ts` | `e354d822120520b2336bacd98cac30b34de7921862cd4562342706358d9efa92` |
| `apps/mobile/tests/device-presentation.test.ts` | `11e79b59ead32c0a6bc4fa818784bc00347f337cfb5dff71d13534673064600a` |
| `apps/mobile/tests/domain.test.ts` | `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d` |
| `apps/mobile/tests/export-evidence.test.ts` | `786b535dfe7940928cdcc9149b7efbb4b8cb9541066a3d2e7d39a78819cc64ee` |
| `apps/mobile/tests/export-projection.test.ts` | `4707168f94a1706dd5f86d1014835651d57eba5be5d1093d2455bfd3d03732c2` |
| `apps/mobile/tests/export-scope.test.ts` | `2e0a94481f2c23702cccd7c4e6daa913b0f87e7b6a392e66afd4735d06fc7c46` |
| `apps/mobile/tests/eye-acquisition.test.ts` | `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5` |
| `apps/mobile/tests/generation-cache.test.ts` | `2a30b7da6606d73d185be5efed38968469e3fcde816063890f8e63bd7b32d756` |
| `apps/mobile/tests/hosted-preview.test.ts` | `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb` |
| `apps/mobile/tests/lifecycle.test.ts` | `a69785a96f7fbe8c6193ba617741db43650cf9ad32a2eb595d92bf04ae9a4099` |
| `apps/mobile/tests/measurement-format.test.ts` | `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2` |
| `apps/mobile/tests/native-storage.test.ts` | `52005beea373ed0bf603dffffc6a20cb2e8fd07371bf5cb0712afa4b3bf208df` |
| `apps/mobile/tests/participant-acquisition.test.ts` | `1867260acffffc4ac828866c0022ce3d1e2bb34b001e1b6558786a794939cf2f` |
| `apps/mobile/tests/profile-form.test.ts` | `0c2b5f39798e297673af92b008243169f4628c08438fc0be9defe065da2dc30e` |
| `apps/mobile/tests/raw-artifacts.test.ts` | `80522a5edec7a841cdaf1ed5257ce336ea1ababb4d2a4001d1c7a443fe7e94b3` |
| `apps/mobile/tests/raw-export.test.ts` | `c68c9146811b6261e384bef9759f0bde4a8a08f3be26391c888da40700d09359` |
| `apps/mobile/tests/raw-recordings.test.ts` | `c850243e541fffdce52a7b44db52ff300e637448bb26d6281eef4c8428c51354` |
| `apps/mobile/tests/raw-upload.test.ts` | `7771c6a9657ccd0dba4d716eb6504e80a97c36290fb6bbd00b6969db2ba769d9` |
| `apps/mobile/tests/replacements.test.ts` | `5942e7dddc7b8e7c403b71d242c7168c28f64890db69543091331e89bea60233` |
| `apps/mobile/tests/report-revisions.test.ts` | `4d1d9f5becc44e8d716ab339de02cdd5c3afde155d2afbbdec5957c33114c3fb` |
| `apps/mobile/tests/research-result.test.ts` | `5e39d0bf4fb9376df15ae349da774b343dc0428d80fae35e6ee7f2b618ba33ea` |
| `apps/mobile/tests/serverless-build.test.ts` | `77087c0fe85b1f27039d6a207636478e56b82d227c33fb4928371f4b2b318e6f` |
| `apps/mobile/tests/service-boundary.test.ts` | `70b18be9dc9bdc1edfee67e9ad73d525e84bb256db367acfa9ac779ce1686360` |
| `apps/mobile/tests/study-consent.test.ts` | `d862ef179f94af0018561a8c6dfa62972dcdd2d89c1e7060ea6a740552807481` |
| `apps/mobile/tests/support-history.test.ts` | `69eb3cea0dd3adba88f964c5b9fedd872f60b0488d53aad4fd242320aecf5f69` |
| `apps/mobile/tests/sync.test.ts` | `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202` |
| `apps/mobile/tests/workspace-scope.test.ts` | `d009b00717789b980a437f76ee379dbf1f3771aac46021d718f649b30544339d` |
| `firmware/tests/signed_reader_acquisition_test.cpp` | `fcab5453fa6058f9ec5c02c9aa30044e979896007eaf06afb7129287af926e7a` |
| `firmware/tests/signed_reader_core_test.cpp` | `f00b6d2edc4b39911caf5418acb1c70d562a44600f8e158d9bb6cfa91753a386` |
| `firmware/tests/signed_reader_grant_test.cpp` | `f398cef88638601878d2182ed671be8624c14b3dcd9e5c4e1c23041e05d93b48` |
| `firmware/tests/sparkfun_ppg_test.cpp` | `00121684618f2ea6a40bba22118a910c0cedef814d8e9f308c50f31a6cb9d78a` |
| `infra/test/test_canonical_health.py` | `5ef6623480bf0056aef21d0a97ff2e90c0be15c44003b12bebb6f4d308bc828e` |
| `infra/test/test_ci_gates.py` | `82805a98da905f9704f2016c67c726ad10c679f55f548179ed8981cf177f7904` |
| `infra/test/test_cloud_endpoints.py` | `786b0d3537e333ffa9d9114c7d946ef8aebfed4213702e7816b2f8cb47726bc4` |
| `infra/test/test_codespaces_preview.py` | `86bf9b8b88e96ca030d5c148d2d46b8fe764ae7a610351704ae419fda759fd28` |
| `infra/test/test_deployment_cli.py` | `136f38dd76a17b8d342965735bb430862c823a1fb0dadfd5dd3ecd61f121a637` |
| `infra/test/test_document_links.py` | `6dd675024788db2819ce01a80f138a3efd5aae849430587933d80624538e4635` |
| `infra/test/test_fargate_deploy.py` | `99970d95bab530bf235f2f53997c76b9ef96cf833c5051e3c1f6fab3707ab559` |
| `infra/test/test_fargate_template.py` | `7d41cd2239fccafdb4f8ee2b96a81906fbecfa6ada5fd074fca86ac15f02ba06` |
| `infra/test/test_hosted_preview.py` | `7d44b7bd8f5482bf65109d9002908eefa2ee480b8eba524ab4fe3a24b240d8ce` |
| `infra/test/test_maintenance.py` | `f7222dcd026bcbe70c73279fbb8c75a65bef166e311e93e0729f3d3570b356bf` |
| `infra/test/test_provenance.py` | `f4b05e5dc8f58d775cb7055632351b4bfdb819c9cefd74dfe48dd8bb86bff420` |
| `infra/test/test_recovery.py` | `598881481a5ab8561446d64b3d949c8f883f52ee4d1d9cc3120a909a383c737c` |
| `infra/test/test_regional_budget.py` | `99b8e2f2582f874d9ca2fddc92a44e69c3b0b287c6122629152ddd5a25084df7` |
| `infra/test/test_release.py` | `3013213897c8f1721e0f28a2c4610f18b48cb46ed6a5f5900ebb4495f3e3f9d5` |
| `infra/test/test_secure_reader_build.py` | `beb1569ec43a14c535b13f29a77222e3d927b8a5c75f38e4bdf630eb79a7cc28` |
| `infra/test/test_serverless_deploy.py` | `2df73b06df3ecd0153d07b1bae18ff6636e8dcd745eb72992158404ec092a784` |
| `infra/test/test_serverless_template.py` | `3391a66f5ee3b76b3faa08c3e4c981b81c17d10555eba227b2efc23ca3da9984` |
| `infra/test/test_store_inputs.py` | `8fb54f33f66e14f35df22dc56bfb41713f48208a63b5f35ec2e30a48deafeab0` |
| `infra/test/test_web_deployment.py` | `e0fbb440ac1b32d67b389b1261d3f6f8360e224793c8c4ad94809ea03fabb2d1` |
| `services/api/tests/test_api.py` | `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48` |
| `services/api/tests/test_capture_policy.py` | `971a808c066b099c4006aab592d052aa3867d08cdfb10fbd0eb2f5288e5febae` |
| `services/api/tests/test_capture_signing.py` | `bf0b38a0ec1eafef692a78ccb3d1bb0174d4f81b997a76c840b47ee1d2dc2751` |
| `services/api/tests/test_cardiac_authority.py` | `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a` |
| `services/api/tests/test_cardiac_authority_provenance.py` | `6247b1ba439b9d6f87a7467ec66a8fa83272aeb811ade6231196d23776294985` |
| `services/api/tests/test_cardiac_interval_governance.py` | `542124d8874ec1307305a677039b9d5b36355778cc06c9ccb8799af5cc8e14ff` |
| `services/api/tests/test_consent_versions.py` | `bdfbbe725088b6adc5e01d3033fd7bfc2ae5f1424c966c3c3ef92249ece1b963` |
| `services/api/tests/test_cross_language.py` | `f702d93abb8e32afa715db8bfce6f0677ed0276be8369c95b1ed321641c55c39` |
| `services/api/tests/test_identity_barriers.py` | `79480e9dde91c88207e1f10675e1a30f1a5e06e6d7df10cdc8c07c4d70fc15d2` |
| `services/api/tests/test_interleavings.py` | `e551a4927813b0ba6550e09bec34d0af953ac8e12cebbe2123159bbb49c0e6c1` |
| `services/api/tests/test_journal_continuity.py` | `4ca05e80289e4626c0096814050433fc39077912de8e761135d1aea59ca9b6cb` |
| `services/api/tests/test_lab_handoff.py` | `3396acf6ae29a8d994bc37f937417b446acb1c40499b6c6a6ce81fff7e0cbeb0` |
| `services/api/tests/test_local_identity.py` | `51b0675eb98628b6b6f6ab912dae1db10f8c1d30ebff60a7eec78acea58424c2` |
| `services/api/tests/test_local_oauth_security.py` | `97d79c648fe5a9b1dc3085146df8bba286647bf2d63b10c76b74c2e63af38b5a` |
| `services/api/tests/test_mobile_store_release.py` | `b371b7707c6106868225fc5a00847fc4702c755ef0eb1522eb1fa11776d526d6` |
| `services/api/tests/test_model_admission.py` | `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867` |
| `services/api/tests/test_model_engine.py` | `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce` |
| `services/api/tests/test_model_evaluation.py` | `753cb94b151befc5742260804631c5e7517813c332d9c435564b25e1537a3aa7` |
| `services/api/tests/test_model_evaluation_cardiac.py` | `23efe98238052ce2b19fbbc6aa50647a384196023d912c0f05fb436b491eca65` |
| `services/api/tests/test_model_optical_authority.py` | `597f44b706a05d5d730b7b4bd28f44e9cbe9d8d02c61cce256dd3eddf5c0150b` |
| `services/api/tests/test_operator_governance.py` | `54e64aca9b9379504922ef67bca4df1f45c518d42746530fec18b97aa58466bf` |
| `services/api/tests/test_optical_evidence.py` | `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414` |
| `services/api/tests/test_participant_acquisition.py` | `a9113ffb30c7907e12aad494ddfdf7d83afc96ef5f3d8c0668768158c2948b57` |
| `services/api/tests/test_participant_postgres.py` | `ca85c9d47be13ef424a67378116482b36d8be72225c66619edac625d1b0159c0` |
| `services/api/tests/test_raw_capture.py` | `ebedc54a2c384fb5992fb61e1959b61d767ad41afbacd8ecf7aec6729710905e` |
| `services/api/tests/test_raw_export.py` | `7ee249d50b4f2bd684639b4340159f3f8eab2f25ede232c0d67ba89bfb7ec627` |
| `services/api/tests/test_raw_retention.py` | `4f2115aa7b12c65d238c674d9568a1a64c1d9666a7b50f6543ee5e602d6923ae` |
| `services/api/tests/test_recovery_authority.py` | `8729463f12702d5da5850ce2436f24c05389a14ed556348f683525e9508bf236` |
| `services/api/tests/test_recovery_scopes.py` | `3783cfcb8a1e80662e828d51356a5f7037d9b40468a3451a8b3e8f1960f63ad1` |
| `services/api/tests/test_replacement_links.py` | `e6091da29dd66c1f496bf9857bd70c8b73bceebf61494014aa3ab9ebec74597b` |
| `services/api/tests/test_replica_cleanup.py` | `7bc5222b3b8d6e05d7d5f6c969a00d717ed1714c862d6f5db59296cdcf8c7ef4` |
| `services/api/tests/test_report_revisions.py` | `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06` |
| `services/api/tests/test_schema_cache.py` | `316bef49cdd9ade7c67fe5cecc22064b19126a553ecd0e6375150458271da90c` |
| `services/api/tests/test_security.py` | `df21a343ca0d2ebb7e0232230c425b2e097e73d1e43f4137198ccfe50b092579` |
| `services/api/tests/test_storage.py` | `66250af1472d94d2d175a3467e9f4304b80445261538ad85a3bea8210678e27f` |
| `services/api/tests/test_vendor_evidence.py` | `ffb2ca5111d52df5d295f0e594a6eb00b17465c452c0abb21a4d2fb79a8930fe` |
| `services/api/tests/test_worker_health.py` | `ece26d38e5588ebff044ca72d1ba09582066202bc49c0d72bd434d6cdd532334` |

## Gate and interface source identity

| Path | SHA-256 |
|---|---|
| `AGENTS.md` | `92a015f16480dae34990dca4a58f5d8085ce3ed651e40819f6b3260562d4bfd8` |
| `specs/PRD.md` | `e2e1a44fbed61941f1b06d5fc7b3e18c45bea399b027a7cd7f1f957b65b06592` |
| `specs/HLD.md` | `ccfd53e196706ac1c39482676b173614d4fc77837c0a57b9408a6bd7a078e4c0` |
| `specs/LLD.md` | `ce59d029fbc3d93afed644df316d4ef444458068e49fe93fea11ed0a365b89ea` |
| `docs/CI_GATES.md` | `9f2342c55144e4e4a5cb15436e840818de6373da2525a6f720da87934d610fe3` |
| `scripts/ci_gate.py` | `c897f5b4bcf149a2aad78cf18aa996400451690554229e27b885665db4b5847d` |
| `scripts/run_all_gates.py` | `535f0d25cfbe7d8a27566b44e6ae587460ac53dfa4e7887456952ff6ae3606bd` |
| `.github/workflows/platform.yml` | `c9aa4d52ef29aea2e82eed4255b9c912e5a4935b276738d26d32bbc0f682dfdc` |
| `.github/workflows/native-build.yml` | `174eff9eefce12f322cb00a0883ea653c1eaa422cf47e2e56488b685f0d26fcd` |
| `.github/workflows/hosted-native-preview.yml` | `1fe53997450a25c04ee6ee40042ba3982630aa0853091d23e0f539c720016106` |
| `.github/workflows/merge-gate.yml` | `9759a137309d85311e482b4c4672ffb01c14bca7678fd12194fe378d295ab20c` |
| `contracts/openapi.yaml` | `ed0c0b71f0921509c777e8c7acd117969625c5b746c6f88410ae20bae73847f9` |
| `contracts/application/openapi.json` | `d67cf5dd455cc80051c3092c54306614a6f485c5a1bf3c9a49bc5d22ff26671f` |
| `contracts/application/README.md` | `da4793b9b2a95c09540eaf030a2985903e102412794acfe174c4f725cf791a70` |
| `apps/mobile/package-lock.json` | `94e68b06919966cb777700e0e6ea521b7c538afa387b6f777b7885a3e3e9f676` |
| `services/api/uv.lock` | `6cb09a75e943c6102a84ea62dd1a30220c897b62f8a52cc6548a6fdb72f22f1c` |
| `infra/package-lock.json` | `543c49db269856c4321d51f870b75b5628631557c0ab349b69f6258baecd0181` |

## Exact additional workflow commands

These are copied from current workflow sources, preserving the actual command bytes. Reproduce each workflow global/job/step environment and working directory (see source hash above). Pinned tool installation is PM-owned; do not run external deploy/store actions. `<working-directory: repository root>` means no step override. A current successful process and current report checks are both required. No command in this appendix was executed by this planning assignment.

### .github/workflows/platform.yml / fargate-container-runtime / Build and execute the actual Fargate backend images

Working directory: `repository root`.

```bash
python scripts/verify-fargate-backend.py --revision "${{ github.sha }}"
```

### .github/workflows/platform.yml / contracts-and-synthesis / run

Working directory: `infra`.

```bash
npm ci --ignore-scripts
```

### .github/workflows/platform.yml / contracts-and-synthesis / run

Working directory: `infra`.

```bash
npm run build
mkdir -p ../reports
node --import tsx --test --test-reporter=junit test/*.test.ts > ../reports/infra-node.xml
```

### .github/workflows/platform.yml / contracts-and-synthesis / run

Working directory: `repository root`.

```bash
uv sync --project services/api --locked
```

### .github/workflows/platform.yml / contracts-and-synthesis / Require infrastructure assertions to execute

Working directory: `repository root`.

```bash
python scripts/ci_gate.py verify-junit reports/infra-node.xml
```

### .github/workflows/platform.yml / contracts-and-synthesis / Scientific contracts and feature inventory

Working directory: `repository root`.

```bash
uv run --project services/api python tools/verify_specs.py
uv run --project services/api python tools/verify_openspec.py
```

### .github/workflows/platform.yml / contracts-and-synthesis / Strict OpenSpec validation

Working directory: `repository root`.

```bash
for change in production-mobile-platform canonical-operator-governance cloud-deployment-customer-access optional-raw-recording-lifecycle authorized-model-execution independent-recovery-admission canonical-optical-native-acquisition canonical-signed-reader-acquisition authorized-raw-export qualified-participant-acquisition verified-release-and-browser-access; do
  npx --yes @fission-ai/openspec@1.14.1 validate "$change" --strict
done
```

### .github/workflows/platform.yml / contracts-and-synthesis / Generated API schema validation and drift

Working directory: `repository root`.

```bash
uv run --project services/api python tools/generate_application_contracts.py
uv run --project services/api python tools/generate_operator_contracts.py
uv run --project services/api python - <<'PY'
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from openapi_spec_validator import validate
root = Path('contracts/application')
validate(json.loads((root / 'openapi.json').read_text()))
for path in Path('contracts').rglob('*.schema.json'):
    Draft202012Validator.check_schema(json.loads(path.read_text()))
assert Path('contracts/research/ResearchResult.schema.json').read_bytes() == Path('apps/mobile/src/contracts/ResearchResult.schema.json').read_bytes(), 'Backend/mobile research schema drift'
PY
git diff --exit-code -- contracts/application contracts/operator contracts/research
```

### .github/workflows/platform.yml / contracts-and-synthesis / run

Working directory: `repository root`.

```bash
uv run --project services/api python scripts/ci_gate.py infra-unit
```

### .github/workflows/platform.yml / contracts-and-synthesis / run

Working directory: `repository root`.

```bash
uv run --project services/api python -m compileall -q scripts deploy infra/local
```

### .github/workflows/platform.yml / postgres-integration / run

Working directory: `repository root`.

```bash
uv sync --project services/api --locked
```

### .github/workflows/platform.yml / postgres-integration / API semantics against actual PostgreSQL

Working directory: `repository root`.

```bash
python scripts/ci_gate.py live-dependencies
```

### .github/workflows/platform.yml / localstack-integration / run

Working directory: `repository root`.

```bash
uv sync --project services/api --locked
```

### .github/workflows/platform.yml / localstack-integration / run

Working directory: `repository root`.

```bash
uv run --project services/api python scripts/local-platform.py prepare
```

### .github/workflows/platform.yml / localstack-integration / Build and start real dependencies

Working directory: `repository root`.

```bash
python scripts/local-platform.py up
```

### .github/workflows/platform.yml / localstack-integration / Repeat bootstrap without data reset

Working directory: `repository root`.

```bash
docker compose --project-name otgd-local --env-file infra/local/.env -f infra/local/compose.yml run --rm --no-deps resource-init
```

### .github/workflows/platform.yml / localstack-integration / Every long-running container healthy; initializers successful

Working directory: `repository root`.

```bash
python scripts/ci_gate.py docker-health
```

### .github/workflows/platform.yml / localstack-integration / Actual versioned conditional S3 and SQS probe

Working directory: `repository root`.

```bash
python scripts/local-platform.py check
```

### .github/workflows/platform.yml / localstack-integration / Fictional OAuth, HTTP, worker, export and deletion flow

Working directory: `repository root`.

```bash
python scripts/local-platform.py check-app --confirm-fictional-workspace
```

### .github/workflows/platform.yml / localstack-integration / Real retained version erasure and late arrival reconciliation

Working directory: `repository root`.

```bash
docker compose --project-name otgd-local --env-file infra/local/.env -f infra/local/compose.yml run --rm --no-deps api uv run --no-sync python /app/infra/local/raw_version_probe.py
```

### .github/workflows/platform.yml / localstack-integration / Real participant collection, delegated report custody and queued result

Working directory: `repository root`.

```bash
docker compose --project-name otgd-local --env-file infra/local/.env -f infra/local/compose.yml run --rm --no-deps migrate uv run --no-sync python /app/infra/local/participant_probe.py --confirm-fictional-workspace
```

### .github/workflows/platform.yml / localstack-integration / Actual signed concurrent API and SQS performance

Working directory: `repository root`.

```bash
python scripts/ci_gate.py performance
```

### .github/workflows/platform.yml / localstack-integration / Stop disposable CI project

Working directory: `repository root`.

```bash
python scripts/local-platform.py down
```

### .github/workflows/native-build.yml / shared-and-firmware / run

Working directory: `apps/mobile`.

```bash
npm ci
```

### .github/workflows/native-build.yml / shared-and-firmware / run

Working directory: `apps/mobile`.

```bash
npm run typecheck
```

### .github/workflows/native-build.yml / shared-and-firmware / run

Working directory: `apps/mobile`.

```bash
npm run test:coverage
```

### .github/workflows/native-build.yml / shared-and-firmware / run

Working directory: `apps/mobile`.

```bash
node modules/scripts/verify-native-assets.mjs
```

### .github/workflows/native-build.yml / shared-and-firmware / Compile and execute portable firmware protocol tests

Working directory: `repository root`.

```bash
g++ -std=c++17 -Wall -Wextra -Werror firmware/tests/protocol_core_test.cpp -o "$RUNNER_TEMP/otgd-protocol-test"
"$RUNNER_TEMP/otgd-protocol-test"
g++ -std=c++17 -Wall -Wextra -Werror -pthread \
  firmware/tests/signed_reader_acquisition_test.cpp \
  -o "$RUNNER_TEMP/otgd-reader-acquisition-test"
"$RUNNER_TEMP/otgd-reader-acquisition-test"
```

### .github/workflows/native-build.yml / shared-and-firmware / Install pinned Arduino CLI with release checksum

Working directory: `repository root`.

```bash
mkdir -p "$RUNNER_TEMP/otgd-arduino"
curl --fail --location --retry 2 https://github.com/arduino/arduino-cli/releases/download/v1.5.1/arduino-cli_1.5.1_Linux_64bit.tar.gz -o "$RUNNER_TEMP/otgd-arduino/cli.tar.gz"
echo "28a8e119c498a25607821c36cb2dc49e8463941b261a0d99091baa7bc692dd2b  $RUNNER_TEMP/otgd-arduino/cli.tar.gz" | sha256sum --check
tar -xzf "$RUNNER_TEMP/otgd-arduino/cli.tar.gz" -C "$RUNNER_TEMP/otgd-arduino"
echo "$RUNNER_TEMP/otgd-arduino" >> "$GITHUB_PATH"
```

### .github/workflows/native-build.yml / shared-and-firmware / Compile Nano ESP32 synthetic peripheral

Working directory: `repository root`.

```bash
python3 -m venv "$RUNNER_TEMP/otgd-arduino-python"
"$RUNNER_TEMP/otgd-arduino-python/bin/pip" install pyserial==3.5
export PATH="$RUNNER_TEMP/otgd-arduino-python/bin:$PATH"
arduino-cli core update-index
arduino-cli core install arduino:esp32@2.0.18-arduino.5
arduino-cli lib install ArduinoJson@7.4.2
g++ -std=c++17 -Wall -Wextra -Werror \
  -I firmware/tests/sparkfun_fake \
  -I"$HOME/Arduino/libraries/ArduinoJson/src" \
  firmware/tests/sparkfun_ppg_test.cpp \
  firmware/nano_esp32_signed_reader/SparkFunBioSensor.cpp \
  firmware/nano_esp32_signed_reader/RyuDouble.cpp \
  -o "$RUNNER_TEMP/otgd-sparkfun-ppg-test"
"$RUNNER_TEMP/otgd-sparkfun-ppg-test" "$RUNNER_TEMP/sparkfun-ppg-result-v1.json"
cmp "$RUNNER_TEMP/sparkfun-ppg-result-v1.json" firmware/tests/fixtures/sparkfun-ppg-result-v1.json
g++ -std=c++17 -Wall -Wextra -Werror \
  -I"$HOME/Arduino/libraries/ArduinoJson/src" \
  firmware/tests/signed_reader_core_test.cpp \
  firmware/nano_esp32_signed_reader/RyuDouble.cpp \
  -o "$RUNNER_TEMP/otgd-signed-reader-test"
"$RUNNER_TEMP/otgd-signed-reader-test"
g++ -std=c++17 -Wall -Wextra -Werror \
  -I"$HOME/Arduino/libraries/ArduinoJson/src" \
  firmware/tests/signed_reader_grant_test.cpp \
  firmware/nano_esp32_signed_reader/RyuDouble.cpp \
  -lcrypto -o "$RUNNER_TEMP/otgd-reader-grant-test"
"$RUNNER_TEMP/otgd-reader-grant-test"
arduino-cli compile --fqbn arduino:esp32:nano_nora --warnings all --output-dir firmware/build/nano_esp32 firmware/nano_esp32_ble_simulator
arduino-cli compile --fqbn arduino:esp32:nano_nora --warnings all --output-dir firmware/build/signed_reader firmware/nano_esp32_signed_reader
```

### .github/workflows/native-build.yml / protected-reader / Prepare and verify immutable protected SDK sources

Working directory: `repository root`.

```bash
python firmware/tools/secure_reader_build.py prepare --cache "$RUNNER_TEMP/otgd-secure-sdk"
```

### .github/workflows/native-build.yml / protected-reader / Install hash-locked build dependencies and official checked toolchain

Working directory: `repository root`.

```bash
set -euo pipefail
otgd_sdk="$RUNNER_TEMP/otgd-secure-sdk"
uv venv --python 3.12 --seed "$otgd_sdk/python"
"$otgd_sdk/python/bin/pip" install --require-hashes -r firmware/secure_reader/requirements.lock
export IDF_PATH="$otgd_sdk/esp-idf"
export IDF_TOOLS_PATH="$otgd_sdk/tools"
"$otgd_sdk/python/bin/python" "$IDF_PATH/tools/idf_tools.py" install xtensa-esp32s3-elf cmake ninja
```

### .github/workflows/native-build.yml / protected-reader / Compile actual encrypted NVS, secure boot and authenticated BLE branch

Working directory: `repository root`.

```bash
set -euo pipefail
otgd_sdk="$RUNNER_TEMP/otgd-secure-sdk"
export IDF_PATH="$otgd_sdk/esp-idf"
export IDF_TOOLS_PATH="$otgd_sdk/tools"
export PATH="$otgd_sdk/python/bin:$IDF_TOOLS_PATH/tools/xtensa-esp32s3-elf/esp-2021r2-patch5-8.4.0/xtensa-esp32s3-elf/bin:$IDF_TOOLS_PATH/tools/cmake/3.23.1/bin:$IDF_TOOLS_PATH/tools/ninja/1.10.2:$PATH"
otgd_ci_key="$RUNNER_TEMP/otgd-fictional-secure-boot.pem"
trap 'rm -f "$otgd_ci_key"' EXIT
umask 077
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:3072 -out "$otgd_ci_key" 2>/dev/null
"$otgd_sdk/python/bin/python" firmware/tools/secure_reader_build.py build --cache "$otgd_sdk" --output "$RUNNER_TEMP/otgd-secure-reader-build" --boot-signing-key "$otgd_ci_key"
```

### .github/workflows/native-build.yml / android / run

Working directory: `apps/mobile`.

```bash
npm ci
```

### .github/workflows/native-build.yml / android / run

Working directory: `apps/mobile`.

```bash
node modules/scripts/verify-native-assets.mjs
```

### .github/workflows/native-build.yml / android / Generate Android project from committed configuration

Working directory: `apps/mobile`.

```bash
node node_modules/expo/bin/cli prebuild --platform android --no-install
```

### .github/workflows/native-build.yml / android / Require Android SDK 36

Working directory: `repository root`.

```bash
otgd_android_sdk="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-/usr/local/lib/android/sdk}}"
otgd_sdkmanager="$otgd_android_sdk/cmdline-tools/latest/bin/sdkmanager"
test -x "$otgd_sdkmanager"
"$otgd_sdkmanager" --sdk_root="$otgd_android_sdk" 'platforms;android-36' 'build-tools;36.0.0'
test -f "$otgd_android_sdk/platforms/android-36/android.jar"
test -x "$otgd_android_sdk/build-tools/36.0.0/aapt2"
```

### .github/workflows/native-build.yml / android / Compile native modules, run Kotlin golden suites, build both local APKs

Working directory: `apps/mobile/android`.

```bash
./gradlew --no-daemon --max-workers=2 --init-script ../modules/scripts/local-preview.init.gradle -PreactNativeDevServerPort=8082 -PreactNativeArchitectures=arm64-v8a,x86_64 :otgd-reaction-task:testDebugUnitTest :otgd-eye-capture:testDebugUnitTest :app:assembleDebug :app:assembleRelease
```

### .github/workflows/native-build.yml / android / Require every native fixture test to execute

Working directory: `repository root`.

```bash
python3 scripts/ci_gate.py verify-junit apps/mobile/modules/reaction-task/android/build/test-results/testDebugUnitTest/*.xml
python3 scripts/ci_gate.py verify-junit apps/mobile/modules/eye-capture/android/build/test-results/testDebugUnitTest/*.xml
```

### .github/workflows/native-build.yml / android / Inspect standalone local APK bundle, application ID and development signer

Working directory: `apps/mobile`.

```bash
python3 modules/scripts/verify_android_preview.py
```

### .github/workflows/native-build.yml / ios / Require reviewed Xcode toolchain

Working directory: `repository root`.

```bash
xcodebuild -version
```

### .github/workflows/native-build.yml / ios / run

Working directory: `apps/mobile`.

```bash
npm ci
```

### .github/workflows/native-build.yml / ios / run

Working directory: `apps/mobile`.

```bash
node modules/scripts/verify-native-assets.mjs
```

### .github/workflows/native-build.yml / ios / Run actual Swift core golden suites on macOS

Working directory: `repository root`.

```bash
set -euo pipefail
mkdir -p reports
swift test --package-path apps/mobile/modules/reaction-task \
  --parallel --num-workers 1 --verbose --disable-swift-testing \
  --xunit-output "$PWD/reports/ios-native.xml" \
  2>&1 | tee reports/ios-native.log
python3 scripts/verify-swift-xctest.py reports/ios-native.xml reports/ios-native.log
python3 scripts/ci_gate.py verify-junit reports/ios-native.xml
swift test --package-path apps/mobile/modules/eye-capture \
  --parallel --num-workers 1 --verbose --disable-swift-testing \
  --xunit-output "$PWD/reports/ios-optical.xml" \
  2>&1 | tee reports/ios-optical.log
python3 scripts/verify-swift-xctest.py reports/ios-optical.xml reports/ios-optical.log
python3 scripts/ci_gate.py verify-junit reports/ios-optical.xml
```

### .github/workflows/native-build.yml / ios / Generate and install iOS native project dependencies

Working directory: `apps/mobile`.

```bash
node node_modules/expo/bin/cli prebuild --platform ios --no-install
pod install --project-directory=ios
```

### .github/workflows/native-build.yml / ios / Compile the complete iOS simulator application

Working directory: `apps/mobile`.

```bash
python3 modules/scripts/build_ios.py
```

### .github/workflows/hosted-native-preview.yml / android / Validate preview tooling without service calls

Working directory: `repository root`.

```bash
python3 -m unittest infra.test.test_hosted_preview -v
```

### .github/workflows/hosted-native-preview.yml / android / run

Working directory: `apps/mobile`.

```bash
npm ci
```

### .github/workflows/hosted-native-preview.yml / android / run

Working directory: `apps/mobile`.

```bash
npm run typecheck && npm run test:coverage
```

### .github/workflows/hosted-native-preview.yml / android / run

Working directory: `apps/mobile`.

```bash
node modules/scripts/verify-native-assets.mjs
```

### .github/workflows/hosted-native-preview.yml / android / run

Working directory: `apps/mobile`.

```bash
node node_modules/expo/bin/cli prebuild --platform android --no-install
```

### .github/workflows/hosted-native-preview.yml / android / Require reviewed Android SDK 36

Working directory: `repository root`.

```bash
set -euo pipefail
otgd_android_sdk="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-/usr/local/lib/android/sdk}}"
otgd_sdkmanager="$otgd_android_sdk/cmdline-tools/latest/bin/sdkmanager"
test -x "$otgd_sdkmanager"
"$otgd_sdkmanager" --sdk_root="$otgd_android_sdk" 'platforms;android-36' 'build-tools;36.0.0'
test -f "$otgd_android_sdk/platforms/android-36/android.jar"
test -x "$otgd_android_sdk/build-tools/36.0.0/aapt2"
```

### .github/workflows/hosted-native-preview.yml / android / Compile Kotlin fixtures and bundled development-signed guest APK

Working directory: `apps/mobile/android`.

```bash
./gradlew --no-daemon --max-workers=2 --init-script ../modules/scripts/local-preview.init.gradle -PreactNativeDevServerPort=8082 -PreactNativeArchitectures=arm64-v8a,x86_64 :otgd-reaction-task:testDebugUnitTest :otgd-eye-capture:testDebugUnitTest :app:assembleRelease
```

### .github/workflows/hosted-native-preview.yml / android / run

Working directory: `repository root`.

```bash
python3 scripts/ci_gate.py verify-junit apps/mobile/modules/reaction-task/android/build/test-results/testDebugUnitTest/*.xml
```

### .github/workflows/hosted-native-preview.yml / android / run

Working directory: `repository root`.

```bash
python3 scripts/ci_gate.py verify-junit apps/mobile/modules/eye-capture/android/build/test-results/testDebugUnitTest/*.xml
```

### .github/workflows/hosted-native-preview.yml / android / run

Working directory: `apps/mobile`.

```bash
python3 modules/scripts/verify_android_preview.py
```

### .github/workflows/hosted-native-preview.yml / android / Bind inspected APK to exact committed preview sources

Working directory: `repository root`.

```bash
python3 apps/mobile/modules/scripts/hosted_preview.py prepare --platform android --artifact apps/mobile/native-build/otgd-local-preview.apk --manifest apps/mobile/native-build/android-hosted-preview.json
```

### .github/workflows/hosted-native-preview.yml / android / run

Working directory: `repository root`.

```bash
python3 apps/mobile/modules/scripts/hosted_preview.py review --artifact apps/mobile/native-build/otgd-local-preview.apk --manifest apps/mobile/native-build/android-hosted-preview.json
```

### .github/workflows/hosted-native-preview.yml / ios / run

Working directory: `repository root`.

```bash
xcodebuild -version
```

### .github/workflows/hosted-native-preview.yml / ios / Validate preview tooling without service calls

Working directory: `repository root`.

```bash
python3 -m unittest infra.test.test_hosted_preview infra.test.test_swift_xctest_report -v
```

### .github/workflows/hosted-native-preview.yml / ios / run

Working directory: `apps/mobile`.

```bash
npm ci
```

### .github/workflows/hosted-native-preview.yml / ios / run

Working directory: `apps/mobile`.

```bash
npm run typecheck && npm run test:coverage
```

### .github/workflows/hosted-native-preview.yml / ios / run

Working directory: `apps/mobile`.

```bash
node modules/scripts/verify-native-assets.mjs
```

### .github/workflows/hosted-native-preview.yml / ios / Execute Swift fixtures and require every native lifecycle

Working directory: `repository root`.

```bash
set -euo pipefail
mkdir -p reports
rm -f reports/ios-hosted-native.xml reports/ios-hosted-native.log
swift test --package-path apps/mobile/modules/reaction-task --scratch-path "$RUNNER_TEMP/otgd-hosted-reaction-swift" --parallel --num-workers 1 --verbose --disable-swift-testing --xunit-output "$PWD/reports/ios-hosted-native.xml" 2>&1 | tee reports/ios-hosted-native.log
python3 scripts/verify-swift-xctest.py reports/ios-hosted-native.xml reports/ios-hosted-native.log
python3 scripts/ci_gate.py verify-junit reports/ios-hosted-native.xml
rm -f reports/ios-hosted-optical.xml reports/ios-hosted-optical.log
swift test --package-path apps/mobile/modules/eye-capture --scratch-path "$RUNNER_TEMP/otgd-hosted-optical-swift" --parallel --num-workers 1 --verbose --disable-swift-testing --xunit-output "$PWD/reports/ios-hosted-optical.xml" 2>&1 | tee reports/ios-hosted-optical.log
python3 scripts/verify-swift-xctest.py reports/ios-hosted-optical.xml reports/ios-hosted-optical.log
python3 scripts/ci_gate.py verify-junit reports/ios-hosted-optical.xml
```

### .github/workflows/hosted-native-preview.yml / ios / Generate canonical iOS project and install pods

Working directory: `apps/mobile`.

```bash
node node_modules/expo/bin/cli prebuild --platform ios --no-install
pod install --project-directory=ios
```

### .github/workflows/hosted-native-preview.yml / ios / Compile bundled unsigned ARM64 simulator guest app

Working directory: `apps/mobile`.

```bash
python3 modules/scripts/build_ios.py
```

### .github/workflows/hosted-native-preview.yml / ios / Inspect actual simulator binary and bind exact committed preview sources

Working directory: `repository root`.

```bash
python3 apps/mobile/modules/scripts/hosted_preview.py prepare --platform ios --artifact apps/mobile/native-build/otgd-ios-simulator.app.zip --manifest apps/mobile/native-build/ios-hosted-preview.json
```

### .github/workflows/hosted-native-preview.yml / ios / run

Working directory: `repository root`.

```bash
python3 apps/mobile/modules/scripts/hosted_preview.py review --artifact apps/mobile/native-build/otgd-ios-simulator.app.zip --manifest apps/mobile/native-build/ios-hosted-preview.json
```

## Checkpoint handoff

Planning artifacts are coherent but intentionally provisional. After checkpoint, verification relinquishes writes until PM schedules post-reconciliation binding refresh/execution. No current app-complete, deployment, native-device, scientific, product/engineering signoff or council approval claim. Temporary full-stack capacity blocker is PM/platform-owned; unaffected audits can proceed.

## Reactivation — independent assertion audit

Audit timestamp 2026-10-25T06:53:56.344429+00:00; checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active builders. Reconciliation changes OTGD-001 to `c8f052979fd2a15da2d0bc09c8533bde246cdc559d798696af728378cf5850f7` and OTGD-047 to `b5523be8de175f257dda911b52b94732ae4e5e838b49cd9c38bea7802d0670c4`. Earlier canonical/source appendices are the initial planning snapshot, not current evidence. All47 dossier canonical hashes refreshed;411 requirements and782 original case IDs retained. No final-source PASS or freeze claimed.

D-001–005 v1 and D-006 v3 acknowledged through actual PM messaging; D-006 v1/v2 remain superseded proof-method history. Reconstructed local image1af98b2872a49d3be4f8e6468507e9bc56468b1554252dcdf19293c21850d57b has independently accepted source-filesystem/Config equivalence, not original/ECR digest identity or cloud release provenance. Resource operations remain PM-only; no Docker/build/probe/test execution by this verifier.

### EVAL-007 history/reference/authenticity audit

Mapped cases: OTGD-008-EVAL-007-01/02; OTGD-041-EVAL-002-03/04/05; OTGD-042-HR-AUTH-008-01/02/03/04; full MOD-004/005/012/014/015 and VAL-004/005/006 are related, not automatically closed.

Independently read test_model_evaluation.py::external_history_pipeline/assert_forged_history_refused and both named test_external_history_references_remain_unverified_through_pipeline/test_self_asserted_or_extra_approval_fields_do_not_authenticate_history wrappers in full and four HR variants. Actual CLI index/freeze/train/evaluate/verify compares original dataset/analysis/split/training/report/artifact hashes, full evidence and eight-row evaluation membership. Original refs and HR custody/source/baseline/manifest remain exact. Every emitted authority/authenticity/history/clinical flag is false; strict extra fields and untyped/rehashed forged manifest refuse. Existing test_real_logistic_fitting... already asserted verified_by_tool false: the original V-SW-001 claim is narrowed accordingly.

Limits/gaps: No scientific authenticity is established. Focused author-reported execution exists, but raw pytest stdout/JUnit is not linked; no final-candidate PASS adopted. These checks cover history custody; independent endpoint, genuine approvals and locked real study remain separate.

### Alcohol dependency and acquisition-boundary audit

Mapped cases: OTGD-019-AND-ALC-001-02, AND-ALC-004-02; related AND-DEV-004, AND-CHECK-002, AND-STUDY-003/004.

Read operator-governance tests: configuration/calibration at -1ms, equality and +1ms; expiry history/body/hash/decisions immutable; calibration failure distinguished from still-current configuration. Current SOFTWARE_ADAPTERS/PHYSICAL_DRIVERS contain no alcohol entry and capability reason is HUMAN_ADAPTER_UNIMPLEMENTED. Four explicitly hypothetical HTTP grant/start cases expire before still-valid grant end, require403 APPROVED_REGISTRY_VERSION_REQUIRED, zero sign_start calls, no persisted start/alcohol and unchanged issued receipt. Mobile three new cases verify strict configuration selection before expiry, fresh absent inventory overrides stale cached availability with zero grant/nonce/hardware events, and a hypothetical returned authoritative-start refusal leaves invalid null alcohol and zero acquisition events.

Limits/gaps: Client refusal transport is controlled, not an integrated real breath instrument. No qualified driver exists. Direct participant recalibration-specific start/recovery remains BLOCKED by absent instrument; generic server refusal must not be relabeled a diagnosis. Server -1ms/equality/+1ms and hypothetical grant race have reported focused execution; mobile author report/release and final gates pending.

### Rendered alcohol state/copy assertion audit

Mapped cases: OTGD-019-AND-ALC-002/003/005/006 cases; related APP-012/013, AND-HIST-003 and AND-RES-004.

Read actual AlcoholScreen/ResultsScreen/HistoryScreen/ResultDetail fixture and assertions in raw-recordings.spec.ts. Measurement/guest/research variants retain unavailable qualified hardware, mg/L and model-specific co-use copy, replace stale unconditional classification statement. Six value/source variants (zero, low, below_loq, not_detected, invalid, simulated) traverse actual history/result/detail; assertions retain units, qualifier/source/time, dashes for null, separate alcohol meaning and no automatic BAC/impairment adjustment. Positive driving/legal-clearance/combined-score patterns absent; truthful clearance Unavailable remains visible.

Limits/gaps: Controlled component inputs are hypothetical reporting records, not acquired sensor data; research fixture is not newly qualified scientific authority. Notification/OS-wide copy is not exhaustively proved by these component surfaces. Writer active; new component tests NOT_RUN in verifier final scope, author final report pending.

### Permissions race and no-reprompt assertion audit

Mapped cases: OTGD-036-AND-SET-003-01/02 and AND-SET-007-02; related AND-EYE-002, AND-ONB-004 and AND-AUTH-005.

Read PermissionsCard implementation and actual exported Settings component harness. Status labels cover denied/canAskAgain, denied/permanent, restricted, undetermined, failed reads; zero prompts across mount/refresh/active-return; OS settings call occurs once only explicit action. Deferred reads resolved newer-first, stale controller epoch before React render, account/generation changes and unmount must not publish old state; new scoped card is Not checked until current read; listener teardown asserted. Real ordinary UI test Settings/Back preserves draft/sample with no camera prompt. Implementation uses active+sequence+captured epoch guard and scoped card identity.

Limits/gaps: Adapters are controlled OS observations. Real Android/iOS settings return, OS permission policy, TalkBack/VoiceOver, key storage and native lifecycle remain Task7 BLOCKED/NOT_RUN. Writer not released; no final gate execution or independent runtime PASS.

### Current release provenance assertion audit

Mapped cases: OTGD-047-STORE-003-01/02; OTGD-015-CLOUD-DEP-002-01/02; related AND-ENV-005/007.

Read verify_github_gates/verify_gate_file and new test_provenance actual assertion bodies. Both current defaults require CURRENT_REQUIRED_JOBS=FARGATE_REQUIRED_JOBS (14), owned HTTP-client recursion retains selected set; tests reject missing/failure/skipped/cancelled fargate-container-runtime, reject base-only gate file, and verify platform build/serverless admission do not reach signing/cloud boundary. Existing exact-run/latest-attempt/duplicate/foreign/pagination checks retained. Explicit historical13 selectors remain only documented original recovery callers; signed historical receipt projection unchanged and cannot replace live admission.

Limits/gaps: HTTP response fixtures prove software refusal only. Actual current remote14 mandatory jobs/run provenance and native artifacts remain pending; baseline38347011315 is historical only and normalized PR wrapper is not trusted-main admission. Logs substantiate focused runs but run-time source manifest absent from author report; do not adopt them as exact frozen-candidate result. Canonical infra gate recorded FAIL (Docker readonly buildx setup + then-missing probe import); secure-SDK follow-up not reached.

### Actual-process interruption probe source audit

Mapped cases: Shared platform §§6/10; related OPS-002/003/005/006, RAW-EXP-004/006/007, RECOVERY-001, AND-SYNC-003/005/006, AND-PRIV-005, AND-RES-002.

Read worker_interrupt_probe.py validate_target, child_worker, OwnedChild, kill_case, verify_output, stale_case and budget_case. Exact separate disposable local DB/namespace/queues/buckets; wrappers delegate real production claim/commit/S3/SQS/run_job; only owned spawned PID receives signals; SIGKILL exit and actual barriers verified. Five export kill stages plus result after-claim/after-commit; unchanged outbox and winning fence/attempt/output assertions; version-pinned bytes/hash. SIGSTOP lets real120s lease expire; new generation denies stale output; SIGCONT late writer must lease_lost; real expiry cleanup removes only own versions and preserves neighbor. Real malformed durable work five-claim/backoff and actual five-receive120s DLQ redrive preserve production constants.

Limits/gaps: Source inspected only; probe and integration WIP, no real process/recovery execution adopted. Unit harness targeting/barrier tests do not prove actual recovery. No study withdrawal or old-backup/cloud restore inferred from generation transaction. PM must assign isolated fixture setup and run after writer release; all resource mutations PM-only. Workflow timeout must fit real production waits; integration pending.

### Authenticated ordinary-web live test source audit

Mapped cases: Related actual paths: AND-AUTH-001/003/005/006; AND-SYNC-002/003/004/007; AND-HIST-001/005/006; AND-EXP-001/002/003/006; AND-PRIV-003/004/005; WEB-DEP-003/008; complete full canonical scenarios remain separately assessed.

Read authenticated-live.spec.ts ordinary account test and helpers. Real issuer PKCE/token responses, notice/profile/context and deliberate synthetic-account Save then Upload. route.fetch sends actual finalize and validates202 before connection-reset abort; no fake success. Actual queued measurement-only result, reload clears account memory and reauthentication retrieves server history, actual export job/ZIP manifest/hash/single-check bytes, foreign404, reauthenticated deletion/current generation barrier, explicit new empty workspace and logout refresh-family refusal. Two actual viewport projects and private bounded fixture inventory; unknown records stop all-data deletion. Network receipts redacted; live config disables OAuth/token-bearing traces/HAR/screenshots.

Limits/gaps: Writer active; planned final gate NOT_RUN. Current inspected ordinary case does not establish all governed consent/withdrawal, raw, pending-lab or research UI/API journeys; later governed work is WIP. No native encrypted persistence, public CloudFront delivery or physical sensing inferred. Need actual raw JUnit/redacted receipts/archive hashes and final gate wiring after freeze.

### Reported executions kept distinct

Evaluation report SHA-256 `4332b81097b9dd4cc25545c46f808554439cf7d61a2425caa77cffe52ee96f0c`: all5 reported test/production source hashes matched current bytes during inspection. 185 evaluation/admission,43 actual-PG governance,1338 non-PG API reports are focused author executions, not a final aggregate.20 PG cases deselected in the SQLite-only inventory remain not passed there. Initial fixture4 failures and SQLite mandatory-PG2 failures remain visible. Raw pytest stdout/JUnit path absent: no independent execution adoption. Existing verified_by_tool=false assertion was already present: initial V-SW-001 finding is narrowed to missing precise full custody/authenticity negatives, now supplied in source.

Provenance report SHA-256 `8d78d5000cbb7d1f08848a3420759a5139e3abdb83eb22f87c01944bb1d4d9f2`: source bodies inspected and focused raw logs read. Logged original4 RED failures, final21/58/232 OK and canonical infra-unit FAIL are retained; missing run-time source manifest prevents full exact-candidate carry-forward. Canonical failure was Docker readonly buildx setup plus then-missing probe import; secure SDK test not reached. PM reports separate PG-role setup mismatch using nonadmin disposable role; that setup failure is neither code-defect evidence nor a passing role gate until corrected exact role check executes.

| Existing focused raw artifact | SHA-256 |
|---|---|
| `/tmp/otgd-provenance-red.log` | `7ffe06ab80b7c1b335ab6b8f694da8cfd4d4b3cfcac73d05d2785f876f724f01` |
| `/tmp/otgd-provenance-green.log` | `7054a34246dcde04823527ac394de64345818a9e695abb814765fb4086401c08` |
| `/tmp/otgd-provenance-focused-green.log` | `a7cdbabf0012d50e55df88a37c75a2157201d5b8f27b3feb900c180af4c911db` |
| `/tmp/otgd-provenance-release-green.log` | `5533a98cf07c957db1baa04bfd2baa0a7fb62e161cdbc2ba4431b424296acdff` |
| `/tmp/otgd-provenance-infra-unit.log` | `c3a42f4bf981e51bc3df77778281a1c52aa2d5eb806f66b0628927bfcde7452f` |

### Current mutable source bindings

These are inspection hashes, not a claim these exact bytes executed. Active writers may change them; refresh once all release. Final implementation source manifest must include all code/tests/contracts/workflows/locks plus dirty/untracked files and final local-image content binding.

| Path | SHA-256 |
|---|---|
| `services/api/tests/test_model_evaluation.py` | `60013323430a0979caeffcef4b2983566a028b0f50e75938df7f053c0498fdc0` |
| `services/api/tests/test_model_evaluation_cardiac.py` | `6ba27142296226c46ec947b7fe5e2a47168faac3baed130da00c364cc85d4ea8` |
| `services/api/tests/test_operator_governance.py` | `4d512a3ad9f7c65b69ee09d94fb471799d1aff63a5bc4c34140526dcac280ae7` |
| `tools/model_evaluation.py` | `80488d36507c7adb49bbf02448eec9f8ab173008f53e82f59c2d5d782194396c` |
| `services/api/otgd/operator_governance.py` | `1e16fc9b3679b1d6abd4cc6bdad1a53d18e8e02c4b759e2c3a950b04286ce971` |
| `deploy/provenance.py` | `81d44c50e87a7fafc200012618920eb607a8bff0d9303a3193b7829a39f87d76` |
| `infra/test/test_provenance.py` | `996ead63b1f3ae3999aa31d81e3de893bbc50b62bfaac6e2a69f88a968d5f6a1` |
| `infra/test/test_serverless_workflow.py` | `cdc99650c1e8a6313045b75465b54f8f2fa2c84ec853a7458cd79f699c3d4ff2` |
| `infra/test/test_fargate_continuation_workflow.py` | `9611209bd9a30e8cae7f58a8e781d6b14ebb3a8100746b1acb6fe5c3bf242fd8` |
| `apps/mobile/tests/acquisition.test.ts` | `797e9858167b9b80bff401e0b66c3fda1f9ae56c8f007fbe5b10c4aeb0b159be` |
| `apps/mobile/src/ui/manage.tsx` | `df28e91c2335b54179bed5f1ad3e606a240f19d471fc735234a577e3a448ce7c` |
| `apps/mobile/src/ui/checks.tsx` | `aa00421169fedb903393a7b778d2cd47281bf007d6ef24b2794e92fbbbc20b95` |
| `apps/mobile/e2e/components.spec.ts` | `725effb97f2e9195340fd6370b8491065eabdf849ce5c5680974c39cc2125c53` |
| `apps/mobile/e2e/raw-recordings.spec.ts` | `2ada98a52caf63a835d979adc71bef5542795c5edbd72fc859cdb7975cbfd3b7` |
| `apps/mobile/e2e/authenticated-live.spec.ts` | `da57b32b6663828f90c0264b3d0b39c41c854048c99aafdc64e642936b095835` |
| `apps/mobile/playwright.live.config.ts` | `c4952d51029987bddd14983e73c3fe27ca76581dc33c9aab05f09fa009a1605f` |
| `infra/local/worker_interrupt_probe.py` | `17f19c89fb376416aec5379cf7181822082171863e5f202cba7b90cd972d98cc` |
| `infra/test/test_worker_interrupt_probe.py` | `9498d5bd7939252f80d1c72edc44df49d6b9a74dddd67285f7da1960b1f828a2` |
| `infra/local/browser_fixture.py` | `01e70e58cec7913d7bf3b442e39158b80514c7c645cad8095f06e3b528695da7` |
| `infra/test/test_browser_fixture.py` | `7ace68aeddce4166e447474b40945196fa0afae0eaa3c98f59ceaef6bce619c1` |
| `.github/workflows/deploy-serverless.yml` | `3f9ead2335a61833294520a12bdea378720cdd6946867e580fd15c05db658e3f` |
| `.github/workflows/deploy-fargate.yml` | `19a92c6831fd7a9f50fb8093f28401670b3040ae377d6385afc0eefe6d609f0b` |
| `scripts/ci_gate.py` | `c897f5b4bcf149a2aad78cf18aa996400451690554229e27b885665db4b5847d` |
| `.github/workflows/platform.yml` | `c9aa4d52ef29aea2e82eed4255b9c912e5a4935b276738d26d32bbc0f682dfdc` |
| `docs/CI_GATES.md` | `558d5db8e8e7d46e55c21da1c7dbb53b6cf5e715ea984876f0482dec4ebcff6e` |

### Final execution handoff and remaining software gaps

1. Every builder releases owned paths and reports; PM reconciles shared ci_gate/platform/docs wiring and all assertions. V-SW-001/002 have exact source assertions;003/004 source reviewed with author/browser execution pending;005/006 WIP probe/live coverage and gate integration;007 actual native/current remote prerequisites;008 full-case runtime binding still open. Do not collapse new test names into complete782-case coverage.
2. Freeze committed implementation/tests/contracts/workflows/specs and Factory documents before combined source fingerprint. Preserve ignored raw logs/JUnit/coverage/JSON during execution and write dossier results afterward. Ensure playwright-live-report/test-results-live and all generated build/report paths are ignored; currently an untracked live HTML output exists and could invalidate the fingerprint. Do not delete evidence to hide changes.
3. PM supplies preserved canonical image/runtime identity (disclosed reconstruction), separate disposable PG and exact scoped probe DB/queues/buckets/journal, ordinary web export and actual origins/issuer browser callbacks. Verifier performs no setup/resource mutation without handoff. Probe uses real production120s timing; 7 recovery cases+2 real-expiry stale cases+DLQ redrive may exceed old25min workflow timeout; final integration must retain a realistic bounded timeout without shortened constants.
4. Run the exact current gates locally and matching CI, including new mandatory live-browser/actual-process probe wiring, both coverage inventories>80%, actual required14 jobs and current native/firmware/hosted-native checks. Record all failures/skips as failure; a focused185/43/232 result cannot replace canonical unit/infra/live/native/performance acceptance. No docs/source edits during combined runner.
5. Current remote Task7 evidence pending: historical baseline38347011315 is not this candidate and normalized PR wrapper does not establish trusted-main admission. Obtain exact revision/latest attempt/full14 job inventory, logs/artifacts and trusted provenance. Android/iOS minimum/current simulator/emulator and physical-phone OS permission/storage/restart/accessibility/native lifecycle matrices remain explicit BLOCKED/NOT_RUN, even if builds/goldens pass.
6. Physical/scientific approvals, actual instrument and ECG safety-state observer, sensor/timing/optical/assay qualification, genuine study/model authority, cloud/store publication remain separate unchanged prerequisites. Six independent per-spec reviews and fresh approver follow the same frozen candidate; no author self-signoff.
