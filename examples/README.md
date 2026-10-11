# Synthetic examples

Every supplied example is fictional. Identifiers, profiles, concentrations, analytical limits, physiological values, and task features exercise data handling only. They are not real participants, validated sensor outputs, clinical ranges, or cannabis-impairment thresholds.

## Files and their roles

| File | What it demonstrates |
|---|---|
| [synthetic_session.json](synthetic_session.json) | One collection, one task, simulated physiological components, explicit missingness, and linked identifiers in a capture snapshot. |
| [measurement_pg_converted.json](measurement_pg_converted.json) | Preservation of an original pg/mL report alongside its ng/mL unit conversion. No new dilution correction is performed. |
| [unvalidated_model_manifest.json](unvalidated_model_manifest.json) | An intentionally incomplete, `unvalidated` model placeholder with unresolved scientific and approval fields. It contains no executable trained model. |
| [synthetic_telemetry.ndjson](synthetic_telemetry.ndjson) | A hand-authored serial-format fixture. Each line is one JSON record; this file is not a captured hardware test. |
| [arduino/synthetic_serial/synthetic_serial.ino](arduino/synthetic_serial/synthetic_serial.ino) | Arduino USB serial bring-up sketch that emits fabricated telemetry approximately once per second. |

The complete session fixture and the small telemetry fixture are different contracts. The serial stream does not implement the full session, saliva envelope, or proposed BLE protocol.

## Run the local demonstration

From the repository root, create and activate its virtual environment, then install the development dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Run the repository checks and examples:

```bash
python tools/verify_specs.py
python tools/run_demo.py
python tools/check_telemetry.py examples/synthetic_telemetry.ndjson
```

`run_demo.py` reads the synthetic session and unvalidated manifest, checks them, and prints a `measurement_only` result with `probability: null`. Its evaluation timestamp and input digest are generated for the run. It does not fit a model or predict intoxication.

`check_telemetry.py` reads a saved NDJSON file and checks the synthetic telemetry contract and sequence/timing continuity. It does not open a serial port, connect to Bluetooth, or acquire measurements. Passing these commands establishes only the behavior actually checked; it does not validate hardware or medical performance.

## Arduino USB serial exercise

The sketch targets the proposed **Arduino Nano ESP32** first board. See [HARDWARE_STARTER_GUIDE.md](../specs/HARDWARE_STARTER_GUIDE.md) for the board selection, parts, wiring, and later workstreams.

1. Install the current Arduino IDE and appropriate Nano ESP32 board package. Record the versions you use.
2. Connect the Nano by a data-capable USB cable. This exercise needs no sensors or electrodes; keep body-contact electrodes disconnected.
3. Open `examples/arduino/synthetic_serial/synthetic_serial.ino`, select the board and port, and build/upload it in your environment.
4. Open Serial Monitor at **115200 baud**. The sketch emits one synthetic NDJSON line approximately every second.
5. Save complete lines without Serial Monitor timestamp prefixes or other decorations into a local text file. Do not combine separate reset/reconnect captures.
6. Check that saved file by passing its path to `python tools/check_telemetry.py`.

Each emitted line carries `source: "simulated"` and `assay_ready: false`. The changing heart-rate number is fabricated. **No BLE, PPG driver, ECG driver, saliva assay, or prediction model is implemented in this sketch.** These instructions are a build/upload procedure, not a claim that the sketch has been compiled or tested on physical hardware here.

Start a fresh receiver capture after reset, reconnect, or counter rollover. Keep any real participant data outside this repository; this example folder is for synthetic fixtures only.

## Where to continue

Use [contracts/README.md](../contracts/README.md) for field semantics, [LLD.md](../specs/LLD.md) for the planned interfaces, and [VALIDATION_PLAN.md](../specs/VALIDATION_PLAN.md) for the experiments needed before analytical or predictive claims. Replacing a fictional number with an ADC reading does not establish cannabinoid sensing or impairment prediction.
