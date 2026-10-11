# Selected vendor source integration

The original SparkFun Beerware attribution and licensing remain in the source and UPSTREAM_README.md. SOURCE.json fixes the official commit and original/compiled hashes. Manufacturer command families, command values, FIFO layouts and numeric decoding remain unchanged.

The integration exposes I/O status and an attach/application-mode entry so the caller executes the vendor reset10ms/boot1000ms sequence without blocking cancellation. The configured1000ms algorithm warmup is deferred to that same state machine. Selected I2C primitives reject write/short-read failures and clear data before failed reads. Combined data initialize all fields and reject failed FIFO reads, preventing stale buffer reuse. Hub firmware version reads fail closed. The SDK returns whole bpm after integer division of the hardware tenth-bpm value; no fractional precision is invented.

No driver or test claims SparkFun algorithm accuracy, confidence calibration, exact optical sample timestamps, clinical fitness or physical board execution. Confidence is vendor signal-quality percentage.
