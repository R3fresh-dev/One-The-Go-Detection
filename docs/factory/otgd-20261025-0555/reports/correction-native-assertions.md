# Correction round1 — native task assertions and reference admission

**Host correction checks passed; changed Kotlin/Swift assertions require fresh native CI execution.** This is an author implementation/evidence report, not independent signoff or application/release approval. Formal correction1/2; PM recovery0/3 unchanged.

Owner /root/firmware_validation, assigned OpenAI gpt-6.1-sol/high. Reviewed immutable candidate supplied by PM28e07295cb37bb9dcaaac82cc8fc846eb89006a6. Replacement working-source SHA256 manifest below binds this correction; no Git commit was made by this worker. D-009 v1/v2 acknowledged before test/fixture edits; v3 read and acknowledged before the narrow production-reference repair after PM independently corroborated the defect. Shared literal fixtures were coordinated with /root/verification, which confirmed no competing writer. PM explicitly assigned the new reference test file and later the one production Python file. No production Kotlin/Swift, native UI/view lifecycle, scientific timing constant or configuration changed. No Docker/runtime/image preparation, services/data manipulation, cleanup, installs, commit/push, participant action or deployment occurred.

## Requirement-to-assertion mapping

Normative source: openspec/changes/production-mobile-platform/specs/android-reaction-task/spec.md, AND-TASK-004 detailed contract and named scenarios; AND-TASK-008 requires literal cross-platform goldens. Verifier mapping: OTGD-033-TASK004-01/03/04, ASSERT004/005/006. The verifier owns final782-case reconciliation.

| Clause | Added evidence/assertion | Actual execution/current limit |
|---|---|---|
| TASK004-01 wrong then correct | Existing literal vector now expects retained count2, sequences0/1, right selected then left additional_response, exact native/dispatch timestamps/delays, pointer/input kind/trial association. Kotlin and Swift generic consumers assert every retained field plus null correct-go RT and unchanged wrong_choice. Reference full66-trial case retains53 total input records, both target-trial touches, wrongGo1/correctGo47, no invented correct-go RT; actual validator leaves full record/digest unchanged. | Python reference executed; Kotlin/Swift authored, current native CI NOT_RUN locally. |
| TASK004-04 opposing equal timestamps | Original right-then-left literal retained; added left-then-right literal with left pointer9 vs right pointer0 to prove target rank before pointer. Added same-target lower-pointer priority and same-pointer native-sequence tie, including reversed raw-array order to discriminate sequence sorting. Consumers assert selected sequence, full sorted sequence list, count and dispositions. | Full66-trial Python validation executes these literals and rejects altered selected sequence. Native scorer assertions need fresh Kotlin/Swift CI. |
| TASK004-03 final drain | Existing native10999/dispatch11079 vector now retains exact delay80 both as input property and serialized map/dictionary. Added combined literal with admitted RT999/delay80 and handlers exactly11100/after11101 ignored; consumers snapshot complete scored trial/input/count/feature evidence before the first rejected arrival and assert unchanged final snapshot, with two ignored arrivals/one retained input. Exact-cutoff omission vector explicitly expects empty ledger. | Python valid/refusal/cutoff arithmetic cases executed. Native snapshots are pure core+admission checks; no native UI/device delivery or terminal integration execution claimed. |
| D-009 v3 proven reference gap | validate_native verifies stored delay against timestamp subtraction at fixed1e-6ms absolute tolerance. Valid runs pin cutoff to last onset+configured1000ms window+100ms drain and refuse any handler at/after that derived cutoff; tiny metadata tolerance cannot extend admission. Invalid/interrupted ledgers retain truthful fault records, including negative/overbudget delays and partial/null cutoff metadata. | Six invalid-fault/cutoff combinations, exact100ms valid boundary, arithmetic tolerance sides, before/equal/after cutoff, missing/shifted cutoff metadata and claimed-score refusals pass. |

