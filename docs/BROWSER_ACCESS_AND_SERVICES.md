# Browser access and external services

Use the canonical application in `apps/mobile`. No account purchases are needed to start the fictional web preview within your GitHub Codespaces allowance.

## Open the web UI without cloning or terminal commands

Open [Create a Codespace](https://codespaces.new/R3fresh-dev/One-The-Go-Detection). Select the reviewed feature branch containing `.devcontainer/devcontainer.json`; until that change merges, the older default `main` does not supply this preview setup. Choose the two-core machine and create the Codespace. GitHub checks out the repository inside its cloud workspace; you do not clone it onto your computer.

The container installs locked dependencies, checks TypeScript, builds the fictional guest web export and starts port 8082 automatically. The forwarded preview opens in the browser. If it does not open automatically, choose **Ports → Fictional application preview → Open in Browser**. Keep the default private port visibility. Stop the Codespace when finished; delete it when you no longer need its stored workspace.

This preview uses isolated fictional guest data. It does not sign into a research account, connect hardware, record camera data or execute an approved model. The ordinary application and its API/LocalStack tests use their normal configuration. Actual signed-in web/device testing belongs in a separately provisioned AWS QA environment.

The Node 24.19.0 container is pinned by its official multi-platform image digest, checked on 2026-10-11. `prepare-preview.sh` and `start-preview.sh` run automatically through devcontainer lifecycle hooks. Setup failures stop preview startup and leave a local diagnostic log, rather than displaying an assumed-ready UI. A successfully exported local UI does not establish that a Codespace or authenticated native simulator session was launched.

## Native iOS and Android in a browser

Use [Appetize](https://appetize.io/) for an interactive hosted iOS simulator or Android emulator. The canonical hosted-preview workflow builds the actual application with a fictional guest guard, executes native fixture tests and prepares source-bound artifact evidence. Pull requests targeting `main` now include mandatory Android/iOS guest builds in the required aggregate with read-only repository access, no service secrets and no Appetize upload. Verify the successful aggregate run and tested source before downloading its artifacts. Manual **Run workflow** becomes available after the workflow exists on default `main`. Upload the verified build through your account and check the guest-only launch. See [hosted native preview instructions](../apps/mobile/HOSTED_PREVIEW.md). No Appetize upload or session launch has occurred here.

An Appetize account is still required for a hosted session. Native browser simulation does not replace physical-phone camera, Bluetooth, display/touch timing or electrical/optical qualification. For installation on real iPhones, use a signed TestFlight build after Apple enrollment; use an internal Google Play track for Android after enrollment. Store review and release approval precede public downloads.

## What to pay for

Official pages were retrieved on **2026-10-11**. Prices may change and depend on region and plan.

| Purpose | Service and current guidance |
|---|---|
| Fictional browser preview | [GitHub Codespaces billing](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces): personal GitHub Free includes 120 core-hours and 15 GB-month storage. Two cores consume two core-hours per elapsed hour, giving about 60 elapsed hours within that compute allowance. Additional two-core usage is listed at $0.18/hour. Existing allowance, billing settings and storage limits apply. |
| Native UI in a browser | [Appetize pricing](https://appetize.io/pricing): free single-user tier lists 30 minutes refilled monthly and two active devices. Start there if its artifact/API/private-access features suit your account; a paid team plan is optional. The page lists Starter at $59/month billed annually ($708/year); verify the selected billing period before buying. |
| iPhone/TestFlight/App Store distribution | [Apple Developer Program](https://developer.apple.com/programs/enroll/): $99 per membership year, subject to regional pricing and eligible fee waivers. Simulator builds can be prepared without membership. |
| Google Play distribution | [Google Play developer registration](https://support.google.com/googleplay/android-developer/answer/6112435): $25 one-time fee, plus identity verification and applicable testing requirements. |
| Signed-in QA and production | [AWS](https://aws.amazon.com/pricing/): usage-based resources in separate QA/prod accounts, plus an owned domain. Budget for RDS, ECS/ALB, NAT, S3/CloudFront, KMS, logs, backups and DNS. Use a current region-specific calculator estimate from the actual synthesized infrastructure; there is no justified flat monthly price yet. |
| Durable local AWS emulation | Pinned community LocalStack 4.14 supports the current fictional tests and requires no subscription. Its state is ephemeral. [LocalStack persistence](https://docs.localstack.cloud/aws/developer-tools/snapshots/persistence/) is listed for licensed Base/Ultimate plans. Buy a suitable plan only if durable emulator state or its additional services are needed. Retained PostgreSQL must never silently adopt a replacement deletion journal. |
| Real research measurements | Approved reader/sensors, calibration/reference equipment, reference-laboratory services and qualified study/safety/statistical oversight. Procure against the selected protocol; software subscriptions do not create a validated THC assay or impairment model. |

OpenSpec, Python/uv, Node, PostgreSQL and the application source do not require separate commercial purchases for this workflow. Expo's hosted build service is optional because the repository already has native GitHub Actions builds.

## Release evidence

All seven required local/integration categories and the complete native/platform/guest-preview aggregate must pass on the exact release revision with unit coverage strictly above 80%. The [`155c60d` checkpoint](https://github.com/R3fresh-dev/One-The-Go-Detection/commit/155c60d78273980dfde4d52bffbaa29ec36e6fb1) passed all seven local categories and [all eleven aggregate GitHub jobs](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38123602878). Changes after that checkpoint require fresh local and GitHub evidence. GitHub protection must also require the aggregate, including for administrators; its administration request returned HTTP 403 and enforced protection remains unverified. A preview launch, historical green run or saved workflow does not replace those criteria. See [CI gates](CI_GATES.md), [implementation status](../IMPLEMENTATION_STATUS.md) and [the alignment audit](REQUIREMENTS_ALIGNMENT_AUDIT.md) for software and external acceptance boundaries.
