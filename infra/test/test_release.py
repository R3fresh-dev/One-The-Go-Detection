"""Release signature tamper and environment-isolation checks; no AWS mocks counted as integration."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('deployment',ROOT/'deploy/platform.py')
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)


class ReleaseTest(unittest.TestCase):
    def test_signed_digest_bound_to_account_environment_and_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp);key=Ed25519PrivateKey.generate();private=path/'private.pem';public=path/'public.pem';release=path/'release.json'
            private.write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()));private.chmod(0o600)
            public.write_bytes(key.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo))
            body={'environment':'qa','account':'123456789012','region':'us-east-2','image_digest':'sha256:'+'b'*64,'release_id':'c'*40,'database_schema':1,'inference_available':False}
            cfg={'environment':'qa','account':'123456789012','region':'us-east-2','imageDigest':body['image_digest'],'releaseId':body['release_id']}
            d.sign_release(body,release,private)
            self.assertEqual(d.verify_release(release,public,cfg),body)
            with self.assertRaises(d.Gate):d.verify_release(release,public,{**cfg,'environment':'prod'})
            with self.assertRaises(d.Gate):d.sign_release(body,release,private)
            altered=json.loads(release.read_text());altered['payload']['inference_available']=True;release.write_text(json.dumps(altered))
            with self.assertRaises(d.Gate):d.verify_release(release,public,cfg)

    def test_signature_does_not_trust_an_embedded_public_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp);private=path/'private.pem';public=path/'trusted.pem';release=path/'release.json'
            key=Ed25519PrivateKey.generate();private.write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()));private.chmod(0o600)
            public.write_bytes(Ed25519PrivateKey.generate().public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo))
            d.sign_release({'anything':'fixture'},release,private)
            with self.assertRaises(InvalidSignature):d.verify_release(release,public,{})

if __name__=='__main__':unittest.main()
