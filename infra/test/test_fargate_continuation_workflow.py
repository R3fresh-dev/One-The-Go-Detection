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


def source_bundle():
    files = continuation_files()
    run = deployment_run()
    return {'schema_version': '1.0.0', 'operation': 'serverless-uninitialized-continuation',
            'account': '738470137867', 'region': 'us-east-2', 'stack_name': 'otgd-serverless-development',
            'failed_run_id': run['id'], 'failed_run_attempt': run['run_attempt'],
            'failed_run_started_at': run['run_started_at'], 'failed_run_completed_at': run['updated_at'],
            'failed_release_id': run['head_sha'], 'artifact_sha256': 'f' * 64,
            **{field: files[name].decode() for field, name in (
                ('original_recovery_raw', 'original-initial-recovery.json'), ('adoption_raw', 'initial-recovery.json'),
                ('deployment_state_raw', 'deployment-state.json'), ('gate_admission_raw', 'gate-admission.json'),
                ('serverless_plan_raw', 'serverless-plan.json'))}}


def previous_run(**changes):
    return deployment_run(**{'id': 40, 'workflow_id': 4, 'path': '.github/workflows/deploy-fargate.yml',
                            'name': 'Deploy OnGo containers to AWS', 'head_sha': REVISION, **changes})


def previous_packet(base=None, previous=None, run_id=40):
    base = base or source_bundle()
    source = {**base, **({'previous_recovery': previous} if previous is not None else {})}
    source_raw = json.dumps(source, indent=2) + '\n'
    run = previous_run()
    state = {'schema_version': '1.0.0', 'environment': 'fargate-development',
             'account': '738470137867', 'region': 'us-east-2', 'release_id': REVISION,
             'status': 'failed', 'current_stage': 'continue-uninitialized-retained-resources',
             'failed_stage': 'continue-uninitialized-retained-resources', 'completed_stages': [],
             'completed_receipts': {}, 'rollback_executed': False}
    journal = {'schema_version': '1.0.0', 'operation': 'serverless-uninitialized-continuation',
               'account': '738470137867', 'region': 'us-east-2', 'stack_name': 'otgd-serverless-development',
               'release_id': REVISION, 'source_bundle_sha256': hashlib.sha256(source_raw.encode()).hexdigest(),
               'journal_established': False, 'actual_resources_deleted': False,
               'application_deployment_completed': False,
               'status': 'blocked-recovery-inspect-protected-journal-before-retry',
               **{key: base[key] for key in ('failed_run_id', 'failed_run_attempt', 'failed_release_id', 'artifact_sha256')}}
    return {'run_id': run_id, 'run_attempt': 1, 'release_id': REVISION, 'artifact_sha256': 'e' * 64,
            'run_started_at': run['run_started_at'], 'run_completed_at': run['updated_at'],
            'source_bundle_raw': source_raw, 'continuation_raw': json.dumps(journal),
            'deployment_state_raw': json.dumps(state)}


