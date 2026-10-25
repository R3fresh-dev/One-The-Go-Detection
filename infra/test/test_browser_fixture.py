"""Admission tests for the fictional browser run ledger; no service mutation."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "local/browser_fixture.py"


class BrowserFixtureTests(unittest.TestCase):
    def load(self):
        spec = importlib.util.spec_from_file_location("browser_fixture", SOURCE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_explicit_confirmation_and_local_origins_are_required(self):
        module = self.load()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture.json"
            with self.assertRaises(ValueError):
                module.prepare(path, confirmed=False)
            for url in ("https://example.org", "http://localhost:8000/other", "http://user@localhost:8000", "http://localhost:8000?x=1"):
                with self.assertRaises(ValueError):
                    module.prepare(path, confirmed=True, api_origin=url)
            self.assertFalse(path.exists())

    def test_manifest_preserves_namespace_and_accepts_only_its_reserved_accounts(self):
        module = self.load()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture.json"
            first = module.prepare(path, confirmed=True)
            self.assertEqual(set(first["accounts"]), {"browser_mobile", "browser_desktop"})
            self.assertEqual(first, module.prepare(path, confirmed=True))
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            first["accounts"]["fixture_a"] = {"session_ids": []}
            path.write_text(json.dumps(first))
            with self.assertRaises(ValueError):
                module.prepare(path, confirmed=True)

    def test_unknown_server_inventory_refuses_cleanup_scope(self):
        module = self.load()
        with tempfile.TemporaryDirectory() as folder:
            ledger = module.prepare(Path(folder) / "fixture.json", confirmed=True)
            own = "11111111-1111-4111-8111-111111111111"
            foreign = "22222222-2222-4222-8222-222222222222"
            ledger["accounts"]["browser_mobile"]["session_ids"] = [own]
            module.require_owned_inventory(ledger, "browser_mobile", {"items": [{"session_id": own}], "next_cursor": None})
            for body in ({"items": [{"session_id": foreign}], "next_cursor": None},
                         {"items": [{"session_id": own}], "next_cursor": "more"}, {},
                         {"items": "not-an-inventory", "next_cursor": None}):
                with self.assertRaises(ValueError):
                    module.require_owned_inventory(ledger, "browser_mobile", body)

    def test_symlinks_public_or_unbounded_ledgers_are_refused_without_overwrite(self):
        module = self.load()
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "target"
            target.write_text("preserve")
            link = Path(folder) / "fixture.json"
            link.symlink_to(target)
            with self.assertRaises((ValueError, OSError)):
                module.prepare(link, confirmed=True)
            self.assertEqual(target.read_text(), "preserve")
            link.unlink()
            module.prepare(link, confirmed=True)
            link.chmod(0o644)
            with self.assertRaises(ValueError):
                module.prepare(link, confirmed=True)
            link.chmod(0o600)
            link.write_text(" " * 65537)
            with self.assertRaises(ValueError):
                module.prepare(link, confirmed=True)


if __name__ == "__main__":
    unittest.main()
