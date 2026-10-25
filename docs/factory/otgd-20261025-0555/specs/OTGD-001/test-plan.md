# OTGD-001: verification plan

Canonical: `specs/FULL_SPECIFICATION.md`; SHA-256 `c8f052979fd2a15da2d0bc09c8533bde246cdc559d798696af728378cf5850f7`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/e2e/mobile.spec.ts` — `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`
- `apps/mobile/e2e/raw-recordings.spec.ts` — `2ada98a52caf63a835d979adc71bef5542795c5edbd72fc859cdb7975cbfd3b7`
- `apps/mobile/modules/eye-capture/android/src/test/java/expo/modules/otgdeye/EyeCoreTest.kt` — `8699039fb6bd8673ba07cd7ea601c219b296ca4bf44573caab299aab3b4042c6`
- `apps/mobile/modules/eye-capture/tests/swift/EyeCoreTests.swift` — `5efcf344d7a09069f312fa3e89b08cfca833293b955fb781a31b947813b38bac`
- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/NativeEventSerializationTest.kt` — `55e01ae96993ce1b3071f9a8a202c4247a87b444dadaa718b783c189362e726e`
- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt` — `a78bd28ecae75464e21e29726bce544c6aa6a6c216c7395f6e4b34bb1d600365`
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift` — `f7658f6df0d7f7bbc6a85bd74c33763357a2805faa6d6b48918032acfb8153b2`
- `apps/mobile/src/device/tests/physical.test.ts` — `23d4938d5015dc6cca7f978a44c3d823f0e9aef3f52631a87898ae5d28c82d9d`
- `apps/mobile/src/device/tests/protocol.test.ts` — `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`
- `apps/mobile/src/device/tests/signal.test.ts` — `6081eb0c7c2681f0520d69962d494c2dd14bfc60cd51bceed79209c9e862fba5`
- `apps/mobile/tests/acquisition.test.ts` — `797e9858167b9b80bff401e0b66c3fda1f9ae56c8f007fbe5b10c4aeb0b159be`
- `apps/mobile/tests/controller.test.ts` — `e354d822120520b2336bacd98cac30b34de7921862cd4562342706358d9efa92`
- `apps/mobile/tests/device-presentation.test.ts` — `11e79b59ead32c0a6bc4fa818784bc00347f337cfb5dff71d13534673064600a`
- `apps/mobile/tests/domain.test.ts` — `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`
- `apps/mobile/tests/export-projection.test.ts` — `4707168f94a1706dd5f86d1014835651d57eba5be5d1093d2455bfd3d03732c2`
- `apps/mobile/tests/eye-acquisition.test.ts` — `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`
- `apps/mobile/tests/generation-cache.test.ts` — `2a30b7da6606d73d185be5efed38968469e3fcde816063890f8e63bd7b32d756`
- `apps/mobile/tests/lifecycle.test.ts` — `a69785a96f7fbe8c6193ba617741db43650cf9ad32a2eb595d92bf04ae9a4099`
- `apps/mobile/tests/measurement-format.test.ts` — `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`
- `apps/mobile/tests/native-storage.test.ts` — `52005beea373ed0bf603dffffc6a20cb2e8fd07371bf5cb0712afa4b3bf208df`
- `apps/mobile/tests/participant-acquisition.test.ts` — `1867260acffffc4ac828866c0022ce3d1e2bb34b001e1b6558786a794939cf2f`
- `apps/mobile/tests/profile-form.test.ts` — `0c2b5f39798e297673af92b008243169f4628c08438fc0be9defe065da2dc30e`
- `apps/mobile/tests/raw-artifacts.test.ts` — `80522a5edec7a841cdaf1ed5257ce336ea1ababb4d2a4001d1c7a443fe7e94b3`
- `apps/mobile/tests/raw-export.test.ts` — `c68c9146811b6261e384bef9759f0bde4a8a08f3be26391c888da40700d09359`
- `apps/mobile/tests/raw-recordings.test.ts` — `c850243e541fffdce52a7b44db52ff300e637448bb26d6281eef4c8428c51354`
- `apps/mobile/tests/raw-upload.test.ts` — `7771c6a9657ccd0dba4d716eb6504e80a97c36290fb6bbd00b6969db2ba769d9`
- `apps/mobile/tests/report-revisions.test.ts` — `4d1d9f5becc44e8d716ab339de02cdd5c3afde155d2afbbdec5957c33114c3fb`
- `apps/mobile/tests/research-result.test.ts` — `5e39d0bf4fb9376df15ae349da774b343dc0428d80fae35e6ee7f2b618ba33ea`
- `apps/mobile/tests/sync.test.ts` — `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`
- `apps/mobile/tests/workspace-scope.test.ts` — `d009b00717789b980a437f76ee379dbf1f3771aac46021d718f649b30544339d`
- `infra/test/test_ci_gates.py` — `82805a98da905f9704f2016c67c726ad10c679f55f548179ed8981cf177f7904`
- `infra/test/test_document_links.py` — `6dd675024788db2819ce01a80f138a3efd5aae849430587933d80624538e4635`
- `infra/test/test_maintenance.py` — `f7222dcd026bcbe70c73279fbb8c75a65bef166e311e93e0729f3d3570b356bf`
- `infra/test/test_provenance.py` — `996ead63b1f3ae3999aa31d81e3de893bbc50b62bfaac6e2a69f88a968d5f6a1`
- `infra/test/test_recovery.py` — `598881481a5ab8561446d64b3d949c8f883f52ee4d1d9cc3120a909a383c737c`
- `infra/test/test_regional_budget.py` — `99b8e2f2582f874d9ca2fddc92a44e69c3b0b287c6122629152ddd5a25084df7`
- `infra/test/test_release.py` — `3013213897c8f1721e0f28a2c4610f18b48cb46ed6a5f5900ebb4495f3e3f9d5`
- `infra/test/test_secure_reader_build.py` — `beb1569ec43a14c535b13f29a77222e3d927b8a5c75f38e4bdf630eb79a7cc28`
- `services/api/tests/test_api.py` — `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`
- `services/api/tests/test_capture_signing.py` — `bf0b38a0ec1eafef692a78ccb3d1bb0174d4f81b997a76c840b47ee1d2dc2751`
- `services/api/tests/test_cardiac_authority.py` — `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`
- `services/api/tests/test_identity_barriers.py` — `79480e9dde91c88207e1f10675e1a30f1a5e06e6d7df10cdc8c07c4d70fc15d2`
- `services/api/tests/test_interleavings.py` — `e551a4927813b0ba6550e09bec34d0af953ac8e12cebbe2123159bbb49c0e6c1`
- `services/api/tests/test_journal_continuity.py` — `4ca05e80289e4626c0096814050433fc39077912de8e761135d1aea59ca9b6cb`
- `services/api/tests/test_lab_handoff.py` — `3396acf6ae29a8d994bc37f937417b446acb1c40499b6c6a6ce81fff7e0cbeb0`
- `services/api/tests/test_model_admission.py` — `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`
- `services/api/tests/test_model_engine.py` — `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`
- `services/api/tests/test_model_evaluation.py` — `60013323430a0979caeffcef4b2983566a028b0f50e75938df7f053c0498fdc0`
- `services/api/tests/test_model_evaluation_cardiac.py` — `6ba27142296226c46ec947b7fe5e2a47168faac3baed130da00c364cc85d4ea8`
- `services/api/tests/test_model_optical_authority.py` — `597f44b706a05d5d730b7b4bd28f44e9cbe9d8d02c61cce256dd3eddf5c0150b`
- `services/api/tests/test_operator_governance.py` — `4d512a3ad9f7c65b69ee09d94fb471799d1aff63a5bc4c34140526dcac280ae7`
- `services/api/tests/test_participant_acquisition.py` — `a9113ffb30c7907e12aad494ddfdf7d83afc96ef5f3d8c0668768158c2948b57`
- `services/api/tests/test_participant_postgres.py` — `ca85c9d47be13ef424a67378116482b36d8be72225c66619edac625d1b0159c0`
- `services/api/tests/test_raw_capture.py` — `ebedc54a2c384fb5992fb61e1959b61d767ad41afbacd8ecf7aec6729710905e`
- `services/api/tests/test_raw_export.py` — `7ee249d50b4f2bd684639b4340159f3f8eab2f25ede232c0d67ba89bfb7ec627`
- `services/api/tests/test_raw_retention.py` — `4f2115aa7b12c65d238c674d9568a1a64c1d9666a7b50f6543ee5e602d6923ae`
- `services/api/tests/test_recovery_authority.py` — `8729463f12702d5da5850ce2436f24c05389a14ed556348f683525e9508bf236`
- `services/api/tests/test_recovery_scopes.py` — `3783cfcb8a1e80662e828d51356a5f7037d9b40468a3451a8b3e8f1960f63ad1`
- `services/api/tests/test_report_revisions.py` — `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`
- `services/api/tests/test_security.py` — `df21a343ca0d2ebb7e0232230c425b2e097e73d1e43f4137198ccfe50b092579`
- `services/api/tests/test_vendor_evidence.py` — `ffb2ca5111d52df5d295f0e594a6eb00b17465c452c0abb21a4d2fb79a8930fe`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### HW-001 — The first electronics prototype MUST use the selected Nano ESP32 platform unless an architectural decision records a replacement.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `HW-001`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-HW-001-01 | Owner acceptance evidence — BOM and firmware target agree with ADR-004. | `apps/mobile/tests/acquisition.test.ts:1158` — late binding receipt cannot bind a foreign replacement or erase a newer same-owner intent | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### HW-002 — Synthetic readings MUST be visibly labeled and carry `simulated` provenance through every storage and display layer.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `HW-002`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-HW-002-01 | Owner acceptance evidence — End-to-end inspection shows no loss or replacement of provenance. | `apps/mobile/src/device/tests/protocol.test.ts:87` — local simulator exercises handshake, clocks, full framed capture and explicit simulated provenance<br>`apps/mobile/tests/acquisition.test.ts:1158` — late binding receipt cannot bind a foreign replacement or erase a newer same-owner intent | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### HW-003 — Each physical reader MUST expose stable device identity, hardware revision, firmware version, and boot/session identity.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `HW-003`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-HW-003-01 | Owner acceptance evidence — Trace a captured record to one reader and firmware build. | `apps/mobile/src/device/tests/physical.test.ts:654` — actual backend bound-reader HTTP fixture passes strict physical token and exact material digest<br>`apps/mobile/tests/acquisition.test.ts:1478` — revoked consent, stale approval and reader substitution cannot invoke hardware | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### HW-004 — The interface MUST detect incomplete frames, duplicate messages, disconnects, and stale readings.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `HW-004`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-HW-004-01 | Owner acceptance evidence — Controlled fault injection produces explicit recoverable or invalid states. | `apps/mobile/tests/acquisition.test.ts:870` — reference laboratory collection has no BLE acquisition, persists a recoverable pending draft, imports separate analysis then permits explicit finalization | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### HW-005 — A body-connected ECG prototype MUST pass the electrical-safety design review before use; early evaluation MUST use a simulator.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `HW-005`.

Prerequisites and limits: BLOCKED external: G-05 electrical-safety review before participant connection; ECG simulator and approved whole-system power/USB/isolation configuration. NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-HW-005-01 | Owner acceptance evidence — Gate G-05 sign-off and bench evidence precede participant connection. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### HW-006 — ECG power, isolation, charging, exposed conductors, and attached USB equipment MUST be evaluated as one system.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `HW-006`.

Prerequisites and limits: BLOCKED external: G-05 whole-system safety evidence, power/connection diagrams and independent hardware review. NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-HW-006-01 | Owner acceptance evidence — Approved power/connection diagram and documented permitted configurations. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### HW-007 — Cardiac acquisition MUST retain sample rate, gain/scaling, contact quality, dropped-sample information, and relevant filtering versions.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `HW-007`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-HW-007-01 | Owner acceptance evidence — Reference signal reconstructs within frozen acquisition tolerances. | `apps/mobile/tests/acquisition.test.ts:870` — reference laboratory collection has no BLE acquisition, persists a recoverable pending draft, imports separate analysis then permits explicit finalization<br>`apps/mobile/src/device/tests/physical.test.ts:820` — actual SparkFun production factory decodes derived-only quality evidence without inventing raw consent or cadence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### HW-008 — Optical capture MUST use an approved stimulus and positioning protocol with bounded exposure; arbitrary phone-flash settings MUST NOT be assumed safe or equivalent.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `HW-008`.

Prerequisites and limits: BLOCKED external: G-04 approved bounded optical exposure and supported positioning/stimulus configuration; measured physical light onset is distinct. NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-HW-008-01 | Owner acceptance evidence — G-04 defines limits and verifies supported configurations. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### HW-009 — Pupil features MUST retain illumination, camera/device metadata, frame timing, segmentation quality, and the coordinate/scale basis.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `HW-009`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-HW-009-01 | Owner acceptance evidence — Reprocess retained permitted data to the same versioned features. | `apps/mobile/src/device/tests/physical.test.ts:820` — actual SparkFun production factory decodes derived-only quality evidence without inventing raw consent or cadence<br>`apps/mobile/tests/acquisition.test.ts:1366` — actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### HW-010 — The prototype MUST keep saliva-contaminated components separate from user electrical contacts and reusable optical surfaces.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `HW-010`.

Prerequisites and limits: BLOCKED external: Contamination-handling bench inspection and approved physical design. NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-HW-010-01 | Owner acceptance evidence — Handling review and inspection demonstrate the defined contamination boundary. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### HW-011 — The final product SHOULD minimize removable electronics and exposed wiring after feasibility; dimensions and battery targets MUST be selected from measured workload.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `HW-011`.

