# Local compact API image proof — otgd-20261025-0555

**PASS for D-006 v2 declared-source packaging proof; runtime execution not performed.** A compact candidate exists with the exact declared saved-source filesystem and complete original runtime Config. Original source image, raw import, raw export, normalized tar and proof container remain preserved. Raw-export/live-VFS discrepancy is unresolved and explicitly not treated as equivalence.

Role: /root/firmware_validation, assigned OpenAI gpt-6.1-sol/high; bounded environment-engineering follow-up. Candidate/check time 2026-10-25T06:31:19.276205+00:00. D-005 v1 and D-006 v1/v2 impact acknowledgments were sent via actual messages; PM accepted v2 after engineering disposition and explicitly authorized the serialized-Config remedy. Mutations were recorded beforehand in action-plan.md and announced to PM. correction_round=0; recovery_attempts=0. No source/gate change, repository Git operation, source retag, image/container/volume deletion, canonical service start/restart, deployment or spend. Earlier firmware report was unaffected.

## Identities and sizes

| Artifact/image | Identity | Size/layers |
|---|---|---|
| Original canonical otgd-api:local | `sha256:cdc2ea781670c2d2400d38af490cf5ef5672334d4f64e439ce40a9f21ee78b31` | 358,016,053B / 17 layers |
| Raw Docker import, preserved by image ID and archive | `sha256:12ac1094e4c6d3ba8733ae735ac85e6f1908af5ba64451211a3d0d4fbbf7b448` | 255,895,545B / 1 layer; ArgsEscaped mismatch, not admissible |
| Final otgd-api:factory-compact candidate | `sha256:1af98b2872a49d3be4f8e6468507e9bc56468b1554252dcdf19293c21850d57b` | 255,895,545B / 1 layer |
| Normalized rootfs / sole DiffID | `sha256:9eb7ae54a33c8a183824112d1ab367bf9a2709e051536e20fe7ed01d2ef7c7e3` | 268,462,080B tar |
| Exact-config load archive | SHA256 `5fb95ab59f2bcb5d00d2c6b1dcd54c170217c11ef9b1b67245ea21abfc82a496` | 268,472,320B |

Docker image-size reduction is 102,120,508 bytes (28.52%). These are local image/config identities, not registry admission digests. OS/architecture linux/amd64 match. Cloud qualification is not claimed. Per-service VFS snapshot costs and complete runtime capacity have **not** been executed or established by the size reduction.

## Proof actually executed

1. Saved original source image without retagging it. Saved serialized config SHA256 exactly equals source image ID; all 17 ordered layer byte hashes equal its declared RootFS DiffIDs.
2. Created only uniquely named proof container `otgd-image-proof-otgd-20261025-0617`, ID b7d2aff870abaf97c3e38f2b0004abf527b0ef35ac41ba08e8306e83e06a14f0, --network none, --pull never, --tmpfs /tmp. It was never started. Status=created, Running=false, Pid=0, StartedAt=0001-01-01T00:00:00Z, Mounts=[]; no anonymous volume exists.
3. Exported its underlying rootfs, independently merged saved layers and compared files without executing image contents. Raw export failed strict equivalence as detailed below. No mismatch was waived.
4. Under accepted D-006 v2, normalized only recorded differences to the **declared saved-source** entries. Full normalized manifest equals source: 17,092 entries, zero missing/added/changed, zero timestamp differences. Numeric ownership/mode, every payload SHA256+length, symlink text, complete hardlink topology, device types/numbers and non-path/time PAX xattr/ACL/capability fields were compared. Both archives have identical 3,569 hardlink groups covering 7,138 paths. Neither declares xattrs/ACL/capabilities or special-file records. Source has no whiteouts; compositor implements ordinary and opaque whiteouts and self-checks them.
5. Imported normalized tar under candidate-only tag. Sole layer DiffID equals normalized tar SHA256. Initial import succeeded but strict Config check failed: Docker omitted source ArgsEscaped=true. All other inspected Config fields matched. Failure is preserved, not converted into PASS.
6. PM authorized bounded serialized metadata restoration: saved raw imported image; replaced its serialized config.Config with exact original source config.Config; retained all other imported image config sections/history/rootfs; recomputed config digest/size, OCI manifest digest/size, index and Docker manifest references. Output archive contains only referenced config/manifest/layer blobs. Independently checked every blob digest and descriptor size. Loaded only candidate tag. Raw imported image ID remains present, though tag moved to final candidate as load explicitly reported.
7. Final inspect verifies **whole Config equality**, including ArgsEscaped=true and all absent/null fields; Env/Cmd/Entrypoint/User/WorkingDir/ExposedPorts/Healthcheck/Volumes/StopSignal match. Sole layer DiffID and linux/amd64 match requirements. Original canonical source image ID remains unchanged. Final proof and all supporting hashes are retained.

