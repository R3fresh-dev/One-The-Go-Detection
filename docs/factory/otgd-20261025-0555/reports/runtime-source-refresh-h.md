# Image H: current source proof; adoption blocked by capacity

Actual proof owner: OpenAI gpt-6.1-sol/high `/root/firmware_validation`, run `otgd-20261025-0555`. Current correction **2/2**, recovery **0/3**. D010v1/v2 acknowledged by actual PM message. Explicit backend COPY release is at `/workspace/scratch/otgd-20261025-0555-live/correction-round2-export/final-handoff.json`,2026-10-25T10:15:30.130467+00:00; author confirms no active owned pytest/wrapper and only two changed COPY files. PM explicitly authorized harmless memory/tmp preparation separately from guarded Docker adoption. This is packaging evidence, not independent signoff, current full-gate acceptance or deployment authorization.

**Prepared and independently verified ONE gzip archive on `/tmp`; Docker adoption remains BLOCKED_CAPACITY.** No Docker mutation, load/tag/recreation/removal/prune, cache deletion, archive migration, source/gate edit, new install, Git operation or private Docker path retry occurred. All A–G archives and raw evidence remain preserved. Current G services/data/volumes/settings/journal untouched. No second full tar written to disk.

| Identity | Exact value |
|---|---|
| Retained archive | `/tmp/otgd-image-proof/source-refresh-h/source-refresh-image-h.tar.gz` |
| Compressed bytes | 97,917,282, below120MiB=125,829,120 |
| Compressed archive SHA-256 | `e33a167902ff8157d4e726fbdf5c4dc3ce0cec962515acc12e7d1ecdbabbf011` |
| Decompressed Docker archive bytes | 268,912,640, streamed only |
| Decompressed Docker archive SHA-256 | `4827f55f27677c7e97530196cf7903160c01c8c2bc01e8cb2102bf188e1b9afc` |
| In-memory rootfs bytes | 268,902,400 |
| Sole layer DiffID | `sha256:6e7d41b251c62f220bfabf15761da2f43b12433396747e06078f12c6c7a929d3` |
| Expected config/image ID | `sha256:f6c164a1739b3470c54af0ecf8d3db548fe9b7ccc3fba9dc328949e557f240c0` |
| Candidate-only tag | `otgd-api:factory-source-520a3853480b` |
| Final frozen plan SHA-256 | `520a3853480bec9190ca2a9d038a85cee93c386096d61d20513a749c612e3c43` |
| Origin plan created | 2026-10-25T10:16:38.690972+00:00 |
| Package proof completed | 2026-10-25T10:16:56.225635+00:00 |
| Separate readback | 2026-10-25T10:17:18.274152+00:00, PASS |

Compressed archive SHA, decompressed complete archive SHA, layer DiffID and image ID bind distinct byte sequences. Gzip integrity/trailer, complete decompressed length/hash, every blob digest and Docker/OCI descriptor were checked. Gzip settings:mtime0,emptyfilename,compressionlevel6,zlib1.3.2;hostPython`3.12.14 (main, Aug 25 2026, 14:00:49) [Clang 22.1.3 ]`. CappedWriter refuses any write over120MiB; no cap failure. A single BytesIO rootfs is written directly into gzip, closed before archive readback; no full disk rootfs tar.

## Exact replay and script change

Adapted H script SHA **`4730cfd8f08a0db9f1b1d64a7746804a76a7b4d361b8be234e35318b2f7d91d6`** first reproduced frozen D at 2026-10-25T10:16:24.987767+00:00–2026-10-25T10:16:27.718287+00:00: exact D DiffID **`sha256:a5b5cf95fc230c53c75d4afaba7a390441488cd9d5352cccda0793c5ef733965`**,268,769,280bytes and all17,096 manifest entries equal retained `refreshed-rootfs-d.tar`. This verifies unchanged member ordering, bytes and metadata against the established disk reconstruction. The replay receipt is bound to the unchanged new script before H packaging.

Reviewed diff `745aecc6587f113abe9a000c718245a1dd3e936a6b535333f531e4743137c60b` is retained in `memory-refresh-from-g.diff`. It changes only H names/output prefix, places the archive on `/tmp`, separates preparation and adoption budgets, and records adoption readiness before/after proof. Tar reconstruction, classifiers/pins, editable dependency verification, Config/platform and digest/manifest checks are unchanged. PM explicitly confirmed this distinction before execution: preparation is authorized with sufficient memory/tmp space even when a later Docker action fails its unchanged root-capacity guard. It grants no Docker permission and does not reduce300MiB load/recreation reserve.

## Whole current COPY and filesystem fidelity

All **224 COPY entries** match released workspace bytes/modes/precise mtimes/sizes/mapped owner and source types before/after freezing, before/after package, twice by independent verifier, and in final report readback. Origin exclusion inventory retained. Exactly two entries differ from G; no paths added/removed and no other copied metadata changes:

- `services/api/otgd/report_revisions.py`: `02e6d0331075209a33261ec6f75499dae778e78d590c9451d4e6584dc0f590f4`
- `services/api/tests/test_current_result_readback.py`: `8df4b2d22a0eb0b0167ec244dc5c46d93e28608682038074f3a6da4112177023`

The retained G archive independently rehashed to **`e7d1d9b7efe2225910c7abb07b4062586bb669f27dffdbd1a5d0c5dea01d26c5`**. G remains valid historical evidence, not current backend source. Backend author reports1538unit+208subtests passed,89.92566681241802%coverage,20PGdeselected; this worker read the signed-by-author handoff and matching source hashes but did not rerun/certify that unit suite or full gates.

H has **17,101 full entries**, **16,877 outside COPY**, **3,569 hardlinks and896symlinks** preserved. Separate verifier compares every outside-COPY header field:type,mode,uid,gid,uname,gname,mtime,size,linkname,devmajor/devminor,allPAXheaders plus regular payload SHA against retained normalized source. All equal. Copied source type/mapped owner/mode/mtime/size/hash and absence of unexpected link/metadata match every frozen entry; no obsolete path survives. No extended PAX/xattr/ACL/capability entries exist in either archived base or H; no meaningful metadata mismatch was waived. Full manifest retained in rootfs-manifest-h.json; every COPY entry is listed below.

Eight exact COPY roots:services/api,contracts,tools,examples,openspec/changes/production-mobile-platform/fixtures,infra/local,infra/certs,scripts. Pinned Dockerfile-specific ignore classifier/build/pyproject/uvlock unchanged. Included sources are ordinary files/directories with no links/xattrs/specialbits; unsupported types fail closed. Dockerfile chown10001:10001/a+rX and exact source nanosecond-derived PAX mtime are preserved.

Normalized base SHA `9eb7ae54a33c8a183824112d1ab367bf9a2709e051536e20fe7ed01d2ef7c7e3` remains exact. Installed dependency tree outside COPY unchanged; editable .pth exactly`/app/services/api`,direct_url exactly editablefile:///app/services/api. No package install or dependency rebuild. Complete original serialized runtime Config equal, including ArgsEscaped=true and all Env/Cmd/User/WorkingDir/ExposedPorts/Volumes values and absent fields; linux/amd64 exact. Serialized compares with serialized, avoiding Docker inspect's added null defaults. Only rootfs/history/created/comment packaging identity changes. Config blob SHA equals expected image ID, sole layer SHA equals DiffID; all OCI/Docker index/manifest/config/layer references,size,hash checked by builder and separate verifier.

Original raw-export discrepancy remains unresolved and preserved: generated init/mount extras, omitted root header, hostname/resolv stubs and different backupetc/group-. D006v2 approved exact DECLARED saved-layer reconstruction, including original root/directory/hostname/resolv/group- restoration. H retains that basis; it does not claim original raw/live filesystem equivalence, original image digest, ECR/cloud admission or original-cloud provenance. Actual current CI image builds/native OS/hardware/study/release requirements remain separate.

## Preparation resources versus unchanged adoption guards

Memory start limit17,179,869,184bytes,current16,105,697,280,available1,074,171,904. Start guard requires estimated full buffer+512MiB and passed; after buffer available709,492,736, final available2,113,187,840. Shared memory/root activity temporarily changed resources; no exclusive-ownership claim. One buffer allocator slack/manifest structures fit actual observed headroom.

Preparation `/tmp` available before archive **455,843,840bytes**; requirement **176,160,768** =125,829,120cap+16,777,216proofmetadata+33,554,432safetyheadroom. Passed. Frozen snapshot already existed at that measurement; proof allowance covers remaining manifest/receipt/log output. Archive/proof completed with/tmpavailable358,105,088; separate verifier measurement is in independent-readback-h.json. No retained file migrated between filesystems.

