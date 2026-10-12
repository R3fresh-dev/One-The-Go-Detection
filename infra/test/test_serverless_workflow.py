"""Run the workflow admission program against failed/stale gate metadata.

These checks validate the credential boundary without contacting AWS or GitHub.
Live release evidence remains the responsibility of deploy.provenance.
"""
import ast
from contextlib import contextmanager
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import Mock, patch
import zipfile

import yaml

from deploy.provenance import Gate, REPOSITORY, WORKFLOW_PATH

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / '.github/workflows/deploy-serverless.yml'
REVISION = 'a' * 40
PREVIOUS_REVISION = 'b' * 40


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


def deployment_run(**changes):
    return {'id': 30, 'workflow_id': 3, 'run_attempt': 1, 'head_sha': PREVIOUS_REVISION,
            'name': 'Deploy serverless development to AWS',
            'path': '.github/workflows/deploy-serverless.yml', 'event': 'workflow_dispatch',
            'head_branch': 'main', 'status': 'completed', 'conclusion': 'failure',
            'repository': {'id': 42, 'full_name': REPOSITORY},
            'head_repository': {'id': 42, 'full_name': REPOSITORY},
            'run_started_at': '2026-10-12T12:00:00Z', 'updated_at': '2026-10-12T12:30:00Z',
            **changes}


def recovery_artifact(**changes):
    return {'id': 40, 'name': f'serverless-deployment-{PREVIOUS_REVISION}-30',
            'expired': False, 'size_in_bytes': 1000, 'created_at': '2026-10-12T12:29:00Z',
            'workflow_run': {'id': 30, 'head_sha': PREVIOUS_REVISION, 'head_branch': 'main',
                             'repository_id': 42, 'head_repository_id': 42}, **changes}


def blocked_manifest(**changes):
    return {'schema_version': '1.0.0', 'operation': 'serverless-initial-recovery',
            'account': '738470137867', 'region': 'us-east-2',
            'stack_name': 'otgd-serverless-development', 'release_id': PREVIOUS_REVISION,
            'original_release_id': 'c' * 40,
            'status': 'blocked-recovery-inspect-protected-journal-before-retry',
            'failed_phase': 'failed-stack-metadata-detached', 'actual_resources_deleted': False,
            'application_deployment_completed': False, **changes}


def archive_bytes(entries):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as archive:
        for name, raw, mode in entries:
            entry = zipfile.ZipInfo(name)
            entry.external_attr = mode << 16
            archive.writestr(entry, raw)
    return stream.getvalue()


def continuation_files(**state_changes):
    original = json.dumps(blocked_manifest(), indent=2).encode() + b'\n'
    adoption = blocked_manifest(status='uninitialized-retained-resources-imported',
                                source_manifest_sha256=hashlib.sha256(original).hexdigest(),
                                recovered_stack_id='arn:aws:cloudformation:us-east-2:738470137867:stack/otgd-serverless-development/example')
    state = {'schema_version': '1.0.0', 'environment': 'serverless-development',
             'account': '738470137867', 'region': 'us-east-2', 'release_id': PREVIOUS_REVISION,
             'status': 'failed', 'current_stage': 'deploy-stopped', 'failed_stage': 'deploy-stopped',
             'completed_stages': ['resume-initial-retained-resources', 'serverless-registry',
                                  'exact-source-archive', 'build-immutable-lambda-images'],
             'completed_receipts': {}, 'rollback_executed': False, **state_changes}
    gate = {'provider': 'github_actions', 'repository': REPOSITORY, 'workflow_path': WORKFLOW_PATH,
            'head_sha': PREVIOUS_REVISION, 'event': 'push', 'head_branch': 'main'}
    return {'original-initial-recovery.json': original,
            'initial-recovery.json': json.dumps(adoption).encode(),
            'deployment-state.json': json.dumps(state).encode(),
            'gate-admission.json': json.dumps(gate).encode(),
            'serverless-plan.json': b'{"deployment_executed":false}'}


