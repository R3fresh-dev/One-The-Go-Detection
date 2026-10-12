"""Run the workflow admission program against failed/stale gate metadata.

These checks validate the credential boundary without contacting AWS or GitHub.
Live release evidence remains the responsibility of deploy.provenance.
"""
import ast
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
import zipfile
from types import SimpleNamespace
from unittest.mock import Mock, patch

import yaml

from deploy.provenance import Gate, REPOSITORY, WORKFLOW_PATH

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / '.github/workflows/deploy-fargate.yml'
REVISION = 'a' * 40


def workflow_source(step_id='admission'):
    workflow = yaml.safe_load(WORKFLOW.read_text())
    step = next(step for step in workflow['jobs']['deploy']['steps'] if step.get('id') == step_id)
    program = step['run'].split("<<'PYCODE'\n", 1)[1].rsplit('\nPYCODE', 1)[0]
    return workflow, program


def workflow_program(step_id='admission'):
    workflow, program = workflow_source(step_id)
    # Compile exactly the Python shipped in Actions; its __main__ block stays idle.
    namespace = {'__name__': 'fargate_workflow_fixture'}
    exec(compile(ast.parse(program), str(WORKFLOW), 'exec'), namespace)
    return workflow, namespace


def workflow_admission():
    return workflow_program()


def gate_run(run_id, *, conclusion='success', status='completed', **changes):
    return {'id': run_id, 'head_sha': REVISION, 'path': WORKFLOW_PATH,
            'event': 'push', 'head_branch': 'main', 'status': status,
            'conclusion': conclusion, **changes}


