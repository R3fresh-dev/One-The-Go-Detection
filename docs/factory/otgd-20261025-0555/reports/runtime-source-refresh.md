# Local source image refresh — otgd-20261025-0555

**ROUND C ARCHIVE READY, current copied-source equality verified; Docker load/adoption not executed by this worker.** Source-only local refresh was prepared, then PM reviewed and authorized immutable snapshot/rootfs/archive generation under /tmp. RoundC contains219 frozen COPY entries and passes source/base/config/platform/hash verification. At 2026-10-25T06:58:23.668891+00:00, all219 included source entries matched the current workspace with zero differences, including final scripts/ci_gate.py. Runtime quality gates remain separate and unexecuted by this packaging proof.

Role: /root/firmware_validation, assigned OpenAI gpt-6.1-sol/high. D-006 v3 acknowledged via actual PM message. PM separately authorized /tmp snapshot/build/package, while holding Docker load/retag/restart/deletion. Current assignment performed no Docker mutations, source/gate edits, cleanup, image deletion, service changes, Git operations, deployment or new spend. Sole PM ownership and correction_round=0/recovery_attempts=0 preserved. Earlier firmware/image-proof reports and their artifacts were not modified.

## Deliverables and identities

| Artifact | Identity/hash | Bytes |
|---|---|---:|
| Current canonical base image | sha256:1af98b2872a49d3be4f8e6468507e9bc56468b1554252dcdf19293c21850d57b | Docker255,895,545 |
| Retained normalized base tar | SHA2569eb7ae54a33c8a183824112d1ab367bf9a2709e051536e20fe7ed01d2ef7c7e3 | 268,462,080 |
| RoundC content-frozen plan | SHA2560b44a7466abfafd016acdc6e76e1cf038d0122bdf9a5577350b7296fc61763f2 | 81,601 |
| Refreshed rootfs-c.tar | SHA25656cb9aba0d4a517c9b03bc7df02a4af37a86ce0efd36fd18ca7ba80178aa5b44 | 268,769,280 |
| source-refresh-image-c.tar | SHA256c873125292bbf247ebb0467f5c4db1af750a0dfdc9e7a66eb1f232528b1b25fe | 268,779,520 |
| Planned image config ID, not yet loaded | sha256:561bf306fb4ac684b3783a532b7129287c362987ed8083212912c1bd0e1f5a83 | — |
| Planned candidate-only tag | otgd-api:factory-source-0b44a7466abf | — |

Files are under /tmp/otgd-image-proof/source-refresh. The archive preserves complete serialized runtime Config including ArgsEscaped=true and linux/amd64, while binding its sole layer to the new rootfs tar SHA256. OCI config/manifest/index and Docker manifest descriptor references, blob digests and sizes were regenerated and independently checked. New top-level history/comment/created metadata disclose reconstructed LOCAL source refresh and bind the frozen plan; original/cloud image identity is not claimed.

RoundA was successfully built but became stale when browser_fixture.py changed afterwards; its source snapshot/rootfs/archive and receipts remain preserved. RoundB captured the final browser fixture but preceded the final ci_gate.py edit; PM loaded B while canonical remained unchanged. PM reconciled an initial comparison of raw serialized Config against Docker-inspect defaults: serialized-to-serialized and inspected-to-inspected both match exactly. Worker read-only B reconciliation is recorded in pm-loaded-b-readback.json. RoundC was captured after the final gate integrator release; nothing was omitted. All earlier archives are retained. Current-source comparison is below.

## Why source-only refresh is justified here

The Dockerfile, Dockerfile-specific ignore, pyproject.toml and uv.lock exactly match base-image bytes. No dependency installation or Dockerfile/environment change is inferred or substituted. The installed editable distribution has `_editable_impl_otgd_api.pth` containing `/app/services/api` and direct_url.json with file:///app/services/api, editable=true. Updating source at that exact destination preserves the installed project target and package metadata. All installed dependencies, /opt/venv, /tmp, identities/security-related base paths and metadata outside COPY roots remain unchanged.

