# Decision impact register

No workers dispatched at checkpoint 1. New workers must acknowledge D-001 v1 and D-002 v1 through real messaging before relying on decisions. ACKs are coordination evidence, never signoff.

| Decision | Recipient | Actual ACK | Scope/action | Resolution |
|---|---|---|---|---|
| D-001 v1 | /root/product_audit | AFFECTED | Preserve scope/boundaries in all 47 product dispositions; raise material choices | Assigned audit owner; no unresolved clarification |
| D-002 v1 | /root/product_audit | NOT_AFFECTED | No product requirement change; parent supervision retained | Closed |
| D-001 v1 | /root/verification | AFFECTED | Bind all 47 plans/results and separate software/external evidence | Assigned planning owner; execution pending PM notice |
| D-002 v1 | /root/verification | AFFECTED | Send bounded updates, no supervisor mutation; preserve counters | Closed for planning |
| D-003 v1 | /root/product_audit | NOT_AFFECTED | Runtime setup independent of authored product requirements | Closed |
| D-003 v1 | /root/verification | AFFECTED | Plans target fresh fictional runtime and separate disposable database, preserve initialized state | Assigned planning owner; runtime execution PM |
| D-004 v1 | /root/product_audit | AFFECTED | Reconcile PRD to approved OpenSpec without scope change | Assigned owner, underway |
| D-004 v1 | /root/verification | AFFECTED | Expand individual PRD IDs, bind final product-source hashes and conditional-research precedence | Assigned planning owner |
| D-001 v1 | /root/firmware_validation | AFFECTED | Software-only firmware checks, no source edits/provisioning | Assigned verification owner |
| D-002 v1 | /root/firmware_validation | NOT_AFFECTED | No supervisor or recovery action | Closed |
| D-003 v1 | /root/firmware_validation | NOT_AFFECTED | Isolated firmware caches, no app data | Closed |
| D-004 v1 | /root/firmware_validation | NOT_AFFECTED | Unchanged firmware baseline, raise future requirement impacts | Closed |
| D-001–005 v1 | /root/engineering_audit | D1/3/4/5 AFFECTED, D2 NOT_AFFECTED | Preserve scope, apply approved PRD reconciliation, bounded source inspection only | Assigned engineering owner |
| D-005 v1 | /root/firmware_validation (reactivated) | AFFECTED | Preserve running services/volumes; no cleanup/restart/migration | Assigned proof owner |
| D-006 v1 | /root/engineering_audit | AFFECTED | Require full filesystem/config equivalence, preserve distinct image identity; no cloud equivalence claim | Conditions incorporated, no audit dependency |
| D-006 v1 | /root/firmware_validation | AFFECTED | Rootfs/Config proof before canonical mutation; stop on resource/fidelity mismatch | Assigned proof owner, canonical mutations held |
| D-006 v2 | /root/engineering_audit | AFFECTED | Exact declared-source reconstruction acceptable for local evidence with full metadata/config proof and original-export discrepancy retained | Conditions incorporated; no source audit dependency |
| D-006 v2 | /root/firmware_validation | AFFECTED | Exact restoration proposal prepared; full root/metadata/hardlink/config proof required before candidate import | Assigned proof owner; canonical actions held |
| D-001–006 current | /root/spec_reconciliation | D1/3/4/5 AFFECTED, D2/6 NOT_AFFECTED to edits | Approved scope/research precedence/fictional runtime/resource limits retained; image proof separate | Reconciliation owner synchronized |

## Implementation dispatch / checkpoint4

Reconciler released all edits; accepted implementation-plan tasks1–8. /root/mobile_builder, /root/evaluation_builder, /root/worker_builder, /root/browser_builder, /root/provenance_builder are real OpenAI gpt-6.1-sol/high (explicit spawn) workers. Each ACKed D001v1/D002v1/D003v1/D004v1/D005v1/D006v3 before edits. Disjoint file ownership; PM retains shared gates/workflows and coordination. No self-signoff. Current/live provenance14 vs explicit historical13 must remain distinct; browser fixture accounts isolated from A/B; worker probe separate disposable DB/queues/buckets.

## Checkpoint5 author/verification routing

Mobile/evaluation/provenance authorsreleased; workerprobe/wrapper frozen foractualpreflight, reportonlyupdates allowed. Browserreserved identities browser_mobile/browser_desktop plus backend-onlybrowser_staff; existingA/B/participantstaff preserved. /root/gate_integration OpenAIgpt-6.1-sol/high explicitspawn ACK D001–005v1/D006v3 and owns sharedci_gate/platformworkflow/CI docs/test only. /root/verification reactivated ACKlatestdecisions, independent percasebinding only,no Docker. Firmwareagent approved/tmp snapshot/build/package only, noDockerload until PMreceiptreview. Mandatoryliveprotocol mustkeep120s visibility/lease and50minjobbudget, current14jobinventory unchanged.
