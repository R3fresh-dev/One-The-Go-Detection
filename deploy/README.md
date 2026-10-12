# Deploy and promote a reviewed release

The CLI [platform.py](platform.py) makes every paid or operational action explicit. No AWS deployment has been performed in this workspace. It uses the normal AWS SDK credential chain, validates the account with STS, and passes database credentials through ECS secret references. Its defaults do not invent an AWS account, domain, alarm recipient, signing key or monthly budget.

## One command for QA, a separate command for production

[qa.py](qa.py) and [prod.py](prod.py) orchestrate infrastructure, security, API/worker code, private web hosting, maintenance, health and browser publication. They reuse the exact-source release admission below; they do not bypass it. Use the API's locked Python environment, Node 24.19.0, Docker Buildx for service build/promotion, the committed npm locks, actual AWS profiles, issued certificates and your independently trusted signing authority. Install `infra` dependencies before invoking them. No AWS account has been supplied or deployment executed here.

Validate an operator-supplied config and show the sequence without AWS access, builds, signing or mutations:

```bash
uv run --project services/api python deploy/qa.py --config infra/config/qa.local.json --plan
uv run --project services/api python deploy/prod.py --config infra/config/prod.local.json --plan
```

Example templates intentionally fail until real inputs and a current regional cost estimate are supplied. The existing published estimate describes the API baseline; add the fourth retained static-assets bucket, CloudFront request/egress/function usage and optional DNS assumptions before approving the hosting workload. CloudFront/S3 usage and retained versions continue to incur cost; a budget alert does not cap spending.

For a first empty QA environment:

```bash
uv run --project services/api python deploy/qa.py \
  --config infra/config/qa.local.json --profile your-qa-profile \
  --gate-evidence deploy/receipts/gates-REVIEWED_COMMIT.json \
  --trusted-public-key /secure/otgd-release-public.pem \
  --signing-key /secure/otgd-release-private.pem --establish-new
```

The command verifies the target account/TLS/database, bootstraps CDK, deploys the private registry, builds/signs the reviewed service, drains an existing rollout, deploys stopped infrastructure, establishes/verifies the independent journal, runs migrations, builds/signs the actual Expo web artifact using the new stack's Cognito identity, then runs independent admission verification in the exact maintenance task before activation. Activation requires its actual ECS completion within fifteen minutes, together with migration/recovery evidence. The command waits for worker progress health and publishes the web bytes. Dependency files precede `index.html`; exact stored bytes and bounded CloudFront invalidation are checked. Public HTTPS bytes/security headers, `/history`, a missing asset and API readiness are then verified. The receipt reports authenticated customer acceptance as **not executed**; perform the real QA probes before signing QA approval.

Each invocation saves immutable records under `.local/deploy/<environment>/<commit>/<attempt-id>/`. A private, bounded `deployment-state.json` is updated before/after each stage; completion is recorded only after that operation returns successfully. On failure it records the exact failed stage/type, completed stages and hashes/paths of actual existing receipts, prints the recovery path and reports no inferred rollback. Inspect it and protected task logs before retrying; do not assume a failed upload undid backend activation. Its final JSON contains `web_origin`, signed service/web release paths, the ZIP, actual maintenance receipt, publication IDs and concrete public probe results. Keep these records protected with the release evidence. On subsequent deployments omit `--establish-new`. `--release /path/to/signed-service.json` reuses an already admitted service record. A new attempt preserves prior records; existing same-prefix web objects must match, and conflicting bytes fail instead of being overwritten. Recoveries require `--backup-created-at <actual UTC snapshot point>` and the reviewed recovery configuration; creation of a new empty journal during recovery is rejected.

After actual QA browser/operational acceptance, use `platform.py approve-qa` below to sign the reviewed approval. In addition to the existing required probes, include `web_customer_access` in `passed_gates` and put `sha256:<SHA-256 of the signed QA web-release.json envelope>` in `evidence_refs.web_customer_access`. Separately set `evidence_refs.web_customer_access_results` to the actual protected authenticated browser acceptance report's HTTPS or S3 reference; production rejects an artifact hash without this separate results reference. The responsible authority must review that report and retain it. This is an explicit signed operator attestation, not an automated replay or an inference from the public probes; no command fabricates those results.

