# Participant instruction authority

Scope: Android and iOS approved instruction presentation and declared compliance before participant acquisition. This capability completes AND-HR-002, AND-ECG-002 and AND-SAL-001 without granting physical or scientific qualification. The [engineering design](../../design.md) preserves exact configuration, consent, start, privacy and evidence contracts.

## ADDED Requirements

### Requirement: PAI-001 Release exact bounded participant instructions
Participant acquisition SHALL resolve immutable typed instructions and permitted context/form rules from its current independently released configuration. The full configuration digest SHALL cover the protocol's text, version, digest, required confirmations and setup rules. Missing or changed instructions SHALL block that acquisition until explicitly reviewed and acknowledged.

#### Scenario: Current approved pulse instructions
- **GIVEN** an owned check with a currently released PPG configuration and protocol
- **WHEN** the participant opens approved capture
- **THEN** the app presents the exact approved rest/posture/contact instructions and their version without inventing a default procedure.

#### Scenario: Same scientific material with different instruction text
- **GIVEN** unchanged numerical material but a new instruction document or required confirmation
- **WHEN** old configuration or acknowledgment identity is used
- **THEN** current admission rejects it; matching the material digest alone cannot restore authority.

### Requirement: PAI-002 Bind an immutable acknowledgment to current scope
The service SHALL issue an immutable receipt for the owned draft/attempt, current generation/consent and exact released configuration/protocol. Acknowledgment SHALL be no more than the approved 1–300 seconds old, no earlier than attempt creation minus 5 seconds and at most 5 seconds ahead of server time. Original client and server acceptance times SHALL remain distinct; freshness uses their minimum and SHALL expire only after the approved bound.

#### Scenario: Explicit participant acknowledgment
- **GIVEN** the exact current protocol and all its required declarations have been presented for the admitted attempt
- **WHEN** the participant confirms them
- **THEN** the server returns a scoped immutable receipt retaining the exact request identity and distinct declared-compliance and acceptance times.

#### Scenario: Foreign or stale acknowledgment
- **GIVEN** a receipt from another account, retired generation, attempt, study or configuration, or outside admitted freshness
- **WHEN** acquisition is requested
- **THEN** the service refuses without creating hardware-start authority or rewriting the receipt's scope/time.

#### Scenario: Exact acknowledgment-age boundary
- **GIVEN** the approved maximum age is A seconds and the minimum of the original client acknowledgment and server acceptance times is T
- **WHEN** fresh authority is evaluated at T+A and then at any later instant
- **THEN** the age check admits the exact boundary subject to all other gates and rejects the later instant; retry or server receipt replay never replaces T.

#### Scenario: Future or pre-attempt declaration
- **GIVEN** a declaration is over 5 seconds ahead of the service or earlier than its attempt's creation minus 5 seconds
- **WHEN** acknowledgment is submitted
- **THEN** the service rejects the time claim instead of correcting it into current acceptance.

### Requirement: PAI-003 Re-admit instructions at every fresh start
Every participant acquisition start SHALL require a fresh online grant whose immutable authority binds the matching instruction receipt and full configuration scope. The service SHALL recheck current account, consent, protocol, configuration and applicable device authority at grant and start. Receipt replay or cached availability SHALL not bypass current admission.

#### Scenario: Exact receipt and current single-use start
- **GIVEN** the current attempt's accepted instruction receipt and independently qualified acquisition prerequisites
- **WHEN** its fresh grant is consumed within the admitted interval
- **THEN** start authority pins that receipt and permits only the exact channel/context/configuration and device origin where required.

#### Scenario: Withdrawal after acknowledgment
- **GIVEN** instructions were acknowledged before consent withdrawal or configuration retirement
- **WHEN** the participant tries the old grant or a new start
- **THEN** current admission refuses, and any local pending capture remains stopped.

#### Scenario: Receipt expires before Start
- **GIVEN** accepted instructions expire before grant issuance or consumption
- **WHEN** the participant selects Start
- **THEN** acquisition remains stopped and the app requires explicit current instruction presentation and new confirmation; historic receipt replay cannot renew its age.

#### Scenario: Declared strict signed wire format
- **GIVEN** the immutable server authorization pins the exact instruction receipt and configuration/context digests
- **WHEN** the signed authorization is verified by its matching declared wire schema
- **THEN** the authorization ID resolves only that immutable scope; explicitly declared direct receipt fields must match, unknown fields remain refused and an older strict reader cannot be treated as compatible by dropping signed fields.

### Requirement: PAI-004 Distinguish declarations from measured safety proof
Participant declarations SHALL not establish independent safety approval or observed hardware state. Human ECG SHALL require its independently reviewed permitted power/charging/cable/isolation configuration and supported current state evidence. Missing state verification SHALL keep human connection unavailable; a participant checkbox, bench scope or device confidence SHALL not satisfy that gate.

