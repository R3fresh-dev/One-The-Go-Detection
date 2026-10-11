# Nano ESP32 synthetic BLE bench firmware

Start with an **Arduino Nano ESP32 and a USB-C data cable** for the embedded communication prototype. This firmware provides an actual BLE peripheral for the Android/iOS app while the analytical and human-sensing hardware remains a separate development and qualification effort.

The firmware reads no sensor pins, electrodes, pupil measurements, saliva strip, or chemical instrument. It publishes fixed fictional PPG, ECG and oral-fluid test records. Use it on a bench without body-connected circuitry. The original serial-only example remains at [examples/arduino/synthetic_serial](../examples/arduino/synthetic_serial/).

## Pinned toolchain

| Item | Pin |
|---|---|
| Board | Arduino Nano ESP32 |
| Fully qualified board name | `arduino:esp32:nano_nora` |
| Arduino board package | `arduino:esp32@2.0.18-arduino.5` |
| Arduino CLI | `1.5.1` |
| ArduinoJson | `7.4.2` |
| esptool Python dependency | `pyserial==3.5` |
| BLE | ESP32 board package's built-in BLE library |

Use the board package's bundled BLE implementation. Installing a similarly named third-party BLE library can change APIs and behavior. The reviewed firmware includes FreeRTOS queueing and the ESP32 monotonic timer through the board package.

## Build and flash

Install [Arduino CLI](https://docs.arduino.cc/arduino-cli/installation/) or use Arduino IDE with the equivalent board/library pins. With the CLI:

```sh
arduino-cli core update-index
arduino-cli core install arduino:esp32@2.0.18-arduino.5
arduino-cli lib install ArduinoJson@7.4.2
python3 -m venv .local/arduino-python
.local/arduino-python/bin/pip install pyserial==3.5
export PATH="$PWD/.local/arduino-python/bin:$PATH"
arduino-cli compile --fqbn arduino:esp32:nano_nora --warnings all \
  --output-dir firmware/build/nano_esp32 firmware/nano_esp32_ble_simulator
arduino-cli board list
```

Select the actual connected board port shown by `board list`, then flash it:

```sh
arduino-cli upload --fqbn arduino:esp32:nano_nora --port YOUR_BOARD_PORT \
  --input-dir firmware/build/nano_esp32
```

The firmware does not wait for USB serial before advertising. Serial monitoring at 115,200 baud is optional. Expected startup text is `OTGD synthetic simulator ready. No human sensing. Fixed fictional fixtures only.` The BLE alias is `OTGD Synthetic`.

In the app, open Devices, choose Scan, grant the contextual Bluetooth permission, and choose the discovered simulator. The UI will show an unverified simulator association. Run a synthetic PPG, ECG or saliva capture from a synthetic/demo check. A successful capture retains the full transport transcript, fixed values and clock evidence. Disconnect and reconnect to exercise recovery; reboot the board when the bounded replay journal is full.

For a software-only first run, choose the app's explicit local simulator. That path is useful before the board arrives, but it does not test the radio, BLE permissions, board clock or firmware.

## Firmware behavior

`nano_esp32_ble_simulator.ino` publishes the project service and capability/read, command/write and event/notify characteristics. [The adapter protocol guide](../apps/mobile/src/device/README.md) specifies the UUIDs, byte header and exact fixture data.

Native BLE callbacks copy only bounded 13–20 byte packets into a 64-element queue. A loop-owned parser validates strict UTF-8 JSON, duplicate keys, sizes, CRC, session/boot identity, command deadlines and sequence/replay rules. It processes `hello`, `clock_sync`, `start_capture`, `cancel_capture` and `ack`. It never treats CRC or a SHA-256 replay fingerprint as authentication.

A physical boot generates a new boot UUID; reconnecting does not. The replay journal retains up to 128 command IDs/content hashes and 64 KiB of cached responses across reconnects, without eviction. The transmit queue holds at most eight messages and 32 KiB. Journal or queue exhaustion stops the operation and asks for a board restart instead of silently dropping evidence. New connections invalidate old callback generations and pending captures.

At MTU 23, fragments are at most 20 bytes with eight payload bytes. Notifications are paced at 10 ms and assembled into records of at most 8,192 bytes including CRC. A response's two-second acknowledgment window starts after its final fragment; at most three retries retain the same message ID/content. Commands carry a deadline and full session/attempt/capture/workspace context. Disconnect, malformed transport, overflow and deadline failures terminate active work.

The fixture record durations are 3 seconds for PPG, 4 seconds for ECG and 2 seconds for saliva. Each completion carries actual device monotonic start/end observations. The waveform is 200 fixed integer samples, not a physiological acquisition. No commands enable optical stimuli, electrodes, chemical analysis or arbitrary raw-stream capture.

## Portable tests

`ProtocolCore.h` has no Arduino dependency. Build its adversarial byte/parser tests on a C++17 host:

```sh
g++ -std=c++17 -Wall -Wextra -Werror \
  firmware/tests/protocol_core_test.cpp -o /tmp/otgd-protocol-test
/tmp/otgd-protocol-test
```

The tests cover the standard CRC vector, strict JSON and UTF-8, duplicate keys including escaped aliases, nesting/numeric limits, fragmented reconstruction, ordering, identical/conflicting duplicates, corruption, bounds and assembly expiry. These host checks are different from compiling the Arduino sketch for its actual board package. The native-build GitHub workflow runs both checks and produces firmware build files; it does not flash or physically test a board.

The actual board-target compile also passed locally on 2026-10-11 with the pins above: 956,469 bytes of program storage (30%) and 75,068 bytes of static global memory (22%). Dynamic allocations are additional to that compiler-reported static total. The source uses explicit buffer, queue and journal bounds. The compile produced board binaries; no physical board was flashed or connected during this check.

For the current executed/pending checks, read [native verification](../apps/mobile/modules/VERIFICATION.md). No firmware build, software simulator, or app bundle constitutes an assay qualification, electrical safety assessment or validated intoxication model.

Primary references: [Arduino Nano ESP32](https://docs.arduino.cc/hardware/nano-esp32/), [Espressif's built-in BLE API](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/ble.html), [Arduino package index](https://downloads.arduino.cc/packages/package_index.json), [ArduinoJson 7 releases](https://arduinojson.org/v7/revisions/), [Arduino CLI 1.5.1 release](https://github.com/arduino/arduino-cli/releases/tag/v1.5.1).

The separate [signed physical reader](nano_esp32_signed_reader/README.md) implements protected device/server signatures and an opt-in real ADC PPG/ECG driver. Its [custom security-enabled ESP-IDF build](secure_reader/README.md) is separate from this fictional simulator. Actual sensing/electrical/calibration/provisioning qualification remains external.