Prerequisites and limits: BLOCKED external: G-10 measured dimensions/battery/duty cycle and human-factors evidence. NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-HW-011-01 | Owner acceptance evidence — G-10 approved drawings, duty-cycle measurements, and human-factors results. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### HW-012 — Reader calibration, maintenance, component replacement, and compatibility MUST be traceable.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `HW-012`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-HW-012-01 | Owner acceptance evidence — An expired or incompatible configuration cannot be reported as qualified. | `apps/mobile/tests/acquisition.test.ts:1214` — reader change during expired-intent removal never starts recovery for its replacement<br>`apps/mobile/src/device/tests/protocol.test.ts:60` — capability source and calibration cannot promote an unprovisioned peripheral | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### ANA-001 — A valid check MUST use one identified saliva collection; multiple analyte channels MAY share it.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `ANA-001`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-ANA-001-01 | Owner acceptance evidence — Specimen lineage shows one collection for a valid check. | `services/api/tests/test_report_revisions.py:919` — test_saliva_free_finalized_check_lists_no_revisions_and_preserves_null_collection<br>`apps/mobile/tests/participant-acquisition.test.ts:87` — actual Python protocol, immutable acknowledgement, specimen and imported report preserve separate truthful lineage | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### ANA-002 — Collection method MUST define volume or dilution, container/collector, handling, timing, storage, and allowed processing.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `ANA-002`.

Prerequisites and limits: BLOCKED external: G-02 approved SOP, physical recovery/stability/handling evidence.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-ANA-002-01 | Owner acceptance evidence — Approved collection SOP and recovery/stability evidence at G-02. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### ANA-003 — Parent delta-9 THC MUST be evaluated first; THC-COOH and 11-OH-THC MUST remain separate feasibility decisions.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `ANA-003`.

Prerequisites and limits: BLOCKED external: Separate chemical feasibility report; THC first, other analytes independently gated.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-ANA-003-01 | Owner acceptance evidence — Channel selection report identifies measured feasibility and unresolved channels. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `11`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### ANA-004 — Each channel MUST establish analyte identity, selectivity, calibration range, detection and quantification limits, precision, bias, recovery, and stability.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `ANA-004`.

Prerequisites and limits: BLOCKED external: G-03 analytical calibration/selectivity/LoD/LoQ/precision/bias/recovery/stability report.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-ANA-004-01 | Owner acceptance evidence — Prespecified qualification report passes G-03 criteria. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### ANA-005 — The reference-method plan MUST address interferents, related cannabinoids/isomers, collection materials, carryover, and oral-matrix effects.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `ANA-005`.

Prerequisites and limits: BLOCKED external: Approved interferent/isomer/carryover/oral-matrix challenge and reference-method comparison.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-ANA-005-01 | Owner acceptance evidence — Challenge panel and method comparison are approved before final qualification. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### ANA-006 — Each value MUST preserve original units and a canonical ng/mL value when conversion is valid; conversion factors MUST be explicit.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `ANA-006`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-ANA-006-01 | Owner acceptance evidence — Unit fixtures include pg/mL conversion without magnitude errors. | `services/api/tests/test_report_revisions.py:463` — test_correction_and_delayed_reanalysis_preserve_original_evidence_and_exact_units<br>`apps/mobile/tests/export-projection.test.ts:54` — retained sample unit conversion, censored null and collection binding are independently checked | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### ANA-007 — Results MUST use the canonical qualifier vocabulary; below-LOQ and not-detected results MUST NOT be stored as measured zero.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `ANA-007`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-ANA-007-01 | Owner acceptance evidence — Contract validation rejects fabricated quantified values for censored results. | `apps/mobile/tests/measurement-format.test.ts:23` — below LOQ displays the supplied bound without creating a concentration or rounding it to zero<br>`services/api/tests/test_lab_handoff.py:304` — test_import_rejects_forged_or_incompatible_analytical_evidence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### ANA-008 — Free and total-after-hydrolysis measurements MUST remain distinguishable; unspecified basis MUST block any model requiring a defined basis.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `ANA-008`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-ANA-008-01 | Owner acceptance evidence — Cross-field validation and incompatible-input cases pass. | `services/api/tests/test_lab_handoff.py:304` — test_import_rejects_forged_or_incompatible_analytical_evidence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### ANA-009 — A portable assay MUST be compared with a reference laboratory method on paired specimens across its intended usable range.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `ANA-009`.

Prerequisites and limits: BLOCKED external: Paired real reference-laboratory study across usable range, independent agreement/failure review.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-ANA-009-01 | Owner acceptance evidence — Prespecified agreement and failure analysis; external validation before claims. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### ANA-010 — Each assay record MUST retain collection/analysis time, lot, method version, calibration, instrument, operator or automation identity, and quality.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `ANA-010`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-ANA-010-01 | Owner acceptance evidence — An independent reviewer reconstructs a selected reported measurement. | `apps/mobile/tests/participant-acquisition.test.ts:257` — document digest, selected method, exact UUID/calendar and electrical setup boundaries are enforced<br>`apps/mobile/e2e/raw-recordings.spec.ts:913` — laboratory method review pins the actual selected method without BLE and resets acknowledgement on document replacement | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### ANA-011 — Failed adequacy, contamination, overflow, expired supplies, and out-of-range results MUST have distinct recorded reasons.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `ANA-011`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-ANA-011-01 | Owner acceptance evidence — Deliberate invalid specimens cannot yield an apparently ordinary concentration. | `apps/mobile/tests/report-revisions.test.ts:164` — rehashed revised results cannot promote an originally invalid check or relabel evaluation as a new assessment<br>`apps/mobile/tests/measurement-format.test.ts:65` — only quantified results display a numeric concentration, preserving a real zero if reported | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### ANA-012 — A consumable replacement MUST create a new attempt linked to the prior one; finalized specimens MUST NOT be silently overwritten.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `ANA-012`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-ANA-012-01 | Owner acceptance evidence — Retry audit preserves both attempts and their disposition. | `services/api/tests/test_participant_acquisition.py:380` — test_invalid_collection_preserves_failure_and_linked_retry_allocates_new_sample<br>`services/api/tests/test_report_revisions.py:919` — test_saliva_free_finalized_check_lists_no_revisions_and_preserves_null_collection | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### ANA-013 — Cartridge selection MUST document consumable cost, shelf life, storage, disposal, sample burden, and observed turnaround.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `ANA-013`.

Prerequisites and limits: BLOCKED external: G-03/G-13 measured consumable cost/shelf life/storage/disposal/burden/turnaround evidence.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-ANA-013-01 | Owner acceptance evidence — G-03 and G-13 contain measured data or dated supplier evidence. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### APP-001 — The app MUST guide one continuous session and show capture progress without representing data capture as a prediction.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `APP-001`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-APP-001-01 | Owner acceptance evidence — Scripted P0 journey displays measurement-only completion. | `apps/mobile/e2e/mobile.spec.ts:6` — guest completes a measurement-only check, exact export and privacy/settings journey<br>`apps/mobile/tests/eye-acquisition.test.ts:264` — End camera dispatches native shutdown and running=false before delayed evidence persistence, and a committed completion survives cancel | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### APP-002 — Profile MUST preserve age, height, weight, units, dates, and source; BMI MUST be derived consistently from qualified height/weight.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `APP-002`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-APP-002-01 | Owner acceptance evidence — Boundary and unit examples produce correct BMI or explicit missing status. | `apps/mobile/tests/profile-form.test.ts:87` — display rounding and repeated unit toggles preserve original canonical values<br>`apps/mobile/e2e/mobile.spec.ts:142` — live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### APP-003 — Use frequency and optional route/timing MUST allow unknown and declined values; self-report MUST remain identifiable as such.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `APP-003`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-APP-003-01 | Owner acceptance evidence — Missing context survives export and cannot become a fabricated timestamp. | `apps/mobile/tests/profile-form.test.ts:56` — optional blank demographics stay null and unknown remains distinct from declined<br>`apps/mobile/tests/controller.test.ts:465` — unmounted task arm is invalidated while unsupported or stale task terminals cannot become valid evidence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### APP-004 — `choice_inhibit_v0` MUST contain six practice and 60 scored trials with 48 go and 12 no-go trials.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `APP-004`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-APP-004-01 | Owner acceptance evidence — Task event record verifies counts and excludes practice from scored features. | `apps/mobile/tests/domain.test.ts:270` — process interruption preserves invalid task evidence with null aggregate features<br>`apps/mobile/tests/research-result.test.ts:163` — changed immutable proof, endpoint, registry identity, classification or owner-record link is never displayed | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `12`, `48`, `60`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### APP-005 — Task timing, stimulus schedule, response windows, interruptions, and invalid-trial rules MUST follow the versioned LLD contract.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `APP-005`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-APP-005-01 | Owner acceptance evidence — Seeded replay and event-level inspection reproduce features. | `apps/mobile/tests/domain.test.ts:270` — process interruption preserves invalid task evidence with null aggregate features<br>`apps/mobile/tests/controller.test.ts:465` — unmounted task arm is invalidated while unsupported or stale task terminals cannot become valid evidence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### APP-006 — Reaction features MUST include speed, variability, omissions, incorrect choices, and commission errors as defined by feature version.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `APP-006`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-APP-006-01 | Owner acceptance evidence — Reference event streams match expected derived feature records. | `apps/mobile/tests/domain.test.ts:270` — process interruption preserves invalid task evidence with null aggregate features | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### APP-007 — Timing-critical capture MUST use native monotonic timing; reported latency tolerances MUST be measured on supported devices.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `APP-007`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-APP-007-01 | Owner acceptance evidence — G-06 freezes and verifies device-specific timing acceptance. | `apps/mobile/tests/eye-acquisition.test.ts:33` — actual Python optical fixture projects bounded native evidence without inventing millimeters, physical onset or latency<br>`apps/mobile/tests/domain.test.ts:152` — check freezes original profile timestamp and recomputes elapsed use at its start | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### APP-008 — Backgrounding, notifications, orientation changes, late frames, and interrupted touches MUST be recorded or invalidate the affected capture.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `APP-008`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-APP-008-01 | Owner acceptance evidence — Interruption cases produce the prescribed quality and retry state. | `apps/mobile/tests/domain.test.ts:270` — process interruption preserves invalid task evidence with null aggregate features | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### APP-009 — Pupil capture MUST reject inadequate recordings under frozen quality rules; normalized geometry MUST NOT be mislabeled millimeters.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `APP-009`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-APP-009-01 | Owner acceptance evidence — Low-quality and unscaled examples cannot pass as calibrated diameter. | `apps/mobile/tests/eye-acquisition.test.ts:33` — actual Python optical fixture projects bounded native evidence without inventing millimeters, physical onset or latency<br>`apps/mobile/tests/domain.test.ts:246` — guest check cannot upload and never acquires an account owner by sign-in | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### APP-010 — Heart-rate context MUST retain acquisition duration, position/activity instructions, quality, and source device.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `APP-010`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-APP-010-01 | Owner acceptance evidence — Result inspection identifies whether a measurement followed the approved protocol. | `apps/mobile/tests/eye-acquisition.test.ts:230` — feature-only optical Start follows context, attempt and fresh grant; native completion saves locally with a separate actual acquisition clock<br>`apps/mobile/tests/domain.test.ts:84` — all retained measurement and application DTO schema copies match source contracts | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### APP-011 — Personal baseline use MUST require qualified earlier sessions and a compatible mode; first-use behavior MUST be separately evaluated.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `APP-011`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-APP-011-01 | Owner acceptance evidence — Temporal audit prevents later sessions entering a baseline. | `apps/mobile/tests/controller.test.ts:228` — maintenance pauses queued consent and withdrawal prevents its later automatic transmission<br>`apps/mobile/tests/research-result.test.ts:242` — personalized baseline cannot omit baseline evidence and legacy 0.1 result cannot acquire research fields | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### APP-012 — The interface MUST distinguish `measurement_only`, `research_estimate`, `inconclusive`, and `invalid`; only `research_estimate` may carry probability.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `APP-012`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-APP-012-01 | Owner acceptance evidence — State-by-state screenshots and API checks match the LLD. | `apps/mobile/tests/domain.test.ts:323` — every research_estimate is rejected even when its shape could be schema-valid<br>`apps/mobile/tests/research-result.test.ts:242` — personalized baseline cannot omit baseline evidence and legacy 0.1 result cannot acquire research fields | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### APP-013 — The app MUST NOT show “safe to drive,” a legal clearance, or unsupported intoxication certainty.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `APP-013`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-APP-013-01 | Owner acceptance evidence — Copy review covers all result, notification, and error screens. | `apps/mobile/tests/controller.test.ts:465` — unmounted task arm is invalidated while unsupported or stale task terminals cannot become valid evidence<br>`apps/mobile/tests/research-result.test.ts:242` — personalized baseline cannot omit baseline evidence and legacy 0.1 result cannot acquire research fields | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### APP-014 — Supported-device, accessibility, language, and input-mode limits MUST be explicit; incompatible task adaptations MUST be revalidated.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `APP-014`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-APP-014-01 | Owner acceptance evidence — G-10 lists supported configurations and tested accommodations. | `apps/mobile/e2e/mobile.spec.ts:142` — live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit<br>`apps/mobile/tests/controller.test.ts:465` — unmounted task arm is invalidated while unsupported or stale task terminals cannot become valid evidence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### MOD-001 — The target MUST be a prespecified independent current-functional-impairment endpoint; exposure and subjective high MUST remain separate labels.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `MOD-001`.