Production uses a separate account and this separate command:

```bash
uv run --project services/api python deploy/prod.py \
  --config infra/config/prod.local.json --profile your-prod-profile \
  --source-config .local/deploy/qa/REVIEWED_COMMIT/QA_ATTEMPT/stopped.local.json \
  --source-release .local/deploy/qa/REVIEWED_COMMIT/QA_ATTEMPT/service-release.json \
  --source-web-release .local/deploy/qa/REVIEWED_COMMIT/QA_ATTEMPT/web-release.json \
  --source-web-artifact .local/deploy/qa/REVIEWED_COMMIT/QA_ATTEMPT/web.zip \
  --source-profile your-qa-profile --qa-evidence /protected/qa-validation-signed.json \
  --gate-evidence deploy/receipts/gates-REVIEWED_COMMIT.json \
  --trusted-public-key /secure/otgd-release-public.pem \
  --signing-key /secure/otgd-release-private.pem --establish-new
```

Use `--establish-new` only for the first empty production environment. Promotion preserves the exact QA service digest and source. The production web build uses the same reviewed source/npm lock with fixed production API/issuer/client values, so its bytes differ from QA; its signed web record explicitly binds the approved QA web envelope. Missing/stale QA approval, artifact tampering, different accounts/source/runtime or a failed stage stops the sequence. Later web upload failure does not imply that already activated backend services were rolled back; inspect protected stage logs and use the runbook. No final verified-access receipt is written on failure.

## Browser URL, custom TLS and CNAME

The actual shared application opens at the receipt's HTTPS `web_origin`. Default hosting uses the CloudFront domain. Browser access retains the app's explicit guest/research, storage and native hardware limitations; opening it does not qualify camera/BLE or publish native apps to stores. Cloud sign-in and API use the exact registered web callback, and study authorization/consent still apply.

For a custom name, add `webDomain` and `webCertificateArn` to the environment JSON. The certificate must be issued for that name in **us-east-1**, in the same AWS account. Keep the separate API `certificateArn` in the deployment region. When the existing public `hostedZoneId`/`hostedZoneName` is supplied, the web name must be a subdomain; CDK creates its CNAME automatically. The zone apex is rejected because CNAME is requested. Without managed Route 53, register the output `WebDistributionDomain` through your DNS provider after TLS/distribution validation.

[register_cname.py](register_cname.py) also supports a separately selected existing public Route 53 zone. It accepts no arbitrary destination and checks the exact admitted stack/distribution, alias, issued TLS and zone ownership. It defaults to a live-validated preview. Add `--apply` to execute the single UPSERT and wait at most ten minutes:

```bash
uv run --project services/api python deploy/register_cname.py \
  --config .local/deploy/qa/REVIEWED_COMMIT/QA_ATTEMPT/stopped.local.json \
  --release .local/deploy/qa/REVIEWED_COMMIT/QA_ATTEMPT/service-release.json \
  --gate-evidence deploy/receipts/gates-REVIEWED_COMMIT.json \
  --trusted-public-key /secure/otgd-release-public.pem --hosted-zone-id YOUR_ACTUAL_ZONE_ID
```

Production DNS additionally requires the signed `--qa-evidence`. Apex/private/foreign zones, pending TLS, unready distributions and existing conflicting records fail without DNS mutation. DNS propagation status is not customer acceptance. Outputs contain resource IDs/public identities, never secret values. Static assets are private at S3 and served only through SigV4 OAC; viewer headers include CSP/HSTS/frame denial/no-sniff/no-referrer. Extensionless SPA routes rewrite to the app; missing asset paths stay errors.

The focused [OpenSpec delta](../openspec/changes/cloud-deployment-customer-access/proposal.md) defines implementation and acceptance boundaries. The detailed operations below remain available for inspection/recovery and individually repeat the same release checks.

## Independent registry operators

