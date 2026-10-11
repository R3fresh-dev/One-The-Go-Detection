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
- Actual LocalStack remained **skipped**. The native workflow for this exact application checkpoint is [38113532881](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38113532881); its final conclusions and artifacts are recorded after execution.
