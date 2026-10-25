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

 def test_release_tool_cannot_hide_below_overall_coverage_or_use_exclusions(self):
  with tempfile.TemporaryDirectory() as directory:
   path=Path(directory)/'coverage.json';source='apps/mobile/modules/scripts/store_release.py'
   for files in ({}, {'another.py':{'summary':{'num_statements':100,'covered_lines':100,'excluded_lines':0}}}, {source:{'summary':{'num_statements':100,'covered_lines':80,'excluded_lines':0}}}, {source:{'summary':{'num_statements':100,'covered_lines':100,'excluded_lines':1,'num_excluded':0}}}, {source:{'summary':{'num_statements':100,'covered_lines':100,'excluded_lines':0,'num_excluded':1}}}, {source:{'summary':{'num_statements':0,'covered_lines':0,'excluded_lines':0}}}):
    path.write_text(json.dumps({'totals':{'num_statements':1000,'covered_lines':1000},'files':files}))
    with self.assertRaises(RuntimeError):gate.require_file_coverage(path,source)
   path.write_text(json.dumps({'files':{source:{'summary':{'num_statements':1000,'covered_lines':801,'excluded_lines':0}}}}))
   self.assertGreater(gate.require_file_coverage(path,source),80)


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
    with patch.dict(os.environ,self.environment,clear=True),patch.object(gate,'REPORTS',Path(directory)),patch.object(gate,'worker_interruption_gate') as worker,patch.object(gate,'live_browser_gate') as browser,patch.object(gate.sys,'argv',['ci_gate.py',name]),patch.object(gate.subprocess,'run',return_value=SimpleNamespace(stdout='{"status":"fictional-command-test"}')) as run,patch('builtins.print'):
     gate.main()
     self.assertEqual(run.call_count,count)
     self.assertEqual(worker.call_count,1 if name=='localstack-api' else 0)
     self.assertEqual(browser.call_count,1 if name=='localstack-api' else 0)
     for invoked in run.call_args_list:
      actual=invoked.kwargs['env']
      self.assertNotIn('OTGD_TOMBSTONE_KEY',actual)
      self.assertEqual(actual['OTGD_LOCAL_API_ORIGIN'],self.environment['OTGD_LOCAL_API_ORIGIN'])
      self.assertEqual(actual['DOCKER_CONFIG'],self.environment['DOCKER_CONFIG'])
      self.assertEqual(actual['HTTPS_PROXY'],self.environment['HTTPS_PROXY'])



