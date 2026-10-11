# Mobile implementation security and integrity review

Review date: **2026-10-11**. Scope: the implementation following reviewed specification checkpoint **47d8ecbfc871b5026f32d4f5f474908e9c0e1b14**, including subsequent working-tree corrections. This is a source and host-test review, not clinical validation or acceptance of physical device behavior.

The review concentrated on account and data-generation isolation, delayed asynchronous responses, authentication persistence, capture cancellation, terminal evidence, and privacy presentation. It also inspected the diagnostics allowlist and the native permission query interfaces. Each finding below records the original counterexample so a corrected implementation is not mistaken for proof that the problem never existed.

## Status meanings

- **Corrected; host evidence recorded:** the named source correction and relevant host regression are present. Platform integration requirements remain separate.
- **Corrected in source; integration evidence pending:** the relevant implementation was independently re-read, but the complete platform interaction was not executed.
- **Correction in progress:** the assigned owner is changing the implementation. This finding remains open until targeted re-review.

No finding is considered closed merely because a comment describes the intended behavior. Full Android/iOS builds, OS lifecycle behavior, physical Bluetooth, permission prompts, camera restrictions, and native presentation latency require their own observed evidence.

## Findings

### MOB-SEC-001 — Radio cleanup could delay native cancellation

**Severity:** High. **Status:** Corrected; host evidence recorded.

**Sources:** `src/controller.ts` — `stopActive`; `src/core/operationGuards.ts` — `RunStopGate`. Requirements: AND-TASK-006/007, AND-CHECK-006, shared immediate-stop and navigation contracts.

**Counterexample:** The user presses Back while the reaction task is active. A Bluetooth cleanup promise takes several seconds. Awaiting that promise before invoking the native view's cancel method allows stimuli and input admission to continue after the user's stop action.

**Required correction and current implementation:** Invoke `view.cancel(runId, reason)` synchronously at the start of the stop operation, before awaiting radio, storage, or navigation work. Concurrent Back, background, and explicit End requests share one run-scoped stop promise. The current controller issues native cancellation first; `RunStopGate` immediately invokes the operation and joins identical-run callers.

**Evidence:** `tests/lifecycle.test.ts`, test **“concurrent route/background stops issue native cancel immediately and wait for terminal persistence”**. The test verifies invocation ordering and a shared promise under delayed stop/persistence. Native UI-thread interruption and physical stimulus cessation remain unexecuted locally.

### MOB-SEC-002 — A cancellation timeout could discard the native terminal ledger

**Severity:** High. **Status:** Corrected; host evidence recorded.

**Sources:** `src/controller.ts` — `completeNativeTask`, `stopActive`; `src/core/operationGuards.ts` — `TerminalEvidenceGate`; `modules/reaction-task/types.ts`; Kotlin and Swift `ReactionTaskView` implementations; `src/ui/checks.tsx` — active task screen. Requirements: AND-TASK-001/005/007, AND-CHECK-005/006, immutable evidence contract.

**Counterexample:** Native cancellation ends a run, but JavaScript event delivery or the encrypted database write takes longer than a fixed 500 ms wait. Clearing `activeTask` after that wait unmounts the view and can discard the full terminal result. An already-ended native run then has only a fabricated partial interruption record in the app.

**Required correction and current implementation:** Each native view caches the immutable full terminal map before emitting completion. The cancellation acknowledgment returns that same result for the matching stopped or already-terminal run. The controller joins the event and acknowledgment by run ID and digest, persists once, and clears active state only after durable settlement. Conflicting terminal payloads are rejected. A storage failure remains retryable from the native cached receipt. The fixed-delay discard path is removed. The screen reports terminal-evidence failure and keeps an explicit retry action.

**Evidence:** `tests/lifecycle.test.ts`, tests **“native callback and cancellation receipt share one durable terminal write while persistence is delayed”** and **“failed terminal storage remains retryable using the native cached receipt”**. Native pure-core terminal latch/admission tests also passed. Complete bridge-to-database lifecycle behavior requires platform execution.

### MOB-SEC-003 — A late sign-in continuation could reactivate a canceled identity

**Severity:** High. **Status:** Corrected in source; integration evidence pending.

**Sources:** `src/controller.ts` — `signIn`, `activate`, `signOut`, `authenticationRequired`; `src/services/auth.ts` — authorization, commit, refresh; `src/core/operationGuards.ts` — `AuthorizationAttemptGuard`. Requirements: shared account/issuer/epoch isolation, OAuth callback identity, same-account reauthentication and stale-response refusal.

