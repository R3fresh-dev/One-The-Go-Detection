"""ZIP verifier unit boundaries; actual OAuth/API/worker flow runs separately."""
import importlib.util
import io
from pathlib import Path
import sys
import unittest
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
