## MODIFIED Requirements

### Requirement: AND-SET-004 Capability and environment integrity
About SHALL show the actual environment and account's currently admitted scope. Settings, deep links, preference files and public configuration SHALL never grant study, model, illumination or participant-upload authority. The new binary MAY expose server-admitted research availability; older binaries SHALL remain measurement-only. Production SHALL reject environment overrides and unsupported capability values.

#### Scenario: Authorized new binary
- **WHEN** the authenticated account has current independently released research and qualified channel scope
- **THEN** capability screens describe that conditional scope without presenting it as clinical validation

#### Scenario: Legacy or unapproved claim
- **WHEN** a legacy result, local preference or valid-looking manifest claims research authority without current complete admission
- **THEN** no score is admitted and the historical measurement-only or unsupported-result boundary remains in force
