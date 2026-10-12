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
