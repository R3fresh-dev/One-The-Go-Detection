# Optional raw recording and frozen retention delta

This normative engineering delta refines AND-EYE-006, AND-STUDY-002, HLD section 8, LLD section 10 and SEC-003/005. It preserves version 1 scientific evidence and separates ordinary study consent, optional raw purpose, upload admission and physical deletion.

## RRAW-001: separately reviewed optional purpose

The application SHALL initialize eye-video and ECG-waveform recording/upload choices false. Enabling a choice SHALL require exact current study consent plus a separately acknowledged released policy/raw notice. The policy SHALL contain a study, purpose ID/text, allowed kinds, exact notice version/text/digest, allowed access roles, bounded days, validity and withdrawal behavior. Three distinct maintenance principals SHALL submit, approve and release immutable material. Unsupported retention exceptions SHALL refuse raw admission rather than imply a legal hold.

### Scenario: study consent does not grant raw permission

Given accepted current study consent and no optional-purpose receipt, when a participant opens raw settings or requests a raw ticket, then settings show both choices false and ticket admission refuses.

### Scenario: reviewed content changed

Given an acknowledged optional raw notice, when consent, policy version/hash, purpose or exact notice changes, then effective choices require a new review and the old grant cannot authorize recording/upload.

## RRAW-002: immutable receipt and acquisition-bound lifetime

Preference acceptance SHALL create a separate immutable receipt and current pointer. A later revocation SHALL never rewrite that receipt. Participant tickets SHALL require its exact ID and an owned immutable acquisition start matching the session/component/modality and prior grant. Retention SHALL freeze at the earlier declared/first-server-owned start plus approved days before ticket creation. Completion retry, policy refresh, terminal attempt update or reupload of identical same-generation bytes SHALL never extend the earlier lifetime. Administrative report PDFs SHALL use a distinct approved purpose/role with a conservative original-session anchor.

### Scenario: permission granted after capture

Given capture preceding the optional grant, when an upload is requested, then admission refuses even if ordinary study consent is current.

### Scenario: retry after verification

Given a frozen lifetime and verified exact object version, when completion is retried or a newer policy is released, then the original deadline remains unchanged.

### Scenario: administrative source document

Given participant raw choices, when a source laboratory PDF is requested, then those choices do not authorize it; a separate current administrative role/purpose/policy is required.

## RRAW-003: immediate authority retirement and safe write-window cleanup

Revocation/withdrawal SHALL immediately stop local capture, retire server verification authority and persist an idempotent privacy receipt. Physical cleanup SHALL retain existing conditional-write barriers until the frozen ticket deadline plus 60 seconds. It SHALL then delete all exact-key version IDs and delete markers, verify an empty inventory and settle purge. Prefix neighbors SHALL remain unchanged. A failed dependency/crash SHALL retry, and purged keys SHALL receive recurring late-arrival reconciliation.

### Scenario: revoked ticket replay

Given a first conditional PUT and a still-valid upload ticket, when consent is revoked, then verification fails, status remains cleanup pending, replay receives 412 while the original version remains, and physical purge follows the write deadline/margin.

### Scenario: old version behind a delete marker

Given an object with overwritten versions and a delete marker, when purge runs, then every exact version and marker is deleted and a marker alone does not count as erasure.

### Scenario: late in-flight write or worker crash

Given apparent purge or external deletion before database settlement, when a late version appears or the worker retries, then retained exact-key references reconcile it without resurrecting verification.

## RRAW-004: bounded lifecycle status and metadata erasure

Status SHALL distinguish retained lifecycle from quarantine/verified upload state, show frozen due times, exact grant/revocation receipts and paginate at most 500 artifact rows. Revocation completion SHALL consider all targeted rows independently of a displayed page. Payload purge SHALL compact raw hash/acquisition/attempt/consent metadata to a bounded cleanup reference and same-generation keyed no-extension fingerprint. Retired generation cleanup SHALL additionally remove fingerprint/study/kind. PostgreSQL SHALL permit only these one-way compactions and SHALL prevent restoring authority or changing owner/key/lifetime.

### Scenario: history has more than one page

Given more than 500 historical lifecycle rows, when status is read, then it returns a next cursor and does not falsely mark an off-page pending revocation completed.

### Scenario: account data is deleted

Given physically purged raw objects in a retired account generation, when cleanup settles, then acquisition/consent identifiers and raw hashes/fingerprints are removed while minimal exact cleanup references remain for delayed writes.

## JRNL-001: independently established journal binding

PostgreSQL SHALL pin the original canonical journal control object's exact non-null version/digest and environment/region/bucket/key. Initialization SHALL check that binding before resource creation; API/readiness SHALL check it before protected admission. A missing/replaced marker SHALL fail closed even in the default local workspace.

### Scenario: emulator state lost but PostgreSQL retained

Given retained accounts and journal binding, when storage restarts without the original control version, then initialization/admission fail and no replacement bucket/marker is silently created.

### Scenario: identical bytes in a replacement version

Given a pinned original version, when identical bytes appear under a new current VersionId, then admission refuses the replacement.

## JRNL-002: explicit one-time administrator upgrade

A confirmed empty first database MAY bind its newly established marker. Existing unbound accounts SHALL require separately reviewed administrator-supplied exact original version and SHA256; resource preflight SHALL not write SQL and migration SHALL write transactionally. This import SHALL never replace an existing binding or authorize recreating missing evidence.

### Scenario: existing unbound deployment

Given retained accounts without a journal binding, when startup has no original independently verified receipt or supplies a mismatched receipt, then migration/preflight refuse automatic adoption.

### Scenario: receipt verified without mutation

Given the exact reviewed original receipt, when resource preflight succeeds, then SQL remains unbound until the maintenance migration transaction commits it.

Implementation: `otgd/raw_retention.py`, `otgd/journal_continuity.py`, migration 004, participant/admin routes, maintenance sweep and resource preflight. Evidence: isolated raw/journal tests, actual disposable LocalStack version probe, mobile actual-server response fixture. Physical capture validity, durable emulator restart and actual QA/prod restore remain separate required release evidence.
