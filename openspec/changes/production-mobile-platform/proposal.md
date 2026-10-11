# Production mobile platform

## Why

The existing HLD, LLD, and PRD establish the system boundaries but do not specify each customer interaction or provide deployable applications. This change turns them into fine-grained feature contracts and implements a shared Android/iOS application with a backend that can run against LocalStack locally and in isolated AWS QA and production environments.

## What Changes

- Specify each Android feature separately, including its iOS equivalent, screen flow, contracts, error recovery, security boundaries, and executable acceptance scenarios.
- Record an adversarial review of the entire specification before application implementation.
- Implement mobile workflows, native task timing, secure local persistence, identity, device integration, measurement-only result handling, and explicit cloud synchronization.
- Implement a modular FastAPI/PostgreSQL service, S3 artifact handling, SQS processing, account/data operations, and structured operational controls.
- Provide reproducible local services and AWS infrastructure, deployment configuration, promotion checks, and recovery procedures.
- Preserve the open assay, optical, ECG, study, and model qualification gates. Software must enforce these gates; it cannot invent the external evidence needed to close them.

## Capabilities

### New Capabilities

- `android-onboarding`: first-use explanation, notice acknowledgment, mode selection, and setup progress.
- `android-sign-in`: account authentication, token lifecycle, logout, and expired-session recovery.
- `android-profile`: optional demographic and use-history inputs with immutable versions.
- `android-dashboard`: next actions, device readiness, recent check, and honest status.
- `android-device-pairing`: discovery, association, trust state, disconnects, and diagnostics.
- `android-guided-check`: one-check orchestration, attempt identity, cancellation, and finalization.
- `android-saliva-measurement`: one collection, assay provenance, qualifiers, and unavailable channels.
- `android-eye-capture`: guided preview, qualified capture configurations, and missing/invalid measurements.
- `android-heart-rate`: resting pulse acquisition, contact quality, and source identity.
- `android-ecg-capture`: optional qualified ECG acquisition with simulator-first behavior.
- `android-reaction-task`: one native repeated-trial game and reproducible timing records.
- `android-results`: distinct result states, quality explanations, and historical time basis.
- `android-history`: authorized check lists, detail inspection, and immutable past results.
- `android-offline-sync`: encrypted persistence, explicit upload, retries, and reconciliation.
- `android-privacy-controls`: notice/consent boundaries, local erasure, and remote deletion requests.
- `android-settings-accessibility`: permissions, accessibility, configuration, and support diagnostics.
- `android-study-enrollment`: authorized study access and scoped capture/upload permission.
- `android-alcohol-channel`: separately labeled future alcohol measurements and unavailable state.
- `android-data-export`: user-requested exports, status, protected download, and expiry.
- `android-app-environment`: startup readiness, version support, local/QA/prod isolation, and service continuity.

### Modified Capabilities

None. This is the first OpenSpec capability set. The existing Markdown architecture and JSON contracts remain upstream references, with implementation extensions documented in design.md.

## Impact

New application code resides in apps/mobile; API, worker, and local identity code in services; infrastructure and deployment code in infra; acceptance checks in tests and tools. Root development tooling pins OpenSpec. The initial clinical state remains unvalidated and measurement-only. External prerequisites include the selected hardware, an appropriate LocalStack license/token, AWS accounts and DNS/TLS configuration, and platform signing credentials for distribution.
