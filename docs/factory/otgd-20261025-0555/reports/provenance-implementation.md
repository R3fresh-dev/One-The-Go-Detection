# Release provenance implementation — author handoff

Author: `/root/provenance_builder`, OpenAI builder, 2026-10-25 UTC. Run `otgd-20261025-0555`; branch `factory/one-the-go-detection-20261025`; observed coordination HEAD `8171dbffb7a38da9f7d17da08b71eccc73674057`, implementation baseline `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This report describes a mutable shared candidate, not independent signoff, exact frozen-candidate gate completion, or release authorization. Correction round 0/2 and recovery attempts 0/3 unchanged.

Read AGENTS, pinned Factory `4770878e18e9c587c2961b9e2bb13315da31abe9` skill/evidence/communication, decisions, Task 8, and spec reconciliation. Acknowledged D-001v1 AFFECTED, D-002v1 NOT_AFFECTED, D-003v1 AFFECTED, D-004v1 AFFECTED, D-005v1 AFFECTED, D-006v3 AFFECTED via actual PM messaging. Applied systematic-debugging, test-driven-development (including writing-good-tests), executing-plans, and verification-before-completion guidance. PM owns shared run state, git, source freeze and independent review. No subagents spawned.

## Proven defect and bounded correction

The committed aggregate/reusable workflows configure **14 mandatory jobs**: application `unit-coverage`, `atdd`, `components`; platform `contracts-and-synthesis`, `postgres-integration`, `localstack-integration`, `fargate-container-runtime`; native `shared-and-firmware`, `protected-reader`, `android`, `ios`; preview `android`, `ios`; and `merge-gate`. Nested runtime names use the `platform /`, `native /`, and `preview /` prefixes. `merge-gate` rejects failed/skipped/cancelled parent results. This configured inventory is not passing execution evidence.

`deploy/provenance.py` previously defaulted both live APIs to the older 13-job `REQUIRED_JOBS`. Although failed jobs present in the GitHub response were already rejected, a response containing only the thirteen successful base jobs could pass default live verification without `platform / fargate-container-runtime`. Fargate direct admission explicitly selected fourteen; other targets did not. HTTP transport fixtures reproduced the actual default verifier and real platform/serverless caller behavior without cloud mutations.

The correction introduces `CURRENT_REQUIRED_JOBS = FARGATE_REQUIRED_JOBS` (fourteen) and selects it as the default for both `verify_github_gates` and `verify_gate_file`, including the latter's owned HTTP-client recursion. Existing run/workflow/repository/revision/trusted-main/latest-attempt/pagination/uniqueness/success and rerun-window checks remain intact. No current live caller explicitly selects thirteen.

The historical `REQUIRED_JOBS` constant, signed receipt projection and `validate_gate_binding` remain thirteen by design. Existing immutable receipts and hashes are not rewritten. Static receipt validation is **not current admission**: build, promotion, activation and deployment must also call the live verifier, which now requires fourteen by default. Explicit `required_jobs=REQUIRED_JOBS` remains available only where the caller deliberately authenticates documented original recovery history. The compatibility regression confirms that historical and current live verification retain the same historical receipt projection/hash, while the default refuses a base-only current run.

### Every release caller inspected

| Caller | Current requirement after correction |
|---|---|
| `deploy/platform.py`: build; post-build recheck; promotion; post-promotion recheck; `require_release` used by activation/approval/operations | Default live fourteen; static `verify_release` retains historical signed shape |
| `deploy/orchestrate.py::deploy` | Default live fourteen |
| `deploy/serverless.py::deploy`, journalled gate readmission | Default live fourteen, including retry/readmission |
| `deploy/fargate.py`: deploy, preflight/admission paths, journalled gate readmission | Explicit `FARGATE_REQUIRED_JOBS` fourteen, unchanged |
| `deploy-serverless.yml`: `admit_sources` | Default live fourteen |
| `deploy-fargate.yml`: current `admit_sources`, `verify_previous_gate` for earlier Fargate sources | Explicit or default live fourteen; earlier Fargate sources also have independent exact-fourteen/latest-attempt checks |
| `deploy-serverless.yml::admit_resume` | Explicit historical thirteen for original Ohio recovery only |
| `deploy-fargate.yml::admit_continuation` and `recheck_legacy_continuation` | Explicit historical thirteen for original failed Ohio source only |
| `deploy/serverless_recovery.py::_continuation_bundle` | Historical recorded thirteen-job shape retained; never replaces current source gate admission |

The last three workflow historical calls previously used the shared default. PM explicitly extended ownership to these identified callsites and their focused workflow tests. They now deliberately select the old inventory so tightening live defaults does not silently break documented historical recovery. Authority is the existing historical Ohio recovery/continuation contract (`deploy/SERVERLESS_AWS.md`, `deploy/FARGATE_AWS.md`), not permission to execute recovery or deploy. No other workflow/gate/specification or builder file was edited.

## Test evidence

Linux shared workspace, service Python 3.12 environment; `UV_CACHE_DIR=/tmp/otgd-uv-cache`. Checks below ran around 06:41–06:44 UTC on the mutable candidate. HTTP GitHub responses are controlled software fixtures, not live CI passing evidence.

1. **RED before production change:** `UV_CACHE_DIR=/tmp/otgd-uv-cache uv run --project services/api python -m unittest infra.test.test_provenance -v` — exit 1, 21 tests, **4 expected failures**, no errors after correcting the cloud-boundary sentinel. Missing fourteenth job passed the default live API and owned-client gate file; the real platform build reached signing; the real serverless admission reached the cloud-operation boundary. Failed/skipped/cancelled runtime jobs were already refused. Log `/tmp/otgd-provenance-red.log`.
2. **GREEN after live defaults:** same command — exit 0, **21 tests**, no skips. Log `/tmp/otgd-provenance-green.log`.
3. **Historical compatibility RED before workflow changes:** `UV_CACHE_DIR=/tmp/otgd-uv-cache uv run --project services/api python -m unittest infra.test.test_serverless_workflow infra.test.test_fargate_continuation_workflow -q` — exit 1, **37 tests, 3 failures** proving all three historical callsites failed to select the explicit legacy inventory. Log `/tmp/otgd-provenance-historical-red.log`.
4. **Focused GREEN:** provenance plus both workflow suites — exit 0, **58 tests**, no skips; existing malicious duplicate ZIP fixtures emit two expected `UserWarning`s. Log `/tmp/otgd-provenance-focused-green.log`.
5. **Broader release GREEN:** `OTGD_ENVIRONMENT=test OTGD_DATABASE_URL=sqlite:// UV_CACHE_DIR=/tmp/otgd-uv-cache uv run --project services/api python -m unittest infra.test.test_provenance infra.test.test_deployment_cli infra.test.test_serverless_deploy infra.test.test_fargate_deploy infra.test.test_fargate_workflow infra.test.test_fargate_continuation_workflow infra.test.test_serverless_workflow infra.test.test_serverless_recovery -q` — exit 0, **232 tests**, no skips, 20.384 seconds. Expected duplicate ZIP fixture warnings and temporary recovery-journal messages. Log `/tmp/otgd-provenance-release-green.log`.
6. **Canonical infrastructure gate FAILED:** `OTGD_ENVIRONMENT=test OTGD_DATABASE_URL=sqlite:// UV_CACHE_DIR=/tmp/otgd-uv-cache uv run --project services/api python scripts/ci_gate.py infra-unit` — exit 1; unittest reports **478 tests, 2 errors**. `test_fargate_containers.FargateContainerTests.setUpClass` attempted `docker build --platform linux/amd64 --target ui …` and failed during client setup with `ERROR: mkdir /home/agent/.docker/buildx: read-only file system`. `test_worker_interrupt_probe` import failed because another builder's `infra/local/worker_interrupt_probe.py` did not yet exist; that file appeared later, but this gate was not rerun. Secure-SDK pytest follow-up was not reached. Log `/tmp/otgd-provenance-infra-unit.log`.

