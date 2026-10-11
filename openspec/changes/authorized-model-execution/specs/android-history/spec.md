## MODIFIED Requirements

### Requirement: AND-HIST-003 Faithful state, qualifier, and time display
History SHALL preserve canonical and original units, assay basis, qualifiers, collection and analysis times, quality and source. Missing or censored values SHALL never become zero. The new reader MAY display an independently verified 1.1.0 research record with its historical target and population; legacy-shaped estimates SHALL remain unsupported. History SHALL never imply a current sobriety assessment.

#### Scenario: Historical approved research result
- **WHEN** a fully verified 1.1.0 research record is opened after its acquisition date
- **THEN** history preserves its target and evaluation dates and labels the historical research scope

#### Scenario: Legacy or unapproved claim
- **WHEN** a legacy result, local preference or valid-looking manifest claims research authority without current complete admission
- **THEN** no score is admitted and the historical measurement-only or unsupported-result boundary remains in force

