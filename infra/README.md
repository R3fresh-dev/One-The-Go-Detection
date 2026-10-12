# Reproducible local, QA and production platform

This directory implements the reviewed [platform contract](../openspec/changes/production-mobile-platform/platform-contract.md). It supplies real PostgreSQL, S3/SQS emulation through LocalStack, a fictional local OAuth issuer, and AWS CDK infrastructure. **The release has no qualified human configuration and no executable cannabis-intoxication model.** Infrastructure readiness does not establish measurement validity or intoxication detection.

Start with [verification status](VERIFICATION.md), [environment settings](ENVIRONMENT.md), [deployment instructions](../deploy/README.md), [operator runbooks](runbooks/OPERATIONS.md) and the [dated AWS estimate](costs/README.md).

## Start the local backend

You need Docker Engine/Desktop with Compose v2, Python 3.12 and `uv` 0.13.0. The default local/CI emulator is the digest-pinned **LocalStack 4.14.0 Apache-2.0 community release**, published February 26, 2026. It needs no LocalStack subscription or authentication token. This is an explicit version choice, and its actual S3/SQS behavior is tested; it does not imply support for services outside this application's contract. [Versioned upstream license](https://github.com/localstack/localstack/blob/v4.14.0/LICENSE.txt)

Run from the repository root:

```bash
uv sync --project services/api --locked
python scripts/local-platform.py prepare --host localhost
python scripts/local-platform.py up
python scripts/check-canonical-health.py
python scripts/local-platform.py check
```

`prepare` creates protected local secrets once. Never commit its generated settings or signing key. The helper does not print credentials. Existing settings and database volumes are preserved when you repeat preparation or startup.