Prerequisites and limits: BLOCKED external: G-01 independently approved endpoint, assessor, timing and label protocol. Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-MOD-001-01 | Owner acceptance evidence — G-01 protocol defines outcome, assessor, timing, and label rules. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### MOD-002 — Inference MUST NOT require an invented demographic metabolic-clearance formula.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `MOD-002`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-MOD-002-01 | Owner acceptance evidence — Model review identifies measured features and any explicitly evaluated latent model. | `apps/mobile/tests/domain.test.ts:123` — default workspace contains no invented demographics and no automatic retry | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### MOD-003 — Feature construction MUST preserve missingness, censoring, assay basis, provenance, and quality without silently normalizing them to healthy values.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `MOD-003`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-MOD-003-01 | Owner acceptance evidence — Adversarial synthetic records produce the specified validity behavior. | `services/api/tests/test_model_engine.py:410` — test_feature_missingness_and_temporal_baseline_gates<br>`services/api/tests/test_model_evaluation.py:312` — test_same_check_observations_and_later_assay_delivery_preserve_original_target | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### MOD-004 — Training and results MUST be pinned to acquisition, assay, task, feature, and model versions.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `MOD-004`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-MOD-004-01 | Owner acceptance evidence — Any prediction can be reconstructed from immutable versioned inputs. | `apps/mobile/tests/research-result.test.ts:163` — changed immutable proof, endpoint, registry identity, classification or owner-record link is never displayed<br>`services/api/tests/test_cardiac_authority.py:377` — test_training_evidence_refs_cannot_qualify_different_current_reader | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### MOD-005 — Data splits MUST hold out whole people and evaluate later sessions; preprocessing and selection MUST be fit on training data only.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `MOD-005`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-MOD-005-01 | Owner acceptance evidence — Split audit and leakage review pass before locked evaluation. | `services/api/tests/test_model_engine.py:437` — test_training_evaluation_policy_and_result_proof_are_bound<br>`services/api/tests/test_model_evaluation_cardiac.py:214` — test_held_out_hr_values_and_outcomes_cannot_affect_training | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### MOD-006 — Features MUST use only information available at the check; future measurements and independent outcome assessments MUST NOT enter predictors.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `MOD-006`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-MOD-006-01 | Owner acceptance evidence — Timestamp and dependency audit covers each feature and baseline. | `services/api/tests/test_model_engine.py:410` — test_feature_missingness_and_temporal_baseline_gates<br>`services/api/tests/test_model_admission.py:567` — test_baseline_bounds_and_bias_are_applied_to_frozen_features | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### MOD-007 — The manifest MUST declare lifecycle, endpoint, required channels, compatibility, units/bases, quality rules, calibration, threshold policy, and permitted cohort.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `MOD-007`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-MOD-007-01 | Owner acceptance evidence — Manifest review and incompatible-record checks pass. | `apps/mobile/tests/research-result.test.ts:163` — changed immutable proof, endpoint, registry identity, classification or owner-record link is never displayed<br>`services/api/tests/test_cardiac_authority.py:277` — test_actual_artifact_not_just_required_channels_is_hr_only | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### MOD-008 — Lifecycle MUST be `unvalidated`, `active_research`, or `retired`; activation MUST require recorded research authorization.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `MOD-008`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-MOD-008-01 | Owner acceptance evidence — Unauthorized activation and retired-model invocation are rejected. | `services/api/tests/test_model_admission.py:396` — test_http_native_evidence_real_registry_lifecycle_worker_and_research_read<br>`apps/mobile/tests/research-result.test.ts:242` — personalized baseline cannot omit baseline evidence and legacy 0.1 result cannot acquire research fields | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### MOD-009 — P0/P1 MUST never emit a probability; simulated required inputs MUST never qualify for a participant research estimate.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `MOD-009`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-MOD-009-01 | Owner acceptance evidence — Negative inference cases verify null/absent probability and explicit reason. | `apps/mobile/tests/research-result.test.ts:218` — a verified uncertainty band requires null abstention rather than a probability or optimistic classification<br>`services/api/tests/test_cardiac_authority.py:377` — test_training_evidence_refs_cannot_qualify_different_current_reader | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### MOD-010 — A probability MUST require an authorized P2 session, `active_research` model, valid required channels, and compatible protocol/cohort.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `MOD-010`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-MOD-010-01 | Owner acceptance evidence — Every gate has both passing and rejecting integration evidence. | `services/api/tests/test_model_engine.py:364` — test_every_acquisition_gate_has_rejection<br>`services/api/tests/test_model_evaluation.py:354` — test_later_validation_without_prior_held_out_session_and_single_class_cohort_fail | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### MOD-011 — Missing channels MAY use a separately qualified model variant; automatic reuse of an incompatible full-channel model is prohibited.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `MOD-011`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-MOD-011-01 | Owner acceptance evidence — Variant selection is explicit, versioned, and validated. | `services/api/tests/test_model_engine.py:364` — test_every_acquisition_gate_has_rejection | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### MOD-012 — Thresholds and calibration MUST be selected before confirmatory testing and frozen with the model artifact.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `MOD-012`.

Prerequisites and limits: BLOCKED external: Prespecified statistical plan and signed frozen artifacts predate confirmatory access; software fixtures prove no authentic approval. Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-MOD-012-01 | Owner acceptance evidence — Locked analysis plan and artifact hashes predate evaluation access. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### MOD-013 — Prediction MUST include model version, applicable endpoint, valid-input summary, uncertainty policy, time basis, and outcome state.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `MOD-013`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-MOD-013-01 | Owner acceptance evidence — Result contract and independent interpretation review pass. | `apps/mobile/tests/research-result.test.ts:163` — changed immutable proof, endpoint, registry identity, classification or owner-record link is never displayed<br>`services/api/tests/test_model_engine.py:437` — test_training_evaluation_policy_and_result_proof_are_bound | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### MOD-014 — Feature selection MUST compare chemical-only, app-only, combined, and ECG-removed configurations on the same evaluation design.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `MOD-014`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-MOD-014-01 | Owner acceptance evidence — Ablation report supports retained measurement burden. | `services/api/tests/test_cardiac_authority.py:363` — test_hr_report_cannot_claim_unmeasured_chemical_or_ecg_comparisons | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### MOD-015 — Model updates MUST require versioned reevaluation and authorization; consumer measurements MUST NOT silently retrain a deployed model.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `MOD-015`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-MOD-015-01 | Owner acceptance evidence — Change-control exercise preserves the prior artifact and results. | `services/api/tests/test_model_admission.py:542` — test_model_retirement_and_consent_change_between_compute_and_commit | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### ALC-001 — Alcohol MUST be a distinct measured channel; physiology or a generic gas-sensor signal MUST NOT be labeled calibrated breath alcohol.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `ALC-001`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-ALC-001-01 | Owner acceptance evidence — Interface and synthetic demonstrations retain channel identity and provenance. | `apps/mobile/tests/export-projection.test.ts:29` — every retained simulated sample, eye, PPG and separate alcohol projection satisfies its exact typed evidence<br>`apps/mobile/e2e/mobile.spec.ts:142` — live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### ALC-002 — The candidate design SHOULD use a fuel-cell measurement path with controlled sampling; final component choice remains gated.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `ALC-002`.

Prerequisites and limits: BLOCKED external: G-11 selected calibrated fuel-cell breath-alcohol path with controlled sampling; component choice independently gated.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-ALC-002-01 | Owner acceptance evidence — G-11 documents supplier specifications and design tradeoffs. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### ALC-003 — The channel MUST report mg/L with calibration identity, units, sampling quality, time, and range qualifier.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `ALC-003`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-ALC-003-01 | Owner acceptance evidence — Contract fixtures preserve all metadata without unapproved blood conversion. | `apps/mobile/tests/domain.test.ts:222` — synthetic concentrations preserve unknown metabolites as null, with exact pg/mL conversion<br>`apps/mobile/tests/measurement-format.test.ts:35` — missing limits produce a qualifier without an invented cutoff | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### ALC-004 — Mouthpiece hygiene, sample adequacy, environmental effects, calibration interval, and cross-sensitivity MUST be qualified independently.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `ALC-004`.

Prerequisites and limits: BLOCKED external: G-11 independent mouthpiece/adequacy/environment/calibration/cross-sensitivity qualification.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-ALC-004-01 | Owner acceptance evidence — Dedicated alcohol qualification against the selected reference method. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### ALC-005 — Cannabis/alcohol co-use MUST be a defined study condition or explicitly unsupported cohort; scores MUST NOT be averaged.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `ALC-005`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-ALC-005-01 | Owner acceptance evidence — Protocol and model manifest agree on co-use handling. | `apps/mobile/tests/export-projection.test.ts:29` — every retained simulated sample, eye, PPG and separate alcohol projection satisfies its exact typed evidence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### SEC-001 — GitHub MUST contain only code, documentation, and synthetic examples; participant data, real eye video, ECG, exports, or credentials are prohibited.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `SEC-001`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-SEC-001-01 | Owner acceptance evidence — Pre-commit/release review and secret/data scan of the staged changes. | `apps/mobile/e2e/raw-recordings.spec.ts:519` — eye and ECG descriptions follow the approved observation and actual provenance without claiming measured light onset<br>`services/api/tests/test_raw_export.py:205` — test_distinct_submit_review_release_required | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### SEC-002 — Research identifiers MUST be separated from direct identity; access MUST follow least privilege and a defined role matrix.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `SEC-002`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-SEC-002-01 | Owner acceptance evidence — Unauthorized-role tests and identity-mapping review pass. | `apps/mobile/e2e/raw-recordings.spec.ts:1253` — actual raw export component keeps every source and separate acknowledgment off until exact purpose review, then resets for another owner | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### SEC-003 — Upload of participant data MUST be explicit and protocol-authorized; basic local operation MUST NOT imply research enrollment.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `SEC-003`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-SEC-003-01 | Owner acceptance evidence — Consent/authorization and upload traces demonstrate the boundary. | `apps/mobile/e2e/raw-recordings.spec.ts:1332` — raw upload selection is explicit per file and local-only, expired or revoked recordings cannot join a check upload<br>`apps/mobile/tests/raw-export.test.ts:148` — server boundary terms remain bounded and optional sources cannot inherit recording consent or broaden selection | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### SEC-004 — Protected transport and storage MUST use approved encryption and secret management; secrets MUST NOT be embedded in app or firmware source.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `SEC-004`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-SEC-004-01 | Owner acceptance evidence — Deployment configuration and access review satisfy G-12. | `apps/mobile/e2e/raw-recordings.spec.ts:1253` — actual raw export component keeps every source and separate acknowledgment off until exact purpose review, then resets for another owner<br>`services/api/tests/test_security.py:92` — test_binding_challenge_is_single_use_and_owner_scoped | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### SEC-005 — Raw optical/cardiac retention MUST be justified, minimized, access-controlled, and bound to a defined retention/deletion policy.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `SEC-005`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-SEC-005-01 | Owner acceptance evidence — G-12 states durations and tests deletion across primary/backup workflows. | `apps/mobile/tests/raw-recordings.test.ts:21` — actual Python raw_status envelope verifies complete policy, exact UTF-8 notice, separate receipt and upload/retention states<br>`services/api/tests/test_raw_export.py:319` — test_expiry_and_retention_are_hard_caps_and_generation_deletion_denies | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### SEC-006 — Logs MUST omit raw health payloads and direct identifiers; audit events MUST still preserve actor, operation, record identity, and time.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `SEC-006`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-SEC-006-01 | Owner acceptance evidence — Representative failure logs pass content review. | `apps/mobile/e2e/raw-recordings.spec.ts:1253` — actual raw export component keeps every source and separate acknowledgment off until exact purpose review, then resets for another owner<br>`apps/mobile/tests/raw-recordings.test.ts:37` — raw policy or notice substitution, wrong owner, unknown data and inconsistent immutable receipt fail closed | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### SEC-007 — Security incidents, lost devices, withdrawal, and data correction MUST have defined operational procedures before participant use.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `SEC-007`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-SEC-007-01 | Owner acceptance evidence — Tabletop exercise and responsible contacts documented. | `apps/mobile/tests/raw-recordings.test.ts:37` — raw policy or notice substitution, wrong owner, unknown data and inconsistent immutable receipt fail closed<br>`services/api/tests/test_security.py:92` — test_binding_challenge_is_single_use_and_owner_scoped | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### OPS-001 — The backend MUST begin as a modular FastAPI application with PostgreSQL; approved raw artifacts MUST use private object storage.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `OPS-001`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-OPS-001-01 | Owner acceptance evidence — Architecture review confirms boundaries and deployment configuration. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | NOT_RUN: no matching assertion found; execute the linked fixture/manual procedure with its full expected conditions and retain evidence, or implement a meaningful automated test. |

