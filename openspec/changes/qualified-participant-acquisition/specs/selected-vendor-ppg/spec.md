# Selected SparkFun digital PPG acquisition

Scope: the actual SparkFun SEN-15219 MAX30101/MAX32664 breakout selected in the committed shopping list, with Android/iOS signed-reader interoperability. It is a separate adapter from the generic ADC implementation. This capability preserves HW-003/007/012, LLD section 5.1, AND-HR-002–006 and the [engineering design](../../design.md).

## ADDED Requirements

### Requirement: VPPG-001 Pin and initialize the actual selected sensor SDK
The selected digital PPG adapter SHALL use the immutable official SparkFun SDK pin and its documented MAX32664 BPM interface with exact approved/provisioned Nano wiring and mode. Disclosed bounded-I2C/nonblocking corrections SHALL preserve vendor register semantics and attribution. Missing driver, incompatible SDK/material, initialization error or unavailable protected configuration SHALL fail closed.

#### Scenario: Exact selected breakout initializes
- **GIVEN** approved/provisioned selected hardware, firmware and SDK material
- **WHEN** the current signed PPG start is admitted
- **THEN** the actual SDK adapter initializes the declared I2C/reset/MFIO/BPM mode and progresses through bounded warmup without blocking cancellation.

#### Scenario: Generic ADC or failed hub initialization
- **GIVEN** a configuration expects SEN-15219 but a different adapter or failed I2C hub is present
- **WHEN** acquisition is requested
- **THEN** it returns a concrete invalid/unavailable disposition and never substitutes ADC counts, a simulator or a fabricated bpm.

### Requirement: VPPG-002 Count only fresh bounded vendor records
The adapter SHALL reset/discard pre-start buffered output and count only successful fresh FIFO dequeues within the current capture. Original status/error and valid/invalid/received counts SHALL reconcile. Empty polls, malformed/short reads, cached output and replayed delivery SHALL not advance counts. Equal values from separate successful dequeues MAY be genuine; host sequence SHALL not be represented as a vendor sample identity.

#### Scenario: Fresh FIFO with known invalid records
- **GIVEN** the current capture receives bounded distinct vendor records with valid and poor-contact statuses
- **WHEN** the adapter processes them
- **THEN** received counts reconcile to valid/invalid dispositions and only fresh permitted records contribute to the summary.

#### Scenario: No new FIFO data
- **GIVEN** one prior valid heart rate followed by empty FIFO, stale records or truncated responses
- **WHEN** polling continues
- **THEN** no prior number fills the missing interval, valid count does not advance and insufficient/stale evidence produces null completion.

#### Scenario: Identical values from genuine fresh dequeues
- **GIVEN** two separately successful current FIFO dequeues contain identical bpm/quality values and the vendor supplies no unique sample timestamp
- **WHEN** the driver consumes each once
- **THEN** both may count as observations, host sequence remains labeled as host-generated and neither equality nor polling cadence manufactures vendor timing or dropped-sample knowledge.

### Requirement: VPPG-003 Preserve vendor quality and finite extraction semantics
A valid PPG summary SHALL require the exact approved finger/status/confidence/range rules, enough fresh data and a named finite extractor. Evidence SHALL preserve vendor confidence meaning, approved derived-value units and explicit unknown cadence/drop/timing reasons. Underlying sequences require separate current recording authority. Invalid output SHALL have null heart rate. PPG SHALL not manufacture ECG RMSSD, SpO2, cannabinoid values or impairment probabilities.

#### Scenario: Valid finger and vendor quality
- **GIVEN** enough fresh vendor records meet the approved finger/status/confidence/range criteria
- **WHEN** the named extractor completes
- **THEN** a finite positive measured bpm and original bounded quality/count evidence are retained; confidence is labeled acquisition quality.

#### Scenario: Poor finger state or confidence reinterpretation
- **GIVEN** finger absence, insufficient accepted data or a vendor confidence score
- **WHEN** output is validated/displayed
- **THEN** invalid capture has null bpm and explicit reasons, and confidence cannot be shown as accuracy or cannabis impairment probability.