CDK outputs `RegistrySubmitter`, `RegistryReviewer` and `RegistryReleaser`, named `otgd-<environment>-registry-submitter`, `...-reviewer` and `...-releaser`. They have same-account MFA trust with one-hour sessions; CDK assigns no human an assume-role policy. The account administrator must authorize **three different responsible people**, each for the matching role, and review their effective permissions. Three session names for one role are one principal; distinct role names alone do not establish independent humans. Participant/API/worker roles cannot assume these roles through the defined trust and receive no authority-table writes.

These operator roles can resolve the exact three IAM role IDs and read only the environment's administrative database secret (with its decrypt grant). They have no generic ECS RunTask/PassRole grant. The operator CLI must run on an approved private operator host/VPN/tunnel with the human's actual assumed-role credentials and administrative PostgreSQL TLS configuration supplied through protected environment/secret loading. A generic migration ECS task runs under its task role and cannot pretend to be the reviewer. Network access, the three actual assignments and administrative credential handling remain real account setup inputs.

The releaser additionally reads the actual independent journal/ObjectLock evidence and can publish only the immutable `scope-resumptions/*` seals used by the separately reviewed post-restore reapproval command. Its KMS permissions are confined to that journal key. Runtime and migration tasks are explicitly denied writes to this authority prefix. The capture-grant signing key is separate: only API tasks receive signing permission; maintenance receives public-key lookup for binding. None of these IAM templates establishes physical device or scientific qualification.

The separately maintained [operator CLI](../services/api/otgd/operator_cli.py) verifies STS account, exact IAM ARN/immutable RoleId and the named role appropriate to the command. Example validation (default rollback, no approval mutation):

```bash
uv run --project services/api python -m otgd.operator_cli \
  --expected-account YOUR_ACTUAL_ACCOUNT \
  --expected-role-arn ACTUAL_REGISTRY_SUBMITTER_OUTPUT \
  submit study /protected/reviewed-study.json
```

Use the reviewer role for `approve`, and releaser role for `release`, `retire` or `revoke`; supply exact version/revision and a non-sensitive audit reason. `--apply` must precede the subcommand to commit the reviewed operation. Immutable submitted evidence, separate role principals and revisions are checked by the service. Administrative database operators remain trusted; they can bypass application workflows through direct SQL, so this is audited workflow separation plus independently administered IAM assignment, not a claim of malicious-administrator-proof database isolation. Deployment/DNS roles do not implicitly approve studies, devices, calibration or models, and no registry content is auto-approved by the deployment scripts.

## 1. Supply real environment inputs

Copy the relevant [QA](../infra/config/qa.example.json) and [production](../infra/config/prod.example.json) templates into ignored `*.local.json` files. Read the [environment contract](../infra/ENVIRONMENT.md). Obtain an issued regional ACM certificate and an appropriate public domain. Register the environment's exact mobile callbacks. The software creates Cognito itself; you do not need to invent a pool/client ID in advance.

Commit a current [cost estimate](../infra/costs/README.md), choose the monthly budget and operational destination, identify the accountable operator, and activate the `deployment` tag as an AWS cost-allocation tag. Budget alerts cannot guarantee a spending cap. The operator needs permission for CDK bootstrapping/deployment, IAM, ECR, ECS, RDS, S3/KMS, Cognito, logs, SQS, SNS and Budgets in the selected account. Use an approved human/CI identity; do not put access keys in project files.

Install dependencies:

```bash
npm ci --ignore-scripts --prefix infra
uv sync --project services/api --locked
```

Validate without AWS writes:

```bash
uv run --project services/api python deploy/platform.py validate --config infra/config/qa.local.json
uv run --project services/api python deploy/platform.py synth --config infra/config/qa.local.json
uv run --project services/api python deploy/platform.py preflight --config infra/config/qa.local.json
```

A normal full preflight expects the configured image digest already in ECR. Registry/bootstrap and build commands use the earlier phase that does not require that image yet. The CLI checks the ACM certificate, RDS minor/class and optional public hosted zone. Exact RDS minor `16.14` in the template is a candidate, not a promise of availability. QA/prod SDK clients ignore configured service endpoints, and child commands remove inherited `AWS_ENDPOINT_URL*` overrides and enable `AWS_IGNORE_CONFIGURED_ENDPOINT_URLS`; an inherited LocalStack setting cannot authorize cloud identity checks or redirect deployment mutations.

