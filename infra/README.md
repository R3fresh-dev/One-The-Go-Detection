# Reproducible local, QA and production platform

This directory implements the reviewed [platform contract](../openspec/changes/production-mobile-platform/platform-contract.md). It supplies real PostgreSQL, S3/SQS emulation through LocalStack, a fictional local OAuth issuer, and AWS CDK infrastructure. **The release has no qualified human configuration and no executable cannabis-intoxication model.** Infrastructure readiness does not establish measurement validity or intoxication detection.

Start with [verification status](VERIFICATION.md), [environment settings](ENVIRONMENT.md), [deployment instructions](../deploy/README.md), [operator runbooks](runbooks/OPERATIONS.md) and the [dated AWS estimate](costs/README.md).

## Start the local backend

You need Docker Engine/Desktop with Compose v2, Python 3.12, `uv` 0.13.0, and a valid LocalStack token. LocalStack's current image requires authentication; a CI environment needs its appropriate CI token. [Official LocalStack authentication](https://docs.localstack.cloud/aws/getting-started/auth-token/)

Run from the repository root:

```bash
uv sync --project services/api --locked
python scripts/local-platform.py prepare --host localhost
python scripts/local-platform.py up
python scripts/local-platform.py check
```

`prepare` creates protected local secrets once. Supply `LOCALSTACK_AUTH_TOKEN` through your environment before preparation, or edit only that field in the generated local settings file. Never commit the file. The helper does not print credentials. Existing settings and database volumes are preserved when you repeat preparation or startup.

Choose the correct origin **before** signing in: `localhost` for the iOS simulator, `10.0.2.2` for an Android emulator, or the computer's LAN IP plus `--lan` for a physical phone. See the full [routing table](ENVIRONMENT.md#local-phone-routing). Configure the matching mobile local build with that API origin. Do not edit a signed S3 URL to make it reachable.

Local endpoints are the API on port 8000, fictional sign-in on 8081, and LocalStack on 4566. PostgreSQL is internal. The API configuration endpoint is `/v1/app-config`; readiness is `/health/ready`. The fictional issuer exposes named Account A and Account B so ownership, switching and synchronization can be tested with synthetic data.

To run the full fictional application flow in a disposable workspace:

```bash
python scripts/local-platform.py check-app --confirm-fictional-workspace
```

That flow performs actual PKCE sign-in, session/evidence HTTP writes, SQS-backed asynchronous processing, authenticated ZIP export, cross-account denial and all-data deletion. It erases **Fictional Account A's local workspace**. It does not invoke the worker directly. The lighter `check` transport probe creates and removes only its own synthetic object and isolated SQS queue.

Useful operations:

```bash
python scripts/local-platform.py status
python scripts/local-platform.py logs
python scripts/local-platform.py down
```

`down` preserves data. `reset --confirm-local-data-loss` explicitly deletes only the named local project's volumes. Do not use it to resolve a failed migration or to hide missing data.

## What startup does

Compose builds the locked API image, starts PostgreSQL and authenticated LocalStack, and waits for health. The resource initializer creates three private versioned buckets and source/dead-letter queues. The migration task creates the schema and a separate DML application role. Then the local issuer, API and worker start. A repeated bootstrap verifies the same resource settings and preserves logical identity; it does not silently create a fresh database.

SQS uses path URLs with the internal `localstack:4566` hostname. Its visibility is 120 seconds, source retention four days, dead-letter retention 14 days and redrive limit five. The worker uses PostgreSQL leases/fencing in addition to SQS visibility. LocalStack message retention is explicitly enabled. [LocalStack SQS URL and retention documentation](https://docs.localstack.cloud/aws/services/sqs/)

The pinned image indexes, exact source tags, architecture digests and retrieval date are recorded in [images.lock.json](images.lock.json). The Python base, PostgreSQL and LocalStack are referenced by SHA-256 digest, and Python/Node dependencies have lockfiles. Image metadata was verified; the current workspace has not pulled or run the images.

## AWS layout

| Component | QA | Production |
|---|---|---|
| Availability zones | Two network zones; single-AZ database | Two zones; multi-AZ database |
| API | One 0.25-vCPU/0.5-GB task | Two 0.5-vCPU/1-GB tasks, scales to four |
| Worker | One 0.5-vCPU/1-GB task | One task, scales to two |
| Metrics publisher | Worker sidecar; one database connection | Same |
| PostgreSQL | `db.t4g.small`, 20–100 GB gp3 | `db.t4g.medium` Multi-AZ, 20–100 GB gp3 |
| Backups | Seven days | 35 days |
| Application logs | Seven days | 30 days |
| NAT gateways | One; cross-AZ egress is a stated compromise | One per zone |
| API ingress | HTTPS ALB, HTTP redirects | Same |
| Storage | Private, versioned, encrypted S3 | Same |
| Deletion journal | Independent KMS key and retained bucket | Same |

Tasks have no public IP and no direct inbound access; the ALB alone reaches the API. The database accepts only API, worker and maintenance security groups. S3 uses a gateway endpoint; image retrieval, secrets, logs, SQS and issuer calls use the declared private-egress/NAT route. Verified database TLS uses the checked-in public [AWS RDS CA bundle manifest](certs/manifest.json). [AWS RDS TLS guidance](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.SSL.html)

API uploads require a signed `If-None-Match: *`, exact length/type/checksum and encryption headers. Bucket policy enforces conditional creation for the API signer. Every accepted read uses a non-null S3 VersionId. Journal roles can append/read and cannot delete events; the worker alone can remove artifact/export versions. Restoring PostgreSQL never restores or replaces the independent journal bucket/key.

## Verify source and integration separately

```bash
npm ci --ignore-scripts --prefix infra
npm run verify --prefix infra
uv run --project services/api python -m unittest discover -s infra/test -p 'test_*.py' -v
```

The [platform workflow](../.github/workflows/platform.yml) runs TypeScript/synthesis checks and API tests against an actual disposable PostgreSQL 16 service. The separately requested LocalStack job fails explicitly if its CI token is missing. It builds Compose, repeats resource initialization, and runs actual transport and fictional application flows. Neither suite substitutes for QA AWS IAM/KMS/private networking, failure injection, recovery or native device checks. Record those results by release digest before production promotion.