New tests call the actual production independent Python validate_native on a full66-trial fixture; they are not a standalone oracle substituting for production reference validation. One selected scored trial is translated from literal10000ms coordinates to its existing planned onset; all66 schedule records, configuration/hash and other baseline300ms responses remain. Sequence offsets preserve unique IDs; corresponding factual count/rate changes are explicit, while quantiles stay300/0/300 with at least47 unchanged baseline RTs. Canonical native-payload digests are recomputed/checked before and after validation and hostile mutations; schedule hashes remain unchanged. This tests native-reference admission directly, not the separate full signed/server-custody chain.

## Defect reproduction and narrow correction

Before production repair, the actual full66-trial validator accepted (a) stored delay80 with native2300/dispatch2305, and (b) retained outside-target event handled exactly at112408ms cutoff. PM independently reproduced both and accepted D-009 v3. The new regressions first produced **3 failed /9 passed**, failing because no Problem was raised for forged delay or equality/after-cutoff retained events. Raw probe/red output is preserved. These are observed software validation defects, not a claim of physical clock accuracy.

The production diff is limited to truthful dispatch subtraction and valid-run derived cutoff validation in services/api/otgd/native_evidence.py. The fixed100ms input budget,1000ms response window,100ms drain and1e-6ms arithmetic tolerance are unchanged. Delay arithmetic is checked even in invalid evidence, allowing truthful negative/101ms values; valid-run cutoff requirements occur after the invalid-ledger return, preserving partial/null terminal semantics. Invalid final features remain null. Existing canceled999/1000ms partial-window regressions continue to pass. Neither correction qualifies sensing, physiological interpretation, participant authority or fitness to drive.

## Fixture/source preservation

Original14 literal trial vectors retain every input, original expected field/value and timing. Only additional expectation fields were added, plus four independently literal vectors (18 total): reverse opposing targets; pointer priority; native-sequence tie; committed drain with equality/after-cutoff arrivals. Existing configuration, all three schedule objects/digests, aggregate vectors and race vectors are identical. Both fixture copies are byte-identical. Preservation was checked against the retained source snapshot only after matching its full pre-edit fixture hash. Native production Kotlin/Swift/view/module and configuration file hashes match the pre-edit manifest. Preservation receipt records those hashes. No expected value was regenerated from a production scorer.

## Executed checks and source-bound results

Final source release verified at report generation 2026-10-25T08:13:53.859396+00:00.

- Actual reference+cross-language suite: **45 passed**, zero failed/errors/skips; **24 new reference cases** and21 existing cross-language cases. Final run08:10:12.840864–08:10:15.013819 UTC, exit0, local disposable SQLite configuration; no canonical database or service touched.
- Canonical scripts/ci_gate.py verify-junit checked the actual final XML and passed.
- Ruff check on the changed Python validator/test passed. Earlier import-order/unused-test-variable findings were corrected in the new test only; initial logs retained.
- Standard native-asset checker passed, validating paired fixtures, fixed configuration hash61bd03244a9f82fdc5a1a2b6658483ca201ab5d39a95e64cde0d00f1d5a666c3 and all three literal schedule hashes. An initial invocation used the module-relative path from repository root and failed locating the file; root-relative retry passed without source changes.
- No firmware rebuild performed because firmware source was unchanged. No install was attempted.

The FastAPI/Starlette httpx test-client deprecation warning is preserved in raw logs; it did not skip assertions or fail these checks.

## Explicit blocked execution and remaining gates

**Action:** execute changed ReactionCoreTest.allLiteralTrialBoundaryVectors and Swift ReactionCoreTests.testAllLiteralTrialBoundaryVectors in their prescribed module jobs. **Targets:** actual Android Gradle reaction module and macOS/Xcode Swift package. **Reason:** current environment has Java, but no kotlinc, swift or xcodebuild; generated apps/mobile/android/gradlew is absent. Current assignment forbids installs. **State:** NOT_RUN/BLOCKED locally; no approval denial or uncertain execution. Old reviewed-candidate CI XML/HTML cannot establish execution of changed assertions. Fresh exact-source CI must compile and execute both suites. Required native checks remain unmet locally, and AGENTS.md forbids overall completion claims or treating missing checks as PASS.

