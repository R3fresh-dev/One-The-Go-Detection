# Canonical cloud deployment and customer browser access

## Why

PRD-025, HLD §7, LLD service boundaries and the customer's explicit deployment request require an executable local → AWS QA → AWS production path. Existing canonical infrastructure hosts the API but has no independently served web artifact, named one-command environment entry points, or UI CNAME operation. Source synthesis is not evidence of an actual deployment.

## What Changes

- Add private versioned static web S3 hosting through CloudFront origin access control, exact browser OAuth callbacks, response security headers and optional custom TLS/DNS.
- Add exact-source Expo web builds, independently signed manifest/archive evidence, immutable publication and public HTTPS transport checks.
- Add separate QA and production Python entry points for infrastructure/security/code, stopped maintenance deployment, independent journal bootstrap verification, migration/recovery, health activation and browser publication.
- Add a bounded Route 53 CNAME operation targeting only the actual admitted distribution and document customer access, operator inputs, receipts, recovery, and remaining external evidence.

## Capabilities

### New Capabilities

- `cloud-browser-delivery`: browser artifact provenance, private hosting, secure origins, publication and customer access boundaries.
- `cloud-release-orchestration`: environment-specific entry points, exact release admission, maintenance sequencing, health gates and DNS changes.

### Modified Capabilities

None. This delta references the existing production-mobile-platform capability set and preserves its initial measurement-only release and native capture boundaries.

## Impact

Code changes are confined to canonical `infra/` and `deploy/`. One additional retained S3 bucket and CloudFront distribution affect cost estimates. Cloud credentials, real DNS/ACM, signing authority, successful exact-revision GitHub gates, QA acceptance, and platform store/simulator credentials remain external inputs. This change does not publish to an app store or certify assay, camera, BLE, model, restore, IAM/KMS or physical-device performance.
