# Android feature: application readiness and environment

Normative integration: [shared application contracts](../../shared-contracts.md) and [platform contracts](../../platform-contract.md). These define the exact cross-feature DTOs, error states, generation/revocation rules, current-release limits, and implementation evidence.

## Purpose and traceability

Make startup, service availability, supported versions, and environment identity predictable for customers and operators. This feature carries the platform acceptance contract behind the Android startup/status experience, with iOS parity. Upstream: PRD-025; OPS-001/006; SEC-004/006/007; DOC-001–003; HLD §§4/7/8; LLD §§9–12; user requirement for LocalStack, AWS QA, and AWS prod.

## Customer experience

On launch the app opens its encrypted local store, resolves the build's fixed environment, checks locally supported contract versions, and requests public app configuration when online. A minimal launch screen cannot remain indefinitely: after the configured request timeout, the app either opens permitted local functionality with an offline notice or presents a specific storage/version/configuration error.

Local and QA builds display persistent **Development** or **QA** identification. The production app has no environment picker. Settings → **About** shows app/build number, platform, environment, supported contract version, device-integration version, and a sanitized support code. **Service status** distinguishes offline connectivity, backend maintenance, and unsupported app version. A production build must never show a local demo's fictional cloud response as a real service response.

During maintenance, saved local records remain readable after unlock and the app can perform only operations permitted by its current configuration. New uploads pause. An unsupported minimum version displays **Update required for synchronization** and preserves data; it never attempts an incompatible upload. The app does not delete the local database because a configuration request failed. Optical, assay, ECG, and clinical-model availability remain separate capability states.

## Engineering and environment contract

Environment values local/qa/prod/test are build/deployment inputs. Android package IDs and iOS bundle IDs differ by environment. API URL, OAuth issuer/client, callback allowlist, and feature-contract versions are immutable in a release build. GET /v1/app-config returns environment, app version range, contract versions, maintenance flag, notice version/hash/content route, and capability summaries. Notice content, generation/revocation, companion evidence, and authenticated export delivery follow the shared contracts. The platform contract freezes queue leases, quotas, pinned object versions, deletion-journal recovery, and operational budgets. Private membership/capability data comes only from authenticated endpoints.

Local Compose includes API, worker, real PostgreSQL, LocalStack S3/SQS, and isolated signed development identity. The LocalStack image/version is pinned and its required activation token comes from an ignored environment file; no token is committed. Missing Docker/token is a reported prerequisite, not silently replaced while claiming LocalStack validation. Startup hooks idempotently create only the local buckets/queues. The same API/worker images run in AWS with actual AWS endpoints and task-role credentials.

QA/prod infrastructure uses separate environment identity/data, ALB TLS, private ECS tasks/RDS, Secrets Manager, private encrypted S3, encrypted SQS/DLQ, CloudWatch logs/alarms, managed database backups, and a bounded outbox/worker retry policy. Production capacity includes at least two API tasks across AZs and Multi-AZ RDS. QA retains security controls at lower capacity. Cloud deployments reject local-auth mode, emulator endpoints, wildcard CORS, placeholder credentials, and missing required TLS/identity configuration.

Operational engineering targets: API availability objective 99.9% monthly excluding declared maintenance; metadata API p95 under 500 ms at an explicitly recorded load; restore RPO ≤24 hours and RTO ≤4 hours as initial objectives requiring measured drills. These are proposed engineering targets, not achieved metrics. Observe request rate/error/latency, unhealthy targets, database connection pressure, outbox age, oldest SQS message, retries/DLQ depth, and privacy-job age. Logs contain safe request/job IDs and error codes, not tokens, raw measurements, images, or direct identity.

Deploy migrations separately, promote immutable tested image digests, wait for health checks, and retain the prior task definition for rollback. A failed migration/rollout blocks promotion. Backup restore requires an isolated drill and replay of a watermarked deletion journal stored independently of the database backup before service access; absent journal continuity fails closed. Platform signing, real AWS deployment, physical device testing, and operational drills are evidence tasks; source files or synthesized templates are not evidence they were executed.

## ADDED Requirements

### Requirement: AND-ENV-001 Fix environment identity in each build
Release builds SHALL pin environment, application identity, API/issuer/callback configuration, and contract versions; production SHALL offer no runtime environment editor.

