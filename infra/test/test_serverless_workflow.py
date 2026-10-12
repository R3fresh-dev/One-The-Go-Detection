"""Run the workflow admission program against failed/stale gate metadata.

These checks validate the credential boundary without contacting AWS or GitHub.
Live release evidence remains the responsibility of deploy.provenance.
"""
import ast
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import yaml

from deploy.provenance import Gate, REPOSITORY, WORKFLOW_PATH

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / '.github/workflows/deploy-serverless.yml'
REVISION = 'a' * 40


def workflow_admission():
    workflow = yaml.safe_load(WORKFLOW.read_text())
    step = next(step for step in workflow['jobs']['deploy']['steps'] if step.get('id') == 'admission')
    program = step['run'].split("<<'PYCODE'\n", 1)[1].rsplit('\nPYCODE', 1)[0]
    # Compile exactly the Python shipped in Actions; its __main__ block stays idle.
    namespace = {'__name__': 'serverless_workflow_fixture'}
    exec(compile(ast.parse(program), str(WORKFLOW), 'exec'), namespace)
    return workflow, namespace


def gate_run(run_id, *, conclusion='success', status='completed', **changes):
    return {'id': run_id, 'head_sha': REVISION, 'path': WORKFLOW_PATH,
            'event': 'push', 'head_branch': 'main', 'status': status,
            'conclusion': conclusion, **changes}


class ServerlessWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.workflow, self.program = workflow_admission()

    def test_newer_failed_or_running_attempt_never_falls_back_to_old_success(self):
        for newer in (gate_run(20, conclusion='failure'),
                      gate_run(20, conclusion=None, status='in_progress'),
                      gate_run(20, conclusion='cancelled')):
            self.program['github_json'] = Mock(return_value={'workflow_runs': [gate_run(10), newer]})
            with self.subTest(newer=newer), self.assertRaisesRegex(Gate, 'latest trusted'):
                self.program['select_latest_gate'](REVISION)

    def test_selection_requires_exact_source_and_trusted_main_workflow(self):
        self.program['github_json'] = Mock(return_value={'workflow_runs': [
            gate_run(10), gate_run(20), gate_run(30, event='pull_request'),
            gate_run(40, event='workflow_dispatch'), gate_run(50, head_branch='feature'),
            gate_run(60, head_sha='b' * 40), gate_run(70, path='different.yml')]})
        self.assertEqual(self.program['select_latest_gate'](REVISION), 20)
        self.program['github_json'] = Mock(return_value={'workflow_runs': [gate_run(30, event='pull_request')]})
        with self.assertRaisesRegex(Gate, 'No trusted exact-source'):
            self.program['select_latest_gate'](REVISION)

    def test_malformed_or_unbounded_workflow_inventory_blocks(self):
        for response in ({'workflow_runs': None}, {'workflow_runs': [None]},
                         {'workflow_runs': [gate_run(True)]},
                         {'workflow_runs': [gate_run(1)] * 101}):
            self.program['github_json'] = Mock(return_value=response)
            with self.subTest(response=response), self.assertRaises(Gate):
                self.program['select_latest_gate'](REVISION)
        self.program['github_json'] = Mock(return_value={'workflow_runs': [gate_run(1)] * 100})
        with self.assertRaisesRegex(Gate, 'supported bounds'):
            self.program['select_latest_gate'](REVISION)

    def test_dispatching_feature_or_stale_main_blocks_before_artifact_download(self):
        environment = {'GITHUB_SHA': REVISION, 'GITHUB_EVENT_NAME': 'workflow_dispatch',
                       'GITHUB_REF': 'refs/heads/feature', 'GH_REPO': REPOSITORY}
        clean = Mock()
        with patch.dict(os.environ, environment, clear=True), patch.object(self.program['platform'], 'require_clean_source', clean):
            with self.assertRaisesRegex(Gate, 'reviewed main'):
                self.program['admit']()
        clean.assert_not_called()
        environment['GITHUB_REF'] = 'refs/heads/main'
        self.program['github_json'] = Mock(side_effect=[{'default_branch': 'main'}, {'object': {'sha': 'b' * 40}}])
        with patch.dict(os.environ, environment, clear=True), patch.object(self.program['platform'], 'require_clean_source', clean):
            with self.assertRaisesRegex(Gate, 'current default main'):
                self.program['admit']()
        clean.assert_not_called()

    def test_success_downloads_selected_run_and_rechecks_live_exact_gate_proof(self):
        environment = {'GITHUB_SHA': REVISION, 'GITHUB_EVENT_NAME': 'workflow_dispatch',
                       'GITHUB_REF': 'refs/heads/main', 'GH_REPO': REPOSITORY}
        self.program['github_json'] = Mock(side_effect=[{'default_branch': 'main'}, {'object': {'sha': REVISION}}])
        self.program['select_latest_gate'] = Mock(return_value=20)
        proof = {'run_id': 20, 'head_sha': REVISION}
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, environment, clear=True), \
                patch.object(self.program['platform'], 'require_clean_source') as clean, \
                patch.object(self.program['platform'], 'verify_gate_file', return_value=proof) as verify, \
                patch.object(self.program['subprocess'], 'run', return_value=Mock(returncode=0)) as downloaded:
            previous = Path.cwd()
            try:
                os.chdir(directory)
                self.program['admit']()
                written = Path('.local/serverlessconfig/gate-admission.json')
                self.assertEqual(json.loads(written.read_text()), proof)
            finally:
                os.chdir(previous)
        clean.assert_called_once_with(REVISION)
        verify.assert_called_once_with(Path('.local/serverlessconfig/gates/gates.json'), REVISION)
        self.assertIn('20', downloaded.call_args.args[0])
        self.assertIn('exact-revision-merge-evidence', downloaded.call_args.args[0])

    def test_unavailable_failed_or_mismatched_gate_artifact_never_writes_admission(self):
        environment = {'GITHUB_SHA': REVISION, 'GITHUB_EVENT_NAME': 'workflow_dispatch',
                       'GITHUB_REF': 'refs/heads/main', 'GH_REPO': REPOSITORY}
        for case in ('download-failed', 'live-gate-failed', 'wrong-run'):
            self.program['github_json'] = Mock(side_effect=[{'default_branch': 'main'}, {'object': {'sha': REVISION}}])
            self.program['select_latest_gate'] = Mock(return_value=20)
            verify = Mock(return_value={'run_id': 30})
            if case == 'live-gate-failed':
                verify.side_effect = Gate('A required job failed')
            downloaded = Mock(returncode=1 if case == 'download-failed' else 0)
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory, \
                    patch.dict(os.environ, environment, clear=True), \
                    patch.object(self.program['platform'], 'require_clean_source'), \
                    patch.object(self.program['platform'], 'verify_gate_file', verify), \
                    patch.object(self.program['subprocess'], 'run', return_value=downloaded):
                previous = Path.cwd()
                try:
                    os.chdir(directory)
                    with self.assertRaises(Gate):
                        self.program['admit']()
                    self.assertFalse(Path('.local/serverlessconfig/gate-admission.json').exists())
                finally:
                    os.chdir(previous)
            if case == 'download-failed':
                verify.assert_not_called()

    def test_source_gate_and_budget_admission_precede_all_aws_credentials(self):
        steps = self.workflow['jobs']['deploy']['steps']
        gate_index = next(i for i, step in enumerate(steps) if step.get('id') == 'admission')
        credential_index = next(i for i, step in enumerate(steps) if step.get('id') == 'credentials')
        plan_index = next(i for i, step in enumerate(steps) if 'serverless.py plan' in step.get('run', ''))
        self.assertLess(gate_index, plan_index)
        self.assertLess(plan_index, credential_index)
        self.assertEqual(self.workflow['permissions'], {'contents': 'read', 'actions': 'read'})
        self.assertIn("github.ref == 'refs/heads/main'", self.workflow['jobs']['deploy']['if'])
        self.assertFalse(self.workflow['concurrency']['cancel-in-progress'])
        self.assertEqual(self.workflow['jobs']['deploy']['timeout-minutes'], 150)
        trigger = self.workflow.get('on', self.workflow.get(True))
        self.assertEqual(set(trigger), {'workflow_dispatch'})
        self.assertFalse(trigger['workflow_dispatch']['inputs']['establish_new']['default'])
        credentials = steps[credential_index]['with']
        self.assertEqual(credentials['aws-access-key-id'], '${{ secrets.ACCESS_KEY_ID }}')
        self.assertEqual(credentials['aws-secret-access-key'], '${{ secrets.AWS_SECRET_ACCESS_KEY }}')
        self.assertEqual(credentials['allowed-account-ids'], '738470137867')
        self.assertFalse(credentials['output-credentials'])
        self.assertTrue(credentials['force-skip-oidc'])
        for step in steps:
            if 'uses' in step:
                self.assertRegex(step['uses'], r'@[0-9a-f]{40}$')

    def test_only_credential_free_receipts_and_recovery_journals_are_uploaded(self):
        steps = self.workflow['jobs']['deploy']['steps']
        upload = next(step for step in steps if step.get('uses', '').startswith('actions/upload-artifact@'))
        self.assertEqual(upload['if'], "always() && steps.admission.outcome == 'success'")
        paths = set(upload['with']['path'].splitlines())
        self.assertEqual(paths, {
            '.local/serverlessconfig/gate-admission.json',
            'reports/serverless-plan.json', 'reports/serverless-deploy.json',
            '.local/deploy/serverless-development/**/deployment.json',
            '.local/deploy/serverless-development/**/deployment-state.json',
        })
        self.assertTrue(upload['with']['include-hidden-files'])
        credentials = next(i for i, step in enumerate(steps) if step.get('id') == 'credentials')
        tooling = next(i for i, step in enumerate(steps) if 'docker buildx version' in step.get('run', ''))
        self.assertLess(tooling, credentials)


if __name__ == '__main__':
    unittest.main()
