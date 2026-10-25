# Verified release and browser access

## Why

The requested QA/prod Python deployment and web CNAME entry points already exist. Review found unsafe file/body reads, incomplete public security-policy verification, an insufficient distribution check and a check-then-UPSERT DNS race. Native store profiles do not yet describe concrete device artifacts, exact submissions or release receipts. Codespaces exports must be isolated from ordinary exports and ambient account origins.

## What Changes

- Harden bounded release-authority/evidence/archive reads and exact public HTTPS policy verification.
- Validate every CloudFront routing origin against the admitted release and create absent CNAME records atomically; preserve equivalent records without writing.
- Add platform-specific, exact-source store build/submission tooling with genuine account/signing inputs, deliberate non-public submission and truthful provider status.
- Serve an explicit fictional guest export in Codespaces and document click-only web/native preview, QA/prod/CNAME commands, store distribution and unresolved real instrument interfaces.

## Capabilities

### New Capabilities

- mobile-store-delivery
- fictional-browser-preview

### Modified Capabilities

- cloud-browser-delivery: complete response-policy verification and actual private release routing.
- cloud-release-orchestration: atomic conflict-safe CNAME registration and bounded authority/evidence loading.

## Impact

Canonical deploy tooling, mobile distribution configuration/scripts, devcontainer setup, release documentation and mandatory specification validation change. No account, domain, signing identity, vendor protocol, human approval or store publication is fabricated. Every changed revision requires fresh seven-category local evidence and GitHub evidence for every actual mandatory job in the exact committed aggregate and reusable workflows. Main protection remains a separately verified prerequisite.
