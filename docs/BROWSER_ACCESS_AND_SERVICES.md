# Browser access and external services

Use the canonical application in `apps/mobile`. No account purchases are needed to start the fictional web preview within your GitHub Codespaces allowance.

## Open the web UI without cloning or terminal commands

Open [Create a Codespace](https://codespaces.new/R3fresh-dev/One-The-Go-Detection). Select `feat/complete-research-platform`, the branch containing this reviewed follow-up. Choose the two-core machine and create the Codespace. GitHub checks out the repository inside its cloud workspace; you do not clone it onto your computer.

The container installs locked dependencies, checks TypeScript, builds the fictional guest web export and starts port 8082 automatically. The forwarded preview opens in the browser. If it does not open automatically, choose **Ports → Fictional application preview → Open in Browser**. Keep the default private port visibility. Stop the Codespace when finished; delete it when you no longer need its stored workspace.

This preview uses isolated fictional guest data. It does not sign into a research account, connect hardware, record camera data or execute an approved model. The ordinary application and its API/LocalStack tests use their normal configuration. Actual signed-in web/device testing belongs in a separately provisioned AWS QA environment.

The Node 24.19.0 container is pinned by its official multi-platform image digest, checked on 2026-10-11. `prepare-preview.sh` and `start-preview.sh` run automatically through devcontainer lifecycle hooks. The separate `dist-preview` export fixes unavailable account origins, ignores dotenv and preserves ordinary `dist`; startup verifies the guest receipt/export and refuses stale or unrelated HTTP content. Setup failures stop preview startup and leave a local diagnostic log. A successfully exported local UI does not establish that a Codespace or native simulator session was launched.

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
| Reviewed signed store build path | [Expo EAS pricing](https://expo.dev/pricing): the supplied store helper requires an actual Expo account/project and its signing/service access. Start with the available free build allowance; a paid plan depends on build volume and queue needs. A guest CI build does not replace signed store delivery. |
| Signed-in QA and production | [AWS](https://aws.amazon.com/pricing/): usage-based resources in separate QA/prod accounts, plus an owned domain. Budget for RDS, ECS/ALB, NAT, S3/CloudFront, KMS, logs, backups and DNS. Use a current region-specific calculator estimate from the actual synthesized infrastructure; there is no justified flat monthly price yet. |
| Optional Aurora/Lambda development | The selected architecture requires an active AWS Paid Plan, not the restricted Free Plan/Aurora Express configuration. [Deployment run 38224276329](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38224276329) actually refused that account-plan prerequisite before deployment stages. The supplied cost estimate and budget alerts do not cap charges. Guest Codespaces/Appetize testing does not require this AWS path. |
| Durable local AWS emulation | Pinned community LocalStack 4.14 supports the current fictional tests and requires no subscription. Its state is ephemeral. [LocalStack persistence](https://docs.localstack.cloud/aws/developer-tools/snapshots/persistence/) is listed for licensed Base/Ultimate plans. Buy a suitable plan only if durable emulator state or its additional services are needed. Retained PostgreSQL must never silently adopt a replacement deletion journal. |
| Real research measurements | Approved reader/sensors, calibration/reference equipment, reference-laboratory services and qualified study/safety/statistical oversight. Procure against the selected protocol; software subscriptions do not create a validated THC assay or impairment model. |

OpenSpec, Python/uv, Node, PostgreSQL and the application source do not require separate commercial purchases for this workflow. Expo is unnecessary for the fictional web preview and existing guest CI builds; the supplied signed store helper uses its actual EAS service.

## Release evidence

All seven required local/integration categories and the complete native/platform/guest-preview aggregate must pass on the exact release revision with unit coverage strictly above 80%. The [`9694554` checkpoint](https://github.com/R3fresh-dev/One-The-Go-Detection/commit/96945549ab0466c26300a2863f907cf20da35042) passed all seven local categories and [all thirteen GitHub jobs](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38131498621). This newer source requires its own checks. Main was independently observed unprotected with no effective rules, and protection administration returned HTTP 403. A preview launch, historical green run or saved workflow does not replace merge enforcement. See [release/browser instructions](RELEASE_AND_BROWSER_TESTING.md), [CI gates](CI_GATES.md), [implementation status](../IMPLEMENTATION_STATUS.md) and [alignment audit](REQUIREMENTS_ALIGNMENT_AUDIT.md) for software and external acceptance boundaries.
