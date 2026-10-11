# Reaction task fixtures before implementation

These are normative specification artifacts, frozen before Kotlin/Swift application code. They establish deterministic software behavior only; no physical display/touch timing or cannabis inference has been qualified.

- `reaction-task-config-v1.json` is the exact developmental configuration. Its JCS/SHA-256 digest is `61bd03244a9f82fdc5a1a2b6658483ca201ab5d39a95e64cde0d00f1d5a666c3`.
- `reaction-task-golden-v1.json` contains 66-trial schedules for seeds 0, 1, and 4294967295, literal schedule digests, focused input/aggregate vectors, and expected terminal behavior.
- A schedule digest covers exactly its nested `schedule` object (`schema_version`, `configuration_sha256`, `seed`, `trials`), using RFC 8785 JCS followed by SHA-256 and lowercase hexadecimal. File indentation/newlines are not hashed.
- Each of the 66 interval values is drawn after both shuffles. Interval i plans trial i+1; the final draw is retained in the schedule/hash but cannot prolong completion. Valid completion closes at the final actual onset + 1000 ms + 100 ms drain.
- Inputs dispatched at or after that terminal cutoff are outside the committed acquisition and cannot change it. Inputs arriving earlier with dispatch delay strictly greater than 100 ms invalidate it. These finite observation bounds are not a claim that every physical input will be captured.
- Focused trial vectors test the extractor with a single trial. They must not be accepted as a complete check. Complete-run recipes use all literal schedule trials; both platforms must construct the recipe independently and compare with the literal expected fields.
- Counts, outcome/state/source/nullability, ordering, schedules, and digests compare exactly. Quantiles/RTs compare at an absolute tolerance of 0.000001 ms; native clock accuracy is not implied by this arithmetic tolerance. Store native numeric resolution and retain unrounded values; UI rounds milliseconds to the nearest integer, halves away from zero.
- JSON configuration/schedule hashing values here use ASCII strings, safe integers, booleans, null, arrays, and objects. Native/app code must use the actual general JCS implementation for arbitrary accepted evidence; sorting keys and ordinary JSON serialization is not a general replacement for RFC 8785.

The implementing tests must read these literal files. A test that merely computes the expected schedule with the same implementation under test is insufficient. Changes to semantics, geometry, ordering, or budgets require a new configuration/fixture version and digest, without rewriting stored attempt evidence.
