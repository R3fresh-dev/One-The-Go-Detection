# Replacement execution handoff — pending source freeze

This is a prepared handoff, not execution authorization for the verifier. The verifier has performed only immutable source/evidence reads and external artifact writes. PM owns resources, runtime mutation and the final gate launch. Candidate28 and checkpoint8 reports remain historical; no replacement aggregate is currently admitted here.

1. All writers release exact source/test/workflow/contract inputs. PM records the new committed revision, tree, canonical47 hashes and full source fingerprint. Preserve original stable782cases/411requirement occurrences. Rebind OTGD020 canonical ENV003 after D009v6; accepted community default requires no token, explicit licensed preset requires its authorized token. Preserve candidate28 hashes as history.
2. Inventory author supplements by actual path/hash; determine affected cases from changed source/shared DTO/fixtures, not only changed test symbols. Freeze source before measurement. Preserve focused RED/GREEN logs as development evidence; do not convert their counts to final PASS. Preparation100ms inclusive is engineering consistency only.
3. PM verifies current source-equivalent local image proof before serial app-runtime adoption. D006v7 compressed archive hash differs from uncompressed rootfs DiffID; preserve every prior archive/data volume/journal. No native/runtime/hardware/scientific admission follows image proof. Require current COPY binding and source after; imageE is invalidated history. Verifier does no Docker, service, protected setting, installation or cleanup action.
4. Use existing protected disposable PostgreSQL test database and authorized canonical fictional local runtime. Never redirect destructive fixture schema setup at canonical retained application DB. Keep runtime-role privilege checks real. The shared runner inherits private test credentials; do not put values in reports or command logs. Preserve local browser ledger on retries. Caches remain `/tmp/otgd-uv-cache`, `/tmp/otgd-npm-cache`, Playwright `/tmp/otgd-playwright`.

From repository root, after PM prepares the required private disposable-test environment, the exact combined local entry point is:

```sh
python scripts/run_all_gates.py
```

The frozen runner must still execute every mandatory gate, without skips, filtering or reduced coverage:

```sh
python scripts/ci_gate.py unit-coverage
python scripts/ci_gate.py atdd
python scripts/ci_gate.py performance
python scripts/ci_gate.py components
python scripts/ci_gate.py live-dependencies
python scripts/ci_gate.py docker-health
python scripts/ci_gate.py localstack-api
```

These commands are the pinned source command interface, not commands executed by this verifier. Re-read frozen replacement scripts/workflows for changed mandatory checks. `run_all_gates.py` requires unchanged HEAD/full fingerprint before and after; every stage output is retained. No partial runner receipt is a complete PASS. Current old combined run stopped intentionally before PostgreSQL; old worker drift-preflight failed; old candidate28 LocalStack CI canceled; none can be silently reused.

Mandatory evidence includes raw `reports/{unit,postgres,atdd,hosted-preview,components,authenticated-live}.xml`, coverage inventories/JSON/XML and mobile source coverage, seven gate logs plus `local-gates.json`, `performance.json` (40workflows/20fictional identities/400writes, all successful, p95<1000ms,p99<2000ms,resultdeadline15s), freshUUID worker-interruption JSON with source-before/after/complete matrix/DLQ checks and raw process logs, actual versioned S3/SQS/bootstrap/raw/participant probes, and authenticated ordinary browser receipts/logs at both viewports. Record paths actually emitted by current frozen scripts; missing, empty, failed, skipped or interrupted evidence fails admission.

Remote CI must run the exact replacement committed source through aggregate `.github/workflows/merge-gate.yml` and its reusable platform/native/hosted-preview workflows. Require **all14mandatory jobs** to pass; canceled/skipped jobs fail aggregate. Retain API run/head/merge/tree/jobs metadata, raw logs, artifact IDs/ZIP SHA/digest checks and extracted XML/HTML/logs. If testing a merge commit, verify the tested tree equals or explicitly binds the reviewed candidate; do not infer identity from branch names.

Separate native/firmware evidence remains mandatory: portable C++ protocol/signed-grant/vendor executables, actual Nano ESP32 synthetic/signedreader compiles, protected security-enabled ESP-IDF branch, Kotlin core/optical tests plus both APK builds, actual macOS Swift golden tests with XML checked against raw XCTest log, full iOS simulator compilation, both guarded fictional preview packaging jobs and current config/provenance inspection. Local Swift/Kotlin source presence is NOT_RUN until actual appropriate toolchain evidence. CI compiled binaries do not demonstrate installed OS/UI/Keychain/SQLCipher/permission/radio/camera/VoiceOver/TalkBack, physical calibration or sensor safety.

After actual replacement artifacts exist, independently reconcile each affected stable case using its complete GIVEN/WHEN/THEN, exact test assertions/helper bodies, real fixture/double boundary and raw named execution. A related-symbol hit or aggregate PASS cannot prove an unasserted clause. Sound composition of existing meaningful assertions is permitted; do not add redundant tests merely to restate implementation. Preserve PARTIAL/NOT_RUN/BLOCKED and exact unproved clause/prerequisite type. Require fresh six independent reviews with per-spec current hash decisions; reviewers cannot approve their own corrections. A fresh final approver may act only after actual prerequisites, never simulated. No merge, deployment, participant use or scientific/clinical/driving claim is authorized by this handoff.