Archive resides on/tmp, so it is charged once to that filesystem, not again to root. Unchanged ROOT budgets:

| Root stage | Bytes |
|---|---:|
| StageA full decompressed load transient | 268,912,640 |
| StageA new VFS layer estimate | 293,220,352 |
| Stage A 300 MiB reserve | 314,572,800 |
| **StageA required** | **876,705,792** |
| StageB new layer + ONE serial app allocation +300MiB reserve | **901,013,504** |
| **Required max, not sum** | **901,013,504** |
| Root at separate proof | **891,973,632** |
| **StageB deficit at proof** | **9,039,872** |

At the before-archive boundary, root had875,212,800bytes and both stages were insufficient; harmless/tmp preparation remained allowed. At completed proof root rebounded to891,973,632:StageA fits by15,267,840; StageB **still fails by9,039,872**. These actual observations remain in receipts; no root action ran during either phase. Layer/container estimate rounds each unique regular inode to4KiB plus4KiB per directory, preserving hardlinks; it is a planning estimate, not measured Docker allocation. Guard reserve not reduced.

Later resource history is retained separately: after the first report write, root briefly measured821,370,880bytes (about70.6MB below proof); cause unverified and PM immediately alerted. At final source/artifact readback **2026-10-25T10:20:31.984579+00:00**, root rebounded to **888,315,904bytes**, with StageB still short **12,697,600bytes**. Status remains **BLOCKED_CAPACITY**; the temporary dip was never interpreted as a proof failure or an adoption success. The proposed9.3MB PM cache action is not guaranteed to fit this later12.7MB deficit. PM alone may classify/archive/remove exact reproducible cache files and then measure actual capacity; proof owner performed no cleanup.

PM must review proof/current source and remeasure actual root bytes before any load. After successful load returns, remeasure and require **607,793,152bytes**=one container293,220,352+reserve314,572,800 before EACH serial app recreation. Any retained load transient is already charged as used space; **no transient-absence assertion**. Prior `/var/lib/docker/tmp` list was OS PermissionError13; this worker did not retry/bypass it or read contents. No stage overlap, cleanup, service interruption or migration is authorized by this proof.

## Exact cache candidates: audit only, no cleanup

The read-only root inventory found no sufficient unused Docker layer: dangling12ac shares its entire normalized layer with initializer-referenced1af,unique0B; Docker build cache14.78kB. All other images referenced. Project bytecode inventory excludes .venv,node_modules,symlinks,reports,archives,data and all retained build outputs. Every listed .pyc is regular,nlink1,with original .py source present and both hashes recorded. File-only capacity candidate list:

| Pure bytecode directory | Files | Allocated file bytes |
|---|---:|---:|
| `/workspace/One-The-Go-Detection/apps/mobile/modules/scripts/__pycache__` | 3 | 176,128 |
| `/workspace/One-The-Go-Detection/deploy/__pycache__` | 13 | 626,688 |
| `/workspace/One-The-Go-Detection/firmware/tools/__pycache__` | 1 | 16,384 |
| `/workspace/One-The-Go-Detection/infra/local/__pycache__` | 5 | 147,456 |
| `/workspace/One-The-Go-Detection/infra/test/__pycache__` | 66 | 2,732,032 |
| `/workspace/One-The-Go-Detection/scripts/__pycache__` | 8 | 86,016 |
| `/workspace/One-The-Go-Detection/services/api/otgd/__pycache__` | 43 | 1,056,768 |
| `/workspace/One-The-Go-Detection/services/api/tests/__pycache__` | 59 | 3,338,240 |
| `/workspace/One-The-Go-Detection/tools/__pycache__` | 4 | 122,880 |

All202candidate files total **8,302,592bytes**; even deleting all would leave **737,280bytes** of the proof's9,039,872byte deficit, before further growth. Directory blocks36,864 are excluded from file-only estimate. No blanket cleanup recommended. Small3.37MBpair alone is insufficient. Exact file list/SHA/originalsource bindings in all-root-bytecode-candidates.json are for PM review, not action permission. Backend author reports no active owned pytest; mobile/operator cache ownership still needs PM check. Bytecode is reproducible cache, not unique raw test evidence; no bytes have been deleted.

Current mobile dist is actively owned/served and excluded. Firmware/build40,374,272bytes is actual retained binary/ELF/map evidence explicitly hash-bound in firmware-validation.md and excluded despite reproducibility. infra/cdk.out and infra/dist absent. Raw reports, unit XML, archives and data remain preserved. If capacity cannot meet guards after a separately authorized minimal action, adoption stays blocked; no automatic worker removal or extra correction round.

## Executed evidence

All commands from/workspace/One-The-Go-Detection; systemPython3, no installs. Replay2026-10-25T10:16:24.987767+00:00–2026-10-25T10:16:27.718287+00:00;Hbuild/package2026-10-25T10:16:39.494252+00:00–2026-10-25T10:16:56.225635+00:00;separate verification2026-10-25T10:17:18.274152+00:00. Actual tool sessions exit0 for compile/replay, sourceplan/freeze/package and independent verifier. No denied or uncertain action in H preparation. Original private Docker OS13 denial remains historical and unretired.

```sh
python3 -m py_compile /tmp/otgd-image-proof/source-refresh-h/memory_refresh.py
python3 /tmp/otgd-image-proof/source-refresh-h/memory_refresh.py replay-d
python3 /tmp/otgd-image-proof/source-refresh/refresh.py --plan /tmp/otgd-image-proof/source-refresh-h/reviewed-plan-h.json
python3 /tmp/otgd-image-proof/source-refresh/freeze.py --plan /tmp/otgd-image-proof/source-refresh-h/reviewed-plan-h.json --output /tmp/otgd-image-proof/source-refresh-h/frozen-source-h --execute-reviewed
# Add origin_plan provenance; verify224entries and onlytwoexactreleasedGdifferences.
python3 /tmp/otgd-image-proof/source-refresh-h/memory_refresh.py package-h --root /tmp/otgd-image-proof/source-refresh-h/frozen-source-h --plan /tmp/otgd-image-proof/source-refresh-h/frozen-source-h.plan.json --workspace /workspace/One-The-Go-Detection --output /tmp/otgd-image-proof/source-refresh-h/source-refresh-image-h.tar.gz
python3 /tmp/otgd-image-proof/source-refresh-h/verify_h.py
```

Freeze helper's initial plan SHA appears in freeze-h.log; explicit origin_plan provenance was added before package without changing any entry. Final plan hash above binds image comment/identity. Scripts refuse overwrites/unsupported/oversized preparation; no second archive authorized.

## Pins

| Input | SHA-256 |
|---|---|
| `infra/local/service.Dockerfile` | `8a1871751a645dfaaf4a8ef5725d2bd95c053035dbb2b1d13bcc601c06faf1ff` |
| `infra/local/service.Dockerfile.dockerignore` | `33c3e74de6de3ed53fcd42a6447864c24a97078f1baf0df95063eeb8f3b4f1ba` |
| `services/api/pyproject.toml` | `eb63eecbf3259ea1cb2440a0ee15b61eecc61887e4a154ff50dd2d595b6961a8` |
| `services/api/uv.lock` | `6cb09a75e943c6102a84ea62dd1a30220c897b62f8a52cc6548a6fdb72f22f1c` |

