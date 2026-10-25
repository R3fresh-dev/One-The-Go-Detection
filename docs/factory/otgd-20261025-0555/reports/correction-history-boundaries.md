# Round 1 history cursor and instruction boundary correction

Owner: `/root/worker_builder`. D-009 v5 acknowledged before edits; still formal correction **1 / 2**, recovery **0 / 3**. This is implementation/test evidence for PM review, not self-signoff, an application completion decision or release authorization. The preceding `correction-backend-assertions.md` and old-candidate adjudications remain preserved.

## Confirmed defect and authorized repair

The normative history contract in `openspec/changes/production-mobile-platform/specs/android-history/spec.md` requires an opaque cursor bound to owner, environment, sort and a stable boundary; AND-HIST-002 requires stable pagination across a newer finalized insert. Existing `session_list` accepted only `{id,created}`. Two new actual HTTP regressions first reproduced foreign-owner and retired-generation cursor acceptance with **200**, where scoped cursor admission requires **422 INVALID_CURSOR**. Returned rows still belonged to the current authenticated owner/generation; this report makes **no cross-account data disclosure claim**.

The repair is limited to `main.py::session_list`, its codec import, and new `otgd/history_cursor.py`. The D-009 v4 `job_view` correction remains intact. The existing owner/generation SQL filter, `(created DESC,id DESC)` ordering, limit/lookahead semantics and response fields remain in place. A supplied empty cursor is now invalid instead of being treated as an absent cursor. Old unsigned cursors require a fresh list request, following the existing invalid-cursor contract; no new cursor lifetime is invented.

The existing replacement-link codec supplied a useful strict bounded parsing pattern but uses an unkeyed scope hash. PM explicitly accepted a domain-separated HMAC using the already bound tombstone key, matching the existing raw-payload reference pattern. No new secret, protected setting, key mutation, key-generation fallback or replacement-link behavior was introduced.

The new history scope binds environment, issuer, authenticated owner, current generation and fixed sort. Its versioned canonical position binds the exact Check UUID and created value under HMAC-SHA256, with constant-time MAC comparison. The parser bounds input to 1024 URL-safe characters before decoding, validates canonical base64/JCS, exact fields, version, canonical UUID, finite positive safe numeric time and MAC shape. The existing identity-key descriptor fails closed if key material is missing. After signature/scope admission, `session_list` separately queries the actual current owned Check with the exact ID, generation and created value. A deleted, moved, retired, changed-time or nonexistent boundary produces the same generic 422 error.

## Assertion bindings

All new history assertions live in `services/api/tests/test_history_cursors.py` and exercise the actual TestClient API/JWT/account transactions with disposable SQLite fixtures. They are software assertions, not live cloud/PostgreSQL or browser/OS evidence.

| Requirement / risk | Named assertion | Observed boundary |
|---|---|---|
| Authenticated owner scope | `test_history_cursor_cannot_be_replayed_for_a_foreign_owner` | A's actual issued cursor is rejected for B, while B's fresh list still returns only B's expected rows. RED old HTTP200 → GREEN422. |
| Current generation | `test_retired_generation_cursor_is_not_an_admitted_current_boundary` | Old cursor is rejected under current generation-two headers; refreshed list returns generation-two rows. RED old HTTP200 → GREEN422. |
| Scope and authenticators | `test_forged_position_scope_or_authenticator_is_refused` | ID, created, scope and MAC tampering, boolean/string/negative/unsafe created values and bad UUID all fail with INVALID_CURSOR. Canonical-shape tampering reaches MAC verification rather than relying only on whitespace rejection. |
| Bounded strict parsing | `test_history_cursor_strict_bounded_parser_refuses_malformed_input` | Empty, malformed, >1024-character, non-URL-safe, null/empty JSON, duplicate-key and nonfinite JSON inputs are rejected. |
| Environment and sort | `test_cursor_environment_and_sort_are_bound_even_with_authentic_mac` | Properly MAC-authenticated cursors issued for another environment or fixed-sort identity still fail current scope admission. |
| No insecure key fallback | `test_cursor_authenticator_has_no_missing_key_fallback` | Missing identity-key material raises `IDENTITY_KEY_UNAVAILABLE`; the codec does not generate or substitute a key. |
| Actual stable current boundary | `test_signed_cursor_still_requires_an_actual_unchanged_owned_boundary` | Otherwise authentic cursors fail after boundary deletion, created-time change, owner change, retirement into another generation, or signing an absent ID. |
| AND-HIST-002 concurrent insert | `test_new_finalized_check_does_not_shift_existing_tied_pages_and_appears_on_refresh` | Five existing tied rows page in descending UUID order; a newly uploaded check is actually finalized between pages. Page two/three contain each original row exactly once, and refresh places the new processing check first. |

## Instruction-age boundaries

The participant semantic reviewer `/root/acceptance_participant` confirmed the exact historical gaps: PAI-002 scenarios **Exact acknowledgment-age boundary** and **Future or pre-attempt declaration** had only 121-second stale / +10-second future checks, without equality or isolated `attempt.created−5` coverage. Their frozen old-candidate assessment remains historical; they explicitly confirmed these additions address the missing assertions for replacement-candidate rebinding, without a blanket PASS or physical/study claim.

Only tests changed in `test_participant_acquisition.py`; no participant acquisition production logic or approved timing threshold changed. Twelve parameterized HTTP cases were added:

