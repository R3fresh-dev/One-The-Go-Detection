## MODIFIED Requirements

### Requirement: AND-DASH-001 Honest scope and provenance
The dashboard SHALL show the active workspace, actual admitted scope and synthetic provenance where applicable. Ordinary and guest workspaces SHALL remain measurement-only. The new binary MAY identify independently admitted research access without inferring it from sign-in. Latest results SHALL use their original acquisition time; missing channels SHALL remain unavailable.

#### Scenario: Admitted research workspace
- **WHEN** current authenticated authority admits the new research pipeline
- **THEN** the dashboard distinguishes authorized research access from demo and ordinary measurement work

#### Scenario: Legacy or unapproved claim
- **WHEN** a legacy result, local preference or valid-looking manifest claims research authority without current complete admission
- **THEN** no score is admitted and the historical measurement-only or unsupported-result boundary remains in force

