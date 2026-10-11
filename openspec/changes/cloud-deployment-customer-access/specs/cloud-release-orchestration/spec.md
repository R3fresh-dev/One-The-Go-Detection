## ADDED Requirements

### Requirement: CLOUD-DEP-001 Provide separate environment entry points
The repository SHALL provide deploy/qa.py and deploy/prod.py, reject the opposite environment and provide a plan mode that validates inputs and lists stages without AWS/build/signing mutations.

#### Scenario: QA plan is requested
- **GIVEN** a concrete validated QA configuration
- **WHEN** qa.py --plan executes
- **THEN** it lists infrastructure/code/maintenance/web stages and reports deployment_executed=false.

#### Scenario: Production wrapper receives QA configuration
- **GIVEN** an environment mismatch
- **WHEN** the wrapper starts
- **THEN** it fails before AWS access or mutation.

### Requirement: CLOUD-DEP-002 Admit exact source and live release gates
Build, promotion and activation SHALL require the independently trusted release authority and successful live latest-attempt GitHub gate provenance for the exact committed source; local claims and skipped/failed/cancelled jobs SHALL not qualify.

#### Scenario: Every required exact-revision gate passes
- **GIVEN** an eligible main/merge-group run and independently trusted signature
- **WHEN** release operations execute
- **THEN** source/run/attempt/job/image bindings are verified and retained.

#### Scenario: A prior or cancelled run is supplied
- **GIVEN** stale or incomplete evidence
- **WHEN** admission executes
- **THEN** the operation fails before release authorization.

### Requirement: CLOUD-DEP-003 Orchestrate infrastructure and code with actual inputs
Execution SHALL verify STS account, TLS, regional database/cost inputs, bootstrap CDK/registry and deploy the admitted infrastructure/security and immutable service image; it SHALL not invent credentials, accounts, budgets, domain or certificates. Cloud SDK clients SHALL ignore ambient/profile service endpoints and reject explicit endpoint overrides; child commands SHALL remove endpoint environment overrides and force configured-endpoint ignore.

#### Scenario: Actual approved inputs are present
- **GIVEN** the configured credential chain and resource authority
- **WHEN** one environment command executes
- **THEN** its actual account/region is verified before infrastructure changes.

#### Scenario: AWS credentials point to another account
- **GIVEN** an STS mismatch
- **WHEN** preflight executes
- **THEN** no target deployment continues.

#### Scenario: Local emulation endpoint settings are inherited
- **GIVEN** global, service-specific or profile endpoint overrides
- **WHEN** cloud identity or mutation clients are constructed
- **THEN** their endpoints resolve to AWS and explicit endpoint overrides are rejected.

### Requirement: CLOUD-DEP-004 Complete maintenance before enablement
The command SHALL drain existing API/workers, deploy stopped, verify independent journal continuity, migrate in the exact private maintenance task, verify actual receipts and run required recovery before activation.

#### Scenario: First empty environment is established
- **GIVEN** explicit establish-new and no admitted data
- **WHEN** bootstrap/migration succeed
- **THEN** actual receipts qualify for the later activation gate.

#### Scenario: Migration or fresh admission verification fails
- **GIVEN** failed maintenance, absent authority or a stale/mismatching admission receipt
- **WHEN** deployment reaches the failure
- **THEN** activation and web publication do not execute and no success receipt is fabricated.

### Requirement: CLOUD-DEP-005 Require actual healthy activation
Activation SHALL reverify admitted release/maintenance/recovery authority, wait for stable services and require actual ECS worker progress health within ten minutes before browser publication.

#### Scenario: Worker dependencies make useful progress
- **GIVEN** dispatcher/cleanup/both consumers qualify
- **WHEN** ECS reports the worker container HEALTHY
- **THEN** publication may proceed after the remaining gates.

#### Scenario: A worker process runs without qualifying progress
- **GIVEN** UNKNOWN/unhealthy worker status
- **WHEN** the bounded health deadline expires
- **THEN** public enablement fails and is not called successful deployment.

