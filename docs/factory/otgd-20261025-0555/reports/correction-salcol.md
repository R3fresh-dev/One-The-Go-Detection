# SALCOL bounded assertions and required-chemistry repair

Owner `/root/worker_builder`; formal correction **1/2**, recovery **0/3**, unchanged. D-009 v7 and v8 acknowledged through actual PM messages and read in `decisions.md`. The PM checkpoint write hold was honored: no new SALCOL edits began until its explicit release after checkpoint 9 (`52ffa1044e787f7fea088c82797d4525af02e9a3`). No commits, pushes, Docker/service operations, installs, retained-data resets, deployment, participant actions or scientific threshold changes were performed. This report is builder evidence, not self-signoff.

## Exact scope and existing evidence

Read the current `reference-lab-collection/spec.md`, existing participant/laboratory test bodies and the verifier's immutable `verification-participant/final-batch.json` rows for six exact criteria. Existing positive full collection/staff-import/finalization tests were retained. Source-creation and ticket-replay negatives were not relabeled as initial-import assertions. The old candidate's adjudication remains unchanged; new source and execution are separately bound here. Browser SALCOL00702 late-callback work remains mobile-owned.

Only two test files were extended under v7: `test_participant_acquisition.py` and `test_lab_handoff.py`. Following the true SALCOL00806 failure, PM's v8 separately authorized a narrow `participant_acquisition.py` guard and a call from `main.py::finalize`. No other runtime behavior was changed by this worker.

| Exact case | New named assertion and observed effect |
|---|---|
| OTGD-040-SALCOL-008-02 | `test_collection_first_late_submission_is_denied_but_exact_key_replay_stays_historical[False/True]`: first actual collection POST at original collection time plus released maximum submission delay plus 1ms returns 422 `COLLECTION_TIME_INVALID`, leaves no collection receipt and preserves the started attempt. A separately accepted exact body/key replay after the same bound returns the identical historical receipt/body/hash/created time; it stays pending with empty chemistry and no lab import. |
| OTGD-040-SALCOL-002-04 | `test_present_collection_value_cannot_also_claim_a_missing_reason[saliva_volume_ml/collector_lot]`: a present numeric or identity field simultaneously claiming `unknown` returns 422 `VALIDATION_FAILED`; no collection is recorded and original arm is unchanged. This isolates the contradictory-value clause from existing null/unapproved-reason tests. |
| OTGD-040-SALCOL-005-03 | `test_initial_import_refuses_foreign_target_scope_not_only_source_creation[study/generation/participant]`: after actual HTTP source ticket/completion, initial HTTP import refuses another study, generation or participant identity. The study case first independently extends the staff role to that other study so the refusal reaches actual target-study mismatch rather than merely an unapproved caller role. Expected errors are `LAB_TARGET_SCOPE_MISMATCH`403, `LAB_TARGET_UNAVAILABLE`403 and `NOT_FOUND`404. |
| OTGD-040-SALCOL-005-04 | `test_initial_import_readmits_configuration_consent_staff_and_report_custody[retired_configuration/withdrawn_consent/foreign_staff/foreign_report]`: first import after actual configuration retirement or consent withdrawal returns `CAPABILITY_DENIED`403; a distinct staff caller with independently released authority for another study receives `LAB_IMPORT_ROLE_REQUIRED`403; verified report metadata belonging to another actor's custody receives `NOT_FOUND`404. These are initial imports, not replay or source-ticket-only checks. |
| OTGD-040-SALCOL-008-05 | `test_pending_collection_cannot_satisfy_required_chemistry_and_does_not_invent_optional_values[True/False]`: starts from an actual HTTP pending collection, then independently submits/reviews/releases typed fictional calibration/model/study bodies with chemical-required versus chemical-optional manifests. The actual `model_engine.scope_check` refuses the required missing chemical with `MISSING_REQUIRED_CHANNEL`; the optional branch preserves empty chemistry while still refusing inappropriate nonchemical provenance/method and expired delivery timing. No score is computed and no lab import or inferred concentration is created. |
| OTGD-040-SALCOL-008-06 | `test_abandonment_cannot_finalize_when_current_model_requires_missing_chemistry[required/optional/unconfigured/retired_model/measurement]`: actual collection, explicit abandonment and sample-only snapshot/manifest publication preserve the original receipt/sample/attempt. A current required-chemistry model now yields 422 `MISSING_REQUIRED_CHANNEL`, stays draft, and creates **no Job and no Outbox**. Permitted missing chemistry, no configured model, a model retired before finalization, and ordinary analytical measurement each retain prior 202 behavior. These positives grant recording/finalization only, not numeric model eligibility. |

Every new initial-import refusal additionally asserts: original collection body/digest and original collection attempt remain; no `lab_import`, analytical attempt, delegated-import audit or successful import dedup row is added; the participant's check remains a draft without a scientific snapshot. Existing report-store helpers are reused; no whole fixture was rewritten. The only fixture adjustment is an optional session-mode parameter used to exercise ordinary analytical measurement without changing existing defaults.

SALCOL00805 is explicitly a **bounded model scope-boundary assertion**: its additional nonchemical channels are engineered fixture data. It is not a full current execution-authority/native/physical/scientific qualification pipeline or evidence of a separately eligible numerical result. Existing broader model authority/tuple tests retain their own scope. PDF storage is the existing named bounded double, not actual LocalStack/AWS report custody.

## Demonstrated defect and authorized runtime repair

