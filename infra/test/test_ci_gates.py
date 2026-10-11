"""Mandatory evidence must reject missing, skipped and exact-80% results."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('ci_gate',ROOT/'scripts/ci_gate.py');gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)

class EvidenceTest(unittest.TestCase):
 def test_unittest_skips_and_expected_failures_are_rejected(self):
  for label in ['empty','skip','expected','unexpected','failure']:
   result=unittest.TestResult()
   if label!='empty':result.testsRun=1
   if label=='skip':result.skipped.append(('required','disabled'))
   if label=='expected':result.expectedFailures.append(('required','failure'))
   if label=='unexpected':result.unexpectedSuccesses.append('required')
   if label=='failure':result.failures.append(('required','failure'))
   with self.subTest(label=label),self.assertRaises(RuntimeError):gate.require_unittest(result)
  result=unittest.TestResult();result.testsRun=1
  gate.require_unittest(result)
 def test_every_case_must_execute(self):
  with tempfile.TemporaryDirectory() as directory:
   path=Path(directory)/'tests.xml'
   for content in ['<testsuites/>','<testsuite><testcase><skipped/></testcase></testsuite>','<testsuite><testcase><failure/></testcase></testsuite>','invalid','<testsuite><testcase><error/></testcase></testsuite>']:
    path.write_text(content)
    with self.assertRaises(RuntimeError):gate.require_junit(path)
   path.write_text('<testsuites><testsuite><testcase name="actual-test"/></testsuite></testsuites>')
   self.assertEqual(gate.require_junit(path),1)
   path.unlink()
   with self.assertRaises(RuntimeError):gate.require_junit(path)
 def test_coverage_must_be_strictly_above_eighty(self):
  with tempfile.TemporaryDirectory() as directory:
   path=Path(directory)/'coverage.json'
   for covered,total in [(0,0),(80,100),(799,1000)]:
    path.write_text(json.dumps({'totals':{'num_statements':total,'covered_lines':covered}}))
    with self.assertRaises(RuntimeError):gate.require_coverage(path)
   path.write_text(json.dumps({'totals':{'num_statements':1000,'covered_lines':801}}))
   self.assertGreater(gate.require_coverage(path),80)

if __name__=='__main__':unittest.main()