### OPS-002 — Session submission MUST be idempotent; retries MUST not duplicate specimens, tasks, or finalized results.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `OPS-002`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-OPS-002-01 | Owner acceptance evidence — Repeated identical submissions produce one accepted logical record. | `apps/mobile/tests/sync.test.ts:340` — repeated unconfirmed export click retains one durable operation identity | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### OPS-003 — Finalized sample/task records MUST be immutable; corrections MUST create linked superseding versions.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `OPS-003`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-OPS-003-01 | Owner acceptance evidence — Correction scenario preserves original content and provenance. | `services/api/tests/test_api.py:212` — test_finalized_records_reject_rewrites<br>`apps/mobile/tests/generation-cache.test.ts:90` — unknown current generation invalidates every cached export but preserves deletion reconciliation evidence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### OPS-004 — Cross-device timestamps MUST use RFC 3339 UTC with explicit clock uncertainty; within-device timing MUST use monotonic milliseconds.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `OPS-004`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-OPS-004-01 | Owner acceptance evidence — Clock-drift and reordered-message cases retain interpretable timing. | `apps/mobile/tests/generation-cache.test.ts:240` — a fresh all-device export after retirement contains no prior current demographic or use context<br>`apps/mobile/tests/sync.test.ts:253` — explicit upload registers evidence then snapshot then finalizes and verifies result | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `3339`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### OPS-005 — Offline behavior MUST preserve session state securely where permitted and reconcile explicitly; no unreceived result may appear complete.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `OPS-005`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-OPS-005-01 | Owner acceptance evidence — Network interruption and restart exercises preserve correct terminal state. | `infra/test/test_recovery.py:44` — test_complete_before_acceptance_and_subject_collision_fail<br>`apps/mobile/tests/sync.test.ts:253` — explicit upload registers evidence then snapshot then finalizes and verifies result | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### OPS-006 — Research deployments MUST define backups, restore verification, monitoring, incident ownership, and availability targets.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `OPS-006`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-OPS-006-01 | Owner acceptance evidence — G-12 documents values and a successful recovery exercise. | `infra/test/test_maintenance.py:57` — test_restore_requires_full_argv_and_recovery_environment | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### VAL-001 — Participant work MUST require an approved protocol, eligibility rules, consent, and appropriate research oversight before collection.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `VAL-001`.

Prerequisites and limits: BLOCKED external: G-07 real approved protocol, eligibility/consent/oversight and staff readiness. Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-VAL-001-01 | Owner acceptance evidence — G-07 authorization and staff readiness records. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### VAL-002 — Reference outcomes MUST be independent of predictor tasks and chemical positivity; assessor blinding and timing MUST be specified.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `VAL-002`.

Prerequisites and limits: BLOCKED external: Independent endpoint manual, blinding and timing evidence; no circular predictor labels. Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-VAL-002-01 | Owner acceptance evidence — Outcome manual and data-flow review exclude circular labels. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### VAL-003 — Sample size MUST follow the endpoint, required precision, repeated-measure structure, intended subgroups, and planned error thresholds.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `VAL-003`.

Prerequisites and limits: BLOCKED external: G-08 named statistical expert approves sample size/precision/repeated-measures/subgroup plan. Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-VAL-003-01 | Owner acceptance evidence — Approved calculation/simulation at G-08; no arbitrary sample guarantee. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### VAL-004 — Validation MUST examine route, use frequency, co-use/confounding conditions, supported devices, baseline availability, and intended population limits.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `VAL-004`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-VAL-004-01 | Owner acceptance evidence — Prespecified strata and exclusions appear in the final report. | `services/api/tests/test_model_evaluation.py:414` — test_subgroups_reconcile_all_rows_and_predictive_values_are_prevalence_qualified | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### VAL-005 — Reports MUST include sensitivity/specificity when an accepted reference standard supports them, otherwise positive/negative percent agreement; include calibration, uncertainty intervals, appropriately qualified prevalence-dependent predictive values, and inconclusive/invalid rates.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `VAL-005`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-VAL-005-01 | Owner acceptance evidence — Independent report reconciles every enrolled check with its disposition. | `services/api/tests/test_model_evaluation.py:414` — test_subgroups_reconcile_all_rows_and_predictive_values_are_prevalence_qualified<br>`services/api/tests/test_operator_governance.py:798` — test_actual_postgresql_retirement_waits_for_current_reference_acceptance_transaction | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### VAL-006 — Confirmatory validation MUST use a locked pipeline and independent prospective or external evaluation appropriate to the claim.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `VAL-006`.

Prerequisites and limits: BLOCKED external: G-09 genuine independent prospective/external locked evaluation. Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-VAL-006-01 | Owner acceptance evidence — G-09 report states independence, limitations, and deviations. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### VAL-007 — The complete one-sample/one-task workflow MUST be evaluated using information available at each real check, even when a visit contains repeated research checks.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `VAL-007`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-VAL-007-01 | Owner acceptance evidence — Temporal audit and study report demonstrate the consumer information boundary. | `services/api/tests/test_model_evaluation.py:331` — test_report_cannot_rebind_tampered_training_plans_or_temporal_order<br>`services/api/tests/test_operator_governance.py:360` — test_real_session_start_requires_current_approved_study_and_exact_protocol | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### VAL-008 — The intended use and applicable device, laboratory, privacy, and study requirements MUST be determined by the responsible experts before release.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `VAL-008`.

Prerequisites and limits: BLOCKED external: G-14 responsible regulatory/privacy/laboratory/study applicability determination. Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-VAL-008-01 | Owner acceptance evidence — G-14 documented applicability determination and required evidence. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### BUS-001 — US$20/month MUST be labeled a hypothesis until hardware terms, consumable allowance, and recurring costs are specified.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `BUS-001`.

Prerequisites and limits: BLOCKED external: Dated commercial copy review; US$20/month remains a hypothesis.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-BUS-001-01 | Owner acceptance evidence — Commercial material avoids an unverified price/performance promise. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `20`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### BUS-002 — Economic scenarios MUST include consumables, reader yield, calibration, support, warranty, shipping, cloud operation, studies, and applicable compliance.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `BUS-002`.

Prerequisites and limits: BLOCKED external: G-13 dated supplier quotations and complete lifecycle economic scenarios; cloud arithmetic is only a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-BUS-002-01 | Owner acceptance evidence — Dated cost model with supplier quotations and sensitivity analysis. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### BUS-003 — Final feature inclusion SHOULD consider incremental predictive value, completion burden, and lifecycle cost together.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `BUS-003`.

Prerequisites and limits: BLOCKED external: Product decision citing real ablation, usability burden and lifecycle cost evidence.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-BUS-003-01 | Owner acceptance evidence — Product decision cites ablation, usability, and cost evidence. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### DOC-001 — Documentation MUST distinguish implemented code, synthetic demonstration, proposed design, evidence, and unresolved work.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `DOC-001`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-DOC-001-01 | Owner acceptance evidence — Repository review finds no unsupported completion claim. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | NOT_RUN: no matching assertion found; execute the linked fixture/manual procedure with its full expected conditions and retain evidence, or implement a meaningful automated test. |

### DOC-002 — Every gate MUST have an assigned person before closure and linked evidence; a role label alone is insufficient to close it.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `DOC-002`.

Prerequisites and limits: BLOCKED external: Named actual human gate approver, date, artifact and decision; role labels cannot close scientific gates.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-DOC-002-01 | Owner acceptance evidence — Gate register contains approver, date, artifact, and decision. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | BLOCKED: named external owner supplies real acceptance evidence; software checks cannot close this criterion. |

### DOC-003 — Normative changes MUST update dependent contracts, decisions, requirements, and verification evidence in one reviewed change.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `DOC-003`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-DOC-003-01 | Owner acceptance evidence — Change-impact checklist and versioned repository history. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | NOT_RUN: no matching assertion found; execute the linked fixture/manual procedure with its full expected conditions and retain evidence, or implement a meaningful automated test. |

