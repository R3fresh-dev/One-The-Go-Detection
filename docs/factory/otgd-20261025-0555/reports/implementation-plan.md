# Approved software completion implementation plan

> **For agentic workers:** Use the Factory PM's assigned OpenAI builders and `superpowers:executing-plans` task by task; ownership remains PM-controlled. This document is an author handoff, not permission to deploy, merge, publish, operate participants or self-sign off.

**Goal:** Repair ENG-004 and close the bounded software acceptance gaps ENG-005–011 / V-SW-001–008 without adding capabilities or weakening assertions.

**Architecture:** Retain the shared Expo application, existing native boundaries, FastAPI/PostgreSQL service and fenced S3/SQS worker. Add focused assertions and actual-process/browser probes around their real interfaces. Keep unavailable instrument/OS/scientific inputs explicitly separate from executable software.

**Tech stack:** TypeScript/React Native/Expo 57.0.27, React 19.2.3, Playwright 1.64.0, Python/FastAPI/pytest, PostgreSQL 16, pinned LocalStack S3/SQS; native Swift/Kotlin and protected reader firmware only at their existing scope.

**Spec:** [reconciled register](../../../../specs/FULL_SPECIFICATION.md), [shared contracts](../../../../openspec/changes/production-mobile-platform/shared-contracts.md), [platform contract](../../../../openspec/changes/production-mobile-platform/platform-contract.md), [engineering findings](engineering-audit.md), [verification plan](verification-plan.md). Stable canonical IDs and current hashes: [inventory](../inventory.json).

## Global constraints

- Measurement mode remains default; legacy 0.1.0 research estimates remain unsupported. Only independently admitted ResearchResult 1.1.0 and explicitly scoped HR-only software can execute conditionally.
- Fictional fixture provenance, current owner/study/consent/model/configuration/retention/generation controls and independent scientific authority remain mandatory. Software fixtures grant no human authority.
- Future alcohol remains a separate calibrated fuel-cell breath channel in mg/L; no generic gas sensor, invented blow duration, new vendor driver, BAC conversion, automatic score averaging or driving/legal clearance.
- Raw record/upload default off; separate export purpose and exact source versions; whole archive at most 50 MiB uncompressed / 64 MiB ZIP, with lower grant limits honored.
- Preserve existing containers, volumes, journals, identity anchors and unrelated records. No cleanup, migration, restart or Docker mutation is authorized by this plan while D-005/D-006 v2 hold remains; PM must release runtime execution after reviewing image proof.
- Independent Python and mobile unit inventories must be strictly greater than 80%; required skips fail. Every mandatory local category and every actual mandatory aggregate/reusable-workflow job requires exact-source evidence (currently 14 jobs). Keep historical counts/results historical.
- Ordinary shared web supports authenticated accounts with memory-only local storage. Isolated `dist-preview` remains account/network/native-disabled. Native SQLCipher/OS evidence and physical/scientific qualification remain independent.
- Correction round 0, recovery attempts 0 at handoff. Authors do not sign their own work; PM owns freeze, commit/push and review routing.

## Review focus

1. Expiry between discovery, grant and actual start must reject at the layer with current calibration evidence; never invoke absent hardware (Task 3).
2. Self-authored external references/extra approval flags must not turn internal consistency into independent approval (Task 2).
3. Stale OS status promises after navigation/account changes must not publish or request permission (Task 4).
4. Worker crash after object write or database commit must preserve redelivery, fence stale effects and remove only owned late outputs (Task 5).
5. Browser reload/reauthentication and lost acknowledgments must preserve server ownership/intent without implying native cache persistence (Task 6).

## Task 1: truthful alcohol copy and rendered no-clearance evidence

**Findings/specs:** ENG-004/007; V-SW-003; OTGD-019 AND-ALC-002/003/005/006; conditional OTGD-006/007. No breath capture implementation.

