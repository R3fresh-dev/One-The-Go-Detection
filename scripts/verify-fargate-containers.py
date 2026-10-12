#!/usr/bin/env python3
"""Run actual Fargate nginx container tests and emit mandatory JUnit evidence."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import time
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


class EvidenceResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rows = []

    def startTest(self, test):
        self.started = time.monotonic()
        super().startTest(test)

    def record(self, test, status, details=''):
        self.rows.append((test.id(), status, time.monotonic() - getattr(self, 'started', time.monotonic()), details))

    def addSuccess(self, test):
        self.record(test, 'passed')
        super().addSuccess(test)

    def addFailure(self, test, error):
        self.record(test, 'failure', self._exc_info_to_string(error, test))
        super().addFailure(test, error)

    def addError(self, test, error):
        self.record(test, 'error', self._exc_info_to_string(error, test))
        super().addError(test, error)

    def addSkip(self, test, reason):
        self.record(test, 'skipped', reason)
        super().addSkip(test, reason)

    def addSubTest(self, test, subtest, error):
        if error is not None:
            status = 'failure' if issubclass(error[0], test.failureException) else 'error'
            self.record(subtest, status, self._exc_info_to_string(error, test))
        super().addSubTest(test, subtest, error)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=ROOT / 'reports' / 'fargate-containers.xml')
    args = parser.parse_args()
    path = ROOT / 'infra/test/test_fargate_containers.py'
    specification = importlib.util.spec_from_file_location('otgd_fargate_container_verification', path)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    result = unittest.TextTestRunner(verbosity=2, resultclass=EvidenceResult).run(suite)
    failures = sum(status == 'failure' for _, status, _, _ in result.rows)
    errors = sum(status == 'error' for _, status, _, _ in result.rows)
    skipped = sum(status == 'skipped' for _, status, _, _ in result.rows)
    root = ET.Element('testsuite', name='fargate-containers', tests=str(len(result.rows)),
        failures=str(failures), errors=str(errors), skipped=str(skipped))
    for name, status, duration, details in result.rows:
        case = ET.SubElement(root, 'testcase', name=name, time=f'{duration:.6f}')
        if status != 'passed':
            ET.SubElement(case, status).text = details
    args.report.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(args.report, encoding='utf-8', xml_declaration=True)
    if not result.wasSuccessful() or result.skipped or result.testsRun != 13:
        raise SystemExit('Actual Fargate container checks must execute all 13 cases without skips')
    print('All 13 actual Fargate nginx container cases passed; evidence: ' + str(args.report))


if __name__ == '__main__':
    main()
