# Worker interruption probe implementation and execution record

Owner: `/root/worker_builder`; Factory run `otgd-20261025-0555`, branch `factory/one-the-go-detection-20261025`. Builder evidence only; no self-signoff, application-completion, merge, deployment, participant-use or scientific qualification decision. PM owns all commits, pushes, runtime setup, source freeze and independent review. Correction round 0 / 2; recovery attempts 0 / 3, unchanged.

## Decisions and scope

Acknowledged through actual PM messages before edits: D-001 v1 AFFECTED; D-002 v1 AFFECTED; D-003 v1 AFFECTED; D-004 v1 NOT_AFFECTED (product-document ownership); D-005 v1 AFFECTED; D-006 v3 AFFECTED. Read repository `AGENTS.md`, pinned Factory `4770878e18e9c587c2961b9e2bb13315da31abe9`, decisions, implementation Task 5, engineering ENG-009 and verification V-SW-005. Applied executing-plans, test-driven-development and verification-before-completion practices to the assigned implementation. Parent's explicit sole-PM ownership supersedes skill defaults about worker commits or additional agents.

Assigned implementation: real process interruption evidence for the fenced worker, using separate explicitly disposable PostgreSQL and LocalStack resources. Preserve canonical services, all existing databases/volumes/journals/identity anchors, measurement default, fictional provenance, and independent research/scientific boundaries. No production worker changes were made. `scripts/ci_gate.py`, `.github/workflows/platform.yml`, and `docs/CI_GATES.md` remain PM integration ownership.

PM additionally assigned `infra/local/worker_interrupt_gate.py` and its focused tests so local and CI use the same invocation. This removes a manual host PostgreSQL forwarding prerequisite for the canonical command. The wrapper runs in an existing one-off migration image; it creates a fresh named database, unique runtime role, dedicated source/DLQ, and three uniquely named buckets. It never adopts, resets or drops existing resources.

## Deliverables and frozen source identity

Source files released to PM at approximately 2026-10-25 06:50 UTC:

| File | SHA-256 |
|---|---|
| `infra/local/worker_interrupt_probe.py` | `17f19c89fb376416aec5379cf7181822082171863e5f202cba7b90cd972d98cc` |
| `infra/local/worker_interrupt_gate.py` | `fd0ec8fccbe344df436775bdcaf484534eb236025c2c0e63e6ffdc7e730223b1` |
| `infra/test/test_worker_interrupt_probe.py` | `9498d5bd7939252f80d1c72edc44df49d6b9a74dddd67285f7da1960b1f828a2` |
| `infra/test/test_worker_interrupt_gate.py` | `1b2c06ea82e1654138b35f037894f00d405b1648b59c4e3729a9850e2874f277` |

The live JSON independently captures before/after hashes for the probe, wrapper, every executed `otgd/**/*.py` source file and contract JSON file. Source drift fails the matrix. This is a scoped source identity; concurrent unrelated authors' workspace edits are not asserted unchanged.

## Safety and instrumentation

The low-level CLI requires `--confirm-fictional-workspace`, `OTGD_DISPOSABLE_DATABASE=true`, local mode, a 16-hex uniquely owned namespace, PostgreSQL database `otgd_worker_probe_<suffix>`, exact namespace buckets and queue paths, local endpoints, and unchanged 120-second visibility. A marker installed only during empty-fixture setup binds database/resources; normal execution additionally requires no fixture accounts and empty source queue. Setup verifies an entirely empty DB and absence of every fixture bucket/queue before provisioning. It does not invoke the canonical bootstrap, which hardcodes canonical queue names.

The canonical wrapper requires the caller's `--project-name otgd-local` plus exact canonical migration connection/service configuration, checks the actual PostgreSQL database/user, proves the fresh DB and runtime-role names absent, and creates only the new database. Existing migration code establishes its own journal/key bindings and provisions its restricted runtime role. Before executing workers the wrapper switches credentials and verifies no superuser/CREATEDB/CREATEROLE/replication privilege, no schema CREATE privilege, and no UPDATE privilege on protected authority tables. The wrapper does not independently inspect Docker labels from inside its container; PM's explicit Compose command selects the project. Ephemeral fixture signing material lives in that one-off container's private `/tmp`.

