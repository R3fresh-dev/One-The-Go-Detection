## ADDED Requirements

### Requirement: SCTL-001 Acquire producer leases before every SQL access
Each serverless producer SHALL acquire its admitted lease before any SQL, including initial/no-due sweep scans and SQL-backed metrics. It SHALL retain the lease until database connections are disposed. Failed acquisition SHALL prevent SQL; failed disposal SHALL not falsely release the drain fence.

#### Scenario: A sweep finds no due work
- **GIVEN** an admitted runtime and no due records
- **WHEN** it scans or emits SQL-backed metrics
- **THEN** its lease precedes SQL and remains until disposal.

#### Scenario: Maintenance or disposal blocks progress
- **GIVEN** refused acquisition or failed connection disposal
- **WHEN** a producer runs
- **THEN** it respectively opens no SQL or retains its fence rather than claiming drainage.

### Requirement: SCTL-002 Close acquisition atomically before drainage
Deployment SHALL close runtime admission atomically before treating lease drainage as maintenance readiness. Every producer acquisition SHALL condition on current admitted state/generation. An invocation already initializing when concurrency becomes zero SHALL not acquire later and access SQL after a closed empty snapshot.

#### Scenario: An old invocation reaches acquisition after closure
- **GIVEN** a producer initialized before deployment closed admission
- **WHEN** it attempts its lease after closure
- **THEN** acquisition refuses before SQL.

#### Scenario: A producer was leased before closure
- **GIVEN** an existing active producer and closed admission
- **WHEN** deployment waits for drainage
- **THEN** it waits for the actual retained lease/disposal rather than an earlier empty observation.

### Requirement: SCTL-003 Allow only deliberately owned maintenance
Closed admission SHALL permit only the explicitly owned maintenance phase; ordinary API/queue/sweep producers SHALL remain denied. Reopening SHALL follow exact successful maintenance/admission and the intended current generation. Missing/incompatible deployed protocol SHALL fail closed rather than assuming older producers honor new metadata.

#### Scenario: Supported closed and drained runtime enters maintenance
- **GIVEN** the supported protocol and exact owned maintenance phase
- **WHEN** the intended maintenance function acquires authority
- **THEN** maintenance proceeds while ordinary producers remain blocked.

#### Scenario: The existing runtime lacks the protocol
- **GIVEN** an unsupported/missing deployed admission version
- **WHEN** automated quiescence or upgrade is attempted
- **THEN** it refuses without declaring a safe drain or resetting retained state.