**Counterexample:** A login receives a code and awaits the capabilities response. Sign-out or a newer login invalidates the earlier operation. Without checks after each await, the old capabilities response can still commit credentials or reopen that account's database.

**Required correction and current implementation:** Bind the flow to its authentication attempt, auth generation, originating workspace epoch, and returned server account identity. Recheck after token/capability retrieval, credential persistence, device unlock, and workspace activation. Serialize workspace activation and close an opened database if its guard no longer holds. A reauthentication callback for a different account is rejected before the protected action.

**Evidence:** Source re-review confirmed the `liveFlow`, `awaitingLogin`, `signedIn`, and `activeAccount` guards and the guarded serialized `activate` operation. `tests/lifecycle.test.ts` verifies ten-minute PKCE expiry, one-use callback consumption, and invalidation on logout/new login. Those pure tests do not substitute for browser callback, keychain, and account-switch integration tests.

### MOB-SEC-004 — A new authorization grant could retain another account's refresh token

**Severity:** High. **Status:** Corrected; host evidence recorded.

**Sources:** `src/services/auth.ts` — token exchange; `src/core/serializedVault.ts` — `refreshTokenForGrant`. Requirements: shared OAuth account binding and no identity fallback across accounts.

**Counterexample:** Account A has a refresh token. Account B's authorization-code response omits `refresh_token`. Falling back to A's previously stored refresh token pairs B's current access token with A's future refresh credentials.

**Required correction and current implementation:** Only a refresh-token grant may retain the captured refresh token from that same session. A new authorization-code grant with no usable refresh token records null. Refresh completion still checks the originating auth generation, account and captured token before commit.

**Evidence:** `tests/lifecycle.test.ts`, **“only a same-session refresh grant can retain an omitted refresh token”**, covers missing/empty new-grant values, same-session fallback, and token rotation.

### MOB-SEC-005 — An in-flight secure-store write could restore credentials after sign-out

**Severity:** High. **Status:** Corrected; host evidence recorded.

**Sources:** `src/core/serializedVault.ts`; `src/services/auth.ts` — `commit`, `updateIdentity`, `clear`. Requirements: immediate local sign-out and no stale credential resurrection.

**Counterexample:** A keychain/keystore `set` begins, sign-out removes the credential, and the earlier asynchronous `set` completes last. The supposedly signed-out account's refresh material is restored on disk.

**Required correction and current implementation:** Serialize vault writes/removals; invalidate in-memory authentication immediately; check generation/current-object guards before queued writes. A removal runs after any already-started write and prevents an older queued identity update from restoring data.

**Evidence:** `tests/lifecycle.test.ts`, tests **“sign-out removal finishes after an already-started OS credential write”** and **“a queued stale identity update cannot restore credentials after invalidation”**. These are controlled asynchronous storage-adapter tests; OS keychain persistence has not been physically exercised.

### MOB-SEC-006 — A pending arm operation could mount or settle after navigation stopped capture

**Severity:** High. **Status:** Corrected in source; integration evidence pending.

**Sources:** `src/controller.ts` — `startNativeTask`, `simulateDevice`, `withCaptureIntent`, `abandonArmedCapture`, `stopActive`. Requirements: AND-CHECK-003/005/006, AND-TASK-001/006/007, shared stop-before-navigation contract.

**Counterexample:** Start task persists or waits for synchronization/auth refresh while `activeTask` is still null. Back or OS background sees no active view and returns. The delayed arm continuation then mounts the task after navigation, or leaves a started attempt that has not been invalidated before the enclosing workspace transition.

**Required correction:** A capture-intent generation must invalidate immediately on any stop. Each awaited arm step must recheck the same foreground route, stage, check, workspace, and intent. A persisted-but-unmounted started attempt must be invalidated before stop completes. Physical acquisition cannot restart automatically when focus returns.

**Current review:** Independently re-read the completed `withCaptureIntent` checks and `stopActive` cleanup join. Stops invalidate capture intent immediately, join pending arm work, and propagate pending-start/invalidation-write failures. If a failed invalidation left an unmounted started attempt, the next explicit stop retries its invalidation before navigation; this avoids a permanently rejected write tail or silently lost evidence. Mounted native runs still require their full terminal receipt. No platform lifecycle acceptance is implied.

### MOB-SEC-007 — Generation/local-clear transitions retained history, selections and export metadata

**Severity:** High. **Status:** Corrected; host evidence recorded.

**Sources:** `src/core/domain.ts` — `quarantineGeneration`; `src/controller.ts` — `applyCapabilities`, `refreshHistory`, `acknowledgeNewGeneration`, `clearLocal`; `src/core/historyView.ts`; `src/ui/manage.tsx` — `HistoryScreen` and cached previews; `App.tsx` — route keys. Requirements: AND-HIST-001/006, AND-PRIV-005, shared anti-resurrection and current-generation display contracts.