#### Scenario: QA and production are installed together
- **GIVEN** separate configured builds
- **WHEN** both run on one phone
- **THEN** they have distinct app identities and local namespaces and QA is visibly labeled.

#### Scenario: Cloud service receives local-only configuration
- **GIVEN** APP_ENV=prod
- **WHEN** local authentication or an emulator endpoint is configured
- **THEN** startup fails before accepting requests.

### Requirement: AND-ENV-002 Bound startup and preserve local data
App startup SHALL time out network readiness checks and SHALL preserve existing encrypted data through offline, maintenance, and upgrade-required states.

#### Scenario: Phone launches offline
- **GIVEN** a usable encrypted store
- **WHEN** the configuration request times out
- **THEN** permitted local functions open with an offline state and no fabricated server result.

#### Scenario: Store cannot be decrypted
- **GIVEN** a missing or invalid local key
- **WHEN** startup opens storage
- **THEN** the app reports a storage recovery/reset choice and does not fall back to plaintext storage.

### Requirement: AND-ENV-003 Provide a reproducible LocalStack path
The repository SHALL provide pinned local services, initialization, health checks, environment examples, and integration commands using actual LocalStack S3/SQS and PostgreSQL.

#### Scenario: Local prerequisites are present
- **GIVEN** Docker and an authorized LocalStack activation token
- **WHEN** the documented local startup command runs
- **THEN** resources initialize idempotently and a synthetic session reaches a persisted result through the API/worker path.

#### Scenario: LocalStack prerequisite is absent
- **GIVEN** no Docker daemon or activation token
- **WHEN** local integration is requested
- **THEN** the command fails with a clear prerequisite message and no test report calls a mock execution LocalStack validation.

### Requirement: AND-ENV-004 Keep cloud isolation and secrets explicit
QA/prod infrastructure SHALL define private data/service networks, TLS, encrypted resources, scoped roles, secret injection, and separate environment identity/data boundaries.

#### Scenario: Synthesized production stack
- **GIVEN** complete deployment inputs
- **WHEN** infrastructure is synthesized and checked
- **THEN** required encryption, private database/task placement, TLS listener, production capacity, and scoped resource access appear in the template.

#### Scenario: Secret is omitted
- **GIVEN** a required database or identity setting is unavailable
- **WHEN** the service starts
- **THEN** readiness fails without logging the secret or accepting unauthenticated fallback traffic.

### Requirement: AND-ENV-005 Promote immutable verified releases
Deployments SHALL use immutable image digests, a separately executed migration step, health-based rollout, and a recorded rollback target.

#### Scenario: QA release passes its checks
- **GIVEN** a tested image digest and compatible schema
- **WHEN** promoted to production
- **THEN** production references that digest and records the migration/release evidence.

#### Scenario: Migration fails
- **GIVEN** a nonzero migration exit
- **WHEN** deployment automation evaluates the gate
- **THEN** service rollout stops and the previous deployment remains the rollback target.

### Requirement: AND-ENV-006 Implement observable recovery boundaries
The system SHALL expose liveness/readiness separately, safe operational metrics/logs, queue/DLQ monitoring, backup configuration, and documented restore/tombstone procedures.

#### Scenario: Database is unavailable
- **GIVEN** a live API process without a usable database
- **WHEN** health is checked
- **THEN** liveness may pass while readiness returns 503 and traffic is not represented as healthy.

#### Scenario: Backup contains subsequently deleted data
- **GIVEN** a restore from an older backup
- **WHEN** the restore runbook is executed
- **THEN** deletion tombstones are reapplied before access is reopened and the drill records whether RPO/RTO objectives were achieved.

### Requirement: AND-ENV-007 Report verification honestly
Release evidence SHALL distinguish implementation, automated verification, and external deployment/device/signing evidence and MUST NOT mark unexecuted checks as passing.

#### Scenario: iOS source exists on a Linux runner
- **GIVEN** no Xcode/macOS build toolchain
- **WHEN** delivery status is generated
- **THEN** iOS native compilation is recorded as unexecuted rather than inferred from a JavaScript bundle.

#### Scenario: Infrastructure synthesis succeeds without AWS credentials
- **GIVEN** a synthesized template but no deployment
- **WHEN** the release report is written
- **THEN** it states synthesis passed and QA/prod deployment remains unexecuted.
