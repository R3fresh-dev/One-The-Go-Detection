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

### Requirement: SBR-004 Bind browser upload CSP to the exact bucket
The serverless web Content Security Policy SHALL admit only the exact selected Ohio/account artifact-bucket HTTPS path, including its trailing slash, in addition to the admitted API and identity origins. Wildcard, neighboring bucket-prefix, foreign account/region or arbitrary output origins SHALL refuse. Canonical QA/prod web policy SHALL remain separately validated.

#### Scenario: The selected private upload path is served
- **GIVEN** the exact artifact bucket and current admitted web distribution
- **WHEN** the actual response security policy is verified
- **THEN** its upload network authority is restricted to that bucket path.

#### Scenario: An expanded upload origin is supplied
- **GIVEN** a wildcard, missing path separator, neighboring prefix or foreign origin
- **WHEN** policy verification runs
- **THEN** it refuses rather than broadening browser network authority.

### Requirement: SBR-005 Verify upload preflight and receipt visibility
Upload readiness SHALL require actual single-web-origin PUT CORS with the exact signed conditional/checksum/SSE headers, exposed ETag/version/checksum receipt headers and admitted cache duration. Positive and unapproved-origin OPTIONS probes SHALL verify the actual browser boundary. Preflight success SHALL not claim an object was uploaded or authenticated customer acceptance completed.

#### Scenario: The admitted web client preflights a signed upload
- **GIVEN** exact CORS methods, signed headers, exposed receipt fields and cache duration
- **WHEN** its actual preflight responds
- **THEN** the selected web origin is admitted and evidence remains scoped to preflight.

#### Scenario: Policy or origin does not match
- **GIVEN** a foreign origin, expanded policy or missing exposed receipt header
- **WHEN** actual CORS/preflight verification runs
- **THEN** upload readiness refuses without reporting a completed object transfer.