@contextmanager
def temporary_working_directory():
    previous = Path.cwd()
    with tempfile.TemporaryDirectory() as directory:
        try:
            os.chdir(directory)
            yield Path(directory)
        finally:
            os.chdir(previous)


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
        self.assertFalse(trigger['workflow_dispatch']['inputs']['recover_initial']['default'])
        resume_input = trigger['workflow_dispatch']['inputs']['resume_initial_run_id']
        self.assertEqual(resume_input['type'], 'string')
        self.assertEqual(resume_input['default'], '')
        self.assertFalse(resume_input['required'])
        entrypoint = ast.parse(steps[gate_index]['run'].split("<<'PYCODE'\n", 1)[1].rsplit('\nPYCODE', 1)[0])
        main = next(node for node in entrypoint.body if isinstance(node, ast.If))
        calls = [statement.value.func.id for statement in main.body[0].body
                 if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call)]
        self.assertEqual(calls, ['admit', 'admit_resume', 'admit_continuation'])
        deployment = next(step for step in steps if 'serverless.py deploy' in step.get('run', ''))
        self.assertIn('--resume-initial "$RESUME_INITIAL_PATH" --resume-initial-sha256 "$RESUME_INITIAL_SHA256"',
                      deployment['run'])
        credentials = steps[credential_index]['with']
        self.assertEqual(credentials['aws-access-key-id'], '${{ secrets.ACCESS_KEY_ID }}')
        self.assertEqual(credentials['aws-secret-access-key'], '${{ secrets.SECRET_ACCESS_KEY }}')
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
            '.local/serverlessconfig/resume-admission.json',
            '.local/serverlessconfig/resume-source/original-initial-recovery.json',
            '.local/serverlessconfig/continuation-admission.json',
            '.local/serverlessconfig/continuation-source/uninitialized-continuation.json',
            'reports/serverless-plan.json', 'reports/serverless-deploy.json',
            '.local/deploy/serverless-development/**/deployment.json',
            '.local/deploy/serverless-development/**/deployment-state.json',
            '.local/deploy/serverless-development/**/initial-recovery.json',
            '.local/deploy/serverless-development/**/uninitialized-continuation.json',
        })
        self.assertTrue(upload['with']['include-hidden-files'])
        credentials = next(i for i, step in enumerate(steps) if step.get('id') == 'credentials')
        tooling = next(i for i, step in enumerate(steps) if 'docker buildx version' in step.get('run', ''))
        self.assertLess(tooling, credentials)

    def test_resume_requires_explicit_both_flags_and_bounded_numeric_run_id(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(self.program['resume_run_id']())
            self.program['github_json'] = Mock()
            self.program['admit_resume']()
            self.program['github_json'].assert_not_called()
        for value in ('0', '-30', '+30', '030', '30.0', '30\n', ' 30', 'true',
                      '9007199254740992', '1' * 1000):
            with self.subTest(value=value), patch.dict(os.environ, {
                    'RESUME_INITIAL_RUN_ID': value, 'ESTABLISH_NEW': 'true', 'RECOVER_INITIAL': 'true'}, clear=True):
                with self.assertRaisesRegex(Gate, 'numeric'):
                    self.program['resume_run_id']()
        for establish, recover in (('false', 'true'), ('true', 'false'), ('false', 'false'), ('True', 'true')):
            with self.subTest(establish=establish, recover=recover), patch.dict(os.environ, {
                    'RESUME_INITIAL_RUN_ID': '30', 'ESTABLISH_NEW': establish, 'RECOVER_INITIAL': recover}, clear=True):
                with self.assertRaisesRegex(Gate, 'requires recover_initial and establish_new'):
                    self.program['resume_run_id']()
        with patch.dict(os.environ, {'RESUME_INITIAL_RUN_ID': '30', 'ESTABLISH_NEW': 'true',
                                   'RECOVER_INITIAL': 'true'}, clear=True):
            self.assertEqual(self.program['resume_run_id'](), 30)

    def test_resume_source_run_requires_failed_main_dispatch_and_same_repository_workflow(self):
        self.program['validate_resume_run'](deployment_run(), 30)
        for changes in ({'id': 31}, {'id': True}, {'workflow_id': True}, {'run_attempt': 0},
                        {'head_sha': REVISION.upper()}, {'path': '.github/workflows/merge-gate.yml'},
                        {'name': 'Different deployment'}, {'event': 'pull_request'}, {'head_branch': 'feature'},
                        {'status': 'in_progress'}, {'conclusion': 'success'}, {'conclusion': 'cancelled'},
                        {'repository': None}, {'head_repository': {'id': 43, 'full_name': REPOSITORY}},
                        {'repository': {'id': 42, 'full_name': 'attacker/fork'}},
                        {'head_repository': {'id': 42, 'full_name': 'attacker/fork'}}):
            with self.subTest(changes=changes), self.assertRaisesRegex(Gate, 'trusted deployment'):
                self.program['validate_resume_run'](deployment_run(**changes), 30)

    def test_resume_artifact_metadata_binds_source_attempt_and_rejects_ambiguous_inventory(self):
        artifact = recovery_artifact()
        self.program['github_json'] = Mock(return_value={'total_count': 1, 'artifacts': [artifact]})
        self.assertEqual(self.program['select_resume_artifact'](deployment_run()), artifact)
        self.assertIn(f'actions/runs/30/artifacts?name={artifact["name"]}',
                      self.program['github_json'].call_args.args[0])
        invalid_inventory = (
            {'total_count': 0, 'artifacts': []}, {'total_count': 2, 'artifacts': [artifact, artifact]},
            {'total_count': True, 'artifacts': [artifact]}, {'total_count': 1, 'artifacts': [None]},
            {'total_count': 101, 'artifacts': [artifact] * 101}, {'total_count': 2, 'artifacts': [artifact]},
            {'total_count': 1, 'artifacts': [recovery_artifact(name='different')]})
        for inventory in invalid_inventory:
            self.program['github_json'] = Mock(return_value=inventory)
            with self.subTest(inventory=inventory), self.assertRaises(Gate):
                self.program['select_resume_artifact'](deployment_run())
        for changes in ({'id': True}, {'expired': True}, {'size_in_bytes': 0}, {'size_in_bytes': 8_388_609},
                        {'created_at': '2026-10-12T11:59:00Z'}, {'created_at': '2026-10-12T12:31:00Z'},
                        {'created_at': 'invalid'}, {'created_at': '2026-10-12T12:29:00'},
                        {'workflow_run': None}, {'workflow_run': {}}):
            self.program['github_json'] = Mock(return_value={
                'total_count': 1, 'artifacts': [recovery_artifact(**changes)]})
            with self.subTest(changes=changes), self.assertRaises(Gate):
                self.program['select_resume_artifact'](deployment_run())
        for field, value in (('id', 31), ('head_sha', REVISION), ('head_branch', 'feature'),
                             ('repository_id', 43), ('head_repository_id', 43)):
            binding = {**artifact['workflow_run'], field: value}
            self.program['github_json'] = Mock(return_value={
                'total_count': 1, 'artifacts': [recovery_artifact(workflow_run=binding)]})
            with self.subTest(field=field), self.assertRaises(Gate):
                self.program['select_resume_artifact'](deployment_run())

    def test_archive_accepts_only_one_bounded_regular_manifest_without_extracting_paths(self):
        raw = json.dumps(blocked_manifest()).encode()
        regular = stat.S_IFREG | 0o600
        valid = [('receipts/initial-recovery.json', raw, regular),
                 ('receipts/deployment-state.json', b'{}', regular),
                 ('resume-source/original-initial-recovery.json', b'old source', regular)]
        with temporary_working_directory():
            path = Path('artifact.zip')
            path.write_bytes(archive_bytes(valid))
            path.chmod(0o600)
            self.assertEqual(self.program['manifest_from_archive'](path), raw)
            self.assertFalse(Path('receipts').exists())
            invalid_entries = (
                [], valid + [('other/initial-recovery.json', raw, regular)],
                [('initial-recovery.json', raw, stat.S_IFLNK | 0o777)],
                [('initial-recovery.json', raw, stat.S_IFIFO | 0o600)],
                [('initial-recovery.json/', b'', stat.S_IFDIR | 0o700)],
                [('initial-recovery.json', b'', regular)],
                [('initial-recovery.json', b'x' * 262_145, regular)],
                [('../initial-recovery.json', raw, regular)],
                [('/initial-recovery.json', raw, regular)],
                [('unsafe\\initial-recovery.json', raw, regular)],
                valid + [(f'other/{number}', b'', regular) for number in range(101)],
                valid + [('large-file', b'x' * 8_388_609, regular)])
            for entries in invalid_entries:
                path.write_bytes(archive_bytes(entries))
                with self.subTest(entries=[item[0] for item in entries]), self.assertRaises(Gate):
                    self.program['manifest_from_archive'](path)
            path.write_bytes(b'not a zip archive')
            with self.assertRaisesRegex(Gate, 'malformed'):
                self.program['manifest_from_archive'](path)
            path.write_bytes(archive_bytes(valid))
            Path('linked.zip').symlink_to(path)
            with self.assertRaises(Gate):
                self.program['manifest_from_archive'](Path('linked.zip'))

    def test_resume_manifest_rejects_mismatched_target_source_and_unsupported_failure(self):
        manifest = blocked_manifest()
        self.assertEqual(self.program['validate_resume_manifest'](json.dumps(manifest).encode(), deployment_run()), manifest)
        for changes in ({'schema_version': '2.0.0'}, {'operation': 'other'}, {'account': '123456789012'},
                        {'region': 'us-east-1'}, {'stack_name': 'otgd-qa'}, {'environment': 'qa'},
                        {'release_id': REVISION}, {'status': 'failed-stack-metadata-detached'},
                        {'status': 'uninitialized-retained-resources-imported'},
                        {'failed_phase': 'import-change-set-created'}, {'failed_phase': 'import-executing'},
                        {'actual_resources_deleted': True}, {'application_deployment_completed': True}):
            with self.subTest(changes=changes), self.assertRaisesRegex(Gate, 'differs'):
                self.program['validate_resume_manifest'](json.dumps(blocked_manifest(**changes)).encode(), deployment_run())
        for raw in (b'not json', b'[]', b'{"status":"blocked","status":"failed"}'):
            with self.subTest(raw=raw), self.assertRaises(Gate):
                self.program['validate_resume_manifest'](raw, deployment_run())

    @contextmanager
    def resume_fixture(self, *, source=None, artifact_download=0, historical_download=0,
                       proof=None, current=None, workflow_changes=None):
        run = deployment_run()
        workflow = {'id': 3, 'path': run['path'], 'name': run['name'], 'state': 'active',
                    **(workflow_changes or {})}
        artifact = recovery_artifact()
        self.program['github_json'] = Mock(side_effect=[
            run, workflow, {'total_count': 1, 'artifacts': [artifact]}, current or run])
        self.program['select_latest_gate'] = Mock(return_value=50)
        raw = source if source is not None else json.dumps(blocked_manifest(), indent=2).encode() + b'\n'
        archive = archive_bytes([('journal/initial-recovery.json', raw, stat.S_IFREG | 0o600)])
        def download(command, **options):
            if command[:2] == ['gh', 'api']:
                options['stdout'].write(archive)
                return Mock(returncode=artifact_download)
            if command[:3] == ['gh', 'run', 'download']:
                return Mock(returncode=historical_download)
            raise AssertionError(command)
        with temporary_working_directory() as directory, patch.dict(os.environ, {
                'RESUME_INITIAL_RUN_ID': '30', 'ESTABLISH_NEW': 'true', 'RECOVER_INITIAL': 'true',
                'GITHUB_ENV': str(directory / 'github-environment')}, clear=True), \
                patch.object(self.program['subprocess'], 'run', side_effect=download) as downloaded, \
                patch.object(self.program['platform'], 'verify_gate_file',
                             return_value=proof or {'run_id': 50, 'head_sha': PREVIOUS_REVISION}) as verify:
            yield directory, raw, downloaded, verify

    def test_resume_admission_preserves_exact_source_hash_and_verifies_separate_historical_gates(self):
        with self.resume_fixture() as (directory, raw, downloaded, verify):
            self.program['admit_resume']()
            source = Path('.local/serverlessconfig/resume-source/original-initial-recovery.json')
            self.assertEqual(source.read_bytes(), raw)
            self.assertEqual(source.stat().st_mode & 0o777, 0o600)
            receipt = json.loads(Path('.local/serverlessconfig/resume-admission.json').read_text())
            self.assertEqual(receipt['source_manifest_sha256'], hashlib.sha256(raw).hexdigest())
            self.assertEqual(receipt['source_run_id'], 30)
            self.assertEqual(receipt['source_artifact_id'], 40)
            self.assertEqual(receipt['source_release_id'], PREVIOUS_REVISION)
            self.program['select_latest_gate'].assert_called_once_with(PREVIOUS_REVISION)
            verify.assert_called_once_with(Path('.local/serverlessconfig/resume-gates/gates.json'), PREVIOUS_REVISION)
            self.assertEqual(downloaded.call_args_list[0].args[0],
                             ['gh', 'api', f'repos/{REPOSITORY}/actions/artifacts/40/zip'])
            self.assertIn('50', downloaded.call_args_list[1].args[0])
            self.assertEqual((directory / 'github-environment').read_text(),
                             f'RESUME_INITIAL_PATH={source}\nRESUME_INITIAL_SHA256={hashlib.sha256(raw).hexdigest()}\n')
            self.assertFalse(Path('.local/serverlessconfig/gates').exists())

    def test_resume_never_exports_cli_authority_after_failed_history_download_or_source_rerun(self):
        cases = ({'artifact_download': 1}, {'historical_download': 1}, {'proof': {'run_id': 51}},
                 {'current': deployment_run(run_attempt=2)}, {'current': deployment_run(conclusion='success')},
                 {'source': json.dumps(blocked_manifest(release_id=REVISION)).encode()},
                 {'workflow_changes': {'path': 'other.yml'}}, {'workflow_changes': {'state': 'disabled_manually'}})
        for case in cases:
            with self.subTest(case=case), self.resume_fixture(**case) as (directory, raw, downloaded, verify):
                with self.assertRaises(Gate):
                    self.program['admit_resume']()
                self.assertFalse(Path('.local/serverlessconfig/resume-admission.json').exists())
                self.assertFalse((directory / 'github-environment').exists())
        with self.resume_fixture() as (directory, raw, downloaded, verify):
            verify.side_effect = Gate('Historical required job failed')
            with self.assertRaisesRegex(Gate, 'Historical required job failed'):
                self.program['admit_resume']()
            self.assertFalse((directory / 'github-environment').exists())
        with self.resume_fixture() as (directory, raw, downloaded, verify):
            self.program['select_latest_gate'].side_effect = Gate('The latest trusted gate failed')
            with self.assertRaisesRegex(Gate, 'latest trusted'):
                self.program['admit_resume']()
            verify.assert_not_called()
            self.assertEqual(downloaded.call_count, 1)

    def test_continuation_requires_first_initialization_and_excludes_other_recovery_modes(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(self.program['continuation_run_id']())
            self.program['github_json'] = Mock()
            self.program['admit_continuation']()
            self.program['github_json'].assert_not_called()
        valid = {'CONTINUE_UNINITIALIZED_RUN_ID': '30', 'ESTABLISH_NEW': 'true', 'RECOVER_INITIAL': 'false'}
        with patch.dict(os.environ, valid, clear=True):
            self.assertEqual(self.program['continuation_run_id'](), 30)
        for changes in ({'CONTINUE_UNINITIALIZED_RUN_ID': '030'}, {'CONTINUE_UNINITIALIZED_RUN_ID': '30\n'},
                        {'CONTINUE_UNINITIALIZED_RUN_ID': '9007199254740992'},
                        {'ESTABLISH_NEW': 'false'}, {'RECOVER_INITIAL': 'true'},
                        {'RESUME_INITIAL_RUN_ID': '10'}):
            with self.subTest(changes=changes), patch.dict(os.environ, {**valid, **changes}, clear=True):
                with self.assertRaises(Gate):
                    self.program['continuation_run_id']()
        with patch.dict(os.environ, {**valid, 'RESUME_INITIAL_RUN_ID': '10', 'RECOVER_INITIAL': 'true'}, clear=True):
            with self.assertRaises(Gate):
                self.program['resume_run_id']()

    def test_continuation_archive_binds_unique_safe_bounded_records_without_extracting(self):
        files = continuation_files()
        entries = [('records/' + name, raw, stat.S_IFREG | 0o600) for name, raw in files.items()]
        with temporary_working_directory():
            path = Path('artifact.zip')
            path.write_bytes(archive_bytes(entries)); path.chmod(0o600)
            self.assertEqual(self.program['continuation_files_from_archive'](path), files)
            self.assertFalse(Path('records').exists())
            for invalid in (entries[:-1], entries + [entries[0]],
                            [('../' + entries[0][0], entries[0][1], entries[0][2]), *entries[1:]],
                            [('unsafe\\folder/' + entries[0][0], entries[0][1], entries[0][2]), *entries[1:]],
                            [(entries[0][0], entries[0][1], stat.S_IFLNK | 0o777), *entries[1:]],
                            [('deployment-state.json', b'x' * 65_537, stat.S_IFREG | 0o600),
                             *[entry for entry in entries if not entry[0].endswith('deployment-state.json')]]):
                path.write_bytes(archive_bytes(invalid))
                with self.subTest(names=[entry[0] for entry in invalid]), self.assertRaises(Gate):
                    self.program['continuation_files_from_archive'](path)
            path.write_bytes(b'not a zip')
            with self.assertRaises(Gate):
                self.program['continuation_files_from_archive'](path)

    def test_continuation_evidence_rejects_initialized_or_unbound_sources(self):
        files = continuation_files()
        self.program['validate_continuation_files'](files, deployment_run())
        for changes in ({'failed_stage': 'bootstrap'}, {'status': 'running'},
                        {'completed_stages': ['bootstrap']}, {'completed_receipts': {'bootstrap.json': {}}},
                        {'rollback_executed': True}, {'account': '123456789012'}, {'release_id': REVISION}):
            with self.subTest(changes=changes), self.assertRaises(Gate):
                self.program['validate_continuation_files'](continuation_files(**changes), deployment_run())
        for name, changes in (
                ('initial-recovery.json', {'source_manifest_sha256': 'f' * 64}),
                ('initial-recovery.json', {'status': 'blocked-recovery-inspect-protected-journal-before-retry'}),
                ('original-initial-recovery.json', {'actual_resources_deleted': True}),
                ('gate-admission.json', {'head_sha': REVISION}),
                ('gate-admission.json', {'event': 'pull_request'}),
                ('serverless-plan.json', {'deployment_executed': True})):
            value = {**json.loads(files[name]), **changes}
            with self.subTest(name=name, changes=changes), self.assertRaises(Gate):
                self.program['validate_continuation_files']({**files, name: json.dumps(value).encode()}, deployment_run())
        with self.assertRaises(Gate):
            self.program['validate_continuation_files']({**files, 'deployment-state.json': b'{"status":1,"status":2}'}, deployment_run())

    @contextmanager
    def continuation_fixture(self, *, files=None, digest_changes=None, artifact_download=0,
                             historical_download=0, current=None, proof=None):
        run = deployment_run()
        files = files or continuation_files()
        archive = archive_bytes([('records/' + name, raw, stat.S_IFREG | 0o600) for name, raw in files.items()])
        artifact = recovery_artifact(**{'digest': 'sha256:' + hashlib.sha256(archive).hexdigest(),
                                       **(digest_changes or {})})
        workflow = {'id': 3, 'path': run['path'], 'name': run['name'], 'state': 'active'}
        self.program['github_json'] = Mock(side_effect=[
            run, workflow, {'total_count': 1, 'artifacts': [artifact]}, current or run])
        self.program['select_latest_gate'] = Mock(return_value=50)
        def download(command, **options):
            if command[:2] == ['gh', 'api']:
                options['stdout'].write(archive)
                return Mock(returncode=artifact_download)
            if command[:3] == ['gh', 'run', 'download']:
                return Mock(returncode=historical_download)
            raise AssertionError(command)
        with temporary_working_directory() as directory, patch.dict(os.environ, {
                'CONTINUE_UNINITIALIZED_RUN_ID': '30', 'ESTABLISH_NEW': 'true', 'RECOVER_INITIAL': 'false',
                'GITHUB_ENV': str(directory / 'github-environment')}, clear=True), \
                patch.object(self.program['subprocess'], 'run', side_effect=download), \
                patch.object(self.program['platform'], 'verify_gate_file',
                             return_value=proof or {'run_id': 50, 'head_sha': PREVIOUS_REVISION}):
            yield directory, files, archive

    def test_continuation_admission_preserves_exact_bytes_and_authenticates_failed_source(self):
        with self.continuation_fixture() as (directory, files, archive):
            self.program['admit_continuation']()
            path = Path('.local/serverlessconfig/continuation-source/uninitialized-continuation.json')
            raw = path.read_bytes(); bundle = json.loads(raw)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(bundle['failed_run_id'], 30)
            self.assertEqual(bundle['failed_run_attempt'], 1)
            self.assertEqual(bundle['failed_release_id'], PREVIOUS_REVISION)
            self.assertEqual(bundle['artifact_sha256'], hashlib.sha256(archive).hexdigest())
            for key, name in (('original_recovery_raw', 'original-initial-recovery.json'),
                              ('adoption_raw', 'initial-recovery.json'), ('deployment_state_raw', 'deployment-state.json'),
                              ('gate_admission_raw', 'gate-admission.json'), ('serverless_plan_raw', 'serverless-plan.json')):
                self.assertEqual(bundle[key].encode(), files[name])
            self.program['select_latest_gate'].assert_called_once_with(PREVIOUS_REVISION)
            receipt = json.loads(Path('.local/serverlessconfig/continuation-admission.json').read_text())
            self.assertEqual(receipt['source_bundle_sha256'], hashlib.sha256(raw).hexdigest())
            self.assertEqual(receipt['source_artifact_sha256'], hashlib.sha256(archive).hexdigest())
            self.assertEqual((directory / 'github-environment').read_text(),
                             f'CONTINUE_UNINITIALIZED_PATH={path}\nCONTINUE_UNINITIALIZED_SHA256={hashlib.sha256(raw).hexdigest()}\n')

    def test_continuation_never_exports_authority_after_digest_gate_or_attempt_changes(self):
        for case in ({'artifact_download': 1}, {'historical_download': 1}, {'proof': {'run_id': 51}},
                     {'current': deployment_run(run_attempt=2)}, {'current': deployment_run(conclusion='success')},
                     {'files': continuation_files(failed_stage='bootstrap')},
                     {'digest_changes': {'digest': None}}, {'digest_changes': {'digest': 'sha256:' + 'f' * 64}}):
            with self.subTest(case=case), self.continuation_fixture(**case) as (directory, files, archive):
                with self.assertRaises(Gate):
                    self.program['admit_continuation']()
                self.assertFalse(Path('.local/serverlessconfig/continuation-admission.json').exists())
                self.assertFalse((directory / 'github-environment').exists())
            self.assertFalse((directory / 'github-environment').exists())


if __name__ == '__main__':
    unittest.main()