**Counterexample:** Generation 1's remote metadata and selected IDs are cached. Deletion advances the account to generation 2. Only local check rows are filtered, so remote rows still appear. Acknowledging the new empty workspace clears the persisted state but leaves the separate displayed history array or same-epoch browsing memory. A late generation-1 history response can also pass an epoch-only guard and repopulate the new generation.

**Required correction:** Retire old asynchronous read authority and clear persisted and displayed history/cursors, selected check/export state, membership cache, retired export receipts, and temporary presentation state atomically with the generation/local-clear transition. Preserve deletion receipts and exact pending deletion reconciliation requests. Scope read continuations to the originating account, generation, workspace epoch, and local-clear fence. A remount key alone does not clear a singleton browsing-memory entry under an unchanged epoch.

**Completed domain correction:** `quarantineGeneration` now clears `historyIndex`, `historyCursor`, `exportEntry`, and `studies`; resets the current profile and use context to empty values; filters out retired-generation export jobs; retains deletion receipts and original pending deletion operations. An unknown current generation invalidates all cached export jobs. It does not rewrite the generation or frozen context of a retained payload. The optional clear timestamp can be supplied explicitly by the caller.

**Evidence:** `tests/generation-cache.test.ts`, **“generation quarantine clears cached history, selections and consent without discarding exact deletion receipts”**, **“unknown current generation invalidates every cached export but preserves deletion reconciliation evidence”**, and **“a fresh all-device export after retirement contains no prior current demographic or use context”** passed. Independently re-read the controller's epoch/fence advancement and presentation reset on a confirmed generation change or local clear. Its actual `retiredWithoutReplacement` helper also covers HTTP 410 before the replacement generation is known, including a deletion-only queue with human-readable service error text; the new direct regression in `tests/workspace-scope.test.ts` passed. History renders from the cleared `state.historyIndex`, scopes memory/events to epoch plus generation, and resets diagnostics previews. The selected-check getter, open action, and draft display reject quarantined records.

### MOB-SEC-008 — Job/study and share continuations lacked an originating owner fence

**Severity:** High. **Status:** Corrected; host evidence recorded.

**Sources:** `src/controller.ts` — `refreshJob`, `refreshStudies`, `shareJob`, export/privacy continuations; `src/services/api.ts` — cancellation semantics. Requirements: shared owner/account/generation isolation, AND-PRIV-005/006 and protected export/research ownership.

**Counterexample:** Account A starts a job or study fetch. The response has already been received, or its completion races an abort. Account B activates. The old continuation calls `commit`, which captures B's current epoch when invoked, and can persist A's job or membership metadata into B's state. Aborting fetch alone does not invalidate a decoded response. A local clear creates the same problem when the epoch remains unchanged.

**Required correction:** Capture an immutable owner/generation/epoch/local-clear/auth-flow scope before the request and check it after every asynchronous boundary and inside queued writes. Use the same scope for downloading and launching a share sheet. Reject or ignore stale results before changing UI, persistence or sharing. Generation changes cannot rebind an old selection to a new generation.

**Current review:** `src/core/workspaceScope.ts` now captures account, issuer, generation, workspace, epoch, local-clear fence, auth flow, unlocked state and foreground state. Independently re-read the job/study/history/download continuations and guarded platform sharing. The actual queued `commit` asserts the captured full scope **before** invoking the mutation and checks it again after storage; it does not rely only on a post-write check. `tests/workspace-scope.test.ts` has four passing delayed-response/confirmation cases plus the separate retirement-predicate regression. Full controller/platform integration remains separate from these pure guard tests.

### MOB-SEC-009 — Fresh local exports could still include quarantined retained records

**Severity:** High. **Status:** Corrected; host evidence recorded.

**Sources:** `src/core/domain.ts` — `selectExportChecks`; `src/services/export.ts` — local export selection. Requirements: AND-HIST-006, AND-PRIV-005, shared current-generation and exact export selection contracts.

**Counterexample:** Clearing an old export selection is insufficient if a new **All records** request still selects every frozen check, including a retained tombstoned generation. An explicit mixed selection could likewise include one current and one retired record.

**Required correction and current implementation:** Eligible records must be frozen, belong to the active workspace and generation, and not be quarantined. All-record selection uses exactly that eligible set. If any explicit selected ID is unavailable, reject the entire request without silently omitting it or broadening to other records. Current-generation ordinary records remain eligible.