### PRD-001 — A valid consumer-format check MUST require one saliva collection and one continuous reaction task. Multiple channels may be measured from that collection.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-001`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-001-01 | PRD acceptance review — \| PRD-001 \| A valid consumer-format check MUST require one saliva collection and one continuous reaction task. Multiple channels may be measured from that collection. \| | `services/api/tests/test_report_revisions.py:919` — test_saliva_free_finalized_check_lists_no_revisions_and_preserves_null_collection<br>`apps/mobile/tests/export-projection.test.ts:96` — an unmounted invalid native arm may omit acquired native evidence but valid prototype task cannot | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-002 — The check MUST also support guided pupil capture and resting heart-rate capture; ECG MUST remain an exploratory input until its incremental value and hardware approach are justified.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-002`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-002-01 | PRD acceptance review — \| PRD-002 \| The check MUST also support guided pupil capture and resting heart-rate capture; ECG MUST remain an exploratory input until its incremental value and hardware approach are justified. \| | `services/api/tests/test_cardiac_interval_governance.py:145` — test_required_channel_scope_is_heart_rate_only<br>`apps/mobile/e2e/raw-recordings.spec.ts:1253` — actual raw export component keeps every source and separate acknowledgment off until exact purpose review, then resets for another owner | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-003 — P0 and P1 MUST produce measurement-only outputs, never an intoxication probability.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-003`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-003-01 | PRD acceptance review — \| PRD-003 \| P0 and P1 MUST produce measurement-only outputs, never an intoxication probability. \| | `services/api/tests/test_api.py:197` — test_end_to_end_measurement_only_and_owner_isolation | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-004 — A P2 probability MUST require an authorized research session, an `active_research` model, a compatible feature contract, and all model-required valid channels.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-004`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-004-01 | PRD acceptance review — \| PRD-004 \| A P2 probability MUST require an authorized research session, an `active_research` model, a compatible feature contract, and all model-required valid channels. \| | `apps/mobile/e2e/raw-recordings.spec.ts:1400` — actual service component labels conditional approved channels and model support, while the fictional build refuses both<br>`services/api/tests/test_cardiac_authority.py:277` — test_actual_artifact_not_just_required_channels_is_hr_only | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-005 — The future impairment endpoint, intended population, operating threshold, and acceptable error rates MUST be selected before confirmatory evaluation.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-005`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-005-01 | PRD acceptance review — \| PRD-005 \| The future impairment endpoint, intended population, operating threshold, and acceptable error rates MUST be selected before confirmatory evaluation. \| | `apps/mobile/tests/profile-form.test.ts:117` — known last-use rejects impossible calendar dates and future times with a field error<br>`apps/mobile/e2e/raw-recordings.spec.ts:913` — laboratory method review pins the actual selected method without BLE and resets acknowledgement on document replacement | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-006 — A model result MUST NOT be presented as proof of cannabis causation, a legal determination, or clearance to drive.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-006`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-006-01 | PRD acceptance review — \| PRD-006 \| A model result MUST NOT be presented as proof of cannabis causation, a legal determination, or clearance to drive. \| | `apps/mobile/tests/research-result.test.ts:144` — actual Python data-only engine interoperability result verifies immutable proof and named historical research endpoint<br>`services/api/tests/test_model_engine.py:437` — test_training_evaluation_policy_and_result_proof_are_bound | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-007 — The product MUST retain distinct invalid, inconclusive, measurement-only, and research-estimate outcomes. Missing information MUST NOT be interpreted as a normal measurement.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-007`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-007-01 | PRD acceptance review — \| PRD-007 \| The product MUST retain distinct invalid, inconclusive, measurement-only, and research-estimate outcomes. Missing information MUST NOT be interpreted as a normal measurement. \| | `apps/mobile/tests/domain.test.ts:323` — every research_estimate is rejected even when its shape could be schema-valid<br>`services/api/tests/test_api.py:429` — test_current_research_estimate_rejected_from_history | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-008 — Alcohol MUST remain a separately measured and separately reported channel; cannabis physiology MUST NOT substitute for a breath-alcohol measurement.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-008`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-008-01 | PRD acceptance review — \| PRD-008 \| Alcohol MUST remain a separately measured and separately reported channel; cannabis physiology MUST NOT substitute for a breath-alcohol measurement. \| | `apps/mobile/tests/export-projection.test.ts:29` — every retained simulated sample, eye, PPG and separate alcohol projection satisfies its exact typed evidence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-009 — Standardized session orchestration

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-009`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-009-01 | PRD acceptance review — \| PRD-009 \| Standardized session orchestration \| P0 MUST establish a complete synthetic workflow with unique attempts, timestamps, quality, and terminal states. \| | `apps/mobile/tests/raw-recordings.test.ts:21` — actual Python raw_status envelope verifies complete policy, exact UTF-8 notice, separate receipt and upload/retention states<br>`infra/test/test_recovery.py:44` — test_complete_before_acceptance_and_subject_collision_fail | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-010 — Quantitative saliva interface

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-010`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-010-01 | PRD acceptance review — \| PRD-010 \| Quantitative saliva interface \| P1 MUST establish reliable specimen handling and a reference-laboratory comparison before any portable concentration claim. \| | `apps/mobile/e2e/raw-recordings.spec.ts:965` — specimen form records actual quantities, explicit unknowns and handling while offering no participant concentration entry<br>`apps/mobile/tests/acquisition.test.ts:870` — reference laboratory collection has no BLE acquisition, persists a recoverable pending draft, imports separate analysis then permits explicit finalization | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-011 — Parent THC channel

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-011`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-011-01 | PRD acceptance review — \| PRD-011 \| Parent THC channel \| P1 MUST evaluate delta-9 THC first. Selection of additional channels requires analytical feasibility and added-value evidence. \| | `apps/mobile/e2e/raw-recordings.spec.ts:1104` — actual raw choices component defaults both optional purposes off and requires exact policy review before a separate local/upload choice<br>`services/api/tests/test_lab_handoff.py:304` — test_import_rejects_forged_or_incompatible_analytical_evidence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-012 — Additional saliva metabolites

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-012`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-012-01 | PRD acceptance review — \| PRD-012 \| Additional saliva metabolites \| THC-COOH and 11-OH-THC SHOULD be investigated; neither is promised as a functional cartridge channel in v0.1.0. \| | `apps/mobile/tests/domain.test.ts:222` — synthetic concentrations preserve unknown metabolites as null, with exact pg/mL conversion | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `1.0`, `11`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### PRD-013 — One repeated-trial game

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-013`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-013-01 | PRD acceptance review — \| PRD-013 \| One repeated-trial game \| P0 MUST support the task contract; P2 MUST evaluate reliability and independent predictive value. \| | `apps/mobile/tests/sync.test.ts:340` — repeated unconfirmed export click retains one durable operation identity<br>`services/api/tests/test_cross_language.py:142` — test_host_generated_native_contract_fixture_against_independent_server_scoring | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-014 — Dynamic pupil measurements

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-014`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-014-01 | PRD acceptance review — \| PRD-014 \| Dynamic pupil measurements \| P1/P2 MUST establish acquisition quality, valid units, optical controls, and repeatability before features enter a model. \| | `apps/mobile/tests/cardiac-selection.test.ts:97` — interrupted ECG alternative preserves valid PPG and does not copy its physiological features<br>`services/api/tests/test_operator_governance.py:439` — test_optical_evidence_cannot_relabel_a_different_authorized_attempt_or_acquisition_clock | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-015 — Heart rate and exploratory ECG

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-015`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-015-01 | PRD acceptance review — \| PRD-015 \| Heart rate and exploratory ECG \| Cardiac capture MUST preserve signal quality and context; an ECG-only benefit MUST be measured by ablation. \| | `services/api/tests/test_cardiac_interval_governance.py:145` — test_required_channel_scope_is_heart_rate_only<br>`apps/mobile/e2e/raw-recordings.spec.ts:519` — eye and ECG descriptions follow the approved observation and actual provenance without claiming measured light onset | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-016 — Profile and use history

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-016`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-016-01 | PRD acceptance review — \| PRD-016 \| Profile and use history \| The app MUST preserve source, measurement date, units, and unknown values; demographics MUST NOT determine an assumed clearance rate. \| | `apps/mobile/e2e/components.spec.ts:79` — profile fields announce validation, preserve canonical units and guard unsaved edits<br>`apps/mobile/tests/domain.test.ts:131` — profile converts SI units and rejects ranges, relative time and unknown enums | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-017 — Separate alcohol channel

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-017`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-017-01 | PRD acceptance review — \| PRD-017 \| Separate alcohol channel \| The design SHOULD reserve integration capability; alcohol performance claims require a calibrated breath system and dedicated validation. \| | `apps/mobile/tests/export-projection.test.ts:29` — every retained simulated sample, eye, PPG and separate alcohol projection satisfies its exact typed evidence<br>`apps/mobile/e2e/raw-recordings.spec.ts:1104` — actual raw choices component defaults both optional purposes off and requires exact policy review before a separate local/upload choice | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-018 — Versioned research dataset

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-018`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-018-01 | PRD acceptance review — \| PRD-018 \| Versioned research dataset \| P2 MUST support reconstruction of the exact specimen, task, device, calibration, feature, and model versions. \| | `apps/mobile/e2e/raw-recordings.spec.ts:1400` — actual service component labels conditional approved channels and model support, while the fictional build refuses both<br>`apps/mobile/tests/service-boundary.test.ts:70` — research result format advertisement supports only the versioned reader and grants no inference authority | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-019 — Quality-aware research result

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-019`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-019-01 | PRD acceptance review — \| PRD-019 \| Quality-aware research result \| Inference MUST enforce the release manifest and required-channel rules without fallback to an incompatible model. \| | `apps/mobile/tests/service-boundary.test.ts:70` — research result format advertisement supports only the versioned reader and grants no inference authority<br>`services/api/tests/test_raw_export.py:205` — test_distinct_submit_review_release_required | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-020 — Understandable session feedback

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-020`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-020-01 | PRD acceptance review — \| PRD-020 \| Understandable session feedback \| The app MUST distinguish capture success, analysis availability, and a research prediction. \| | `apps/mobile/e2e/mobile.spec.ts:6` — guest completes a measurement-only check, exact export and privacy/settings journey | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-029 — A person can enter guest practice or authenticate, recover an interrupted sign-in, refresh safely and sign out with truthful remote-revocation status. Environment/account partitions and retained signed-out data stay isolated.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-029`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-029-01 | PRD acceptance review — \| PRD-029 \| A person can enter guest practice or authenticate, recover an interrupted sign-in, refresh safely and sign out with truthful remote-revocation status. Environment/account partitions and retained signed-out data stay isolated. \| SEC-002/004/007; AND-ONB-001–006; AND-AUTH-001–007; AND-ENV-001/002 \| | `apps/mobile/tests/controller.test.ts:353` — delayed history cannot enter another account or reopen a signed-out workspace<br>`services/api/tests/test_local_identity.py:250` — test_refresh_rotation_preserves_auth_time_and_family_and_revocation_blocks_new_tokens | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `002`, `004`, `006`, `007`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### PRD-030 — An invited eligible account can review exact study consent and current channel availability; sign-in, age, a guessed study ID or a checkbox cannot create research authority. Withdrawal stops local study work immediately and preserves its durable receipt.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-030`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-030-01 | PRD acceptance review — \| PRD-030 \| An invited eligible account can review exact study consent and current channel availability; sign-in, age, a guessed study ID or a checkbox cannot create research authority. Withdrawal stops local study work immediately and preserves its durable receipt. \| SEC-002/003; MOD-008–010; AND-STUDY-001–006; PAI-001–008 \| | `apps/mobile/tests/controller.test.ts:107` — explicit study consent is durable before upload and a lost receipt retries the original timestamp and request identity<br>`apps/mobile/tests/sync.test.ts:19` — a queued receipt commit cannot revive consent when withdrawal publishes before its serialized callback | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `003`, `006`, `008`, `010`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### PRD-031 — A check freezes its confirmed optional profile/context, one-sample/one-task information boundary, original target, all attempts and selected evidence. Interruptions and linked replacements preserve original records.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-031`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-031-01 | PRD acceptance review — \| PRD-031 \| A check freezes its confirmed optional profile/context, one-sample/one-task information boundary, original target, all attempts and selected evidence. Interruptions and linked replacements preserve original records. \| ANA-001/012; APP-001–008; OPS-002–005; AND-PRO-001–007; AND-CHECK-001–008 \| | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload<br>`services/api/tests/test_model_evaluation.py:312` — test_same_check_observations_and_later_assay_delivery_preserve_original_target | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `005`, `007`, `008`, `012`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### PRD-032 — Native reaction acquisition preserves deterministic practice/scored schedules, actual native events, missingness and immediate stop behavior; build success and clock resolution do not establish physical timing qualification.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-032`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-032-01 | PRD acceptance review — \| PRD-032 \| Native reaction acquisition preserves deterministic practice/scored schedules, actual native events, missingness and immediate stop behavior; build success and clock resolution do not establish physical timing qualification. \| APP-004–008/014; AND-TASK-001–008; G-06 \| | `apps/mobile/tests/export-evidence.test.ts:207` — host-generated native golden is fully checked without claiming a physical acquisition<br>`apps/mobile/tests/eye-acquisition.test.ts:230` — feature-only optical Start follows context, attempt and fresh grant; native completion saves locally with a separate actual acquisition clock | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `008`, `014`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### PRD-033 — Device discovery, verified binding and fresh scoped starts distinguish a working connection from a qualified channel. Protected BLE, actual adapter inventory, quality, cancellation and replay/origin fences apply to conditional reader capture.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-033`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-033-01 | PRD acceptance review — \| PRD-033 \| Device discovery, verified binding and fresh scoped starts distinguish a working connection from a qualified channel. Protected BLE, actual adapter inventory, quality, cancellation and replay/origin fences apply to conditional reader capture. \| HW-003/004/007/012; SEC-004; AND-DEV-001–008; CAN-SR-001–011; VPPG-001–007 \| | `apps/mobile/tests/acquisition.test.ts:1101` — binding reconnect reconciles old receipt then requires a new device proof in the current connection<br>`apps/mobile/src/device/tests/physical.test.ts:550` — actual framed signed test peripheral requires verified binding before authorized capture | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `004`, `007`, `008`, `011`, `012`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### PRD-034 — Saliva collection/import, optical capture and selected PPG/exploratory ECG have explicit pending, unavailable, invalid and permitted retry paths. Declarations, approved software and signatures do not qualify an assay, optics, electrical setup or sensor.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-034`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-034-01 | PRD acceptance review — \| PRD-034 \| Saliva collection/import, optical capture and selected PPG/exploratory ECG have explicit pending, unavailable, invalid and permitted retry paths. Declarations, approved software and signatures do not qualify an assay, optics, electrical setup or sensor. \| ANA-001–012; HW-005–009; APP-009/010; AND-SAL-001–007; SALCOL-001–008; AND-EYE-001–007/101–106; AND-HR-001–007; AND-ECG-001–007 \| | `apps/mobile/tests/export-evidence.test.ts:354` — executed software-only saliva, PPG and ECG transcript exports reject rehashed clock/replay/identity tampering<br>`apps/mobile/tests/participant-acquisition.test.ts:257` — document digest, selected method, exact UUID/calendar and electrical setup boundaries are enforced | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `007`, `008`, `009`, `010`, `012`, `101`, `106`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### PRD-035 — Protected local save precedes a separate explicit account upload; restart, lost receipts, bounded retry and conflicts preserve ownership, original times and immutable evidence. Permission failures and retired generations cannot be repaired by automatic reupload.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-035`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-035-01 | PRD acceptance review — \| PRD-035 \| Protected local save precedes a separate explicit account upload; restart, lost receipts, bounded retry and conflicts preserve ownership, original times and immutable evidence. Permission failures and retired generations cannot be repaired by automatic reupload. \| SEC-003/004; OPS-002–005; AND-SYNC-001–007; AND-CHECK-006; shared contracts §§2–5 \| | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload<br>`apps/mobile/e2e/raw-recordings.spec.ts:1332` — raw upload selection is explicit per file and local-only, expired or revoked recordings cannot join a check upload | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `004`, `005`, `007`, `2`, `5`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### PRD-036 — History/results show the actual scientific state separately from delivery, preserve qualifiers and old acquisition times, and navigate immutable original/replacement and same-specimen report-revision lineage.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-036`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-036-01 | PRD acceptance review — \| PRD-036 \| History/results show the actual scientific state separately from delivery, preserve qualifiers and old acquisition times, and navigate immutable original/replacement and same-specimen report-revision lineage. \| APP-012/013; MOD-013; AND-HIST-001–007; AND-RES-001–007; report-revision and replacement-links contracts \| | `apps/mobile/tests/participant-acquisition.test.ts:87` — actual Python protocol, immutable acknowledgement, specimen and imported report preserve separate truthful lineage<br>`services/api/tests/test_replacement_links.py:69` — test_bidirectional_links_are_direct_frozen_and_bound_to_acquisition_times | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `007`, `013`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### PRD-037 — Optional eye/ECG recording and upload default off, have distinct reviewed purposes, retain exact receipts and expire under original retention deadlines. Revocation stops capture before cleanup; pending quarantine/cleanup is visible.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-037`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-037-01 | PRD acceptance review — \| PRD-037 \| Optional eye/ECG recording and upload default off, have distinct reviewed purposes, retain exact receipts and expire under original retention deadlines. Revocation stops capture before cleanup; pending quarantine/cleanup is visible. \| SEC-003–005; AND-RAW-001–007; AND-EYE-006/106; AND-ECG-007; raw-recording-retention contract \| | `apps/mobile/e2e/raw-recordings.spec.ts:1104` — actual raw choices component defaults both optional purposes off and requires exact policy review before a separate local/upload choice<br>`apps/mobile/tests/raw-recordings.test.ts:77` — default off, local-only opt-in, upload dependency, policy expiry and pending stop fences remain distinct | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `005`, `007`, `106`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### PRD-038 — The owner can create a bounded exact-scope structured export, optionally include separately authorized retained raw sources, verify and deliberately share it. Downloads require current authority; expiration, revocation and temporary-file cleanup remain explicit.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-038`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-038-01 | PRD acceptance review — \| PRD-038 \| The owner can create a bounded exact-scope structured export, optionally include separately authorized retained raw sources, verify and deliberately share it. Downloads require current authority; expiration, revocation and temporary-file cleanup remain explicit. \| SEC-002/005/007; AND-EXP-001–007; RAW-EXP-001–008; AND-RAW-008 \| | `apps/mobile/e2e/raw-recordings.spec.ts:1297` — expired or unselected raw export sources remain unavailable while structured export stays separate<br>`apps/mobile/tests/raw-export.test.ts:65` — actual authenticated Python scope, completed job and worker ZIP verify exact independent raw authority and versioned binary sources | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `005`, `007`, `008`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### PRD-039 — Local clear, cloud-data deletion, account deletion and withdrawal show distinct scopes and honest asynchronous receipts. Generation barriers and independent retained recovery evidence prevent resurrection; study recovery requires fresh independent reapproval and participant consent.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-039`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-039-01 | PRD acceptance review — \| PRD-039 \| Local clear, cloud-data deletion, account deletion and withdrawal show distinct scopes and honest asynchronous receipts. Generation barriers and independent retained recovery evidence prevent resurrection; study recovery requires fresh independent reapproval and participant consent. \| SEC-005/007; OPS-003–006; AND-PRIV-001–007; RECOVERY-001/002; platform contract \| | `services/api/tests/test_recovery_scopes.py:89` — test_fresh_registry_reapproval_seal_allows_only_exact_study_and_new_consent<br>`apps/mobile/tests/generation-cache.test.ts:34` — generation quarantine clears cached history, selections and consent without discarding exact deletion receipts | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `002`, `006`, `007`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### PRD-040 — Instructions, navigation, errors and privacy controls support specified Android/iOS accessibility and permission recovery. Changes to timed-task presentation/input retain their separate compatibility and qualification boundary.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-040`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-040-01 | PRD acceptance review — \| PRD-040 \| Instructions, navigation, errors and privacy controls support specified Android/iOS accessibility and permission recovery. Changes to timed-task presentation/input retain their separate compatibility and qualification boundary. \| APP-014; AND-SET-001–007 and feature-specific parity requirements; shared contracts §9 \| | `infra/test/test_hosted_preview.py:107` — test_ios_and_android_bundles_are_inspected<br>`services/api/tests/test_cardiac_authority.py:255` — test_shared_exact_interval_arithmetic_nonzero_margin_and_inclusive_boundary | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `007`, `9`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### PRD-041 — Independently governed operator releases can admit the exact conditional research software, including only explicitly approved model variants and baseline scope. Measurement-only remains default; the restricted HR-only evaluation mode discloses absent multimodal comparisons.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-041`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-041-01 | PRD acceptance review — \| PRD-041 \| Independently governed operator releases can admit the exact conditional research software, including only explicitly approved model variants and baseline scope. Measurement-only remains default; the restricted HR-only evaluation mode discloses absent multimodal comparisons. \| MOD-001–015; VAL-001–007; OPERATOR-AUTHORITY-001–009; MODEL-001–006; EVAL-001–008 as modified; HR-AUTH-001–008 \| | `apps/mobile/e2e/raw-recordings.spec.ts:1400` — actual service component labels conditional approved channels and model support, while the fictional build refuses both<br>`services/api/tests/test_raw_export.py:234` — test_metadata_only_request_remains_default_scope_and_cannot_carry_raw_approval | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `006`, `007`, `008`, `009`, `015`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### PRD-042 — Isolated fictional previews and reviewable local/QA/prod/store delivery tooling preserve exact source/artifact identity, environment and uncertain outcomes. Prepared software, submitted artifacts, hosted access, public availability and scientific qualification remain separate evidence.

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-042`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-042-01 | PRD acceptance review — \| PRD-042 \| Isolated fictional previews and reviewable local/QA/prod/store delivery tooling preserve exact source/artifact identity, environment and uncertain outcomes. Prepared software, submitted artifacts, hosted access, public availability and scientific qualification remain separate evidence. \| HW-002; SEC-001/004; OPS-001–006; AND-ENV-001–007; AND-PREV-001–003; WEB-DEP-001–010; CLOUD-DEP-001–011; PREVIEW-001–003; STORE-001–018 \| | `apps/mobile/tests/hosted-preview.test.ts:11` — hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service<br>`services/api/tests/test_mobile_store_release.py:406` — test_actual_submission_receipt_never_means_public_store_availability | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `003`, `004`, `006`, `007`, `010`, `011`, `018`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### PRD-021 — Analytical usefulness

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-021`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-021-01 | PRD acceptance review — \| PRD-021 \| Analytical usefulness \| Compare each intended cartridge channel with a traceable reference method over a prespecified range, including censored and invalid results. Freeze acceptance limits before qualification. \| | `infra/test/test_web_deployment.py:469` — test_production_requires_results_reference_separate_from_artifact_binding<br>`apps/mobile/e2e/raw-recordings.spec.ts:913` — laboratory method review pins the actual selected method without BLE and resets acknowledgement on document replacement | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-022 — Independent prediction value

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-022`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-022-01 | PRD acceptance review — \| PRD-022 \| Independent prediction value \| Compare chemistry alone, app signals alone, and the combined model against the same independent outcome. Require evidence of useful incremental benefit. \| | `services/api/tests/test_cross_language.py:142` — test_host_generated_native_contract_fixture_against_independent_server_scoring<br>`apps/mobile/src/device/tests/signal.test.ts:20` — clean PPG and ECG require every batch before transport completion; the visible ring does not replace full evidence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-023 — Single-check usability

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-023`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-023-01 | PRD acceptance review — \| PRD-023 \| Single-check usability \| Measure completion rate, duration distribution, retries, specimen failures, camera failures, and task interruptions using the intended workflow. \| | `services/api/tests/test_cardiac_authority.py:347` — test_signed_sdk_duration_uses_reviewed_rate_error_and_exact_unrounded_custody_bound<br>`apps/mobile/tests/acquisition.test.ts:1032` — unknown specimen receipt retries the immutable declaration and key; explicit analysis cancellation never erases collection | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-024 — Generalization

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-024`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-024-01 | PRD acceptance review — \| PRD-024 \| Generalization \| Report errors and calibration for held-out people, later sessions, supported devices, consumption routes, use-frequency strata, and first-use versus personalized modes. \| | `services/api/tests/test_model_evaluation.py:354` — test_later_validation_without_prior_held_out_session_and_single_class_cohort_fail<br>`services/api/tests/test_model_evaluation_cardiac.py:214` — test_held_out_hr_values_and_outcomes_cannot_affect_training | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-025 — Operational reliability

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-025`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-025-01 | PRD acceptance review — \| PRD-025 \| Operational reliability \| Measure record completeness, upload reconciliation, recovery after interruption, and traceability of finalized results. \| | `apps/mobile/e2e/raw-recordings.spec.ts:1104` — actual raw choices component defaults both optional purposes off and requires exact policy review before a separate local/upload choice<br>`services/api/tests/test_raw_retention.py:488` — test_upload_without_record_and_duplicate_revoke_are_invalid | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-026 — Economic feasibility

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-026`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-026-01 | PRD acceptance review — \| PRD-026 \| Economic feasibility \| Build usage-based cost scenarios before selecting subscription allowances or promising a hardware subsidy. \| | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | NOT_RUN: no matching assertion found; execute the linked fixture/manual procedure with its full expected conditions and retain evidence, or implement a meaningful automated test. |

### PRD-027 — Freeze intended use, primary impairment outcome, population, thresholds, and collection-to-result interval

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-027`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-027-01 | PRD acceptance review — \| PRD-027 \| Freeze intended use, primary impairment outcome, population, thresholds, and collection-to-result interval \| Clinical and product leads, with statistical lead \| P2 confirmatory evaluation and all P3 claims \| | `services/api/tests/test_model_engine.py:437` — test_training_evaluation_policy_and_result_proof_are_bound<br>`services/api/tests/test_cardiac_interval_governance.py:101` — test_collection_only_proof_cannot_qualify_server_interval | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PRD-028 — Select collection/cartridge chemistry, cardiac implementation, optical protocol, supported phone list, final retention policy, and subscription allowance