**Files:** Modify `apps/mobile/src/ui/manage.tsx::AlcoholScreen`; extend `apps/mobile/e2e/components.spec.ts` or `raw-recordings.spec.ts` using the existing esbuild fixture pattern; create `apps/mobile/e2e/fixtures/alcohol-component.tsx` if controlled account/result variants cannot be reached through the existing fixture. Extend `apps/mobile/tests/measurement-format.test.ts` only for actual formatting boundaries not already asserted. Inspect `src/ui/checks.tsx`, `core/historyView.ts` and existing result/detail renderers before binding surface assertions.

**Interfaces:** Keep `AlcoholScreen({controller,model}:ScreenProps)`, actual `CheckRecord` alcohol companion and verified research result unchanged. Fixture controls only inputs to actual components, never substitutes a fake result renderer. Use existing backend research fixture for admitted-scope display; do not create authority by setting a Boolean.

- [ ] Add `alcohol copy remains accurate for measurement and admitted research contexts`: render ordinary/guest and verified research contexts; demonstrate the stale unconditional `No classification exists` failure.
- [ ] Add `alcohol qualifiers never confer clearance`: render quantified zero, low quantified, `below_loq`, `not_detected`, invalid and simulated records in each actual result/history/detail alcohol surface. Assert mg/L, qualifier/source/acquisition time, null nonquantified magnitude, unavailable hardware and separate channel meaning; reject positive safe-to-drive/legal-clearance/combined-score claims while accepting truthful `clearance: unavailable` text.
- [ ] Replace the stale effect fact with bounded truthful copy, for example `No automatic combined classification; research co-use requires model-specific authority`. Preserve qualified breath instrument unavailable, blood conversion unavailable and deliberate demo behavior.
- [ ] Run from `apps/mobile`: `npm run typecheck`; `CI=1 npm run export:web`; `CI=1 npm run test:e2e -- e2e/components.spec.ts e2e/raw-recordings.spec.ts`. New fixture assertions belong in one of these gate-selected files so they execute in local/Actions component gates.
- [ ] Record test name/assertion/fixture source bindings and red/green result; deliver only owned files to PM for a focused commit and independent review.

## Task 2: precise evaluation-history and authenticity negatives

**Finding/specs:** ENG-005 / V-SW-001; OTGD-008 EVAL-007; OTGD-041/042 HR restriction. Existing `test_real_logistic_fitting_is_train_only_deterministic_and_engine_compatible` already asserts `external_assertions.verified_by_tool is False`; retain it.

**Files:** Extend `services/api/tests/test_model_evaluation.py` and `test_model_evaluation_cardiac.py`; change `tools/model_evaluation.py` only if a new meaningful assertion exposes an actual defect. Retain runtime self-approval refusal tests in `test_model_admission.py`/`test_operator_governance.py`.

**Interfaces:** Actual `cohort_index(dataset)`, `freeze(index,plan)`, `train(dataset,plan,split,trained_at,pipeline_locked_at=None)`, `evaluate(dataset,plan,split,artifacts,training,evaluated_at) -> (report,evidence)`, and `main(argv)` verify path. Use existing full and HR-only fixture builders; exact original values/hashes must be recorded before execution.

- [ ] Add `test_external_history_references_remain_unverified_through_pipeline` in both modes: use distinct unmistakably fictional/unverified authorization, plan-lock, endpoint-evidence and HR source-bundle references. Exercise freeze/train/evaluate/verify; compare exact preserved external refs, original dataset/analysis/split/training/report/artifact and row-accounting hashes.
- [ ] Assert `verified_by_tool`, `historical_lock_or_blinding_proven`, `authority_granted`, `clinical_success_claimed`, freeze `historical_lock_proven` and HR custody `signatures_registry_release_and_independent_review_authenticated` remain false wherever their output contract emits them. Do not require nonexistent fields or invent a new verifier.
- [ ] Add `test_self_asserted_or_extra_approval_fields_do_not_authenticate_history`: extra flags in strict typed inputs refuse; tampered untyped receipts/evidence either refuse deterministic verification or cannot change authority. `endpoint.independently_assessed=true` remains a required assertion rather than verified independence. Run the existing runtime self-approval denial cases separately.
- [ ] Run from root: `UV_CACHE_DIR=/tmp/otgd-uv-cache uv run --project services/api pytest services/api/tests/test_model_evaluation.py services/api/tests/test_model_evaluation_cardiac.py services/api/tests/test_model_admission.py -q`. Require executed non-skipped cases and original-reference equality; record failures before fixes and final actual counts.
- [ ] PM reviews the focused diff and commits the bounded assertion improvement; no genuine dataset/study approval or predictive performance is claimed.

