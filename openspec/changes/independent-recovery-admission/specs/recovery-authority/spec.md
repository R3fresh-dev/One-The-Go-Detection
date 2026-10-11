## ADDED Requirements

### Requirement: RECOVERY-001 Independent retained admission
The system SHALL verify retained journal control, accepted deletion barriers and
latest recovery activation before API admission and nonprivacy worker leases,
computation and commits, regardless of database recovery flags.

#### Scenario: Consistent retained authority
- **WHEN** the database matches all pinned retained control, identity, generation, deletion and recovery evidence
- **THEN** ordinary service admission may proceed subject to current participant and study authority

#### Scenario: Stale restored active row
- **WHEN** a retained deletion or recovery activation conflicts with an active database row or its queued job
- **THEN** API and worker refuse new data work before commit, including when the database recovery row is absent

#### Scenario: Missing local establishment
- **WHEN** retained PostgreSQL is paired with a missing or replacement emulator journal
- **THEN** bootstrap and running service admission refuse silent establishment or account provisioning

### Requirement: RECOVERY-002 Scoped independent reapproval
The system SHALL keep global recovered scopes suspended and resume a study only
through its independently retained seal of fresh exact three-principal approvals
after activation plus fresh participant consent.

#### Scenario: Reapproved study
- **WHEN** every current registry dependency is freshly submitted, independently reviewed and released, and the exact study seal and participant consent are current
- **THEN** that study may collect through current qualified configurations while every unsealed study remains suspended

#### Scenario: Boolean or stale approval override
- **WHEN** a database flag changes, old approval or consent is reused, a seal disappears or a dependency is retired or changed
- **THEN** study capture and model execution refuse resumption

#### Scenario: Privacy cleanup during suspension
- **WHEN** nonprivacy admission fails while an accepted deletion needs safe object cleanup
- **THEN** privacy cleanup may continue without reopening data or removing independently retained deletion evidence
