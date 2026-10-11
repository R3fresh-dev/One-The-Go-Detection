"""Mandatory evidence must reject missing, skipped and exact-80% results."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
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


class RetainedComposeEnvironmentTest(unittest.TestCase):
 def setUp(self):
  self.environment={
   'OTGD_TOMBSTONE_KEY':'disposable-database-fixture-only',
   'OTGD_DATABASE_URL':'postgresql+psycopg://fictional@localhost/otgd_ci',
   'OTGD_LOCAL_API_ORIGIN':'http://127.0.0.1:8000',
   'OTGD_LOCAL_APP_PASSWORD':'fictional-local-password',
   'DOCKER_CONFIG':'/fictional/docker-config',
   'HTTPS_PROXY':'http://fictional-proxy:8080',
  }

 def test_disposable_test_commands_keep_their_explicit_identity(self):
  with patch.dict(os.environ,self.environment,clear=True),patch.object(gate.subprocess,'run') as run:
   gate.call('python','pytest',env={'OTGD_ENVIRONMENT':'test'})
   actual=run.call_args.kwargs['env']
   self.assertEqual(actual['OTGD_TOMBSTONE_KEY'],self.environment['OTGD_TOMBSTONE_KEY'])
   self.assertEqual(actual['OTGD_ENVIRONMENT'],'test')

 def test_retained_commands_remove_the_key_after_merging_without_mutating_the_parent(self):
  with patch.dict(os.environ,self.environment,clear=True),patch.object(gate.subprocess,'run') as run:
   gate.call('docker','compose',env={'OTGD_TOMBSTONE_KEY':'another-test-key','CUSTOM_OPTION':'preserved'},local_compose=True)
   actual=run.call_args.kwargs['env']
   self.assertNotIn('OTGD_TOMBSTONE_KEY',actual)
   self.assertEqual(actual['CUSTOM_OPTION'],'preserved')
   for key,value in self.environment.items():
    if key!='OTGD_TOMBSTONE_KEY':
     self.assertEqual(actual[key],value)
   self.assertEqual(os.environ['OTGD_TOMBSTONE_KEY'],self.environment['OTGD_TOMBSTONE_KEY'])

 def test_every_compose_gate_is_isolated_including_nested_scripts_and_performance(self):
  for name,count in [('docker-health',1),('localstack-api',4),('performance',1)]:
   with self.subTest(gate=name),tempfile.TemporaryDirectory() as directory:
    with patch.dict(os.environ,self.environment,clear=True),patch.object(gate,'REPORTS',Path(directory)),patch.object(gate.sys,'argv',['ci_gate.py',name]),patch.object(gate.subprocess,'run',return_value=SimpleNamespace(stdout='{"status":"fictional-command-test"}')) as run,patch('builtins.print'):
     gate.main()
     self.assertEqual(run.call_count,count)
     for invoked in run.call_args_list:
      actual=invoked.kwargs['env']
      self.assertNotIn('OTGD_TOMBSTONE_KEY',actual)
      self.assertEqual(actual['OTGD_LOCAL_API_ORIGIN'],self.environment['OTGD_LOCAL_API_ORIGIN'])
      self.assertEqual(actual['DOCKER_CONFIG'],self.environment['DOCKER_CONFIG'])
      self.assertEqual(actual['HTTPS_PROXY'],self.environment['HTTPS_PROXY'])

if __name__=='__main__':unittest.main()
