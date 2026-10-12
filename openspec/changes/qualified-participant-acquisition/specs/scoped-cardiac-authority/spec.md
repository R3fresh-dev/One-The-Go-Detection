## ADDED Requirements

### Requirement: HR-AUTH-001 Explicit restricted model policy
The service SHALL permit server interval authority only when the independently released model requires exactly `cardiac_hr`, its artifact uses exactly `cardiac.heart_rate_bpm`, and its explicit `cardiac_timing_policy` selects `server_issue_to_attestation_receipt_v1`, a current calibration, bounded maximum interval and baseline-delta permission. Absent or incompatible policy SHALL retain refusal.

#### Scenario: Explicit approved heart-rate-only policy
- **GIVEN** a current independently released HR-only model, exact one-feature artifact and matching released server-interval policy
- **WHEN** an owned fully admitted cardiac measurement is evaluated
- **THEN** the service evaluates the separate interval authority before model execution
- **AND** the policy alone grants no device, study or measurement qualification

#### Scenario: Unsupported predictor or implicit policy
- **GIVEN** missing policy, an ECG/RMSSD predictor, an additional required channel or a mismatching artifact feature
- **WHEN** server interval qualification is requested
- **THEN** the service refuses that authority and performs no model execution
- **AND** no legacy model is silently upgraded

### Requirement: HR-AUTH-002 Exact independent calibration scope
The service SHALL require a current independently released `cardiac_server_interval` calibration and qualified-measurement dependencies binding exact device/key, hardware, firmware, channel/modality, adapter/extractor, configuration ID/version/full submitted digest, method, maximum interval, finite server UTC error and `follows_current_signed_grant` behavior. Caller declarations SHALL NOT create or widen this authority.

#### Scenario: Exact released measurement and behavior scope
- **GIVEN** current independently released model, configuration, hardware, firmware, qualification and calibration records for the exact protected reader and HR adapter
- **WHEN** their complete immutable scope matches the owned accepted measurement
- **THEN** the server may derive the restricted interval proof
- **AND** externally observed sensor freshness and behavior evidence remains an approval prerequisite
- **AND** the approved maximum interval is 100–120000 ms and server UTC error is 0–1000 ms
- **AND** vendor signed-duration comparison requires independently reviewed monotonic rate error of 0–10000 ppm; ADC has no inferred signed duration or rate error

#### Scenario: One changed dependency or self-asserted calibration
- **GIVEN** a different key, device, firmware, extractor, configuration version/digest, method or interval bound, or an expired/retired/revoked dependency
- **WHEN** the measurement is admitted or re-admitted
- **THEN** the interval authority is refused
- **AND** a participant checkbox or a caller-supplied qualified boolean cannot replace the released evidence

### Requirement: HR-AUTH-003 Conservative original server interval
The server SHALL derive a finite nonnegative interval from the immutable original signed-start issue time to the owned signature-verified attestation record's original receipt time. It SHALL verify current accepted attempt, authorization, signature and scope before using that interval. It SHALL NOT renew either endpoint on replay or present the interval as measured sensor onset, cadence or a precise acquisition clock.

#### Scenario: Original custody bounds retained
- **GIVEN** an owned accepted valid PPG attempt whose exact signed grant and device-signed completion have been verified
- **WHEN** the original attestation receipt follows original grant issue within the approved maximum
- **THEN** the proof records both original endpoints and their conservative width
- **AND** the original snapshot, target chronology and unqualified clock flags remain unchanged

#### Scenario: Missing, reversed or renewed endpoints
- **GIVEN** absent accepted attestation, negative/nonfinite/reversed times, a foreign attempt, a mismatching signature or an interval above its approved maximum
- **WHEN** authority is computed
- **THEN** the service refuses it
- **AND** replay or a replacement receipt cannot restart its age or shorten the original interval

#### Scenario: Vendor signed duration fits the conservative interval
- **GIVEN** the actual SDK-signed monotonic duration and exact independently reviewed rate-error bound
- **WHEN** its rational comparison satisfies `duration_us × 1000000 ≤ custody_window_us × (1000000 + maximum_monotonic_rate_error_ppm)` using the unrounded widened endpoints
- **THEN** that consistency check permits admission
- **AND** it does not establish sensor onset, actual cadence or absolute device UTC

