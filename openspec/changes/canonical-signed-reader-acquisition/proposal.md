# Canonical signed physical reader and bounded ADC acquisition

## Why

The canonical reader previously admitted only fictional measurements and had no executable protected-key acquisition path. Real PPG/ECG transport must bind the participant's current authorization and configuration on the device, acquire actual observations within signed bounds and preserve cancellation/consent fences. Compiling a stock board SDK cannot prove its disabled encrypted-NVS branch.

## What Changes

- Implement a strict signed-reader dialect, exact binding/capture domains, fresh device nonce and device-verifiable scoped server start signature.
- Implement a protected opt-in actual ESP32-S3 ADC PPG/ECG driver with measured timestamps, explicit contact, approved reference/gain and bounded extraction.
- Define immutable connection-origin/replay boundaries, raw-purpose restrictions and shutdown before transport backpressure.
- Provide an immutable-source security-enabled ESP-IDF build entry that compiles protected NVS, with strict private-key and generated-config validation.
- Preserve external physical/electrical/calibration/vendor/clinical qualification as explicit release prerequisites.

## Capabilities

### New Capabilities

- `signed-reader-acquisition`: protected instrument authorization, actual bounded sampling and secure build qualification.

### Modified Capabilities

None. These requirements refine AND-HR-002/003, AND-ECG-002/003 and existing device/privacy requirements without authorizing an unknown assay or weakening registry approval.

## Impact

Canonical device client/firmware, operator ADC material, signed-start API schema, actual backend cross-language fixtures, firmware host/board build gates and secure SDK tooling. No hardware is flashed or permanently provisioned by the build helper.