The comparator models hardlink inode snapshots at creation, including later path overwrite, and symlink ancestors. Self-checks cover hardlinks, whiteouts, symlink parents and capability/xattr/ownership differences. The first self-check fixture used a shallow mutable snapshot and failed; deepcopy corrected that fixture, with main compositor unchanged. Initial root-excluding comparison was tightened to include explicit root and exact timestamps; original evidence versions are retained under .v1-excluded-root names. Complete final equality uses the tightened comparator.

## Raw export discrepancy and exact restorations

Raw export tar:267,728,896B, SHA256 `3c6bea67100d93f33a83a3c1e1d7d711d317b1a76760c84873800cf7d07b1061`. Its 17,097 entries differ from the declared source's 17,092: source root '.' header omitted; six Docker init/mount additions; changed source hostname/resolv bytes/modes; changed group- backup bytes; dev/etc/run directory timestamps. This is **not** claimed identical to source/live VFS or a hardware/cloud attestation.

Removed only `.dockerenv`, `dev/console`, `dev/pts`, `dev/shm`, `etc/hosts`, `etc/mtab`. Restored exact original headers/payloads below. All have empty xattr/ACL PAX data and no links; active group/passwd, application code, protected storage and Config were not altered by normalization.

| Restored target | Source archive layer/member | Original mode UID:GID / mtime | Bytes/SHA256 |
|---|---|---|---|
| `.` | layer0 `blobs/sha256/e58989146fcec76699871403b9897b5c014af1ccd85f5a9300a215e7975525d7` member `.` | 0o755 0:0 / 1791158400 | 0B / `None` |
| `dev` | layer0 `blobs/sha256/e58989146fcec76699871403b9897b5c014af1ccd85f5a9300a215e7975525d7` member `dev` | 0o755 0:0 / 1791158400 | 0B / `None` |
| `etc` | layer4 `blobs/sha256/80e3d46afd4f9f075da34f184a925ed6a3ec591c19b57db314e3b50c701d6778` member `etc` | 0o755 0:0 / 1792908153 | 0B / `None` |
| `etc/group-` | layer0 `blobs/sha256/e58989146fcec76699871403b9897b5c014af1ccd85f5a9300a215e7975525d7` member `etc/group-` | 0o644 0:0 / 1791158400 | 434B / `0cc1a09e6a22f2c31ef0279e880f5e53bfb9fc86eb4a57fa8bfcbcd6ad72fc41` |
| `etc/hostname` | layer0 `blobs/sha256/e58989146fcec76699871403b9897b5c014af1ccd85f5a9300a215e7975525d7` member `etc/hostname` | 0o644 0:0 / 1791158400 | 14B / `411eb208674138b8ce7624993e678f6b1d8a39c6f2bc4156e10d9466e0c71d2b` |
| `etc/resolv.conf` | layer0 `blobs/sha256/e58989146fcec76699871403b9897b5c014af1ccd85f5a9300a215e7975525d7` member `etc/resolv.conf` | 0o644 0:0 / 1791158400 | 104B / `a535ac16b8fe54e9e1afbb474c4c19fd8faeddbac8b1e1c17f8f52191ce84f96` |
| `run` | layer0 `blobs/sha256/e58989146fcec76699871403b9897b5c014af1ccd85f5a9300a215e7975525d7` member `run` | 0o755 0:0 / 1791158400 | 0B / `None` |

