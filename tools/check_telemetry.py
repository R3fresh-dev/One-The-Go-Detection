"""Check a saved synthetic serial capture; this does not open a serial port."""

import argparse
import json
from pathlib import Path

from spec_validation import validate_telemetry


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="NDJSON capture saved from Serial Monitor")
    args = parser.parse_args()
    records = [json.loads(line) for line in args.path.read_text().splitlines() if line.strip()]
    count = validate_telemetry(records)
    print(f"PASS: {count} synthetic telemetry records; no chemical measurement or impairment estimate.")
