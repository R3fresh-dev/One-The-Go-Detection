"""Release signature tamper and environment-isolation checks; no AWS mocks counted as integration."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('deployment',ROOT/'deploy/platform.py')
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)


class ReleaseTest(unittest.TestCase):
    def test_private_signing_key_is_regular_private_bounded_and_single_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);path=root/'private.pem'
            key=Ed25519PrivateKey.generate()
            raw=key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
            path.write_bytes(raw);path.chmod(0o600)
            self.assertEqual(d.private_key(path).private_bytes(serialization.Encoding.Raw,serialization.PrivateFormat.Raw,serialization.NoEncryption()),
                key.private_bytes(serialization.Encoding.Raw,serialization.PrivateFormat.Raw,serialization.NoEncryption()))
            symbolic=root/'symbolic.pem';symbolic.symlink_to(path)
            with self.assertRaises(d.Gate):d.private_key(symbolic)
            with self.assertRaises(d.Gate):d.private_key(root)
            linked=root/'linked.pem';os.link(path,linked)
            with self.assertRaises(d.Gate):d.private_key(path)
            linked.unlink()
            path.chmod(0o644)
            with self.assertRaises(d.Gate):d.private_key(path)
            path.chmod(0o600)
            with patch.object(d.os,'getuid',return_value=os.getuid()+1),self.assertRaises(d.Gate):d.private_key(path)
            path.write_bytes(b'x'*8193)
            with self.assertRaises(d.Gate):d.private_key(path)
            path.write_bytes(b'not an Ed25519 private key')
            with self.assertRaises(d.Gate):d.private_key(path)

    def test_fifo_key_is_rejected_without_waiting_for_a_writer(self):
        with tempfile.TemporaryDirectory() as tmp:
            fifo=Path(tmp)/'private-fifo.pem';os.mkfifo(fifo,0o600)
            code="from pathlib import Path; from deploy.platform import private_key; from deploy.provenance import Gate; import sys\ntry: private_key(Path(sys.argv[1]))\nexcept Gate: raise SystemExit(0)\nraise SystemExit(1)"
            environment={key:value for key,value in os.environ.items() if not key.startswith(('AWS_','OTGD_','GH_','GITHUB_'))}
            environment['AWS_EC2_METADATA_DISABLED']='true'
            result=subprocess.run([sys.executable,'-c',code,str(fifo)],cwd=ROOT,env=environment,
                capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,0,result.stderr)

    def test_signing_key_metadata_change_during_read_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'private.pem'
            path.write_bytes(Ed25519PrivateKey.generate().private_bytes(serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,serialization.NoEncryption()));path.chmod(0o600)
            read=os.read
            def changed(descriptor,size):
                result=read(descriptor,size)
                path.chmod(0o644)
                return result
            with patch.object(d.os,'read',side_effect=changed),self.assertRaises(d.Gate):d.private_key(path)

    def test_signed_digest_bound_to_account_environment_and_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp);key=Ed25519PrivateKey.generate();private=path/'private.pem';public=path/'public.pem';release=path/'release.json'
            private.write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()));private.chmod(0o600)
            public.write_bytes(key.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo))
            body={'environment':'qa','account':'123456789012','region':'us-east-2','image_digest':'sha256:'+'b'*64,'release_id':'c'*40,'database_schema':1,'inference_available':False}
            from deploy.provenance import REPOSITORY, WORKFLOW_PATH, REQUIRED_JOBS, sha256
            proof={'provider':'github_actions','repository':REPOSITORY,'workflow_path':WORKFLOW_PATH,'workflow_id':1,'run_id':2,'run_attempt':1,'head_sha':body['release_id'],'run_url':f'https://github.com/{REPOSITORY}/actions/runs/2','event':'push','head_branch':'main','jobs':{name:i for i,name in enumerate(sorted(REQUIRED_JOBS),1)}}
            body.update(gate_provenance=proof,gate_provenance_sha256=sha256(proof))
            body.update(oci_revision=body['release_id'],image_config_digest='sha256:'+'f'*64)
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
