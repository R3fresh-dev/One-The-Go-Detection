"""Actual bounded GitHub HTTP protocol; fictional metadata, no cloud calls."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx

from deploy import serverless_gates as gates
from deploy.provenance import Gate, REPOSITORY, REQUIRED_GATE_LABELS, REQUIRED_JOBS, WORKFLOW_PATH

SHA = 'a' * 40
PREFIX = '/repos/' + REPOSITORY


def run(identifier=20, **changes):
    return {'id': identifier, 'run_attempt': 1, 'workflow_id': 7,
        'head_sha': SHA, 'path': WORKFLOW_PATH, 'event': 'push', 'head_branch': 'main',
        'repository': {'full_name': REPOSITORY}, 'head_repository': {'full_name': REPOSITORY},
        'status': 'completed', 'conclusion': 'success', **changes}


class Provider:
    def __init__(self):
        self.latest = run()
        self.main = SHA
        self.default = 'main'
        self.full_name = REPOSITORY
        self.after_jobs = None
        self.jobs = [{'id': 100 + index, 'name': name, 'run_id': 20, 'run_attempt': 1,
            'head_sha': SHA, 'status': 'completed', 'conclusion': 'success'}
            for index, name in enumerate(sorted(REQUIRED_JOBS))]
        self.calls = []

    def request(self, request):
        self.calls.append(str(request.url))
        path = request.url.path
        if path == PREFIX:
            value = {'full_name': self.full_name, 'default_branch': self.default}
        elif path == PREFIX + '/git/ref/heads/main':
            value = {'object': {'sha': self.main, 'type': 'commit'}}
        elif path == PREFIX + '/actions/workflows/merge-gate.yml/runs':
            value = {'total_count': 1, 'workflow_runs': [self.latest]}
        elif path == PREFIX + '/actions/runs/20':
            value = run()
        elif path == PREFIX + '/actions/workflows/7':
            value = {'id': 7, 'path': WORKFLOW_PATH, 'state': 'active'}
        elif path == PREFIX + '/actions/runs/20/attempts/1/jobs':
            value = {'total_count': len(self.jobs), 'jobs': self.jobs}
            if self.after_jobs:
                self.after_jobs(self)
        else:
            raise AssertionError('Unexpected route: ' + path)
        return httpx.Response(200, json=value)


class ServerlessGateAdmissionTest(unittest.TestCase):
    def verify(self, provider):
        with tempfile.TemporaryDirectory() as directory:
            evidence = Path(directory) / 'gates.json'
            evidence.write_text(json.dumps({'revision': SHA, 'passed': sorted(REQUIRED_GATE_LABELS),
                'run_url': 'https://github.com/' + REPOSITORY + '/actions/runs/20'}))
            with httpx.Client(transport=httpx.MockTransport(provider.request), follow_redirects=False) as client:
                return gates.verify_serverless_gates(evidence, SHA, client=client)

    def test_actual_thirteen_job_protocol_is_rechecked_against_current_main_and_newest_run(self):
        provider = Provider()
        proof = self.verify(provider)
        self.assertEqual(proof['run_id'], 20)
        self.assertEqual(set(proof['jobs']), REQUIRED_JOBS)
        self.assertEqual(sum('/git/ref/heads/main' in path for path in provider.calls), 2)
        self.assertEqual(sum('/merge-gate.yml/runs' in path for path in provider.calls), 2)

    def test_new_separate_pending_failed_or_cancelled_run_blocks_original_success(self):
        for status, conclusion in [('in_progress', None), ('completed', 'failure'), ('completed', 'cancelled')]:
            provider = Provider()
            provider.latest = run(21, status=status, conclusion=conclusion)
            with self.subTest(status=status, conclusion=conclusion), self.assertRaisesRegex(Gate, 'latest trusted'):
                self.verify(provider)
            self.assertFalse(any('/attempts/' in path for path in provider.calls))

    def test_new_successful_run_still_requires_its_own_evidence(self):
        provider = Provider()
        provider.latest = run(21)
        with self.assertRaisesRegex(Gate, 'newest trusted'):
            self.verify(provider)

    def test_separate_run_arriving_while_job_proof_loads_blocks(self):
        for newer in (run(21), run(21, status='in_progress', conclusion=None)):
            provider = Provider()
            provider.after_jobs = lambda p: setattr(p, 'latest', newer)
            with self.subTest(newer=newer), self.assertRaises(Gate):
                self.verify(provider)

    def test_main_advance_during_thirteen_job_read_blocks(self):
        provider = Provider()
        provider.after_jobs = lambda p: setattr(p, 'main', 'b' * 40)
        with self.assertRaisesRegex(Gate, 'current default main'):
            self.verify(provider)

    def test_initial_main_default_or_repository_mismatch_blocks_before_run_proof(self):
        for field, value in [('main', 'b' * 40), ('default', 'release'), ('full_name', 'foreign/repo')]:
            provider = Provider()
            setattr(provider, field, value)
            with self.subTest(field=field), self.assertRaisesRegex(Gate, 'current default main'):
                self.verify(provider)
            self.assertFalse(any('/actions/' in path for path in provider.calls))

    def test_skipped_or_failed_required_job_cannot_pass_newest_run_admission(self):
        for status in ('skipped', 'failure'):
            provider = Provider()
            provider.jobs[0]['conclusion'] = status
            with self.subTest(status=status), self.assertRaisesRegex(Gate, 'failed, was skipped'):
                self.verify(provider)

    def test_untrusted_newer_fork_branch_or_wrong_workflow_does_not_replace_trusted_run(self):
        for changes in [{'head_branch': 'feature'}, {'event': 'pull_request'}, {'path': 'other.yml'},
                {'head_sha': 'b' * 40}, {'head_repository': {'full_name': 'foreign/repo'}}]:
            values = [run(), run(21, **changes)]
            self.assertEqual(gates.select_latest_gate(SHA, lambda *a, **k: {'total_count': 2, 'workflow_runs': values}), 20)

    def test_pagination_requires_complete_nonduplicated_stable_bounded_inventory(self):
        for response in [{'workflow_runs': []}, {'total_count': True, 'workflow_runs': []},
                {'total_count': 1001, 'workflow_runs': []}, {'total_count': 2, 'workflow_runs': [run()]},
                {'total_count': 0, 'workflow_runs': [run()]}, {'total_count': 2, 'workflow_runs': [run(), run()]},
                {'total_count': 1, 'workflow_runs': [None]}, {'total_count': 1, 'workflow_runs': [run(True)]},
                {'total_count': 1, 'workflow_runs': 'wrong'}, {'total_count': 0, 'workflow_runs': []}]:
            with self.subTest(response=response), self.assertRaises(Gate):
                gates.select_latest_gate(SHA, lambda *a, **k: response)
        batch = [run(index) for index in range(1, 101)]
        responses = iter([{'total_count': 101, 'workflow_runs': batch},
                          {'total_count': 100, 'workflow_runs': [run(101)]}])
        with self.assertRaises(Gate):
            gates.select_latest_gate(SHA, lambda *a, **k: next(responses))
        responses = iter([{'total_count': 101, 'workflow_runs': batch},
                          {'total_count': 101, 'workflow_runs': [run(101)]}])
        self.assertEqual(gates.select_latest_gate(SHA, lambda *a, **k: next(responses)), 101)

    def test_malformed_revision_never_fetches_metadata(self):
        for revision in (None, 'a' * 39, 'A' * 40, 'main'):
            with self.subTest(revision=revision), self.assertRaises(Gate):
                gates.select_latest_gate(revision, lambda *a, **k: self.fail('Unexpected HTTP'))

    def test_strict_bounded_http_refuses_redirect_without_forwarding_authorization(self):
        for status, wire in [(302, b'{}'), (200, b'[]'), (200, b'{"a":1,"a":2}'),
                (200, b' ' * 2_097_153), (503, b'{}')]:
            requests = []
            def handler(request):
                requests.append(request)
                return httpx.Response(status, content=wire, headers={'Location': 'https://foreign.test/private'})
            with self.subTest(status=status, size=len(wire)), httpx.Client(
                    transport=httpx.MockTransport(handler), follow_redirects=False) as client:
                with self.assertRaises(Gate):
                    gates._read(client, 'repos/' + REPOSITORY)
            self.assertEqual(len(requests), 1)
            self.assertEqual(requests[0].url.host, 'api.github.com')

    def test_http_failure_is_sanitized_and_owned_client_is_closed(self):
        def failure(request):
            raise httpx.ReadTimeout('fictional-private-provider-error')
        with httpx.Client(transport=httpx.MockTransport(failure)) as client:
            with self.assertRaises(Gate) as caught:
                gates._read(client, 'repos/' + REPOSITORY)
            self.assertNotIn('private-provider-error', str(caught.exception))
        provider = Provider()
        real = httpx.Client(transport=httpx.MockTransport(provider.request), follow_redirects=False)
        with patch.dict('os.environ', {'GH_TOKEN': 'fictional-test-only-token'}), patch.object(
                gates.httpx, 'Client', return_value=real) as create:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'gates.json'
                path.write_text(json.dumps({'revision': SHA, 'passed': sorted(REQUIRED_GATE_LABELS),
                    'run_url': 'https://github.com/' + REPOSITORY + '/actions/runs/20'}))
                self.assertEqual(gates.verify_serverless_gates(path, SHA)['run_id'], 20)
        self.assertTrue(real.is_closed)
        self.assertFalse(create.call_args.kwargs['follow_redirects'])


if __name__ == '__main__':
    unittest.main()
