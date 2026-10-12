## ADDED Requirements

### Requirement: SDEV-001 Keep the runtime explicitly developmental
Serverless runtime SHALL require the named serverless-development profile, intended Ohio region and QA transport/authentication mode; production serverless mode or an absent/wrong profile SHALL refuse. That QA alias SHALL not substitute for canonical QA acceptance, signed production promotion or store release authority.

#### Scenario: The configured development stack starts
- **GIVEN** the exact profile/account/region and current admitted source
- **WHEN** its runtime settings load
- **THEN** development mode is explicit and normal cloud identity/TLS controls apply.

#### Scenario: Production or an ambiguous profile is supplied
- **GIVEN** serverless mode with production or a missing/wrong profile
- **WHEN** settings load
- **THEN** startup refuses before application access.

### Requirement: SDEV-002 Recheck source admission before mutation
Deployment SHALL require actual trusted current-main thirteen-job success for its exact source and recheck that authority before registry/image publication, stopping/updating runtime, maintenance and activation. A newer unfinished/failed run, changed source or substituted local passed array SHALL refuse further mutation without inventing rollback.

#### Scenario: Admitted source remains current
- **GIVEN** the exact completed current main run and unchanged source
- **WHEN** a mutation stage begins
- **THEN** actual admission is checked before that stage.

#### Scenario: Authority changes during rollout
- **GIVEN** a later failed/unfinished run or changed source
- **WHEN** the next stage is attempted
- **THEN** it stops and preserves actual prior-stage evidence.

### Requirement: SDEV-003 Bind cost parsing and hashing to one snapshot
Cost admission SHALL parse and hash the same stable bounded regular-file snapshot, validate the reviewed region/workload/rate assumptions and compare the estimate to the approved budget. File replacement, oversize or changed evidence SHALL refuse before deployment. A budget alert SHALL not be represented as a spending cap.

#### Scenario: Reviewed bounded estimate is supplied
- **GIVEN** unchanged matching cost evidence within the approved threshold
- **WHEN** admission executes
- **THEN** parsed values and recorded wire digest describe identical bytes.

#### Scenario: Evidence changes or exceeds its bound
- **GIVEN** a special/replaced/oversized cost file
- **WHEN** admission reads it
- **THEN** no unbounded second read or cloud mutation occurs.

### Requirement: SDEV-004 Preserve independent operator access
Each of the three distinct MFA registry operator roles SHALL retain exact required master-secret read and corresponding key-decryption access without trusting application runtime principals. Documentation SHALL identify the private database network prerequisite. Source/IAM assertions SHALL not claim that an operator's actual network/MFA session was exercised.

#### Scenario: A genuine operator uses its assigned role
- **GIVEN** the intended MFA role and separately prepared private network path
- **WHEN** its existing loader requests the exact database secret
- **THEN** IAM supplies the needed narrowly scoped access without combining human decisions.

#### Scenario: Runtime or foreign authority is supplied
- **GIVEN** an application principal or unrelated secret/key
- **WHEN** access is requested
- **THEN** operator trust is not inherited from deployment or runtime identity.

### Requirement: SDEV-005 Verify maintenance identity and outcome
Maintenance admission SHALL verify the expected deployed function/image/role/configuration/account/source and require the response's exact requested operation and operation-specific outcome. A successful status from another operation, no-op handler or stale deployment SHALL not admit bootstrap, migration or activation.

#### Scenario: The intended maintenance operation completes
- **GIVEN** the exact admitted function and matching operation evidence
- **WHEN** the caller verifies the response
- **THEN** only that operation's allowed success outcome advances its stage.

#### Scenario: An apparently successful foreign operation responds
- **GIVEN** bootstrap evidence returned for admission or a wrong handler/source
- **WHEN** verification runs
- **THEN** activation refuses despite a generic passed status.

### Requirement: SDEV-006 Preserve recovery limits and journal continuity
Serverless development SHALL preserve retained journals/data on failure and SHALL not establish a replacement journal to bypass continuity. Documentation SHALL distinguish its missing Aurora/Lambda restore integration from existing canonical ECS/RDS restore and from unexecuted live checks. Development receipts SHALL not authorize production promotion or claim completed recovery.

#### Scenario: A retained journal cannot be proven
- **GIVEN** existing data with missing/mismatched continuity
- **WHEN** deployment or maintenance runs
- **THEN** it refuses and retains prior state for reviewed recovery.