## Retained proof hashes

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `/tmp/otgd-image-proof/source-refresh-h/action-plan.md` | 1216 | `7046e6e44732f44c402b2076d01c017ca7eb1f886e1ae743636bc7f9c6320b44` |
| `/tmp/otgd-image-proof/source-refresh-h/resource-plan.json` | 1819 | `5bbea3d6574a4dcc727932eba18d737ec3826181d33f18a1b311b594813e016f` |
| `/tmp/otgd-image-proof/source-refresh-h/root-cache-candidates.json` | 97766 | `567a2ea39633f6a192f5517955803e2e84c5f10f90bdebdb74c3094cb1f905fa` |
| `/tmp/otgd-image-proof/source-refresh-h/all-root-bytecode-candidates.json` | 99319 | `3d8b6a27d1115bae7b09a572b5c56a481242c03072451ecc937b8ce1a5373c4d` |
| `/tmp/otgd-image-proof/source-refresh-h/memory_refresh.py` | 13603 | `4730cfd8f08a0db9f1b1d64a7746804a76a7b4d361b8be234e35318b2f7d91d6` |
| `/tmp/otgd-image-proof/source-refresh-h/memory-refresh-from-g.diff` | 9587 | `745aecc6587f113abe9a000c718245a1dd3e936a6b535333f531e4743137c60b` |
| `/tmp/otgd-image-proof/source-refresh-h/d-memory-replay.json` | 1179 | `18978515720031b18b56c6c6e4e083b8aa9b1f5f900e96d32a38aef785c9d566` |
| `/tmp/otgd-image-proof/source-refresh-h/d-memory-replay.log` | 1179 | `18978515720031b18b56c6c6e4e083b8aa9b1f5f900e96d32a38aef785c9d566` |
| `/tmp/otgd-image-proof/source-refresh-h/reviewed-plan-h.json` | 88224 | `258f886816c6b3c9e4eb60f91898f3b1721391f22e40c361df6491f8bbc8db58` |
| `/tmp/otgd-image-proof/source-refresh-h/current-plan.log` | 7480 | `91954387250b5dd0ca1150a75e107e6565f2978cd12c76876d3089e234c9bcac` |
| `/tmp/otgd-image-proof/source-refresh-h/freeze-h.log` | 307 | `06dd78fcaa8ce2fe5a3a23213be598bebd931f0bbd5bc1b51536c3d355405311` |
| `/tmp/otgd-image-proof/source-refresh-h/frozen-source-h.plan.json` | 88151 | `520a3853480bec9190ca2a9d038a85cee93c386096d61d20513a749c612e3c43` |
| `/tmp/otgd-image-proof/source-refresh-h/package-h.log` | 4752 | `bb080ecd23329607f6ffb594163136bafb5d90a2151067485d3df2e5d1d4b401` |
| `/tmp/otgd-image-proof/source-refresh-h/image-h.receipt.json` | 4752 | `bb080ecd23329607f6ffb594163136bafb5d90a2151067485d3df2e5d1d4b401` |
| `/tmp/otgd-image-proof/source-refresh-h/rootfs-manifest-h.json` | 5050593 | `de8e7d4c2ecf57f02c0bd224642379e51a3301bdd3173eb5416006debf3c62a1` |
| `/tmp/otgd-image-proof/source-refresh-h/serialized-config-h.json` | 2108 | `e75ea1e59480cf8e4d9c57a4b366fb96d6e3aed075e376b09bc7cee92b8611c6` |
| `/tmp/otgd-image-proof/source-refresh-h/verify_h.py` | 6169 | `f75c21dab778d4a2d1699c2953a70c6741450618d480b013446ec728290a1bf7` |
| `/tmp/otgd-image-proof/source-refresh-h/independent-readback-h.json` | 2920 | `e9104780b22a4e4270840b8aead06fb1f91a614cda0d613739637c5ef2d9890a` |
| `/tmp/otgd-image-proof/source-refresh-h/independent-readback-h.log` | 2920 | `e9104780b22a4e4270840b8aead06fb1f91a614cda0d613739637c5ef2d9890a` |
| `/tmp/otgd-image-proof/source-refresh-h/final-readback-h.json` | 566 | `dac0edd666ca82fe0e8207fde34ef48e88d5c056e164081cc7dd61319af36909` |

## Every current COPY entry and mapped metadata

UID/GID10001:10001 for each row; mode octal aftera+rX; precise mtime decimal seconds; file SHA-256, directories no payload. Full origin exclusion inventory retained in plan.

