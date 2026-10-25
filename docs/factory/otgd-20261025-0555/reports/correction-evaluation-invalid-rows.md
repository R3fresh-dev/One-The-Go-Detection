# Round1 evaluation invalid-row supplement

Owner: sole PM /root, OpenAI GPT-6 family reported by host; exact runtime variant unavailable. Scope: verifier-confirmed EVAL-003-02 missing acceptance assertion within active correction1/2; recovery0/3. Production unchanged. The prior evaluation author released this file before PM edit.

The existing eleven future/invalid input corruption cases now run for both valid and invalid acquisition rows. Each first proves that the uncorrupted row is admissible with its stated acquisition status, then requires actual Dataset admission to reject the corrupted input. This directly covers future information even when an acquisition is already invalid; invalid status cannot bypass predictor custody.

Actual command: `UV_CACHE_DIR=/tmp/otgd-uv-cache uv run --project services/api pytest services/api/tests/test_model_evaluation.py -q -k invalid_or_future_source_data --junitxml=/workspace/scratch/otgd-20261025-0555-live/evaluation-invalid-future.xml`. Exit0;22passed,35deselected in0.42s, one existing Starlette/httpx deprecation warning. Deselections belong to this focused check; final full gate must execute every required case. No production fix or new scientific threshold.

SHA-256 source: `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`. Raw log: `9cc2b389134b372140291ad1dc87ac851cc9b26cc4f4ca84197a29ba7972552b`. Raw JUnit: `615c1de1a2f9be270b28caab819dbe0a2332c9b6090acb3c74a4f276c3f6cf0b`. Evidence remains external at the named paths.

This supplements, rather than rewrites, the earlier correction-evaluation author report and its historical179-case source binding. Final190-case evaluation/full local and CI execution are still required for the replacement candidate. No scientific/participant/hardware qualification or independent signoff follows.