The infrastructure gate unexpectedly entered a Docker-build test despite this builder's no-Docker-mutation restriction. The builder should have inspected that setup first, immediately notified PM, did not retry, and did not bypass the failure or change Docker configuration. Client setup failed before successful build evidence; no Docker state change was confirmed. This gate failure remains recorded, not converted into a pass by the 232-test focused suite. PM/verifier must run the canonical gate under its separately authorized runtime plan. No live deployment, workflow dispatch, git mutation, cleanup, participant use or data reset was performed by this builder.

New behavioral regressions name the missing-runtime default verification, owned-client gate file, real platform build and real serverless admission paths. Existing adversarial checks retain failed/skipped/cancelled/wrong-attempt/wrong-revision/duplicate-ID runtime refusal, pagination, trusted workflow/main and signed QA bindings. Workflow contract checks cover explicit historical intent; earlier Fargate chain checks still require fourteen. No test assertion was weakened to accept base-only current admission.

## Exact current native build requirements — read-only inventory

Source: `.github/workflows/native-build.yml` and `hosted-native-preview.yml`, as inspected in this candidate; no dispatch or build performed for this inventory.

- **Shared/firmware (Ubuntu 24.04):** Node 24.19.0, `npm ci`, typecheck, mobile coverage, native asset verification; portable C++17 `-Wall -Wextra -Werror` protocol and signed-reader acquisition tests; Arduino CLI 1.5.1 checked SHA-256, `arduino:esp32@2.0.18-arduino.5`, ArduinoJson 7.4.2, pyserial 3.5; actual SparkFun/reader core/grant C++ tests and fixture-byte comparison; `arduino-cli compile --fqbn arduino:esp32:nano_nora --warnings all` for both simulator and signed-reader firmware. Artifacts `nano-esp32-synthetic-firmware` and `nano-esp32-signed-reader-firmware`.
- **Protected reader (Ubuntu 24.04):** Python 3.12/uv 0.13.0; `python firmware/tools/secure_reader_build.py prepare --cache "$RUNNER_TEMP/otgd-secure-sdk"`; hash-locked requirements; checked `xtensa-esp32s3-elf`, CMake and Ninja; ephemeral fictional RSA-3072 key; `secure_reader_build.py build --cache … --output … --boot-signing-key …` compiling actual encrypted NVS/secure boot/authenticated BLE branch. Artifact includes application/bootloader/partition binaries and build manifest. No provisioning or eFuse operation.
- **Android (Ubuntu 24.04):** Node 24.19.0, Temurin JDK 17, Android platform 36/build-tools 36.0.0, asset verification and Expo prebuild. From `apps/mobile/android`: `./gradlew --no-daemon --max-workers=2 --init-script ../modules/scripts/local-preview.init.gradle -PreactNativeDevServerPort=8082 -PreactNativeArchitectures=arm64-v8a,x86_64 :otgd-reaction-task:testDebugUnitTest :otgd-eye-capture:testDebugUnitTest :app:assembleDebug :app:assembleRelease`. Require both Kotlin JUnit inventories without skips; verify inspected standalone APK, local application ID and development signer. Artifacts `android-local-preview-apk`, `android-debug-apk`, native test reports.
- **iOS (macOS 26):** `DEVELOPER_DIR=/Applications/Xcode_26.4.1.app/Contents/Developer`, Node 24.19.0, assets, actual `swift test --package-path apps/mobile/modules/{reaction-task,eye-capture} --parallel --num-workers 1 --verbose --disable-swift-testing --xunit-output …`; verify each XCTest XML/log and JUnit; Expo prebuild, `pod install --project-directory=ios`, `python3 modules/scripts/build_ios.py`. Artifact `ios-simulator-app` plus native reports. Complete unsigned ARM64 simulator build, not signed iPhone/TestFlight evidence.
- **Mandatory preview siblings:** Android repeats coverage/Kotlin golden tests, reviewed SDK and bundled `assembleRelease`, verifies APK, then `hosted_preview.py prepare/review` with exact committed sources. iOS repeats coverage/Swift no-skip fixtures, Xcode 26.4.1/prebuild/pods/full simulator build and `hosted_preview.py prepare/review`. Artifacts `android-hosted-guest-${github.sha}` / `ios-hosted-guest-${github.sha}`. Neither job uploads to or launches a hosted device service. Physical/native OS journeys, timing/sensing/scientific qualification and store release remain separate evidence.