Normative acceptance source: `specs/FULL_SPECIFICATION.md` / `PRD-028`. Also bind the individually expanded PRD row in `specs/PRD.md`.

Prerequisites and limits: Independent study/model/endpoint authorization and genuine scientific dataset evidence remain separate; engineering fixtures cannot establish validity.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-001-PRD-028-01 | PRD acceptance review — \| PRD-028 \| Select collection/cartridge chemistry, cardiac implementation, optical protocol, supported phone list, final retention policy, and subscription allowance \| Respective analytical, hardware, optical, app, data, and commercial leads \| Respective feasibility and release gates \| | `apps/mobile/e2e/raw-recordings.spec.ts:1104` — actual raw choices component defaults both optional purposes off and requires exact policy review before a separate local/upload choice<br>`services/api/tests/test_raw_export.py:205` — test_distinct_submit_review_release_required | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

### EVAL-007 history/reference/authenticity audit

Mapped existing cases: OTGD-008-EVAL-007-01/02; OTGD-041-EVAL-002-03/04/05; OTGD-042-HR-AUTH-008-01/02/03/04; full MOD-004/005/012/014/015 and VAL-004/005/006 are related, not automatically closed.

Assertion adequacy inspected: Independently read test_model_evaluation.py::external_history_pipeline/assert_forged_history_refused and both named test_external_history_references_remain_unverified_through_pipeline/test_self_asserted_or_extra_approval_fields_do_not_authenticate_history wrappers in full and four HR variants. Actual CLI index/freeze/train/evaluate/verify compares original dataset/analysis/split/training/report/artifact hashes, full evidence and eight-row evaluation membership. Original refs and HR custody/source/baseline/manifest remain exact. Every emitted authority/authenticity/history/clinical flag is false; strict extra fields and untyped/rehashed forged manifest refuse. Existing test_real_logistic_fitting... already asserted verified_by_tool false: the original V-SW-001 claim is narrowed accordingly.

Remaining limits: No scientific authenticity is established. Focused author-reported execution exists, but raw pytest stdout/JUnit is not linked; no final-candidate PASS adopted. These checks cover history custody; independent endpoint, genuine approvals and locked real study remain separate.

### Alcohol dependency and acquisition-boundary audit

Mapped existing cases: OTGD-019-AND-ALC-001-02, AND-ALC-004-02; related AND-DEV-004, AND-CHECK-002, AND-STUDY-003/004.

Assertion adequacy inspected: Read operator-governance tests: configuration/calibration at -1ms, equality and +1ms; expiry history/body/hash/decisions immutable; calibration failure distinguished from still-current configuration. Current SOFTWARE_ADAPTERS/PHYSICAL_DRIVERS contain no alcohol entry and capability reason is HUMAN_ADAPTER_UNIMPLEMENTED. Four explicitly hypothetical HTTP grant/start cases expire before still-valid grant end, require403 APPROVED_REGISTRY_VERSION_REQUIRED, zero sign_start calls, no persisted start/alcohol and unchanged issued receipt. Mobile three new cases verify strict configuration selection before expiry, fresh absent inventory overrides stale cached availability with zero grant/nonce/hardware events, and a hypothetical returned authoritative-start refusal leaves invalid null alcohol and zero acquisition events.

Remaining limits: Client refusal transport is controlled, not an integrated real breath instrument. No qualified driver exists. Direct participant recalibration-specific start/recovery remains BLOCKED by absent instrument; generic server refusal must not be relabeled a diagnosis. Server -1ms/equality/+1ms and hypothetical grant race have reported focused execution; mobile author report/release and final gates pending.

### Rendered alcohol state/copy assertion audit

Mapped existing cases: OTGD-019-AND-ALC-002/003/005/006 cases; related APP-012/013, AND-HIST-003 and AND-RES-004.

Assertion adequacy inspected: Read actual AlcoholScreen/ResultsScreen/HistoryScreen/ResultDetail fixture and assertions in raw-recordings.spec.ts. Measurement/guest/research variants retain unavailable qualified hardware, mg/L and model-specific co-use copy, replace stale unconditional classification statement. Six value/source variants (zero, low, below_loq, not_detected, invalid, simulated) traverse actual history/result/detail; assertions retain units, qualifier/source/time, dashes for null, separate alcohol meaning and no automatic BAC/impairment adjustment. Positive driving/legal-clearance/combined-score patterns absent; truthful clearance Unavailable remains visible.

Remaining limits: Controlled component inputs are hypothetical reporting records, not acquired sensor data; research fixture is not newly qualified scientific authority. Notification/OS-wide copy is not exhaustively proved by these component surfaces. Writer active; new component tests NOT_RUN in verifier final scope, author final report pending.

### Permissions race and no-reprompt assertion audit

Mapped existing cases: OTGD-036-AND-SET-003-01/02 and AND-SET-007-02; related AND-EYE-002, AND-ONB-004 and AND-AUTH-005.

Assertion adequacy inspected: Read PermissionsCard implementation and actual exported Settings component harness. Status labels cover denied/canAskAgain, denied/permanent, restricted, undetermined, failed reads; zero prompts across mount/refresh/active-return; OS settings call occurs once only explicit action. Deferred reads resolved newer-first, stale controller epoch before React render, account/generation changes and unmount must not publish old state; new scoped card is Not checked until current read; listener teardown asserted. Real ordinary UI test Settings/Back preserves draft/sample with no camera prompt. Implementation uses active+sequence+captured epoch guard and scoped card identity.

Remaining limits: Adapters are controlled OS observations. Real Android/iOS settings return, OS permission policy, TalkBack/VoiceOver, key storage and native lifecycle remain Task7 BLOCKED/NOT_RUN. Writer not released; no final gate execution or independent runtime PASS.

### Current release provenance assertion audit

Mapped existing cases: OTGD-047-STORE-003-01/02; OTGD-015-CLOUD-DEP-002-01/02; related AND-ENV-005/007.

Assertion adequacy inspected: Read verify_github_gates/verify_gate_file and new test_provenance actual assertion bodies. Both current defaults require CURRENT_REQUIRED_JOBS=FARGATE_REQUIRED_JOBS (14), owned HTTP-client recursion retains selected set; tests reject missing/failure/skipped/cancelled fargate-container-runtime, reject base-only gate file, and verify platform build/serverless admission do not reach signing/cloud boundary. Existing exact-run/latest-attempt/duplicate/foreign/pagination checks retained. Explicit historical13 selectors remain only documented original recovery callers; signed historical receipt projection unchanged and cannot replace live admission.

Remaining limits: HTTP response fixtures prove software refusal only. Actual current remote14 mandatory jobs/run provenance and native artifacts remain pending; baseline38347011315 is historical only and normalized PR wrapper is not trusted-main admission. Logs substantiate focused runs but run-time source manifest absent from author report; do not adopt them as exact frozen-candidate result. Canonical infra gate recorded FAIL (Docker readonly buildx setup + then-missing probe import); secure-SDK follow-up not reached.

### Actual-process interruption probe source audit

Mapped existing cases: Shared platform §§6/10; related OPS-002/003/005/006, RAW-EXP-004/006/007, RECOVERY-001, AND-SYNC-003/005/006, AND-PRIV-005, AND-RES-002.

Assertion adequacy inspected: Read worker_interrupt_probe.py validate_target, child_worker, OwnedChild, kill_case, verify_output, stale_case and budget_case. Exact separate disposable local DB/namespace/queues/buckets; wrappers delegate real production claim/commit/S3/SQS/run_job; only owned spawned PID receives signals; SIGKILL exit and actual barriers verified. Five export kill stages plus result after-claim/after-commit; unchanged outbox and winning fence/attempt/output assertions; version-pinned bytes/hash. SIGSTOP lets real120s lease expire; new generation denies stale output; SIGCONT late writer must lease_lost; real expiry cleanup removes only own versions and preserves neighbor. Real malformed durable work five-claim/backoff and actual five-receive120s DLQ redrive preserve production constants.

