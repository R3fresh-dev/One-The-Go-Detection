import importlib.util
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('health_gate', ROOT / 'scripts/check-canonical-health.py')
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)


def rows():
    return [{'service': service, 'project': 'otgd-local', 'oneoff': 'False', 'state': 'running', 'running': True,
             'health': 'healthy', 'exit_code': 0} for service in h.RUNNING] + [
        {'service': service, 'project': 'otgd-local', 'oneoff': 'False', 'state': 'exited', 'running': False,
         'health': None, 'exit_code': 0} for service in h.COMPLETED]


class HealthGateTest(unittest.TestCase):
    def test_all_five_long_services_and_two_successful_initializers_required(self):
        self.assertEqual(h.validate(rows())['status'], 'passed')
        for values in (rows()[:-1], rows() + rows()[:1], None):
            with self.assertRaises(h.HealthFailure): h.validate(values)

    def test_no_missing_health_running_initializer_failed_migration_or_oneoff_counts(self):
        for service, changes in [('worker', {'health': None}), ('api', {'health': 'unhealthy'}), ('identity', {'state': 'restarting'}),
                ('postgres', {'running': False}), ('migrate', {'exit_code': 1}), ('resource-init', {'state': 'running'}),
                ('migrate', {'exit_code': False}), ('api', {'oneoff': 'True'}), ('api', {'project': 'other'})]:
            values = rows()
            next(row for row in values if row['service'] == service).update(changes)
            with self.subTest(service=service, changes=changes), self.assertRaises(h.HealthFailure): h.validate(values)

    def test_filtered_inspect_never_reads_environment_or_health_log(self):
        calls = []
        def run(command, **kwargs):
            calls.append(command)
            if command[1] == 'compose': return SimpleNamespace(stdout='\n'.join(format(i, '064x') for i in range(7)))
            self.assertNotIn('.Config.Env', command[3]); self.assertNotIn('.State.Health.Log', command[3])
            return SimpleNamespace(stdout='\n'.join(json.dumps(row) for row in rows()))
        self.assertEqual(h.inspect(run=run, licensed=True)['status'], 'passed')
        self.assertIn(str(ROOT / 'infra/local/compose.localstack-licensed.yml'), calls[0])
        with self.assertRaises(h.HealthFailure): h.inspect('invalid project', run=run)

    def test_docker_failure_missing_inventory_and_invalid_json_are_explicit_failures(self):
        def denied(*args, **kwargs): raise subprocess.CalledProcessError(1, 'docker', stderr='secret must not be printed')
        with self.assertRaisesRegex(h.HealthFailure, 'DOCKER_STATE_UNAVAILABLE'): h.inspect(run=denied)
        for output in ('', 'bad-id', ' '.join('a' * 64 for _ in range(7))):
            def run(command, **kwargs): return SimpleNamespace(stdout=output if command[1] == 'compose' else 'invalid JSON')
            with self.assertRaises(h.HealthFailure): h.inspect(run=run)

    def test_cli_preserves_failure_exit_without_vendor_secret_output(self):
        with patch.object(h, 'inspect', return_value={'status': 'passed'}), patch('sys.stdout', new_callable=__import__('io').StringIO) as output:
            self.assertEqual(h.main([]), 0)
            self.assertEqual(json.loads(output.getvalue()), {'status': 'passed'})
        with patch.object(h, 'inspect', side_effect=h.HealthFailure('REQUIRED_SERVICE_MISSING')), patch('sys.stderr', new_callable=__import__('io').StringIO) as output:
            self.assertEqual(h.main([]), 1)
            self.assertEqual(json.loads(output.getvalue()), {'status': 'failed', 'reason': 'REQUIRED_SERVICE_MISSING'})
