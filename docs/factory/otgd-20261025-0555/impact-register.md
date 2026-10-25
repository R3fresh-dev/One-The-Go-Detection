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