The eight exact COPY roots are services/api; contracts; tools; examples; openspec/changes/production-mobile-platform/fixtures; infra/local; infra/certs; scripts. Only those trees are replaced, removing obsolete copied-source entries if necessary. Dockerfile chown10001:10001 and ordinary chmoda+rX semantics are applied: preserve ordinary source mode/write bits, add world readability, add all execute bits for directories or an already-executable file. Source with special permission bits, symlinks, hardlinks, special files or extended attributes is rejected instead of guessing COPY/chown behavior. Base /app has no cross-boundary links.

The context classifier implements only the exact pinned Dockerfile-specific ignore, including .env variants, .venv, node_modules, caches, secrets, reports, cdk.out, verification and *.local.json exclusions at the declared depths. Any build/dependency/ignore hash change fails closed. The Dockerfile-specific ignore takes precedence over the root file, as specified in [Docker build-context documentation](https://docs.docker.com/build/concepts/context/#filename-and-location). Current snapshot contains219 entries; excluded runtime/cache/secret trees were not copied. Snapshots preserve ordinary source modes and nanosecond mtimes. Content hashes, path inventory and metadata bind the snapshot; build rereads it before and after generation. This is a content-frozen artifact, not a claim that host files were made filesystem-immutable.

Refresh verification compared every outside-COPY base entry (payload/hash/length, uid/gid/mode, timestamps, link target/type and extended PAX metadata) against the refreshed archive, and checked every included source entry against its frozen manifest with no missing or extra paths. All original hardlink representations outside COPY roots remain untouched. The separately executed verification repeated these filesystem checks, confirmed full serialized Config/platform equality, and hashed the actual archived layer against the declared sole DiffID.

| Pinned input | SHA256, current=base |
|---|---|
| `infra/local/service.Dockerfile` | `8a1871751a645dfaaf4a8ef5725d2bd95c053035dbb2b1d13bcc601c06faf1ff` |
| `infra/local/service.Dockerfile.dockerignore` | `33c3e74de6de3ed53fcd42a6447864c24a97078f1baf0df95063eeb8f3b4f1ba` |
| `services/api/pyproject.toml` | `eb63eecbf3259ea1cb2440a0ee15b61eecc61887e4a154ff50dd2d595b6961a8` |
| `services/api/uv.lock` | `6cb09a75e943c6102a84ea62dd1a30220c897b62f8a52cc6548a6fdb72f22f1c` |

## Executed scope and current-source distinction

RoundC snapshot/rootfs/archive commands ran 2026-10-25T06:58:06.388041+00:00 through2026-10-25T06:58:11.334260+00:00; all exit0. Independent verification ran06:58:21.932660–06:58:23.690571 UTC, exit0. At that check:

```json
{
  "added": [],
  "removed": [],
  "changed": []
}
```

All copied inputs, including runtime/service source, helpers and final scripts/ci_gate.py, match this snapshot at verification. This supersedes the provisional roundB source mismatch; no mismatch was waived. Source-specific final gates remain required. Recompare COPY inputs immediately before adoption if any writer resumes.

| Key frozen source | SHA256 |
|---|---|
| `services/api/otgd/local_identity.py` | `118723bf3242154fef3d7faae9d624d5d5f1d02b458844952167ae4a07330a3d` |
| `services/api/otgd/local_oauth_state.py` | `e7456407ee43ddf4578161a7eeee2fe0bbe796fbd51a742524f283a1e20678ad` |
| `infra/local/participant_probe.py` | `8243f9c8da985fe7c3f4dd79a83a42d89199f64e4895f81f2b46e632d9fdd5cb` |
| `infra/local/browser_fixture.py` | `01e70e58cec7913d7bf3b442e39158b80514c7c645cad8095f06e3b528695da7` |
| `infra/local/worker_interrupt_probe.py` | `17f19c89fb376416aec5379cf7181822082171863e5f202cba7b90cd972d98cc` |
| `infra/local/worker_interrupt_gate.py` | `fd0ec8fccbe344df436775bdcaf484534eb236025c2c0e63e6ffdc7e730223b1` |
| `scripts/ci_gate.py` | `96b1daa84983ed76d99dc4a45dfa1bc387e3703778ed2828d5eb66c307e0ec1a` |

RoundC changes relative to the baseline copied-source payload/modes:

```json
[
  {
    "change": "add copied source",
    "path": "app/infra/local/browser_fixture.py"
  },
  {
    "change": "payload/mode/owner",
    "new_sha256": "8243f9c8da985fe7c3f4dd79a83a42d89199f64e4895f81f2b46e632d9fdd5cb",
    "old_sha256": "ddba6d97d6c979bdea69138152e43f310f4be51c4620e86ea0f1f13a3251b112",
    "path": "app/infra/local/participant_probe.py"
  },
  {
    "change": "add copied source",
    "path": "app/infra/local/worker_interrupt_gate.py"
  },
  {
    "change": "add copied source",
    "path": "app/infra/local/worker_interrupt_probe.py"
  },
  {
    "change": "payload/mode/owner",
    "new_sha256": "96b1daa84983ed76d99dc4a45dfa1bc387e3703778ed2828d5eb66c307e0ec1a",
    "old_sha256": "c897f5b4bcf149a2aad78cf18aa996400451690554229e27b885665db4b5847d",
    "path": "app/scripts/ci_gate.py"
  },
  {
    "change": "payload/mode/owner",
    "new_sha256": "118723bf3242154fef3d7faae9d624d5d5f1d02b458844952167ae4a07330a3d",
    "old_sha256": "c59c7e438ee855232d4bf96ce04ea7485a0967a6dbf006d8f900a109f240e49f",
    "path": "app/services/api/otgd/local_identity.py"
  },
  {
    "change": "payload/mode/owner",
    "new_sha256": "e7456407ee43ddf4578161a7eeee2fe0bbe796fbd51a742524f283a1e20678ad",
    "old_sha256": "14a8495e6658ed8f89e7a55c3250759d95c252c244ffb7fdcadb1d5611933d65",
    "path": "app/services/api/otgd/local_oauth_state.py"
  },
  {
    "change": "add copied source",
    "path": "app/services/api/tests/test_browser_fixture_staff.py"
  },
  {
    "change": "payload/mode/owner",
    "new_sha256": "991733f845ff60d0ca13e145482497b6273425b1f293361a6d73eb874d29993f",
    "old_sha256": "51b0675eb98628b6b6f6ab912dae1db10f8c1d30ebff60a7eec78acea58424c2",
    "path": "app/services/api/tests/test_local_identity.py"
  },
  {
    "change": "payload/mode/owner",
    "new_sha256": "60013323430a0979caeffcef4b2983566a028b0f50e75938df7f053c0498fdc0",
    "old_sha256": "753cb94b151befc5742260804631c5e7517813c332d9c435564b25e1537a3aa7",
    "path": "app/services/api/tests/test_model_evaluation.py"
  },
  {
    "change": "payload/mode/owner",
    "new_sha256": "6ba27142296226c46ec947b7fe5e2a47168faac3baed130da00c364cc85d4ea8",
    "old_sha256": "23efe98238052ce2b19fbbc6aa50647a384196023d912c0f05fb436b491eca65",
    "path": "app/services/api/tests/test_model_evaluation_cardiac.py"
  },
  {
    "change": "payload/mode/owner",
    "new_sha256": "4d512a3ad9f7c65b69ee09d94fb471799d1aff63a5bc4c34140526dcac280ae7",
    "old_sha256": "54e64aca9b9379504922ef67bca4df1f45c518d42746530fec18b97aa58466bf",
    "path": "app/services/api/tests/test_operator_governance.py"
  }
]
```

## Resources, safety bounds and next step

Initial read-only state showed five canonical long-running containers healthy and resource-init/migrate exited0. Original image archives and existing data/runtime are preserved. Other PM-owned live probes may run concurrently; this assignment did not alter them. The canonical base image was reread after packaging and still equals1af98b28..., and the proposed source tag remained absent.

At final verification, root free1,674,702,848B; /tmp free1,118,912,512B. Each generation checked headroom before writing. Three source-refresh pairs are retained; no further pair is planned under current resource scope; no cleanup performed. Normal17-layer rebuild has not been shown safe: historical layer tar sum377,207,808B, cumulative uncompressed layer-size sum3,829,634,560B, exceeding measured free root before VFS/build/container overhead. This is a risk indicator, not an exact physical-space forecast. Recheck capacity before image loading and each service recreation.

**Action held:** load candidate archive, inspect exact runtime Config/platform/DiffID, adopt its tag and recreate only separately authorized application containers. **Target:** local Docker candidate/canonical images and app-only containers. **Reason/state:** pending separate PM review/assignment, as explicitly required by current task; not denied and no uncertain Docker execution. PostgreSQL/LocalStack volumes/settings/deletion journal must remain preserved. This worker ran no Docker load command. PM loaded roundB separately; C was absent at its verification timestamp and is handed to PM for a separately owned load/adoption step. Live browser/API/worker gates remain execution work outside this archive proof. No scientific, sensor, participant or cloud qualification is established.

The prepared reusable scripts are refresh.py (pin checks, plan, exact tar reconstruction), freeze.py (reviewed source capture) and package.py (exact Config/platform archive construction). They perform no Docker calls. Plans and receipts expose intended identities before loading. AST and pinned-context classifier checks ran; archive generation and independent archive checks were then executed after PM authorization. No guessed tool/dependency versions were installed.

## Actual commands and results

**reviewed-source-plan**: 2026-10-25T06:51:46.897175+00:00 to 2026-10-25T06:51:47.953161+00:00; exit0; 1.056s; log `/tmp/otgd-image-proof/source-refresh/reviewed-source-plan.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/source-refresh/refresh.py",
  "--plan",
  "/tmp/otgd-image-proof/source-refresh/reviewed-plan.json"
]
```

**immutable-source-snapshot**: 2026-10-25T06:51:47.978820+00:00 to 2026-10-25T06:51:48.070379+00:00; exit0; 0.092s; log `/tmp/otgd-image-proof/source-refresh/immutable-source-snapshot.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/source-refresh/freeze.py",
  "--plan",
  "/tmp/otgd-image-proof/source-refresh/reviewed-plan.json",
  "--output",
  "/tmp/otgd-image-proof/source-refresh/frozen-source",
  "--execute-reviewed"
]
```

**refreshed-rootfs-build**: 2026-10-25T06:51:48.097238+00:00 to 2026-10-25T06:51:51.010243+00:00; exit0; 2.913s; log `/tmp/otgd-image-proof/source-refresh/refreshed-rootfs-build.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/source-refresh/refresh.py",
  "--root",
  "/tmp/otgd-image-proof/source-refresh/frozen-source",
  "--plan",
  "/tmp/otgd-image-proof/source-refresh/frozen-source.plan.json",
  "--build",
  "/tmp/otgd-image-proof/source-refresh/refreshed-rootfs.tar",
  "--execute-reviewed"
]
```

**source-refresh-image-archive**: 2026-10-25T06:51:56.811621+00:00 to 2026-10-25T06:51:58.098122+00:00; exit0; 1.287s; log `/tmp/otgd-image-proof/source-refresh/source-refresh-image-archive.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/source-refresh/package.py",
  "--plan",
  "/tmp/otgd-image-proof/source-refresh/frozen-source.plan.json",
  "--rootfs",
  "/tmp/otgd-image-proof/source-refresh/refreshed-rootfs.tar",
  "--output",
  "/tmp/otgd-image-proof/source-refresh/source-refresh-image.tar",
  "--execute-reviewed"
]
```

**reviewed-source-plan-b**: 2026-10-25T06:53:50.908065+00:00 to 2026-10-25T06:53:51.769523+00:00; exit0; 0.861s; log `/tmp/otgd-image-proof/source-refresh/reviewed-source-plan-b.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/source-refresh/refresh.py",
  "--plan",
  "/tmp/otgd-image-proof/source-refresh/reviewed-plan-b.json"
]
```

**immutable-source-snapshot-b**: 2026-10-25T06:53:51.795290+00:00 to 2026-10-25T06:53:51.894455+00:00; exit0; 0.099s; log `/tmp/otgd-image-proof/source-refresh/immutable-source-snapshot-b.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/source-refresh/freeze.py",
  "--plan",
  "/tmp/otgd-image-proof/source-refresh/reviewed-plan-b.json",
  "--output",
  "/tmp/otgd-image-proof/source-refresh/frozen-source-b",
  "--execute-reviewed"
]
```

**refreshed-rootfs-build-b**: 2026-10-25T06:53:51.920101+00:00 to 2026-10-25T06:53:54.725906+00:00; exit0; 2.806s; log `/tmp/otgd-image-proof/source-refresh/refreshed-rootfs-build-b.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/source-refresh/refresh.py",
  "--root",
  "/tmp/otgd-image-proof/source-refresh/frozen-source-b",
  "--plan",
  "/tmp/otgd-image-proof/source-refresh/frozen-source-b.plan.json",
  "--build",
  "/tmp/otgd-image-proof/source-refresh/refreshed-rootfs-b.tar",
  "--execute-reviewed"
]
```

**source-refresh-image-archive-b**: 2026-10-25T06:53:54.751775+00:00 to 2026-10-25T06:53:55.679102+00:00; exit0; 0.927s; log `/tmp/otgd-image-proof/source-refresh/source-refresh-image-archive-b.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/source-refresh/package.py",
  "--plan",
  "/tmp/otgd-image-proof/source-refresh/frozen-source-b.plan.json",
  "--rootfs",
  "/tmp/otgd-image-proof/source-refresh/refreshed-rootfs-b.tar",
  "--output",
  "/tmp/otgd-image-proof/source-refresh/source-refresh-image-b.tar",
  "--execute-reviewed"
]
```

**independent-current-source-verification-b**: 2026-10-25T06:54:35.853386+00:00 to 2026-10-25T06:54:37.723391+00:00; exit0; 1.870s; log `/tmp/otgd-image-proof/source-refresh/independent-current-source-verification-b.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/source-refresh/verify_b.py"
]
```

**reviewed-source-plan-c**: 2026-10-25T06:58:06.388041+00:00 to 2026-10-25T06:58:07.322594+00:00; exit0; 0.935s; log `/tmp/otgd-image-proof/source-refresh/reviewed-source-plan-c.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/source-refresh/refresh.py",
  "--plan",
  "/tmp/otgd-image-proof/source-refresh/reviewed-plan-c.json"
]
```

**immutable-source-snapshot-c**: 2026-10-25T06:58:07.352372+00:00 to 2026-10-25T06:58:07.445132+00:00; exit0; 0.093s; log `/tmp/otgd-image-proof/source-refresh/immutable-source-snapshot-c.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/source-refresh/freeze.py",
  "--plan",
  "/tmp/otgd-image-proof/source-refresh/reviewed-plan-c.json",
  "--output",
  "/tmp/otgd-image-proof/source-refresh/frozen-source-c",
  "--execute-reviewed"
]
```

**refreshed-rootfs-build-c**: 2026-10-25T06:58:07.474299+00:00 to 2026-10-25T06:58:10.336757+00:00; exit0; 2.862s; log `/tmp/otgd-image-proof/source-refresh/refreshed-rootfs-build-c.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/source-refresh/refresh.py",
  "--root",
  "/tmp/otgd-image-proof/source-refresh/frozen-source-c",
  "--plan",
  "/tmp/otgd-image-proof/source-refresh/frozen-source-c.plan.json",
  "--build",
  "/tmp/otgd-image-proof/source-refresh/refreshed-rootfs-c.tar",
  "--execute-reviewed"
]
```

**source-refresh-image-archive-c**: 2026-10-25T06:58:10.364854+00:00 to 2026-10-25T06:58:11.334260+00:00; exit0; 0.969s; log `/tmp/otgd-image-proof/source-refresh/source-refresh-image-archive-c.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/source-refresh/package.py",
  "--plan",
  "/tmp/otgd-image-proof/source-refresh/frozen-source-c.plan.json",
  "--rootfs",
  "/tmp/otgd-image-proof/source-refresh/refreshed-rootfs-c.tar",
  "--output",
  "/tmp/otgd-image-proof/source-refresh/source-refresh-image-c.tar",
  "--execute-reviewed"
]
```

**independent-current-source-verification-c**: 2026-10-25T06:58:21.932660+00:00 to 2026-10-25T06:58:23.690571+00:00; exit0; 1.758s; log `/tmp/otgd-image-proof/source-refresh/independent-current-source-verification-c.log`.

```json
[
  "python3",
  "/tmp/otgd-image-proof/source-refresh/verify_c.py"
]
```

## Artifact receipts

| File | Bytes | SHA256 |
|---|---:|---|
| `/tmp/otgd-image-proof/source-refresh/action-plan.md` | 1,249 | `8e1db231ff692821906d6e03880af2f17136b58fbd27cb53787c0fe04c03b743` |
| `/tmp/otgd-image-proof/source-refresh/commands.jsonl` | 6,772 | `cfae6a9b81330377165d1bd75bafcee43bb649d75fb305decc8aff9302017ccb` |
| `/tmp/otgd-image-proof/source-refresh/current-plan.json` | 80,217 | `70b6c766025190db3308fbfca4a86f5157aa90b11bf90ce74cd45c58f73317cd` |
| `/tmp/otgd-image-proof/source-refresh/final-verification-b.json` | 2,142 | `d081fc5787fe79104b1aef2b8872908bd2fe734769ff18efa2f100b9ba0fecb7` |
| `/tmp/otgd-image-proof/source-refresh/final-verification-c.json` | 2,105 | `0b8828ef1cb52c40c8c8d38fddb4d7debd87196bd127dfcccfddd69e5eca30c0` |
| `/tmp/otgd-image-proof/source-refresh/final-verification.json` | 1,286 | `df249db7b3a9830a424a66fb81700f6324d314ab4aee10e0873743dd8d387b34` |
| `/tmp/otgd-image-proof/source-refresh/freeze.py` | 2,826 | `d8bc40999e5e941ef97542e9cc447c883d15e1610f85d9bfa104c7b1582ea3cc` |
| `/tmp/otgd-image-proof/source-refresh/frozen-source-b.plan.json` | 81,334 | `0819cce4fc8b33f6225eb3ca72afb2a2d7a1250a4763f9e3dd2c2164ff517317` |
| `/tmp/otgd-image-proof/source-refresh/frozen-source-c.plan.json` | 81,601 | `0b44a7466abfafd016acdc6e76e1cf038d0122bdf9a5577350b7296fc61763f2` |
| `/tmp/otgd-image-proof/source-refresh/frozen-source.plan.json` | 81,332 | `95267a1dc9cc65ab142f32ce9a899007089728dccb5f79d94d0086fe84c07d3e` |
| `/tmp/otgd-image-proof/source-refresh/immutable-source-snapshot-b.log` | 573 | `10c749261e3c6a07dfa500461ae50f123502a15311d510f096200bb49880b13d` |
| `/tmp/otgd-image-proof/source-refresh/immutable-source-snapshot-c.log` | 573 | `1da689300d3a7c2b74e39e9583cf5f90c929dd17429a2fd81dde7f30f7fc4119` |
| `/tmp/otgd-image-proof/source-refresh/immutable-source-snapshot.log` | 565 | `2209e8706f589de0bd3868b176e7824d9f64bdefdb14f2b533d5436423f88ce5` |
| `/tmp/otgd-image-proof/source-refresh/independent-current-source-verification-b.log` | 2,253 | `c6b4bbe9360aed5c9a37780d9df7d107a4cc9e278de6389281e3619854099717` |
| `/tmp/otgd-image-proof/source-refresh/independent-current-source-verification-c.log` | 2,216 | `933f3289604b00816d26aaf51906333eba6864396ec441039ad39402ffda76ac` |
| `/tmp/otgd-image-proof/source-refresh/package.py` | 4,825 | `a8c20f609717dd7a70e2015a873e82453c4fa60aab635f8cff60409a82ac740e` |
| `/tmp/otgd-image-proof/source-refresh/pm-loaded-b-readback.json` | 463 | `aefb954f6a76d6650d0b9e68503260b740f6e1108ffd7ba8fa2ce42068089f30` |
| `/tmp/otgd-image-proof/source-refresh/proposed-plan.json` | 80,217 | `9bf78df1a96bbb07800d37e2c8fe445deda15c16969cf2cdaf8f5d58f8414935` |
| `/tmp/otgd-image-proof/source-refresh/read-only-state.json` | 5,623 | `d7ce57b2ada039bdb9d52fddb067e1e31dd588a2f18b1188138c28f43f6c2258` |
| `/tmp/otgd-image-proof/source-refresh/refresh.py` | 9,038 | `ad15aa0167f8dfe3461565a4f2af8a3a7a0d9b36cd7669ed506051aebc608ac4` |
| `/tmp/otgd-image-proof/source-refresh/refreshed-rootfs-b.receipt.json` | 712 | `599a5170210851693eeffb772360ec2ae793bcebc0747148eed447c54defdb75` |
| `/tmp/otgd-image-proof/source-refresh/refreshed-rootfs-b.tar` | 268,769,280 | `72be38a19106e195b9c54f0bea6089eac09cd02ee362bbd959414ce3d1dd1e2f` |
| `/tmp/otgd-image-proof/source-refresh/refreshed-rootfs-build-b.log` | 1,060 | `2bdeb9269a93c92bc91d4977c9dd1c2fc142bf3c6936db27ff1fb8a2241c29e4` |
| `/tmp/otgd-image-proof/source-refresh/refreshed-rootfs-build-c.log` | 1,060 | `76ec55984aa58f261bb733973149f177707cee0c789107c21f7f81af20885a4b` |
| `/tmp/otgd-image-proof/source-refresh/refreshed-rootfs-build.log` | 1,052 | `ff2ce4539d858943993edc669c5fa526d7b836da691e2863048da3cbc14a4f04` |
| `/tmp/otgd-image-proof/source-refresh/refreshed-rootfs-c.receipt.json` | 712 | `59c79932d9ecd1a7c6992c6beb0c606df3309acc0421473642ffb6c52dbadffe` |
| `/tmp/otgd-image-proof/source-refresh/refreshed-rootfs-c.tar` | 268,769,280 | `56cb9aba0d4a517c9b03bc7df02a4af37a86ce0efd36fd18ca7ba80178aa5b44` |
| `/tmp/otgd-image-proof/source-refresh/refreshed-rootfs.receipt.json` | 710 | `a9b307136ff81516ae98f6e3010713a00291278fbc66231608ca984d5d96d8a3` |
| `/tmp/otgd-image-proof/source-refresh/refreshed-rootfs.tar` | 268,769,280 | `e7606ae49f6362765e366ac040c740edc1d603892f55eece44cad58afcb57b8a` |
| `/tmp/otgd-image-proof/source-refresh/reviewed-plan-b.json` | 81,457 | `2f2572262f9a3cf0b83a002eebcc6efe36fd66a8a225808912a7701981acf976` |
| `/tmp/otgd-image-proof/source-refresh/reviewed-plan-c.json` | 81,724 | `137895f2ae7c7c5bbaf99d377a0407594092dee7a1909654cde438d6ce0fbbb5` |
| `/tmp/otgd-image-proof/source-refresh/reviewed-plan.json` | 81,457 | `274c75b8e26ed73e36761b95fb1a1698dd6282a98be38a6cd16d45f7bd2bd68d` |
| `/tmp/otgd-image-proof/source-refresh/reviewed-source-plan-b.log` | 2,780 | `1b5360d348dfb6b65cdd2cf63d842f69b10dd14ca2333eb1c448e762e7df88c0` |
| `/tmp/otgd-image-proof/source-refresh/reviewed-source-plan-c.log` | 3,046 | `a8ca834ff7bfd4a67919555856bd3c827be8862c9a750f3f25dcca8b4a24f9de` |
| `/tmp/otgd-image-proof/source-refresh/reviewed-source-plan.log` | 2,776 | `17e0b20429c28533f9e06e2a49ede816a2ba1a30d29b9ff22398a39c8ded46b4` |
| `/tmp/otgd-image-proof/source-refresh/run.py` | 746 | `ab8a6aa1ee69de9b36d74829e3da0e3c22bd1dc10593a6a572e8afaf2b749b87` |
| `/tmp/otgd-image-proof/source-refresh/runtime-source-refresh-round-b.md` | 20,978 | `a320e8ab5c4329feb263eba4432768ef0ad26761926f7b41b79f53f35edc9926` |
| `/tmp/otgd-image-proof/source-refresh/source-refresh-image-archive-b.log` | 1,069 | `99f761e91e081019b9a2b82e45aca58c446383fc9ec4b3ffae56ea44fdabdf31` |
| `/tmp/otgd-image-proof/source-refresh/source-refresh-image-archive-c.log` | 1,069 | `d0a617c43e3e2ee05d941e86b8d322b79e83582fa4c12afa47a2cda8fef17390` |
| `/tmp/otgd-image-proof/source-refresh/source-refresh-image-archive.log` | 1,061 | `f592d51c262f34709e431c33c42f805308aa0843744251c4514d6f2419f49d62` |
| `/tmp/otgd-image-proof/source-refresh/source-refresh-image-b.receipt.json` | 707 | `80f3792b366a0a88aef6ddd5549c0c299a4415dab5434e058dbdef9b3ee5e60c` |
| `/tmp/otgd-image-proof/source-refresh/source-refresh-image-b.tar` | 268,779,520 | `b91fd5bd8e3436b44f37522437ed16979c14ec4eadd06c187fe15c22ae0ca9cc` |
| `/tmp/otgd-image-proof/source-refresh/source-refresh-image-c.receipt.json` | 707 | `10192d32cf4254b5b77a7a7b6e512df5a1774fc4c96025c9c0ac7f541c6bc404` |
| `/tmp/otgd-image-proof/source-refresh/source-refresh-image-c.tar` | 268,779,520 | `c873125292bbf247ebb0467f5c4db1af750a0dfdc9e7a66eb1f232528b1b25fe` |
| `/tmp/otgd-image-proof/source-refresh/source-refresh-image.receipt.json` | 705 | `0b961d6947e1f9aa87659e45eec23e1a13205c3c56d858b1beffc2628db0e4a0` |
| `/tmp/otgd-image-proof/source-refresh/source-refresh-image.tar` | 268,779,520 | `f11e0802735fe214393bd429b0068ce498d716e27ee47fe5997b7b6c0b8050c4` |
| `/tmp/otgd-image-proof/source-refresh/verify_b.py` | 3,414 | `3972ff4d34777ef1c7796250fdb7ae440bc6099085ead8ee6b211505a465abac` |
| `/tmp/otgd-image-proof/source-refresh/verify_c.py` | 3,428 | `99977c9ec8a120819a1cee50d1c523ef0e30c694fd880b8a6580456930421b17` |

## D-006 v4 handoff

PM accepted and recorded D-006 v4 after independently checking roundC219 source payloads, serialized Config and platform. This worker acknowledged the decision via actual message. PM owns C image loading, canonical tagging and application-only recreation, preserving PostgreSQL/LocalStack/journal/live probe and all archives. Parent reported its load session31777 executing; completion/adoption is not asserted by this worker. No additional Docker actions performed. C archive/source proof above remains the completed scope; runtime execution evidence belongs to PM records.