## Task 3: alcohol dependency expiry and absent-adapter refusal

**Finding/specs:** ENG-006 / V-SW-002; OTGD-019 AND-ALC-001/004. There is no qualified alcohol adapter; a positive real breath start is blocked by that missing input, not supplied by this task.

**Files:** Extend `services/api/tests/test_operator_governance.py` using `governance_fixture.py` and `apps/mobile/tests/acquisition.test.ts`. Inspect existing `otgd/operator_governance.py::active_body/check_dependencies`, `core/acquisition.ts::configurationsFor/configurationFor/verifyCaptureGrant/verifyCaptureStart`, and controller start paths. Modify these production functions only if direct assertions fail; no new driver file.

**Interfaces:** Current typed `Channel='alcohol'`, `modality='breath_alcohol'`, `raw_unit='mg/L'`, independently scoped device/calibration/configuration records. Server expiry `expires_at <= now()` refuses; client current configuration requires `Date.parse(expires_at) > Date.now()`. Use actual owned fixture context and existing HTTP start/grant routes, with calls to the existing adapter boundary counted.

- [ ] Add direct before/equal/after expiry cases for both configuration and its calibration dependency; retain distinct calibration-expiry evidence at the authoritative layer. The before-expiry case proves dependency validity only, not instrument availability.
- [ ] Add calibration-expiry-between-grant-and-start and stale cached-capability cases: expired start rejected, hardware call count zero, no accepted concentration. Assert current source inventory still reports the missing alcohol adapter; hypothetical mechanics remain explicitly labeled contract fixtures.
- [ ] Check participant-facing recovery honestly identifies recalibration when that reason is available. Do not replace a true absent-adapter reason with a fabricated calibration diagnosis. If production loses a real calibration reason, make the smallest propagation correction with its regression assertion.
- [ ] Run root: `UV_CACHE_DIR=/tmp/otgd-uv-cache uv run --project services/api pytest services/api/tests/test_operator_governance.py -q`; mobile: `node --import tsx --test tests/acquisition.test.ts`. Later run actual PostgreSQL suite with disposable test database via C-PG.
- [ ] Record unexecuted real-instrument recalibration journey separately; PM accepts only bounded software evidence and routes review.

## Task 4: denied-camera Settings and no-reprompt component assertions

**Finding/specs:** ENG-008 / V-SW-004; OTGD-036 AND-SET-003; related native row remains Task 7.

**Files:** Extend `apps/mobile/e2e/raw-recordings.spec.ts` and create `e2e/fixtures/permissions-component.tsx` using its existing actual-component/esbuild pattern; extend test-only native-web shim/aliases only as needed. `src/ui/manage.tsx::PermissionsCard` is currently private; exercise through exported Settings screen or export the unchanged card for controlled testing only if necessary. Keep any production behavioral correction within that file. Do not let global shim changes alter guest/account suites.

**Interfaces:** Actual `getCameraPermissionStatus`, `Camera.getCameraPermissionsAsync`, `getBluetoothPermissionStatus`, `getEnrolledLevelAsync`, `AppState.addEventListener('change',...)`, `Linking.openSettings`; observe actual labels/actions. Adapter spies provide controlled OS observations, not real OS evidence.

