## MODIFIED Requirements

### Requirement: CLOUD-DEP-007 Register only the exact deployed UI CNAME
The DNS operation SHALL validate the admitted enabled/deployed private release distribution, public zone ownership, non-apex name, exact TLS alias and issued same-account us-east-1 certificate; it SHALL reject conflicting records and offer preview before explicit apply. An absent record SHALL use one atomic CREATE, never UPSERT; an equivalent existing record SHALL remain unchanged and report an observed no-op without inventing a change ID.

#### Scenario: A valid absent public subdomain is registered
- **GIVEN** a matching enabled private distribution, issued TLS and absent record
- **WHEN** apply is explicitly requested
- **THEN** one CNAME is created; successful change observation must occur within ten minutes, SDK timeouts/retries may delay failure reporting, and failure does not imply cancellation or rollback.

#### Scenario: A foreign record appears after preview
- **GIVEN** an absent lookup followed by another actor creating that record
- **WHEN** CREATE is submitted
- **THEN** AWS rejects the conflict, the foreign record is preserved and the command reports failure.

#### Scenario: The exact target already exists
- **GIVEN** the observed CNAME has the admitted target and supported record form
- **WHEN** apply is requested
- **THEN** no write occurs and the receipt identifies an observed equivalent record rather than fabricated propagation evidence.

#### Scenario: Caller supplies apex or foreign authority
- **GIVEN** a private/foreign zone, conflicting record, disabled distribution, wrong alias or certificate
- **WHEN** admission runs
- **THEN** no DNS mutation or successful registration receipt occurs.

## ADDED Requirements

### Requirement: CLOUD-DEP-011 Bound release authority and evidence inputs
Release tools SHALL read regular, non-symlink, stable bounded files without blocking on special files; enforce 8,192 bytes for PEM keys and the existing 48,000-byte signed JSON cap before decoding; and require current-user-owned single-link private keys without group/other access. Public trusted keys SHALL retain independent authority comparison. Limits SHALL apply before hashing/allocating artifacts.

#### Scenario: Genuine matching release authority is supplied
- **GIVEN** bounded stable regular key/evidence files and the matching independently trusted Ed25519 public key
- **WHEN** the actual release operation loads them
- **THEN** signature verification/signing uses those exact bytes and never logs key material.

#### Scenario: A file is special, replaced or exposed
- **GIVEN** a FIFO, symlink, oversized file, changed inode/metadata or broadly readable private key
- **WHEN** the reader is called
- **THEN** it refuses promptly before signing or cloud mutation.
