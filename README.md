# One-The-Go Detection

A mobile and device development platform for one saliva sample, physiological measurements, and one continuous reaction task, with a separate future breath-alcohol channel.

**The repository contains the reviewed OpenSpec feature set, Android/iOS application source, native modules, API/worker, reader firmware and LocalStack/QA/production infrastructure.** Measurement mode is the default. The separate `ResearchResult 1.1.0` software path can execute a bounded research model only with current, independently released study, consent, device, calibration and model/evaluation authority. No genuine human approvals, qualified clinical model, validated saliva assay or approved human sensor configuration are seeded. Fictional examples and uncalibrated practice do not establish intoxication, metabolic clearance or fitness to drive.

Read the [implementation and verification status](IMPLEMENTATION_STATUS.md) for the exact distinction between supplied source, passing checks, native builds and external release prerequisites. No AWS deployment or clinical qualification is implied by source or infrastructure synthesis.

The [required merge checks](docs/CI_GATES.md) describe the strict coverage, browser, performance, real-dependency, Docker, LocalStack and native gates. At the [`155c60d` checkpoint](https://github.com/R3fresh-dev/One-The-Go-Detection/commit/155c60d78273980dfde4d52bffbaa29ec36e6fb1), all seven local gate categories and [all eleven aggregate GitHub jobs](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38123602878) passed. Further changes require fresh checks on their exact revision. Branch-protection administration returned HTTP 403, so enforced merge protection remains unverified.

## Start here

| What you want | Start here |
|---|---|
| Find the project documents | [Document index](docs/README.md), including the [integrated device/app/model MVP](docs/product/MVP_SCOPE.md), [marketing plan](docs/business/MARKETING_PLAN.md), and [YC application draft](docs/business/YC_APPLICATION_DRAFT.md). |
| Buy the initial bench parts | [Exact shopping list and vendor links](specs/SHOPPING_LIST.md): **$94.40**, or **$115.90 with a multimeter**, before tax/shipping. |
| Review the product and architecture | [PRD](specs/PRD.md), [HLD](specs/HLD.md), [LLD](specs/LLD.md), [full specification](specs/FULL_SPECIFICATION.md). |
| Implement/review one app feature | [20-feature OpenSpec index](openspec/changes/production-mobile-platform/README.md), [shared contracts](openspec/changes/production-mobile-platform/shared-contracts.md), [tasks](openspec/changes/production-mobile-platform/tasks.md). |
| See the adversarial review | [Findings and re-review ledger](openspec/changes/production-mobile-platform/reviews/RESOLUTION_LEDGER.md). |
| Run Android/iOS | [Mobile application](apps/mobile/README.md), native modules under `apps/mobile/modules`. |
| Try the UIs in a browser | [Codespaces web preview, Appetize native preview and service costs](docs/BROWSER_ACCESS_AND_SERVICES.md). |
| Run actual local service dependencies | [LocalStack and PostgreSQL quick start](infra/README.md), [routing/environment settings](infra/ENVIRONMENT.md). |
| Deploy an approved release to AWS | [Fargate development deployment](deploy/FARGATE_AWS.md), [QA/production tooling](deploy/README.md), [operator runbooks](infra/runbooks/OPERATIONS.md), [development cost estimate](infra/costs/FARGATE.md). |
| Work on the backend/API | [Service engineering guide](services/api/README.md), [generated application contract](contracts/application/README.md). |

## Specifications before implementation

The reviewed specification checkpoint is commit [`47d8ecb`](https://github.com/R3fresh-dev/One-The-Go-Detection/commit/47d8ecbfc871b5026f32d4f5f474908e9c0e1b14). It contains **20 Android feature capabilities, 140 requirements and 321 acceptance scenarios**, with iOS parity, detailed customer flows and engineering contracts. Three independent review perspectives covered product/domain, security/data and platform/operations. The ledger preserves 38 original findings, their corrections and targeted re-reviews; no critical/high specification blocker remained before implementation began.

The latest AWS requirement is implemented as three separate environments. The scientific gates in the original PRD/HLD/LLD remain open. Later commercial-strategy research is preserved as proposed alternative scope, not silently substituted for this application.

The selected first product milestone is an [integrated physical device, companion app, and research model MVP](docs/product/MVP_SCOPE.md). Its development includes the existing P0/P1 measurement prerequisites and P2 authorized model evaluation; it does not close the independent consumer-release gates. Customer discovery and the [consumer marketing plan](docs/business/MARKETING_PLAN.md) progress alongside that work. The repository is the source of record for project documents.

## Application and platform source

The mobile application uses Expo/React Native with shared Android/iOS journeys and native Kotlin/Swift modules for the reaction task, BLE transport and protected storage support. It includes first-run introduction, notice acknowledgment, PKCE sign-in, profile/context, Home, guided checks, sensor steps, history, results, explicit uploads, export, deletion, settings and study membership/withdrawal.

Native account data uses SQLCipher with protected per-workspace keys and an encrypted outbox. The browser preview is deliberately memory-only. The reaction module retains full trial/input/timing evidence, checks the frozen task configuration and marks practice uncalibrated. Sensor simulators retain fictional provenance. Phone preview and a generic board are not treated as selective cannabinoid sensors.

The FastAPI/PostgreSQL service supplies owner/generation isolation, immutable evidence, RFC 8785 hashes, conditional versioned S3 uploads, SQS workers, independently governed raw-inclusive exports and deletion recovery. QA/prod CDK stacks provide private Fargate/RDS, TLS ingress, Cognito, private encrypted buckets/queues, secrets, backups, budget inputs and alarms. Dependency and base-image locks are committed; deployment receipts must bind the actual reviewed service image digest and web artifact. Separate [QA and production Python commands](deploy/README.md) deploy infrastructure, security and code, and [register_cname.py](deploy/register_cname.py) verifies the deployed UI distribution before registering an owned subdomain. These cloud operations have not been executed here.

## Run the mobile preview

Use Node 24.19.0 and npm 11 with the committed lockfile:

```bash
npm ci --prefix apps/mobile
npm run typecheck --prefix apps/mobile
npm test --prefix apps/mobile
npm run web --prefix apps/mobile
```

The preview runs on port **8082**, leaving **8081** for the local identity issuer. Guest demo works without the backend. Web preview does not implement native reaction acquisition, Bluetooth, OS-protected account storage or native sharing behavior. Use a development client for those paths. For browser-only setup, select the feature branch containing the devcontainer in [Codespaces](docs/BROWSER_ACCESS_AND_SERVICES.md). Pull requests targeting `main` now include required guarded hosted-native artifact builds; their successful execution must be observed before using artifacts. Manual dispatch becomes available after the workflow reaches default `main`. An Appetize account and an actual guest-only launch are still required. No hosted native session or store release has been launched here.

For Android, install the documented SDK/JDK and run `npm run android` from `apps/mobile`. For iOS, use the documented macOS/Xcode toolchain and `npm run ios`. The mobile guide gives exact emulator/phone environment settings and explains the difference between a debug APK, simulator app and signed store build. Expo Go cannot supply these custom native modules or SQLCipher configuration.

## Run LocalStack and the service

Install Docker with Compose v2, Python 3.12 and `uv` 0.13.0. The pinned community LocalStack preset needs no subscription or authentication token. For a new disposable fictional workspace, run:

```bash
uv sync --project services/api --locked
python scripts/local-platform.py prepare --host localhost
python scripts/local-platform.py up
python scripts/local-platform.py check
```

Choose the correct host **before preparing the environment and building the app**: `localhost` for the iOS simulator, `10.0.2.2` for the Android emulator, or your computer's LAN IP with `--lan` for a physical phone. Configure API and OAuth origins consistently; identity issuer URLs must match exactly. See the [routing table](infra/ENVIRONMENT.md#local-phone-routing).

For an existing workspace, preserve its secrets, database and independently versioned journal. Follow the [retained-runtime upgrade checklist](docs/JOURNAL_CONTINUITY.md#upgrade-a-retained-local-runtime) before recreating services. Community LocalStack storage persistence is unqualified; a restart can lose journal objects even while PostgreSQL survives. The optional licensed preset needs its own entitlement and restart/recovery qualification; see [infra/README.md](infra/README.md).

For a disposable fictional local workspace, `python scripts/local-platform.py check-app --confirm-fictional-workspace` exercises actual PKCE → HTTP API → SQS worker → export → all-data deletion. This command deletes Fictional Account A's local data. The script requires real local services and never calls an in-process replacement worker.

## Verify contracts and backend source

```bash
uv run --project services/api python tools/verify_specs.py
uv run --project services/api pytest -q services/api/tests
uv run --project services/api python tools/generate_application_contracts.py
npm ci --ignore-scripts --prefix infra
npm run verify --prefix infra
OPENSPEC_TELEMETRY=0 npx --yes @fission-ai/openspec@1.14.1 validate production-mobile-platform --strict
```

Read the verification report for actual counts and externally unexecuted gates. The [required aggregate workflow](.github/workflows/merge-gate.yml) requires unit coverage strictly above 80%, ATDD, components, performance, real dependencies, every Docker health outcome, LocalStack API/application flows, PostgreSQL, firmware and Android/iOS checks on the exact revision. No skipped required job qualifies. Verify GitHub branch protection separately; a green source job does not satisfy AWS or physical-device release acceptance.

## Hardware sequence

Start with the **Arduino Nano ESP32 with headers (ABX00083)** and the exact [shopping basket](specs/SHOPPING_LIST.md). The new `firmware/nano_esp32_ble_simulator` firmware exercises the app's bounded synthetic BLE transport. The original [USB serial sketch](examples/arduino/synthetic_serial/synthetic_serial.ino) remains useful for the first board/USB check.

First establish repeatable board power, USB upload and explicitly fictional BLE exchange. Then wire and validate the selected SparkFun PPG driver and finger fixture using the documented 3.3 V wiring. Develop selective saliva chemistry, collection and reference-method comparison with a suitable laboratory in parallel. ECG begins with simulator/circuit review; qualified optics, human-contact electronics and chemical measurement are separate engineering milestones. A custom PCB follows demonstrated sensing and power requirements.

## Research reports

- [THC chemistry and sensing review](specs/research/THC_CHEMISTRY_REVIEW.md): 46-source review of metabolites in blood, urine, and saliva; breath collection; sensing methods; and implications for the pocket device. [PDF edition](specs/research/THC_Chemistry_and_Pocket_Device_Research.pdf).
- [FDA regulatory and compliance assessment](specs/research/FDA_REGULATORY_ASSESSMENT.md): current US classification, study, quality, software, cybersecurity, and postmarket requirements mapped to the repository's evidence gates. [PDF edition](specs/research/FDA_Regulatory_Assessment.pdf).
- [Faster market-entry strategy](specs/research/FAST_MARKET_STRATEGY.md): proposed staged launch using existing products and a limited app, followed by an OEM all-in-one exposure device; includes a 30-day readiness sprint and illustrative $20/month economics. These research recommendations do not change the current product requirements or close release gates. [PDF edition](specs/research/Fast_Market_Strategy.pdf).

## Result and release boundaries

| Release area | Current behavior / evidence needed |
|---|---|
| Demonstration | Fictional sensor values and separately labeled native practice; guest records stay local. |
| Account data | Explicit profile saves and check uploads, current notice, account ownership and data-generation enforcement. |
| Human channel | Requires actual qualified hardware/configuration, current study/consent where applicable, and exact provenance; no approved real configuration is seeded. |
| Research model execution | Conditional `ResearchResult 1.1.0` admission, scoring, abstention and evidence readers are implemented. Legacy `0.1.0` results and fictional hosted previews remain measurement-only. Genuine independent approvals, endpoint labels, locked evaluation and prospective validation are required before participant research use or any impairment claim. |
| AWS production | Infrastructure and promotion controls supplied; actual QA evidence, deployment inputs, credentials, operator ownership and release gates are required. |

Keep real participant recordings, identifiable measurements and credentials out of this repository. Examples and test fixtures are fictional. Qualification cannot be manufactured with a `validated_sensor` string, a device name, a CRC or an approval flag. Changes to units, assay basis, collection matrix, task configuration, feature extraction, hardware scope or model eligibility require coordinated changes to contracts and evidence.

Supporting documents: [reading order](specs/README.md), [validation plan](specs/VALIDATION_PLAN.md), [decision log](specs/DECISIONS.md), [source register](specs/SOURCES.md) and [hardware development guide](specs/HARDWARE_STARTER_GUIDE.md).
