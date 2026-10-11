# Selected SparkFun digital PPG driver

The committed [shopping list](../../specs/SHOPPING_LIST.md) and LLD select the SparkFun SEN-15219 MAX30101/MAX32664 breakout. `otgd_sparkfun_max32664_v1` implements that digital I2C reader. `otgd_esp32_adc_v1` remains a separate, opt-in ADC/front-end adapter; it does not operate the selected breakout. The untracked historical board-firmware draft is not an approved requirement source.

## Exact SDK and data meaning

[The official SDK](https://github.com/sparkfun/SparkFun_Bio_Sensor_Hub_Library/tree/91575258e5e2c47f0f4b8ec97b651381671f4637) is vendored at version 1.1, commit `91575258e5e2c47f0f4b8ec97b651381671f4637`. `vendor/sparkfun/SOURCE.json` records original and compiled SHA256 values. The source and unchanged upstream README preserve SparkFun's Beerware attribution and derivative terms. `PATCHES.md` describes checked I2C status/lengths, cleared failed buffers and cooperative boot/warmup integration; manufacturer commands and data layout remain the pinned SDK's implementation. The protected build helper rejects changed source/attribution bytes.

The driver uses actual `configSensorBpm`, `numSamplesOutFifo`, `readSensorBpm`, `readSensorHubVersion` and `readSampleRate` APIs. Modes 1 and 2 use the SDK's combined sensor/algorithm FIFO. A successful FIFO dequeue is one fresh host observation, including when successive values happen to be identical. A transport replay cannot become another observation. The hardware supplies no unique sensor timestamp or sequence in this SDK record.

The pinned SDK divides its tenth-bpm register value by 10 into an integer. The retained heart rate is the latest accepted **whole bpm**, without extra precision, smoothing or averaging. Confidence is the vendor's signal-quality percentage, never a calibrated probability, clinical accuracy or intoxication probability. Finger status 3, approved confidence/heart-rate bounds and the approved minimum count are required. Contact loss, any invalid observation, missed polling, data gap, firmware mismatch or I2C error makes the run invalid; invalid heart rate is null.

## Wiring and protected configuration

Follow the [manufacturer hookup guide](https://learn.sparkfun.com/tutorials/sparkfun-pulse-oximeter-and-heart-rate-monitor-hookup-guide/all) and the independently reviewed hardware power/electrical plan. The narrow driver contract fixes address `0x55`, bus 100 kHz and physical ESP32-S3 GPIOs: SDA 11 (Nano A4), SCL 12 (A5), RESET 5 (D2), MFIO 6 (D3). The stock Nano target resolves its actual logical-pin remapping; the custom ESP-IDF target uses physical GPIO numbers. This code does not perform clinical electrical or wiring qualification.

Offline encrypted identity NVS `reader/ppg_provision` contains exact JSON fields `{schema_version,configuration_id,configuration_hash,configuration_submitted_sha256,configuration_version,calibration_id,material}`. These are the approved registry identifiers/hashes, never phone-selected replacements. `configuration_hash` is SHA256 of RFC8785 canonical `material`. Provisioning requires a reviewed manufacturing plan; neither this driver nor the build helper writes keys or eFuses.

The material is the server's strict `SparkFunMaterial`, with no acquisition defaults:

| Fields | Exact contract |
|---|---|
| Identity | `schema_version=1.0.0`, `channel=cardiac`, `modality=ppg`, `adapter_id=otgd_sparkfun_max32664_v1`, `protocol_version=1` |
| SDK/extractor | Exact commit above, `sdk_version=1.1`, `extractor_version=sparkfun_sensor_bpm_v1` |
| Bus/GPIO | `i2c_address=85`, `bus_frequency_hz=100000`, `sda_gpio=11`, `scl_gpio=12`, `reset_gpio=5`, `mfio_gpio=6` |
| Timing | `duration_ms` 3000–60000, `end_guard_ms` 100–500, `poll_interval_ms` 50–1000, `i2c_timeout_ms` 1–20, `warmup_ms` 1000–10000, `max_no_data_ms` between poll interval and 5000 |
| Algorithm | `algorithm_mode` 1 or 2; `minimum_valid_samples` 1–256; `minimum_confidence` 0–100; `minimum_heart_rate_bpm` and `maximum_heart_rate_bpm` 1–300 with minimum strictly below maximum |
| Actual expected firmware | `hub_firmware_major`, `hub_firmware_minor`, `hub_firmware_revision`, each 0–255; matched against the actual SDK read before enabling the sensor |

Duration must exceed reset 10 ms + boot 1000 ms + approved warmup + end guard + 250 ms configuration budget. Bus transactions have configured timeouts and a conservative remaining-time check. The vendor's configuration sequence includes two 45 ms waits; the approved warmup is cooperative rather than a blocking 1000 ms SDK delay. Cancellation and origin transitions share the existing short driver mutex; the finite configuration call can delay their delivery by its bounded I2C/command budget. RESET is held low to stop the hub without waiting on BLE acknowledgment or TX queue space. Unselected adapters never change another driver's pins.

Only a fresh, protected-SPKI-verified server start token with the exact approved material/hash/version, device/boot/nonce/binding/owner/generation/context and signed instruction protocol SHA/receipt permits acquisition. The instruction receipt records a participant acknowledgment, not physical compliance or analytical qualification. `raw_recording_permission` must be null for this feature-only PPG driver; a raw PPG request is rejected.

## Signed retention and timing limits

The device signs the complete `{projection,ppg_evidence}` wrapper. `SparkFunPpgEvidence.h` is the actual production payload factory used by the driver and host interop fixture. Projection uses the existing cardiac wire schema, with null sample rate, null ECG features and `ecg_status=not_collected`.

Quality evidence retains SDK identity, actual observed hub firmware (null before a successful read), algorithm mode, aggregate observation/valid/invalid/missed/empty/backlog counts and the latest derived bpm/vendor confidence/finger/extended status. Host sequence is zero-based dequeue order. Raw IR/red optical counts are consumed only in RAM, never emitted or persisted in the feature-only result, and are cleared on stop/reset. There is no PPG raw recording codec or raw-sequence retention.

`configured_sensor_rate_hz` is the actual read sensor register setting, not measured cadence or algorithm FIFO rate. `actual_sensor_cadence_hz` and `sensor_dropped_samples` remain null. `host_poll_interval_ms` is a host scheduling setting. Per-observation time is the actual I2C receive observation; it does not recover sensor onset or the age of buffered FIFO data. These limitations survive device signing and registry approval.

Actual acquisition start/end microseconds are included in the signed wrapper. UTC projection uses the signed server issue timestamp plus actual acquisition duration and retains `SERVER_WALL_ANCHOR_UNQUALIFIED`, `HOST_I2C_RECEIVE_TIMESTAMPS_UNQUALIFIED` and `SPARKFUN_SENSOR_BPM_V1`. That anchor is not observed acquisition UTC or a qualified clock reconstruction. Physical clock/cadence accuracy, signal/confidence meaning, sensor contact, calibration, safety and model eligibility require independent evidence.

## Reproducible software checks

Install the pinned ArduinoJson 7.4.2 dependency using the existing firmware toolchain. On a host:

```sh
g++ -std=c++17 -Wall -Wextra -Werror \
  -I firmware/tests/sparkfun_fake -I "$HOME/Arduino/libraries/ArduinoJson/src" \
  firmware/tests/sparkfun_ppg_test.cpp \
  firmware/nano_esp32_signed_reader/SparkFunBioSensor.cpp \
  firmware/nano_esp32_signed_reader/RyuDouble.cpp \
  -o /tmp/otgd-sparkfun-ppg-test
/tmp/otgd-sparkfun-ppg-test /tmp/sparkfun-ppg-result-v1.json
cmp /tmp/sparkfun-ppg-result-v1.json firmware/tests/fixtures/sparkfun-ppg-result-v1.json
```

This compiles and executes the **actual pinned SDK** against explicit fake I2C bytes, plus the actual-used core and payload factory. It tests vendor command bytes, both modes, configured-rate decoding, fresh/empty FIFO, short reads/NACKs/errors, no stale values, quality/contact/gap/cutoff/cancel behavior, absence of persisted raw counts and a literal cross-language fixture. All observations in the fixture are fictional software tests. The independent client/server validators check that production-generated payload; the server remains authoritative for cryptographic/registry admission.

The ordinary Nano target and [protected ESP-IDF target](../secure_reader/README.md) must both compile the final exact source. Build binaries and unsigned manifests do not establish hardware execution, approved key provisioning, finger-contact qualification, sensor-algorithm accuracy or permission to use the system with human participants. Fresh required CI must pass before merge.
