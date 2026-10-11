## ADDED Requirements

### Requirement: AND-PREV-001 Accept fictional hosted mode only in local builds
The build SHALL accept EXPO_PUBLIC_HOSTED_PREVIEW=true only with APP_ENV=local and a matching compiled public environment. QA and production MUST reject the flag. Hosted native artifacts SHALL carry the same accepted mode as inspectable platform metadata, and their publication SHALL require reviewed workflow provenance.

#### Scenario: Production enables the preview flag
- **GIVEN** APP_ENV=prod
- **WHEN** the hosted preview flag is true
- **THEN** configuration fails before building application code.

#### Scenario: An isolated local preview is packaged
- **GIVEN** APP_ENV=local and the matching compiled public environment
- **WHEN** the hosted flag is accepted and the reviewed workflow packages the app
- **THEN** its bundle and platform metadata identify fictional hosted mode and account and real acquisition services remain disabled.

### Requirement: AND-PREV-002 Disable every account and real acquisition path
The standalone preview SHALL run without AWS, OAuth, a backend or Metro. It MUST skip credential recovery, deny API requests/downloads before credential or network access, hide account controls, and avoid camera, Bluetooth and native reaction acquisition. Fictional examples SHALL state their provenance and MUST NOT imply physiological measurement or a clinical result.

#### Scenario: A customer saves a browser example
- **GIVEN** the standalone fictional preview
- **WHEN** the customer acknowledges the notice, confirms context and saves a check
- **THEN** the UI shows a measurement-only fictional record with no account, sensor or upload calls.

#### Scenario: A credential or hardware path is invoked directly
- **GIVEN** the standalone fictional preview
- **WHEN** a caller attempts sign-in, credential recovery, API download, Bluetooth discovery or native reaction acquisition
- **THEN** the request is refused before network or hardware access and no fictional record is promoted to a measurement.

### Requirement: AND-PREV-003 Isolate guest records and explain persistence
Preview records SHALL use a dedicated fictional namespace, never migrate or import into an account, and contain no participant data. Browser records SHALL remain memory-only and clear on reload; hosted native records SHALL remain isolated local fictional data. The persistent preview banner SHALL explain these limits.

#### Scenario: The browser reloads after saving an example
- **GIVEN** a fictional saved browser check
- **WHEN** the page reloads
- **THEN** its records and acknowledgment disappear and the first-use fictional flow returns.

#### Scenario: A guest example is selected for account upload
- **GIVEN** a saved check in the isolated fictional guest namespace
- **WHEN** a caller attempts account migration, import or upload
- **THEN** the operation is refused and the account namespace receives no guest data.