| Image path | Kind | Mode | Bytes | mtime | SHA-256 |
|---|---|---|---:|---|---|
| `app/contracts` | dir | 0755 | 0 | 1792906887.769651651 | `—` |
| `app/contracts/README.md` | file | 0644 | 4609 | 1792906887.766295524 | `48222e16b81e6e15733b964144446a03ac0a86021523e9f090015776728b8343` |
| `app/contracts/application` | dir | 0755 | 0 | 1792906887.768223389 | `—` |
| `app/contracts/application/Alcohol.schema.json` | file | 0644 | 4544 | 1792906887.767039399 | `9b5850b9b6528df7f44b0530c4bfbb05b81a2127acc60cc9b0495e0248733474` |
| `app/contracts/application/Attestation.schema.json` | file | 0644 | 3654 | 1792906887.767039399 | `d1e11a401fa993d51601967f23a7d6849c834c26bd5a1a90f26d9fec041a0bbd` |
| `app/contracts/application/CaptureAttempt.schema.json` | file | 0644 | 3879 | 1792906887.767039399 | `1e8573d7b3d42cb7a5302021f0b44cc08a66a4b0e8a3a15923183bd24c2721a2` |
| `app/contracts/application/CaptureAuthorization.schema.json` | file | 0644 | 2057 | 1792906887.767039399 | `4c94ab363981bfb074b4d126852a7245d5f1fc643dc21c32fa49373c617d5e90` |
| `app/contracts/application/CaptureContext.schema.json` | file | 0644 | 5771 | 1792906887.767039399 | `ffc678dec16845c20a91da983c9551ca92fb989a3f89ff91701f85d1e1541d34` |
| `app/contracts/application/CollectionAbandonment.schema.json` | file | 0644 | 457 | 1792906887.767039399 | `82e7c2b9adfd8bd60c26b5ec7170ad40ce136c6a6f6374ce3a453a327b3ac2f1` |
| `app/contracts/application/CollectionReceipt.schema.json` | file | 0644 | 17974 | 1792906887.767039399 | `177ccd5c3b7bd6d2be271eec6bf0335cf3b9932be4eda44f85dd9a3912577b99` |
| `app/contracts/application/CollectionRequest.schema.json` | file | 0644 | 5790 | 1792906887.767039399 | `92cb4bede2a88175a4ab9b6ee8ed3b54dde66853e0d1e4a17e12326e7e50c726` |
| `app/contracts/application/ECGRecording.schema.json` | file | 0644 | 7414 | 1792906887.767039399 | `794e80c6762412092ced00acd1ddd34ba795f7a3348dc67888b6888c7c198590` |
| `app/contracts/application/EvidenceManifest.schema.json` | file | 0644 | 3336 | 1792906887.767039399 | `d066e582c2b24ea0a1629a5a690051381e19210894360961e0e176dbb0f357c8` |
| `app/contracts/application/ExportRequest.schema.json` | file | 0644 | 3186 | 1792906887.767039399 | `e058e8acf28221e8d905611f2b3a9524d44e87b4aa7bde807e9c012a8cd7866c` |
| `app/contracts/application/InstructionAcknowledgment.schema.json` | file | 0644 | 2862 | 1792906887.767039399 | `d6f2da1ada7db6dfa41016d1d8ffbb30e1ea2cc7de4febcd4232f10bca72a05d` |
| `app/contracts/application/LabSourceRequest.schema.json` | file | 0644 | 1703 | 1792906887.767039399 | `cbe7839e2c99b0a2e9e29784467dfba68febbeda668237cf2383559c8e4deb47` |
| `app/contracts/application/PPGEvidence.schema.json` | file | 0644 | 5670 | 1792906887.767039399 | `c9113ec14bf8a5847901ecbc2d7f1d485ac0f0aa6b2e615ceed4c53b091c433d` |
| `app/contracts/application/ProfileWrite.schema.json` | file | 0644 | 5009 | 1792906887.767039399 | `5cac4fdb8bdfbebfe8728879ba5b820cdd1cc4edbe5ccd64ec7c1201d121760d` |
| `app/contracts/application/README.md` | file | 0644 | 4377 | 1792906887.767039399 | `da4793b9b2a95c09540eaf030a2985903e102412794acfe174c4f725cf791a70` |
| `app/contracts/application/ReplacementLinks.schema.json` | file | 0644 | 2241 | 1792906887.767039399 | `0d4ac14eec5be61e5e6a68c7553124aae77494ea8ce03b13f7d7beb3740bbfbd` |
| `app/contracts/application/ReportDescriptor.schema.json` | file | 0644 | 17303 | 1792906887.767039399 | `82d5e34902882645e7ba5d55963adc044a3c832d7d4565c42bca9ec126239f21` |
| `app/contracts/application/ReportRevisionCompanion.schema.json` | file | 0644 | 23337 | 1792906887.767039399 | `439339d69c6a988000e57f19f005dcd02fc4208d5f535fdbf99d6fbca79002ea` |
| `app/contracts/application/ReportRevisionDetail.schema.json` | file | 0644 | 25095 | 1792906887.767039399 | `2e6a20e76d5b143ea139e9b1215f91e6552203627b813c17bc854a7cbc82f4ed` |
| `app/contracts/application/ReportRevisionIndex.schema.json` | file | 0644 | 2646 | 1792906887.767039399 | `b2f3034016eb5863bb3e1e02997034500e6d13b9d537122c8570ead0e8909863` |
| `app/contracts/application/ReportRevisionList.schema.json` | file | 0644 | 4872 | 1792906887.767039399 | `b8e92dc764d6a03ee860ed2b562532d1ac40da50fe2ebed51532f9b1f2b67d9f` |
| `app/contracts/application/ReportRevisionRequest.schema.json` | file | 0644 | 12323 | 1792906887.767039399 | `db1cc503469558a7891be14d40e098ba2b6caf32dbf6cf35d9f5eebd4c269b83` |
| `app/contracts/application/ReportRevisionResult.schema.json` | file | 0644 | 3101 | 1792906887.767039399 | `a0766a4c0462fe064ee2cb93968fce50f9cae0581c39b12cb09eacbce288c11a` |
| `app/contracts/application/ServerStartToken.schema.json` | file | 0644 | 8732 | 1792906887.767039399 | `0f14a43845a44744ab29e938d9cc5f7cd70d3c9a0540069e3b774eb55f32b5c2` |
| `app/contracts/application/StartAuthorization.schema.json` | file | 0644 | 852 | 1792906887.767039399 | `faa2d376f852c21e49b821e09f3e43b47aee9cb64085aea107da000e47bb640e` |
| `app/contracts/application/SyntheticDeviceCapture.schema.json` | file | 0644 | 17807 | 1792906887.767039399 | `8cc6b2bc9d0ceadedbadb40111919451560a251e193967aab0cb01e1c56e13ce` |
| `app/contracts/application/canonical-golden.json` | file | 0644 | 1498 | 1792906887.767039399 | `cfcf7a79db3fc20c737b364391aea73fe238379873cc24b5d5aed5539b7bc944` |
| `app/contracts/application/fixtures` | dir | 0755 | 0 | 1792906887.768223389 | `—` |
| `app/contracts/application/fixtures/synthetic-transport-ecg.json` | file | 0644 | 13609 | 1792906887.768223389 | `f3c577014f85bb67fd6de6d75a6222942e044c311490469b8e9b67ddb0d2a749` |
| `app/contracts/application/fixtures/synthetic-transport-ppg.json` | file | 0644 | 8434 | 1792906887.768223389 | `89ea865c840ffc7d805e4e127c5603d327a1e8f76b6f0883e1c9dc8393f89286` |
| `app/contracts/application/fixtures/synthetic-transport-saliva.json` | file | 0644 | 9782 | 1792906887.768223389 | `b4baaf1a3d4975b4d56fcbd9423475a4d8b523ba33744ba65ba40419c588c9ef` |
| `app/contracts/application/openapi.json` | file | 0644 | 287656 | 1792906887.768223389 | `d67cf5dd455cc80051c3092c54306614a6f485c5a1bf3c9a49bc5d22ff26671f` |
| `app/contracts/measurement.schema.json` | file | 0644 | 8121 | 1792906887.768223389 | `5793bcd9738d62c546608449d3806ed6fe0da4802233c575f45ba91d499a931f` |
| `app/contracts/model_manifest.schema.json` | file | 0644 | 11017 | 1792906887.768223389 | `a3dea558f563b9e79cd848fa17e4d6f41b1feb708ea1564d87710e6b5aa0a27e` |
| `app/contracts/openapi.yaml` | file | 0644 | 17885 | 1792906887.768223389 | `ed0c0b71f0921509c777e8c7acd117969625c5b746c6f88410ae20bae73847f9` |
| `app/contracts/operator` | dir | 0755 | 0 | 1792906887.768933064 | `—` |
| `app/contracts/operator/calibration.schema.json` | file | 0644 | 14645 | 1792906887.768933064 | `6355138d056f400431496cd9108f726e4bb8d66489b7673f21de2d1e9b2364f2` |
| `app/contracts/operator/configuration.schema.json` | file | 0644 | 62790 | 1792906887.768933064 | `e72cbe9a5783e76b2b5c86cb42d6d5c2bb4ca5f402bbfb408368c15e33b2f0c5` |
| `app/contracts/operator/device.schema.json` | file | 0644 | 2636 | 1792906887.768933064 | `a8018091e2b05df13332832a46609183a81f90fb2faba14765ad98641f683fc7` |
| `app/contracts/operator/method.schema.json` | file | 0644 | 2509 | 1792906887.768933064 | `38bf52c68ccb5d460ae00783a105e5ecc76514c111bc2cf8e0f2e03481e70232` |
| `app/contracts/operator/model.schema.json` | file | 0644 | 15287 | 1792906887.768933064 | `01dde37c9e331252026bc57cba4ca9a43510b00d03c644288337ab09ceebadec` |
| `app/contracts/operator/qualification.schema.json` | file | 0644 | 2884 | 1792906887.768933064 | `83b19c1e6c6e2eaf62881bab0c0888b6dcb1d22e46627d1a66bec72d4b063428` |
| `app/contracts/operator/raw_export.schema.json` | file | 0644 | 4292 | 1792906887.768933064 | `028a399579882361c69e51316be89017b78c08538a3bbad52d1ec54fb481e443` |
| `app/contracts/operator/retention.schema.json` | file | 0644 | 3418 | 1792906887.768933064 | `cf5757264305ee0c1c6ed51aa67b40dbb054e9b703d6653c4a55e7b553131280` |
| `app/contracts/operator/role.schema.json` | file | 0644 | 2021 | 1792906887.768933064 | `78183ee1bb315e4cb618ac72687d9d2561ad564787870c9e4639a4e2534f8da8` |
| `app/contracts/operator/study.schema.json` | file | 0644 | 3449 | 1792906887.768933064 | `571ca4c34a2f3b6d24c598b6dd8db630dd1cfc3fb28e1c33c03ff0a69a21b99e` |
| `app/contracts/research` | dir | 0755 | 0 | 1792906887.769651651 | `—` |
| `app/contracts/research/ResearchResult.schema.json` | file | 0644 | 37859 | 1792906887.769651651 | `4c4663f625bf2d72b87e7c9101eafd6f3c5a209ad51b7044dda7466e947d4964` |
| `app/contracts/result.schema.json` | file | 0644 | 5144 | 1792906887.769651651 | `0eddf1e7079db6dddcf36f662857608b85cd8968059cf1f0cefd11b4f8055fa8` |
| `app/contracts/session.schema.json` | file | 0644 | 28069 | 1792906887.769651651 | `bceca135190143791a6cfec5fef1412c6f1c6f491f197885018e74dc95991a14` |
| `app/contracts/telemetry.schema.json` | file | 0644 | 977 | 1792906887.769651651 | `d65f44641ea8605d533b5e50d74aa2843ba9429ab2ad55fdd33b95d11e1d5a50` |
| `app/examples` | dir | 0755 | 0 | 1792906887.775074 | `—` |
| `app/examples/README.md` | file | 0644 | 4433 | 1792906887.774955233 | `67f7297332c891c36f229c17d90b2f7de33ddbb8f685772b4943be1700558e09` |
| `app/examples/arduino` | dir | 0755 | 0 | 1791685770.982165458 | `—` |
| `app/examples/arduino/synthetic_serial` | dir | 0755 | 0 | 1792906887.775074 | `—` |
| `app/examples/arduino/synthetic_serial/synthetic_serial.ino` | file | 0644 | 1202 | 1792906887.775074 | `a601a4b7e8675f7acb6504972c24eab30751ee63d192f654d6544fd78b823697` |
| `app/examples/measurement_pg_converted.json` | file | 0644 | 851 | 1792906887.775074 | `2010e6f823cd6dfd00fb831d8e39707f08073601cce88612ede7e890f3363cd9` |
| `app/examples/synthetic_session.json` | file | 0644 | 5748 | 1792906887.775074 | `8b4fc99f2dbe04f8be7254b92abde5bbfe4bfcef38c29ba932fea1a57bd11b4e` |
| `app/examples/synthetic_telemetry.ndjson` | file | 0644 | 742 | 1792906887.775074 | `69c2db3a49fd68ffebd5b6d262a71e7bc22c6745054f7da97b4b1bfef199ec2e` |
| `app/examples/unvalidated_model_manifest.json` | file | 0644 | 1187 | 1792906887.775074 | `3e102c3a5bff074fc0e37203eb36cd80bfbfadec6e4ce1e5888a47c9bd5eb9d6` |
| `app/infra/certs` | dir | 0755 | 0 | 1792906887.780221008 | `—` |
| `app/infra/certs/global-bundle.pem` | file | 0644 | 169984 | 1792906887.780221008 | `fe45bbebf92ad3e27a583bbb2ddd1553c521ed4d49af5514dc0a40372ea5395c` |
| `app/infra/certs/manifest.json` | file | 0644 | 292 | 1792906887.780221008 | `b4098d3a01c163ee3cb92818a9c2b16f3cc31b341dd5fdec8862d9e4d68a9ea8` |
| `app/infra/local` | dir | 0755 | 0 | 1792910940.4482474 | `—` |
| `app/infra/local/app_flow.py` | file | 0644 | 13272 | 1792906887.784920763 | `3ab3d1440b0161e92f3850c7fafb15fe60a7cd2de8e7fc48827fa3c396c552d9` |
| `app/infra/local/bootstrap_resources.py` | file | 0644 | 5185 | 1792906887.784920763 | `fb2eb230c8b9cc6609e93c5373297ed5c2a8d33aef17d1babd3f21b65ce52751` |
| `app/infra/local/browser_fixture.py` | file | 0644 | 7860 | 1792911147.075918908 | `01e70e58cec7913d7bf3b442e39158b80514c7c645cad8095f06e3b528695da7` |
| `app/infra/local/compose.localstack-licensed.yml` | file | 0644 | 362 | 1792906887.784920763 | `54a825620e4da78ba6e839b8bc835337ab053ab1288f66112d2fb44c0867f859` |
| `app/infra/local/compose.yml` | file | 0644 | 6544 | 1792906887.784920763 | `bfee23800ef703fd187b6faf3e6fb1f331ee573d37a5f221d21d96f16a82b689` |
| `app/infra/local/participant_probe.py` | file | 0644 | 26713 | 1792910923.099876269 | `8243f9c8da985fe7c3f4dd79a83a42d89199f64e4895f81f2b46e632d9fdd5cb` |
| `app/infra/local/performance.py` | file | 0644 | 7594 | 1792906887.784920763 | `1a44d7d691d7528c7c87c36362d9ddd3bd1d817df349b7c5293981b11100e176` |
| `app/infra/local/raw_version_probe.py` | file | 0644 | 3760 | 1792906887.784920763 | `95caae0b6a579e6bebcc3d01f3e4218cdfb4275de068c1f293e59d6082121d78` |
| `app/infra/local/service.Dockerfile` | file | 0644 | 1698 | 1792906887.784920763 | `8a1871751a645dfaaf4a8ef5725d2bd95c053035dbb2b1d13bcc601c06faf1ff` |
| `app/infra/local/service.Dockerfile.dockerignore` | file | 0644 | 961 | 1792906887.784920763 | `33c3e74de6de3ed53fcd42a6447864c24a97078f1baf0df95063eeb8f3b4f1ba` |
| `app/infra/local/smoke.py` | file | 0644 | 3040 | 1792906887.784920763 | `0cb57219bb7fa7f4755c0eed7134ad5982819a618eb753604b3d1ac2d3dd8860` |
| `app/infra/local/worker_interrupt_gate.py` | file | 0644 | 9116 | 1792910940.664252005 | `fd0ec8fccbe344df436775bdcaf484534eb236025c2c0e63e6ffdc7e730223b1` |
| `app/infra/local/worker_interrupt_probe.py` | file | 0644 | 41778 | 1792911031.850201332 | `17f19c89fb376416aec5379cf7181822082171863e5f202cba7b90cd972d98cc` |
| `app/openspec/changes/production-mobile-platform/fixtures` | dir | 0755 | 0 | 1792906887.793309729 | `—` |
| `app/openspec/changes/production-mobile-platform/fixtures/README.md` | file | 0644 | 2633 | 1792906887.793309729 | `e40e8695adb63e889721779f3a3449d38fbbf2487425fc7c10238f808aa80c2d` |
| `app/openspec/changes/production-mobile-platform/fixtures/reaction-task-config-v1.json` | file | 0644 | 5450 | 1792906887.793309729 | `62bdf0bf1115c267269654d0f438ac14e6c5b1c97587c72e1d1d88ad4c7528ea` |
| `app/openspec/changes/production-mobile-platform/fixtures/reaction-task-golden-v1.json` | file | 0644 | 59057 | 1792915218.987471302 | `1e3ee2974e977aa5977bbe36a828851ff044e1f3335ac37e62b3f7ba4cb1270c` |
| `app/scripts` | dir | 0755 | 0 | 1792910556.439421662 | `—` |
| `app/scripts/check-canonical-health.py` | file | 0644 | 4052 | 1792906887.806618728 | `fa52100a8a4bebcdedf6131e6e3cd90aed7ae8c2cb1d5fa3c4e22224c592c478` |
| `app/scripts/ci_gate.py` | file | 0644 | 10772 | 1792911270.764649021 | `96b1daa84983ed76d99dc4a45dfa1bc387e3703778ed2828d5eb66c307e0ec1a` |
| `app/scripts/configure_merge_protection.py` | file | 0644 | 4531 | 1792906887.806618728 | `966bb6b67b04c97e377ce66135a28a5a94ec04f37ac7720f6c9d40665b874538` |
| `app/scripts/local-platform.py` | file | 0644 | 6094 | 1792906887.806618728 | `b099d77903869e6a0b3dc349250b26d151e4b83fee959a2873126ad407fc9644` |
| `app/scripts/publish-metrics.py` | file | 0755 | 3119 | 1792906887.806618728 | `9522cbdd85dc68344ffe1cf9d6ebaa06d9a20943f891d96f8c31c95c6ddd5055` |
| `app/scripts/reapprove-recovered-study.py` | file | 0644 | 1277 | 1792906887.806618728 | `474ec2f037689a911833413e2578f20712b9ee22b5dfcb2d354fe4a7e867281b` |
| `app/scripts/replay-job.py` | file | 0755 | 4454 | 1792906887.806618728 | `654cc88d70194de4e79941d27cb84d55aa4442e6599e3f606e17518b106c5e2b` |
| `app/scripts/restore-journal.py` | file | 0755 | 11583 | 1792906887.806618728 | `8506b7aed83cc9c27379b2e4505f5c6436a28bd181bb5b6cf107949aff2fed40` |
| `app/scripts/run_all_gates.py` | file | 0644 | 2069 | 1792906887.806618728 | `535f0d25cfbe7d8a27566b44e6ae587460ac53dfa4e7887456952ff6ae3606bd` |
| `app/scripts/serverless_runtime.py` | file | 0644 | 3386 | 1792906887.806618728 | `911eb0cc7852345a7db71e4729764da0e1b92c40d656fd35e22afe0aefa77050` |
| `app/scripts/verify-fargate-backend.py` | file | 0644 | 11926 | 1792906887.806618728 | `1e967f4175a3ae76225eae89b2ffc4de0e0e7853abecb9da83891799ba656620` |
| `app/scripts/verify-fargate-containers.py` | file | 0644 | 3256 | 1792906887.806618728 | `b7b1a26c52968031c2664731fb382e27c67d8782ded82514189ee0bc0a8c7cdf` |
| `app/scripts/verify-swift-xctest.py` | file | 0644 | 3115 | 1792906887.806618728 | `c3f6f2bea0f83d3cbed58734d13bfa4a37beafcce88750aa0e53bcbdcb8d6bc1` |
| `app/services/api` | dir | 0755 | 0 | 1792920304.945161659 | `—` |
| `app/services/api/LOCAL_IDENTITY.md` | file | 0644 | 5021 | 1792906887.807328342 | `8c582e988f27f9024abbe8fe44ca4609287088c9518408921ddcdfa6e8e6f8a8` |
| `app/services/api/README.md` | file | 0644 | 13109 | 1792906887.807328342 | `eb2d85d143ebf6545e489aa4f87073cf84bdd5e269f1bc590981188b01b3e06a` |
| `app/services/api/otgd` | dir | 0755 | 0 | 1792917657.816608739 | `—` |
| `app/services/api/otgd/__init__.py` | file | 0644 | 117 | 1792906887.807513988 | `154a88f80d65ab95f4102878db91aed1523f1772016f52330947d4f3e6f6691f` |
| `app/services/api/otgd/auth.py` | file | 0644 | 7164 | 1792906887.807513988 | `865f4d0fcf199b9898d3bb43fd5301f814979d47f01ea48d9be2df75063c4fd7` |
| `app/services/api/otgd/canonical.py` | file | 0644 | 1884 | 1792906887.807513988 | `44400843af24ec301c3f6663e22206d599611934a05cc6b841b58717ffcfc186` |
| `app/services/api/otgd/capture_signing.py` | file | 0644 | 9026 | 1792906887.807513988 | `234fdc8a6660f81683232461d27bfe1821aa39bd6688513fa906b5fa1a1065d2` |
| `app/services/api/otgd/cardiac_authority.py` | file | 0644 | 23805 | 1792906887.807513988 | `3cd89f16cc15742323f753b85bfe4e7ec7563dea42e7b96dfef7dd8f56c33f2d` |
| `app/services/api/otgd/config.py` | file | 0644 | 11006 | 1792906887.807513988 | `684e9b17549519c8cd880dffa9013f0020bef8b25d00dc383290ad7f6105ef61` |
| `app/services/api/otgd/db.py` | file | 0644 | 11432 | 1792906887.807513988 | `60562b98fbaab9c5e83d47ca376f727ca235f2eaa2aa0f9b415cd3bf4d4c612e` |
| `app/services/api/otgd/domain.py` | file | 0644 | 29647 | 1792919931.698071498 | `ba1d898a1107ab9983a5ce4d2f6f04884b94acab3fc6130e04ad106fb3fc92d5` |
| `app/services/api/otgd/dto.py` | file | 0644 | 13280 | 1792906887.807513988 | `8702de1a389b622b30a34b123087026e72159f1930cdeb231d00456a2d534103` |
| `app/services/api/otgd/errors.py` | file | 0644 | 812 | 1792906887.807513988 | `8e9649fce20f0b184249f9f1c2d16392c22cddb439b2b80241f43cd9d47c32b3` |
| `app/services/api/otgd/fargate_runtime.py` | file | 0644 | 23599 | 1792906887.807513988 | `d765a1d84be59fde00ba0fc0227bf6bbdc54c637719828298882f93ca21fcff5` |
| `app/services/api/otgd/history_cursor.py` | file | 0644 | 3080 | 1792917863.309038198 | `f6fff83507257b75a7fcabde84fd35ac46ad129563df4bcafe6fcefac700112e` |
| `app/services/api/otgd/identity_keys.py` | file | 0644 | 1217 | 1792906887.807513988 | `e3abade5a3242b8f8e30a67c2dd791f413c1ee675e95311a45845b4625e75ac0` |
| `app/services/api/otgd/journal_continuity.py` | file | 0644 | 6743 | 1792906887.807513988 | `09eb707c29150acd3e6b520f23e600df1b320ac24d8e3ec1b172b309c60332d2` |
| `app/services/api/otgd/lab_handoff.py` | file | 0644 | 18748 | 1792906887.807513988 | `ab6a3136b75934a95327aee9e20f8f454b5b6d8b4ad8540d5e6c2a755a1e70e1` |
| `app/services/api/otgd/local_identity.py` | file | 0644 | 15374 | 1792912161.4183166 | `1576b35868abd7a22b402f2efea4777b6d34dcfb786e8670350b915972bc1e9e` |
| `app/services/api/otgd/local_oauth_state.py` | file | 0644 | 4339 | 1792910882.839013725 | `e7456407ee43ddf4578161a7eeee2fe0bbe796fbd51a742524f283a1e20678ad` |
| `app/services/api/otgd/main.py` | file | 0644 | 82594 | 1792919931.982077638 | `a84b0694e0e97b41ed113f78ad261e0cfc352c9d84961969311d72d10681a46a` |
| `app/services/api/otgd/migrate.py` | file | 0644 | 6433 | 1792906887.807513988 | `2d11514252952b5f4c808e9bbf37ca643b7411d46be7d177d8f248af3882f3e8` |
| `app/services/api/otgd/model_engine.py` | file | 0644 | 46783 | 1792906887.807513988 | `8c145b7674d44068ad0b16fdab04776f3fc9c3ce9c03bfb772efb211683760e7` |
| `app/services/api/otgd/native_evidence.py` | file | 0644 | 18315 | 1792915780.151884415 | `be7d1fe0b49c666f599d0e8978cdef2e6d5230268335c29d1a1a18663a045ced` |
| `app/services/api/otgd/operator_cli.py` | file | 0644 | 8192 | 1792906887.807513988 | `944d9a6a429f10e6159bcf4761748d0b6c380b6d1b2d787bb7eb2edab273f396` |
| `app/services/api/otgd/operator_governance.py` | file | 0644 | 61295 | 1792906887.807513988 | `1e16fc9b3679b1d6abd4cc6bdad1a53d18e8e02c4b759e2c3a950b04286ce971` |
| `app/services/api/otgd/optical_evidence.py` | file | 0644 | 24913 | 1792906887.807513988 | `3a25c6dbceba62c35f609fee33de126dc20c69064254009a3108301f78cd5a73` |
| `app/services/api/otgd/participant_acquisition.py` | file | 0644 | 31633 | 1792919453.603649151 | `bfef64d21a695a3bf9c3dd853592b007f8ff3b75eb02888af9e70963e33eba6e` |
| `app/services/api/otgd/participant_migration.py` | file | 0644 | 5764 | 1792906887.807513988 | `4e819b8b4aa6619b20345de83991ccef1dce3197c0716559c8b053e69e13b7a0` |
| `app/services/api/otgd/raw_capture.py` | file | 0644 | 11792 | 1792906887.807513988 | `dd0e60fe5d177809e106ed5fb36676d90db5efacc4f73268bd347a7050f69d31` |
| `app/services/api/otgd/raw_export.py` | file | 0644 | 21440 | 1792919932.450087756 | `476079108819029a785bc86950406029752e5834fb5f59660e59d7ac2523d8b8` |
| `app/services/api/otgd/raw_retention.py` | file | 0644 | 44220 | 1792906887.807513988 | `fdf39af29f04bdfc39cce72425cf1c37068985aad74f37f68dae1e3a34de0fd0` |
| `app/services/api/otgd/recovery_authority.py` | file | 0644 | 23441 | 1792906887.807513988 | `ffd428ab0b804cded987ff625c1623297c6e7cf887e5c35f35903221465ac821` |
| `app/services/api/otgd/recovery_scopes.py` | file | 0644 | 8613 | 1792906887.807513988 | `43f68c53f2bc0eca790654e1a8cc9dfe9ba9185348e2989e40269f8d094db31b` |
| `app/services/api/otgd/replacement_links.py` | file | 0644 | 4551 | 1792906887.807513988 | `e78d403aa32f68e6a47eab62864ff7cab057fe6df8c9405c20869dbb0399f8a5` |
| `app/services/api/otgd/replica_cleanup.py` | file | 0644 | 9223 | 1792906887.807513988 | `00bd71eeeb380cd0cab235f7bb74cd329e902d50e451d90e1fdd1010137a3cc3` |
| `app/services/api/otgd/report_revisions.py` | file | 0644 | 41327 | 1792922836.625637267 | `02e6d0331075209a33261ec6f75499dae778e78d590c9451d4e6584dc0f590f4` |
| `app/services/api/otgd/schema_migrations.py` | file | 0644 | 3600 | 1792906887.807513988 | `e78165d36a6287669aa3cada9e83f76822b79d6869922c201b06c87a184703b3` |
| `app/services/api/otgd/serverless_control.py` | file | 0644 | 16752 | 1792906887.807513988 | `0660528a8e939b8f1373bf58df2f775016f669e2b11109255acfe06554d09162` |
| `app/services/api/otgd/serverless_lifecycle.py` | file | 0644 | 9990 | 1792906887.807513988 | `ecbf832e92dbe7965aff8392da8a0b7e4ad3d974314af5535a37df57e854edb2` |
| `app/services/api/otgd/serverless_worker.py` | file | 0644 | 11748 | 1792906887.807513988 | `c7891a212ee4c979b615be01d01b3062e690ee4a0dbdbd7200b213dbcf99b0da` |
| `app/services/api/otgd/storage.py` | file | 0644 | 7025 | 1792906887.807513988 | `fe72246a6247dad323cab209b0c412d20c143233fa46d16387c530bfc2f39d4b` |
| `app/services/api/otgd/synthetic_evidence.py` | file | 0644 | 14529 | 1792906887.807513988 | `2c0f699cc6de6c00ae07831951f12b36b75bdae68b30119fcbf4c82e50f45654` |
| `app/services/api/otgd/vendor_evidence.py` | file | 0644 | 6087 | 1792906887.807513988 | `4d8869f13b01292a2fe052e651858aea8904e391550a62d4f2d6a6fe8c3eb959` |
| `app/services/api/otgd/worker.py` | file | 0644 | 30635 | 1792919932.214082654 | `71340311bc34f66daf641c439b4c6f66098cf1386969e78309731779edb9787d` |
| `app/services/api/otgd/worker_health.py` | file | 0644 | 3401 | 1792906887.807513988 | `9d23d0074ed19244931ce9444f23b82e152c8cd0491f244dc40773d4ddb87aac` |
| `app/services/api/pyproject.toml` | file | 0644 | 894 | 1792906887.807513988 | `eb63eecbf3259ea1cb2440a0ee15b61eecc61887e4a154ff50dd2d595b6961a8` |
| `app/services/api/tests` | dir | 0755 | 0 | 1792919461.095814548 | `—` |
| `app/services/api/tests/__init__.py` | file | 0644 | 0 | 1792906887.811922099 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `app/services/api/tests/conftest.py` | file | 0644 | 3078 | 1792906887.811922099 | `9805699e452fcbdfdbefb1206798bdaa929be70798d2da6dfecd5abe80a6849c` |
| `app/services/api/tests/fixtures` | dir | 0755 | 0 | 1792906887.812020805 | `—` |
| `app/services/api/tests/fixtures/raw-export-v1` | dir | 0755 | 0 | 1792906887.812020805 | `—` |
| `app/services/api/tests/fixtures/raw-export-v1/README.md` | file | 0644 | 1596 | 1792906887.812020805 | `c9d4339604ca44c1bb2631299e321daeae669db2c5e7fc6bcaa176bbc7c81b5e` |
| `app/services/api/tests/fixtures/raw-export-v1/raw-export-job.json` | file | 0644 | 1776 | 1792906887.812020805 | `f39a300b8ef8b461fbbf982508085d1031ef4c6b0b0f1431e0b4775935598059` |
| `app/services/api/tests/fixtures/raw-export-v1/raw-export-revoked-job.json` | file | 0644 | 511 | 1792906887.812020805 | `b33eaa49ea343aa30d68e58f79a154a3cdc88e16ff418940839de6567cde0b0b` |
| `app/services/api/tests/fixtures/raw-export-v1/raw-export-scopes.json` | file | 0644 | 989 | 1792906887.812020805 | `fce0a896f49bee5ff2f13176a0a796de6f8ecbdb68c0257fd1ea7abd13cbbfb6` |
| `app/services/api/tests/fixtures/raw-export-v1/raw-export.zip` | file | 0644 | 5206 | 1792906887.812020805 | `b6485485321ee8cd9ff8947b7f857c05b7d3adb6fad63e33870726ce29823ad1` |
| `app/services/api/tests/fixtures/report-revision-export.zip` | file | 0644 | 7858 | 1792906887.812020805 | `b69ac5fffe007547446ea597f824cd546c7e58bb3d5aa020fdbf1c1f8a5dd25f` |
| `app/services/api/tests/fixtures/report-revision-wire.json` | file | 0644 | 101274 | 1792906887.812020805 | `ef5354125d025eeeecabdce1cf8884800f069d75c2bbeee3812839f303eb3ef3` |
| `app/services/api/tests/generate_report_revision_fixtures.py` | file | 0644 | 4214 | 1792906887.812020805 | `54ad2e16eeb858f06f5b2b1604495ec22023d7c77a29152ea84f010b70ed6dc6` |
| `app/services/api/tests/governance_fixture.py` | file | 0644 | 8693 | 1792906887.812020805 | `2adf96795107cafa47e2daf2d56af00f39f7b571ef7557b924b7f3ea11a2c72a` |
| `app/services/api/tests/helpers.py` | file | 0644 | 3188 | 1792906887.812020805 | `e96d83d26cef46ad4710790d94fdbfb3cfa2b2569fccb9fd18966e5528100fd7` |
| `app/services/api/tests/journal_fixture.py` | file | 0644 | 1190 | 1792906887.812020805 | `f4dff14e0935b6ff6cb459357f9c6084cd143745ddb6e84a8450120aa0e50e8e` |
| `app/services/api/tests/test_api.py` | file | 0644 | 17121 | 1792906887.812020805 | `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48` |
| `app/services/api/tests/test_auth_fixture.py` | file | 0644 | 1513 | 1792906887.812020805 | `c6956358fdf5942b2464724a662cf45817d4a1cd6c973fcd91e9898e4b26fcff` |
| `app/services/api/tests/test_browser_fixture_staff.py` | file | 0644 | 1370 | 1792910923.437052094 | `93b39727aa58c5b48d0c93391b2d89f84510e59f1284b06e3c3e63fdc8654000` |
| `app/services/api/tests/test_capture_guard_upgrade.py` | file | 0644 | 7621 | 1792906887.812020805 | `7283cf493fd3e15ed0b198592b3c02967a8d3bf9182d7552a282eaea69ffe5f6` |
| `app/services/api/tests/test_capture_policy.py` | file | 0644 | 3461 | 1792906887.812020805 | `971a808c066b099c4006aab592d052aa3867d08cdfb10fbd0eb2f5288e5febae` |
| `app/services/api/tests/test_capture_signing.py` | file | 0644 | 10528 | 1792906887.812020805 | `bf0b38a0ec1eafef692a78ccb3d1bb0174d4f81b997a76c840b47ee1d2dc2751` |
| `app/services/api/tests/test_cardiac_authority.py` | file | 0644 | 27373 | 1792906887.812020805 | `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a` |
| `app/services/api/tests/test_cardiac_authority_provenance.py` | file | 0644 | 11203 | 1792906887.812020805 | `6247b1ba439b9d6f87a7467ec66a8fa83272aeb811ade6231196d23776294985` |
| `app/services/api/tests/test_cardiac_interval_governance.py` | file | 0644 | 10300 | 1792906887.812020805 | `542124d8874ec1307305a677039b9d5b36355778cc06c9ccb8799af5cc8e14ff` |
| `app/services/api/tests/test_consent_versions.py` | file | 0644 | 9776 | 1792906887.812020805 | `bdfbbe725088b6adc5e01d3033fd7bfc2ae5f1424c966c3c3ef92249ece1b963` |
| `app/services/api/tests/test_cross_language.py` | file | 0644 | 14746 | 1792906887.812020805 | `f702d93abb8e32afa715db8bfce6f0677ed0276be8369c95b1ed321641c55c39` |
| `app/services/api/tests/test_current_result_readback.py` | file | 0644 | 13938 | 1792922875.798481738 | `8df4b2d22a0eb0b0167ec244dc5c46d93e28608682038074f3a6da4112177023` |
| `app/services/api/tests/test_fargate_lifecycle.py` | file | 0644 | 13964 | 1792906887.812020805 | `7ebad0b4815359104c57f07dc53d66d7952cfd02246b64da4aadf93c1021459f` |
| `app/services/api/tests/test_fargate_runtime.py` | file | 0644 | 30765 | 1792906887.812020805 | `ca197ab6b956e6d137d18c955f7d5dce0df628423458b6fa18bcbf4a4f2877d1` |
| `app/services/api/tests/test_history_cursors.py` | file | 0644 | 7758 | 1792918065.277369215 | `6c309744fdcd25f8d9b28ac4981736f52232700e3047e0ddb5dda45147fbf554` |
| `app/services/api/tests/test_identity_barriers.py` | file | 0644 | 5719 | 1792906887.812020805 | `79480e9dde91c88207e1f10675e1a30f1a5e06e6d7df10cdc8c07c4d70fc15d2` |
| `app/services/api/tests/test_interleavings.py` | file | 0644 | 4860 | 1792906887.812020805 | `e551a4927813b0ba6550e09bec34d0af953ac8e12cebbe2123159bbb49c0e6c1` |
| `app/services/api/tests/test_journal_continuity.py` | file | 0644 | 12854 | 1792906887.812020805 | `4ca05e80289e4626c0096814050433fc39077912de8e761135d1aea59ca9b6cb` |
| `app/services/api/tests/test_lab_handoff.py` | file | 0644 | 34137 | 1792918943.176549111 | `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492` |
| `app/services/api/tests/test_local_identity.py` | file | 0644 | 13486 | 1792912151.982115855 | `1ba323cfe3b792427f8479a4e91c129a8e163ec295336e288280ba6a9459b0a1` |
| `app/services/api/tests/test_local_oauth_security.py` | file | 0644 | 20540 | 1792906887.812020805 | `97d79c648fe5a9b1dc3085146df8bba286647bf2d63b10c76b74c2e63af38b5a` |
| `app/services/api/tests/test_mobile_store_release.py` | file | 0644 | 48227 | 1792915890.839739243 | `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d` |
| `app/services/api/tests/test_model_admission.py` | file | 0644 | 22304 | 1792906887.812020805 | `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867` |
| `app/services/api/tests/test_model_engine.py` | file | 0644 | 18725 | 1792906887.812020805 | `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce` |
| `app/services/api/tests/test_model_evaluation.py` | file | 0644 | 47979 | 1792915935.907208901 | `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31` |
| `app/services/api/tests/test_model_evaluation_cardiac.py` | file | 0644 | 23013 | 1792914923.445376509 | `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83` |
| `app/services/api/tests/test_model_optical_authority.py` | file | 0644 | 6391 | 1792906887.812020805 | `597f44b706a05d5d730b7b4bd28f44e9cbe9d8d02c61cce256dd3eddf5c0150b` |
| `app/services/api/tests/test_operator_governance.py` | file | 0644 | 60185 | 1792916816.434334465 | `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600` |
| `app/services/api/tests/test_optical_evidence.py` | file | 0644 | 18714 | 1792906887.812020805 | `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414` |
| `app/services/api/tests/test_participant_acquisition.py` | file | 0644 | 62175 | 1792919515.540999781 | `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a` |
| `app/services/api/tests/test_participant_postgres.py` | file | 0644 | 11237 | 1792906887.812020805 | `ca85c9d47be13ef424a67378116482b36d8be72225c66619edac625d1b0159c0` |
| `app/services/api/tests/test_participant_privacy_inventory.py` | file | 0644 | 3411 | 1792906887.812020805 | `9b83b8ba8b871175413cf770b749beeba2924fe1496fd055a42e232faff4fd8e` |
| `app/services/api/tests/test_privacy_receipts.py` | file | 0644 | 2413 | 1792916376.820823466 | `84efc2d18bd0bcced419d82a6877e619b2bc1924a06118333b74cbe0f3c0c1d7` |
| `app/services/api/tests/test_raw_capture.py` | file | 0644 | 28922 | 1792906887.812020805 | `ebedc54a2c384fb5992fb61e1959b61d767ad41afbacd8ecf7aec6729710905e` |
| `app/services/api/tests/test_raw_export.py` | file | 0644 | 43106 | 1792916136.075499761 | `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014` |
| `app/services/api/tests/test_raw_retention.py` | file | 0644 | 41295 | 1792906887.812020805 | `4f2115aa7b12c65d238c674d9568a1a64c1d9666a7b50f6543ee5e602d6923ae` |
| `app/services/api/tests/test_reaction_task_goldens.py` | file | 0644 | 13062 | 1792915812.784582312 | `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e` |
| `app/services/api/tests/test_recovery_authority.py` | file | 0644 | 23684 | 1792916816.714340459 | `c6f39c45163f8e2c709b5f63094f1c7df83afb094c9905003fee61fc7fa0b638` |
| `app/services/api/tests/test_recovery_scopes.py` | file | 0644 | 13438 | 1792916816.97034594 | `3fe448145c086a5441b96caeffa0fa006f24a0b18396da3ac60462fba4850344` |
| `app/services/api/tests/test_regional_cleanup_hooks.py` | file | 0644 | 13516 | 1792906887.812020805 | `bf6e3f46b4d853b9fae0ed59eb8e44f40ec15c05b3e741b4308f2399c3816032` |
| `app/services/api/tests/test_replacement_links.py` | file | 0644 | 7608 | 1792906887.815412023 | `e6091da29dd66c1f496bf9857bd70c8b73bceebf61494014aa3ab9ebec74597b` |
| `app/services/api/tests/test_replica_cleanup.py` | file | 0644 | 16181 | 1792906887.815412023 | `7bc5222b3b8d6e05d7d5f6c969a00d717ed1714c862d6f5db59296cdcf8c7ef4` |
| `app/services/api/tests/test_report_revisions.py` | file | 0644 | 51473 | 1792906887.815412023 | `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06` |
| `app/services/api/tests/test_schema_cache.py` | file | 0644 | 2885 | 1792906887.815412023 | `316bef49cdd9ade7c67fe5cecc22064b19126a553ecd0e6375150458271da90c` |
| `app/services/api/tests/test_security.py` | file | 0644 | 10596 | 1792906887.815412023 | `df21a343ca0d2ebb7e0232230c425b2e097e73d1e43f4137198ccfe50b092579` |
| `app/services/api/tests/test_serverless_control.py` | file | 0644 | 19166 | 1792906887.815412023 | `421302a8614a5b887eb4bf0625b86a4f1b0a8d813b2356132f19f35c4bd7dc4f` |
| `app/services/api/tests/test_serverless_lifecycle.py` | file | 0644 | 22792 | 1792906887.815412023 | `5e1ee8d32ff49f6b1182028681e0f27a5c3315f87b3eda45a8b427722cc059bd` |
| `app/services/api/tests/test_serverless_worker.py` | file | 0644 | 14459 | 1792906887.815412023 | `a98c41829888f5ce3e89b4129256d43f1464efbbb1ca4615b552ae9a2cd6963a` |
| `app/services/api/tests/test_storage.py` | file | 0644 | 6112 | 1792906887.815412023 | `66250af1472d94d2d175a3467e9f4304b80445261538ad85a3bea8210678e27f` |
| `app/services/api/tests/test_vendor_evidence.py` | file | 0644 | 12855 | 1792906887.815412023 | `ffb2ca5111d52df5d295f0e594a6eb00b17465c452c0abb21a4d2fb79a8930fe` |
| `app/services/api/tests/test_worker_health.py` | file | 0644 | 3798 | 1792906887.815412023 | `ece26d38e5588ebff044ca72d1ba09582066202bc49c0d72bd434d6cdd532334` |
| `app/services/api/uv.lock` | file | 0644 | 133536 | 1792906887.815412023 | `6cb09a75e943c6102a84ea62dd1a30220c897b62f8a52cc6548a6fdb72f22f1c` |
| `app/tools` | dir | 0755 | 0 | 1792906887.819921086 | `—` |
| `app/tools/check_telemetry.py` | file | 0644 | 633 | 1792906887.819921086 | `8a39906dbc0f9f987de885311b2458a00ffca7307770db37572e32d8da76251e` |
| `app/tools/generate_application_contracts.py` | file | 0644 | 9638 | 1792906887.819921086 | `7372a2c1c2dca5e79369b6b83c6f02129651feebb2541a457cafc69fce30cf63` |
| `app/tools/generate_operator_contracts.py` | file | 0644 | 2244 | 1792906887.819921086 | `b2e2d2507431a0add5aa5a3bca8c828c430fd20b34923c3030a5a24da13ab8ee` |
| `app/tools/model_evaluation.py` | file | 0644 | 54142 | 1792906887.819921086 | `80488d36507c7adb49bbf02448eec9f8ab173008f53e82f59c2d5d782194396c` |
| `app/tools/run_demo.py` | file | 0644 | 2063 | 1792906887.819921086 | `c78df2e08cdbb230e398db69a3cb6ced89a5f6412e28bbf7281af744c621641f` |
| `app/tools/spec_validation.py` | file | 0644 | 9492 | 1792906887.819921086 | `0a187b8978d7b0a096c4bc1ad6245b1f5b89922a45e183cb8499152c3d6289f8` |
| `app/tools/verify_openspec.py` | file | 0644 | 2330 | 1792906887.819921086 | `f70bf575d139a909c089a31761aef4b78b94b280cb1a9e8aadbe2518fd8f10d8` |
| `app/tools/verify_specs.py` | file | 0644 | 12284 | 1792906887.819921086 | `7332fe825925dce65fca3071b9d7ecb441d894c8c99b7c4959993911aeb6b687` |

Proof preparation is complete; adoption is blocked by capacity and pending PM action. Exact current full gates, all 14 CI and six independent replacement reviews/final approval remain required. No sensor/physical timing/anatomical/clinical/participant/fitness-to-drive qualification follows. Measurement defaults, fictional provenance, research controls and the future separately calibrated fuel-cell breath alcohol mg/L scope unchanged.
