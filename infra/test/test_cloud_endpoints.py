"""Actual SDK endpoint resolution tests; no cloud network or credential reads."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from botocore.config import Config
from deploy import platform


class CloudEndpointTest(unittest.TestCase):
    def test_identity_and_mutation_clients_ignore_global_service_and_profile_endpoints(self):
        with tempfile.TemporaryDirectory() as directory:
            config=Path(directory)/'config'
            config.write_text('[profile endpoint-fixture]\nregion = us-east-2\nservices = local-overrides\n'
                '[services local-overrides]\nsts =\n  endpoint_url = https://profile-identity.invalid\n'
                'ecs =\n  endpoint_url = https://profile-mutation.invalid\n')
            environment={'AWS_CONFIG_FILE':str(config),'AWS_SHARED_CREDENTIALS_FILE':str(Path(directory)/'absent'),
                'AWS_ACCESS_KEY_ID':'fixture-only','AWS_SECRET_ACCESS_KEY':'fixture-only','AWS_EC2_METADATA_DISABLED':'true',
                'AWS_ENDPOINT_URL':'https://ambient-global.invalid','AWS_ENDPOINT_URL_STS':'https://ambient-identity.invalid',
                'AWS_ENDPOINT_URL_ECS':'https://ambient-mutation.invalid','AWS_IGNORE_CONFIGURED_ENDPOINT_URLS':'false'}
            for mode in ('ambient','profile'):
                selected={key:value for key,value in environment.items() if mode=='ambient' or not key.startswith('AWS_ENDPOINT_URL')}
                with patch.dict(os.environ,selected,clear=True):
                    aws=platform.session({'region':'us-east-2'},'endpoint-fixture')
                    for service,expected in [('sts','https://sts.us-east-2.amazonaws.com'),('ecs','https://ecs.us-east-2.amazonaws.com')]:
                        with self.subTest(mode=mode,service=service):
                            unguarded=aws._session.client(service,config=Config(ignore_configured_endpoint_urls=False))
                            self.assertTrue(unguarded.meta.endpoint_url.endswith('.invalid'))
                            unguarded.close()
                            client=aws.client(service,config=Config(ignore_configured_endpoint_urls=False))
                            self.assertEqual(client.meta.endpoint_url,expected)
                            client.close()
                    with self.assertRaises(platform.Gate):aws.client('sts',endpoint_url='https://explicit.invalid')

    def test_child_processes_drop_endpoints_and_force_configured_endpoint_ignore(self):
        with patch.dict(os.environ,{'AWS_ENDPOINT_URL':'http://localstack:4566','AWS_ENDPOINT_URL_STS':'http://localstack:4566',
                'AWS_IGNORE_CONFIGURED_ENDPOINT_URLS':'false','AWS_PROFILE':'reviewed-profile'},clear=True):
            environment=platform.deployment_environment()
        self.assertNotIn('AWS_ENDPOINT_URL',environment)
        self.assertNotIn('AWS_ENDPOINT_URL_STS',environment)
        self.assertEqual(environment['AWS_IGNORE_CONFIGURED_ENDPOINT_URLS'],'true')
        self.assertEqual(environment['AWS_PROFILE'],'reviewed-profile')
        with patch.object(platform.subprocess,'run') as process:
            platform.run(['npm','exec','--','cdk','deploy','reviewed-stack'])
        self.assertEqual(process.call_args.kwargs['env']['AWS_IGNORE_CONFIGURED_ENDPOINT_URLS'],'true')


if __name__=='__main__':unittest.main()