#### Scenario: Signed duration cannot fit the original custody window
- **GIVEN** a vendor duration above the exact conservative bound, missing vendor rate-error qualification or an inferred ADC duration
- **WHEN** interval authority is resolved or validated
- **THEN** authority refuses despite an apparently fitting rounded millisecond interval
- **AND** no endpoint, duration or original flag is rewritten

### Requirement: HR-AUTH-004 Direct model timing gates
The service SHALL compare independently derived conservative interval width, acquisition bounds and current delivery age directly with the frozen model's timing limits. Equality SHALL follow the declared inclusive maximum; exceeding any limit SHALL refuse. Null or unqualified legacy snapshot timing SHALL NOT be converted into precise values, and the approved interval SHALL NOT authorize unrelated physical or chemical timing claims.

#### Scenario: Conservative bounds meet every limit
- **GIVEN** an exact admitted HR-only authority whose conservative width and acquisition bounds meet all model limits
- **WHEN** current delivery age also meets the model's maximum
- **THEN** timing admission may succeed using the separately labeled bounds
- **AND** the immutable snapshot is not rewritten to look physically calibrated
- **AND** both endpoint error margins widen the bounds with one shared outward-rounding calculation

#### Scenario: Original issue reveals late delivery
- **GIVEN** an apparently recent client capture timestamp but an original signed issue time whose delivery age exceeds the frozen maximum
- **WHEN** execution is requested
- **THEN** the service refuses the late measurement
- **AND** a current retry time or attestation replay cannot make it current

#### Scenario: Exact limit and adjacent overflow
- **GIVEN** the same valid immutable measurement with finite conservative bounds
- **WHEN** a bound equals the declared inclusive maximum
- **THEN** that comparison permits admission
- **BUT WHEN** it exceeds the maximum by a representable positive amount
- **THEN** that comparison refuses admission

### Requirement: HR-AUTH-005 Retained quality and restricted meaning
The service SHALL retain every original cardiac quality flag and admit only the exact known unqualified-clock flag set for the shipped ADC or selected vendor adapter under valid interval authority. Any fault or extra flag SHALL refuse. This exception SHALL authorize only heart-rate prediction; it SHALL NOT qualify ECG, RMSSD, SpO2, vendor confidence, sampling cadence, sensor onset or clinical impairment validity.

#### Scenario: Recognized timing limitation remains visible
- **GIVEN** a valid exact adapter measurement carrying its complete known unqualified server/host timing flags and a matching interval proof
- **WHEN** restricted HR-only execution succeeds
- **THEN** the original evidence and authority manifest retain those flags and explain the conservative method
- **AND** vendor confidence remains acquisition quality rather than a calibrated prediction probability

#### Scenario: Fault flag or different modality
- **GIVEN** a contact, range, confidence, dropped-data or unknown additional fault flag, or ECG/unsupported modality
- **WHEN** an interval proof is presented
- **THEN** the service refuses the exception
- **AND** no flag is removed, normalized or hidden to make the measurement eligible

### Requirement: HR-AUTH-006 Independent historical baseline admission
A personalized HR model SHALL use baseline delta only when its explicit policy permits it and the baseline independently passes full owned evidence, current released dependency and exact device/key/configuration/calibration/adapter checks. The frozen historical age limit SHALL remain enforced separately. Current measurement authority SHALL NOT qualify a missing, incompatible or unverified baseline.

#### Scenario: Independently admitted compatible baseline
- **GIVEN** explicit baseline-delta permission and current and historical measurements with the same exact allowed scope
- **WHEN** each original interval is independently valid and baseline age meets the frozen historical limit
- **THEN** the model may calculate only the approved heart-rate baseline delta
- **AND** both authority proofs are retained separately

#### Scenario: Current proof with incompatible baseline
- **GIVEN** a valid current proof but an old baseline with another device/key/configuration, absent signed evidence, retired calibration or excess historical age
- **WHEN** personalized execution is requested
- **THEN** personalized admission refuses
- **AND** the service does not silently substitute zero delta, a population result or the current proof for the baseline proof

