"""CommonMark angle destinations must be checked without corrupting URLs."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
spec=importlib.util.spec_from_file_location('document_checks',ROOT/'tools/verify_specs.py')
checks=importlib.util.module_from_spec(spec);spec.loader.exec_module(checks)


class DocumentLinksTest(unittest.TestCase):
 def test_external_parentheses_and_local_spaces_in_angle_destinations(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory)
   (root/'guide with spaces.md').write_text('Target document')
   (root/'README.md').write_text('[API](<https://example.com/authorization(for:)>)\n[Guide](<guide with spaces.md>)\n[Plain](README.md)')
   with patch.object(checks,'ROOT',root):checks.check_document_links()

 def test_broken_angle_destination_still_fails(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'README.md').write_text('[Missing](<missing guide.md>)')
   with patch.object(checks,'ROOT',root),self.assertRaisesRegex(AssertionError,'Broken local link'):
    checks.check_document_links()


if __name__=='__main__':unittest.main()