| Named test | Cases and observations |
|---|---|
| `test_acknowledgment_submission_maximum_age_exact_boundary` | At approved age A−1ms and exactly A, POST returns 201 and retains the original declaration. At A+1ms it returns 422 ACKNOWLEDGMENT_TIME_INVALID and creates no receipt. The separate attempt-creation bound is deliberately nonlimiting. |
| `test_acknowledgment_submission_attempt_minus_five_seconds_exact_boundary` | At attempt.created−5s+1ms and exactly −5s, POST returns 201. At −5s−1ms it returns 422, no receipt is created, and the saved arm body stays unchanged. The age window is separately nonlimiting. |
| `test_original_instruction_receipt_expires_only_after_maximum_at_grant_and_start` | Actual fresh grant **and** actual start are separately evaluated at original T+A−1ms, equality, and +1ms. The original client declaration is explicitly earlier than original server acceptance, so their minimum T cannot be replaced by a replay time. Equality is admitted; later authority is denied with 403 INSTRUCTION_ACKNOWLEDGMENT_EXPIRED. Same-key response replay, stored body/hash/created time remain unchanged. Refused grants create no authorization; refused starts leave only an issued, unstarted authorization. |

The participant-module clock and disposable fixture creation times are controlled only to isolate these software boundaries. Real approved durations, server authority checks and production constants are unchanged. These cases do not establish elapsed physical rest, OS timing, human compliance or sensing qualification. Other PAI clauses and external prerequisites retain their own evidence requirements.

## Actual commands and results

From `/workspace/One-The-Go-Detection`, with the installed API environment and `UV_CACHE_DIR=/tmp/otgd-uv-cache`:

```sh
uv run --project services/api pytest services/api/tests/test_history_cursors.py -q -k 'foreign_owner or retired_generation' --junitxml=/tmp/correction-history-red.xml
```

Observed against the prior cursor code: **2 failed**, 26 deselected; both failures were actual HTTP200 instead of expected INVALID_CURSOR422. The preserved RED XML is not passing evidence.

```sh
uv run --project services/api pytest services/api/tests/test_history_cursors.py -q --junitxml=/tmp/correction-history-green.xml
uv run --project services/api pytest services/api/tests/test_participant_acquisition.py -q -k 'maximum_age_exact or minus_five_seconds or expires_only_after_maximum' --junitxml=/tmp/correction-preparation-boundaries.xml
```

Observed initial history implementation **28 passed**, then **12 new instruction cases passed / 47 unrelated cases deselected**. History coverage was subsequently strengthened with authentic sort signatures and missing-key/retired-boundary cases, reaching 30 history cases in the final aggregate below.

Final source check:

```sh
uv run --project services/api ruff check services/api/otgd/history_cursor.py services/api/tests/test_history_cursors.py services/api/tests/test_participant_acquisition.py
uv run --project services/api pytest services/api/tests/test_history_cursors.py services/api/tests/test_participant_acquisition.py services/api/tests/test_api.py services/api/tests/test_replacement_links.py services/api/tests/test_identity_barriers.py services/api/tests/test_privacy_receipts.py -q --junitxml=/tmp/correction-history-boundaries-final.xml
git diff --check
```

Observed **158 passed**, 13.64 seconds, exit 0; no JUnit skips, failures or errors. All three scoped Ruff targets and whitespace check passed. The existing Starlette/httpx deprecation warning remained; no installation or dependency adjustment was made. No full aggregate gate, live dependency runner or Docker/service action was invoked.

## Released source and preserved evidence

Final COPY source release sent to PM at **2026-10-25 approximately 08:49 UTC**:

| File | SHA-256 |
|---|---|
| `services/api/otgd/main.py` | `87c17dd014fa325e2283c1a06a27607609d5697f5e07422d6c4512ccefb96c29` |
| `services/api/otgd/history_cursor.py` | `f6fff83507257b75a7fcabde84fd35ac46ad129563df4bcafe6fcefac700112e` |
| `services/api/tests/test_history_cursors.py` | `6c309744fdcd25f8d9b28ac4981736f52232700e3047e0ddb5dda45147fbf554` |
| `services/api/tests/test_participant_acquisition.py` | `b8d8445e4d55518f0bd5fdfe3c870542623c2c72d249f849ab4600ec691ee843` |

Final JUnit SHA-256: `5b2c4eb2fea0a367236c4be308c5528e6bd54ee058f81a14bfec33bfe8ec1e6a`. Exact-boundary JUnit SHA-256: `0cb2531e76795e9a5e38ced8d864984d5c702d27c5c4be5e8a67f50172c109d9`. RED JUnit SHA-256: `650d3f5f76661fe78ebd9f8a2d495ffcf3fc2edb937c70f8ec5bc388e7a8b892`.

Durable copies and a source/artifact manifest are retained in `/workspace/scratch/otgd-20261025-0555-live/correction-history-boundaries/`. No existing reports, retained databases, public schemas, credentials, app services, volumes or journals were reset or removed. No commit or push was made. No action was approval-denied or left with an uncertain external outcome.

The prior ImageE was prepared before this main/codec change and is explicitly **not current executable-source evidence** for these edits. PM controls regeneration, admission and any later runtime adoption after the required source proof. Final exact-candidate local/CI gates, independent coverage, complete semantic reconciliation, affected independent confirmations and final approval remain pending; no release or participant authority follows from these 158 software tests.