To select the pinned **licensed 2026.09.1** alternative, supply an authorized `LOCALSTACK_AUTH_TOKEN` securely and add `--licensed-localstack` to every lifecycle/health command. The explicit override is [compose.localstack-licensed.yml](local/compose.localstack-licensed.yml); it refuses a missing token. A workstation uses an appropriate Developer Token; automated CI uses a workspace CI Auth Token. Current commercial subscriptions are Base/Ultimate/Enterprise; Hobby is for noncommercial use, and OSS sponsorship requires vendor approval. No account, subscription or sponsorship has been created for this repository. [Official authentication](https://docs.localstack.cloud/aws/getting-started/auth-token/), [plans](https://docs.localstack.cloud/aws/licensing/).

Changing emulator versions can change persisted-state compatibility. Use a separate disposable Compose project for testing an alternative, or review and perform the vendor-supported migration first. Startup never resets existing volumes to hide a version or migration failure.

The community preset adds **zero LocalStack license fees** to the development budget; Docker compute and CI runner usage still cost according to their providers. The licensed alternative is optional for this S3/SQS test scope and requires its own current vendor quote/entitlement. Neither emulator substitutes for AWS IAM/KMS/network or recovery qualification.

Use the community preset for **disposable fictional CI and UI workspaces**. Durable S3/SQS state across emulator shutdown is unqualified: the inspected community runtime has no persistence module, and merely setting `PERSISTENCE=1` does not supply that feature. Official snapshot persistence is included in the vendor's Base/Ultimate plans; the licensed override explicitly enables it. Even that preset needs an actual restart/recovery test before using durable local research data. [Official persistence requirements](https://docs.localstack.cloud/aws/capabilities/state-management/persistence/)

The local initializer and API now bind the marker's exact version/digest to retained PostgreSQL and refuse a missing/replaced journal. Existing pre-binding databases require a separately reviewed administrator receipt import; they cannot silently adopt a fresh marker. This closes the software reseeding gap, while durable emulator restart/recovery remains unqualified. Preserve failed volumes for review and use a separate disposable fictional project; resetting volumes does not repair lost evidence. See [journal continuity and upgrade details](../docs/JOURNAL_CONTINUITY.md).

Choose the correct origin **before** signing in: `localhost` for the iOS simulator, `10.0.2.2` for an Android emulator, or the computer's LAN IP plus `--lan` for a physical phone. See the full [routing table](ENVIRONMENT.md#local-phone-routing). Configure the matching mobile local build with that API origin. Do not edit a signed S3 URL to make it reachable.

Local endpoints are the API on port 8000, fictional sign-in on 8081, and LocalStack on 4566. PostgreSQL is internal. The API configuration endpoint is `/v1/app-config`; readiness is `/health/ready`. The fictional issuer exposes named Account A and Account B so ownership, switching and synchronization can be tested with synthetic data.

To run the full fictional application flow in a disposable workspace:

```bash
python scripts/local-platform.py check-app --confirm-fictional-workspace
```

That flow performs actual PKCE sign-in, session/evidence HTTP writes, stable finalize retries, SQS-backed asynchronous processing, authenticated ZIP export with independently checked member hashes, unauthenticated/cross-account/range denial and all-data deletion. It verifies retired-generation writes remain denied and logout revokes only the current token family while preserving its retry receipt. Privacy probes honor the actual server `Retry-After` within a bounded 15-second window, preserving the same intent and payload; performance writes do not retry throttling. It erases **Fictional Account A's local workspace**. It does not invoke the worker directly. The lighter `check` transport probe creates and removes only its own synthetic object and isolated SQS queue.

Useful operations:

```bash
python scripts/local-platform.py status
python scripts/local-platform.py logs
python scripts/local-platform.py down
```

`down` preserves PostgreSQL and disk volumes, while the community emulator's in-memory S3/SQS state can be lost. Retained disk volumes alone do not prove journal or artifact continuity. `reset --confirm-local-data-loss` explicitly deletes only the named local project's volumes. Do not use it to resolve a failed migration or to hide missing data.

## What startup does

Compose builds the locked API image, starts PostgreSQL and LocalStack, and waits for health. The resource initializer creates three private versioned buckets and source/dead-letter queues. The migration task creates the schema and a separate DML application role. Then the local issuer, API and worker start. A repeated bootstrap verifies the same resource settings and preserves logical identity; it does not silently create a fresh database.

`check-canonical-health.py` requires **all five long-running services** (`postgres`, `localstack`, `identity`, `api`, `worker`) to be running with Docker health `healthy`, and **both one-shot jobs** (`resource-init`, `migrate`) to have exited successfully with code zero. Missing healthchecks, incomplete jobs, duplicate service containers and a different Compose project fail the check. It reads only filtered container state, excluding environment values and health logs. A worker healthcheck verifies recent monotonic success from the dispatcher, cleanup and both SQS consumers, bound to the live process start identity. Dependency failures invalidate the affected channel immediately; a live but stalled process fails after 75 seconds. This verifies operational progress, while the separate application flow establishes actual job completion.

SQS uses path URLs with the internal `localstack:4566` hostname. Its visibility is 120 seconds, source retention four days, dead-letter retention 14 days and redrive limit five. The worker uses PostgreSQL leases/fencing in addition to SQS visibility. LocalStack message retention is explicitly enabled. [LocalStack SQS URL and retention documentation](https://docs.localstack.cloud/aws/services/sqs/)

The pinned image indexes, exact source tags, architecture digests and retrieval date are recorded in [images.lock.json](images.lock.json). The Python base, PostgreSQL and both LocalStack presets are referenced by SHA-256 digest, and Python/Node dependencies have lockfiles. Report actual Docker/application execution separately for the exact tested revision.

Managed cloud environments with an HTTPS inspection proxy may build with `docker build --secret id=proxy_ca,src=/path/to/combined-ca-bundle -f infra/local/service.Dockerfile -t otgd-api:local .`, then start the already-built image with Compose `up --no-build --detach --wait`. The optional BuildKit CA is mounted only for pip/uv dependency installation, never copied into an image. Ordinary CI uses its standard CA trust; certificate verification stays enabled.

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

The [platform workflow](../.github/workflows/platform.yml) runs TypeScript/synthesis checks and API tests against an actual disposable PostgreSQL 16 service. The mandatory merge gate also builds Compose, requires every service/initializer health outcome, repeats resource initialization, and runs actual transport and fictional application flows. The explicit licensed preset additionally requires its CI token; missing prerequisites fail instead of skipping the gate. These suites do not substitute for QA AWS IAM/KMS/private networking, failure injection, recovery or native device checks. Record those results by release digest before production promotion.
