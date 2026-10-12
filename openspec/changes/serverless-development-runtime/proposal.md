## Why

A separate serverless development feature was merged while the release/browser follow-up was being verified. Its Aurora/Lambda runtime, client deadlines, cost evidence and deployment workflow require their own fine-grained contract and adversarial review. The canonical signed QA/prod deployment and recovery path remains separate.

## What Changes

- Specify development-only runtime identity, current-source admission and bounded cost inputs.
- Fence every SQL producer and close acquisition atomically before draining for maintenance.
- Verify exact maintenance operation/outcome and deployed function identity.
- Preserve explicit guest isolation, bounded client deadlines and actual transport limits.
- Document private operator access and unimplemented serverless restore integration without calling it production qualification.

## Impact

Affected software includes deploy/serverless.py, its template/workflow, serverless control/lifecycle/worker modules, configuration, mobile deadlines and the guarded guest exporter. The external serverless merge is retained; fixes preserve its intended low-volume development scope. Actual AWS access, cloud transport, backup/restore and qualification are not established by unit doubles or existing LocalStack checks.

## Verification

Strict validation, independent source review and meaningful positive/refusal regressions precede the complete current-source local and GitHub gates. No mandatory check may be skipped or weakened. Actual main enforcement remains required independently from passing workflow files.
