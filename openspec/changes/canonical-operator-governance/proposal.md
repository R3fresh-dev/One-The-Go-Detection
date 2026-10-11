# Canonical operator registry governance

## Why

CAN-01 identifies a canonical software gap: generic operator rows and constant
customer capability values do not implement the requested approved research
workflow. A customer must not manufacture authority, and an operator must not
silently rewrite submitted evidence or approve their own version.

## What changes

Add maintenance-only typed administration with immutable submissions,
independent review and release, expiry, retirement and revocation history.
Resolve current participant channel capability from actual approved records,
consent, device/calibration bindings and shipped software adapters. Preserve the
scientific task material digest separately from the complete registry envelope
digest. Add no real study, device, assay, timing qualification or model evidence.

## Impact

Canonical FastAPI domain/main integration, PostgreSQL additive migration 003,
maintenance CLI and generated operator schemas. Runtime credentials remain
read-only for authority records. The actual AWS IAM assignments and scientific
qualification are required external inputs, not inferred from unit fixtures.
