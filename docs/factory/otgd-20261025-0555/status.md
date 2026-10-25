# Factory status

As of: 2026-10-25T07:15:03.737802+00:00
Run: otgd-20261025-0555
Branch: factory/one-the-go-detection-20261025
Factory revision: 4770878e18e9c587c2961b9e2bb13315da31abe9

Implementation and preflight testing remain active. Product, engineering and specification audits are complete. Checkpoint 5 (8a7294db0bdf98fb2bc6c3a0a77dce62223170c0) is verified remotely; checkpoint 6 captures the shared live gates, updated dossiers and browser fixes.

All five canonical services are healthy. PostgreSQL and LocalStack IDs, both volumes and the deletion journal remain preserved. Source image C is adopted; the identity service additionally has the reviewed read-only CSP source overlay under D-007. The real worker interruption preflight runs in its isolated database/queues; five export and two result crash cases have executed, and stale-output cases are progressing. Its final source check must fail after the explicitly recorded identity-source change; a fresh frozen-candidate matrix is required.

The PostgreSQL preflight passed 1,361 tests and repeated migrations/runtime permission denials. The browser journey now reaches real PKCE, explicit upload, result, export, consent withdrawal, deletion and recovery on both viewports. Two demonstrated sign-in defects were fixed (OAuth state length and registered callback CSP). The latest run found logout revoking the provider family before the API can record its logout receipt; this newly demonstrated defect remains to repair. Test results are preflight evidence, not final acceptance.

Shared local/CI gates now require the live worker and browser checks. CI still has 14 mandatory jobs, with a 50-minute localstack job budget. Full frozen-source gates, current native CI, six independent reviews and final approval are pending. Native OS/device, scientific and release prerequisites remain explicit.

Root free space is about 1.46 GB and /tmp about 1.12 GB. No resize tool is exposed. No broad cleanup or data reset is authorized. Parent owns ten-minute supervision and fifteen-minute progress. Correction rounds: 0/2; PM crash recovery attempts: 0/3.