## Available remote evidence — historical only

Read-only connected GitHub tools queried baseline `0844868aa543af4ab75ac5065ad48cf807b86bb3` and returned [Required application gates run 38347011315](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38347011315), reported completed/success. Its latest-attempt first-page job tool returned all **14 jobs**, each completed/success, including:

| Job | Job ID |
|---|---|
| `native / shared-and-firmware` | `115137237046` |
| `native / protected-reader` | `115137236695` |
| `native / android` | `115137236836` |
| `native / ios` | `115137237153` |
| `preview / android` | `115137236758` |
| `preview / ios` | `115137236693` |
| `platform / fargate-container-runtime` | `115137236702` |
| `merge-gate` | `115140527201` |

Returned step summaries mark the actual protected-branch compile, Android SDK/Kotlin/APK build, Swift suites/full simulator build and preview prepare/review steps successful. Full logs, native reports, artifact bytes/signatures, physical device results and remote branch protection were not examined. These tools normalize away some run provenance fields; the commit-run wrapper filters **pull-request runs and returns first page only**, so this does **not establish trusted-main admission**. The same wrapper returned no PR runs for coordination HEAD `8171dbffb7a38da9f7d17da08b71eccc73674057`; that is not proof that no other events/runs exist. Combined-status query for baseline returned an empty status list, which does not supersede Actions job evidence. No current mutable source run is claimed.

## Delivery and remaining work

Owned code/workflow/test output is ready for PM inspection and independent review; this author gives no signoff. Six changed source/test/workflow files plus this report are handed back. No production Python caller beyond `deploy/provenance.py` needed modification because its imported live default propagates to every inspected caller. `deploy/README.md` still lists thirteen as its current default; PM/documentation owner should reconcile that current-admission paragraph while retaining historical receipt/recovery distinctions. It was outside assigned documentation ownership and was not changed here.

Current-source complete gates, both coverage inventories strictly above 80%, required native/device/live categories, independent reviews/signoffs, source freeze, commit/push and any release decision remain PM/verifier work. The canonical infra gate failed as recorded; no successful full-gate or deployment outcome is implied. Default measurement mode, fictional/research authority, scientific qualification and separate future calibrated mg/L breath-channel boundaries are unchanged.