The only source etc/group- entry is a regular base-layer file,434B SHA2560cc1a09e6a22f2c31ef0279e880f5e53bfb9fc86eb4a57fa8bfcbcd6ad72fc41. Layer4 replaces active etc/group but contains no etc/group-. Raw export's regular group- instead hashes74842904631a5088b134a25257b8180367913d2b64cf1e3fed061db5fcbd8379, equal to base etc/group. No source or export hardlink is involved in this mismatch; hardlink-update count is zero. `docker container diff` on the never-started proof emitted no rows. Cause remains unresolved; accepted v2 constructs the exact declared saved-source image and does not characterize this as raw/live equality. Both versions remain preserved.

Docker documents that export omits mounted-volume contents and uses the underlying image directory, and import restores metadata only through supported --change instructions. [Docker export](https://docs.docker.com/reference/cli/docker/container/export/), [Docker import](https://docs.docker.com/reference/cli/docker/image/import/). Moby28.4.0 derives imported Config using BuildFromConfig and command dispatch; this is consistent with the measured ArgsEscaped omission. [Import implementation](https://raw.githubusercontent.com/moby/moby/v28.4.0/daemon/images/image_import.go), [command dispatch](https://raw.githubusercontent.com/moby/moby/v28.4.0/builder/dockerfile/dispatchers.go). Exact equality was restored through the separately authorized archive metadata remedy, not an assertion that import supports every Config field.

## Preserved services, resource bounds and next action

At 2026-10-25T06:31:19.276205+00:00, PostgreSQL and LocalStack were healthy with identical IDs, image IDs, Created/StartedAt timestamps, Config/HostConfig hashes and named-volume mounts compared to the initial snapshots. Proof container remains created/never started and no anonymous volume was created. Source/raw-import/final-candidate images remain inspectable.

Root headroom minimum during import:1,168,982,016B; during load:912,502,784B. Neither700MiB guard triggered. Final /workspace free:1,168,855,040B; /tmp free:2,779,070,464B. No cleanup or resizing performed.

**Remaining hold:** canonical retag, deletion and service start/restart were not executed and require explicit PM assignment after reviewing this proof. Full LocalStack/API/worker/live-dependency/performance/gate execution remains pending outside this packaging proof. Raw/live export discrepancy remains an identified limitation. The smaller reported image does not establish enough disk for the complete concurrent VFS runtime; measure that separately with headroom preserved. No blocked install, denial or uncertain Docker operation remains in this assignment.

## Exact commands and results

**source-save** — 2026-10-25T06:18:43.963832+00:00 to 2026-10-25T06:18:46.529118+00:00; exit0; 2.565s. Log `/tmp/otgd-image-proof/source-save.log`.

```json
[
  "docker",
  "image",
  "save",
  "-o",
  "/tmp/otgd-image-proof/source-image.tar",
  "sha256:cdc2ea781670c2d2400d38af490cf5ef5672334d4f64e439ce40a9f21ee78b31"
]
```

**proof-create** — 2026-10-25T06:19:03.378056+00:00 to 2026-10-25T06:19:04.463483+00:00; exit0; 1.085s. Log `/tmp/otgd-image-proof/proof-create.log`.

```json
[
  "docker",
  "container",
  "create",
  "--name",
  "otgd-image-proof-otgd-20261025-0617",
  "--network",
  "none",
  "--pull",
  "never",
  "--tmpfs",
  "/tmp",
  "sha256:cdc2ea781670c2d2400d38af490cf5ef5672334d4f64e439ce40a9f21ee78b31"
]
```

**proof-export** — 2026-10-25T06:19:04.524797+00:00 to 2026-10-25T06:19:06.699845+00:00; exit0; 2.175s. Log `/tmp/otgd-image-proof/proof-export.log`.

```json
[
  "docker",
  "container",
  "export",
  "-o",
  "/tmp/otgd-image-proof/rootfs.tar",
  "otgd-image-proof-otgd-20261025-0617"
]
```

**filesystem-comparison** — 2026-10-25T06:20:43.369646+00:00 to 2026-10-25T06:20:53.002312+00:00; exit0; 9.633s. Log `/tmp/otgd-image-proof/filesystem-comparison.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/compare.py"
]
```

**proof-diff** — 2026-10-25T06:21:41.582867+00:00 to 2026-10-25T06:21:41.890854+00:00; exit0; 0.308s. Log `/tmp/otgd-image-proof/proof-diff.log`.

```json
[
  "docker",
  "container",
  "diff",
  "otgd-image-proof-otgd-20261025-0617"
]
```

**comparator-selftest** — 2026-10-25T06:22:37.190319+00:00 to 2026-10-25T06:22:37.223086+00:00; exit1; 0.033s. Log `/tmp/otgd-image-proof/comparator-selftest.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/comparator-selftest.py"
]
```

**comparator-selftest-deepcopy** — 2026-10-25T06:22:46.147661+00:00 to 2026-10-25T06:22:46.175938+00:00; exit0; 0.028s. Log `/tmp/otgd-image-proof/comparator-selftest-deepcopy.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/comparator-selftest.py"
]
```

**filesystem-comparison-v2-root-times** — 2026-10-25T06:25:48.369821+00:00 to 2026-10-25T06:25:59.179308+00:00; exit0; 10.809s. Log `/tmp/otgd-image-proof/filesystem-comparison-v2-root-times.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/compare.py"
]
```

**comparator-selftest-v2-root-times** — 2026-10-25T06:25:59.216754+00:00 to 2026-10-25T06:25:59.251154+00:00; exit0; 0.034s. Log `/tmp/otgd-image-proof/comparator-selftest-v2-root-times.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/comparator-selftest.py"
]
```

**normalization** — 2026-10-25T06:27:03.022968+00:00 to 2026-10-25T06:27:06.064647+00:00; exit0; 3.042s. Log `/tmp/otgd-image-proof/normalization.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/normalize.py"
]
```

**normalized-filesystem-comparison** — 2026-10-25T06:27:13.740682+00:00 to 2026-10-25T06:27:23.668493+00:00; exit0; 9.928s. Log `/tmp/otgd-image-proof/normalized-filesystem-comparison.log`.

```json
[
  "env",
  "OTGD_IMAGE_PROOF_CANDIDATE=/tmp/otgd-image-proof/normalized-rootfs.tar",
  "OTGD_IMAGE_PROOF_SUFFIX=-normalized",
  "python3",
  "/tmp/otgd-image-proof/compare.py"
]
```

**candidate-import-and-verify** — 2026-10-25T06:28:38.564427+00:00 to 2026-10-25T06:28:42.277641+00:00; exit1; 3.713s. Log `/tmp/otgd-image-proof/candidate-import-and-verify.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/import_candidate.py"
]
```

**candidate-save** — 2026-10-25T06:29:52.856914+00:00 to 2026-10-25T06:29:54.663310+00:00; exit0; 1.806s. Log `/tmp/otgd-image-proof/candidate-save.log`.

```json
[
  "docker",
  "image",
  "save",
  "-o",
  "/tmp/otgd-image-proof/candidate-imported-image.tar",
  "sha256:12ac1094e4c6d3ba8733ae735ac85e6f1908af5ba64451211a3d0d4fbbf7b448"
]
```

**restore-serialized-config** — 2026-10-25T06:30:51.022541+00:00 to 2026-10-25T06:30:53.264191+00:00; exit0; 2.242s. Log `/tmp/otgd-image-proof/restore-serialized-config.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/restore_config.py"
]
```

**candidate-load-and-final-verify** — 2026-10-25T06:31:18.573308+00:00 to 2026-10-25T06:31:19.288186+00:00; exit0; 0.715s. Log `/tmp/otgd-image-proof/candidate-load-and-final-verify.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/load_and_verify.py"
]
```

Nested actual import/load commands (helper wrappers above record full results):

```json
[
  "docker",
  "image",
  "import",
  "--platform",
  "linux/amd64",
  "--message",
  "Factory D-006 v2 exact declared-source local compact packaging; no cloud admission",
  "--change",
  "ENV PATH=\"/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\"",
  "--change",
  "ENV LANG=\"C.UTF-8\"",
  "--change",
  "ENV GPG_KEY=\"7169605F62C751356D054A26A821E680E5FA6305\"",
  "--change",
  "ENV PYTHON_VERSION=\"3.12.15\"",
  "--change",
  "ENV PYTHON_SHA256=\"c2c4321961fab0fb999d66e0cecf521c2ab3994c7992873ea99e306c1094fd5a\"",
  "--change",
  "ENV PYTHONUNBUFFERED=\"1\"",
  "--change",
  "ENV PYTHONDONTWRITEBYTECODE=\"1\"",
  "--change",
  "ENV UV_PROJECT_ENVIRONMENT=\"/opt/venv\"",
  "--change",
  "ENV UV_NO_SYNC=\"1\"",
  "--change",
  "ENV UV_CACHE_DIR=\"/tmp/uv-cache\"",
  "--change",
  "CMD [\"uv\", \"run\", \"--no-sync\", \"uvicorn\", \"otgd.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\", \"--no-access-log\", \"--limit-concurrency\", \"100\", \"--timeout-graceful-shutdown\", \"100\"]",
  "--change",
  "USER 10001",
  "--change",
  "WORKDIR /app/services/api",
  "--change",
  "EXPOSE 8000/tcp",
  "--change",
  "VOLUME [\"/tmp\"]",
  "/tmp/otgd-image-proof/normalized-rootfs.tar",
  "otgd-api:factory-compact"
]
```

```json
[
  "docker",
  "image",
  "load",
  "--input",
  "/tmp/otgd-image-proof/candidate-exact-config-image.tar"
]
```

## Current artifact hashes

Scripts, archives and receipts are reproducible inputs/evidence under /tmp. Original/raw files were preserved; final report records immutable hashes even if temporary storage later expires.

| Artifact | Bytes | SHA256 |
|---|---:|---|
| `/tmp/otgd-image-proof/action-plan.md` | 3,662 | `13fa0f8cd9dc1bd41c4471c7717f3381b6f4fefbf0cae766fbb178eb0618b28b` |
| `/tmp/otgd-image-proof/archive-manifest.json` | 6,269 | `8272f1ad3c8507b06049844d43f2340b82b0647a10d21825f79b0d149f7264c4` |
| `/tmp/otgd-image-proof/candidate-equivalence.json` | 3,012 | `f3ab82352a521247708171566736657c6ce4b33e07a9804538f1987d4e792cf7` |
| `/tmp/otgd-image-proof/candidate-exact-config-image.tar` | 268,472,320 | `5fb95ab59f2bcb5d00d2c6b1dcd54c170217c11ef9b1b67245ea21abfc82a496` |
| `/tmp/otgd-image-proof/candidate-exact-inspect.json` | 1,711 | `2b16f2c0e12bf9c87c737716c80a998b5c1ab4e9a74ab4b20cbacb65fd0f5a50` |
| `/tmp/otgd-image-proof/candidate-import-and-verify.log` | 6,832 | `47555b1f28c306057e42b8e43b4d29c25bc878de761e3574cbcc56210dbe2019` |
| `/tmp/otgd-image-proof/candidate-import.log` | 1,304 | `daa807dce262d127bf2756c0b6365d9c98138aea2ce17f44b89e7d78073b1f02` |
| `/tmp/otgd-image-proof/candidate-imported-image.tar` | 268,473,344 | `e569b4fb2b7b9370e5b3dd5125476ea82b8589e36af28acd383f4d86a60e06e7` |
| `/tmp/otgd-image-proof/candidate-inspect.json` | 1,696 | `7217d14e2944bc5676ed4b8e7644b6c62e6c2cb82bb0b57edb0882f7061b8c9d` |
| `/tmp/otgd-image-proof/candidate-load-and-final-verify.log` | 1,445 | `674b9ee46d69c3df2da1c285ac82aeb790c912010712ab925fccdc4f3fe465a3` |
| `/tmp/otgd-image-proof/candidate-load-result.json` | 321 | `1b536a2f4be369a75c31a087a4ceea59c53391c18b4b62cef84641b3c0ac9532` |
| `/tmp/otgd-image-proof/candidate-load.log` | 351 | `eb586d7d6693ee981be131c500818a0a4133974909a90b32b85f8e7067001cbe` |
| `/tmp/otgd-image-proof/candidate-save.log` | 210 | `62f9024ac24c256a1cb0c34f82dafa02268b107d66adf7c2d60465572e93dfff` |
| `/tmp/otgd-image-proof/commands.jsonl` | 4,990 | `1d16695b8f0d5c4003caa74e9cebb7bbafd53bd7ddf2a5cf91b29e547aa32a80` |
| `/tmp/otgd-image-proof/comparator-selftest-deepcopy.log` | 277 | `6743b76babfc60d2b98f853394f96b205c0bd997a0d7df46d5a51cc2f5f93c27` |
| `/tmp/otgd-image-proof/comparator-selftest-v2-root-times.log` | 277 | `271b3350cdc870f86fa98b35e3c22b049f0ff330fbd3aad0f0fbb6f5c9cfc756` |
| `/tmp/otgd-image-proof/comparator-selftest.log` | 545 | `8db4064cead5292e1dc7767754132a31da0dbf7ab30800359521aa292bdde4fc` |
| `/tmp/otgd-image-proof/comparator-selftest.py` | 1,708 | `212d69aee23f2205bc8e5ffd2c85ba884b148dcaa2751871a2dc6490f8a80ba3` |
| `/tmp/otgd-image-proof/compare.py` | 6,906 | `105659341cbc2fd076d39b542bcabf42e221ab2ebefe10512777c76b0cfb1339` |
| `/tmp/otgd-image-proof/compare.py.v1-excluded-root` | 6,653 | `1beaf875ebbcfb958ba6d3042da89d7605ba2db33eccfe4b3e5e104f0914b2f1` |
| `/tmp/otgd-image-proof/config-restoration-receipt.json` | 1,884 | `5ef390787cab0686e7a10804e2a63b1f4c80330c42d26182d854bf44a24864d1` |
| `/tmp/otgd-image-proof/export-filesystem.json` | 6,290,917 | `bf5305d9f847edc577e9f0283d5720576e2adb7a0c6fdff7802be549123356b5` |
| `/tmp/otgd-image-proof/export-filesystem.json.v1-excluded-root` | 5,829,300 | `22773ba5c0b703fe4b30184e1b4baceb620aeee69a773d2e01c8bddae46d7273` |
| `/tmp/otgd-image-proof/export-normalized-filesystem.json` | 6,289,838 | `2efd948397f34704aec0207c607591c259fe9d1beb492ec6c928ed8b7fa7929b` |
| `/tmp/otgd-image-proof/filesystem-comparison-v2-root-times.log` | 3,870 | `34307910f82a81751237199d12621616bc6275881d4c4118c8dfe635ec496879` |
| `/tmp/otgd-image-proof/filesystem-comparison.json` | 7,779 | `ebda1f1dc4aea69ac0a1a2cb9dc83b5c05af40783344aad765eb6868b764d6a5` |
| `/tmp/otgd-image-proof/filesystem-comparison.json.v1-excluded-root` | 6,427 | `10e4703efc540bbe6a27ee4d38ab3206dfcfaaed2297c323a51b17d1eaee8678` |
| `/tmp/otgd-image-proof/filesystem-comparison.log` | 2,518 | `ce05dff85e5c9e913d9594b2f9330e4d7e76ed96d371a930d1525cc614ac0c0b` |
| `/tmp/otgd-image-proof/filesystem-normalized-comparison.json` | 4,158 | `98c97e52906c2f25423c9c98a9744eae629d439fd079f0048c71a2f898b7a847` |
| `/tmp/otgd-image-proof/final-proof.json` | 3,216 | `5c3401f1306f355a7bb7c46949eb04c3060eaa552441db18b1a7984ea19ef24a` |
| `/tmp/otgd-image-proof/import-command-result.json` | 1,647 | `962501a2245336cb8fc515b972bb25c95f98e643407fb6cf9dd2f894b7663037` |
| `/tmp/otgd-image-proof/import-command.json` | 1,265 | `2a67ab662af3930ec69582a735fc067771cd80f699992e3d1d7967ea9bf8d00d` |
| `/tmp/otgd-image-proof/import_candidate.py` | 4,073 | `f7c76748c3d9eec3363df9852483c2f9aa80c22f07515a651bcb35caf6b3af30` |
| `/tmp/otgd-image-proof/load_and_verify.py` | 4,090 | `afb3e07fbd2a387585c6a4ab10bf032d4eae8229cf9ca1d4ec622fb7911acac6` |
| `/tmp/otgd-image-proof/normalization-proposal.json` | 4,507 | `e5ba5869be3876b1761a64048e42db481e6240f66308a4735514a713edbdbf66` |
| `/tmp/otgd-image-proof/normalization-receipt.json` | 4,170 | `9e8c642814fc8314327808b7450861445f44a9cd45363321e79c045f5c7c8755` |
| `/tmp/otgd-image-proof/normalization.log` | 788 | `a1b56d6e1c2b6b5cf1564e170f59052ea1259a6d0aff911d928e3ef909d357fa` |
| `/tmp/otgd-image-proof/normalize.py` | 2,570 | `85215d294531adde276fcbd1da82ed9e39b75c4432a1674034fc7ec4b14a5270` |
| `/tmp/otgd-image-proof/normalized-filesystem-comparison.log` | 875 | `cab4a64b5f1c6f668ec9ff073b2f5ad321e442204c677822ba1f305b53dc7ebb` |
| `/tmp/otgd-image-proof/normalized-rootfs.tar` | 268,462,080 | `9eb7ae54a33c8a183824112d1ab367bf9a2709e051536e20fe7ed01d2ef7c7e3` |
| `/tmp/otgd-image-proof/proof-container-inspect.json` | 5,739 | `c5a6a53fcbb9331457180aa16efe08eb82b039c249219891fa98584a061c720f` |
| `/tmp/otgd-image-proof/proof-create.log` | 329 | `8064cbbe4b251a54e0323bbc2e6b31b523772cff3e0140d4ffd91943d4788fc2` |
| `/tmp/otgd-image-proof/proof-diff.log` | 118 | `86cb6c4b69bd12ff526bc9d73c64331f3405baa7fcfc041b9ed2644de61a21f3` |
| `/tmp/otgd-image-proof/proof-export.log` | 162 | `b66fcba24e490f0c078f2c4e55f356f47cfbcd7f0faf63d8d281ab84cbd44f0f` |
| `/tmp/otgd-image-proof/restore-serialized-config.log` | 1,017 | `d3891a54fb0d33c668fa2f57726c67051a69acf8c5e268ad6644b5d9a9a18594` |
| `/tmp/otgd-image-proof/restore_config.py` | 4,298 | `d1af2e4a5ad0a58341e59c29289578bd2236c5c85a322067c9ac970500dca45e` |
| `/tmp/otgd-image-proof/rootfs.tar` | 267,728,896 | `3c6bea67100d93f33a83a3c1e1d7d711d317b1a76760c84873800cf7d07b1061` |
| `/tmp/otgd-image-proof/run.py` | 731 | `86bb1b661e4d66e10792fca640385f92c1ffdcfc8066c902660271d0ab67a390` |
| `/tmp/otgd-image-proof/services-before.json` | 1,914 | `6b62ed7f10b37622ed21905bd5a5ec308fd7291185eea2f56cc5ef5d37d33189` |
| `/tmp/otgd-image-proof/source-filesystem.json` | 6,289,838 | `2efd948397f34704aec0207c607591c259fe9d1beb492ec6c928ed8b7fa7929b` |
| `/tmp/otgd-image-proof/source-filesystem.json.v1-excluded-root` | 5,828,241 | `4e2cff7f7fa7b18341fe61337df4532d6559d010a889ccda0f2d2438296c0e54` |
| `/tmp/otgd-image-proof/source-image.tar` | 377,260,032 | `bee9be9e32befc11564069f836b71e0539b1c122f037485f06d8233c7631754c` |
| `/tmp/otgd-image-proof/source-inspect.json` | 2,941 | `4816c60f4858ee65b87c58214bbb9719460411201013b07df96e0ecb6bfe0a9a` |
| `/tmp/otgd-image-proof/source-save.log` | 198 | `ad5ccae51f00e86c562c1e7d7f5aeed841a7d4735ca0c4718765b47490c012b2` |
| `/tmp/otgd-image-proof/state-after.json` | 2,365 | `937bef7e2a1425cdd7544714e18b76c32faf44da9b753aad2e8e962e6c2c1382` |
