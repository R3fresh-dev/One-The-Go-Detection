"""Credential boundary checks for the Fargate continuation of a failed Lambda stop."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import stat
import unittest
from unittest.mock import Mock, patch
from infra.test import test_serverless_workflow as legacy
from infra.test.test_fargate_workflow import workflow_program
from deploy.provenance import Gate, REPOSITORY, WORKFLOW_PATH
REVISION = legacy.REVISION
PREVIOUS_REVISION = legacy.PREVIOUS_REVISION
deployment_run = legacy.deployment_run
recovery_artifact = legacy.recovery_artifact
archive_bytes = legacy.archive_bytes
blocked_manifest = legacy.blocked_manifest
temporary_working_directory = legacy.temporary_working_directory

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

class FargateContinuationWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.workflow, self.program = workflow_program('continuation')

    def test_continuation_admission_and_upload_are_before_aws_and_keep_retired_route(self):
        steps = self.workflow['jobs']['deploy']['steps']
        position = {step.get('id'): index for index, step in enumerate(steps) if step.get('id')}
        self.assertLess(position['admission'], position['continuation'])
        self.assertLess(position['continuation'], position['credentials'])
        deployment = next(step for step in steps if step.get('id') == 'deployment')
        self.assertIn('--continue-uninitialized', deployment['run'])
        self.assertIn('CONTINUE_UNINITIALIZED_SHA256', deployment['run'])
        upload = next(step for step in steps if step.get('uses', '').startswith('actions/upload-artifact@'))
        self.assertIn('.local/fargateconfig/continuation-source/uninitialized-continuation.json', upload['with']['path'])
        self.assertIn('.local/deploy/fargate-development/**/uninitialized-continuation.json', upload['with']['path'])
        _, program = workflow_program('recovery')
        program['github_json'] = Mock()
        with patch.dict(os.environ, {'RECOVERY_RUN_ID': '30', 'CONTINUE_UNINITIALIZED_RUN_ID': '40'}, clear=True):
            with self.assertRaises(Gate):
                program['prepare_recovery']()
        program['github_json'].assert_not_called()


    def test_continuation_requires_first_initialization_and_excludes_other_recovery_modes(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(self.program['continuation_run_id']())
            self.program['github_json'] = Mock()
            self.program['admit_continuation']()
            self.program['github_json'].assert_not_called()
        valid = {'CONTINUE_UNINITIALIZED_RUN_ID': '30', 'ESTABLISH_NEW': 'true', 'RECOVERY_RUN_ID': ''}
        with patch.dict(os.environ, valid, clear=True):
            self.assertEqual(self.program['continuation_run_id'](), 30)
        for changes in ({'CONTINUE_UNINITIALIZED_RUN_ID': '030'}, {'CONTINUE_UNINITIALIZED_RUN_ID': '30\n'},
                        {'CONTINUE_UNINITIALIZED_RUN_ID': '9007199254740992'},
                        {'ESTABLISH_NEW': 'false'}, {'RECOVERY_RUN_ID': '30'},
                        {'RECOVERY_RUN_ID': '10'}):
            with self.subTest(changes=changes), patch.dict(os.environ, {**valid, **changes}, clear=True):
                with self.assertRaises(Gate):
                    self.program['continuation_run_id']()

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
                'CONTINUE_UNINITIALIZED_RUN_ID': '30', 'ESTABLISH_NEW': 'true', 'RECOVERY_RUN_ID': '',
                'GITHUB_ENV': str(directory / 'github-environment')}, clear=True), \
                patch.object(self.program['subprocess'], 'run', side_effect=download), \
                patch.object(self.program['platform'], 'verify_gate_file',
                             return_value=proof or {'run_id': 50, 'head_sha': PREVIOUS_REVISION}):
            yield directory, files, archive

    def test_continuation_admission_preserves_exact_bytes_and_authenticates_failed_source(self):
        with self.continuation_fixture() as (directory, files, archive):
            self.program['admit_continuation']()
            path = Path('.local/fargateconfig/continuation-source/uninitialized-continuation.json')
            raw = path.read_bytes(); bundle = json.loads(raw)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(bundle['failed_run_id'], 30)
            self.assertEqual(bundle['failed_run_attempt'], 1)
            self.assertEqual(bundle['failed_run_started_at'], deployment_run()['run_started_at'])
            self.assertEqual(bundle['failed_run_completed_at'], deployment_run()['updated_at'])
            self.assertEqual(bundle['failed_release_id'], PREVIOUS_REVISION)
            self.assertEqual(bundle['artifact_sha256'], hashlib.sha256(archive).hexdigest())
            for key, name in (('original_recovery_raw', 'original-initial-recovery.json'),
                              ('adoption_raw', 'initial-recovery.json'), ('deployment_state_raw', 'deployment-state.json'),
                              ('gate_admission_raw', 'gate-admission.json'), ('serverless_plan_raw', 'serverless-plan.json')):
                self.assertEqual(bundle[key].encode(), files[name])
            self.program['select_latest_gate'].assert_called_once_with(PREVIOUS_REVISION)
            receipt = json.loads(Path('.local/fargateconfig/continuation-admission.json').read_text())
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
                self.assertFalse(Path('.local/fargateconfig/continuation-admission.json').exists())
                self.assertFalse((directory / 'github-environment').exists())
            self.assertFalse((directory / 'github-environment').exists())