Spawned children execute actual `worker.main()`, `dispatch_once()`, `consume()`, `run_job()`, SQL claims/finalizations, S3 versioned writes/reads/cleanup and SQS operations. Wrappers pause immediately around real operations, emitting PID/job/fence/generation/version and one-way receipt fingerprints through a pipe. No mocks replace live I/O; no production timeout or clock is patched. Signals target only the `multiprocessing.Process` PID created and tracked by that invocation. Every observed barrier/signal is persisted before continuing.

## Acceptance matrix implemented

| Case | Actual evidence and asserted boundary |
|---|---|
| Export before claim | SIGKILL after receiving a real delivery, before `claim_job`; production visibility elapses; replacement processes same stable job/outbox. |
| Export after claim | SIGKILL after real committed claim; replacement waits genuine lease/visibility, increments fence and completes once. |
| Export after object write | SIGKILL after actual non-null S3 VersionId; replacement cannot adopt unverified fence-one bytes and commits its own pinned output. |
| Export after DB commit | SIGKILL after real commit; redelivery returns terminal without changing output or completion timestamp. |
| Export before SQS delete | SIGKILL immediately before actual acknowledgement; terminal redelivery preserves same output/completion. |
| Result after claim / after commit | Real synthetic snapshot, context/attempt/manifest digest lineage and evidence validation; actual Check+Job atomic commit, measurement-only result; terminal redelivery retains the same committed result. |
| SIGTERM | Signal a paused real claim, release work, observe successful acknowledgement and clean process exit within 30 seconds. This is the observed small-work stop window, not a proof of arbitrary long-task shutdown. |
| Stale late writer | SIGSTOP entire child, including heartbeat, before real S3 write; replacement wins a newer genuine fence; SIGCONT permits late write, stale commit must return `lease_lost` and preserve winner. |
| Retired generation during downtime | Real transaction increments account generation and marks deleting while stopped; replacement refuses retired export; late original write cannot publish. This tests worker generation authority, not the HTTP deletion request/journal lifecycle. |
| Late output cleanup | Wait for the job's actual initial expiry without modifying clocks/leases/expiry; run real recurring cleanup; all owned versions/markers vanish while an unrelated neighboring job key stays readable by exact version. No immediate orphan deletion claim is made. |
| Logical failed-claim budget | Persist a deliberately malformed fictional export body; execute the actual exporter exception path five times with real 2/4/8/16-second waits; assert failure at five and refusal of another claim. No synthetic SDK exception is injected. |
| Queue DLQ budget | A unique malformed fictional SQS delivery is actually received five times at unchanged 120-second visibility; verify the same MessageId/body reaches the configured DLQ. Do not change visibility or delete that message to accelerate the test. |

The JSON explicitly excludes raw-export-specific authority revocation, the full 900-second processing deadline, the HTTP privacy deletion lifecycle, cloud semantics, native-device evidence and scientific qualification. Related existing tests remain separate evidence. These exclusions do not grant per-spec signoff or erase outstanding acceptance requirements.

## Checks actually executed

From repository root, before live source release:

```sh
UV_CACHE_DIR=/tmp/otgd-uv-cache uv run --project services/api python -m unittest infra/test/test_worker_interrupt_probe.py infra/test/test_worker_interrupt_gate.py
UV_CACHE_DIR=/tmp/otgd-uv-cache uv run --project services/api ruff check infra/local/worker_interrupt_probe.py infra/local/worker_interrupt_gate.py infra/test/test_worker_interrupt_probe.py infra/test/test_worker_interrupt_gate.py
git diff --check
```

Observed: focused unit suite **7 / 7 passed**, approximately 0.213 seconds; Ruff passed; diff whitespace check passed. Unit checks cover rejected broad/remote targets, exact namespace/project/configuration guards, PID/stage/job protocol validation, real owned child blocking/release, receipt redaction, and synthetic digest/provenance lineage. They do **not** establish live worker recovery. RED observations were missing probe/wrapper modules and missing `result_fixture`, then GREEN with implementation.

An initially authorized broad infrastructure command was started at approximately 06:46 UTC:

```sh
UV_CACHE_DIR=/tmp/otgd-uv-cache uv run --project services/api python scripts/ci_gate.py infra-unit > /tmp/otgd-worker-infra-unit.log 2>&1
```