### Requirement: CLOUD-DEP-006 Bind production to tested QA service and web evidence
Production SHALL preserve the approved QA source/image/lock in a separate account, verify unexpired independently signed QA approval, require its web_customer_access artifact reference to match the exact signed QA web envelope, and require a separate protected HTTPS/S3 authenticated customer-results reference as an explicit operator attestation.

#### Scenario: Approved QA is promoted
- **GIVEN** source service/web records and actual protected QA evidence
- **WHEN** the authority signs and production admission runs
- **THEN** production preserves the image/source and binds its separately configured web artifact to the approved QA envelope.

#### Scenario: Web evidence refers to another artifact
- **GIVEN** a foreign/missing web digest or expired QA approval
- **WHEN** production starts
- **THEN** it fails before target deployment.

### Requirement: CLOUD-DEP-007 Register only the exact deployed UI CNAME
The DNS operation SHALL validate the admitted distribution/release, public zone ownership, non-apex name, exact TLS alias and issued same-account us-east-1 certificate; it SHALL reject existing conflicting records and offer preview before explicit apply.

#### Scenario: A valid public subdomain is registered
- **GIVEN** a deployed matching distribution and issued TLS
- **WHEN** apply is explicitly requested
- **THEN** one CNAME targets that distribution and its actual change is awaited for at most ten minutes.

#### Scenario: Caller supplies apex, foreign zone or target
- **GIVEN** a mismatching zone/alias/certificate/record
- **WHEN** validation executes
- **THEN** no DNS mutation occurs.

### Requirement: CLOUD-DEP-008 Preserve immutable attempts and report actual checks
Every invocation SHALL preserve prior releases/receipts in a new ignored attempt directory, journal successful stage completions and exact failure stage/type with actual receipt paths/hashes in a bounded credential-free private state file, exit nonzero on any stage failure and print the recovery path, and write a final receipt only after actual public-byte/header/navigation/readiness checks; it SHALL not infer rollback from failure.

#### Scenario: An operator repeats deployment
- **GIVEN** prior reviewed records
- **WHEN** another invocation starts
- **THEN** a separate attempt retains earlier evidence and same-prefix object conflicts fail closed.

#### Scenario: Public access or invalidation fails
- **GIVEN** incomplete delivery
- **WHEN** the bounded operation fails
- **THEN** no verified-access receipt is written and cloud acceptance remains unresolved.

### Requirement: CLOUD-DEP-009 Provision distinct registry operator authority without assigning approvals
Infrastructure SHALL create separate named submitter/reviewer/releaser MFA operator roles with scoped role-ID/admin-secret access, no default human assignments or participant/runtime trust, and no generic task identity presented as a reviewer; actual three-human assignment and private operator access SHALL remain explicit account setup evidence.

#### Scenario: An authorized operator validates registry evidence
- **GIVEN** an approved private operator host with the actual named role and protected database credentials
- **WHEN** the typed CLI validates the corresponding command
- **THEN** STS/IAM identity and database authority are verified independently of participant API access.

#### Scenario: A deployed application task attempts an approval
- **GIVEN** a runtime database/task identity
- **WHEN** it attempts to administer or impersonate a registry operator
- **THEN** runtime write/trust permissions do not authorize the operation and no approval is invented.

### Requirement: CLOUD-DEP-010 Require fresh independent admission evidence
Activation SHALL require the exact recovery_authority module command without overrides, actual ECS completion within fifteen minutes, UTC receipt completion within sixty seconds of ECS completion, and matching account/region/source/image/task, regardless of recoveryRequired.

#### Scenario: Maintenance completes with current independent authority
- **GIVEN** migration and required recovery have completed with services stopped
- **WHEN** the exact pinned admission task verifies journal/control versions and database barriers
- **THEN** its fresh actual ECS receipt may qualify activation alongside the other release gates.

#### Scenario: Admission proof is stale or uses a no-op command
- **GIVEN** stale completion, mismatching bindings or a command that only mentions the module
- **WHEN** activation verifies the receipt against ECS
- **THEN** services are not activated using that evidence.
