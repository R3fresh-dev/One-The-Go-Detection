# Separate optional raw recording and fictional hosted preview

## Why

AND-STUDY-002, AND-EYE-006, AND-ECG-007, AND-PRIV-001/006, HLD §8 and LLD §10 require a recording purpose that is distinct from study acceptance. The customer must be able to decline raw acquisition, inspect retention and stop recording without confusing pending requests with completed deletion. A browser preview must also work without AWS credentials or a localhost API.

## What Changes

- Specify separate default-off device recording and explicit upload choices for eye video and ECG waveform, exact policy and notice review, immutable receipts and durable retries.
- Specify locally enforced revocation fences, independent server upload/retention states, pagination and physical cleanup receipts.
- Implement an isolated local fictional guest build with no account, network, sensor permission or native reaction-task path.
- Verify real returned API envelopes and real React Native Web DOM controls. Sensor qualification and clinical evidence remain separate requirements.

## Capabilities

### New Capabilities

- `raw-recording-customer-flow`: optional-purpose choices, receipt verification and stop/retention review.
- `fictional-hosted-preview`: standalone browser and hosted native guest UX without service credentials.

### Modified Capabilities

None. These requirements refine the existing production-mobile-platform study, privacy, eye and ECG requirements without changing their approval prerequisites.

## Impact

Canonical mobile client, raw-purpose API, worker cleanup, hosted artifact inspection and CI browser gates. Optional-purpose receipts do not implement an optical assay or imply approval of a capture device. The preview has no mechanism to import guest records into account workspaces.