class FargateRecoveryArtifactTest(unittest.TestCase):
    def setUp(self):
        _, self.program = workflow_program('recovery')
        self.run_id = 38272959415
        self.artifact_id = 11758225153

    def run_metadata(self):
        return {'id': self.run_id, 'workflow_id': 10, 'path': self.program['LEGACY_WORKFLOW'],
                'head_sha': REVISION, 'head_branch': 'main', 'event': 'workflow_dispatch',
                'status': 'completed', 'conclusion': 'failure',
                'repository': {'full_name': REPOSITORY}, 'head_repository': {'full_name': REPOSITORY}}

    def artifact(self, raw=b'fixture-archive'):
        return {'id': self.artifact_id, 'expired': False, 'size_in_bytes': len(raw),
                'name': f'serverless-deployment-{REVISION}-{self.run_id}',
                'digest': 'sha256:' + hashlib.sha256(raw).hexdigest(),
                'workflow_run': {'id': self.run_id, 'head_sha': REVISION, 'head_branch': 'main'}}

    def zip_bytes(self, names=None):
        output = io.BytesIO()
        with zipfile.ZipFile(output, 'w') as archive:
            for name in names or ['.local/deploy/serverless-development/source/attempt/initial-recovery.json']:
                archive.writestr(name, '{"schema_version":"1.0.0","status":"fixture-only"}')
            archive.writestr('private-fixture.log', 'fictional-sensitive-log-not-to-extract')
        return output.getvalue()

    def test_legacy_run_requires_failed_owned_main_dispatch_and_actual_workflow_path(self):
        for field, value in (('conclusion', 'success'), ('status', 'in_progress'), ('event', 'pull_request'),
                             ('head_branch', 'feature'), ('path', 'untrusted.yml'),
                             ('head_repository', {'full_name': 'foreign/repository'})):
            self.program['github_json'] = Mock()
            run = {**self.run_metadata(), field: value}
            with self.subTest(field=field), self.assertRaisesRegex(Gate, 'failed trusted legacy'):
                self.program['validate_run'](run, self.run_id)
            self.program['github_json'].assert_not_called()
        self.program['github_json'] = Mock(return_value={'id': 10, 'path': 'different.yml'})
        with self.assertRaisesRegex(Gate, 'workflow differs'):
            self.program['validate_run'](self.run_metadata(), self.run_id)

    def test_exact_artifact_must_be_available_unique_and_bound_to_run_source_and_digest(self):
        for field, value in (('expired', True), ('digest', None), ('size_in_bytes', 0),
                             ('size_in_bytes', self.program['MAX_ARCHIVE'] + 1),
                             ('workflow_run', {'id': self.run_id, 'head_sha': 'b' * 40, 'head_branch': 'main'})):
            artifact = {**self.artifact(), field: value}
            self.program['github_json'] = Mock(return_value={'artifacts': [artifact]})
            with self.subTest(field=field), self.assertRaisesRegex(Gate, 'digest, source or availability'):
                self.program['select_artifact'](self.run_metadata(), self.run_id)
        for artifacts in ([], [self.artifact(), self.artifact()]):
            self.program['github_json'] = Mock(return_value={'artifacts': artifacts})
            with self.subTest(duplicates=len(artifacts)), self.assertRaisesRegex(Gate, 'One exact-source'):
                self.program['select_artifact'](self.run_metadata(), self.run_id)

    def test_recovery_opt_in_and_run_identifier_are_checked_before_any_download(self):
        for run_id, establish in (('38272959415', 'false'), ('-1', 'true'), ('1; echo unsafe', 'true')):
            self.program['github_json'] = Mock()
            with self.subTest(run_id=run_id), patch.dict(os.environ, {
                    'RECOVERY_RUN_ID': run_id, 'ESTABLISH_NEW': establish, 'GH_REPO': REPOSITORY}, clear=True):
                with self.assertRaises(Gate):
                    self.program['prepare_recovery']()
            self.program['github_json'].assert_not_called()
        with patch.dict(os.environ, {'RECOVERY_RUN_ID': ''}, clear=True):
            self.program['prepare_recovery']()

    def test_zip_extracts_only_single_bounded_journal_and_rejects_traversal_or_duplicates(self):
        for names in (['../initial-recovery.json'], ['/initial-recovery.json'],
                      ['a/initial-recovery.json', 'b/initial-recovery.json']):
            with self.subTest(names=names), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                archive = root / 'archive.zip'
                archive.write_bytes(self.zip_bytes(names))
                target = root / 'manifest.json'
                with self.assertRaises(Gate):
                    self.program['extract_manifest'](archive, target)
                self.assertFalse(target.exists())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / 'archive.zip'
            archive.write_bytes(self.zip_bytes())
            target = root / 'manifest.json'
            self.program['extract_manifest'](archive, target)
            self.assertEqual(json.loads(target.read_text())['status'], 'fixture-only')
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
            self.assertEqual({path.name for path in root.iterdir()}, {'archive.zip', 'manifest.json'})

    def test_archive_digest_mismatch_never_extracts_journal_or_writes_proof(self):
        raw = self.zip_bytes()
        self.program['github_json'] = Mock(side_effect=[self.run_metadata(),
            {'id': 10, 'path': self.program['LEGACY_WORKFLOW']}, {'artifacts': [self.artifact(raw)]}])
        def download(command, **kwargs):
            kwargs['stdout'].write(raw + b'corrupt')
            return SimpleNamespace(returncode=0)
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {
                'RECOVERY_RUN_ID': str(self.run_id), 'ESTABLISH_NEW': 'true', 'GH_REPO': REPOSITORY}, clear=True), \
                patch.object(self.program['subprocess'], 'run', side_effect=download):
            previous = Path.cwd()
            try:
                os.chdir(directory)
                with self.assertRaisesRegex(Gate, 'GitHub digest'):
                    self.program['prepare_recovery']()
                self.assertFalse(Path('.local/fargateconfig/recovery/initial-recovery.json').exists())
                self.assertFalse(Path('.local/fargateconfig/recovery/artifact-proof.json').exists())
            finally:
                os.chdir(previous)

    def test_valid_download_preserves_original_zip_and_records_only_nonsecret_provenance(self):
        raw = self.zip_bytes()
        self.program['github_json'] = Mock(side_effect=[self.run_metadata(),
            {'id': 10, 'path': self.program['LEGACY_WORKFLOW']}, {'artifacts': [self.artifact(raw)]}])
        def download(command, **kwargs):
            self.assertEqual(command, ['gh', 'api', f'repos/{REPOSITORY}/actions/artifacts/{self.artifact_id}/zip'])
            kwargs['stdout'].write(raw)
            return SimpleNamespace(returncode=0)
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {
                'RECOVERY_RUN_ID': str(self.run_id), 'ESTABLISH_NEW': 'true', 'GH_REPO': REPOSITORY}, clear=True), \
                patch.object(self.program['subprocess'], 'run', side_effect=download):
            previous = Path.cwd()
            try:
                os.chdir(directory)
                self.program['prepare_recovery']()
                root = Path('.local/fargateconfig/recovery')
                self.assertEqual((root / 'recovery-artifact.zip').read_bytes(), raw)
                proof = json.loads((root / 'artifact-proof.json').read_text())
                self.assertEqual(proof['run_id'], self.run_id)
                self.assertEqual(proof['artifact_id'], self.artifact_id)
                self.assertEqual(proof['archive_sha256'], self.artifact(raw)['digest'])
                self.assertNotIn('fictional-sensitive', json.dumps(proof))
                self.assertEqual({p.name for p in root.iterdir()}, {
                    'initial-recovery.json', 'recovery-artifact.zip', 'artifact-proof.json'})
            finally:
                os.chdir(previous)