## 2. Bootstrap CDK and the private registry

A first-time AWS account/region needs the standard CDK bootstrap stack. Review its proposed roles/storage before running the command with your real account and region. [CDK bootstrapping](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html)

```bash
cd infra
npm exec -- cdk bootstrap aws://YOUR_ACTUAL_ACCOUNT/us-east-2
cd ..
uv run --project services/api python deploy/platform.py registry --config infra/config/qa.local.json
```

The registry keeps tags immutable and images retained so rollback targets are not silently expired. The CLI preserves CDK's review of broadened IAM permissions during an actual deployment.

## 3. Build and sign the immutable release

Use a release-signing key controlled by the responsible operator. The CLI expects Ed25519 PEM, readable only by its owner. Keep the private key outside the repository/image; distribute the public key through a separate trusted operator/CI channel. Do not trust a public key supplied inside an untrusted release record.

The `build` command requires a clean, committed checkout and `releaseId` equal to its full Git commit. Download `gates.json` from that revision's **Required application gates** run and supply `--gate-evidence` for release operations. The CLI verifies the actual GitHub API run and every job in its latest attempt; the file's claims alone cannot authorize a release. Configure authorized Actions read access through `GH_TOKEN` or `GITHUB_TOKEN` when the repository requires it. Tokens stay in request headers and must never be committed or placed in command arguments.

Eligible runs belong to `R3fresh-dev/One-The-Go-Detection`, use the active `.github/workflows/merge-gate.yml`, and test the exact release commit through `push` on `main` or the actual `merge_group` commit targeting `main`. PR-only, manual, fork, older direct platform/native workflows, skipped jobs and an earlier successful attempt do not qualify. Required job names are `unit-coverage`, `atdd`, `components`, `merge-gate`, `platform / contracts-and-synthesis`, `platform / postgres-integration`, `platform / localstack-integration`, `native / shared-and-firmware`, `native / protected-reader`, `native / android`, `native / ios`, `preview / android`, and `preview / ios`. All thirteen required jobs must execute successfully in the qualifying aggregate; nested names and exact source must be confirmed against that run. The verifier fails closed if they differ.

Docker Buildx builds the locked Linux/amd64 service image from `git archive` of the exact commit, pushes a commit tag, obtains its ECR digest and signs a canonical release record. Ignored/untracked files and concurrent checkout edits cannot enter that immutable build context. The CLI applies `org.opencontainers.image.revision`, pulls the actual pinned image, checks its revision label and configuration digest, and rechecks the clean source before signing. The release binds that image configuration digest; deployment and activation retrieve the immutable ECR manifest and verify its digest/configuration against the signed record. Promotion preserves the same digest/configuration and source label. Multi-platform indexes or unverifiable manifest representations fail closed in this Linux/amd64 release path.

Authentication is sent to Docker through stdin; it is not placed in arguments or logs. Configure Docker's credential helper for the operator account. The signing key must match the independently trusted public key. The signed record includes the GitHub run ID, attempt, workflow, exact SHA and required job IDs, plus their canonical SHA-256. A rerun invalidates an older signed receipt until a fresh record binds the new successful attempt; changing a local `passed` array cannot repair it. The CLI checks for changed run evidence again after long build/promotion work and immediately before activation. Older signed records without these source/gate bindings cannot activate through this CLI; obtain a newly reviewed record rather than weakening verification.

```bash
uv run --project services/api python deploy/platform.py build \
  --config infra/config/qa.local.json \
  --signing-key /secure/otgd-release-private.pem \
  --trusted-public-key /secure/otgd-release-public.pem \
  --gate-evidence deploy/receipts/gates-REVIEWED_COMMIT.json \
  --output deploy/releases/qa-REVIEWED_COMMIT.json
```

Copy the resulting actual `image_digest` into the QA config. A signed record binds account, region, environment, source commit, exact digest, database schema and `inference_available=false`. The file is immutable; a new record uses a new path. Container scanning, source review and dependency checks must pass for the digest before activation. ECR scan-on-push is configured, but a configured scanner is not a passed scan.