- [ ] Render denied/canAskAgain, denied/cannotAskAgain, restricted, undetermined and status-read failure; assert exact recovery labels and permission-request count zero on mount, manual refresh and OS active return.
- [ ] Assert Settings opens once only after explicit action; change denied to granted on active return and assert current status. Resolve requests out of order and after unmount; assert stale values never publish. Back preserves the actual draft and does not prompt.
- [ ] Run `npm run typecheck` then `CI=1 npm run test:e2e -- e2e/raw-recordings.spec.ts` from mobile after ordinary export. A failing existing card race gets the smallest correction before rerun.
- [ ] Record controlled adapter limits; leave Android/iOS actual settings round trips pending Task 7. PM commits and requests independent review.

## Task 5: actual worker process-interruption matrix

**Finding/specs:** ENG-009 / V-SW-005; shared platform §§6/10; OTGD-010/016/018/022/029/031 and result jobs. **Prepared implementation may proceed; execution is blocked until PM confirms runtime capacity and preserved-state launch strategy.**

**Files:** Create `infra/local/worker_interrupt_probe.py`; add protocol/fixture safety assertions in new `infra/test/test_worker_interrupt_probe.py`; extend `scripts/ci_gate.py` localstack-api path and `.github/workflows/platform.yml` to run the same probe after canonical services are ready. Modify `services/api/otgd/worker.py` only if a required actual failure is demonstrated; deterministic instrumentation belongs in the child probe wrapper, not a production bypass/shortened timeout. Update `docs/CI_GATES.md` with exact executable command and preserved-state boundaries.

**Interfaces:** Actual `claim_job(job_id)`, `execute_claim(claim)`, `commit_output(claim,output)`, `run_job(job_id,receipt,...)`, `dispatch_once`, `consume` and `storage.client('sqs').delete_message`. Child wrapper delegates all I/O and decisions to real implementations and emits only bounded stage acknowledgments over a parent pipe. A pause wrapper may block immediately before/after a real call; it cannot replace DB/S3/SQS with mocks or falsify authority/time.

- [ ] Probe validates `--confirm-fictional-workspace`, local endpoints and a unique owned fixture namespace; refuse nonlocal, broad target or missing scope. Because current `dispatch_once()`/`cleanup_once()` scan database work globally, use an explicitly disposable separate PostgreSQL test database, dedicated source/DLQ queues and dedicated namespaced test buckets under the existing local services with canonical visibility/redrive/object limits. PM must first prepare that isolated fixture schema/resources using approved test setup; never migrate or clear the retained application database. Run actual dispatcher/consumer/cleanup against the isolated target only, with its own fictional journal authority/configuration; canonical consumers must not consume fixture messages. Preserve retained journal anchors and all existing records.
- [ ] Parent starts one owned standalone worker child; await deterministic pipe barrier before claim, after real claim, after actual object write, after real DB commit, and before actual SQS delete. SIGKILL only that recorded child PID; run SIGTERM stop-window evidence separately. Retain PID, stage, job/outbox/fence/generation/object VersionId and redacted queue receipts.
- [ ] Start replacement child for same identity; observe actual visibility/lease expiry/redelivery with production constants. Assert exactly one committed result, no lost durable outbox, no premature queue deletion and valid version-pinned output. Exercise stale late write/commit after fence change, revocation/deletion during downtime, owned late-output cleanup and retry/DLQ budget. Keep expected deadline failures explicit; never reset queues/data to manufacture PASS.
- [ ] Proposed new command after implementation, from root: `UV_CACHE_DIR=/tmp/otgd-uv-cache uv run --project services/api python infra/local/worker_interrupt_probe.py --confirm-fictional-workspace`. It needs the approved isolated disposable test database and dedicated fixture queue/bucket/journal configuration described above, with real local service endpoints; do not print/copy secrets. PM may choose existing maintenance-container execution with the same script when capacity allows, recording the exact command used. The new harness must document its actual CLI and launch/ownership checks before execution.
- [ ] Add the real probe to `python scripts/ci_gate.py localstack-api` and the matching platform workflow; unit checks only validate probe targeting/barriers, not worker recovery. Run `uv run --project services/api python scripts/ci_gate.py infra-unit` for probe tooling, then actual live gate. Runtime shortage leaves this acceptance BLOCKED with prepared command/log, never mock PASS. PM owns launch permission and commit.