Required existing commands on capable CI:

```sh
# Existing native Android job after canonical prebuild/toolchain preparation:
./gradlew --no-daemon --max-workers=2 --init-script ../modules/scripts/local-preview.init.gradle -PreactNativeDevServerPort=8082 -PreactNativeArchitectures=arm64-v8a,x86_64 :otgd-reaction-task:testDebugUnitTest :otgd-eye-capture:testDebugUnitTest :app:assembleDebug :app:assembleRelease
# Existing macOS Swift job:
set -o pipefail
swift test --package-path apps/mobile/modules/reaction-task --parallel --num-workers 1 --verbose --disable-swift-testing --xunit-output "$PWD/reports/ios-native.xml" 2>&1 | tee reports/ios-native.log
python3 scripts/verify-swift-xctest.py reports/ios-native.xml reports/ios-native.log
python3 scripts/ci_gate.py verify-junit reports/ios-native.xml
```

Android/iOS native UI/touch dispatch, actual OS lifecycle/cutoff, assistive integration, physical display/touch calibration and hardware qualification are separate explicit gaps. No local Swift or Kotlin compile/run is claimed. API runtime image D is stale for the corrected Python file and new API tests; PM requires a new current source binding before final gates. This worker has not prepared that image or performed Docker actions. Current final local/all14CI gates, affected six independent rereviews, source freeze and fresh approver prerequisites remain PM-owned. This report is not self-signoff.

## Released source hashes

| File | SHA256 |
|---|---|
| `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt` | `a8ab3f8d36028c621cd0e65df73d1f2bb0d6edd9b0c2107dd70c5f013d1c121e` |
| `apps/mobile/modules/reaction-task/fixtures/golden.json` | `1e3ee2974e977aa5977bbe36a828851ff044e1f3335ac37e62b3f7ba4cb1270c` |
| `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift` | `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc` |
| `openspec/changes/production-mobile-platform/fixtures/reaction-task-golden-v1.json` | `1e3ee2974e977aa5977bbe36a828851ff044e1f3335ac37e62b3f7ba4cb1270c` |
| `services/api/otgd/native_evidence.py` | `be7d1fe0b49c666f599d0e8978cdef2e6d5230268335c29d1a1a18663a045ced` |
| `services/api/tests/test_reaction_task_goldens.py` | `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e` |

## Exact executed command records

**reference-red** — 2026-10-25T08:05:44.620809+00:00 to 2026-10-25T08:05:46.259895+00:00; exit1; 1.639s; log `/tmp/otgd-native-correction/reference-red.log`.

```json
[
  "services/api/.venv/bin/python",
  "-m",
  "pytest",
  "services/api/tests/test_reaction_task_goldens.py",
  "-q",
  "--junitxml=/tmp/otgd-native-correction/reference-red.xml"
]
```

**reference-green** — 2026-10-25T08:08:29.758458+00:00 to 2026-10-25T08:08:32.449251+00:00; exit0; 2.691s; log `/tmp/otgd-native-correction/reference-green.log`.

```json
[
  "env",
  "OTGD_DATABASE_URL=sqlite://",
  "services/api/.venv/bin/python",
  "-m",
  "pytest",
  "services/api/tests/test_reaction_task_goldens.py",
  "services/api/tests/test_cross_language.py",
  "-q",
  "--junitxml=/tmp/otgd-native-correction/reference-green.xml"
]
```

**native-assets** — 2026-10-25T08:08:32.478816+00:00 to 2026-10-25T08:08:32.509509+00:00; exit1; 0.031s; log `/tmp/otgd-native-correction/native-assets.log`.

```json
[
  "node",
  "modules/scripts/verify-native-assets.mjs"
]
```

**native-assets-root** — 2026-10-25T08:08:39.538517+00:00 to 2026-10-25T08:08:39.591311+00:00; exit0; 0.053s; log `/tmp/otgd-native-correction/native-assets-root.log`.

