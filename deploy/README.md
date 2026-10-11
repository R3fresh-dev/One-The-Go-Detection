# Deploy and promote a reviewed release

The CLI [platform.py](platform.py) makes every paid or operational action explicit. No AWS deployment has been performed in this workspace. It uses the normal AWS SDK credential chain, validates the account with STS, and passes database credentials through ECS secret references. Its defaults do not invent an AWS account, domain, alarm recipient, signing key or monthly budget.

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

A normal full preflight expects the configured image digest already in ECR. Registry/bootstrap and build commands use the earlier phase that does not require that image yet. The CLI checks the ACM certificate, RDS minor/class and optional public hosted zone. Exact RDS minor `16.14` in the template is a candidate, not a promise of availability.

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

Eligible runs belong to `R3fresh-dev/One-The-Go-Detection`, use the active `.github/workflows/merge-gate.yml`, and test the exact release commit through `push` on `main` or the actual `merge_group` commit targeting `main`. PR-only, manual, fork, older direct platform/native workflows, skipped jobs and an earlier successful attempt do not qualify. Required job names are `unit-coverage`, `atdd`, `components`, `merge-gate`, `platform / contracts-and-synthesis`, `platform / postgres-integration`, `platform / localstack-integration`, `native / shared-and-firmware`, `native / android`, and `native / ios`. The new aggregate workflow must actually execute before it can produce qualifying evidence; expected nested names must be confirmed against that run. The verifier fails closed if they differ.

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

Set `activateServices=true` in the reviewed QA config and activate:

```bash
uv run --project services/api python deploy/platform.py activate \
  --config infra/config/qa.local.json \
  --release deploy/releases/qa-REVIEWED_COMMIT.json \
  --gate-evidence deploy/receipts/gates-REVIEWED_COMMIT.json \
  --trusted-public-key /secure/otgd-release-public.pem \
  --output deploy/receipts/qa-migration.json
```

Activation re-verifies the signed release and checks the exact deployed maintenance task-definition ARN, cluster, start marker, single migration container, immutable image and successful exit. Receipts bind account, region and release revision. The complete migration or restore command must match, including the recovery timestamp and quiescence flag; an unused module/script argument does not qualify. Unexpected environment, role and resource overrides are rejected. Snapshot recovery timestamps must match the actual selected recovery point. A local JSON file alone is insufficient evidence. ECS retains stopped-task metadata for a limited period; if it is no longer verifiable, rerun the bounded migration with services stopped and save a fresh receipt. ECS readiness/rollback then protects rollout. Successful service stabilization still requires the acceptance probes below.

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

Then use the same stopped deployment → bootstrap verification → migration → activation sequence for production, supplying the production signed release, `--gate-evidence` and `--qa-evidence` on each operation. Bootstrap creation is permitted only for its first empty journal. Production has no fictional issuer and rejects synthetic-cloud capture. Mobile signed builds must carry the actual production origin/issuer/client identity; they do not discover a local override at runtime.

## Rollback and disaster recovery

Use the detailed [runbooks](../infra/runbooks/OPERATIONS.md). Rollback chooses a previously signed, still-retained digest and a database-compatible release. This baseline supports schema 1 only; it never automatically downgrades a database. Stop services, deploy the prior digest stopped, run/verify its compatible migration and activate from a fresh receipt. Do not recover health data from an older snapshot merely to undo an application release.

Database recovery is a separate process with a deletion-journal replay and fresh authentication cutoff. Optional `databaseSnapshotIdentifier` names a same-account/region RDS snapshot ARN and requires `recoveryRequired=true`. Preflight checks its source environment tag, original age, encryption key, engine/version and capacity. Recovery retains the replaced database for operator reconciliation; it does not drop the independent journal/key or shrink snapshot storage. Keep that snapshot identifier in subsequent configs until an explicitly reviewed infrastructure migration removes the restore-origin property; removing it casually can trigger another replacement.