## Task 6: authenticated ordinary-web/live-stack ATDD

**Finding/specs:** ENG-010 / V-SW-006; OTGD-014 WEB-DEP-003/008 plus identity/save/history/export/privacy refinements. **Execute after PM restores canonical API/identity/worker capacity.**

**Files:** Create `apps/mobile/e2e/authenticated-live.spec.ts` and `playwright.live.config.ts`; create `infra/local/browser_fixture.py` only for bounded namespaced fictional setup based on existing participant-probe authority patterns; extend `scripts/ci_gate.py`, `.github/workflows/platform.yml` and `apps/mobile/e2e/README.md`/`docs/CI_GATES.md` so the same live browser command runs locally/CI. Keep existing guest and hosted-preview configs intact. Modify auth/routing/controller/service code only for a demonstrated failure.

**Interfaces:** Actual `services/auth.ts::authorize` web origin callback/PKCE, `controller.ts` notice/profile/context/save/upload/history/export/delete/signOut paths, actual API contracts, issuer on configured origin (canonical local 8081), API (8000), shared ordinary export (8082), real PostgreSQL/S3/SQS/worker. Register the exact browser callback; no `page.route().fulfill`, API abort or replacement auth token stands in for this suite's core transport. Fixture setup can create explicitly fictional governed records, never genuine participant approval; do not require native sensors or native task for the browser journey.

- [ ] Launch ordinary `dist` with hosted preview false; assert account entry is available and `dist-preview` is not served. Browser completes actual issuer PKCE sign-in and separate notice/profile/context, then owned measurement-only save followed by explicit Upload; wait for actual queued result.
- [ ] Observe actual result/history and exact-scope structured export download. Open real archive and verify hashes/selected IDs/provenance; exercise deletion/receipt/logout. Raw positive selection, reference-lab pending work or admitted research result use separately labeled fictional authorities where their canonical cases require it; no fake scientific approval. Observe receipts from the server/worker.
- [ ] Add lost HTTP response (drop acknowledgment after actual server acceptance, not substitute success), reload/reauthentication, foreign ownership, revoked refresh family, withdrawn consent/retired generation and pending recovery cases. Assert memory-only reload clears browser cache and requires truthful reauthentication/server history retrieval; no native encrypted persistence claim.
- [ ] Live config selects only `authenticated-live.spec.ts`, phone/desktop viewports, no retries, and explicit live-prerequisite failure. Ordinary guest config must ignore this file so isolated atdd does not accidentally require live services; live suite is mandatory in localstack-api and matching CI once supplied. Capture actual origins, viewport, network destinations, artifact SHA and redacted receipts without tokens/health payload logs.
- [ ] Proposed new commands after files exist: mobile `CI=1 npm run export:web`; `CI=1 npx playwright test --config=playwright.live.config.ts`; root `python scripts/ci_gate.py localstack-api`. If fixture setup is needed, proposed root `uv run --project services/api python infra/local/browser_fixture.py --confirm-fictional-workspace` must supply bounded read-only fixture locators through protected test inputs; finalize actual CLI and its safety tests before execution.
- [ ] Keep `python scripts/ci_gate.py atdd` and `components` passing independently. PM records true current evidence and commits; physical native acceptance remains open.

## Task 7: actual native execution, separate from qualification

**Finding/specs:** ENG-011 / V-SW-007; shared §9 and each applicable Android/iOS scenario. No speculative native feature or new sensing driver.

**Files:** Existing native-build workflow, `apps/mobile/modules/scripts/{verify_android_preview.py,build_ios.py}`, module Kotlin/Swift tests and current `verification-plan.md` command appendix; write actual per-platform evidence into PM-assigned dossier/results paths. Do not change build pins or pass criteria merely to accommodate missing tools.