**Evidence:** `tests/generation-cache.test.ts`, **“all-record device export excludes tombstoned and retired-generation retained records”** and **“explicit export containing one retired or quarantined check fails as a whole and never expands its scope”** passed.

## Areas inspected without an additional blocking finding

### Diagnostics and permission status

`src/core/diagnostics.ts` constructs a fixed allowlist rather than serializing exceptions or application records. Version, platform, environment, capability codes, sync state, error category and support request ID are bounded/validated; service URLs are reduced to their origin and reject embedded credentials. The diagnostics UI previews the exact report before an explicit copy action and handles clipboard refusal. Tests in `tests/support-history.test.ts` include contaminated error/profile/token inputs and untrusted oversized strings. Cached preview state must still be reset by the scope/presentation correction in MOB-SEC-007.

`PermissionsCard` guards asynchronous status results by query sequence and mounted state. Bluetooth and camera status helpers make no permission request. iOS uses the static `CBManager.authorization` and `AVCaptureDevice.authorizationStatus(for: .video)` APIs, with restricted, denied, not-determined and authorized cases. The podspec links CoreBluetooth and AVFoundation. Android uses `PermissionsAndroid.check` and labels false as not granted rather than claiming the OS distinguishes never requested from denied. The web adapter reports native unavailability/unknown explicitly.

Apple's primary API references inspected for the signatures: [CBManager.authorization](https://developer.apple.com/documentation/corebluetooth/cbmanager/authorization-swift.type.property) and [AVCaptureDevice.authorizationStatus(for:)](https://developer.apple.com/documentation/avfoundation/avcapturedevice/authorizationstatus(for:)). Signature inspection and TypeScript checking do not establish OS permission behavior on a device.

### Exact export and privacy confirmation

The reviewed export screen preserves exact selected IDs when changing device/cloud source, requires an explicit reviewed selection, and presents a new confirmation before widening to all records. An unavailable selected record causes an error. Completed export/deletion job labels are distinct; partial retention is not presented as total erasure. Native acquisition stops before confirmation overlays. Owner/generation and pending-arm findings above remain applicable to the asynchronous action handlers.

### Cardiac alternatives and saliva presentation

The reviewed ECG-006 correction permits one valid PPG and one valid ECG before freezing, retains both independent attempts, and requires explicit selection when both exist. Same-modality valid retakes remain blocked. `tests/cardiac-selection.test.ts` contains ten passing focused checks for modality, lineage, immutable evidence, failed alternatives and exact manifest selection.

Saliva display preserves nulls and qualifier meanings; it shows a numeric bound only when the corresponding LOD/LOQ/upper limit exists, and retains original report units and values without silently applying a second correction. `tests/measurement-format.test.ts` contains five passing focused checks. These are software presentation tests for fictional/reference DTOs, not assay validation.

## Evidence boundary and remaining verification

Executed native/device checks and reproduction commands are recorded in [`modules/VERIFICATION.md`](modules/VERIFICATION.md). They include the actual Kotlin production-core compile and six JUnit tests, fourteen device protocol/controller host tests, C++ adversarial protocol tests, the actual Nano ESP32 board-target compilation, literal configuration/hash checks, and independent backend validation of explicitly host-generated native and software-simulator fixtures.

The integrated commands `npm run typecheck` and `node --import tsx --test tests/*.test.ts src/device/tests/*.test.ts` were independently rerun after the completed controller corrections: **TypeScript passed; 94 host tests passed, zero failed**. The host result includes five generation/export/privacy regressions, five workspace-scope/retirement cases, seven auth/lifecycle guard cases, ten cardiac-selection cases and five saliva-presentation cases. `node modules/scripts/verify-native-assets.mjs` also passed for the unchanged configuration and three literal schedules. The three final source findings were closed by the targeted re-review described above, with host tests recorded at their actual scope.

This review does **not** assert that the full Android app, the Swift/Expo bridge, iOS application, physical Bluetooth radio, camera positioning, OS restrictions, or native task timing has passed device acceptance. No Android SDK or Xcode is installed in the local workspace. The GitHub workflow must produce actual successful build logs and artifacts before Android/iOS binary completion is reported. Photon onset, device input/display latency, optical/ECG hardware safety, saliva analytical performance and intoxication inference remain outside these host tests and are not qualified by this release.

All nine identified implementation findings are corrected at the source/host scope stated above. Full Android/iOS build and device-interaction gates remain outstanding until their actual outputs are observed. Do not convert an authored workflow or a source-level correction into fabricated execution evidence. The separate administrative report-revision amendment has its own pre-implementation review ledger and is not accepted as implemented by this report.
