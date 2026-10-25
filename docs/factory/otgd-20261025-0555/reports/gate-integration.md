# Shared live gate integration — implementer handoff

Run: `otgd-20261025-0555`; builder: `/root/gate_integration`; recorded 2026-10-25 UTC. Factory source pin `4770878e18e9c587c2961b9e2bb13315da31abe9`. ACK D-001 v1–D-005 v1 and D-006 v3; AFFECTED Tasks 5/6/8. Correction/recovery counters unchanged at 0/2 and 0/3. PM alone owns git, runtime execution, freeze and review routing.

## Changed behavior

Owned outputs only: `scripts/ci_gate.py`, `.github/workflows/platform.yml`, `infra/test/test_ci_gates.py`, `docs/CI_GATES.md`, and this report.

`python scripts/ci_gate.py localstack-api` now requires the existing API probes followed by the actual worker interruption wrapper and authenticated ordinary-web acceptance. The platform workflow invokes that same command, retains repeat bootstrap, Docker health and performance, retains its four platform jobs (14 aggregate mandatory jobs), and installs pinned Node 24.19.0, locked mobile dependencies and actual Playwright Chromium. Its budget is 50 minutes to accommodate the approximately 29-minute worker matrix without changing production timers.

The worker command uses canonical `otgd-local` one-off `migrate`, `--rm --no-deps`, read-only current `infra/local` and `services/api/otgd` binds, writable `reports`, explicit fictional confirmation/project, and a fresh `/app/reports/worker-interrupt-<uuid>.json`. Existing paths and symlinks refuse before command dispatch, while the wrapper independently exclusively creates the output before resource mutation. Missing/invalid/unfinished/failed/nonfictional reports fail. Both reported source manifests must equal the current host probe/wrapper, all `otgd` Python and all JSON contract hashes. No old report is adopted or removed.

The browser command first prepares the host private ledger (default `/tmp/otgd-browser-fixture.json`, optional `OTGD_BROWSER_FIXTURE`), then provisions through a separate `migrate` one-off with the two read-only source binds and only the exact ledger file writable at `/tmp/otgd-browser-fixture.json`. It preserves that ledger on retries. It exports ordinary `dist` with `CI=1 npm run export:web`, runs `CI=1 npm run test:e2e -- --config=playwright.live.config.ts --reporter=line,junit`, and requires fresh nonempty `reports/authenticated-live.xml` with every case passing. Existing fixture ownership/inventory admission remains authoritative. No bearer tokens are printed by the gate.

The existing `child_environment(local_compose=True)` behavior still removes a disposable parent `OTGD_TOMBSTONE_KEY`; real Compose dispatches retain that flag. Disposable PostgreSQL tests keep their explicitly supplied key. Protected journal/default-measurement/fictional scientific boundaries are unchanged.

## Executed verification

- RED: `python -m unittest infra.test.test_ci_gates -q` exited 1 after the new acceptance tests and before implementation: 12 tests, 11 missing-feature errors identifying absent worker/browser helpers and report admission. This was the expected unavailable integration API, not live dependency evidence.
- GREEN: the same focused command exited 0 after implementation: 12 tests, no failures/skips.
- Final: `python -m unittest infra.test.test_ci_gates -v` exited 0: 13 tests, no failures/skips. Coverage includes missing/failed/running/mismatched-source worker reports, immutable unique worker evidence paths, host-ledger-before-maintenance dispatch, exact-file mount isolation, missing/empty/failed/skipped browser reports, nested Python/contract inventory, both mandatory helpers being invoked by `localstack-api`, and retained environment isolation.
- `python -m py_compile scripts/ci_gate.py infra/test/test_ci_gates.py` exited 0.
- Host Python `yaml.safe_load` parsed `.github/workflows/platform.yml`; assertions confirmed four platform jobs, 50-minute localstack budget, and exactly one shared `localstack-api` step. Manual inspection confirmed repeat bootstrap, health, performance and pinned Node/Chromium prerequisites.

## Remaining verification and limits

Implementation and focused command/report validation are verified at the scope above. Actual live worker/browser transport acceptance is **unverified by this implementer**. Per PM direction, no Docker, live gate, aggregate gate or `infra-unit` execution was launched while the existing matrix runs under limited disk capacity. No runtime sources, wrapper, probe, contracts, volumes or journals were changed. No commits/pushes or external actions were performed.

Pending PM action: after the in-flight matrix and runtime/image prerequisite work, freeze the candidate, verify current issuer/browser principals and runtime sources, then run `python scripts/ci_gate.py localstack-api` plus the remaining exact-revision required local/Actions gates. Preserve the private ledger on retries and keep each worker UUID evidence report. Live command failure, timeout, missing prerequisites or skipped mandatory cases remains failure; focused unit dispatch checks cannot replace real process/browser execution. Native device, AWS, participant and scientific release qualification remain separate and open as applicable.

Review ownership is released to PM for these five paths. Independent review/signoff is not supplied by the implementer.