**Interfaces:** Installed real native app and OS camera/BLE/settings/key storage/unlock/touch/lifecycle callbacks, exact source-bound build identity. Emulator/simulator execution verifies OS integration only; physical sensing/timing/geometry/electrical qualification requires independent real-world evidence.

- [ ] PM secures Android SDK36/JDK17/emulators and supported physical handset; actual macOS/Xcode26.4+ with minimum/current iOS simulators and physical iPhone. Execute C-ANDROID/C-IOS commands already reproduced in verification plan; preserve actual build/golden artifacts and inspect identities.
- [ ] Execute Android minimum/current emulator and physical handset, iOS minimum/current simulator and physical iPhone at standard/200% text, TalkBack/VoiceOver: offline restart/process kill, denied unlock/key loss, camera/BLE denial/settings return, native touch/cancel/background, account/generation races and draft recovery. Bind each applicable canonical scenario to observed result.
- [ ] Missing tool/device rows remain BLOCKED with exact target/prerequisite. Linux parse/typecheck, fake native adapters and compiled binaries cannot close those rows. Physical G-04/G-05/G-06/G-11 and genuine study/vendor/model/operator evidence remain independently open even after all software rows pass.

## Task 8: source freeze, every-case binding and independent gates

**Finding/specs:** V-SW-008 and AGENTS; all OTGD-001–047, all 11 pending changes. Owner PM + verifier, then independent domain/product/engineering reviewers and fresh approver.

**Files:** Inventory and every canonical dossier, `docs/CI_GATES.md`, committed workflow/provenance contracts; source `deploy/provenance.py` has `REQUIRED_JOBS` (historical base 13) and `FARGATE_REQUIRED_JOBS` (14). Inspect actual release callers and tests before assuming one set covers every target. No deploy/store execution is authorized.

- [ ] Map each canonical scenario/PRD criterion to actual assertions; distinguish matching test symbol from sufficient acceptance. Refresh current hashes after all builders stop; preserve stable IDs and original scientific gates.
- [ ] Check admission against every actual mandatory job in committed aggregate/reusable workflows, including Fargate container-runtime verification. Add a meaningful provenance regression for a missing/failed new mandatory job if any release caller could admit stale base-only evidence; fix only demonstrated source gap, preserve historical recorded proof shapes as history. Report any target-specific authority ambiguity to PM rather than weakening required jobs.
- [ ] Freeze all nonignored source/docs/tests/contracts before final gate fingerprint; include this report and task edits in the frozen candidate. Run exact commands in verification plan: C-SPEC, C-SCHEMA, C-CDK, C-FW/C-SECURE/C-ANDROID/C-IOS, all seven C-ALL categories and matching required Actions jobs; no required skips, Python/mobile coverage each strictly >80%.
- [ ] Record actual commands/UTC/environment/revision/full manifest/exit codes/reports. Recheck runtime/source binding after any change. Unit/structural results do not close live, native, physical, scientific, AWS or store rows.
- [ ] Obtain all four independent domain reviews plus per-spec product and engineering signoffs on the same candidate with decisions acknowledged; authors do not sign themselves. PM consolidates at most two correction rounds; fresh independent approver only after prerequisites. Commit/push dedicated work branch within user authorization; no merge/deploy/participant-use.

## Handoff state

All checkboxes above are planned, not executed by this reconciler. Task 1 contains the observed production defect; Tasks 2–4 close focused missing direct assertions unless they expose a bug. Tasks 5–6 add genuine transport/process evidence and stay execution-blocked while runtime capacity is held. Task 7 software execution prerequisites are distinct from scientific qualification and are not silently deferred. No driver is required from unspecified future instruments. PM can dispatch nonoverlapping tasks after accepting this concrete ownership handoff; shared `manage.tsx`, gate/workflow and test fixture edits must be sequenced.
