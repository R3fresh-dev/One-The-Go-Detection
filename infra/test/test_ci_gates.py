"""Mandatory evidence must reject missing, skipped and exact-80% results."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
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

 def test_release_tool_cannot_hide_below_overall_coverage_or_use_exclusions(self):
  with tempfile.TemporaryDirectory() as directory:
   path=Path(directory)/'coverage.json';source='apps/mobile/modules/scripts/store_release.py'
   for files in ({}, {'another.py':{'summary':{'num_statements':100,'covered_lines':100,'excluded_lines':0}}}, {source:{'summary':{'num_statements':100,'covered_lines':80,'excluded_lines':0}}}, {source:{'summary':{'num_statements':100,'covered_lines':100,'excluded_lines':1,'num_excluded':0}}}, {source:{'summary':{'num_statements':100,'covered_lines':100,'excluded_lines':0,'num_excluded':1}}}, {source:{'summary':{'num_statements':0,'covered_lines':0,'excluded_lines':0}}}):
    path.write_text(json.dumps({'totals':{'num_statements':1000,'covered_lines':1000},'files':files}))
    with self.assertRaises(RuntimeError):gate.require_file_coverage(path,source)
   path.write_text(json.dumps({'files':{source:{'summary':{'num_statements':1000,'covered_lines':801,'excluded_lines':0}}}}))
   self.assertGreater(gate.require_file_coverage(path,source),80)

 def test_serverless_gate_rejects_missing_duplicate_extra_and_excluded_sources(self):
  def valid_files():
   return {source:{'summary':{'num_statements':100,'covered_lines':81,'excluded_lines':0,'num_excluded':0},'excluded_lines':[]} for source in gate.SERVERLESS_DEPLOYMENT_SOURCES}
  with tempfile.TemporaryDirectory() as directory:
   path=Path(directory)/'coverage.json'
   for label in ('missing','different','duplicate','extra','exact-eighty','zero-statements','summary-exclusion','legacy-exclusion','actual-exclusion'):
    files=valid_files();source=gate.SERVERLESS_DEPLOYMENT_SOURCES[0]
    if label=='missing':files.pop(source)
    elif label=='different':files['deploy/unrelated.py']=files.pop(source)
    elif label=='duplicate':files['deploy/./serverless.py']=files[source]
    elif label=='extra':files['deploy/unrelated.py']=files[source]
    elif label=='exact-eighty':files[source]['summary']['covered_lines']=80
    elif label=='zero-statements':files[source]['summary'].update(num_statements=0,covered_lines=0)
    elif label=='summary-exclusion':files[source]['summary']['excluded_lines']=1
    elif label=='legacy-exclusion':files[source]['summary']['num_excluded']=1
    elif label=='actual-exclusion':files[source]['excluded_lines']=[1]
    path.write_text(json.dumps({'totals':{'num_statements':1000,'covered_lines':999},'files':files}))
    with self.subTest(label=label),self.assertRaises(RuntimeError):gate.require_serverless_coverage(path)
   path.write_text(json.dumps({'files':valid_files()}))
   self.assertEqual(gate.require_serverless_coverage(path),dict.fromkeys(gate.SERVERLESS_DEPLOYMENT_SOURCES,81.0))


class InfrastructureCoverageLifecycleTest(unittest.TestCase):
 def exercise(self, *, discovery_error=False, low_coverage=False):
  with tempfile.TemporaryDirectory() as directory:
   reports=Path(directory);outer=reports/'unit-coverage.json';outer.write_text('preserved API/store evidence')
   json_report=reports/'infra-serverless-coverage.json';json_report.write_text('stale evidence')
   xml_report=reports/'infra-serverless-coverage.xml';xml_report.write_text('stale XML')
   chronology=[];coverage=Mock()
   coverage.erase.side_effect=lambda:chronology.append('erase')
   coverage.start.side_effect=lambda:chronology.append('start')
   coverage.stop.side_effect=lambda:chronology.append('stop')
   coverage.save.side_effect=lambda:chronology.append('save')
   def discover(*args,**kwargs):
    chronology.append('discover')
    self.assertFalse(json_report.exists());self.assertFalse(xml_report.exists())
    if discovery_error:raise RuntimeError('Discovery failed before execution')
    return unittest.TestSuite()
   def write_json(**kwargs):
    files={source:{'summary':{'num_statements':100,'covered_lines':81,'excluded_lines':0,'num_excluded':0},'excluded_lines':[]} for source in gate.SERVERLESS_DEPLOYMENT_SOURCES}
    if low_coverage:files[gate.SERVERLESS_DEPLOYMENT_SOURCES[-1]]['summary']['covered_lines']=80
    Path(kwargs['outfile']).write_text(json.dumps({'files':files}))
   coverage.json_report.side_effect=write_json
   coverage.xml_report.side_effect=lambda **kwargs:Path(kwargs['outfile']).write_text('<coverage/>')
   result=unittest.TestResult();result.testsRun=1
   with patch.object(gate,'REPORTS',reports),patch('coverage.Coverage',return_value=coverage) as constructor,patch.object(unittest.defaultTestLoader,'discover',side_effect=discover),patch.object(unittest,'TextTestRunner') as runner,patch.object(gate,'pytest_gate') as sdk:
    runner.return_value.run.return_value=result
    if discovery_error or low_coverage:
     with self.assertRaises(RuntimeError):gate.infrastructure_unit_gate()
     sdk.assert_not_called()
    else:
     gate.infrastructure_unit_gate()
     sdk.assert_called_once_with('secure-sdk','infra/test/test_secure_reader_build.py')
    constructor.assert_called_once_with(source=[str(gate.ROOT/'deploy')],config_file=False,data_file=str(reports/'.coverage.infra-serverless'))
    self.assertEqual(chronology,['erase','start','discover','stop','save'])
    sources=[str(gate.ROOT/source) for source in gate.SERVERLESS_DEPLOYMENT_SOURCES]
    coverage.json_report.assert_called_once_with(morfs=sources,outfile=str(json_report))
    coverage.xml_report.assert_called_once_with(morfs=sources,outfile=str(xml_report))
    self.assertEqual(outer.read_text(),'preserved API/store evidence')
    self.assertTrue(json_report.exists());self.assertEqual(xml_report.read_text(),'<coverage/>')

 def test_measurement_starts_before_discovery_and_keeps_existing_evidence_and_sdk(self):
  self.exercise()

 def test_discovery_failure_stops_tracing_and_never_runs_the_sdk_gate(self):
  self.exercise(discovery_error=True)

 def test_one_deployment_source_at_eighty_blocks_the_sdk_gate(self):
  self.exercise(low_coverage=True)


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
