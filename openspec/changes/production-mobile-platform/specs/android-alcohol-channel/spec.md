# Android feature: separate alcohol channel

Normative integration: [shared application contracts](../../shared-contracts.md) and [platform contracts](../../platform-contract.md). These define the exact cross-feature DTOs, error states, generation/revocation rules, current-release limits, and implementation evidence.

## Purpose and traceability

Reserve the all-in-one product's breath-alcohol experience while preserving a distinct instrument, measurement, and interpretation. Upstream: PRD-008/017; ALC-001–005; HLD §9; LLD measurement/source principles; gate G-11. This feature implements availability, guided state, record validation, and separate reporting; no calibrated breath hardware exists in the initial kit.

## Customer experience

Home provides an **Alcohol measurement** entry with **Hardware required** until an approved breath instrument and sampling configuration are available. Opening it explains **Alcohol measurements need a calibrated breath sensor. Your pulse sensor does not measure alcohol.** The primary available action is **View device requirements**; a development-only **Try a labeled demo** uses fictional values and never changes the real device state.

When an approved device is associated, the flow is preparation → device readiness → sampling → processing → result. Instructions, mouthpiece details, sample-adequacy criteria, environmental limits, and calibration-expiry rules come from the selected approved instrument configuration. Missing configuration blocks the sampling action; the app cannot invent generic blow duration or substitute a timer for qualified sampling. Cancelation preserves an incomplete attempt. A valid alcohol record shows **Breath alcohol**, mg/L, acquisition time, source, calibration status, and qualifier. It is not merged into a cannabis score.

## Engineering contract

Alcohol is a separate versioned record linked to session_id; it is not inserted into the cannabinoid measurement enum or silently appended to the v0.1 acquisition snapshot. Fields include measurement_id, session_id, collected_at, measured_at, source, qualifier, value_mg_l, unit=mg/L, limits, method_id, calibration_id, device_id, boot_id, configuration_hash, and quality_flags. Qualified measurements require verified device provenance and approved calibration; simulated values require a synthetic parent session. Nonquantified values are null. API routes GET/POST /v1/sessions/{session_id}/alcohol follow shared contract §8 with owner/generation/idempotency checks. The selected record/hash is frozen in the companion evidence manifest before finalization; later append/overwrite is rejected and a correction needs a new linked session. History/export retains the separate record. Guest demo remains local; authenticated synthetic API fixtures are a separate engineering path.

The server rejects derived BAC units, unsupported analytes, absent calibration for a claimed qualified measurement, and attempts to infer ethanol from PPG/ECG/camera/task signals. Alcohol co-use in the cannabis profile remains a separate self-report/measurement context. A future model must explicitly support that cohort; the app does not average two probabilities. Android and iOS share units and statuses; locale formatting must never change stored magnitude or use percent signs for mg/L.

## ADDED Requirements

### Requirement: AND-ALC-001 Display actual alcohol availability
The app SHALL show unavailable hardware/configuration reasons until the complete breath-alcohol channel is authorized and usable.

#### Scenario: Only the starter PPG board is connected
- **GIVEN** a Nano ESP32 and PPG module without a calibrated breath channel
- **WHEN** Alcohol is opened
- **THEN** the app shows hardware-required guidance and does not start a blow timer or produce an alcohol value.

#### Scenario: Approved configuration is missing
- **GIVEN** a connected device advertises alcohol capability without an approved configuration
- **WHEN** sampling is requested
- **THEN** the app and server reject the request with a configuration-unavailable reason.

### Requirement: AND-ALC-002 Keep alcohol records independent
An alcohol result MUST retain its own measurement identity, sample timing, units, calibration, source, and quality, separately from cannabis fields.

#### Scenario: Combined session has two measured channels
- **GIVEN** independently valid alcohol and cannabis records
- **WHEN** session detail is displayed
- **THEN** each channel has its own card, units, timing, and validity explanation.

#### Scenario: Cannabis result is unavailable
- **GIVEN** a valid authorized alcohol record and unavailable cannabis inference
- **WHEN** results render
- **THEN** the alcohol measurement does not manufacture a cannabis estimate.

### Requirement: AND-ALC-003 Preserve mg/L and qualifiers
The alcohol contract SHALL use mg/L and null values for not_measured, invalid, below_loq, above_range, and not_detected qualifiers.

#### Scenario: Quantified record arrives
- **GIVEN** an in-range qualified measurement in mg/L
- **WHEN** the record is validated and displayed
- **THEN** its numeric value and mg/L label remain paired.

#### Scenario: Caller submits a BAC percentage
- **GIVEN** a value labeled percent BAC
- **WHEN** it is submitted to the breath-alcohol route
- **THEN** the service rejects the incompatible unit and performs no conversion.

### Requirement: AND-ALC-004 Require calibration and sample adequacy
A qualified record MUST refer to the approved instrument's current calibration and passing sampling criteria; failure SHALL produce an invalid record with reasons.

#### Scenario: Sampling is inadequate
- **GIVEN** the device reports an inadequate breath sample
- **WHEN** acquisition ends
- **THEN** the result is invalid with no exact concentration and an actionable retry explanation.

#### Scenario: Calibration expires
- **GIVEN** the instrument calibration is outside its qualified interval
- **WHEN** a new record is requested
- **THEN** the app blocks qualified sampling and identifies recalibration as the required action.

### Requirement: AND-ALC-005 Isolate fictional demonstrations
Alcohol demonstration records SHALL be visibly synthetic, belong only to a synthetic session, and be excluded from qualified measurement/inference paths.

#### Scenario: Demo is intentionally opened
- **GIVEN** the development demo action
- **WHEN** the customer previews the channel
- **THEN** every value is labeled fictional and no real measurement claim is made.

#### Scenario: Simulated record targets a participant session
- **GIVEN** a nonsynthetic parent session
- **WHEN** a simulated alcohol record is submitted
- **THEN** the service rejects the provenance mismatch.

### Requirement: AND-ALC-006 Prohibit combined impairment shortcuts
The app MUST NOT average cannabis/alcohol scores, infer alcohol from physiology, or display driving clearance from an alcohol measurement.

#### Scenario: Alcohol co-use is present
- **GIVEN** the cannabis model does not support alcohol co-use
- **WHEN** a future research request is evaluated
- **THEN** the unsupported cohort is handled by the manifest gate rather than a score adjustment in the app.

#### Scenario: A low displayed value
- **GIVEN** a low or censored alcohol result
- **WHEN** the result screen is shown
- **THEN** no **Safe to drive** or legal-clearance message appears.