PM subsequently prohibited running the broad gate because its Fargate container setup builds images under a tight disk budget. The already-running owned Python PID 48986 was immediately interrupted with SIGINT; observed command exit **130**. Partial log retained at `/tmp/otgd-worker-infra-unit.log`; it contains a Fargate-container `setUpClass ERROR` and is **not** a passing or completed gate. No retry was made. Last measured root capacity remained approximately 2.4 GiB free. PM coordinates any required full infra-unit rerun. This was a PM stop instruction, not an approval denial or a confirmed recovery event.

## Live run in progress

PM launched the approved canonical wrapper at approximately **2026-10-25 06:51 UTC**, session **95815**. Durable evidence: `reports/worker-interrupt-preflight-20261025T0654.json`; the filename timestamp is a label, not the observed start time. Fresh fixture namespace **`otgd-worker-probe-eec5896e4274c6a7`**, database **`otgd_worker_probe_eec5896e4274c6a7`**, and corresponding restricted runtime role were successfully prepared by the wrapper. First actual `before_claim` SIGKILL against recorded child PID 13 is persisted. Status at this report's initial write: **RUNNING**, no acceptance PASS claimed.

The independently PM-prepared manual fixture `otgd-worker-probe-202610250555abcd` / database `otgd_worker_probe_202610250555abcd` remains preserved and unused by the canonical wrapper. No retained canonical database, queue, bucket or journal was reset.

## Exact canonical local / CI invocation and proposed integration

PM owns integration. The same Compose command must be invoked from the local aggregate gate and the platform workflow. Source mounts ensure the running worker/probe use current checkout Python rather than an older image snapshot. Use a fresh output basename per invocation; the wrapper refuses overwriting prior evidence.

```sh
docker compose --project-name otgd-local --env-file infra/local/.env -f infra/local/compose.yml run --rm --no-deps \
  -v "$PWD/infra/local:/app/infra/local:ro" \
  -v "$PWD/services/api/otgd:/app/services/api/otgd:ro" \
  -v "$PWD/reports:/app/reports" \
  migrate uv run --no-sync python /app/infra/local/worker_interrupt_gate.py \
  --confirm-fictional-workspace --project-name otgd-local \
  --output /app/reports/worker-interrupt-UNIQUE_RUN_ID.json
```

Recommended `scripts/ci_gate.py` patch: import `uuid4` from `uuid`; in `localstack-api`, after the existing participant probe, call:

```python
probe_report = 'worker-interrupt-' + uuid4().hex + '.json'
call('docker', 'compose', '--project-name', 'otgd-local', '--env-file', 'infra/local/.env',
     '-f', 'infra/local/compose.yml', 'run', '--rm', '--no-deps',
     '-v', str(ROOT / 'infra/local') + ':/app/infra/local:ro',
     '-v', str(ROOT / 'services/api/otgd') + ':/app/services/api/otgd:ro',
     '-v', str(REPORTS) + ':/app/reports',
     'migrate', 'uv', 'run', '--no-sync', 'python', '/app/infra/local/worker_interrupt_gate.py',
     '--confirm-fictional-workspace', '--project-name', 'otgd-local',
     '--output', '/app/reports/' + probe_report, local_compose=True)
```

Recommended platform workflow changes: invoke that same command, or the same canonical `localstack-api` gate containing it, after readiness; allow at least **50 minutes** for the localstack integration job; retain `reports/worker-interrupt-*.json` on success/failure with the other test artifacts. Update the final evidence-limit copy so it reports which local crash scenarios actually ran and keeps raw-authority/deadline/cloud/native/scientific limits explicit. Do not call the probe twice in the same job by adding both an aggregate invocation and a separate step.

Recommended `docs/CI_GATES.md` entry: document the canonical command, approximately 29-minute production-timing matrix, explicit local-only disposable ownership, restricted role, preserved fixtures and output, source-drift checks, report glob and bounded failure semantics. Never list skipped/blocked live execution as passing.

## Remaining gates and blockers

At initial report write the live matrix is pending completion. Full canonical gate integration, required broad infrastructure tests, exact-candidate aggregate checks, coverage >80%, independent per-spec council reviews and PM freeze/commit/push remain outside this builder's completed evidence. No action was auto-review denied; no external deployment, merge or participant operation was attempted. Any live failure must be reconciled against its retained fixture and evidence before editing/retrying; existing fixtures must never be reset to manufacture a PASS.
