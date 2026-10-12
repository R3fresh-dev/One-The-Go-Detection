"""Exercise the documented file entrypoints in fresh interpreters, without AWS."""
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class DeploymentCliTests(unittest.TestCase):
    def test_documented_help_and_helper_imports_do_not_shadow_stdlib_platform(self):
        # Import-based tests do not reproduce Python putting deploy/ first when
        # a user invokes python deploy/qa.py (uuid/botocore import platform).
        environment = {key: value for key, value in os.environ.items()
            if not key.startswith(('AWS_', 'OTGD_', 'GH_', 'GITHUB_'))}
        environment['AWS_EC2_METADATA_DISABLED'] = 'true'
        for directory in (ROOT, ROOT/'deploy'):
            for script in ('qa.py', 'prod.py', 'platform.py', 'register_cname.py',
                'orchestrate.py', 'web_artifact.py'):
                with self.subTest(directory=directory.name, script=script):
                    result = subprocess.run([sys.executable, str(ROOT/'deploy'/script), '--help'],
                        cwd=directory, env=environment, capture_output=True, text=True, timeout=30)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, '')
                    if script in ('orchestrate.py', 'web_artifact.py'):
                        # These are intentionally action-free helper modules,
                        # rather than additional deployment interfaces.
                        self.assertEqual(result.stdout, '')
                    else:
                        self.assertIn('usage:', result.stdout)
                        self.assertIn('--config', result.stdout)
                        self.assertIn('--gate-evidence', result.stdout)


if __name__ == '__main__':
    unittest.main()