Remaining limits: Source inspected only; probe and integration WIP, no real process/recovery execution adopted. Unit harness targeting/barrier tests do not prove actual recovery. No study withdrawal or old-backup/cloud restore inferred from generation transaction. PM must assign isolated fixture setup and run after writer release; all resource mutations PM-only. Workflow timeout must fit real production waits; integration pending.

### Authenticated ordinary-web live test source audit

Mapped existing cases: Related actual paths: AND-AUTH-001/003/005/006; AND-SYNC-002/003/004/007; AND-HIST-001/005/006; AND-EXP-001/002/003/006; AND-PRIV-003/004/005; WEB-DEP-003/008; complete full canonical scenarios remain separately assessed.

Assertion adequacy inspected: Read authenticated-live.spec.ts ordinary account test and helpers. Real issuer PKCE/token responses, notice/profile/context and deliberate synthetic-account Save then Upload. route.fetch sends actual finalize and validates202 before connection-reset abort; no fake success. Actual queued measurement-only result, reload clears account memory and reauthentication retrieves server history, actual export job/ZIP manifest/hash/single-check bytes, foreign404, reauthenticated deletion/current generation barrier, explicit new empty workspace and logout refresh-family refusal. Two actual viewport projects and private bounded fixture inventory; unknown records stop all-data deletion. Network receipts redacted; live config disables OAuth/token-bearing traces/HAR/screenshots.

Remaining limits: Writer active; planned final gate NOT_RUN. Current inspected ordinary case does not establish all governed consent/withdrawal, raw, pending-lab or research UI/API journeys; later governed work is WIP. No native encrypted persistence, public CloudFront delivery or physical sensing inferred. Need actual raw JUnit/redacted receipts/archive hashes and final gate wiring after freeze.


## Final corrected source evidence — e89897cc852a

# OTGD-001 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `specs/FULL_SPECIFICATION.md`; SHA256 `c8f052979fd2a15da2d0bc09c8533bde246cdc559d798696af728378cf5850f7`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-001/test-plan.md`. External review artifact only; PM controls import.

