"""Release-evidence adversarial unit tests; mocked GitHub is not live CI evidence."""
import copy
from datetime import datetime, timedelta, timezone
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch, Mock

import httpx
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("deployment_provenance", ROOT / "deploy/platform.py")
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
from deploy import provenance as p

SHA = "c" * 40
NOW = datetime(2026, 10, 11, 12, tzinfo=timezone.utc)


def gate_fixture():
    evidence = {"revision": SHA, "run_url": f"https://github.com/{p.REPOSITORY}/actions/runs/23", "passed": sorted(p.REQUIRED_GATE_LABELS)}
    run = {"id": 23, "head_sha": SHA, "status": "completed", "conclusion": "success", "path": p.WORKFLOW_PATH,
           "repository": {"full_name": p.REPOSITORY}, "head_repository": {"full_name": p.REPOSITORY},
           "head_branch": "main", "event": "push", "run_attempt": 2, "workflow_id": 17}
    jobs = [{"id": i, "name": name, "run_id": 23, "run_attempt": 2, "head_sha": SHA, "status": "completed", "conclusion": "success"}
            for i, name in enumerate(sorted(p.REQUIRED_JOBS), 1)]
    return evidence, run, jobs


def fixture_client(run, jobs, *, second_run=None, workflow=None, count=None, status=200):
    requests = []
    workflow = workflow or {"id": 17, "path": p.WORKFLOW_PATH, "state": "active"}
    def respond(request):
        requests.append(request)
        if "/attempts/" in request.url.path:
            page = int(request.url.params["page"])
            value = {"total_count": len(jobs) if count is None else count, "jobs": jobs[(page - 1) * 100:page * 100]}
        elif "/workflows/" in request.url.path:
            value = workflow
        else:
            value = second_run if second_run is not None and sum("/attempts/" not in r.url.path and "/workflows/" not in r.url.path for r in requests) > 1 else run
        return httpx.Response(status, json=value)
    return httpx.Client(transport=httpx.MockTransport(respond), follow_redirects=False), requests


