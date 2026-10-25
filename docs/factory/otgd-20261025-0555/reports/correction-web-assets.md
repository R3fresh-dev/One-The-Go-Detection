# Round1 complete web-asset verification

Owner /root, OpenAI GPT-6 family per host; exact runtime variant unavailable. D009v5 authorized existing WEB-DEP-007/010 transport acceptance repair; correction1/2, recovery0/3. No deployment, public-service probe or publication was performed.

The verifier previously checked only index.html and the first JavaScript chunk. It now checks every admitted file's exact bounded bytes, including secondary scripts, CSS, images and additional HTML. Every HTML response must pass the existing exact security-header policy. Deep-link, missing-asset, readiness, no-redirect, identity-encoding and bounded-length/hash checks remain intact.

New regression matrix proves every expected asset is requested once; missing, same-length changed, and oversized secondary script/CSS/image/HTML bodies refuse verification before readiness can establish success. A second test refuses missing security policy on an additional HTML page.

The first direct pytest invocation failed during collection because it omitted repository package context (`ModuleNotFoundError: deploy`); no tests executed. Corrected command uses `uv run --project services/api python -m pytest`. Before production repair it recorded14 intended assertion failures (including13 subtests),1 method pass,32 deselections. After repair the entire test_web_deployment.py suite passed; raw output below is authoritative. These are actual HTTP MockTransport software checks, not cloud acceptance.

Final command: `UV_CACHE_DIR=/tmp/otgd-uv-cache uv run --project services/api python -m pytest infra/test/test_web_deployment.py -q --junitxml=/workspace/scratch/otgd-20261025-0555-live/web-assets-green.xml`. Exit0.

```text
................. [ 50%]
.................         [100%]
=============================== warnings summary ===============================
infra/test/test_web_deployment.py::WebArtifactTest::test_public_asset_types_paths_symlinks_and_duplicate_zip_entries_are_rejected
  /opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/zipfile/__init__.py:1625: UserWarning: Duplicate name: 'index.html'
    return self._open_to_write(zinfo, force_zip64=force_zip64)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
34 passed, 1 warning, 102 subtests passed in 0.28s
```

- `deploy/web_artifact.py` SHA-256 `883b39d1a57992a7ee0124f85b861f5ae76ec1ff5e316e7c0f99b74cac7bda32`
- `infra/test/test_web_deployment.py` SHA-256 `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`
- `/workspace/scratch/otgd-20261025-0555-live/web-assets-red.log` SHA-256 `731f408509c20696712dac65e616ee64b05c95103fa3a109aeb0de252a8a697a`
- `/workspace/scratch/otgd-20261025-0555-live/web-assets-red-executed.log` SHA-256 `9cb9127654492453b31e75539247fd78b646e27b0aad94ca2cf2d3bfa6bcaebf`
- `/workspace/scratch/otgd-20261025-0555-live/web-assets-green.log` SHA-256 `4073b91451a1a470fe2eac450b75a59078d5c644553f33142a27517ec3f823ae`
- `/workspace/scratch/otgd-20261025-0555-live/web-assets-green.xml` SHA-256 `ca7942930c54712db489a4d6dd7e930cd6e3f2e34e2f81698955c175751b392a`

The earlier auth report binding of these shared files remains historical. Final combined-source unit/infra/CI gates and independent confirmations are still required. No scope, signed-artifact identity or authenticated-customer claim was broadened.