All 128 stable cases / 128 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`
- `uv run --project services/api python scripts/ci_gate.py infra-unit`
- `node --import tsx --test --test-reporter=junit test/*.test.ts (cwd: infra)`
- `swift test --package-path apps/mobile/modules/reaction-task --parallel --num-workers 1 --verbose --disable-swift-testing --xunit-output "$PWD/reports/ios-native.xml"`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-001-HW-001-01 | Owner acceptance evidence — BOM and firmware target agree with ADR-004. | PARTIAL |
| OTGD-001-HW-002-01 | Owner acceptance evidence — End-to-end inspection shows no loss or replacement of provenance. | PARTIAL |
| OTGD-001-HW-003-01 | Owner acceptance evidence — Trace a captured record to one reader and firmware build. | PARTIAL |
| OTGD-001-HW-004-01 | Owner acceptance evidence — Controlled fault injection produces explicit recoverable or invalid states. | PASS |
| OTGD-001-HW-005-01 | Owner acceptance evidence — Gate G-05 sign-off and bench evidence precede participant connection. | BLOCKED |
| OTGD-001-HW-006-01 | Owner acceptance evidence — Approved power/connection diagram and documented permitted configurations. | BLOCKED |
| OTGD-001-HW-007-01 | Owner acceptance evidence — Reference signal reconstructs within frozen acquisition tolerances. | BLOCKED |
| OTGD-001-HW-008-01 | Owner acceptance evidence — G-04 defines limits and verifies supported configurations. | BLOCKED |
| OTGD-001-HW-009-01 | Owner acceptance evidence — Reprocess retained permitted data to the same versioned features. | PARTIAL |
| OTGD-001-HW-010-01 | Owner acceptance evidence — Handling review and inspection demonstrate the defined contamination boundary. | BLOCKED |
| OTGD-001-HW-011-01 | Owner acceptance evidence — G-10 approved drawings, duty-cycle measurements, and human-factors results. | BLOCKED |
| OTGD-001-HW-012-01 | Owner acceptance evidence — An expired or incompatible configuration cannot be reported as qualified. | PASS |
| OTGD-001-ANA-001-01 | Owner acceptance evidence — Specimen lineage shows one collection for a valid check. | PASS |
| OTGD-001-ANA-002-01 | Owner acceptance evidence — Approved collection SOP and recovery/stability evidence at G-02. | BLOCKED |
| OTGD-001-ANA-003-01 | Owner acceptance evidence — Channel selection report identifies measured feasibility and unresolved channels. | BLOCKED |
| OTGD-001-ANA-004-01 | Owner acceptance evidence — Prespecified qualification report passes G-03 criteria. | BLOCKED |
| OTGD-001-ANA-005-01 | Owner acceptance evidence — Challenge panel and method comparison are approved before final qualification. | BLOCKED |
| OTGD-001-ANA-006-01 | Owner acceptance evidence — Unit fixtures include pg/mL conversion without magnitude errors. | PASS |
| OTGD-001-ANA-007-01 | Owner acceptance evidence — Contract validation rejects fabricated quantified values for censored results. | PASS |
| OTGD-001-ANA-008-01 | Owner acceptance evidence — Cross-field validation and incompatible-input cases pass. | PARTIAL |
| OTGD-001-ANA-009-01 | Owner acceptance evidence — Prespecified agreement and failure analysis; external validation before claims. | BLOCKED |
| OTGD-001-ANA-010-01 | Owner acceptance evidence — An independent reviewer reconstructs a selected reported measurement. | PARTIAL |
| OTGD-001-ANA-011-01 | Owner acceptance evidence — Deliberate invalid specimens cannot yield an apparently ordinary concentration. | PARTIAL |
| OTGD-001-ANA-012-01 | Owner acceptance evidence — Retry audit preserves both attempts and their disposition. | PASS |
| OTGD-001-ANA-013-01 | Owner acceptance evidence — G-03 and G-13 contain measured data or dated supplier evidence. | BLOCKED |
| OTGD-001-APP-001-01 | Owner acceptance evidence — Scripted P0 journey displays measurement-only completion. | PASS |
| OTGD-001-APP-002-01 | Owner acceptance evidence — Boundary and unit examples produce correct BMI or explicit missing status. | PASS |
| OTGD-001-APP-003-01 | Owner acceptance evidence — Missing context survives export and cannot become a fabricated timestamp. | PARTIAL |
| OTGD-001-APP-004-01 | Owner acceptance evidence — Task event record verifies counts and excludes practice from scored features. | PASS |
| OTGD-001-APP-005-01 | Owner acceptance evidence — Seeded replay and event-level inspection reproduce features. | PASS |
| OTGD-001-APP-006-01 | Owner acceptance evidence — Reference event streams match expected derived feature records. | PASS |
| OTGD-001-APP-007-01 | Owner acceptance evidence — G-06 freezes and verifies device-specific timing acceptance. | BLOCKED |
| OTGD-001-APP-008-01 | Owner acceptance evidence — Interruption cases produce the prescribed quality and retry state. | PARTIAL |
| OTGD-001-APP-009-01 | Owner acceptance evidence — Low-quality and unscaled examples cannot pass as calibrated diameter. | PASS |
| OTGD-001-APP-010-01 | Owner acceptance evidence — Result inspection identifies whether a measurement followed the approved protocol. | PARTIAL |
| OTGD-001-APP-011-01 | Owner acceptance evidence — Temporal audit prevents later sessions entering a baseline. | PASS |
| OTGD-001-APP-012-01 | Owner acceptance evidence — State-by-state screenshots and API checks match the LLD. | PARTIAL |
| OTGD-001-APP-013-01 | Owner acceptance evidence — Copy review covers all result, notification, and error screens. | PARTIAL |
| OTGD-001-APP-014-01 | Owner acceptance evidence — G-10 lists supported configurations and tested accommodations. | BLOCKED |
| OTGD-001-MOD-001-01 | Owner acceptance evidence — G-01 protocol defines outcome, assessor, timing, and label rules. | BLOCKED |
| OTGD-001-MOD-002-01 | Owner acceptance evidence — Model review identifies measured features and any explicitly evaluated latent model. | PARTIAL |
| OTGD-001-MOD-003-01 | Owner acceptance evidence — Adversarial synthetic records produce the specified validity behavior. | PASS |
| OTGD-001-MOD-004-01 | Owner acceptance evidence — Any prediction can be reconstructed from immutable versioned inputs. | PASS |
| OTGD-001-MOD-005-01 | Owner acceptance evidence — Split audit and leakage review pass before locked evaluation. | PARTIAL |
| OTGD-001-MOD-006-01 | Owner acceptance evidence — Timestamp and dependency audit covers each feature and baseline. | PASS |
| OTGD-001-MOD-007-01 | Owner acceptance evidence — Manifest review and incompatible-record checks pass. | PASS |
| OTGD-001-MOD-008-01 | Owner acceptance evidence — Unauthorized activation and retired-model invocation are rejected. | PASS |
| OTGD-001-MOD-009-01 | Owner acceptance evidence — Negative inference cases verify null/absent probability and explicit reason. | PASS |
| OTGD-001-MOD-010-01 | Owner acceptance evidence — Every gate has both passing and rejecting integration evidence. | PARTIAL |
| OTGD-001-MOD-011-01 | Owner acceptance evidence — Variant selection is explicit, versioned, and validated. | PARTIAL |
| OTGD-001-MOD-012-01 | Owner acceptance evidence — Locked analysis plan and artifact hashes predate evaluation access. | BLOCKED |
| OTGD-001-MOD-013-01 | Owner acceptance evidence — Result contract and independent interpretation review pass. | PARTIAL |
| OTGD-001-MOD-014-01 | Owner acceptance evidence — Ablation report supports retained measurement burden. | PARTIAL |
| OTGD-001-MOD-015-01 | Owner acceptance evidence — Change-control exercise preserves the prior artifact and results. | PARTIAL |
| OTGD-001-ALC-001-01 | Owner acceptance evidence — Interface and synthetic demonstrations retain channel identity and provenance. | PASS |
| OTGD-001-ALC-002-01 | Owner acceptance evidence — G-11 documents supplier specifications and design tradeoffs. | BLOCKED |
| OTGD-001-ALC-003-01 | Owner acceptance evidence — Contract fixtures preserve all metadata without unapproved blood conversion. | PARTIAL |
| OTGD-001-ALC-004-01 | Owner acceptance evidence — Dedicated alcohol qualification against the selected reference method. | BLOCKED |
| OTGD-001-ALC-005-01 | Owner acceptance evidence — Protocol and model manifest agree on co-use handling. | PARTIAL |
| OTGD-001-SEC-001-01 | Owner acceptance evidence — Pre-commit/release review and secret/data scan of the staged changes. | NOT_RUN |
| OTGD-001-SEC-002-01 | Owner acceptance evidence — Unauthorized-role tests and identity-mapping review pass. | PARTIAL |
| OTGD-001-SEC-003-01 | Owner acceptance evidence — Consent/authorization and upload traces demonstrate the boundary. | PASS |
| OTGD-001-SEC-004-01 | Owner acceptance evidence — Deployment configuration and access review satisfy G-12. | BLOCKED |
| OTGD-001-SEC-005-01 | Owner acceptance evidence — G-12 states durations and tests deletion across primary/backup workflows. | PARTIAL |
| OTGD-001-SEC-006-01 | Owner acceptance evidence — Representative failure logs pass content review. | PARTIAL |
| OTGD-001-SEC-007-01 | Owner acceptance evidence — Tabletop exercise and responsible contacts documented. | BLOCKED |
| OTGD-001-OPS-001-01 | Owner acceptance evidence — Architecture review confirms boundaries and deployment configuration. | BLOCKED |
| OTGD-001-OPS-002-01 | Owner acceptance evidence — Repeated identical submissions produce one accepted logical record. | PASS |
| OTGD-001-OPS-003-01 | Owner acceptance evidence — Correction scenario preserves original content and provenance. | PASS |
| OTGD-001-OPS-004-01 | Owner acceptance evidence — Clock-drift and reordered-message cases retain interpretable timing. | PARTIAL |
| OTGD-001-OPS-005-01 | Owner acceptance evidence — Network interruption and restart exercises preserve correct terminal state. | PARTIAL |
| OTGD-001-OPS-006-01 | Owner acceptance evidence — G-12 documents values and a successful recovery exercise. | BLOCKED |
| OTGD-001-VAL-001-01 | Owner acceptance evidence — G-07 authorization and staff readiness records. | BLOCKED |
| OTGD-001-VAL-002-01 | Owner acceptance evidence — Outcome manual and data-flow review exclude circular labels. | BLOCKED |
| OTGD-001-VAL-003-01 | Owner acceptance evidence — Approved calculation/simulation at G-08; no arbitrary sample guarantee. | BLOCKED |
| OTGD-001-VAL-004-01 | Owner acceptance evidence — Prespecified strata and exclusions appear in the final report. | PARTIAL |
| OTGD-001-VAL-005-01 | Owner acceptance evidence — Independent report reconciles every enrolled check with its disposition. | PARTIAL |
| OTGD-001-VAL-006-01 | Owner acceptance evidence — G-09 report states independence, limitations, and deviations. | BLOCKED |
| OTGD-001-VAL-007-01 | Owner acceptance evidence — Temporal audit and study report demonstrate the consumer information boundary. | PARTIAL |
| OTGD-001-VAL-008-01 | Owner acceptance evidence — G-14 documented applicability determination and required evidence. | BLOCKED |
| OTGD-001-BUS-001-01 | Owner acceptance evidence — Commercial material avoids an unverified price/performance promise. | BLOCKED |
| OTGD-001-BUS-002-01 | Owner acceptance evidence — Dated cost model with supplier quotations and sensitivity analysis. | BLOCKED |
| OTGD-001-BUS-003-01 | Owner acceptance evidence — Product decision cites ablation, usability, and cost evidence. | BLOCKED |
| OTGD-001-DOC-001-01 | Owner acceptance evidence — Repository review finds no unsupported completion claim. | PARTIAL |
| OTGD-001-DOC-002-01 | Owner acceptance evidence — Gate register contains approver, date, artifact, and decision. | BLOCKED |
| OTGD-001-DOC-003-01 | Owner acceptance evidence — Change-impact checklist and versioned repository history. | PARTIAL |
| OTGD-001-PRD-001-01 | PRD acceptance review — \| PRD-001 \| A valid consumer-format check MUST require one saliva collection and one continuous reaction task. Multiple channels may be measured from that collection. \| | PARTIAL |
| OTGD-001-PRD-002-01 | PRD acceptance review — \| PRD-002 \| The check MUST also support guided pupil capture and resting heart-rate capture; ECG MUST remain an exploratory input until its incremental value and hardware approach are justified. \| | PARTIAL |
| OTGD-001-PRD-003-01 | PRD acceptance review — \| PRD-003 \| P0 and P1 MUST produce measurement-only outputs, never an intoxication probability. \| | PASS |
| OTGD-001-PRD-004-01 | PRD acceptance review — \| PRD-004 \| A P2 probability MUST require an authorized research session, an `active_research` model, a compatible feature contract, and all model-required valid channels. \| | PASS |
| OTGD-001-PRD-005-01 | PRD acceptance review — \| PRD-005 \| The future impairment endpoint, intended population, operating threshold, and acceptable error rates MUST be selected before confirmatory evaluation. \| | BLOCKED |
| OTGD-001-PRD-006-01 | PRD acceptance review — \| PRD-006 \| A model result MUST NOT be presented as proof of cannabis causation, a legal determination, or clearance to drive. \| | PARTIAL |
| OTGD-001-PRD-007-01 | PRD acceptance review — \| PRD-007 \| The product MUST retain distinct invalid, inconclusive, measurement-only, and research-estimate outcomes. Missing information MUST NOT be interpreted as a normal measurement. \| | PASS |
| OTGD-001-PRD-008-01 | PRD acceptance review — \| PRD-008 \| Alcohol MUST remain a separately measured and separately reported channel; cannabis physiology MUST NOT substitute for a breath-alcohol measurement. \| | PASS |
| OTGD-001-PRD-009-01 | PRD acceptance review — \| PRD-009 \| Standardized session orchestration \| P0 MUST establish a complete synthetic workflow with unique attempts, timestamps, quality, and terminal states. \| | PASS |
| OTGD-001-PRD-010-01 | PRD acceptance review — \| PRD-010 \| Quantitative saliva interface \| P1 MUST establish reliable specimen handling and a reference-laboratory comparison before any portable concentration claim. \| | PARTIAL |
| OTGD-001-PRD-011-01 | PRD acceptance review — \| PRD-011 \| Parent THC channel \| P1 MUST evaluate delta-9 THC first. Selection of additional channels requires analytical feasibility and added-value evidence. \| | BLOCKED |
| OTGD-001-PRD-012-01 | PRD acceptance review — \| PRD-012 \| Additional saliva metabolites \| THC-COOH and 11-OH-THC SHOULD be investigated; neither is promised as a functional cartridge channel in v0.1.0. \| | PARTIAL |
| OTGD-001-PRD-013-01 | PRD acceptance review — \| PRD-013 \| One repeated-trial game \| P0 MUST support the task contract; P2 MUST evaluate reliability and independent predictive value. \| | PARTIAL |
| OTGD-001-PRD-014-01 | PRD acceptance review — \| PRD-014 \| Dynamic pupil measurements \| P1/P2 MUST establish acquisition quality, valid units, optical controls, and repeatability before features enter a model. \| | PARTIAL |
| OTGD-001-PRD-015-01 | PRD acceptance review — \| PRD-015 \| Heart rate and exploratory ECG \| Cardiac capture MUST preserve signal quality and context; an ECG-only benefit MUST be measured by ablation. \| | PARTIAL |
| OTGD-001-PRD-016-01 | PRD acceptance review — \| PRD-016 \| Profile and use history \| The app MUST preserve source, measurement date, units, and unknown values; demographics MUST NOT determine an assumed clearance rate. \| | PASS |
| OTGD-001-PRD-017-01 | PRD acceptance review — \| PRD-017 \| Separate alcohol channel \| The design SHOULD reserve integration capability; alcohol performance claims require a calibrated breath system and dedicated validation. \| | PARTIAL |
| OTGD-001-PRD-018-01 | PRD acceptance review — \| PRD-018 \| Versioned research dataset \| P2 MUST support reconstruction of the exact specimen, task, device, calibration, feature, and model versions. \| | PASS |
| OTGD-001-PRD-019-01 | PRD acceptance review — \| PRD-019 \| Quality-aware research result \| Inference MUST enforce the release manifest and required-channel rules without fallback to an incompatible model. \| | PARTIAL |
| OTGD-001-PRD-020-01 | PRD acceptance review — \| PRD-020 \| Understandable session feedback \| The app MUST distinguish capture success, analysis availability, and a research prediction. \| | PARTIAL |
| OTGD-001-PRD-029-01 | PRD acceptance review — \| PRD-029 \| A person can enter guest practice or authenticate, recover an interrupted sign-in, refresh safely and sign out with truthful remote-revocation status. Environment/account partitions and retained signed-out data stay isolated. \| SEC-002/004/007; AND-ONB-001–006; AND-AUTH-001–007; AND-ENV-001/002 \| | PARTIAL |
| OTGD-001-PRD-030-01 | PRD acceptance review — \| PRD-030 \| An invited eligible account can review exact study consent and current channel availability; sign-in, age, a guessed study ID or a checkbox cannot create research authority. Withdrawal stops local study work immediately and preserves its durable receipt. \| SEC-002/003; MOD-008–010; AND-STUDY-001–006; PAI-001–008 \| | PARTIAL |
| OTGD-001-PRD-031-01 | PRD acceptance review — \| PRD-031 \| A check freezes its confirmed optional profile/context, one-sample/one-task information boundary, original target, all attempts and selected evidence. Interruptions and linked replacements preserve original records. \| ANA-001/012; APP-001–008; OPS-002–005; AND-PRO-001–007; AND-CHECK-001–008 \| | PARTIAL |
| OTGD-001-PRD-032-01 | PRD acceptance review — \| PRD-032 \| Native reaction acquisition preserves deterministic practice/scored schedules, actual native events, missingness and immediate stop behavior; build success and clock resolution do not establish physical timing qualification. \| APP-004–008/014; AND-TASK-001–008; G-06 \| | PASS |
| OTGD-001-PRD-033-01 | PRD acceptance review — \| PRD-033 \| Device discovery, verified binding and fresh scoped starts distinguish a working connection from a qualified channel. Protected BLE, actual adapter inventory, quality, cancellation and replay/origin fences apply to conditional reader capture. \| HW-003/004/007/012; SEC-004; AND-DEV-001–008; CAN-SR-001–011; VPPG-001–007 \| | PARTIAL |
| OTGD-001-PRD-034-01 | PRD acceptance review — \| PRD-034 \| Saliva collection/import, optical capture and selected PPG/exploratory ECG have explicit pending, unavailable, invalid and permitted retry paths. Declarations, approved software and signatures do not qualify an assay, optics, electrical setup or sensor. \| ANA-001–012; HW-005–009; APP-009/010; AND-SAL-001–007; SALCOL-001–008; AND-EYE-001–007/101–106; AND-HR-001–007; AND-ECG-001–007 \| | PARTIAL |
| OTGD-001-PRD-035-01 | PRD acceptance review — \| PRD-035 \| Protected local save precedes a separate explicit account upload; restart, lost receipts, bounded retry and conflicts preserve ownership, original times and immutable evidence. Permission failures and retired generations cannot be repaired by automatic reupload. \| SEC-003/004; OPS-002–005; AND-SYNC-001–007; AND-CHECK-006; shared contracts §§2–5 \| | PARTIAL |
| OTGD-001-PRD-036-01 | PRD acceptance review — \| PRD-036 \| History/results show the actual scientific state separately from delivery, preserve qualifiers and old acquisition times, and navigate immutable original/replacement and same-specimen report-revision lineage. \| APP-012/013; MOD-013; AND-HIST-001–007; AND-RES-001–007; report-revision and replacement-links contracts \| | PASS |
| OTGD-001-PRD-037-01 | PRD acceptance review — \| PRD-037 \| Optional eye/ECG recording and upload default off, have distinct reviewed purposes, retain exact receipts and expire under original retention deadlines. Revocation stops capture before cleanup; pending quarantine/cleanup is visible. \| SEC-003–005; AND-RAW-001–007; AND-EYE-006/106; AND-ECG-007; raw-recording-retention contract \| | PARTIAL |
| OTGD-001-PRD-038-01 | PRD acceptance review — \| PRD-038 \| The owner can create a bounded exact-scope structured export, optionally include separately authorized retained raw sources, verify and deliberately share it. Downloads require current authority; expiration, revocation and temporary-file cleanup remain explicit. \| SEC-002/005/007; AND-EXP-001–007; RAW-EXP-001–008; AND-RAW-008 \| | PARTIAL |
| OTGD-001-PRD-039-01 | PRD acceptance review — \| PRD-039 \| Local clear, cloud-data deletion, account deletion and withdrawal show distinct scopes and honest asynchronous receipts. Generation barriers and independent retained recovery evidence prevent resurrection; study recovery requires fresh independent reapproval and participant consent. \| SEC-005/007; OPS-003–006; AND-PRIV-001–007; RECOVERY-001/002; platform contract \| | PARTIAL |
| OTGD-001-PRD-040-01 | PRD acceptance review — \| PRD-040 \| Instructions, navigation, errors and privacy controls support specified Android/iOS accessibility and permission recovery. Changes to timed-task presentation/input retain their separate compatibility and qualification boundary. \| APP-014; AND-SET-001–007 and feature-specific parity requirements; shared contracts §9 \| | BLOCKED |
| OTGD-001-PRD-041-01 | PRD acceptance review — \| PRD-041 \| Independently governed operator releases can admit the exact conditional research software, including only explicitly approved model variants and baseline scope. Measurement-only remains default; the restricted HR-only evaluation mode discloses absent multimodal comparisons. \| MOD-001–015; VAL-001–007; OPERATOR-AUTHORITY-001–009; MODEL-001–006; EVAL-001–008 as modified; HR-AUTH-001–008 \| | PASS |
| OTGD-001-PRD-042-01 | PRD acceptance review — \| PRD-042 \| Isolated fictional previews and reviewable local/QA/prod/store delivery tooling preserve exact source/artifact identity, environment and uncertain outcomes. Prepared software, submitted artifacts, hosted access, public availability and scientific qualification remain separate evidence. \| HW-002; SEC-001/004; OPS-001–006; AND-ENV-001–007; AND-PREV-001–003; WEB-DEP-001–010; CLOUD-DEP-001–011; PREVIEW-001–003; STORE-001–018 \| | PARTIAL |
| OTGD-001-PRD-021-01 | PRD acceptance review — \| PRD-021 \| Analytical usefulness \| Compare each intended cartridge channel with a traceable reference method over a prespecified range, including censored and invalid results. Freeze acceptance limits before qualification. \| | BLOCKED |
| OTGD-001-PRD-022-01 | PRD acceptance review — \| PRD-022 \| Independent prediction value \| Compare chemistry alone, app signals alone, and the combined model against the same independent outcome. Require evidence of useful incremental benefit. \| | PARTIAL |
| OTGD-001-PRD-023-01 | PRD acceptance review — \| PRD-023 \| Single-check usability \| Measure completion rate, duration distribution, retries, specimen failures, camera failures, and task interruptions using the intended workflow. \| | BLOCKED |
| OTGD-001-PRD-024-01 | PRD acceptance review — \| PRD-024 \| Generalization \| Report errors and calibration for held-out people, later sessions, supported devices, consumption routes, use-frequency strata, and first-use versus personalized modes. \| | PARTIAL |
| OTGD-001-PRD-025-01 | PRD acceptance review — \| PRD-025 \| Operational reliability \| Measure record completeness, upload reconciliation, recovery after interruption, and traceability of finalized results. \| | PARTIAL |
| OTGD-001-PRD-026-01 | PRD acceptance review — \| PRD-026 \| Economic feasibility \| Build usage-based cost scenarios before selecting subscription allowances or promising a hardware subsidy. \| | BLOCKED |
| OTGD-001-PRD-027-01 | PRD acceptance review — \| PRD-027 \| Freeze intended use, primary impairment outcome, population, thresholds, and collection-to-result interval \| Clinical and product leads, with statistical lead \| P2 confirmatory evaluation and all P3 claims \| | BLOCKED |
| OTGD-001-PRD-028-01 | PRD acceptance review — \| PRD-028 \| Select collection/cartridge chemistry, cardiac implementation, optical protocol, supported phone list, final retention policy, and subscription allowance \| Respective analytical, hardware, optical, app, data, and commercial leads \| Respective feasibility and release gates \| | BLOCKED |
