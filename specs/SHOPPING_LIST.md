# One-The-Go Detection — What to Buy First

**Checked:** October 10, 2026, America/Chicago. **Currency:** US dollars. **Purpose:** one development prototype for board communication and finger PPG acquisition. Prices are the observed single-quantity retail prices; taxes, shipping, and any local services are excluded. No purchases have been made.

Buy the **Arduino Nano ESP32 with headers, SKU ABX00083**, and the following small bench kit. The specific headered board is **$19.30**. The earlier $18.30 board listing in the starter guide is the headerless variant, ABX00092; choosing ABX00083 avoids soldering the Nano headers. [Arduino US listing](https://store-usa.arduino.cc/products/nano-esp32-with-headers)

## 1. Recommended first order

Buy one of each row. Reuse equivalent cables, tools, and wire packs that you already own.

| Item and exact purchase link | SKU / variant | Quantity | Price | Why it is in this order |
|---|---|---:|---:|---|
| [Arduino Nano ESP32 with headers](https://store-usa.arduino.cc/products/nano-esp32-with-headers) | **ABX00083**, headers installed | 1 board | **$19.30** | BLE-capable controller and USB development connection. |
| [SparkFun MAX30101 + MAX32664 PPG module](https://www.sparkfun.com/sparkfun-pulse-oximeter-and-heart-rate-sensor-max30101-max32664-qwiic.html) | **SEN-15219**, Qwiic breakout | 1 board | **$48.95** | The exact finger-pulse module used by the hardware plan. |
| [USB 2.0 Type-C cable, 1 meter](https://www.sparkfun.com/usb-2-0-type-c-cable-1-meter.html) | **CAB-16905**, USB-C to USB-C, data-capable | 1 cable | **$6.50** | Connects a USB-C computer port to the Nano for programming and serial output. |
| [Self-adhesive white breadboard](https://www.sparkfun.com/breadboard-self-adhesive-white.html) | **PRT-12002**, 400 tie points, 0.1-inch pitch | 1 board | **$6.25** | Holds the Nano and provides accessible connections. |
| [Flexible Qwiic cable to breadboard jumpers](https://www.sparkfun.com/flexible-qwiic-cable-breadboard-jumper-4-pin.html) | **PRT-17912**, four male breadboard ends | 1 cable | **$1.95** | Connects the sensor's Qwiic socket to the Nano through the breadboard. |
| [IC hooks with pigtails](https://www.sparkfun.com/ic-hook-with-pigtail.html) | **CAB-09741**, five-pack, male pin ends | 1 pack | **$5.75** | Two hooks provide temporary RESET and MFIO connections without soldering. Three are spare. |
| [6-inch male-to-male jumper wires](https://www.sparkfun.com/jumper-wires-connected-6-m-m-20-pack.html) | **PRT-12795**, 20-pack | 1 pack | **$2.95** | Breadboard routing and power-rail connections. |
| [6-inch male-to-female jumper wires](https://www.sparkfun.com/jumper-wires-connected-6-m-f-20-pack.html) | **PRT-12794**, 20-pack | 1 pack | **$2.75** | Extends male test leads and supports a later soldered-header sensor connection. |
| **Eight-item basket subtotal** | | | **$94.40** | Before tax and shipping. |

The Arduino page offered add-to-cart, and the linked SparkFun listings showed in-stock status at the check. Availability may change before checkout. The product links are the sources for price, packaging, and connector claims in each row.

**If the computer only has USB-A:** substitute [SparkFun CAB-14743, USB-A to USB-C data cable](https://www.sparkfun.com/usb-3-1-cable-a-to-c-3-foot.html), **$7.95**, for CAB-16905. That basket is **$95.85**. Buy the cable matching the computer; there is no need to buy both.

## 2. Add this if you do not own a meter

| Item | Quantity | Price | What it includes |
|---|---:|---:|---|
| [SparkFun Digital Multimeter — Basic, TOL-12966](https://www.sparkfun.com/digital-multimeter-basic.html) | 1 | **$21.50** | Meter, test probes, and 9 V battery. Useful for continuity and DC supply checks. |
| **USB-C basket plus meter** | | **$115.90** | Before tax and shipping. |

The meter is intended here for the low-voltage prototype bench. Use continuity mode with circuit power disconnected. Check the Nano's 3.3 V supply before connecting the sensor. Follow the meter's operating instructions and its correct input sockets.

## 3. Why the connectors matter

The Nano does not provide a Qwiic socket. A cable with Qwiic connectors at both ends therefore does not directly connect this sensor to the selected Nano. **PRT-17912** provides the necessary four male breadboard connections. Its color mapping is black = GND, red = 3.3 V, blue = SDA, yellow = SCL. [Cable documentation](https://www.sparkfun.com/flexible-qwiic-cable-breadboard-jumper-4-pin.html)

The PPG module also requires **RESET and MFIO**. These signals are not carried by its four-wire Qwiic connection. The vendor's own hookup instructions use IC hooks for these two connections, which makes the first stationary bench assembly possible without buying a soldering iron. [Sensor hookup instructions](https://learn.sparkfun.com/tutorials/sparkfun-pulse-oximeter-and-heart-rate-monitor-hookup-guide/hardware-hookup)

With power disconnected, mount the Nano across the breadboard center channel and use this proposed mapping:

| Connection from the PPG module | Nano connection | Connection method |
|---|---|---|
| 3V3 | 3V3 | Red Qwiic breakout lead through breadboard. |
| GND | GND | Black Qwiic breakout lead through breadboard. |
| SDA | A4 | Blue Qwiic breakout lead through breadboard. |
| SCL | A5 | Yellow Qwiic breakout lead through breadboard. |
| RESET | D2 | One IC hook on the labeled breakout connection; male end routed to D2. |
| MFIO | D3 | Second IC hook on the labeled breakout connection; male end routed to D3. |

D2/D3 are this project's chosen control pins; SparkFun's example uses different assignments. Set the driver to the actual wiring and use the Arduino pin labels, since raw ESP32 GPIO numbers differ. The sensor and Nano GPIO use **3.3 V**. [Nano specifications](https://store-usa.arduino.cc/products/nano-esp32-with-headers), [pin-numbering documentation](https://support.arduino.cc/hc/en-us/articles/10483225565980-Select-pin-numbering-for-Nano-ESP32-in-Arduino-IDE), [sensor electrical connections](https://learn.sparkfun.com/tutorials/sparkfun-pulse-oximeter-and-heart-rate-monitor-hookup-guide/hardware-overview).

Keep the test hooks stationary and clear of adjacent pads. For a durable prototype, replace them with soldered headers or wires after the interface works. One [PRT-00116 straight 40-pin header strip](https://www.sparkfun.com/straight-header-male-pth-0-1in-40-pin.html), **$1.95**, can be cut to the required sensor header length. That approach additionally needs a soldering iron, appropriate solder, and normal soldering tools, or someone to assemble the connector. A loose pin pushed into an unsoldered plated hole is not a reliable electrical connection.

## 4. Use or borrow equipment already available

| Equipment | What to do now |
|---|---|
| Development computer | Use your existing computer for Arduino and Android development. Local iOS compilation requires a Mac with a compatible Xcode installation; a managed macOS build environment is another option. Verify the mobile project's selected SDK requirements before buying a computer. |
| Android phone | Use or borrow a supported physical phone for BLE, permission, camera, lifecycle, and task-timing checks. An emulator can cover substantial UI work but does not replace those device checks. |
| iPhone | Use or borrow a supported physical iPhone for the corresponding iOS checks. Select the exact supported device/OS set in the mobile validation plan before expanding the test fleet. |
| Phone holder | Reuse a stable desk stand or tripod to make camera-framing experiments repeatable. A dedicated holder can be selected after the capture geometry is defined. |
| Finger support | Begin with a clean, stable support that reduces movement and keeps the optical window clear. Develop a repeatable fixture as part of the PPG experiments. |

The $94.40/$115.90 totals exclude phones, computers, a fixture, developer-account fees, and cloud services. This is the first electronics order, not the final product's manufacturing cost.

## 5. Purchase after the relevant design decision

| Workstream | Next purchase trigger |
|---|---|
| Saliva THC assay | The assay team specifies the analytical method, collection device, sample preparation, calibration materials, and required reader. A generic electrochemical board does not supply cannabinoid selectivity. |
| ECG | A reviewed circuit and simulator-based test plan define the front end, electrode interface, isolation/power arrangement, and accessories. |
| Alcohol sensing | A fuel-cell sampling and calibration design defines the sensor, pump/flow components, interface, and calibration apparatus. |
| Portable power | Measured consumption and duty cycle define the battery, protection, charging, and regulation requirements. USB development power is enough for the first board work. |
| Custom PCB and enclosure | Sensor interfaces, power requirements, antenna placement, and mechanical contact geometry have been demonstrated on the bench. |

The hardware work can proceed while Android and iOS development uses synthetic records. First verify board programming and serial output, then the communication contract, then the actual PPG signal and quality handling. The first purchase does not include a quantitative saliva assay or a validated impairment classifier; those remain explicit workstreams in the [hardware guide](HARDWARE_STARTER_GUIDE.md) and [validation plan](VALIDATION_PLAN.md).
