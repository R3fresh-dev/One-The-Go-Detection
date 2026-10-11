// One-The-Go Detection: synthetic USB serial bring-up only.
// No sensors, BLE, chemistry, ECG, or intoxication model are implemented.
// Disconnect all body-contact electrodes; this demo needs only a USB cable.
// Select Arduino Nano ESP32 in the Arduino IDE and Serial Monitor 115200.
// Start a fresh receiver capture after a reset/reconnect or counter rollover.

#include <Arduino.h>

const uint32_t EMIT_INTERVAL_MS = 1000;
uint32_t last_emit_ms = 0;
uint32_t sequence_number = 0;

void setup() {
  Serial.begin(115200);
}

void loop() {
  const uint32_t now_ms = millis();
  if (static_cast<uint32_t>(now_ms - last_emit_ms) < EMIT_INTERVAL_MS) {
    return;
  }
  last_emit_ms = now_ms;

  // Deliberately fabricated values: the board is not measuring a person.
  const unsigned int synthetic_heart_rate = 70 + (sequence_number % 5);
  Serial.print("{\"schema_version\":\"0.1.0\",\"device_id\":\"synthetic-nano-001\",\"seq\":");
  Serial.print(sequence_number);
  Serial.print(",\"monotonic_ms\":");
  Serial.print(now_ms);
  Serial.print(",\"source\":\"simulated\",\"heart_rate_bpm\":");
  Serial.print(synthetic_heart_rate);
  Serial.println(",\"assay_ready\":false}");
  sequence_number++;
}
