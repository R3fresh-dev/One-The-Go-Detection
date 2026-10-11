"""Check the feature specification inventory; this is not implementation evidence."""

from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CHANGE = ROOT / "openspec/changes/production-mobile-platform"


def main() -> None:
    ids: set[str] = set()
    inventory = []
    for path in sorted((CHANGE / "specs").glob("*/spec.md")):
        text = path.read_text()
        assert "## ADDED Requirements" in text, path
        blocks = re.split(r"^### Requirement: ", text, flags=re.M)[1:]
        scenario_total = 0
        for block in blocks:
            identifier = re.match(r"AND-[A-Z]+-\d{3}\b", block)
            assert identifier, f"Missing requirement ID: {path}"
            key = identifier[0]
            assert key not in ids, f"Duplicate ID: {key}"
            ids.add(key)
            normative = block.split("#### Scenario:", 1)[0].split("\n", 1)[1]
            assert re.search(r"\b(SHALL|MUST)\b", normative), key
            scenarios = re.split(r"^#### Scenario: ", block, flags=re.M)[1:]
            assert len(scenarios) >= 2, f"Positive/negative scenarios missing: {key}"
            names = [scenario.splitlines()[0] for scenario in scenarios]
            assert len(set(names)) == len(names), f"Duplicate scenario title: {key}"
            for scenario in scenarios:
                for clause in ("GIVEN", "WHEN", "THEN"):
                    assert f"**{clause}**" in scenario, f"{key}: {clause} missing"
            scenario_total += len(scenarios)
        assert "iOS" in text, f"iOS parity missing: {path}"
        inventory.append({"feature": path.parent.name,
                          "requirements": len(blocks), "scenarios": scenario_total})
    assert len(inventory) == 20, "Expected one capability per 20 application features"
    assert len(ids) >= 140, "Requirement inventory unexpectedly shrank"
    for required in ("proposal.md", "design.md", "tasks.md", "README.md"):
        assert (CHANGE / required).is_file(), required
    print(json.dumps({"features": inventory, "requirement_count": len(ids),
                      "scenario_count": sum(i["scenarios"] for i in inventory),
                      "status": "passed", "scope": "specification structure only"}, indent=2))


if __name__ == "__main__":
    main()
