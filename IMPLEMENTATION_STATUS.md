# Implementation and release evidence

Updated **2026-10-11**. This report separates supplied implementation, executed verification, conditional software still absent, and external release evidence. A build or a fictional fixture does not establish that the product detects current intoxication.

## Product status

The repository contains the Android/iOS measurement application, Kotlin/Swift reaction and Bluetooth modules, FastAPI API and worker, PostgreSQL persistence, Nano ESP32 synthetic peripheral, LocalStack setup, and separate AWS QA/production infrastructure. The reviewed specification checkpoint is [`47d8ecb`](https://github.com/R3fresh-dev/One-The-Go-Detection/commit/47d8ecbfc871b5026f32d4f5f474908e9c0e1b14), committed before implementation.

The release is **measurement-only**. `inference_available=false` is enforced independently by application parsing, API admission and result/export validation. There is no trained or qualified intoxication model. A one-sample metabolite concentration, demographic profile, heart rate, pupil appearance or reaction result is not converted into metabolic clearance, intoxication probability, a legal threshold or driving clearance.

The 20 OpenSpec capabilities contain **140 requirements and 321 scenarios**. The requirement-to-source/test map is maintained under `openspec/changes/production-mobile-platform/verification`. Its source dispositions are **121 source present, 15 with explicitly missing conditional positive-code branches, and 4 operations source**, with no unresolved current-release partial-software row. These dispositions do not count every written scenario as executed or every conditional future acquisition path as implemented.

## Delivered software

| Area | Implemented behavior |
|---|---|
| Entry and accounts | First-run introduction; exact notice/digest review; isolated guest/account workspaces; hosted authorization-code PKCE; refresh/revocation and account generation handling. |
| Context and check | Optional age/height/weight and use context; SI conversion; immutable context at Start; one continuous native reaction run; all attempt lineage retained; explicit PPG/ECG selection. |
| Measurements | Versioned fictional saliva, pupil, PPG, ECG and separate alcohol examples; native uncalibrated reaction evidence; camera positioning preview; source/quality/limits/basis shown without invented missing values. |
| Records | Immutable snapshot/context/attempt/manifest hashes; local history/results; physical original/replacement navigation; separate same-specimen report revisions; explicit account Upload check; bounded retry queue; conflict and retired-generation states. |
| Privacy | Encrypted native workspace/outbox, protected per-workspace keys, device unlock, exact-scope local/cloud exports, authenticated download, deletion/withdrawal receipts and durable recovery. |
| Settings | Theme/units/motion, permission status and OS return refresh, redacted diagnostics preview/copy, truthful environment/capability state, separate study enrollment and withdrawal. |
| Device development | Bounded fragmented BLE protocol, clock exchange, sequence/replay checks, cancellation and lifecycle boundaries; Home device status; bounded fictional live PPG/ECG preview with named fault states; local software simulator and real-board-compilable synthetic firmware. |
| Backend | Typed bounded JSON, strict metadata/provenance, owner/current-generation admission, immutable evidence, P-256 binding/attestation gates, conditional/versioned artifact storage, fenced jobs, deletion journal and repeat cleanup. |
| Environments | Compose API/worker/PostgreSQL/LocalStack/local issuer; CDK TLS/private Fargate/RDS/Cognito/KMS/S3/SQS; image-digest promotion, migration/restore/incident scripts, metrics and alarms. |

## Conditional acquisition branches

The current-release specifications require an unavailable state when no qualified method/configuration exists. Those refusal paths are implemented. The following positive branches are **not represented as complete merely because their server gate or schema exists**:

- Qualified camera frame/illumination extraction and approved raw recording orchestration. Current camera preview does not extract pupil size or record evidence.
- Provisioned human-reader client binding/revocation and approved PPG/ECG acquisition adapters. Current BLE transport accepts the explicitly synthetic protocol; a connected simulator cannot become a trusted human sensor.
- An approved quantitative saliva method/reader and its collection workflow. Test concentrations and limits are fictional. Selective chemistry and laboratory comparison are separate development work.
- A calibrated breath-alcohol device adapter. There is no guessed blow duration, blood-alcohol conversion or cannabis classification derived from alcohol.

Administrative same-specimen correction/reanalysis is now supplied as a reviewed, versioned companion workflow. It preserves the original immutable evidence and adds purpose-specific verified report upload, current operator/study/consent/method authorization, read-only mobile history, separate bounded export records and deletion coverage. Fictional fixtures exercise the workflow; no real operator role, laboratory method, source PDF or participant authority is provisioned by these tests.

Some of these branches need additional software as well as real hardware/protocol qualification. They remain visible in the implementation map and task checklist. The scientific gates G-01–G-14 remain open; no device whitelist, study document, operator trust anchor or clinical model is fabricated.

## Executed checks in this workspace

| Check | Observed evidence |
|---|---|
| Specification review | Three independent review perspectives; 38 original findings corrected and re-reviewed before implementation; strict OpenSpec validation and structural verification passed at the specification checkpoint. |
| Existing semantic contracts | 41 contract checks passed during implementation; final rerun recorded with delivery evidence. |
| API | Current source passed 169 host tests with two actual-PostgreSQL-only skips, including 21 cross-language cases. Both integrated checkpoint `21ee30a` and final build checkpoint `9376dba` passed all **171 tests against actual PostgreSQL with no skips**, including the later task-evidence cases and concurrent report revisions. Two migration replays and runtime-role restrictions passed. Storage remains an explicit test double in that API suite; it is not LocalStack/S3 execution. |
| Mobile host and browser | TypeScript, production web compilation and all 146 host tests passed. All six final phone/desktop Playwright journeys passed in 14.2 seconds, including synthetic ECG failure and replacement navigation. Fresh screenshots were inspected after the result-heading and content-order corrections. These are not native device execution. |
| New settings/history helpers | Five tests passed for diagnostic allowlisting, in-memory history isolation/pending-state semantics and mixed local/synced acquisition ordering. |
| Native reaction core | Production Kotlin core compiled with Kotlin 2.2.20/JRE 17; six JUnit tests passed against schedules/hashes, 14 golden vectors and timing/lifecycle/bounds. No physical latency claim. |
| Device protocol | Fourteen TypeScript protocol tests and the C++ protocol test passed. Software transport evidence was independently verified by the API. |
| Firmware | Arduino CLI 1.5.1 compiled the actual `arduino:esp32:nano_nora` target using core 2.0.18-arduino.5 and ArduinoJson 7.4.2: 956,469 sketch bytes and 75,068 global-data bytes. GitHub CI also compiled and uploaded the firmware. No board was flashed. |
| Actual Android build | At `9376dba`, actual Gradle compilation, **7/7 native JUnit tests**, both APK builds and the standalone bundle/application-ID/development-signer inspection passed. Root downloaded and digest-verified both artifacts; the standalone APK embeds JavaScript and both arm64-v8a/x86_64 libraries. The separate debug APK uses Metro 8082. Neither APK has been installed/exercised on an emulator or phone in this session. |
| Actual iOS build | macOS/Xcode CI executed the Swift test step and compiled the complete unsigned iOS simulator Release application at both `21ee30a` and `9376dba`. Root downloaded the final artifact and verified GitHub's SHA-256. This is a simulator package; iPhone signing and native interaction remain separate. Exact artifact identities and run boundaries are in the CI ledger. |
| Infrastructure | Five TypeScript/CDK assertions and ten Python operational tests passed; synthesis and script compilation are distinct from deployed AWS behavior. |
| Adversarial implementation review | Stale ORM admission/fencing, terminal outbox starvation and artifact completion/cleanup races were fixed and covered by deterministic regressions. The nine original mobile cancellation/auth/privacy findings, three later export/report findings and six report implementation findings were corrected and independently re-reviewed at their recorded scope. The report amendment has a separate six-finding preimplementation review. Native cancellation-window and consistently rehashed export cases were added during final cross-platform integration. |

## Unexecuted release gates

| Gate | What is needed |
|---|---|
| Actual LocalStack | Docker/Compose runtime and a valid LocalStack auth token. Neither a mock nor a SQLite suite satisfies this gate. Use the supplied `check` and disposable `check-app` probes. |
| Physical phones | Android/iPhone permission denial/return, secure storage/restart, Bluetooth loss/background, orientation, accessible text and TalkBack/VoiceOver. Physical task timing remains uncalibrated. |
| QA | Actual AWS account/region, DNS and ACM certificate, Cognito callback identity, secrets, image digest and permissions; run deployment, recovery, queue-kill, isolation and load evidence. |
| Production | Independent production configuration, reviewed QA evidence, signed immutable promotion, store/signing identities and release authorization. No production deployment has occurred here. |
| Human sensing/inference | Approved assay, optics, electrical/device safety and qualified configuration; approved study/data pipeline; prospectively validated target endpoint and model. Software tests do not substitute for these. |

No uptime/latency SLO, medical-device clearance, store approval, physical erasure beyond verified storage evidence, or clinical sensitivity/specificity is claimed by this report.

## Start and review

- [Shopping list](specs/SHOPPING_LIST.md) and [hardware development](firmware/README.md).
- [Mobile guide](apps/mobile/README.md), [native verification](apps/mobile/modules/VERIFICATION.md), [API guide](services/api/README.md).
- [Local and cloud setup](infra/README.md), [environment routing](infra/ENVIRONMENT.md), [deployment](deploy/README.md), [operations](infra/runbooks/OPERATIONS.md).
- [OpenSpec feature index](openspec/changes/production-mobile-platform/README.md), [specification review ledger](openspec/changes/production-mobile-platform/reviews/RESOLUTION_LEDGER.md), [task checklist](openspec/changes/production-mobile-platform/tasks.md), [implementation race review](infra/IMPLEMENTATION_REVIEW.md), [actual CI evidence](openspec/changes/production-mobile-platform/verification/ci-evidence.md).

Both [native](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38114016108) and [platform](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38114016095) workflows passed at `9376dba`. The [CI evidence ledger](openspec/changes/production-mobile-platform/verification/ci-evidence.md#verified-development-builds--9376dba) links every artifact, checksum and retained failure. GitHub retains these native artifacts until **2026-10-25**; the PostgreSQL report expires **2026-10-18**. Download them or reproduce the pinned workflow. The standalone local Android APK, Metro/debug APK, unsigned iOS simulator app and synthetic firmware are development artifacts; production signing, deployment and clinical validation remain open.