#### Scenario: Recovery capability is reported
- **GIVEN** only development deployment software and canonical restore tools
- **WHEN** readiness is documented
- **THEN** the separate serverless recovery integration remains explicit, without a fabricated restore result.

### Requirement: SDEV-007 Admit only empty first-attempt recovery
Initial infrastructure recovery SHALL require an exactly owned, fully rolled-back first creation, the exact supported reviewed stopped template, complete creation history, never-created and still-absent database/application functions, and empty retained bucket/multipart/control/identity state. Initialized or unsupported historical deployments SHALL refuse without replacing authority.

#### Scenario: An exactly empty first rollback is admitted
- **GIVEN** explicit initial-recovery authorization, the matching stopped template, complete first-creation history and verified empty retained authority
- **WHEN** recovery eligibility is checked
- **THEN** the exact initial-state plan is retained before any mutation.

#### Scenario: A database or application function was previously created
- **GIVEN** a database/function completion event, existing application resource, journal version/delete marker, multipart upload, control row or user
- **WHEN** initial recovery is planned
- **THEN** it refuses before detaching metadata and cannot establish a replacement journal.

#### Scenario: The original template uses an unsupported protocol
- **GIVEN** an original template that cannot be proven equal to the supported reviewed stopped deployment
- **WHEN** initial recovery is requested
- **THEN** it fails closed for separately reviewed recovery without relaxing identity checks or replacing retained authority.

### Requirement: SDEV-008 Import identical retained infrastructure
Recovery SHALL detach only failed stack metadata and import the exact surviving retained physical identities, with no resource replacement or journal reset. The actual change set SHALL contain each expected resource exactly once with only Import actions. Protected phase evidence SHALL precede mutation, preserve failures and report only observed infrastructure adoption without claiming rollback or SQL restoration.

#### Scenario: The exact retained resources are imported
- **GIVEN** an admitted empty plan and exact Import change set
- **WHEN** adoption completes and actual identities/status/protection are verified
- **THEN** the original resources remain and the receipt identifies only the completed infrastructure operation.

#### Scenario: The proposed import changes the resource set
- **GIVEN** an extra, missing, duplicate, foreign or non-Import change
- **WHEN** the actual change set is verified
- **THEN** import execution refuses, preserving actual completed-stage evidence.

### Requirement: SDEV-009 Refresh recovery admission and invariants
Recovery SHALL recheck current-source thirteen-job authority before every cloud mutation and reread retained-state and absent-application invariants before import execution and after adoption. Changed authority/state SHALL stop further mutation and retain the precise protected failure phase; an earlier empty snapshot SHALL not establish current success.

#### Scenario: Authority becomes nonempty during an AWS waiter
- **GIVEN** an initially empty plan and a later retained-state or application-presence change
- **WHEN** pre-execution or post-adoption invariants are reread
- **THEN** recovery remains failed rather than reporting the stale empty snapshot as current success.

#### Scenario: Main or its latest gate changes during recovery
- **GIVEN** earlier valid source authority followed by changed main or a newer unfinished/failed run
- **WHEN** another recovery mutation is attempted
- **THEN** admission stops that mutation and records the precise protected phase.

#### Scenario: Post-adoption state contradicts the plan
- **GIVEN** completed import metadata but changed retained identities, state or application presence
- **WHEN** final invariants are verified
- **THEN** recovery reports failure and preserves completed-stage evidence without claiming rollback.

### Requirement: SDEV-010 Verify the actual AWS account plan
Development deployment SHALL verify the selected STS account and its active Paid Plan before recovery or deployment mutation. A restricted Free Plan, wrong account, missing or malformed plan state SHALL refuse rather than silently selecting Aurora Express or a different architecture. Planning SHALL describe usage assumptions and shall not represent free credits or budget alerts as a spending cap.

#### Scenario: The selected account has an active Paid Plan
- **GIVEN** the exact selected account and observed active Paid Plan
- **WHEN** preflight evaluates the planned Aurora configuration
- **THEN** deployment can continue to its remaining admission checks without changing the architecture.

#### Scenario: The account has a restricted or unverified plan
- **GIVEN** a Free Plan, inactive state, wrong account or unavailable plan response
- **WHEN** preflight runs
- **THEN** it stops before deployment/recovery mutation and reports the actual prerequisite.