def previous_archive_entries(packet):
    prefix = f'.local/deploy/fargate-development/{packet["release_id"]}/' + '0' * 32 + '/'
    regular = stat.S_IFREG | 0o600
    return [('.local/fargateconfig/continuation-source/uninitialized-continuation.json',
             packet['source_bundle_raw'].encode(), regular),
            (prefix + 'uninitialized-continuation.json', packet['continuation_raw'].encode(), regular),
            (prefix + 'deployment-state.json', packet['deployment_state_raw'].encode(), regular),
            ('reports/fargate-deploy.json', b'', regular)]

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

    def test_explicit_blank_recovery_input_uses_dispatch_defaults_without_selecting_both_routes(self):
        trigger = self.workflow.get('on', self.workflow.get(True))
        definitions = trigger['workflow_dispatch']['inputs']
        requested = {'recovery_run_id': '', 'continue_uninitialized_run_id': '38294513822',
                     'establish_new': True}
        # GitHub resolves an explicitly blank optional input to its YAML default.
        resolved = {name: requested[name] or definitions[name]['default'] for name in requested}
        environment = {'RECOVERY_RUN_ID': resolved['recovery_run_id'],
                       'CONTINUE_UNINITIALIZED_RUN_ID': resolved['continue_uninitialized_run_id'],
                       'ESTABLISH_NEW': str(resolved['establish_new']).lower(), 'GH_REPO': REPOSITORY}
        _, recovery = workflow_program('recovery')
        recovery['github_json'] = Mock()
        with patch.dict(os.environ, environment, clear=True), \
                patch.object(recovery['subprocess'], 'run') as download:
            self.assertIsNone(recovery['prepare_recovery']())
            self.assertEqual(self.program['continuation_run_id'](), 38294513822)
        recovery['github_json'].assert_not_called()
        download.assert_not_called()

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
                             historical_download=0, current=None, proof=None, workflow_state='active',
                             post_chain_current=None, post_chain_proof=None):
        run = deployment_run()
        files = files or continuation_files()
        archive = archive_bytes([('records/' + name, raw, stat.S_IFREG | 0o600) for name, raw in files.items()])
        artifact = recovery_artifact(**{'digest': 'sha256:' + hashlib.sha256(archive).hexdigest(),
                                       **(digest_changes or {})})
        workflow = {'id': 3, 'path': run['path'], 'name': run['name'], 'state': workflow_state}
        self.program['github_json'] = Mock(side_effect=[
            run, workflow, {'total_count': 1, 'artifacts': [artifact]}, current or run, post_chain_current or run])
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
                             side_effect=[proof or {'run_id': 50, 'head_sha': PREVIOUS_REVISION},
                                          post_chain_proof or proof or {'run_id': 50, 'head_sha': PREVIOUS_REVISION}]):
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

    def test_retired_lambda_source_can_remain_manually_disabled(self):
        with self.continuation_fixture(workflow_state='disabled_manually') as (directory, _, _):
            self.program['admit_continuation']()
            self.assertTrue(Path('.local/fargateconfig/continuation-admission.json').is_file())
            self.assertIn('CONTINUE_UNINITIALIZED_SHA256=', (directory / 'github-environment').read_text())
        for state in ('disabled_inactivity', 'deleted', None):
            with self.subTest(state=state), self.continuation_fixture(workflow_state=state) as (directory, _, _):
                with self.assertRaisesRegex(Gate, 'reviewed historical'):
                    self.program['admit_continuation']()
                self.assertFalse((directory / 'github-environment').exists())

    def test_prior_chain_cannot_export_after_legacy_run_or_gate_changes(self):
        cases = ({'post_chain_current': deployment_run(run_attempt=2)},
                 {'post_chain_current': deployment_run(status='in_progress', conclusion=None)},
                 {'post_chain_proof': {'run_id': 50, 'head_sha': PREVIOUS_REVISION, 'run_attempt': 2}},
                 {'latest_gate_changed': True})
        for case in cases:
            changed = {key: value for key, value in case.items() if key != 'latest_gate_changed'}
            with self.subTest(case=list(case)), self.continuation_fixture(**changed) as (directory, _, _), \
                    patch.dict(os.environ, {'PREVIOUS_CONTINUATION_RUN_ID': '40'}), \
                    patch.dict(self.program, {'admit_previous_recovery': Mock(return_value=previous_packet())}):
                if case.get('latest_gate_changed'):
                    self.program['select_latest_gate'] = Mock(side_effect=[50, 51])
                with self.assertRaises(Gate):
                    self.program['admit_continuation']()
                self.assertFalse(Path('.local/fargateconfig/continuation-admission.json').exists())
                self.assertFalse((directory / 'github-environment').exists())

    def test_previous_input_is_empty_by_default_and_requires_the_legacy_continuation_route(self):
        trigger = self.workflow.get('on', self.workflow.get(True))
        inputs = trigger['workflow_dispatch']['inputs']
        self.assertEqual(inputs['previous_continuation_run_id']['default'], '')
        self.assertEqual(inputs['recovery_run_id']['default'], '')
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(self.program['previous_continuation_run_id'](None))
        for value in ('0', '040', '40\n', ' 40', '9007199254740992'):
            with self.subTest(value=value), patch.dict(os.environ, {'PREVIOUS_CONTINUATION_RUN_ID': value}, clear=True):
                with self.assertRaises(Gate):
                    self.program['previous_continuation_run_id'](30)
        with patch.dict(os.environ, {'PREVIOUS_CONTINUATION_RUN_ID': '40'}, clear=True):
            with self.assertRaises(Gate):
                self.program['previous_continuation_run_id'](None)
            self.assertEqual(self.program['previous_continuation_run_id'](30), 40)
        self.program['github_json'] = Mock()
        for environment in ({'PREVIOUS_CONTINUATION_RUN_ID': '40'},
                            {'PREVIOUS_CONTINUATION_RUN_ID': '40', 'RECOVERY_RUN_ID': '30'},
                            {'PREVIOUS_CONTINUATION_RUN_ID': '40', 'CONTINUE_UNINITIALIZED_RUN_ID': '30',
                             'RECOVERY_RUN_ID': '30', 'ESTABLISH_NEW': 'true'}):
            with self.subTest(environment=environment), patch.dict(os.environ, environment, clear=True):
                with self.assertRaises(Gate):
                    self.program['admit_continuation']()
        self.program['github_json'].assert_not_called()

    def test_previous_archive_selects_only_exact_source_and_same_attempt_journals(self):
        packet = previous_packet()
        entries = previous_archive_entries(packet)
        with temporary_working_directory():
            path = Path('previous.zip'); path.write_bytes(archive_bytes(entries)); path.chmod(0o600)
            files = self.program['previous_files_from_archive'](path, REVISION)
            self.assertEqual(files, {key: packet[key] for key in ('source_bundle_raw', 'continuation_raw', 'deployment_state_raw')})
            invalid = [entries[:1], entries + [entries[0]],
                       [('../source.json', b'{}', stat.S_IFREG | 0o600), *entries],
                       [(entries[0][0], entries[0][1], stat.S_IFLNK | 0o777), *entries[1:]],
                       [entries[0], (entries[1][0].replace(REVISION, PREVIOUS_REVISION), entries[1][1], entries[1][2]), *entries[2:]],
                       [entries[0], entries[1], (entries[2][0].replace('0' * 32, '1' * 32), entries[2][1], entries[2][2]), entries[3]],
                       [*entries[:3], ('reports/fargate-deploy.json', b'{}', stat.S_IFREG | 0o600)],
                       [entries[0], (entries[1][0], b'x' * 262145, entries[1][2]), *entries[2:]]]
            for receipt in ('bootstrap.json', 'migration.json', 'admission.json', 'activation.json', 'deployment.json'):
                invalid.append([*entries, (entries[1][0].rsplit('/', 1)[0] + '/' + receipt, b'{}', stat.S_IFREG | 0o600)])
            for changed in invalid:
                path.write_bytes(archive_bytes(changed))
                with self.subTest(paths=[row[0] for row in changed]), self.assertRaises(Gate):
                    self.program['previous_files_from_archive'](path, REVISION)
            self.assertFalse(Path('.local').exists())

    def test_previous_chain_binds_original_raw_source_and_rejects_any_initialization(self):
        base = source_bundle(); packet = previous_packet(base)
        self.assertEqual(self.program['previous_chain'](packet, base), [packet])
        for field, changes in (
                ('deployment_state_raw', {'failed_stage': 'bootstrap'}),
                ('deployment_state_raw', {'current_stage': 'deploy-stopped'}),
                ('deployment_state_raw', {'completed_stages': ['continue-uninitialized-retained-resources']}),
                ('deployment_state_raw', {'completed_receipts': {'activation.json': {}}}),
                ('deployment_state_raw', {'rollback_executed': True}),
                ('deployment_state_raw', {'release_id': PREVIOUS_REVISION}),
                ('continuation_raw', {'source_bundle_sha256': 'f' * 64}),
                ('continuation_raw', {'journal_established': True}),
                ('continuation_raw', {'application_deployment_completed': True}),
                ('continuation_raw', {'actual_resources_deleted': True}),
                ('continuation_raw', {'failed_run_id': 31}),
                ('continuation_raw', {'account': '123456789012'}),
                ('source_bundle_raw', {'failed_release_id': REVISION}),
                ('source_bundle_raw', {'unexpected_file_raw': '{}'})):
            value = {**json.loads(packet[field]), **changes}
            changed = {**packet, field: json.dumps(value)}
            with self.subTest(field=field, changes=changes), self.assertRaises(Gate):
                self.program['previous_chain'](changed, base)
        for changed in ({**packet, 'source_bundle_raw': '{"account":1,"account":2}'},
                        {**packet, 'source_bundle_raw': 'x' * 8388609},
                        {**packet, 'deployment_state_raw': 'x' * 65537},
                        {**packet, 'run_attempt': True}, {**packet, 'unexpected': 1},
                        {**packet, 'run_completed_at': '2026-10-12T00:00:00Z'}):
            with self.subTest(changed=list(changed)), self.assertRaises(Gate):
                self.program['previous_chain'](changed, base)
        chain = None
        for run_id in range(40, 48):
            chain = previous_packet(base, previous=chain, run_id=run_id)
        self.assertEqual(len(self.program['previous_chain'](chain, base)), 8)
        with self.assertRaises(Gate):
            self.program['previous_chain'](previous_packet(base, previous=chain, run_id=48), base)

    def test_pre_aws_default_failure_cannot_substitute_for_an_entered_continuation(self):
        # The earlier 383125 default-input failure uploaded only admission/plan
        # records; neither a runtime continuation journal nor source authority exists.
        entries = [('.local/fargateconfig/gate-admission.json', b'{}', stat.S_IFREG | 0o600),
                   ('reports/fargate-plan.json', b'{}', stat.S_IFREG | 0o600)]
        with temporary_working_directory():
            path = Path('default-failure.zip'); path.write_bytes(archive_bytes(entries)); path.chmod(0o600)
            with self.assertRaisesRegex(Gate, 'entered-stage journals'):
                self.program['previous_files_from_archive'](path, REVISION)

    def test_nested_packet_is_compared_with_its_own_authenticated_latest_archive(self):
        base = source_bundle(); older = previous_packet(base, run_id=40)
        newest = previous_packet(base, previous=older, run_id=41)
        run = previous_run(id=41)
        self.program['load_previous_packet'] = Mock(side_effect=[
            (newest, run), ({**older, 'run_attempt': 2}, previous_run(run_attempt=2))])
        self.program['verify_previous_gate'] = Mock(return_value={'run_id': 50})
        self.program['require_latest_previous_run'] = Mock()
        self.program['github_json'] = Mock()
        with self.assertRaisesRegex(Gate, 'Nested previous recovery'):
            self.program['admit_previous_recovery'](41, base, Path('proof'))
        self.assertEqual([call.args[0] for call in self.program['load_previous_packet'].call_args_list], [41, 40])
        self.program['github_json'].assert_not_called()

    def test_previous_gate_requires_all_fourteen_from_the_explicit_latest_attempt(self):
        run = {'id': 50, 'head_sha': REVISION, 'path': WORKFLOW_PATH, 'status': 'completed',
               'conclusion': 'success', 'event': 'push', 'head_branch': 'main', 'run_attempt': 2, 'workflow_id': 10}
        jobs = [{'id': index, 'name': name, 'run_id': 50, 'run_attempt': 2, 'head_sha': REVISION,
                 'status': 'completed', 'conclusion': 'success'}
                for index, name in enumerate(sorted(self.program['FARGATE_JOBS']), 1)]
        proof = {'run_id': 50, 'head_sha': REVISION}
        for mutation in ('valid', 'missing-fargate', 'skipped', 'cancelled', 'wrong-attempt', 'wrong-head', 'duplicate-id', 'gate-rerun'):
            changed = [dict(job) for job in jobs]
            current = dict(run)
            if mutation == 'missing-fargate':
                changed = [job for job in changed if job['name'] != 'platform / fargate-container-runtime']
            elif mutation in ('skipped', 'cancelled'):
                changed[0]['conclusion'] = mutation
            elif mutation == 'wrong-attempt':
                changed[0]['run_attempt'] = 1
            elif mutation == 'wrong-head':
                changed[0]['head_sha'] = PREVIOUS_REVISION
            elif mutation == 'duplicate-id':
                changed[0]['id'] = changed[1]['id']
            elif mutation == 'gate-rerun':
                current['run_attempt'] = 3
            self.program['select_latest_gate'] = Mock(return_value=50)
            self.program['github_json'] = Mock(side_effect=[run, {'total_count': len(changed), 'jobs': changed}, current])
            with self.subTest(mutation=mutation), temporary_working_directory(), \
                    patch.object(self.program['subprocess'], 'run', return_value=Mock(returncode=0)), \
                    patch.object(self.program['platform'], 'verify_gate_file', return_value=proof):
                if mutation == 'valid':
                    self.assertEqual(self.program['verify_previous_gate'](REVISION, Path('gates')), proof)
                    self.assertIn('/attempts/2/jobs?', self.program['github_json'].call_args_list[1].args[0])
                else:
                    with self.assertRaises(Gate):
                        self.program['verify_previous_gate'](REVISION, Path('gates'))

    def test_previous_chain_authenticates_archives_and_never_accepts_latest_attempt_drift(self):
        base = source_bundle(); packet = previous_packet(base)
        raw = archive_bytes(previous_archive_entries(packet))
        run = previous_run()
        artifact = recovery_artifact(id=60, name=f'fargate-deployment-{REVISION}-40',
            digest='sha256:' + hashlib.sha256(raw).hexdigest(), size_in_bytes=len(raw),
            workflow_run={'id': 40, 'head_sha': REVISION, 'head_branch': 'main', 'repository_id': 42, 'head_repository_id': 42})
        workflow = {'id': 4, 'path': run['path'], 'name': run['name'], 'state': 'active'}
        for mutation in ('valid', 'digest', 'latest-attempt', 'source-route', 'expired'):
            current, selected, first = dict(run), dict(artifact), dict(run)
            if mutation == 'digest': selected['digest'] = 'sha256:' + '0' * 64
            if mutation == 'latest-attempt': current['run_attempt'] = 2
            if mutation == 'source-route': first['path'] = '.github/workflows/deploy-serverless.yml'
            if mutation == 'expired': selected['expired'] = True
            self.program['github_json'] = Mock(side_effect=[first, workflow, {'total_count': 1, 'artifacts': [selected]}, current])
            def download(command, **kwargs):
                self.assertEqual(command[:2], ['gh', 'api'])
                kwargs['stdout'].write(raw)
                return Mock(returncode=0)
            with self.subTest(mutation=mutation), temporary_working_directory(), \
                    patch.object(self.program['subprocess'], 'run', side_effect=download), \
                    patch.dict(self.program, {'verify_previous_gate': Mock(return_value={'run_id': 50}),
                                              'require_unchanged_previous_gate': Mock(),
                                              'require_latest_previous_run': Mock()}):
                if mutation == 'valid':
                    admitted = self.program['admit_previous_recovery'](40, base, Path('proof'))
                    self.assertEqual(admitted['artifact_sha256'], hashlib.sha256(raw).hexdigest())
                    self.assertEqual(admitted['source_bundle_raw'], packet['source_bundle_raw'])
                    self.program['require_unchanged_previous_gate'].assert_called_once_with(REVISION, {'run_id': 50})
                else:
                    with self.assertRaises(Gate):
                        self.program['admit_previous_recovery'](40, base, Path('proof'))

    def test_gate_rerun_after_other_chain_members_still_blocks_admission(self):
        proof = {'run_id': 50, 'run_attempt': 2, 'workflow_id': 10}
        current = {'head_sha': REVISION, 'status': 'completed', 'conclusion': 'success',
                   'run_attempt': 2, 'workflow_id': 10}
        self.program['select_latest_gate'] = Mock(return_value=50)
        self.program['github_json'] = Mock(return_value=current)
        self.program['require_unchanged_previous_gate'](REVISION, proof)
        self.program['github_json'] = Mock(return_value={**current, 'run_attempt': 3})
        with self.assertRaises(Gate):
            self.program['require_unchanged_previous_gate'](REVISION, proof)

    def test_previous_outer_packet_cannot_bypass_a_newer_main_fargate_dispatch(self):
        older = previous_run()
        current = previous_run(id=100, status='in_progress', conclusion=None)
        with patch.dict(os.environ, {'GITHUB_RUN_ID': '100'}, clear=True):
            self.program['github_json'] = Mock(return_value={'workflow_runs': [older, current]})
            self.program['require_latest_previous_run'](40)
            for newer in (previous_run(id=41, status='in_progress', conclusion=None),
                          previous_run(id=41, conclusion='success'), previous_run(id=101, status='queued', conclusion=None)):
                self.program['github_json'] = Mock(return_value={'workflow_runs': [older, newer, current]})
                with self.subTest(newer=newer['status']), self.assertRaisesRegex(Gate, 'latest prior'):
                    self.program['require_latest_previous_run'](40)

    def test_previous_packet_is_appended_only_after_authenticated_legacy_admission(self):
        with self.continuation_fixture() as (_, _, _):
            packet = previous_packet()
            def admit_previous(run_id, base, directory):
                self.assertEqual(run_id, 40)
                self.assertNotIn('previous_recovery', base)
                return packet
            with patch.dict(os.environ, {'PREVIOUS_CONTINUATION_RUN_ID': '40'}), \
                    patch.dict(self.program, {'admit_previous_recovery': Mock(side_effect=admit_previous)}):
                self.program['admit_continuation']()
                bundle = json.loads(Path('.local/fargateconfig/continuation-source/uninitialized-continuation.json').read_text())
                self.assertEqual(bundle['previous_recovery'], packet)
                self.program['admit_previous_recovery'].assert_called_once()
