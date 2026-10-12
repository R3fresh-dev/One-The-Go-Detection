"""Account/endpoint and managed identity boundaries; no live AWS claims."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from botocore.exceptions import NoCredentialsError
from botocore.stub import Stubber
from deploy import check_access
from deploy.platform import CloudSession
from deploy.provenance import Gate


class AwsAccessTest(unittest.TestCase):
    def test_real_sdk_endpoint_and_account_confirmation_ignore_ambient_emulator(self):
        env = {'AWS_ACCESS_KEY_ID': 'fictional-access', 'AWS_SECRET_ACCESS_KEY': 'fictional-secret',
               'AWS_EC2_METADATA_DISABLED': 'true', 'AWS_ENDPOINT_URL': 'http://localhost:4566'}
        with patch.dict(os.environ, env, clear=True):
            aws = CloudSession('us-east-2', None)
            client = aws.client('sts')
            self.assertEqual(client.meta.endpoint_url, 'https://sts.us-east-2.amazonaws.com')
            with Stubber(client) as stub, patch.object(aws, 'client', return_value=client), patch.object(check_access, 'CloudSession', return_value=aws):
                stub.add_response('get_caller_identity', {'Account': '123456789012',
                    'Arn': 'arn:aws:sts::123456789012:assumed-role/deployer/session', 'UserId': 'fictional-user'})
                result = check_access.check('123456789012', 'us-east-2')
            self.assertEqual(result['status'], 'identity_verified')
            self.assertFalse(result['deployment_permissions_verified'])
            self.assertNotIn('fictional-secret', json.dumps(result))

    def test_wrong_account_blocks_without_reporting_remote_identity(self):
        env = {'AWS_ACCESS_KEY_ID': 'fictional-access', 'AWS_SECRET_ACCESS_KEY': 'fictional-secret', 'AWS_EC2_METADATA_DISABLED': 'true'}
        with patch.dict(os.environ, env, clear=True):
            aws = CloudSession('us-east-2', None)
            client = aws.client('sts')
            with Stubber(client) as stub, patch.object(aws, 'client', return_value=client), patch.object(check_access, 'CloudSession', return_value=aws):
                stub.add_response('get_caller_identity', {'Account': '987654321098',
                    'Arn': 'arn:aws:iam::987654321098:user/foreign', 'UserId': 'fictional-user'})
                with self.assertRaisesRegex(Gate, 'differs'):
                    check_access.check('123456789012', 'us-east-2')

    def test_explicit_manifest_alias_selects_config_and_restores_inherited_context(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / 'config'
            config.write_text('[profile deployment]\nregion = us-east-2\n')
            manifest = root / 'manifest.json'
            manifest.write_text(json.dumps({'version': 1, 'connections': [
                {'alias': 'wrong-default', 'provider_kind': 'aws', 'is_default': True, 'config_file': str(config)},
                {'alias': 'deployment', 'provider_kind': 'aws', 'config_file': str(config)}]}))
            env = {'OIC_MANIFEST_PATH': str(manifest), 'AWS_PROFILE': 'inherited', 'AWS_CONFIG_FILE': 'inherited-config',
                   'IDENTITY_HEADER': 'fictional-preserved-header'}
            with patch.dict(os.environ, env, clear=True):
                with check_access.identity_selection('deployment') as selected:
                    self.assertEqual(selected, 'deployment')
                    self.assertEqual(os.environ['AWS_PROFILE'], 'deployment')
                    self.assertEqual(os.environ['AWS_CONFIG_FILE'], str(config))
                    self.assertEqual(os.environ['IDENTITY_HEADER'], 'fictional-preserved-header')
                self.assertEqual(os.environ['AWS_PROFILE'], 'inherited')
                self.assertEqual(os.environ['AWS_CONFIG_FILE'], 'inherited-config')
                with self.assertRaises(Gate):
                    with check_access.identity_selection('not-configured'):
                        self.fail('Unknown identity must not select the provider default')

    def test_unconfigured_or_unsupported_identity_manifest_fails_closed(self):
        with patch.dict(os.environ, {}, clear=True), self.assertRaises(Gate):
            with check_access.identity_selection('deployment'):
                self.fail('No manifest')
        with tempfile.TemporaryDirectory() as temporary:
            manifest = Path(temporary) / 'manifest.json'
            manifest.write_text('{"version":2,"connections":[]}')
            with patch.dict(os.environ, {'OIC_MANIFEST_PATH': str(manifest)}, clear=True), self.assertRaises(Gate):
                with check_access.identity_selection('deployment'):
                    self.fail('Unsupported manifest')

    def test_bad_inputs_and_provider_failure_never_print_credentials(self):
        with self.assertRaises(Gate):
            check_access.check('bad-account', 'us-east-2')
        with self.assertRaises(Gate):
            check_access.check('123456789012', 'bad-region')
        with self.assertRaises(Gate):
            check_access.check('123456789012', 'us-east-2', 'profile', 'alias')
        with patch.object(check_access, 'check', side_effect=NoCredentialsError()), patch('sys.stderr') as stderr:
            self.assertEqual(check_access.main(['--account', '123456789012', '--region', 'us-east-2']), 2)
            emitted = ''.join(call.args[0] for call in stderr.write.call_args_list if call.args)
            self.assertIn('NoCredentialsError', emitted)
            self.assertNotIn('AccessKey', emitted)


if __name__ == '__main__':
    unittest.main()
