## ADDED Requirements

### Requirement: SBR-001 Preserve one bounded client operation deadline
The explicit serverless client flag MAY select longer bounded cloud request/download deadlines; refresh, stream reads and cancellation SHALL retain the original operation deadline and owned abort control. It SHALL not enable hosted account/sensor/inference capabilities, override configured identity or admit serverless mode for local/test configuration.

#### Scenario: A serverless request refreshes authentication
- **GIVEN** its original bounded deadline and an authentication refresh
- **WHEN** the request continues
- **THEN** its remaining budget is not reset and cancellation still aborts owned work.

#### Scenario: A guest or local client inherits a cloud flag
- **GIVEN** local/test/hosted configuration
- **WHEN** capabilities are resolved
- **THEN** cloud deadlines cannot enable account, hardware or model access.

### Requirement: SBR-002 Pin guest serverless mode to false
The guarded guest exporter and checked preview receipt SHALL explicitly set serverless=false together with their fixed local/unavailable account configuration, independent of inherited cloud flags or dotenv. Missing/true receipt fields or stale output SHALL refuse startup; ordinary exports and unrelated servers SHALL remain preserved.

#### Scenario: The shell was configured for cloud serverless
- **GIVEN** inherited serverless=true and cloud origins
- **WHEN** a guest export is built and served
- **THEN** its checked configuration remains local guest/serverless=false with no account or sensor calls.

#### Scenario: A manifest omits or changes the field
- **GIVEN** missing/true serverless evidence
- **WHEN** startup checks the export
- **THEN** it refuses rather than relabeling it as a guarded guest.

### Requirement: SBR-003 Report actual public transport bounds
Delivery documentation SHALL distinguish the configured sixty-second CloudFront first-header/idle origin bound from longer streaming and client lifetimes. Actual cold/resumed-database HTTPS acceptance SHALL precede transport/latency qualification; a successful template or extended client timer SHALL not claim that a late first header is supported.

#### Scenario: Streaming lifetime is described
- **GIVEN** a longer Lambda/API streaming limit and sixty-second origin read timeout
- **WHEN** delivery limits are reported
- **THEN** first-header and body/client budgets remain distinct.

#### Scenario: Cold cloud transport has not run
- **GIVEN** only software/template checks
- **WHEN** readiness is reported
- **THEN** actual resumed-database HTTPS behavior remains unexecuted evidence.