class LiveAcceptanceGateTest(unittest.TestCase):
 def test_worker_source_inventory_includes_nested_python_and_contracts(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory)
   files=('infra/local/worker_interrupt_probe.py','infra/local/worker_interrupt_gate.py',
          'services/api/otgd/worker.py','services/api/otgd/nested/runtime.py',
          'contracts/application/nested/schema.json')
   for name in files:
    path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b'abc')
   (root/'services/api/otgd/ignored.pyc').write_bytes(b'not executable source')
   with patch.object(gate,'ROOT',root):actual=gate.worker_source_manifest()
   self.assertEqual(actual,{name:'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad' for name in files})

 def test_worker_report_requires_passed_fictional_current_source_evidence(self):
  with tempfile.TemporaryDirectory() as directory:
   report=Path(directory)/'worker.json'
   with self.assertRaises(RuntimeError):gate.require_worker_report(report)
   current={'infra/local/worker_interrupt_probe.py':'a'*64}
   good={'status':'passed','fictional':True,'source_manifest_before':current,'source_manifest_after':current}
   with patch.object(gate,'worker_source_manifest',return_value=current):
    for value in ({}, {**good,'status':'failed'}, {**good,'status':'running'}, {**good,'fictional':False}, {**good,'source_manifest_before':{}}, {**good,'source_manifest_after':{'other.py':'b'*64}}):
     report.write_text(json.dumps(value))
     with self.subTest(value=value),self.assertRaises(RuntimeError):gate.require_worker_report(report)
    report.write_text('invalid')
    with self.assertRaises(RuntimeError):gate.require_worker_report(report)
    report.write_text(json.dumps(good))
    gate.require_worker_report(report)

 def test_worker_dispatch_uses_fresh_report_readonly_source_and_retained_environment(self):
  with tempfile.TemporaryDirectory() as directory:
   reports=Path(directory); commands=[]
   def invoke(*args,**kwargs):
    commands.append((args,kwargs))
    output=Path(args[args.index('--output')+1])
    self.assertEqual(output.parent,Path('/app/reports'))
    self.assertRegex(output.name,r'^worker-interrupt-[0-9a-f]{32}\.json$')
    (reports/output.name).write_text(json.dumps({'status':'passed','fictional':True,'source_manifest_before':{'probe.py':'a'},'source_manifest_after':{'probe.py':'a'}}))
   with patch.object(gate,'REPORTS',reports),patch.object(gate,'worker_source_manifest',return_value={'probe.py':'a'}),patch.object(gate,'call',side_effect=invoke):
    gate.worker_interruption_gate();gate.worker_interruption_gate()
   self.assertEqual(len(list(reports.glob('worker-interrupt-*.json'))),2)
   for args,kwargs in commands:
    self.assertTrue(kwargs['local_compose'])
    self.assertIn('--rm',args);self.assertIn('--no-deps',args)
    self.assertIn('migrate',args);self.assertNotIn('api',args)
    self.assertIn('/app/infra/local/worker_interrupt_gate.py',args)
    self.assertIn('--confirm-fictional-workspace',args)
    self.assertEqual(args[args.index('--project-name',3)+1],'otgd-local')
    self.assertIn(str(ROOT/'infra/local')+':/app/infra/local:ro',args)
    self.assertIn(str(ROOT/'services/api/otgd')+':/app/services/api/otgd:ro',args)
    self.assertIn(str(reports)+':/app/reports:rw',args)

 def test_worker_dispatch_refuses_existing_report_before_running_any_command(self):
  with tempfile.TemporaryDirectory() as directory:
   reports=Path(directory);report=reports/('worker-interrupt-'+'a'*32+'.json');report.write_text('preserved')
   with patch.object(gate,'REPORTS',reports),patch.object(gate,'uuid4',return_value=SimpleNamespace(hex='a'*32)),patch.object(gate,'call') as call:
    with self.assertRaises(RuntimeError):gate.worker_interruption_gate()
   call.assert_not_called();self.assertEqual(report.read_text(),'preserved')

 def test_browser_dispatch_prepares_host_ledger_before_separate_maintenance_provision(self):
  with tempfile.TemporaryDirectory() as directory:
   reports=Path(directory);manifest=reports/'private-ledger.json';calls=[]
   def invoke(*args,**kwargs):
    calls.append((args,kwargs))
    if '/app/infra/local/browser_fixture.py' in args:
     self.assertTrue(manifest.is_file(),'Host ledger must exist before Docker bind')
     self.assertEqual(manifest.read_text(),'preserve-on-retry')
    elif 'infra/local/browser_fixture.py' in args:
     manifest.write_text('preserve-on-retry')
    elif '--config=playwright.live.config.ts' in args:
     Path(kwargs['env']['PLAYWRIGHT_JUNIT_OUTPUT_FILE']).write_text('<testsuite><testcase name="live"/></testsuite>')
   with patch.dict(os.environ,{'OTGD_BROWSER_FIXTURE':str(manifest)}),patch.object(gate,'REPORTS',reports),patch.object(gate,'call',side_effect=invoke):gate.live_browser_gate()
   self.assertEqual(len(calls),4)
   prepare,provision,export,browser=[args for args,_ in calls]
   self.assertNotIn('--provision-governed',prepare)
   self.assertIn('--provision-governed',provision)
   self.assertIn('migrate',provision);self.assertIn('--no-deps',provision)
   self.assertIn(str(manifest)+':/tmp/otgd-browser-fixture.json:rw',provision)
   self.assertNotIn(str(manifest.parent)+':/tmp:rw',provision)
   self.assertIn(str(ROOT/'infra/local')+':/app/infra/local:ro',provision)
   self.assertIn(str(ROOT/'services/api/otgd')+':/app/services/api/otgd:ro',provision)
   self.assertTrue(calls[1][1]['local_compose'])
   self.assertIn('export:web',export)
   self.assertEqual(calls[3][1]['env']['OTGD_BROWSER_FIXTURE'],str(manifest))
   self.assertIn('--reporter=line,junit',browser)
   self.assertEqual(manifest.read_text(),'preserve-on-retry')

 def test_browser_gate_rejects_missing_failed_and_skipped_current_report(self):
  for result in (None,'<testsuite/>','<testsuite><testcase><skipped/></testcase></testsuite>','<testsuite><testcase><failure/></testcase></testsuite>'):
   with self.subTest(result=result),tempfile.TemporaryDirectory() as directory:
    report=Path(directory)/'authenticated-live.xml'
    report.write_text('<testsuite><testcase name="stale-pass"/></testsuite>')
    def invoke(*args,**kwargs):
     if '--config=playwright.live.config.ts' in args and result is not None:
      Path(kwargs['env']['PLAYWRIGHT_JUNIT_OUTPUT_FILE']).write_text(result)
    with patch.object(gate,'REPORTS',Path(directory)),patch.object(gate,'call',side_effect=invoke):
     with self.assertRaises(RuntimeError):gate.live_browser_gate()

if __name__=='__main__':unittest.main()
