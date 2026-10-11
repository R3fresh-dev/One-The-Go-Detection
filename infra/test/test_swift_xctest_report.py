"""The native report adapter must reject SwiftPM's successful skipped process."""
import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('swift_xctest', ROOT/'scripts/verify-swift-xctest.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
CLASS = 'OTGDReactionCoreTests.ReactionCoreTests'
NAME = 'testFrozenLiteralSchedulesAndHashes'
IDENTITY = f'-[{CLASS} {NAME}]'
REPORT = f'<testsuites><testsuite tests="1"><testcase classname="{CLASS}" name="{NAME}"/></testsuite></testsuites>'
START = f"Test Case '{IDENTITY}' started.\n"
PASS = f"Test Case '{IDENTITY}' passed (0.003 seconds).\n"


class NativeXCTestEvidenceTest(unittest.TestCase):
    def verify(self, report=REPORT, log=START+PASS):
        with tempfile.TemporaryDirectory() as directory:
            report_path, log_path = Path(directory)/'tests.xml', Path(directory)/'tests.log'
            if report is not None:
                report_path.write_text(report)
            if log is not None:
                log_path.write_text(log)
            return gate.require_xctest(report_path, log_path)

    def test_actual_darwin_lifecycle_with_runner_noise_passes(self):
        log = 'Build complete!\n[1/1] Testing core\n'+START+PASS+'Executed 1 test, with 0 failures (0 unexpected)\n'
        self.assertEqual(self.verify(log=log), 1)

    def test_missing_invalid_empty_and_ambiguous_report_fail(self):
        reports = [None, 'invalid', '<testsuites/>', REPORT.replace('testsuites', 'unknown'), REPORT.replace(f'classname="{CLASS}"', ''),
                   REPORT.replace(NAME, 'testName ambiguous'), REPORT.replace(CLASS, 'Ambiguous Class'),
                   REPORT.replace(CLASS, 'Ambiguous..Class'),
                   REPORT.replace('</testsuite>', f'<testcase classname="{CLASS}" name="{NAME}"/></testsuite>')]
        for report in reports:
            with self.subTest(report=report), self.assertRaises(RuntimeError):
                self.verify(report=report)

    def test_report_failures_and_skips_fail(self):
        for outcome in ['skipped', 'failure', 'error']:
            with self.subTest(outcome=outcome), self.assertRaises(RuntimeError):
                self.verify(report=REPORT.replace('/>', f'><{outcome}/></testcase>'))

    def test_skipped_successful_process_and_expected_failure_fail(self):
        logs = [START+PASS.replace('passed', 'skipped'), START+PASS.replace('passed', 'failed')]
        logs += [START+PASS+marker+' recorded\n' for marker in ['Expected failure', 'expected-failure', 'ExpectedFailure', 'XCTExpectFailure']]
        for log in logs:
            with self.subTest(log=log), self.assertRaises(RuntimeError):
                self.verify(log=log)

    def test_missing_truncated_duplicate_reordered_and_unreported_lifecycles_fail(self):
        logs = [None, '', START, PASS, PASS+START, START+START+PASS, START+PASS+PASS,
                START+PASS+(START+PASS).replace(NAME, 'testUnreportedCase')]
        for log in logs:
            with self.subTest(log=log), self.assertRaises(RuntimeError):
                self.verify(log=log)

    def test_native_log_requires_every_reported_case(self):
        two_cases = REPORT.replace('</testsuite>', f'<testcase classname="{CLASS}" name="testSecondCase"/></testsuite>')
        with self.assertRaises(RuntimeError):
            self.verify(report=two_cases)
        self.assertEqual(self.verify(report=two_cases, log=START+PASS+(START+PASS).replace(NAME, 'testSecondCase')), 2)


if __name__ == '__main__':
    unittest.main()