```json
[
  "node",
  "apps/mobile/modules/scripts/verify-native-assets.mjs"
]
```

**python-lint** — 2026-10-25T08:08:39.618607+00:00 to 2026-10-25T08:08:39.629555+00:00; exit1; 0.011s; log `/tmp/otgd-native-correction/python-lint.log`.

```json
[
  "services/api/.venv/bin/ruff",
  "check",
  "services/api/otgd/native_evidence.py",
  "services/api/tests/test_reaction_task_goldens.py"
]
```

**python-lint-final** — 2026-10-25T08:09:40.542342+00:00 to 2026-10-25T08:09:40.550747+00:00; exit1; 0.008s; log `/tmp/otgd-native-correction/python-lint-final.log`.

```json
[
  "services/api/.venv/bin/ruff",
  "check",
  "services/api/otgd/native_evidence.py",
  "services/api/tests/test_reaction_task_goldens.py"
]
```

**reference-final** — 2026-10-25T08:09:40.578398+00:00 to 2026-10-25T08:09:43.000850+00:00; exit0; 2.422s; log `/tmp/otgd-native-correction/reference-final.log`.

```json
[
  "env",
  "OTGD_DATABASE_URL=sqlite://",
  "services/api/.venv/bin/python",
  "-m",
  "pytest",
  "services/api/tests/test_reaction_task_goldens.py",
  "services/api/tests/test_cross_language.py",
  "-q",
  "--junitxml=/tmp/otgd-native-correction/reference-final.xml"
]
```

**python-lint-passed** — 2026-10-25T08:10:12.808243+00:00 to 2026-10-25T08:10:12.815982+00:00; exit0; 0.008s; log `/tmp/otgd-native-correction/python-lint-passed.log`.

```json
[
  "services/api/.venv/bin/ruff",
  "check",
  "services/api/otgd/native_evidence.py",
  "services/api/tests/test_reaction_task_goldens.py"
]
```

**reference-release** — 2026-10-25T08:10:12.840864+00:00 to 2026-10-25T08:10:15.013819+00:00; exit0; 2.173s; log `/tmp/otgd-native-correction/reference-release.log`.

```json
[
  "env",
  "OTGD_DATABASE_URL=sqlite://",
  "services/api/.venv/bin/python",
  "-m",
  "pytest",
  "services/api/tests/test_reaction_task_goldens.py",
  "services/api/tests/test_cross_language.py",
  "-q",
  "--junitxml=/tmp/otgd-native-correction/reference-release.xml"
]
```

**reference-junit** — 2026-10-25T08:10:15.041355+00:00 to 2026-10-25T08:10:15.112180+00:00; exit0; 0.071s; log `/tmp/otgd-native-correction/reference-junit.log`.

```json
[
  "python3",
  "scripts/ci_gate.py",
  "verify-junit",
  "/tmp/otgd-native-correction/reference-release.xml"
]
```

**native-tool-inventory** — 2026-10-25T08:10:15.141771+00:00 to 2026-10-25T08:10:15.167093+00:00; exit0; 0.025s; log `/tmp/otgd-native-correction/native-tool-inventory.log`.

```json
[
  "python3",
  "-c",
  "import json,shutil,pathlib;print(json.dumps({\"java\":shutil.which(\"java\"),\"kotlinc\":shutil.which(\"kotlinc\"),\"swift\":shutil.which(\"swift\"),\"xcodebuild\":shutil.which(\"xcodebuild\"),\"android_gradlew\":pathlib.Path(\"apps/mobile/android/gradlew\").exists()},sort_keys=True))"
]
```

## Supporting evidence hashes