#### Scenario: Declared posture with independent device admission
- **GIVEN** an approved PPG protocol and independently admitted hardware
- **WHEN** the participant records its permitted posture/activity declarations
- **THEN** evidence labels those values as declared context and preserves separate actual device provenance.

#### Scenario: Checkbox substitutes for ECG power observation
- **GIVEN** a human ECG setup requires observed USB/charging state but the installed adapter cannot supply it
- **WHEN** the participant confirms a power or safety statement
- **THEN** human-connected capture remains unavailable with the missing verifier identified; no safety proof is fabricated.

#### Scenario: Bench scope cannot become human scope
- **GIVEN** an explicitly permitted simulator/bench configuration
- **WHEN** it is used to claim human-connected eligibility
- **THEN** service and client reject the scope substitution even if all participant confirmations are true.

### Requirement: PAI-005 Preserve acknowledgment retry and replacement identity
The client SHALL durably retain the exact acknowledgment body, timestamp and idempotency key before sending. An unknown outcome SHALL retry unchanged and reconcile the exact receipt. A newer protocol, attempt or owner SHALL require explicit fresh confirmation. Delayed callbacks SHALL not replace a newer intent or revive old start authority.

#### Scenario: Accepted response is lost
- **GIVEN** the server accepted acknowledgment but its response was lost
- **WHEN** the client reconnects
- **THEN** it retries the original body/key, verifies the matching immutable receipt and separately obtains current start authority.

#### Scenario: Replacement during receipt persistence
- **GIVEN** an old receipt response is delayed while the owner, attempt or retained intent changes
- **WHEN** that callback runs
- **THEN** scope and keyed-intent guards preserve the replacement and reject old acceptance; no old timestamp is rewritten as a fresh acknowledgment.

### Requirement: PAI-006 Stop before privacy and lifecycle transitions
Cancel, Back, withdrawal, account/generation change and prohibited interruption SHALL stop local capture acceptance before confirmation or navigation. Pending instruction/start work SHALL be fenced to its originating attempt/workspace. A late accepted receipt SHALL not resume an interrupted collection or device capture, including after Keep draft.

#### Scenario: Withdrawal while grant is pending
- **GIVEN** current instructions were confirmed and start is awaiting a network response
- **WHEN** withdrawal is requested
- **THEN** local acceptance stops immediately, privacy intent remains durable and the later grant cannot invoke hardware.

#### Scenario: Keep draft after cancellation
- **GIVEN** an admitted attempt was interrupted before completion
- **WHEN** the customer keeps the draft and revisits it
- **THEN** prior attempt/instruction evidence remains immutable and any new collection requires a separately admitted current start.

### Requirement: PAI-007 Show capability and provenance truthfully
Customer text and OS permission descriptions SHALL distinguish installed conditional capture, currently admitted authority, fictional data, declared context and unqualified physical timing. Measurement cards SHALL derive labels from actual source. A software-unavailable label SHALL not conceal a shipped conditional adapter, and installed code SHALL not imply a seeded approved human configuration.

#### Scenario: Conditionally admitted optical or ECG evidence
- **GIVEN** the installed adapter has current authority or a saved non-simulated signed measurement
- **WHEN** its screen or metric is rendered
- **THEN** copy describes that exact capability/source and retains the unresolved physical-onset or safety limitations.

#### Scenario: Guest or missing qualification
- **GIVEN** a fictional guest or account without a qualified configuration
- **WHEN** acquisition or permission information is displayed
- **THEN** fictional/unavailable limits remain explicit and no protocol checkbox or public flag enables participant sensing.

### Requirement: PAI-008 Guide declared cardiac rest without clock shortcuts
The client SHALL begin the owned attempt before guiding its approved 0–3600-second rest and SHALL use monotonic elapsed time before enabling rest confirmation. Interruption/background, attempt/workspace replacement or clock discontinuity SHALL invalidate the preparation and require fresh guidance. Retained UTC rest times and posture/activity/contact choices SHALL remain declarations, never measured compliance or electrical-state evidence.

#### Scenario: Approved rest interval completes
- **GIVEN** the current cardiac protocol requires R seconds of rest and the current owned attempt has begun
- **WHEN** foreground monotonic elapsed time reaches R without interruption and the participant explicitly confirms all approved declarations
- **THEN** the app may submit the exact preparation acknowledgment and retains its original UTC rest-start and confirmation times as declared context.

#### Scenario: Background or wall clock advances during rest
- **GIVEN** preparation is incomplete or its wall clock becomes inconsistent with retained monotonic elapsed time
- **WHEN** the app backgrounds, the workspace changes or the clock advances enough to appear complete
- **THEN** it cannot enable early Start; it clears current preparation authority and requires new foreground guidance and explicit confirmation.

#### Scenario: Zero-duration approved preparation
- **GIVEN** the independently released protocol explicitly requires zero seconds of rest
- **WHEN** the owned attempt and exact setup instructions are presented
- **THEN** the timer introduces no invented delay but every required participant declaration and independent hardware/safety gate remains mandatory.
