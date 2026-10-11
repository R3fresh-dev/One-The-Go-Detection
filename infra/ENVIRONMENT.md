# Platform environment contract

The local, QA and production builds use separate fixed configuration. An application must never rewrite a signed upload URL, accept a token from another issuer, or switch a production build to a development origin.

## Cloud deployment inputs

Copy [qa.example.json](config/qa.example.json) or [prod.example.json](config/prod.example.json) into an ignored `*.local.json` file. Every `REPLACE_…` value and the zero budget deliberately fails validation. Exact PostgreSQL minor `16.14` is a candidate; `preflight` checks regional availability and the selected instance class before deployment. Do not silently replace it with `latest`.

| Input | Meaning |
|---|---|
| `account`, `region` | Actual AWS account and region; default region is `us-east-2`. STS must agree. |
| `domain`, `certificateArn` | Public API domain and an issued ACM certificate in that account/region. |
| `hostedZoneId`, `hostedZoneName` | Optional pair for an existing public Route 53 zone. If omitted, the operator creates DNS to the output ALB. |
| `cognitoDomainPrefix` | Unique hosted sign-in prefix; CDK creates the pool and public client. |
| `oauthRedirectUris`, `oauthLogoutUris` | Exact native callbacks; register their scheme in the matching mobile environment. No wildcard or local cloud callback. |
| `imageDigest`, `releaseId` | Immutable ECR SHA-256 digest and reviewed Git commit, bound by a signed release record. |
| `monthlyBudgetUsd`, `alarmEmail` | Owner-chosen positive budget and actual operational destination. No recipient or spending limit is invented. |
| `ownerRole`, `costCenter` | Actual responsibility and billing tags. Activate the `deployment` cost-allocation tag so the budget can observe its resources. |
| `costEstimatePath` | Dated regional estimate relative to the `infra` working directory; at most 31 days old. |
| `databaseSnapshotIdentifier` | Recovery only: exact same-account/region RDS snapshot ARN. The previous database is retained and the snapshot storage size is inherited. |
| `activateServices` | Starts false; becomes true only after verified bootstrap/migration. Recovery additionally requires a successful restore receipt. |
| `recoveryRequired` | Set true before restoring a database and keep it true after recovery so readiness continues to require verified recovery state. |

## Service settings injected by CDK/Compose

| Setting | Source / rule |
|---|---|
| `OTGD_ENVIRONMENT` | Fixed `local`, `qa` or `prod`; `test` is used only by disposable tests. |
| `OTGD_DATABASE_HOST`, `PORT`, `NAME`, `USER` | RDS outputs or internal Compose database; production database is private. |
| `OTGD_DATABASE_PASSWORD` | Application secret at runtime; separate RDS migration credential in the maintenance task. |
| `OTGD_DATABASE_SSLMODE`, `OTGD_DATABASE_SSLROOTCERT` | Cloud uses `verify-full` and the packaged public AWS RDS CA bundle. Local PostgreSQL uses its private Compose network. |
| `OTGD_APP_DATABASE_USER`, `OTGD_APP_DATABASE_PASSWORD` | Maintenance only: create/rotate the DML application role. Runtime cannot write operator registry or recovery state. |
| `OTGD_DATABASE_URL` | Optional test/local tooling override. Never print it or place real passwords in shell arguments. |
| `OTGD_DATABASE_POOL_SIZE` | API 5, worker 3, metrics 1, migration 1, local issuer 2; SQLAlchemy overflow is zero. |
| `OTGD_ISSUER`, `CLIENT_ID`, `JWKS_URL` | Exact issuer/public client/JWKS. Local validation uses the internal JWKS route while the signed issuer is the phone-visible origin. |
| `OTGD_API_ORIGIN`, `IDENTITY_ORIGIN`, `OAUTH_REDIRECT_URIS` | Fixed public origins and JSON list of callbacks. |
| `OTGD_AWS_REGION` | Region of S3/SQS/Cognito. |
| `OTGD_AWS_ENDPOINT_URL` | Local-only internal `http://localstack:4566`; absent in cloud. |
| `OTGD_S3_PUBLIC_ENDPOINT_URL` | Local-only phone-visible endpoint for signing. Changing it invalidates old tickets; never rewrite their host. |
| `OTGD_ARTIFACT_BUCKET`, `EXPORT_BUCKET`, `JOURNAL_BUCKET` | Separate versioned private buckets. |
| `OTGD_STORAGE_KMS_KEY_ID`, `JOURNAL_KMS_KEY_ID` | Separate data and deletion-journal keys; cloud rejects missing/equal keys. |
| `OTGD_QUEUE_URL`, `DLQ_URL` | Actual provisioned URLs. No automatic in-process cloud-outage fallback. |
| `OTGD_TOMBSTONE_KEY`, `TOMBSTONE_KEY_ID` | Independent 256-bit hex secret and version identifier; preserve for the lifetime of its restore evidence. |
| `OTGD_USER_POOL_ID` | Cloud only; limits identity-removal permissions to the environment pool. |
| `OTGD_LOCAL_SIGNING_KEY_PATH` | Local-only protected RSA key mount. Never packaged into an image. |
| `OTGD_RECOVERY_REQUIRED` | Cloud recovery readiness gate. |

## Connection capacity

A production rollout can briefly run eight API tasks (40 connections), four worker tasks (12), four metrics sidecars (4), one migration (1), and a ten-connection operator reserve: **67**, below the reviewed **80** budget. Steady production is two API tasks plus one worker/sidecar. QA permits two API tasks during rollout, two worker/sidecar tasks, one migration and the same reserve: **29**, below **40**. Local issuer connections are additional local-only capacity. These are configured bounds; load and failover tests remain required before changing task counts or pools.

## Local phone routing

| Client | Prepare command / origin host |
|---|---|
| iOS simulator on the Docker host | `python scripts/local-platform.py prepare --host localhost` |
| Android emulator on the Docker host | `python scripts/local-platform.py prepare --host 10.0.2.2` |
| Physical phone on the same trusted LAN | `python scripts/local-platform.py prepare --host YOUR_COMPUTER_LAN_IP --lan` |

Use one host choice consistently for API, issuer and S3 before creating tokens or tickets. `prepare` preserves an existing settings file; edit its three documented origin values if changing clients, then recreate the local containers and sign in again. `--lan` explicitly publishes ports on all host interfaces; otherwise they remain loopback. Restrict LAN exposure with the host firewall. Production and QA require HTTPS and never inherit local cleartext exceptions.

The mobile callback is `otgd-local://oauth/callback`; local web development uses exactly `http://localhost:8082/`. Port 8081 belongs to the identity service. Preparation also registers `http://<selected-host>:8082/` for an explicitly selected LAN/emulator host; keep the exact web origin in `OTGD_LOCAL_OAUTH_REDIRECT_URIS` when changing routing. Cloud native callback and logout use `otgd-qa://oauth/callback` or `otgd-prod://oauth/callback` respectively.