| Artifact | Bytes | SHA256 |
|---|---:|---|
| `/tmp/otgd-native-correction/native-assets-root.log` | 346 | `11e0eac6ac86ccd7f77d2c1a423134463689fc9e3e6916167cb07c4fd97f62a0` |
| `/tmp/otgd-native-correction/native-assets.log` | 887 | `d91adb5234fddebe2c69cd0ef7bf8c36b91d741fad03b0218fe29cdb87dfeeca` |
| `/tmp/otgd-native-correction/native-tool-inventory.log` | 458 | `4a9cad6bdaa070ba12dd612a794ed605ecf2d0cef9ec6dd7eefdb16a29627108` |
| `/tmp/otgd-native-correction/native_evidence-before.py` | 17,300 | `c807bcec91bf8b60125334feb3b8177d12e5a05ec84c4acb539077a1e03d8510` |
| `/tmp/otgd-native-correction/preservation-checks.json` | 1,742 | `fcee5e6281247bcf116c7641f4b4c330eae909bbc32bfeb1abfc777d85b9fcbe` |
| `/tmp/otgd-native-correction/python-lint-final.log` | 839 | `4f183d2ca280d32dff05dc4098c47ce11d226aec1c085082183f6c792a8fb32d` |
| `/tmp/otgd-native-correction/python-lint-passed.log` | 199 | `13f3521250f224f69d3014d3d0fa863239384f91ed590d7bb9950ef6366d2df1` |
| `/tmp/otgd-native-correction/python-lint.log` | 2,113 | `cd14c2bfa83ab3b8b438fc9435df6a80b1c28f355ca5c3b6bd8968c7986d3523` |
| `/tmp/otgd-native-correction/reference-final.log` | 925 | `60e9506dd00ed8d64739a19e08a5bd39e1b43f6baf768fd44c618d256ac4aa6e` |
| `/tmp/otgd-native-correction/reference-final.xml` | 6,838 | `1e331e007c280f438ebcebd8b3e84b1d9e44a1c024d87f9e63fbc621af737102` |
| `/tmp/otgd-native-correction/reference-green.log` | 925 | `6c340b7ed6e9294aaa897a8ec645e2cba6a21b617edf29ddee1129081064eece` |
| `/tmp/otgd-native-correction/reference-green.xml` | 6,380 | `f7b74abacd553c277c3d084ec81c79286f0282b0dfb5debd9108c3755e6fff3c` |
| `/tmp/otgd-native-correction/reference-junit.log` | 150 | `1ac74660f5e9b5ed99f47b0a4d9667a628027e445c02ed941d8333c4818638d4` |
| `/tmp/otgd-native-correction/reference-probe.py` | 1,600 | `166bc8818fe732ce846ba2c0fd00953b41ec697082bd69a914c431fbb55ce756` |
| `/tmp/otgd-native-correction/reference-red.log` | 4,177 | `eeb03343e73906c57d20803ed19fb1062b1dd41dda5a527d51cefd50503d819f` |
| `/tmp/otgd-native-correction/reference-red.xml` | 5,047 | `5d877da317f50b7bf964622f2a010d2a7cd4d365ae37f1b009267b9a3f6ac272` |
| `/tmp/otgd-native-correction/reference-release.log` | 927 | `689e6a5beae8cd27998bb70e1f20028048436b06314980aa3f7d4dd32b35f2ad` |
| `/tmp/otgd-native-correction/reference-release.xml` | 6,838 | `ea101dcfed302c73a5c9ab9d327968361b9b4f71af039b66218ece48b5aa2709` |
| `/tmp/otgd-native-correction/results.jsonl` | 4,457 | `355e91ce7c8fa451daf8c8acf0186a535f4eb485b8211728512cbd5408ab01c0` |
| `/tmp/otgd-native-correction/run.py` | 761 | `283ba76d9b85a4f5489abb33e386185cecfda6501475dea9b2ea316f248b343a` |
| `/tmp/otgd-native-correction/source-before.json` | 3,259 | `3025c709c9f872b39845af7b42ae84056956773738630f11af96e15bb62b2b7d` |
| `/tmp/otgd-native-correction/source-release.json` | 836 | `fe3cb80c9436519f2131383ce819497c63624cc4c22c21aa2bc9178957fb98fd` |
