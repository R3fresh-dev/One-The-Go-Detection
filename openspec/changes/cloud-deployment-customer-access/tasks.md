## Evidence reconciliation — 2026-10-25

Current `deploy/` release tooling, cloud infrastructure, browser callbacks/CORS and immutable origin software are present. Checked tooling history is not executed AWS deployment or customer access. The ordinary shared web app supports authenticated accounts; isolated fictional `dist-preview` does not. All six unchecked verification/QA/production/browser/account/DNS external-evidence rows remain open; ENG-010 adds local authenticated browser evidence without deploying.

Current sources and exact bounded follow-up: [engineering author audit](../../../docs/factory/otgd-20261025-0555/reports/engineering-audit.md), [spec reconciliation](../../../docs/factory/otgd-20261025-0555/reports/spec-reconciliation.md), and [implementation plan](../../../docs/factory/otgd-20261025-0555/reports/implementation-plan.md). Checked history is preserved; unchecked implementation-plus-verification rows are **implemented-unverified** where source is present, **blocked** for unavailable execution/external inputs, and never silently completed. These author dispositions are not independent signoff.

---

## 1. Infrastructure and implementation

- [x] Add private versioned static web origin and CloudFront OAC/HTTPS/security headers.
- [x] Add exact browser callbacks/CORS and optional us-east-1 custom TLS/subdomain CNAME.
- [x] Add exact-source bounded ZIP/manifest construction, independent signing and immutable upload verification.
- [x] Add separate QA/prod one-command entry points and stopped maintenance/health/publication sequencing.
- [x] Require actual fresh independent journal-admission ECS evidence before activation and isolate cloud clients from inherited emulation endpoints.
- [x] Add an actual-target CNAME preview/apply operation with bounded propagation wait.
- [x] Document credentials/configuration/receipt/browser access and external acceptance limits.

## 2. Verification and release evidence

- [ ] Pass strict OpenSpec validation and independent adversarial source review.
- [ ] Pass expanded CDK and deployment negative unit tests in mandatory CI for the final revision.
- [ ] Deploy with actual supplied AWS accounts, DNS/issued ACM and trusted signing authority.
- [ ] Execute authenticated browser ATDD and all QA operational probes for the exact image and signed web artifact.
- [ ] Sign actual reviewed QA approval and promote/validate production with independent account inputs.
- [ ] Exercise worker replacement, deletion-journal recovery, rollback and alarms in real AWS.

No unchecked live-evidence task is implied complete by implementation, fixtures, synthesis or a plan output.
