# Physical replacement navigation — implementation amendment

**Status:** normative contract, authored before its follow-up implementation. **Date:** 2026-10-11. This freezes the read boundary for AND-HIST-004 and AND-RES-005. Administrative same-specimen report revisions follow the separate [report revision contract](report-revision-contract.md).

## Customer experience and scope

A saved check with `supersedes_session_id` offers **View original check**. A saved original offers its directly replacing checks, newest first, under **Replacement checks**, with **Load more** only when another bounded page exists. Each entry shows its original acquisition time and current processing/result state. Opening a link uses the normal owned-check detail journey and preserves the origin history position. A replacement is a new physical check with its own target and captures; navigation never copies measurements, changes either record, or implies that the original was deleted or invalidated.

Local derivation uses only the active workspace, current data generation and nonquarantined checks. A late cloud response or callback from an older workspace/generation/epoch cannot alter navigation or reopen old data. Offline, show locally available relationships with **More links may be available when connected**; do not represent a partial local list as a complete cloud lineage. A foreign, deleted or unavailable target shows the usual unavailable state without echoing hidden record metadata.

## HTTP contract

`GET /v1/sessions/{session_id}/replacement-links?cursor={opaque}&limit={n}` requires the same active owner, current generation and token-family policy as ordinary session reads. The base session must be owned, have an accepted snapshot and have server state `processing`, `completed` or `invalid` (finalization has frozen the snapshot); otherwise return non-enumerating 404 or `409 SNAPSHOT_NOT_AVAILABLE` for an owned draft. It does not widen the existing strict session/list DTOs. `limit` defaults to **20** and accepts **1–100**; cursor input is limited to **1,024 ASCII characters**. The response has exactly:

```text
schema_version: "1.0.0"
session_id: UUID of the requested base
data_generation: positive safe integer of the current owner
base_snapshot_sha256: exact accepted base snapshot SHA-256
previous: {session_id: UUID, created_at: UTC, state: State} | null
items: [{session_id: UUID, created_at: UTC, state: State}]
next_cursor: opaque string | null
```

`State` is one of `processing`, `completed`, or `invalid`, matching the base service check-state vocabulary. A completed check is not a claim of clinical normality; its ordinary detail result preserves measurement-only/inconclusive semantics. `previous` is the directly superseded check when it is still owned, in the same generation, and has an accepted frozen snapshot in one of those three states; otherwise null. `items` contains only directly replacing, currently owned, same-generation checks with accepted frozen snapshots in one of those three states. An uploaded draft snapshot remains mutable and SHALL be excluded until finalization. Every linked `created_at` is the linked immutable snapshot's acquisition time, never the time a history row was fetched or a result reevaluated. No report values, profile fields, device identifiers, report revisions or unrelated descendants appear in this route.

## Integrity, pagination and bounded work

The relationship is the server-owned immutable `Check.supersedes_id`, verified against the accepted snapshot's `supersedes_session_id`. Sort directly replacing records by their immutable service creation key descending and UUID descending for a stable keyset page. The service exposes each record's acquisition time separately; this ordering is not a physiological comparison. Requesting the next page cannot disclose another parent's children: cursor identity is bound to the current account, generation and requested parent, its finite creation key and UUID. Malformed, oversized, wrong-parent or wrong-generation cursors fail with `422 INVALID_CURSOR`; a deleted/retired owner still fails before cursor resolution. Cursor values confer no authority and are always intersected with current ownership predicates.

The query uses an index on `(account_id, generation, supersedes_id, created, id)` and fetches at most `limit + 1` relationship rows. The direct predecessor is one owned lookup. Each returned relation verifies both stored IDs and snapshot links and cannot point back to itself. Corrupted relations fail closed with `409 REPLACEMENT_LINK_INTEGRITY`; a removed predecessor is treated as unavailable rather than a new current record. There is no recursive traversal, unbounded history download or metadata-derived cross-account lookup.

## Acceptance evidence

Before source closure, verify a replacement-to-original link, multiple original-to-replacement pages with tied timestamps, no duplicates between pages, exact current-generation filtering, another-account and deleted-parent refusal, cursor parent/generation mismatch and bounds, draft exclusion, immutable acquisition-time rendering, corrupted relation rejection, and mobile rejection of stale scopes or inconsistent base hashes. These tests establish navigation/integrity only; they do not qualify new physical acquisition or clinical results.

## Adversarial review disposition

The mobile implementation reviewer raised **RLINK-001 (High)**: snapshot presence alone admitted an uploaded draft that could still change through the draft snapshot PUT route, contradicting immutable navigation. The contract now requires base and linked server states `processing`, `completed` or `invalid`; owned drafts receive `409 SNAPSHOT_NOT_AVAILABLE`, and draft predecessors/children are excluded. The read-only owner/generation/hash and bounded cursor rules remain. This is specification resolution before code; acceptance execution is recorded with implementation evidence.