def keys(root):
    private, public = root / "private.pem", root / "trusted.pem"
    key = Ed25519PrivateKey.generate()
    private.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    private.chmod(0o600)
    public.write_bytes(key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
    return private, public


def qa_fixture(now=NOW):
    expected = {"account": "123456789012", "region": "us-east-2", "image_digest": "sha256:" + "b" * 64,
                "release_id": SHA, "qa_release_sha256": "d" * 64, "gate_provenance_sha256": "e" * 64}
    body = {**expected, "schema_version": "1.0.0", "purpose": "qa-release-approval", "environment": "qa", "status": "passed",
            "passed_gates": sorted(p.QA_PROBES), "executed_at": (now - timedelta(hours=2)).isoformat(),
            "approved_at": (now - timedelta(hours=1)).isoformat(), "expires_at": (now + timedelta(days=1)).isoformat(),
            "operator_ref": "fixture-reviewer", "evidence_refs": {name: "https://qa-artifacts.invalid/run/fictional-" + name for name in p.QA_PROBES}}
    return expected, body


class ProvenanceTest(unittest.TestCase):
    def test_evidence_and_trusted_key_inputs_refuse_links_and_oversize_before_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);evidence=root/'evidence.json';evidence.write_text('{"revision":"fictional"}')
            self.assertEqual(p.bounded_json(evidence),{'revision':'fictional'})
            link=root/'linked-evidence.json';link.symlink_to(evidence)
            with self.assertRaises(p.Gate):p.bounded_json(link)
            evidence.write_bytes(b'x'*65537)
            with patch.object(p.os,'read') as read,self.assertRaises(p.Gate):p.bounded_json(evidence)
            read.assert_not_called()
            private,public=keys(root)
            record=root/'signed.json';d.sign_release({'fictional':'software'},record,private)
            linked=root/'linked-public.pem';linked.symlink_to(public)
            with self.assertRaises(p.Gate):p.verify_signed_record(record,linked)
            public.write_bytes(b'x'*8193)
            with self.assertRaises(p.Gate):p.verify_signed_record(record,public)

    def test_fifo_evidence_is_rejected_without_waiting_for_a_writer(self):
        with tempfile.TemporaryDirectory() as tmp:
            fifo=Path(tmp)/'fifo.json';os.mkfifo(fifo,0o600)
            code="from pathlib import Path; from deploy.provenance import bounded_json, Gate; import sys\ntry: bounded_json(Path(sys.argv[1]))\nexcept Gate: raise SystemExit(0)\nraise SystemExit(1)"
            environment={key:value for key,value in os.environ.items() if not key.startswith(('AWS_','OTGD_','GH_','GITHUB_'))}
            result=subprocess.run([sys.executable,'-c',code,str(fifo)],cwd=ROOT,env=environment,
                capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,0,result.stderr)

    def test_latest_attempt_requires_every_nested_job_and_aggregate(self):
        evidence, run, jobs = gate_fixture()
        # Independent pagination: mandatory jobs are not necessarily on page one.
        extras = [{**jobs[0], "id": 100 + i, "name": f"extra-{i}"} for i in range(98)]
        client, requests = fixture_client(run, extras + jobs)
        with client:
            proof = p.verify_github_gates(evidence, SHA, client=client)
        self.assertEqual(set(proof["jobs"]), p.REQUIRED_JOBS)
        self.assertEqual(proof["run_attempt"], 2)
        self.assertEqual([r.url.params.get("page") for r in requests if "/attempts/" in r.url.path], ["1", "2"])
        self.assertTrue(all(r.url.host == "api.github.com" for r in requests))
        self.assertEqual(p.validate_gate_binding(proof, SHA), p.sha256(proof))

    def test_local_claims_cannot_replace_missing_failed_skipped_or_old_attempt_jobs(self):
        evidence, run, jobs = gate_fixture()
        failures = [[x for x in jobs if x["name"] != name] for name in sorted(p.REQUIRED_JOBS)]
        for field, value in (("conclusion", "skipped"), ("conclusion", "failure"), ("conclusion", "cancelled"), ("status", "in_progress"), ("run_attempt", 1), ("head_sha", "a" * 40), ("run_id", 22)):
            changed = copy.deepcopy(jobs)
            changed[0][field] = value
            failures.append(changed)
        failures.append(jobs + [{**jobs[0], "id": 88}])
        for rows in failures:
            with self.subTest(rows=rows[0]):
                client, _ = fixture_client(run, rows)
                with client, self.assertRaises(p.Gate):
                    p.verify_github_gates(evidence, SHA, client=client)

    def test_current_fargate_requires_fourteenth_job_and_preserves_historical_proof(self):
        evidence, run, jobs = gate_fixture()
        runtime = {**jobs[0], "id": 88, "name": "platform / fargate-container-runtime"}
        self.assertEqual(p.FARGATE_REQUIRED_JOBS, p.REQUIRED_JOBS | {runtime["name"]})
        client, _ = fixture_client(run, jobs)
        with client:
            historical = p.verify_github_gates(evidence, SHA, client=client)
        client, _ = fixture_client(run, jobs)
        with client, self.assertRaises(p.Gate):
            p.verify_github_gates(evidence, SHA, client=client, required_jobs=p.FARGATE_REQUIRED_JOBS)
        client, _ = fixture_client(run, jobs + [runtime])
        with client:
            current = p.verify_github_gates(evidence, SHA, client=client,
                                            required_jobs=p.FARGATE_REQUIRED_JOBS)
        self.assertEqual(current, historical)
        self.assertEqual(set(current["jobs"]), p.REQUIRED_JOBS)
        self.assertEqual(p.validate_gate_binding(current, SHA), p.sha256(historical))

    def test_fargate_job_must_be_unique_successful_and_from_the_same_latest_attempt(self):
        evidence, run, jobs = gate_fixture()
        runtime = {**jobs[0], "id": 88, "name": "platform / fargate-container-runtime"}
        cases = [("duplicate", [runtime, {**runtime, "id": 89}])]
        cases.extend((field + "=" + str(value), [{**runtime, field: value}])
                     for field, value in (("conclusion", "skipped"), ("conclusion", "failure"),
                                          ("status", "in_progress"), ("run_attempt", 1),
                                          ("run_id", 22), ("head_sha", "a" * 40)))
        for label, rows in cases:
            client, _ = fixture_client(run, jobs + rows)
            with self.subTest(label=label), client, self.assertRaises(p.Gate):
                p.verify_github_gates(evidence, SHA, client=client,
                                      required_jobs=p.FARGATE_REQUIRED_JOBS)

    def test_required_jobs_cannot_weaken_historical_admission(self):
        evidence, run, jobs = gate_fixture()
        for required in (p.REQUIRED_JOBS - {"merge-gate"}, set(), None,
                         p.REQUIRED_JOBS | {None}, [p.REQUIRED_JOBS]):
            client, requests = fixture_client(run, jobs)
            with self.subTest(required=required), client, self.assertRaises(p.Gate):
                p.verify_github_gates(evidence, SHA, client=client, required_jobs=required)
            self.assertEqual(requests, [])

    def test_gate_file_and_owned_client_preserve_fargate_requirements(self):
        evidence, run, jobs = gate_fixture()
        runtime = {**jobs[0], "id": 88, "name": "platform / fargate-container-runtime"}
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "gates.json"
            path.write_text(json.dumps(evidence))
            for rows, succeeds in ((jobs, False), (jobs + [runtime], True)):
                client, requests = fixture_client(run, rows)
                with self.subTest(succeeds=succeeds), patch.object(p.httpx, "Client", return_value=client):
                    if succeeds:
                        proof = p.verify_gate_file(path, SHA, required_jobs=p.FARGATE_REQUIRED_JOBS)
                        self.assertEqual(set(proof["jobs"]), p.REQUIRED_JOBS)
                    else:
                        with self.assertRaises(p.Gate):
                            p.verify_gate_file(path, SHA, required_jobs=p.FARGATE_REQUIRED_JOBS)
                self.assertTrue(any("/attempts/2/jobs" in request.url.path for request in requests))

    def test_trusted_repository_workflow_main_sha_and_latest_run_are_mandatory(self):
        evidence, run, jobs = gate_fixture()
        for field, value in (("head_sha", "a" * 40), ("path", ".github/workflows/platform.yml"), ("event", "workflow_dispatch"),
                             ("event", "pull_request"), ("head_branch", "feature"), ("conclusion", "failure"),
                             ("status", "in_progress"), ("run_attempt", True), ("repository", {"full_name": "untrusted/fork"}),
                             ("head_repository", {"full_name": "untrusted/fork"})):
            client, _ = fixture_client({**run, field: value}, jobs)
            with self.subTest(field=field), client, self.assertRaises(p.Gate):
                p.verify_github_gates(evidence, SHA, client=client)
        for workflow in ({"id": 17, "path": p.WORKFLOW_PATH, "state": "disabled_manually"}, {"id": 17, "path": ".github/workflows/platform.yml", "state": "active"}):
            client, _ = fixture_client(run, jobs, workflow=workflow)
            with client, self.assertRaises(p.Gate):
                p.verify_github_gates(evidence, SHA, client=client)
        client, _ = fixture_client(run, jobs, second_run={**run, "run_attempt": 3})
        with client, self.assertRaises(p.Gate):
            p.verify_github_gates(evidence, SHA, client=client)

    def test_untrusted_urls_redirects_and_incomplete_pagination_fail_closed(self):
        evidence, run, jobs = gate_fixture()
        for url in (evidence["run_url"] + "?override=1", evidence["run_url"].replace("github.com", "github.com.evil.invalid"),
                    evidence["run_url"].replace(p.REPOSITORY, "fork/project")):
            client, requests = fixture_client(run, jobs)
            with client, self.assertRaises(p.Gate):
                p.verify_github_gates({**evidence, "run_url": url}, SHA, client=client)
            self.assertEqual(requests, [])
        for kwargs in ({"status": 302}, {"status": 403}, {"count": len(jobs) + 1}):
            client, _ = fixture_client(run, jobs, **kwargs)
            with client, self.assertRaises(p.Gate):
                p.verify_github_gates(evidence, SHA, client=client)

    def test_gate_file_rejects_duplicate_json_keys_oversize_and_missing_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "evidence.json"
            for content in ('{"revision":"a","revision":"b"}', " " * 65537):
                path.write_text(content)
                with self.assertRaises(p.Gate):
                    p.bounded_json(path)
            with self.assertRaises(p.Gate):
                p.verify_gate_file(None, SHA)

    def test_qa_approval_requires_trusted_signature_every_probe_and_exact_source(self):
        expected, body = qa_fixture()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            private, public = keys(root)
            path = root / "approval.json"
            path.write_text(json.dumps(body))
            with self.assertRaises(p.Gate):
                p.verify_qa_approval(path, public, expected, now=NOW)
            path.unlink()
            d.sign_release(body, path, private)
            self.assertEqual(p.verify_qa_approval(path, public, expected, now=NOW), body)
            for field in expected:
                with self.subTest(field=field), self.assertRaises(p.Gate):
                    p.verify_qa_approval(path, public, {**expected, field: "different"}, now=NOW)
            other = root / "different"
            other.mkdir()
            _, wrong_public = keys(other)
            with self.assertRaises(InvalidSignature):
                p.verify_qa_approval(path, wrong_public, expected, now=NOW)
        for change in ({"passed_gates": []}, {"evidence_refs": {}}, {"operator_ref": ""}, {"environment": "prod"}, {"status": "pending"}):
            with self.subTest(change=change), self.assertRaises(p.Gate):
                p.validate_qa_approval({**body, **change}, expected, now=NOW)

    def test_qa_approval_expiry_future_execution_and_non_utc_are_rejected(self):
        expected, body = qa_fixture()
        for change in ({"expires_at": NOW.isoformat()}, {"expires_at": (NOW + timedelta(days=8)).isoformat()},
                       {"executed_at": (NOW + timedelta(minutes=1)).isoformat()}, {"approved_at": (NOW + timedelta(minutes=1)).isoformat()},
                       {"approved_at": "2026-10-11T10:00:00"}, {"approved_at": "2026-10-11T10:00:00+01:00"}):
            with self.subTest(change=change), self.assertRaises(p.Gate):
                p.validate_qa_approval({**body, **change}, expected, now=NOW)

    def test_build_refuses_local_json_gate_claim_before_docker_or_signing(self):
        import sys
        cfg = {"environment": "qa", "releaseId": SHA}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with patch.object(sys, "argv", ["platform.py", "build", "--config", str(root / "qa.json"), "--output", str(root / "release.json"), "--signing-key", str(root / "key.pem"), "--trusted-public-key", str(root / "public.pem")]), \
                    patch.object(d, "read_config", return_value=cfg), patch.object(d, "preflight"), \
                    patch.object(d, "run", side_effect=["", SHA]), patch.object(d, "login") as login, \
                    patch.object(d, "sign_release") as signing, self.assertRaises(p.Gate):
                d.main()
            login.assert_not_called()
            signing.assert_not_called()

    def test_production_activation_rechecks_signed_git_and_exact_qa_envelopes(self):
        import hashlib
        evidence, run, jobs = gate_fixture()
        client, _ = fixture_client(run, jobs)
        with client:
            proof = p.verify_github_gates(evidence, SHA, client=client)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            private, public = keys(root)
            expected, approval = qa_fixture(datetime.now(timezone.utc))
            expected["gate_provenance_sha256"] = p.sha256(proof)
            approval.update(expected)
            qa = root / "qa-approval.json"
            d.sign_release(approval, qa, private)
            payload = {"environment": "prod", "account": "987654321098", "region": "us-east-2",
                       "image_digest": expected["image_digest"], "release_id": SHA, "database_schema": 1,
                       "inference_available": False, "gate_provenance": proof, "gate_provenance_sha256": p.sha256(proof),
                       "oci_revision": SHA,"image_config_digest": "sha256:"+"f"*64,
                       "qa_source": expected, "promoted_from_release_sha256": expected["qa_release_sha256"],
                       "qa_evidence_sha256": hashlib.sha256(qa.read_bytes()).hexdigest()}
            release = root / "prod.json"
            d.sign_release(payload, release, private)
            cfg = {"environment": "prod", "account": payload["account"], "region": payload["region"],
                   "releaseId": SHA, "imageDigest": payload["image_digest"]}
            args = SimpleNamespace(release=release, trusted_public_key=public, gate_evidence=root / "gates.json", qa_evidence=qa)
            with patch.object(d, "verify_gate_file", return_value=proof):
                self.assertEqual(d.require_release(args, cfg), payload)
                args.qa_evidence = None
                with self.assertRaises(p.Gate):
                    d.require_release(args, cfg)
                args.qa_evidence = qa
                # The signed production approval binds the exact QA envelope,
                # even when another byte representation still verifies.
                qa.write_text(qa.read_text() + "\n")
                with self.assertRaises(p.Gate):
                    d.require_release(args, cfg)
            with patch.object(d, "verify_gate_file", return_value={**proof, "run_attempt": 3}), self.assertRaises(p.Gate):
                d.require_release(args, cfg)

    def test_signer_must_match_independently_trusted_key(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            private, public = keys(root)
            d.require_trusted_signer(private, public)
            other = root / "other"
            other.mkdir()
            _, wrong = keys(other)
            with self.assertRaises(p.Gate):
                d.require_trusted_signer(private, wrong)
            with self.assertRaises(p.Gate):
                d.require_trusted_signer(private, None)

    def test_cloud_image_manifest_and_local_config_must_bind_signed_source(self):
        import hashlib
        raw=json.dumps({"schemaVersion":2,"mediaType":"application/vnd.oci.image.manifest.v1+json",
                        "config":{"digest":"sha256:"+"f"*64},"layers":[]})
        digest="sha256:"+hashlib.sha256(raw.encode()).hexdigest()
        cfg={"environment":"qa","imageDigest":digest}
        response={"images":[{"imageId":{"imageDigest":digest},"imageManifest":raw}]}
        ecr=Mock();ecr.batch_get_image.return_value=response
        aws=Mock();aws.client.return_value=ecr
        self.assertEqual(d.image_config_digest(aws,cfg),"sha256:"+"f"*64)
        d.verify_release_image(aws,cfg,{"image_config_digest":"sha256:"+"f"*64})
        with self.assertRaises(p.Gate):
            d.verify_release_image(aws,cfg,{"image_config_digest":"sha256:"+"e"*64})
        for changed in ({"images":[]},{"failures":[{"failureCode":"ImageNotFound"}],**response},
                        {"images":[{**response["images"][0],"imageManifest":raw+" "}]},
                        {"images":[{**response["images"][0],"imageId":{"imageDigest":"sha256:"+"a"*64}}]}):
            ecr.batch_get_image.return_value=changed
            with self.subTest(response=changed),self.assertRaises(p.Gate):
                d.image_config_digest(aws,cfg)
        reference="registry.invalid/otgd-qa@"+digest
        inspected={"id":"sha256:"+"f"*64,"labels":{"org.opencontainers.image.revision":SHA},"repo_digests":[reference]}
        with patch.object(d,"run",side_effect=["",json.dumps(inspected)]):
            d.verify_container_source("registry.invalid/otgd-qa",digest,SHA,"sha256:"+"f"*64)
        for changed in ({"labels":{"org.opencontainers.image.revision":"a"*40}},{"id":"sha256:"+"a"*64},{"repo_digests":[]}):
            with patch.object(d,"run",side_effect=["",json.dumps({**inspected,**changed})]),self.assertRaises(p.Gate):
                d.verify_container_source("registry.invalid/otgd-qa",digest,SHA,"sha256:"+"f"*64)
        for values in (["a"*40],[SHA," M services/api/otgd/main.py"]):
            with patch.object(d,"run",side_effect=values),self.assertRaises(p.Gate):
                d.require_clean_source(SHA)


if __name__ == "__main__":
    unittest.main()