### Requirement: VPPG-004 Bind measured output to signed current origin
The existing protected device signature SHALL bind the vendor projection and exact account/generation/session/attempt/authorization, device/key/boot, configuration/context and current instruction authority. Timing SHALL distinguish host I2C receipt from unobserved sensor onset/cadence. Advertisement, caller-provided key, signed stale output or approval text alone SHALL not establish current measured provenance.

#### Scenario: Current signed vendor completion
- **GIVEN** a verified binding and current scoped start token with actual accepted vendor records
- **WHEN** completion is signed and consumed by Android/iOS and the API
- **THEN** the unchanged normalized evidence and timing/source labels survive exact signature and configuration validation.

#### Scenario: Foreign boot or configuration
- **GIVEN** a signed completion from another boot, authorization, protocol/configuration or workspace
- **WHEN** it is delivered late or replayed
- **THEN** current client/server admission rejects it without attaching the old bpm to the replacement attempt.

### Requirement: VPPG-005 Stop independently of transport and connection replacement
All vendor start/read/reset/stop effects SHALL retain the existing immutable origin gate and secure-link policy. Acquisition SHALL stop within the conservative signed duration independently of TX pressure. Cancel, contact/quality failure, disconnect, reboot and replacement SHALL prevent subsequent reads/signing/notifications from affecting another origin, while preserving an explicit terminal disposition.

#### Scenario: Cancellation during warmup or blocked delivery
- **GIVEN** vendor acquisition is warming up or terminal transport is backpressured
- **WHEN** Cancel or the admitted cutoff occurs
- **THEN** the actual adapter stops before later delivery, retains the originating terminal identity and performs no resumed sampling.

#### Scenario: Late old vendor read versus reconnect
- **GIVEN** an old read/result is delayed while another authenticated connection becomes current
- **WHEN** it completes or notification is attempted
- **THEN** origin fencing rejects its effects and only its own resources may be stopped; no participant payload reaches the replacement peer.

### Requirement: VPPG-006 Advertise only the installed matching vendor adapter
Capabilities and protected firmware inventory SHALL distinguish selected digital PPG from ADC, synthetic and unsupported assay drivers. Current availability SHALL require exact shipped material, SDK/extractor, approved hardware/firmware, binding, calibration, consent and instruction/start scope. Raw retention SHALL require a separately implemented current codec and purpose; vendor outputs SHALL not enable unsolicited recording.

#### Scenario: Installed and currently admitted vendor PPG
- **GIVEN** the selected adapter is compiled and all its exact current independently released scopes match
- **WHEN** Home and PPG capture are opened
- **THEN** the supported vendor path and instruction journey are shown while actual acquisition still obtains a fresh start.

#### Scenario: Approved record names an absent driver or raw codec
- **GIVEN** an operator record names a missing vendor build or unsupported raw encoding
- **WHEN** capability/start/recording is evaluated
- **THEN** software availability remains refused; an approval cannot manufacture code or raw permission.

### Requirement: VPPG-007 Verify executable software separately from physical qualification
Acceptance SHALL include actual-used SDK fake-I2C/FIFO boundary tests, current signed client/server fixtures, strict portable origin/cancellation tests and actual stock/protected target compilation against pinned sources. Mandatory exact-revision merge checks SHALL still pass. Compiler or fictional test success SHALL not claim physical accuracy, calibration, contact/motion robustness, safe participant use or model eligibility.

#### Scenario: Actual driver software fixtures
- **GIVEN** the same adapter used by firmware and the pinned vendor commands
- **WHEN** fresh/empty/malformed FIFO, reset, quality, cutoff and cancellation cases execute
- **THEN** tests verify its actual observable outcomes and both target builds retain source/artifact evidence without claiming sensor execution.

#### Scenario: Compile mistaken for participant qualification
- **GIVEN** stock/protected compilation and fictional interoperability pass but no genuine reference/device/study evidence exists
- **WHEN** participant or model eligibility is evaluated
- **THEN** those external gates remain closed and the reports explicitly distinguish software tests from real sensor validation.
