"""Require real, passing XCTest lifecycles alongside SwiftPM's xUnit report.

SwiftPM 6.3 emits XCTest xUnit only through its parallel runner. That report
records the test process exit status, which can treat an XCTSkip as successful.
Keep the verbose native log and require each reported test to start and pass;
a missing, skipped, failed, duplicated or ambiguous lifecycle fails closed.
"""
import argparse
from collections import Counter
from pathlib import Path
import re
import xml.etree.ElementTree as ET


LIFECYCLE = re.compile(r"Test Case '(?P<identity>-\[[^\]\r\n]+\])' (?P<status>started|passed|failed|skipped)\b")
FORBIDDEN = re.compile(r"Test Case '[^\r\n]+' (?:failed|skipped)\b|\b(?:expected[\s_-]*failures?|XCTExpectFailure)\b", re.IGNORECASE)


def require_xctest(report_path, log_path):
    try:
        root = ET.parse(report_path).getroot()
        log = Path(log_path).read_text(encoding='utf-8')
    except (OSError, UnicodeError, ET.ParseError):
        raise RuntimeError('Missing or invalid current XCTest report or verbose log') from None
    if root.tag not in ('testsuite', 'testsuites'):
        raise RuntimeError('Invalid XCTest xUnit root')
    cases = root.findall('.//testcase')
    identities = []
    for case in cases:
        classname, name = case.get('classname', ''), case.get('name', '')
        if not re.fullmatch(r'(?:[A-Za-z_][A-Za-z0-9_]*\.)*[A-Za-z_][A-Za-z0-9_]*', classname) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', name):
            raise RuntimeError('Missing or ambiguous XCTest classname/name')
        if any(case.find(tag) is not None for tag in ('skipped', 'failure', 'error')):
            raise RuntimeError('Every mandatory XCTest must execute and pass')
        identities.append(f'-[{classname} {name}]')
    if not identities or len(set(identities)) != len(identities):
        raise RuntimeError('Missing or duplicated XCTest report cases')
    if FORBIDDEN.search(log):
        raise RuntimeError('Skipped, failed or expected-failure XCTest evidence is forbidden')
    starts, passes = Counter(), Counter()
    for event in LIFECYCLE.finditer(log):
        identity, status = event.group('identity', 'status')
        if status == 'started':
            starts[identity] += 1
        elif status == 'passed':
            if starts[identity] != 1 or passes[identity]:
                raise RuntimeError('XCTest must start exactly once before passing exactly once')
            passes[identity] += 1
        else:
            raise RuntimeError('Every mandatory XCTest must execute and pass')
    expected = Counter(identities)
    if starts != expected or passes != expected:
        raise RuntimeError('Current XCTest log must contain every reported start and pass exactly once')
    print(f'{len(identities)} native XCTest cases executed and passed without skips')
    return len(identities)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report')
    parser.add_argument('log')
    args = parser.parse_args()
    require_xctest(args.report, args.log)


if __name__ == '__main__':
    main()