The initial required-chemistry regression genuinely released the fictional current model with `required_channels=['saliva_thc']`, matching artifact feature identity and model calibration, and linked the current study through its actual three-principal lifecycle. It accepted a genuine collection and explicit abandonment, published the corresponding empty-chemistry snapshot and exact evidence hashes, then called `/finalize`. The old code returned **202 processing and a result job**, contradicting canonical SALCOL00806's missing-minimum refusal.

The true RED is preserved as `correction-salcol-chemistry-red.xml` and `.log`. That run also contains a separate optional-test fixture mistake: an unscaled eye mutation retained a millimeter diameter forbidden by the Session schema. The test input was corrected to null diameter before probing the intended incompatibility guard. That oracle issue was not counted as a second production defect.

PM corroborated the finalization failure and assigned D-009 v8 before any runtime edit. The repair adds `require_abandoned_chemistry`, called **after** `verify_evidence` and exact submitted digest matching, **before** evidence/state/revision/job/outbox mutation. Its boundary is deliberately narrow:

- It applies only to controlled-research checks with a current owned-generation abandonment reference. Existing evidence verification authenticates the selected collection, abandonment, consent and configuration first.
- It resolves the existing current released study and optional current released model. No model, a retired/unadmitted model, or a model not admitting this study retains ordinary recording behavior.
- It returns without adding other-channel or whole-model scope gates when the current manifest requires no chemical channel.
- For required chemical channels only, existing model dependency validation remains in force; the verified snapshot must contain a valid specimen and actual quantified entries for every required chemical analyte. Missing chemistry returns the established `MISSING_REQUIRED_CHANNEL`422.
- It neither invokes inference nor creates values, approvals, new thresholds, secrets, hardware actions or retention policy. Original specimen/attempt/receipt/abandonment evidence remains unchanged.

The required refusal and four positive controls pass. Numeric read-admission work is a separate PM-assigned specialist task; this worker explicitly released `main.py` to that owner and made no read-boundary edits.

## Actual execution

All commands ran from `/workspace/One-The-Go-Detection` with installed dependencies and `UV_CACHE_DIR=/tmp/otgd-uv-cache`:

```sh
uv run --project services/api pytest services/api/tests/test_lab_handoff.py services/api/tests/test_participant_acquisition.py -q -k 'first_late_submission or present_collection_value or initial_import_' --junitxml=/tmp/correction-salcol-import-chronology.xml
uv run --project services/api pytest services/api/tests/test_participant_acquisition.py -q -k 'pending_collection_cannot or abandonment_cannot_finalize' --junitxml=/tmp/correction-salcol-chemistry-red.xml
uv run --project services/api pytest services/api/tests/test_participant_acquisition.py services/api/tests/test_lab_handoff.py -q -k 'not abandonment_cannot_finalize' --junitxml=/tmp/correction-salcol-existing-and-new.xml
uv run --project services/api pytest services/api/tests/test_participant_acquisition.py -q -k 'pending_collection_cannot or abandonment_cannot_finalize' --junitxml=/tmp/correction-salcol-chemistry-green.xml
uv run --project services/api pytest services/api/tests/test_participant_acquisition.py services/api/tests/test_lab_handoff.py services/api/tests/test_api.py services/api/tests/test_model_admission.py services/api/tests/test_recovery_scopes.py services/api/tests/test_privacy_receipts.py -q --junitxml=/tmp/correction-salcol-final.xml
```

Observed in order: **11 passed / 103 deselected** for the first added boundaries; true RED **2 failed / 1 passed / 63 deselected** with the two distinct causes above; **116 passed / 1 deselected** for unaffected/other related cases while the confirmed failure awaited assignment; **6 passed / 63 deselected** after the authorized repair; final related regression **184 passed**, **25.91s**, exit0, with **zero JUnit skips, failures or errors**. Intermediate deselections are declared scoped runs, never mandatory-gate passes.

Final per-file execution: participant70, laboratory51, API33, model-admission15, recovery-scopes14, privacy-receipt1. Existing Starlette/httpx deprecation warning remains. Scoped test-participant Ruff and whitespace diff checks pass. Broader Ruff findings in existing participant runtime/lab files are preexisting; no broad formatting cleanup was performed. No full gate, current coverage claim, hosted/browser/native test or live dependency execution is represented by this report.

## Released source and evidence

All four runtime/test files were explicitly released to PM at approximately **2026-10-25 09:13 UTC**; `main.py` was also explicitly handed off to the separate numeric-read specialist. These hashes bind **this worker's executed/released boundary**, not later edits by that owner:

| File | SHA-256 |
|---|---|
| `services/api/otgd/main.py` | `2832d8623381d5e7e875cd2baaa48f737725fb2da380f2b03dd7dd5d17534aac` |
| `services/api/otgd/participant_acquisition.py` | `bfef64d21a695a3bf9c3dd853592b007f8ff3b75eb02888af9e70963e33eba6e` |
| `services/api/tests/test_participant_acquisition.py` | `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a` |
| `services/api/tests/test_lab_handoff.py` | `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492` |

This external directory retains ten raw XML/log artifacts, exact copies of the four released files under `source/`, and a source/artifact SHA-256 manifest with per-file test counts. Prior reports and E/F image proofs remain unchanged/unadopted; a new current COPY proof is required only after all runtime authors release. Final exact-candidate gates, coverage, semantic reconciliation, six independent confirmations and final approval remain PM-owned. There was no auto-review denial or uncertain external action. No software result here grants participant or scientific authority.
