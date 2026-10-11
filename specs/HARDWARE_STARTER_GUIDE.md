# One-The-Go Detection — Hardware Starter Guide

**Status:** engineering development plan, version 0.1.\
**Research and price check:** October 10, 2026, America/Chicago.\
**First board:** Arduino Nano ESP32.\
**First milestone:** a clearly labeled synthetic serial stream, followed by BLE transport and nonclinical PPG acquisition.\
**Release boundary:** this guide does not describe a validated cannabis detector, a production circuit, or an instrument that establishes fitness to drive.

## 1. Start with an Arduino, and make the first objective small

Yes: start with an **Arduino Nano ESP32**, programmed through the Arduino environment. Its job is to acquire measurements, attach timing and quality information, and communicate with the phone. The phone performs the camera assessment and the reaction task. The cannabis assay develops as a separate analytical workstream.

Arduino documents the Nano ESP32 as an ESP32-S3 board with BLE, USB-C, and 16 MB of flash. These are useful capabilities for the integration prototype; they are not specifications for the final battery life, sensing accuracy, or enclosure. [Arduino board documentation](https://docs.arduino.cc/hardware/nano-esp32/)

The first successful demonstration should be: **the board sends a synthetic telemetry record, the receiver recognizes it as synthetic, and a reset or reconnect starts a fresh receiver capture. Explicit boot/session identities belong to the later protocol.** The next demonstration adds measured optical pulse data. Neither demonstration should calculate a cannabis probability.

The included [`synthetic_serial.ino`](../examples/arduino/synthetic_serial/synthetic_serial.ino) is a **USB serial NDJSON example only**. It does not implement BLE, read the PPG sensor, measure cannabinoids, or predict impairment. The remaining work below is intentionally described as work to implement and verify.

### Alternative boards

| Option | When to consider it | Decision for this project |
|---|---|---|
| Arduino Nano ESP32 | Early firmware, phone communication, and sensor integration | Selected first board. Keep Wi-Fi disabled when evaluating a BLE-only design. |
| Arduino Nano 33 BLE Rev2 | A later comparison focused on BLE and a Nordic controller | Viable alternative; confirm current core and library compatibility before switching. |
| Nordic development kit or a production radio module | Detailed power measurements and custom PCB development | Evaluate after interfaces and duty cycles stabilize. |
| A larger Linux computer | Laboratory automation or image-processing experiments | Useful as a bench computer; unnecessary inside the first pocket-device prototype. |

A current toolchain detail matters for the Nordic Arduino option: Arduino announced its stable Zephyr core in July 2026 and began deprecating corresponding Mbed-based cores. A new project should follow the current supported installation path. [Arduino transition announcement](https://blog.arduino.cc/2026/07/29/arduino-core-on-zephyr-0-90-0-is-officially-stable-and-leaving-beta/)

## 2. What lives where

| Subsystem | Initial implementation | Later development question |
|---|---|---|
| Profile and reaction game | Phone application | Does the exact task contribute predictive value against an independent endpoint? |
| Pupil response | Guided phone camera workflow and recording-quality checks | Which phones, lighting conditions, and stimulus procedure provide reproducible measurements? |
| Heart rate | Finger PPG development module | What optical geometry and contact fixture work consistently? |
| ECG | Simulator-driven evaluation, followed by professionally reviewed human-contact hardware | Does ECG add information beyond pulse and the other inputs? |
| Saliva chemistry | Reference laboratory results and clearly separated synthetic development fixtures | Can a disposable quantitative assay meet the required sensitivity and specificity? |
| Breath alcohol | Separate future fuel-cell measurement channel | Can the complete sampling system be calibrated and validated? |

The consumer vision remains one device and one app. During development, several bench instruments may be needed. Putting everything in one enclosure before the measurements work independently would make failures harder to diagnose.

For cannabis mode, retain **one saliva collection and one reaction task per check**. Multiple analytes may be measured from that single collection. Development studies can collect repeated sessions and reference samples without changing the intended consumer workflow.

## 3. First shopping list and budget

### Verified component listings

These are observed retail listings, not quotations or commitments. Confirm the selected variant, headers, availability, shipping, and taxes before ordering. No purchases have been made.

| Item | Listed price | Purchase timing and purpose |
|---|---:|---|
| Arduino Nano ESP32 | US $18.30 | First purchase; board and USB communication. |
| SparkFun MAX30101 + MAX32664 PPG module, SEN-15219 | US $48.95 | First sensor; raw/processed optical pulse data and acquisition-quality information. |
| SparkFun AD8232 module, SEN-12650 | US $24.41 | Optional later educational ECG evaluation, initially using a simulator. |
| Dart breath alcohol sensor | £16.73 | Future alcohol workstream; bare sensor only. |
| Dart sensor interface board | £59.99 | Future evaluation interface; select the compatible variant and review its output voltage. |

Price sources: [Arduino US store](https://store-usa.arduino.cc/products/nano-esp32), [SparkFun PPG module](https://www.sparkfun.com/sparkfun-pulse-oximeter-and-heart-rate-sensor-max30101-max32664-qwiic.html), [SparkFun AD8232 module](https://www.sparkfun.com/sparkfun-single-lead-heart-rate-monitor-ad8232.html), [Dart alcohol sensors](https://www.dart-sensors.com/product-ranges/alcohol/), and [Dart interface board](https://www.dart-sensors.com/products/accessories/interface-circuit-board/).

The first board plus PPG module total **$67.25** before accessories. The following are planning allowances, not researched vendor prices:

| Additional item | Planning allowance | Notes |
|---|---:|---|
| Data-capable USB cable, breadboard, jumpers, headers, and suitable Qwiic breakout cable | $15–35 | Match the actual connectors; Qwiic alone does not supply the PPG module's extra control connections. |
| Basic multimeter | $25–60 | Skip if already available. |
| Simple finger-position fixture | $5–20 | Development materials only; final contact materials require a separate decision. |
| Suitable protected battery supply or USB power bank | $15–35 | For untethered integration; not a complete electrical-safety assessment. |

Allow approximately **$130–220** for a basic BLE/PPG bench setup when starting without these accessories. This excludes the phone, ECG simulator, ECG accessories, soldering equipment, analytical instrumentation, reagents, reference standards, alcohol calibration apparatus, and human studies. It is not the manufacturing bill of materials and does not establish the feasibility of a $20/month business model.

Do not buy an electrochemical assay reader until the assay team identifies the measurement technique it needs. A potentiostat could be appropriate, but an optical cartridge could require a different reader.

## 4. First week: serial first, then transport and PPG

The sequence is a suggested work order. Completion depends on demonstrated behavior, not the calendar.

### Step A — Establish the development environment

1. Install the current Arduino IDE and the board package appropriate to the Nano ESP32.
2. Record the board package, compiler, library, and board revisions in the development log.
3. Connect only the development board by a data-capable USB cable. Leave all human-contact electrodes disconnected.
4. Open the supplied serial example, select the board and port, and upload it.
5. Confirm that each complete serial line is valid JSON and identified as synthetic.
6. Reset the board and reconnect the receiver. Confirm that a fresh session cannot be mistaken for continuation of an older one.

Use the sketch's configured serial rate. Do not describe its output as laboratory data or use it to estimate model performance. Synthetic values are for exercising software paths.

### Step B — Add BLE as a separate implementation task

Implement the protocol defined by the system LLD after the serial path works. Start with device information, a command/status exchange, and synthetic measurement notifications. Test session identifiers, sequence numbers, disconnect behavior, and bounded buffering before attaching sensors.

A lost connection should produce a recoverable transport state. It should not cause the app to reuse a measurement from the previous check. Keep test-device identity separate from user identity and avoid including names or health information in advertisements.

**Exit evidence:** a captured synthetic telemetry trace, an intentional disconnect, and a fresh receiver capture after reconnect. The supplied sketch does not provide reboot-safe session identity. BLE support is future work relative to the supplied serial sketch.

### Step C — Wire the selected PPG breakout

This wiring proposal applies specifically to **SparkFun SEN-15219**, not to an arbitrary board advertised as a MAX30101 or MAX30102 module. Power down before wiring and inspect the breakout revision and markings.

| SparkFun PPG connection | Nano ESP32 connection | Purpose |
|---|---|---|
| 3V3 | 3V3 | Module power |
| GND | GND | Common circuit ground |
| SDA | A4 / SDA | I2C data |
| SCL | A5 / SCL | I2C clock |
| RESET | D2 | Proposed control-pin assignment |
| MFIO | D3 | Proposed control-pin assignment |

The vendor specifies a 3.3 V host and requires RESET and MFIO connections in addition to I2C. Its examples use different control-pin numbers; configure the driver for the D2/D3 assignment above. [SparkFun wiring guide](https://learn.sparkfun.com/tutorials/sparkfun-pulse-oximeter-and-heart-rate-monitor-hookup-guide/hardware-hookup)

Use named pin constants such as `D2`, `D3`, `A4`, and `A5`, and record the IDE pin-numbering mode. Nano ESP32 Arduino pin labels and raw ESP32 GPIO numbers differ. [Arduino pin-numbering documentation](https://support.arduino.cc/hc/en-us/articles/10483225565980-Select-pin-numbering-for-Nano-ESP32-in-Arduino-IDE)

The board uses 3.3 V GPIO; its documented VIN range is 6–21 V. Do not feed a 5 V sensor output into a GPIO or connect a single Li-ion cell directly to VIN as a presumed supported power arrangement. Follow a reviewed supply design. [Nano ESP32 datasheet](https://docs.arduino.cc/resources/datasheets/ABX00083-datasheet.pdf)

### Step D — Acquire and inspect pulse data

Start with the vendor's current driver and example, adapting only the documented wiring and configuration. Confirm device initialization and capture the device's own quality/status fields before adding feature extraction.

Log raw measurements where available, configured sample rate, sensor settings, host timestamps, sequence information, and missing-data intervals. Display heart rate only with an appropriate acquisition-quality state. Do not replace a failed measurement with zero, and do not keep displaying an old value as if it were current.

The SparkFun module exposes finger detection and confidence information, as well as raw and processed data. These are useful development inputs; its confidence field is not a probability of cannabis impairment. The module's sensor hub address is `0x55`. [Module specifications](https://www.sparkfun.com/sparkfun-pulse-oximeter-and-heart-rate-sensor-max30101-max32664-qwiic.html)

**Exit evidence:** successful initialization; cleanly detected finger removal; recorded effects of motion and changing contact pressure; reproducible session storage; and comparison against an appropriate heart-rate reference under a defined nonclinical protocol. A plausible waveform alone does not demonstrate accuracy.

## 5. Eye measurements and the reaction game belong on the phone

Implement one continuous reaction task with repeated trials and versioned instructions. Record target presentation, response timing, missed trials, incorrect responses, interruptions, and the phone model. The development study determines task length and quality thresholds.

For eye recordings, first establish whether the phone can reproduce the stimulus and acquisition conditions. Track exposure changes, frame timing, distance or scale information, occlusion, and recording failures. A proposed short capture duration is a usability target until validated.

Do not add an unreviewed high-intensity LED to the Arduino as an eye stimulus. A custom optical accessory needs an optical design and exposure assessment. The controlled smartphone study used a specific acquisition procedure; it does not validate arbitrary selfie recordings. [Controlled smartphone eye study](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2024.1492246/full)

## 6. ECG is a later, electrically reviewed experiment

Begin with an ECG simulator or an appropriate test signal. Verify input range, filtering, sampling, clipping, and lead-status behavior before considering skin contact. A low-cost development breakout does not establish that the assembled system is suitable for connection to a person.

The AD8232 module is an educational analog option. SparkFun explicitly distinguishes it from a medical device and recommends battery operation to avoid current loops involving the electrical grid. [AD8232 product guidance](https://www.sparkfun.com/sparkfun-single-lead-heart-rate-monitor-ad8232.html)

For a later integrated design, MAX30003 is a candidate digital ECG front end with SPI, waveform acquisition, and R-R detection. These are component capabilities; suitability depends on the complete electrode interface and circuit. [Analog Devices MAX30003](https://www.analog.com/en/products/max30003.html)

Before any body-connected prototype is used, have a qualified engineer review protection, leakage paths, electrode contacts, power, fault conditions, and the intended setting. For the early configuration, require battery operation and wireless transfer while electrodes are attached: disconnect charging, mains USB, grounded test equipment, and other conductive paths. Battery power alone is not evidence that the design is safe.

Keep ECG research optional until an ablation study shows useful predictive improvement. Record waveform quality and rejected segments; do not turn this channel into a cardiac diagnosis feature.

## 7. Develop the saliva assay independently

The critical unresolved component is a **quantitative, selective assay in collected oral fluid**. Arduino ADC readings, generic gas sensors, or the presence of a potentiostat do not supply that selectivity.

Commission analytical feasibility work with a qualified laboratory or assay-development partner. Define parent delta-9-THC as an explicit analyte, then evaluate whether THC-COOH and 11-OH-THC can be measured at useful levels. Document the specimen basis, collection recovery, dilution, sample stability, free versus total analyte definition, and lower/upper quantitation limits.

Ask the assay partner to provide:

- A complete analyte list and unambiguous chemical definitions.
- Calibration and quantitation evidence in the actual collection matrix.
- Precision, bias, carryover, interference, and cross-reactivity results.
- Collection-volume tolerance, recovery, and invalid-sample criteria.
- Reagent, electrode, and cartridge lot variability.
- Read-time and storage-stability evidence.
- A path from laboratory prototype to a sealed disposable cartridge.
- A comparison with a qualified reference method on paired specimens.

An AD5940-based evaluation system can examine electrochemical cells, including relevant current or impedance measurements. The EVAL-AD5940ELCZ kit includes its own host board and should initially be evaluated using its vendor workflow. It is a measurement instrument, not a cannabinoid recognition element. [AD5940 evaluation kit](https://www.analog.com/en/resources/evaluation-hardware-and-software/evaluation-boards-kits/eval-ad5940elcz.html)

If electrochemistry is selected, begin with a dummy cell and characterize noise, drift, and readout range. Then use the assay team's electrode and reagent design. If optical detection is selected, specify the illumination, detector, reference channel, and optical controls instead. Do not freeze the final reader architecture ahead of these results.

Human specimen studies and controlled cannabis-administration studies belong under a professionally designed protocol with the relevant institutional approvals. They are not a DIY extension of the Arduino tutorial.

## 8. Preserve the alcohol channel as a separate measurement system

For the eventual all-in-one product, investigate a fuel-cell breath alcohol sensor with a controlled sampling path, flow or pressure qualification, and documented calibration. A bare sensor is only one part of the instrument.

Dart notes that calibration depends on the complete sampling and interpretation system; its individual sensor data cannot substitute for full-instrument calibration. [Dart sensor documentation](https://www.dart-sensors.com/product-ranges/alcohol/)

There is a specific electrical integration issue: Dart's evaluation interface can output up to 3.75 V on a 9 V supply. That exceeds the Nano's 3.3 V input domain. Use a reviewed conditioning and ADC interface; do not wire the output directly to the Nano. [Dart interface specifications](https://www.dart-sensors.com/products/accessories/interface-circuit-board/)

Develop the alcohol channel using suitable reference standards and test equipment. Keep breath alcohol concentration and any derived blood-alcohol estimate distinctly labeled, with their units and calibration provenance. Do not infer cannabinoid concentration from that alcohol sensor.

## 9. Integration and production gates

| Gate | Required evidence before proceeding |
|---|---|
| Transport prototype | Synthetic serial and then BLE sessions are correctly identified, parsed, timed, and recovered after interruption. |
| Sensor prototype | PPG quality failures are detected; optional ECG works against a simulator; phone tasks and camera collection are versioned. |
| Analytical feasibility | The saliva method measures the selected analytes in the intended matrix against a suitable reference, with documented limitations. |
| Integrated research unit | Collection, timing, sample identity, assay results, and phone measurements remain correctly associated. Human-contact design has been reviewed. |
| Predictive validation | A locked model is tested against an independent endpoint using genuinely held-out participants and sessions. |
| Product engineering | Custom electronics, enclosure, power, cleaning, disposable paths, calibration service, manufacturing controls, and applicable market requirements are addressed. |

Before a custom PCB, measure the actual peak and average current in each operating state. Budget radio, pump, illumination, ADC, and processor loads separately. Preserve space for the antenna, protect sensitive analog paths, and prevent saliva or condensate from reaching reusable electronics or user-contact electrodes.

Before enclosure tooling, demonstrate cartridge insertion, sample adequacy detection, spill containment, mouthpiece separation, and cleaning access using inexpensive fixtures. A pocket-sized envelope remains a target until the fluidic and optical paths are proven.

**Immediate next action:** build and inspect the synthetic serial example with the Nano alone. Then implement BLE transport and add the documented PPG breakout. In parallel, obtain an assay-feasibility proposal that specifies what can actually be quantified from the single saliva collection. Those two workstreams establish whether the eventual integrated device is worth engineering.
