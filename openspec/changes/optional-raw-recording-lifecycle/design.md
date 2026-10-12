# Design

## Approved metadata and customer actions

Research access links an exact current study consent to Recording choices & retention. Before any optional recording choice, the customer sees the purpose, policy ID/version, independently verified JCS SHA-256, exact plain-text notice and UTF-8 hash, maximum days from the first owned acquisition start, authorization expiry, permitted roles, withdrawal behavior and explicit exceptions. No participant source-laboratory-report control exists.

Each eye_video/ecg_waveform purpose has two controls: Record on this device and Allow explicit upload. Upload requires recording, never toggles automatically, and still requires a distinct Upload action. Raw acquisition requires a fresh device/configuration grant in addition to the purpose receipt. New account, workspace generation, consent receipt, policy or notice remounts the form; unfinished checks do not transfer. Previously accepted choices are displayed only for the same exact current server tuple.

The raw-policy summary must match its full approved content, not merely carry a hash. Policy expiry is represented as UTC text in the summary and epoch seconds in the canonical body. The fixed retention basis is first_owned_acquisition_start. All consent and policy digests remain immutable.

## Persistence, retries and barriers

raw_preference is an ordinary protected mutation. The client persists the confirmed UTC timestamp, full choices, consent/policy/notice tuple and original idempotency key before transmission. A lost receipt replays that exact intent. The verified response includes the original immutable preference receipt. A fresh key does not silently replace an unresolved intent.

raw_revocation is a privacy intent with per-kind scope. It stops native acquisition before durable writes or network requests can delay hardware shutdown, fences recording locally, blocks dependent grant intents, persists the original key and can reconcile while offline or when ordinary writes are paused. Clearing local measurement records preserves outstanding privacy intents and stop fences. Late preference replies cannot publish after the queue barrier. Older completed receipts cannot clear a newer cleanup-pending fence.

Server status exposes immutable granted choices separately from effective choices. Effective choices may narrow a grant after revocation; they cannot widen it. Artifact upload_state and retention state are independent. cleanup_pending is never rendered as completed deletion; physical cleanup_completed_at and completed receipts provide that evidence. Each artifact page is bounded to 500, with an explicit next cursor. Revocation completion is determined against all targeted rows, not the current page.

## Fictional preview isolation

EXPO_PUBLIC_HOSTED_PREVIEW=true is accepted only in APP_ENV=local. The compiled public environment must agree with APP_ENV. Both config metadata and compiled constants use that same accepted flag. Browser export embeds public environment/origins because Expo Web may not provide native expoConfig.extra. Hosted native artifacts carry iOS OTGDHostedPreview and Android dev.r3fresh.otgd.HOSTED_PREVIEW markers; artifact inspection alone is not signed provenance, so a successful reviewed hosted workflow remains required.

The guest controller skips credential recovery and public-config fetches; its API rejects every request and download before credentials or fetch. Its native transport is unavailable, camera views/permission controls do not mount, and reaction acquisition is disabled. Fictional records use a separate namespace. Browser persistence is memory only and reload clears it; native fictional persistence is local and isolated. No guest import, account upload, clinical classification or driving-clearance statement is available.

## Verification boundaries

API-returned fixtures establish DTO agreement; controller tests exercise durable intent and delayed-reply races; React Native Web component tests exercise actual switches and remount behavior; hosted browser ATDD observes network and sensor calls while saving a check. These do not qualify camera timing, a real assay, firmware key custody, Apple signing or physical devices. Required merge gates run on the final revision and remain open until all requested categories actually pass.
