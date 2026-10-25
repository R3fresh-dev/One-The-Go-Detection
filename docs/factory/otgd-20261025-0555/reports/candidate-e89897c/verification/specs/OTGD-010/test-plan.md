# OTGD-010 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/authorized-raw-export/specs/raw-export-authorization/spec.md`; SHA256 `6e7ff5b60880e7234eec431ccb702b3e452b6a1d6e76a01720cb60b478782993`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-010/test-plan.md`. External review artifact only; PM controls import.

All 19 stable cases / 8 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-010-RAW-EXP-001-01 | Recording exists without export approval — - **GIVEN** an owned retained recording and current optional recording consent - **WHEN** a participant requests its raw export without separate released authority - **THEN** raw export is denied and metadata-only export remains available. | PARTIAL |
| OTGD-010-RAW-EXP-001-02 | The reviewer is also the submitter — - **GIVEN** a submitted raw-export version - **WHEN** the same verified principal tries to approve or release it - **THEN** the registry rejects the transition and no current export grant exists. | PASS |
| OTGD-010-RAW-EXP-001-03 | Three distinct authorized principals release an exact grant — - **GIVEN** current independently approved dependencies and a typed owner/generation grant - **WHEN** distinct submitter, reviewer and releaser complete its real registry lifecycle - **THEN** its immutable version and content hash admit only the exact approved scope. | PASS |
| OTGD-010-RAW-EXP-002-01 | Nine valid authorities contain maximum-sized notices — - **GIVEN** nine current independently released owned authorities - **WHEN** the client follows each authority cursor - **THEN** all nine are offered across bounded pages without response overflow. | PASS |
| OTGD-010-RAW-EXP-002-02 | A source exceeds the complete export byte cap — - **GIVEN** a retained recording larger than its authority's uncompressed cap - **WHEN** current export choices are requested - **THEN** that source cannot be selected and other eligible choices remain usable. | PASS |
| OTGD-010-RAW-EXP-003-01 | Consent to recording is reused as export confirmation — - **GIVEN** the participant approved optional recording earlier - **WHEN** raw export is requested without its separate confirmed export notice - **THEN** the request fails without creating a raw job. | PARTIAL |
| OTGD-010-RAW-EXP-003-02 | An accepted reply was lost and the grant is later retired — - **GIVEN** an accepted raw export and its original request key/body - **WHEN** the request is retried after authority retirement - **THEN** current admission denies it rather than disclosing the stale approved scope. | PASS |
| OTGD-010-RAW-EXP-003-03 | A separately confirmed owned selection creates a stable job — - **GIVEN** exact current authority and an explicitly acknowledged export notice - **WHEN** the customer submits selected owned artifacts and retries the identical body/key - **THEN** one pending job preserves the original selected sources and acknowledgement. | PARTIAL |
| OTGD-010-RAW-EXP-004-01 | The current key has a new S3 version — - **GIVEN** an accepted pinned original source version - **WHEN** a different current object version appears - **THEN** worker reads only the verified accepted version and checks its actual bytes. | PARTIAL |
| OTGD-010-RAW-EXP-004-02 | Withdrawal occurs during source retrieval — - **GIVEN** a raw job reading outside a database transaction - **WHEN** its participant consent is withdrawn before the read completes - **THEN** post-read admission rejects publication and no current ZIP is exposed. | PARTIAL |
| OTGD-010-RAW-EXP-005-01 | A ZIP contains a rehashed unselected recording — - **GIVEN** an authenticated job permits only recording A - **WHEN** a well-formed rehashed ZIP includes recording B instead - **THEN** the client rejects the archive rather than importing or sharing it. | PARTIAL |
| OTGD-010-RAW-EXP-005-02 | An exact selected archive verifies against its authenticated job — - **GIVEN** a completed job with exact approved source descriptors - **WHEN** its ZIP preserves all selected structured lineage and raw versions/hashes/bytes - **THEN** the archive inspector validates it and exposes only the approved selected contents. | PASS |
| OTGD-010-RAW-EXP-006-01 | Expiry occurs while S3 download is delayed — - **GIVEN** a currently approved completed export - **WHEN** it expires before the storage read returns - **THEN** post-read admission returns a denial with no ZIP bytes disclosed. | PASS |
| OTGD-010-RAW-EXP-006-02 | Revocation follows the first delivery chunk — - **GIVEN** a verified archive larger than 64 KiB - **WHEN** raw permission is revoked after its first admitted chunk - **THEN** the next admission fails and no second chunk is sent. | PASS |
| OTGD-010-RAW-EXP-006-03 | An uninterrupted verified download succeeds — - **GIVEN** current authority and a completed exact-version ZIP - **WHEN** storage bytes and every delivery-boundary admission remain valid - **THEN** the signed-in owner receives the complete hash-matching no-store attachment. | PASS |
| OTGD-010-RAW-EXP-007-01 | A stale worker uploads after the first cleanup sweep — - **GIVEN** revoked logical delivery and a completed first prefix sweep - **WHEN** an older worker's output arrives later - **THEN** the recurring sweep deletes its exact version and delivery remains denied. | PARTIAL |
| OTGD-010-RAW-EXP-007-02 | The customer refreshes after raw-copy cleanup — - **GIVEN** an owned revoked export after cleanup - **WHEN** its status is refreshed - **THEN** the terminal revoked receipt remains visible without grant or download metadata. | PASS |
| OTGD-010-RAW-EXP-008-01 | Raw sources fit but their structured evidence exceeds the cap — - **GIVEN** raw files fit within the approved uncompressed byte limit - **WHEN** adding selected structured records and the manifest exceeds that limit - **THEN** the entire job fails without producing a partial downloadable archive. | PASS |
| OTGD-010-RAW-EXP-008-02 | The complete selected archive fits all approved bounds — - **GIVEN** selected structured records, manifest and explicit raw sources within the narrower caps - **WHEN** the fenced worker assembles and publishes the exact verified archive - **THEN** the complete job succeeds without omitting a selected record or widening the limits. | PARTIAL |