### Requirement: HR-AUTH-007 Immutable proof and current publication authority
ResearchResult 1.1.0 SHALL bind a separately hashed cardiac authority companion to immutable original measurement/model evidence. The service SHALL re-admit current authority for conditional numeric admission, execution, publication, replay and read, including baseline when used. Loss of authority SHALL stop numeric disclosure. Engineering fixtures and compiled adapters SHALL NOT seed genuine approvals or qualify legacy 0.1 results.

#### Scenario: Bound proof through accepted job and read
- **GIVEN** exact independently admitted current and optional baseline authority
- **WHEN** the accepted worker publishes and the participant reads the versioned result
- **THEN** its immutable authority manifest binds the original proof digest and model/input scope
- **AND** current checks pass before every numeric disclosure

#### Scenario: Revocation after acceptance or forged companion
- **GIVEN** authority revoked after job acceptance, or a changed companion with a newly computed caller digest
- **WHEN** execution, commit, cached replay or result read occurs
- **THEN** current server admission refuses numeric disclosure
- **AND** neither a hash alone nor a fictional fixture creates an approval

#### Scenario: Legacy measurement behavior preserved
- **GIVEN** a legacy 0.1 result or an HR measurement without the explicit released model/calibration policy
- **WHEN** it is rendered or evaluated
- **THEN** existing measurement-only or unavailable behavior remains
- **AND** no new numeric research claim is inserted into the strict legacy envelope

#### Scenario: Safe measurement job without model authority
- **GIVEN** an otherwise admitted measurement whose current HR model or calibration authority is unavailable
- **WHEN** the participant explicitly finalizes and queues its measurement job
- **THEN** the service may process its measurement-only result under the ordinary current account/study rules
- **AND** accepting that job supplies no numeric HR-model authority; every subsequent conditional execution or disclosure still requires complete current proof

### Requirement: HR-AUTH-008 Prespecified interval-aware research evaluation
The offline tooling SHALL support an explicitly prespecified HR-only evaluation mode with full unchanged current and, when required, baseline snapshots, typed interval authority and reviewed source-bundle references/digests. It SHALL derive only the approved HR predictor/delta, preserve original flags and every row denominator, and emit runtime-compatible scoped artifacts/reports. Editable-file consistency SHALL NOT authenticate external source or approval authority.

#### Scenario: Scoped population training and evaluation
- **GIVEN** a frozen HR-only plan and source-bundle/custody review references with exact typed current snapshot and interval companions
- **WHEN** original flags, value, target, information cutoff, policy and source digests match and every conservative timing gate passes
- **THEN** train-only fitting and held-out/later-session evaluation produce the explicit `cardiac_hr_only` artifact/report variant
- **AND** invalid and abstaining rows and all six frozen strata retain complete counts
- **AND** the output does not invent chemical/app/ECG comparison results

#### Scenario: Explicit personalized baseline evidence
- **GIVEN** a frozen baseline-delta policy, historical age bound and both full original current/baseline snapshots
- **WHEN** the companion independently binds both snapshots and runtime-equivalent original interval, scope, chronology and baseline-age checks succeed
- **THEN** the sole fitted predictor is the exact current-minus-baseline heart-rate value
- **AND** no arbitrary earlier dataset row supplies a missing baseline

#### Scenario: Forged consistency or incomplete baseline
- **GIVEN** changed original flags/value/target, mismatching policy/source digest, missing required baseline or an incompatible/late interval
- **WHEN** fitting or evaluation is attempted
- **THEN** the tooling refuses the incompatible row or dataset under its explicit invalid-row rules
- **AND** matching editable hashes do not establish trusted server signatures, current registry state or genuine custody review

#### Scenario: Legacy quality and four-ablation behavior
- **GIVEN** a plan without the explicit HR-only policy
- **WHEN** it encounters an unqualified flagged cardiac row or runs the existing evaluation mode
- **THEN** the original quality refusal and all four matched-ablation requirements remain
- **AND** a caller cannot switch modes after dataset/analysis locking to remove failures or comparisons