class FargateWorkflowTest(unittest.TestCase):
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
                written = Path('.local/fargateconfig/gate-admission.json')
                self.assertEqual(json.loads(written.read_text()), proof)
            finally:
                os.chdir(previous)
        clean.assert_called_once_with(REVISION)
        verify.assert_called_once_with(Path('.local/fargateconfig/gates/gates.json'), REVISION)
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
                    self.assertFalse(Path('.local/fargateconfig/gate-admission.json').exists())
                finally:
                    os.chdir(previous)
            if case == 'download-failed':
                verify.assert_not_called()

    def test_source_gate_and_budget_admission_precede_all_aws_credentials(self):
        steps = self.workflow['jobs']['deploy']['steps']
        gate_index = next(i for i, step in enumerate(steps) if step.get('id') == 'admission')
        credential_index = next(i for i, step in enumerate(steps) if step.get('id') == 'credentials')
        plan_index = next(i for i, step in enumerate(steps) if 'fargate.py plan' in step.get('run', ''))
        self.assertLess(gate_index, plan_index)
        self.assertLess(plan_index, credential_index)
        self.assertEqual(self.workflow['permissions'], {'contents': 'read', 'actions': 'read'})
        self.assertIn("github.ref == 'refs/heads/main'", self.workflow['jobs']['deploy']['if'])
        self.assertFalse(self.workflow['concurrency']['cancel-in-progress'])
        self.assertEqual(self.workflow['jobs']['deploy']['timeout-minutes'], 150)
        trigger = self.workflow.get('on', self.workflow.get(True))
        self.assertEqual(set(trigger), {'workflow_dispatch'})
        self.assertFalse(trigger['workflow_dispatch']['inputs']['establish_new']['default'])
        self.assertEqual(trigger['workflow_dispatch']['inputs']['recovery_run_id']['default'], '38272959415')
        recovery_index = next(i for i, step in enumerate(steps) if step.get('id') == 'recovery')
        self.assertLess(plan_index, recovery_index)
        self.assertLess(recovery_index, credential_index)
        credentials = steps[credential_index]['with']
        self.assertEqual(credentials['aws-access-key-id'], '${{ secrets.ACCESS_KEY_ID }}')
        self.assertEqual(credentials['aws-secret-access-key'], '${{ secrets.SECRET_ACCESS_KEY }}')
        self.assertEqual(credentials['allowed-account-ids'], '738470137867')
        self.assertFalse(credentials['output-credentials'])
        self.assertTrue(credentials['force-skip-oidc'])
        for step in steps:
            if 'uses' in step:
                self.assertRegex(step['uses'], r'@[0-9a-f]{40}$')

    def test_configuration_stamps_exact_source_and_rejects_another_account_or_budget(self):
        _, source = workflow_source('configuration')
        base = {'environment': 'fargate-development', 'account': '738470137867',
                'region': 'us-east-2', 'monthlyBudgetUsd': 100, 'releaseId': 'b' * 40}
        for changes in ({}, {'account': '111111111111'}, {'monthlyBudgetUsd': 50},
                        {'monthlyBudgetUsd': 100.01}, {'environment': 'serverless-development'}):
            with self.subTest(changes=changes), tempfile.TemporaryDirectory() as directory, \
                    patch.dict(os.environ, {'GITHUB_SHA': REVISION}, clear=True):
                previous = Path.cwd()
                try:
                    os.chdir(directory)
                    Path('infra/config').mkdir(parents=True)
                    Path('.local/fargateconfig').mkdir(parents=True)
                    Path('infra/config/fargate.example.json').write_text(json.dumps({**base, **changes}))
                    if changes:
                        with self.assertRaises(SystemExit):
                            exec(compile(ast.parse(source), str(WORKFLOW), 'exec'), {'__name__': 'configuration_fixture'})
                        self.assertFalse(Path('.local/fargateconfig/fargate.json').exists())
                    else:
                        exec(compile(ast.parse(source), str(WORKFLOW), 'exec'), {'__name__': 'configuration_fixture'})
                        actual = json.loads(Path('.local/fargateconfig/fargate.json').read_text())
                        self.assertEqual(actual['releaseId'], REVISION)
                        self.assertEqual(actual['monthlyBudgetUsd'], 100)
                finally:
                    os.chdir(previous)

    def test_recovery_identifiers_and_paths_are_separate_cli_arguments_without_credentials(self):
        _, source = workflow_source('deployment')
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {
                'ESTABLISH_NEW': 'true', 'AWS_ACCESS_KEY_ID': 'fictional-sensitive-key',
                'AWS_SECRET_ACCESS_KEY': 'fictional-sensitive-secret'}, clear=True), patch('subprocess.run') as run:
            previous = Path.cwd()
            try:
                os.chdir(directory)
                Path('reports').mkdir()
                proof = Path('.local/fargateconfig/recovery/artifact-proof.json')
                proof.parent.mkdir(parents=True)
                proof.write_text(json.dumps({'run_id': 38272959415, 'artifact_id': 11758225153}))
                exec(compile(ast.parse(source), str(WORKFLOW), 'exec'), {'__name__': 'deployment_fixture'})
            finally:
                os.chdir(previous)
        command = run.call_args.args[0]
        self.assertEqual(command[1:3], ['deploy/fargate.py', 'deploy'])
        self.assertIn('--establish-new', command)
        self.assertEqual(command[command.index('--recovery-run-id') + 1], '38272959415')
        self.assertEqual(command[command.index('--recovery-artifact-id') + 1], '11758225153')
        self.assertEqual(command[command.index('--recovery-manifest') + 1], '.local/fargateconfig/recovery/initial-recovery.json')
        self.assertNotIn('fictional-sensitive', ' '.join(command))

    def test_only_credential_free_receipts_and_recovery_journals_are_uploaded(self):
        steps = self.workflow['jobs']['deploy']['steps']
        upload = next(step for step in steps if step.get('uses', '').startswith('actions/upload-artifact@'))
        self.assertEqual(upload['if'], "always() && steps.admission.outcome == 'success'")
        paths = set(upload['with']['path'].splitlines())
        self.assertEqual(paths, {
            '.local/fargateconfig/gate-admission.json',
            '.local/fargateconfig/recovery/artifact-proof.json',
            'reports/fargate-plan.json', 'reports/fargate-deploy.json',
            '.local/deploy/fargate-development/**/deployment.json',
            '.local/deploy/fargate-development/**/deployment-state.json',
            '.local/deploy/fargate-development/**/initial-recovery.json',
            '.local/deploy/fargate-development/**/initial-resume.json',
        })
        self.assertTrue(upload['with']['include-hidden-files'])
        credentials = next(i for i, step in enumerate(steps) if step.get('id') == 'credentials')
        tooling = next(i for i, step in enumerate(steps) if 'docker buildx version' in step.get('run', ''))
        self.assertLess(tooling, credentials)


if __name__ == '__main__':
    unittest.main()
