# Infrastructure verification record

Checked **2026-10-11** in the repository workspace. No AWS stack, external account, notification subscription, purchase or native application binary was created by this infrastructure work.

## Executed here

| Check | Evidence |
|---|---|
| Locked infrastructure dependency installation | `npm install --ignore-scripts`; committed `package-lock.json`. |
| TypeScript compiler and CDK assertions | `npm run verify` in `infra`; QA/prod network, storage, queue, identity, IAM, budget, encryption and stopped-first-deployment assertions. 5 tests passed, including snapshot recovery with retained dependencies and inherited storage size. |
| Recovery, operational metrics and signed-release unit tests | `uv run --project services/api python -m unittest discover -s infra/test -p 'test_*.py' -v`: 10 tests passed. SQLite tests cover deterministic barrier/reconciliation and cleanup-alarm logic; they are not PostgreSQL lock tests. |
| Targeted backend implementation review | 4 tests in `services/api/tests/test_interleavings.py` passed for cached-account/job races, terminal outbox starvation and artifact cleanup/completion. SQLite and SQS/S3 test doubles were used. Findings and source resolutions: [IMPLEMENTATION_REVIEW.md](IMPLEMENTATION_REVIEW.md). |
| Python syntax, Compose/workflow source, local links | Compiled all owned Python scripts; parsed Compose and the three-job workflow; checked fixed callbacks, CA digest and documentation targets. No runtime integration inferred. |
| OCI metadata resolution | Official registry manifests for Python, PostgreSQL and LocalStack; pinned immutable indexes/architecture digests in `images.lock.json`. Images were not pulled. |
| GitHub Action commit resolution | Official GitHub tag API for checkout/setup-node/setup-uv/upload-artifact; exact commit SHAs recorded in workflow. |
| AWS cost sources | Official current regional AWS price lists, saved selected SKUs/rates and primary NAT example; six scenarios calculated in `costs/us-east-2-estimate.json`. |
| RDS trust bundle | Official AWS global CA bundle downloaded over HTTPS; source, size and SHA-256 in `certs/manifest.json`. It is public trust material, not a credential. |

## Unexecuted in this workspace

| Gate | Reason / supplied executable path |
|---|---|
| Docker service image build and Compose startup | Docker is unavailable here. `scripts/local-platform.py up` builds real services. |
| Actual LocalStack bootstrap/idempotence/conditional S3/SQS | Requires Docker and an appropriate LocalStack token. `check`, repeated `resource-init`, and the manually requested workflow job execute it. A missing token fails the requested gate. |
| Actual fictional OAuth → API → SQS worker → authenticated export → deletion | `check-app --confirm-fictional-workspace` is supplied for a disposable local project; it has not run here. |
| Actual PostgreSQL API/role/migration tests | Workflow provides a pinned PostgreSQL 16 service, API tests and `infra/test/postgres_roles.py`. The latter verifies two migrations, protected role permissions and the 72-character subject-key storage requirement. |
| AWS CDK deployment / network / IAM / KMS / Cognito | Actual account, credentials, issued domain certificate, operator/destination and positive budget are not supplied. Synthesis is not deployment evidence. |
| ECS failure matrix, DLQ replay, late uploads, RDS failover, old-snapshot journal replay | Requires the deployed QA environment and fault injection. Operator runbooks and maintenance scripts define the tests. |
| Verified database TLS against RDS | Public CA bundle and verify-full configuration supplied; no RDS endpoint exists here. |
| Alarm delivery / incident ownership | Alarm resources require the actual destination, subscription confirmation, delivery probe and staffed operator. |
| Android/iOS builds, phones and hardware channels | Owned by the mobile/native workstreams. This record makes no claim that platform source tests compile or validate native apps. |
| Clinical interpretation or intoxication prediction | No executable qualified model or preapproved human measurement configuration exists. |

## Release gates

The CI workflow separates source/synthesis, actual PostgreSQL, and requested actual LocalStack evidence. A green source job alone cannot satisfy production promotion. A production release requires the exact signed QA image plus actual `private_network`, `conditional_upload`, `worker_kill_matrix`, `deletion_restore`, `authenticated_export` and `alarm_delivery` evidence. The promotion record binds the QA evidence hash and exact digest; the operator controls its signing key.

The deployment helper refuses placeholders/zero budgets, mutable image tags, unsupported or missing regional input, missing trusted release signature, active services during maintenance, unverified maintenance tasks and missing recovery evidence. Database recovery continues to block readiness on missing/unreadable/inconsistent journal evidence and suspends restored scope authority. These are implemented gates with source/unit evidence; actual cloud failure drills remain unexecuted.
