# Commit-bound continuous integration evidence

This file records observed job conclusions and artifacts, not merely workflow source. A later source change needs its own relevant verification. None of these jobs establishes physical timing, sensing qualification, clinical validity, a LocalStack deployment or AWS QA/production operation.

## Initial implementation checkpoint — 8aa56ce

Commit: [`8aa56ce9883aaafeba11b809c94bc406e7ee0a0a`](https://github.com/R3fresh-dev/One-The-Go-Detection/commit/8aa56ce9883aaafeba11b809c94bc406e7ee0a0a). Observed on 2026-10-11.

| Job | Observed conclusion | Evidence |
|---|---|---|
| Actual PostgreSQL integration | **Passed**: 84 tests; no PostgreSQL-only skip. Migration replay ran twice; runtime DDL, qualification/recovery writes and audit update/delete were denied as expected. | [Platform run](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38111022860), [job](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38111022860/job/114386425656), [JUnit artifact](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38111022860/artifacts/11691359963). |
| Infrastructure/source | **Passed**: locked CDK verification, Python operational tests and script compilation. | [Job](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38111022860/job/114386425797). This is synthesis/source evidence, not an AWS deployment. |
| Actual LocalStack | **Skipped** on this push; the separate workflow-dispatch gate requires its real activation token. | The skipped job is visible in the platform run. No token was fabricated and no mock was counted as LocalStack. |
| Shared mobile and actual board compile | **Passed**: TypeScript, host suite, native asset verification, C++ protocol tests and actual Nano ESP32 target compilation. | [Native run](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38111022849), [job](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38111022849/job/114386425655), [firmware artifact](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38111022849/artifacts/11691373490). No board was flashed. |
| iOS | **Passed**: actual Swift core tests, CocoaPods installation and complete iOS simulator application compilation. | [Job](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38111022849/job/114386425766), [iOS simulator app artifact](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38111022849/artifacts/11692156017). This is an unsigned simulator build, not an iPhone/TestFlight/store package. |
| Android | **Failed before Gradle**: prebuild succeeded, then `sdkmanager` was not on the runner PATH. No APK was produced by this job. | [Job](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38111022849/job/114386425801). The runner-path correction was committed separately as [`4264c89`](https://github.com/R3fresh-dev/One-The-Go-Detection/commit/4264c89d1ff349b4782de26b87a3348ac736850f). Read its subsequent run before claiming Android success. |

The native workflow's overall initial conclusion is failure because Android failed; that does not erase the separately successful iOS and firmware jobs. It is also not reported as an overall native pass.

### Artifact identities and retention

| Artifact | GitHub artifact ID | ZIP size | GitHub SHA-256 | Expiry recorded by GitHub |
|---|---:|---:|---|---|
| iOS simulator app | 11692156017 | 18,193,806 bytes | `441ec426dd6c1c81eb0fcb453f00d1340722c4a81116ccedcb3e43452cef277a` | 2026-10-25 04:25:55 UTC |
| Nano ESP32 synthetic firmware | 11691373490 | 9,182,420 bytes | `56c6e34f8a0d5f41a9ed3d84ed8e40dd3804d6c6c803468495af579ed948bb2f` | 2026-10-25 04:17:06 UTC |
| PostgreSQL JUnit results | 11691359963 | 2,079 bytes | `8cc00e70360edbe8f72726e0c5b69ae52f5f10d7b9d6d2071946412237872f09` | Seven-day workflow retention |

Download retained artifacts before expiry or reproduce them with the pinned workflow. Artifact hashes identify development build output; they do not establish medical, regulatory or store-release approval.

## Report/replacement service checkpoint — cf5df00

Commit: [`cf5df00e01e567c5326880a4b8bedfa197d71bbe`](https://github.com/R3fresh-dev/One-The-Go-Detection/commit/cf5df00e01e567c5326880a4b8bedfa197d71bbe). [Platform run 38112423086](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38112423086) was observed on 2026-10-11.

- **Actual PostgreSQL passed all 168 tests, with no skips**, in 37.17 seconds. This includes the report-revision race that refuses competing branches, the earlier idempotent creation race, replacement pagination/isolation, full original-evidence validation and export bounds. The one test-run warning concerns Starlette's deprecated HTTPX test-client integration.
- Migration replay ran twice and the separate application role was denied runtime DDL, operator/system authority writes, and audit update/delete. [PostgreSQL job](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38112423086/job/114390571126).
- The JUnit artifact is [11691832955](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38112423086/artifacts/11691832955), 3,923 ZIP bytes, SHA-256 `bf58800389423a62e1488288ed62cabeea412ede5d1ea2848f981373fb2c7dd8`, expiring 2026-10-18 04:43:21 UTC.
- **The overall platform run failed:** its CDK checks passed, then the newly added document-link gate found that this evidence file was linked by the report review but absent from that selective commit. The file is committed in the following documentation correction; the failed conclusion is retained here. Generated-schema and later operational steps were skipped in that failed job.
- Actual LocalStack remained **skipped**. PostgreSQL integration uses explicit storage doubles and does not establish real LocalStack or S3 behavior.

## Android build corrections

The SDK path fix at `4264c89` exposed missing native-module `versionName` values during Expo Gradle configuration. Commit `9b4a401` supplied module version metadata and standalone preview artifact verification. Its [Android job](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38112203366/job/114389912035) then refused a React Native included plugin build because the preview guard expected every Gradle build to contain the application project. Commit [`a246345`](https://github.com/R3fresh-dev/One-The-Go-Detection/commit/a24634574944f8da2248a7e78feb67b599be5654) scopes that guard to the top-level application build while retaining the local identity, environment, embedded-bundle and development-signing checks. These earlier failures produced no Android APK. A subsequent successful job and artifact are required before claiming one.

The [a246345 Android job](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38112450362/job/114390719377) then reached compilation and reported a nullable event-body type mismatch in `OTGDReactionTaskView.kt`. The integrated follow-up uses Expo's public generic `EventDispatcher<Map<String, Any?>>()` API and adds an actual Expo/RN converter regression that retains nulls at every evidence level. Source inspection and host checks do not count as an Android compilation pass. The same workflow's [iOS job](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38112450362/job/114390719329) and [shared/firmware job](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38112450362/job/114390719198) passed.

## Complete platform correction — 0d6970a

Commit [`0d6970aece3b54d35a08b867ea78f864de204660`](https://github.com/R3fresh-dev/One-The-Go-Detection/commit/0d6970aece3b54d35a08b867ea78f864de204660) supplied the linked evidence document. [Platform run 38112562147](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38112562147) **passed overall**: [actual PostgreSQL integration](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38112562147/job/114390983138) and [contracts/infrastructure/operations](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38112562147/job/114390983212) both passed. The latter includes strict OpenSpec and semantic validation, generated-schema drift checks, CDK assertions/synthesis and operational script verification. Actual LocalStack remained explicitly **skipped**. Later task/mobile/fixture corrections require their own relevant run.

## Integrated mobile/service checkpoint — 21ee30a

Commit [`21ee30a23ba9ac51a581361d4f3da10c72bea03f`](https://github.com/R3fresh-dev/One-The-Go-Detection/commit/21ee30a23ba9ac51a581361d4f3da10c72bea03f) preserves the separately merged Android compiler correction and supplies the final reviewed mobile, export, report, replacement, signal and task-evidence source.

- [Actual PostgreSQL job](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38113532849/job/114393800343) **passed all 171 tests, with no skips**, in 78.01 seconds. The one warning is the known Starlette HTTPX test-client deprecation. The two migration replays and denied runtime DDL/authority/audit-mutation checks also passed.
- Its [JUnit artifact](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38113532849/artifacts/11692274331) is 4,041 ZIP bytes, SHA-256 `d616a95ceaa09569c73ab62d03bda0eeb89841e560fe24d19857b3a7b81c4eee`, expiring 2026-10-18 05:04:52 UTC.
- The [platform workflow](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38113532849) failed overall because the document-link checker interpreted an angle-wrapped Apple documentation URL as a local file. The correction normalizes the URL's parentheses and removes the wrapper; it changes no application code or validation rule. All 41 local semantic/document checks then passed. The corrective platform run must be read separately.
- Actual LocalStack remained **skipped**. The native workflow for this exact application checkpoint is [38113532881](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38113532881).

### Integrated native results

| Job | Observed conclusion | Artifact |
|---|---|---|
| [Shared mobile and firmware](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38113532881/job/114393844794) | **Passed**: TypeScript, all 146 host tests (zero failed/skipped), native assets, portable C++ tests and the actual Nano ESP32 compile. | [11691994826](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38113532881/artifacts/11691994826), 9,182,420 ZIP bytes, SHA-256 `57d4f069e5299f831d3a67a11476827bc54f3cdd7d4ea862667193b0b352d82d`, expires 2026-10-25 05:04:43 UTC. |
| [iOS](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38113532881/job/114393844669) | **Passed**: actual Swift suite step, dependency generation and complete unsigned simulator app build; completed 05:09:40 UTC. Full-log retrieval failed, so no unobserved Swift test count is quoted. | [11692407420](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38113532881/artifacts/11692407420), 18,260,758 ZIP bytes, SHA-256 `54e7376725bd48c340fa74a72bd141a256eabcf772fe0315b6a53f3d7a1d97b2`, expires 2026-10-25 05:09:35 UTC. |
| [Android](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38113532881/job/114393844650) | **Failed at unit-test compilation** after the production reaction module compiled. React bridge types were absent from the test compile classpath, and two older golden assertions used `JSONArray.toList()`, which Android's JSON API lacks. No APK was produced. | No successful APK artifact for this job. |

The next narrow correction adds the React Android dependency only to the test configuration; the installed React Gradle plugin pins its version across configurations. Indexed `getString`/`getInt` reads preserve both golden assertions without the unavailable JSON method. Root independently checked those changes and the actual plugin resolution source. The changed Kotlin core tests compiled locally and passed all six JUnit tests; the Expo converter and APKs still require the next actual Android job. Application behavior and scientific contracts are unchanged.

### Successful platform correction — 3a92511

The documentation-only corrective commit [`3a92511d89434ccaf2c003234fd274b22a61e993`](https://github.com/R3fresh-dev/One-The-Go-Detection/commit/3a92511d89434ccaf2c003234fd274b22a61e993) passed [platform workflow 38113684169](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38113684169) overall. [PostgreSQL](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38113684169/job/114394234324) and [contracts/infrastructure/operations](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38113684169/job/114394234410) passed; LocalStack remained explicitly skipped. This verifies the same integrated application/service source plus the normalized document link.

## Verified development builds — 9376dba

Commit [`9376dbaac603252bb49ad2bb5ec5ba8cc5be5017`](https://github.com/R3fresh-dev/One-The-Go-Detection/commit/9376dbaac603252bb49ad2bb5ec5ba8cc5be5017) supplies the reviewed Android test-classpath and portable JSON assertion corrections. Both [native workflow 38114016108](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38114016108) and [platform workflow 38114016095](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38114016095) were observed **completed/success** at this exact commit.

| Check | Actual result |
|---|---|
| [Android](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38114016108/job/114395188365) | **Passed** native compilation, actual Gradle/JUnit execution, Debug and standalone local Release APK builds, and independent bundle/application-ID/development-signer inspection. The downloaded report contains **7 tests, 0 failures, 0 skipped**: 6 `ReactionCoreTest` cases and `NativeEventSerializationTest.explicitNullsSurviveEventConversionAtEveryDepth`. |
| [iOS](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38114016108/job/114395188325) | **Passed** the actual Swift test step, native dependency generation, full simulator Release build and artifact upload; completed 05:18:20 UTC. Full-log retrieval failed, so no exact unobserved Swift case count is asserted. |
| [Shared mobile/firmware](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38114016108/job/114395188235) | **Passed** TypeScript, **146/146 host tests** with zero failed/skipped in 9.15 seconds, native assets, portable C++ tests and actual Nano ESP32 compilation. Compiler output: 956,469 program bytes and 75,068 global-data bytes. |
| [Actual PostgreSQL](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38114016095/job/114395188350) | **171 passed, no skips**, one known test-client deprecation warning, 79.60 seconds. Two migration replays passed. Runtime DDL, authority writes and audit update/delete were denied as expected. |
| [Contracts/platform source](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38114016095/job/114395188166) | **Passed** strict OpenSpec, all 41 semantic/document checks, the 20-feature/140-requirement/321-scenario inventory, generated OpenAPI/JSON Schema validation and drift checks, 5 CDK assertions/synthesis, 10 operational tests and script compilation. |
| Actual LocalStack | **Skipped**, as shown in the platform run. Successful PostgreSQL and synthesis jobs do not establish S3/SQS emulation or deployed AWS operation. |
| Browser journey checkpoint | The final application UI is unchanged from `21ee30a`: **6/6 phone/desktop journeys** passed in 14.2 seconds against `AppEntry-f317b822b70c22c98e10fd54c00de3ab.js`. The later Android changes affect only test dependencies/assertions. Browser evidence remains distinct from native interaction. |

### Retained artifacts for 9376dba

All hashes below identify the **GitHub artifact ZIP**, rather than an extracted APK.

| Artifact and download | ZIP bytes | SHA-256 | GitHub expiry (UTC) |
|---|---:|---|---|
| [Android standalone local preview — 11693316195](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38114016108/artifacts/11693316195) | 35,886,992 | `50e390b5efbb61d28ed21c6a7193ea908a62129b4aff188653f8e073133264f7` | 2026-10-25 05:23:03 |
| [Android Metro/debug — 11693031559](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38114016108/artifacts/11693031559) | 55,533,681 | `f6cd046e4d7720c9b7a139f974b54a02d209358243b22ee6a1c8c8e842dd6653` | 2026-10-25 05:23:06 |
| [Android native test report — 11693336175](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38114016108/artifacts/11693336175) | 6,984 | `72094d673ad1086f2effb0708a727909eab176e1a80a59fa5346d8dd2f1d728e` | 2026-10-25 05:23:10 |
| [iOS simulator app — 11693001318](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38114016108/artifacts/11693001318) | 18,260,845 | `4d39d844a786c52294ae552032b687e832720f5f8d0d2da3aea90aa2732cf145` | 2026-10-25 05:18:10 |
| [Nano ESP32 synthetic firmware — 11693465040](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38114016108/artifacts/11693465040) | 9,182,420 | `facde6cd7bdb135f1dc3419524e8f787331b225d972c3245718361a8f6bf47bd` | 2026-10-25 05:13:15 |
| [PostgreSQL JUnit — 11693010889](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38114016095/artifacts/11693010889) | 4,011 | `282db39dc4db9634c9a09860843c2bf233bdf24718baa7843a9b8eed6e372510` | 2026-10-18 05:13:47 |

Root downloaded both APK ZIPs, the iOS ZIP and firmware ZIP and verified their exact digests. The native reviewer downloaded, digest-verified and inspected the Android test report. The extracted standalone APK is **73,175,800 bytes**, SHA-256 `38b639136a07621898851970f767644302190673d2d1b66dc3a48aa9198b1663`; it contains `assets/index.android.bundle` and arm64-v8a/x86_64 libraries. The extracted debug APK is **123,543,303 bytes**, SHA-256 `ffc45156b847e0f030f8dcc82a33eeebeb83e347377ec2d7f7509991d4cd6ae2`; it has both architectures and obtains JavaScript from Metro 8082. The standalone APK uses the generated development signing key and local application identity, not a production signing identity.

These are real development build artifacts. Android/iOS simulator or physical interaction, permission and secure-storage behavior, radio/electrical/optical/assay qualification, LocalStack, AWS QA/production operation, store signing/submission and clinical inference remain separate unexecuted gates. No simulator or artifact closes a missing conditional acquisition implementation.
