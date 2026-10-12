## ADDED Requirements

### Requirement: PREVIEW-001 Build an isolated fixed-origin guest export
Codespaces SHALL build the canonical fictional guest export in dist-preview with no dotenv and fixed unavailable API/issuer/account-client values. It SHALL clear Metro cache and preserve ordinary dist. Its manifest SHALL identify fictional browser-memory-only guest operation with account, sensor, upload and inference services unavailable.

#### Scenario: Ambient production values are present
- **GIVEN** a host or dotenv containing production API/OAuth configuration
- **WHEN** the preview is prepared
- **THEN** only explicit guest configuration enters its separate bundle.

#### Scenario: An ordinary export also exists
- **GIVEN** dist and dist-preview from different modes
- **WHEN** the preview starts
- **THEN** the guest server uses only dist-preview and its matching manifest.

### Requirement: PREVIEW-002 Verify the correct preview before reuse
Post-start SHALL check the actual guest manifest and exported application before starting/reusing its private forwarded server; an unrelated HTTP 200 service SHALL not count as ready. Startup SHALL be bounded and leave a concrete diagnostic on failure, without killing unrelated processes or presenting a fabricated hosted URL.

#### Scenario: A correct private guest server is already running
- **GIVEN** matching prepared guest bytes/manifest on the forwarded port
- **WHEN** post-start runs again
- **THEN** it reuses the verified server without duplicate processes.

#### Scenario: A foreign service occupies the port
- **GIVEN** ordinary/unrelated HTTP 200 content or a missing guest export
- **WHEN** post-start runs
- **THEN** it refuses readiness and preserves the unrelated service.

### Requirement: PREVIEW-003 Document actual click-only hosting boundaries
Documentation SHALL give the reviewed Codespaces branch/create/Ports browser flow and verified Appetize APK/iOS simulator ZIP upload steps, require genuine service access, and distinguish prepared/local validation from an actual hosted launch. It SHALL explain fictional data and store/physical-device limitations and SHALL not expose loopback URLs as user previews.

#### Scenario: A user has the supported service account
- **GIVEN** the reviewed branch and successful source-bound guest artifacts
- **WHEN** the documented browser hosting steps are followed
- **THEN** no local clone/build commands are needed to explore the fictional UI.

#### Scenario: No hosting access exists
- **GIVEN** no managed forwarding capability, existing Codespace or Appetize credentials
- **WHEN** delivery is reported
- **THEN** it supplies setup/artifacts and concrete account steps without claiming a launched session.