## 4. Create services in the stopped state

Keep `activateServices=false`. Use the signed release and independently trusted public key:

```bash
uv run --project services/api python deploy/platform.py deploy-stopped \
  --config infra/config/qa.local.json \
  --release deploy/releases/qa-REVIEWED_COMMIT.json \
  --gate-evidence deploy/receipts/gates-REVIEWED_COMMIT.json \
  --trusted-public-key /secure/otgd-release-public.pem
```

Inspect stack outputs for public API/issuer/client configuration, private maintenance networking, resource names, secrets **ARNs**, the database connection budget and image digest. No secret value is output.

For the first **empty** deployment only, establish the independent journal's continuity record:

```bash
uv run --project services/api python deploy/platform.py bootstrap \
  --config infra/config/qa.local.json \
  --release deploy/releases/qa-REVIEWED_COMMIT.json \
  --gate-evidence deploy/receipts/gates-REVIEWED_COMMIT.json \
  --trusted-public-key /secure/otgd-release-public.pem \
  --establish-new --output deploy/receipts/qa-bootstrap.json
```

A subsequent bootstrap omits `--establish-new`. A missing journal after data admission is a recovery incident; creating a new empty journal would conceal missing deletion evidence and is forbidden.

Run migration before traffic:

```bash
uv run --project services/api python deploy/platform.py migrate \
  --config infra/config/qa.local.json \
  --release deploy/releases/qa-REVIEWED_COMMIT.json \
  --gate-evidence deploy/receipts/gates-REVIEWED_COMMIT.json \
  --trusted-public-key /secure/otgd-release-public.pem \
  --output deploy/receipts/qa-migration.json
```

The CLI verifies all API/worker tasks are stopped, runs one private maintenance task, enforces a 15-minute deadline and records its actual ECS task ARN and exit status. The migration uses the separate administrative credential, an advisory lock and timeouts; it gives the application DML rights while denying DDL and writes to operator/recovery authority tables. The baseline migration provisions no study, device qualification or model.

## 5. Activate and validate QA

With services still stopped, verify independent journal admission after migration and any required restore. This checks actual journal/control Object Lock and pinned versions, accepted deletion/generation barriers and the current database activation binding. It is required in QA/prod even when snapshot recovery is not selected:

```bash
uv run --project services/api python deploy/platform.py verify-admission \
  --config infra/config/qa.local.json \
  --release deploy/releases/qa-REVIEWED_COMMIT.json \
  --gate-evidence deploy/receipts/gates-REVIEWED_COMMIT.json \
  --trusted-public-key /secure/otgd-release-public.pem \
  --output deploy/receipts/qa-admission.json
```

Then set `activateServices=true` in the reviewed QA config and activate within fifteen minutes of admission-task completion:

```bash
uv run --project services/api python deploy/platform.py activate \
  --config infra/config/qa.local.json \
  --release deploy/releases/qa-REVIEWED_COMMIT.json \
  --gate-evidence deploy/receipts/gates-REVIEWED_COMMIT.json \
  --trusted-public-key /secure/otgd-release-public.pem \
  --output deploy/receipts/qa-migration.json \
  --admission-receipt deploy/receipts/qa-admission.json
```

Activation re-verifies the signed release and checks the exact deployed maintenance task-definition ARN, cluster, start marker, single migration container, immutable image and successful exit. Receipts bind account, region and release revision. The complete migration, restore or admission command must match, including the recovery timestamp and quiescence flag; an unused module/script argument does not qualify. Unexpected environment, role and resource overrides are rejected. Snapshot recovery timestamps must match the actual selected recovery point. Admission must run `uv run --no-sync python -m otgd.recovery_authority` without environment overrides, have an actual ECS stopped time within fifteen minutes and a UTC receipt completion within sixty seconds of that time. Missing, stale or fabricated receipts do not qualify. ECS retains stopped-task metadata for a limited period; if it is no longer verifiable, rerun the bounded operation with services stopped and save a fresh receipt. Runtime independently checks journal authority as well. ECS readiness/rollback then protects rollout. Successful service stabilization still requires the acceptance probes below.

