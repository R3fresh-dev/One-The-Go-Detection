"""ZIP verifier unit boundaries; actual OAuth/API/worker flow runs separately."""
import importlib.util
import io
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'services/api'))
spec = importlib.util.spec_from_file_location('actual_flow', ROOT / 'infra/local/app_flow.py')
flow = importlib.util.module_from_spec(spec); spec.loader.exec_module(flow)
SID = '10000000-0000-4000-8000-000000000001'


def archive(*, mutate=None, extra=False, bad_hash=False, bad_size=False, bad_evidence=False):
    files = {f'checks/{SID}.json': flow.canonical({'session_id': SID, 'attempts': [1, 2, 3] if bad_evidence else [1, 2, 3, 4]}), 'profile.json': b'{}'}
    manifest = {'session_ids': [SID], 'selection': {'kind': 'single'}, 'omitted_categories': ['raw_artifacts'],
        'files': [{'path': name, 'sha256': '0' * 64 if bad_hash else flow.hashlib.sha256(raw).hexdigest(),
                   'size_bytes': len(raw) + 1 if bad_size else len(raw)} for name, raw in files.items()]}
    if mutate: mutate(manifest)
    files['manifest.json'] = flow.canonical(manifest)
    if extra: files['foreign-account.json'] = b'{}'
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as target:
        for name, data in files.items(): target.writestr(name, data)
    return buffer.getvalue()


class ExportVerifierTest(unittest.TestCase):
    def test_exact_complete_selection_passes(self):
        flow.verify_export(archive(), SID)

    def test_foreign_bytes_corruption_size_and_incomplete_evidence_fail(self):
        for values in ({'extra': True}, {'bad_hash': True}, {'bad_size': True}, {'bad_evidence': True}):
            with self.subTest(values=values), self.assertRaises(AssertionError): flow.verify_export(archive(**values), SID)

    def test_wrong_selection_raw_category_or_file_inventory_fail(self):
        for change in (lambda m: m.update(session_ids=['other']), lambda m: m.update(selection={'kind': 'all'}),
                       lambda m: m.update(omitted_categories=[]), lambda m: m['files'].pop()):
            with self.assertRaises(AssertionError): flow.verify_export(archive(mutate=change), SID)


class PrivacyRetryTest(unittest.TestCase):
    def test_same_intent_honors_actual_server_delay(self):
        time=[0]; waits=[]
        def wait(delay): waits.append(delay); time[0]+=delay
        accepted=SimpleNamespace(status_code=200,headers={})
        http=Mock();http.request.side_effect=[SimpleNamespace(status_code=429,headers={'retry-after':'3'}),accepted]
        headers={'Idempotency-Key':'same-intent'};body={'confirmation':True}
        response=flow.checked_request(http,'POST','/v1/privacy/deletion-requests',headers,body,retry_throttled=True,clock=lambda:time[0],wait=wait)
        self.assertIs(response,accepted);self.assertEqual(waits,[3])
        self.assertEqual(http.request.call_args_list[0],http.request.call_args_list[1])

    def test_unthrottled_writes_and_non_throttle_errors_never_retry(self):
        for status,retry in [(429,False),(401,True),(503,True)]:
            http=Mock();http.request.return_value=SimpleNamespace(status_code=status,headers={'retry-after':'3'})
            wait=Mock()
            with self.assertRaises(AssertionError):flow.checked_request(http,'POST','/v1/sessions',{},retry_throttled=retry,wait=wait)
            self.assertEqual(http.request.call_count,1);wait.assert_not_called()

    def test_invalid_or_excessive_delay_and_exhausted_window_fail(self):
        for delay in ['', '-1','0','1.5','3 seconds','61','3600','15']:
            http=Mock();http.request.return_value=SimpleNamespace(status_code=429,headers={'retry-after':delay})
            wait=Mock()
            with self.assertRaises(AssertionError):flow.checked_request(http,'POST','/v1/auth/logout',{},retry_throttled=True,clock=lambda:0,wait=wait)
            wait.assert_not_called()
        time=[0];http=Mock();http.request.return_value=SimpleNamespace(status_code=429,headers={'retry-after':'3'})
        with self.assertRaises(AssertionError):flow.checked_request(http,'POST','/v1/auth/logout',{},retry_throttled=True,clock=lambda:time[0],wait=lambda delay:time.__setitem__(0,time[0]+delay))
        self.assertEqual(time[0],12);self.assertEqual(http.request.call_count,5)

    def test_success_received_after_deadline_does_not_hide_late_response(self):
        time=[0];http=Mock()
        def late(*args,**kwargs):
            time[0]=16
            return SimpleNamespace(status_code=200,headers={})
        http.request.side_effect=late
        with self.assertRaises(AssertionError):flow.checked_request(http,'POST','/v1/auth/logout',{},retry_throttled=True,clock=lambda:time[0])
