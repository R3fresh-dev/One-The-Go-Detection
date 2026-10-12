## MODIFIED Requirements

### Requirement: WEB-DEP-007 Enforce browser security headers
Delivery SHALL set and verify no-sniff, frame denial, long-lived HSTS, no-referrer and the complete supported CSP on both index and deep-link HTML. CSP SHALL restrict scripts/default/font/base to self, object/frame ancestry to none, image sources to self/data, style sources to self with documented inline allowance, and connections to self plus the exact API/hosted OAuth/issuer origins. Duplicate, missing, wildcard or weakened directives SHALL refuse verified-access receipts.

#### Scenario: Public transport probes execute
- **GIVEN** a published admitted artifact and the full supported response policy
- **WHEN** index, assets and the history route are retrieved over verified HTTPS
- **THEN** exact byte digest/size and all required transport/CSP controls verify.

#### Scenario: A policy fragment hides a weaker route
- **GIVEN** a missing referrer directive, wildcard script/connect source, duplicate CSP directive or unprotected history response
- **WHEN** public verification runs
- **THEN** it fails without a verified-access receipt.

#### Scenario: A public response exceeds the signed file
- **GIVEN** an oversized or unexpectedly encoded HTTP response
- **WHEN** verification streams the response
- **THEN** it refuses at the expected-size boundary without allocating the full untrusted body.

## ADDED Requirements

### Requirement: WEB-DEP-009 Verify the actual complete private release route
Publication and CNAME admission SHALL inspect the actual enabled/deployed CloudFront configuration, binding its single HTTPS viewer route to the admitted regional S3 bucket, exact releases/releaseId origin path, empty OAI and actual S3 SigV4 always-signing OAC. Extra origins/cache behaviors/origin groups SHALL be refused. Archive hash and member verification SHALL use the same bounded stable snapshot under existing 256-member, 16-MiB-member and 128-MiB archive/expanded limits.

#### Scenario: The supplied infrastructure matches the release
- **GIVEN** the actual one-origin OAC distribution and unchanged signed archive
- **WHEN** publication or DNS admission runs
- **THEN** routing and every archive member match the admitted release before mutation.

#### Scenario: A secondary route escapes the admitted origin
- **GIVEN** a foreign assets behavior, extra origin/group, wrong prefix, disabled distribution or non-always-signing OAC
- **WHEN** admission runs
- **THEN** it refuses publication and DNS changes.

#### Scenario: An archive changes during verification
- **GIVEN** a special/oversized/replaced archive or mismatching member/digest
- **WHEN** bounded verification executes
- **THEN** it fails before any public bytes are published.

### Requirement: WEB-DEP-010 Bound public response verification by signed bytes
Public HTTPS probes SHALL request identity encoding and stream each response under the admitted file's exact size plus an overrun sentinel. Index and history HTML SHALL match the signed index bytes; assets SHALL match their signed digest/size. Unexpected compression, oversized or changed bytes SHALL refuse verified-access receipts before an unbounded body allocation.

#### Scenario: The public release returns its exact artifact
- **GIVEN** the admitted published index/assets and matching identity responses
- **WHEN** the bounded transport probe executes
- **THEN** signed byte sizes and digests match, including the history fallback.

#### Scenario: The public response is unexpectedly encoded or oversized
- **GIVEN** compression or more bytes than the signed artifact
- **WHEN** the response is streamed
- **THEN** verification refuses at its bound without buffering the untrusted body.