Record actual QA evidence only after reviewing the underlying results. Its payload has `schema_version: "1.0.0"`, `purpose: "qa-release-approval"`, `environment: "qa"`, the source QA `account`, `region`, `release_id`, exact `image_digest`, `qa_release_sha256` (SHA-256 of the signed QA release file), and that release's `gate_provenance_sha256`. It also needs `status: "passed"`, UTC `executed_at`, `approved_at` and `expires_at`, an accountable `operator_ref`, and `passed_gates` containing `private_network`, `conditional_upload`, `worker_kill_matrix`, `deletion_restore`, `authenticated_export`, and `alarm_delivery`. `evidence_refs` maps every required probe name to its actual protected result reference. Times must satisfy execution ≤ approval ≤ now < expiry, with expiry no more than seven days after probe execution. Missing probes, expired approval or a different image/commit/environment/source envelope block promotion.

Sign that reviewed payload with the existing trusted release authority:

```bash
uv run --project services/api python deploy/platform.py approve-qa \
  --config infra/config/qa.local.json \
  --release deploy/releases/qa-REVIEWED_COMMIT.json \
  --gate-evidence deploy/receipts/gates-REVIEWED_COMMIT.json \
  --trusted-public-key /secure/otgd-release-public.pem \
  --signing-key /secure/otgd-release-private.pem \
  --qa-evidence deploy/receipts/qa-reviewed-probe-payload.json \
  --output deploy/receipts/qa-validation-signed.json
```

This operation signs an operator approval; it reports `checks_executed=false` and does not run or invent QA probes. Promotion verifies its Ed25519 signature under the independently trusted key. Production deployment, maintenance and activation require the same signed `--qa-evidence`, recheck its expiry and binding, and verify its exact envelope hash against the production release. A plain JSON `passed` file is insufficient. Keep the underlying private-network, IAM/KMS, worker interruption, restore and alarm evidence available for review.

## 6. Promote the exact QA image to production

Provision the production registry with its real inputs first. Set the production config's digest and commit to the tested QA values. `promote` copies the existing image, checks that its manifest digest did not change, and signs a production record binding the QA evidence hash. It does not rebuild the source. Supply `--source-profile` when the QA registry is accessed through a separate AWS profile/account.

```bash
uv run --project services/api python deploy/platform.py promote \
  --config infra/config/prod.local.json \
  --source-config infra/config/qa.local.json \
  --source-release deploy/releases/qa-REVIEWED_COMMIT.json \
  --trusted-public-key /secure/otgd-release-public.pem \
  --signing-key /secure/otgd-release-private.pem \
  --gate-evidence deploy/receipts/gates-REVIEWED_COMMIT.json \
  --qa-evidence deploy/receipts/qa-validation-signed.json \
  --output deploy/releases/prod-REVIEWED_COMMIT.json
```

Then use the same stopped deployment → bootstrap verification → migration/recovery → fresh admission verification → activation sequence for production, supplying the production signed release, `--gate-evidence` and `--qa-evidence` on each operation. Bootstrap creation is permitted only for its first empty journal. Production has no fictional issuer and rejects synthetic-cloud capture. Mobile signed builds must carry the actual production origin/issuer/client identity; they do not discover a local override at runtime.

## Rollback and disaster recovery

Use the detailed [runbooks](../infra/runbooks/OPERATIONS.md). Rollback chooses a previously signed, still-retained digest and a database-compatible release. This baseline supports schema 1 only; it never automatically downgrades a database. Stop services, deploy the prior digest stopped, run/verify its compatible migration, obtain a fresh independent admission receipt and activate using both. Do not recover health data from an older snapshot merely to undo an application release.

Database recovery is a separate process with a deletion-journal replay and fresh authentication cutoff. Optional `databaseSnapshotIdentifier` names a same-account/region RDS snapshot ARN and requires `recoveryRequired=true`. Preflight checks its source environment tag, original age, encryption key, engine/version and capacity. Recovery retains the replaced database for operator reconciliation; it does not drop the independent journal/key or shrink snapshot storage. Keep that snapshot identifier in subsequent configs until an explicitly reviewed infrastructure migration removes the restore-origin property; removing it casually can trigger another replacement.
