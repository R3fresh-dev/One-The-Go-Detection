# OTGD-040 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/qualified-participant-acquisition/specs/reference-lab-collection/spec.md`; SHA256 `09cbf8dccec136a1ec7895fc553c62160b63fa1e2133f5b5864d7d3aed13547a`.

26 cases, 8 requirements: PARTIAL 4, PASS 22. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-040-SALCOL-001-01 — PASS

Approved laboratory method without a peripheral — - **GIVEN** an authenticated participant has current consent and a released reference-lab collection configuration - **WHEN** Saliva is opened with no BLE reader - **THEN** approved instructions and collection actions are available, and no physical-reader start is attempted.

Current proof: Approved method instructions selectable without Bluetooth; signed lab grant has no binding/device; controller explicitly records no nonce/hardware-acquire.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::laboratory method review pins the actual selected method without BLE and resets acknowledgement on document replacement` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 920; 4 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::reference laboratory collection has no BLE acquisition, persists a recoverable pending draft, imports separate analysis then permits explicit finalization` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 870; 1 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_positive_collection_without_ble_is_owned_immutable_and_pending` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 264; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 87db80193dd6a52516124292f612788321106652f77b1b9c927c9f335455ad33. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-001-02 — PARTIAL

Unsupported cartridge-reader configuration — - **GIVEN** a configuration names an unimplemented assay reader - **WHEN** availability or Start is evaluated - **THEN** the app identifies the missing adapter rather than substituting the laboratory form, a timer or a generic ADC reading.

Current proof: Generic cardiac transport without a driver reports HUMAN_ADAPTER_UNIMPLEMENTED and start refuses. Inspected software_supported rejects adapter names outside channel whitelist; saliva whitelist contains only reference_lab_import_v1.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_current_device_calibration_binding_and_software_inventory` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 740; 5 current observation(s).
- `services/api/tests/test_operator_governance.py::test_signed_reader_transport_and_recording_approval_cannot_invent_a_sampling_driver_or_raw_codec` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 649; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Unsupported assay-reader saliva configuration specifically identifies missing adapter in availability/Start and cannot substitute laboratory form/timer/generic ADC: existing inspected inventory tests exercise cardiac transport, not this assay-channel dispatch case.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0c7a5ef25c5373be55ee1cf5bb9554e2bcb369fab6bbeb8849bf20c6b8008fea. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-002-01 — PASS

Approved buffered collection — - **GIVEN** the method permits measured saliva/buffer volumes and defines the dilution convention - **WHEN** the participant records those values and current lot/handling information - **THEN** the bounded form retains the explicit quantities, method/version and dilution meaning in companion metadata.

Current proof: Form retains actual saliva/buffer/dilution, lot/handling and selected method/version; backend round-trips each supported dilution convention and typed companion retains request.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::specimen form records actual quantities, explicit unknowns and handling while offering no participant concentration entry` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 972; 4 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_each_supported_dilution_convention_preserves_its_approved_meaning` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 483; 10 current observation(s).
- `apps/mobile/tests/participant-acquisition.test.ts::actual Python protocol, immutable acknowledgement, specimen and imported report preserve separate truthful lineage` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 87; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 326e0fd9861ac41d235e0244aedb8dbeb9c893ff3943e4cd133b35ae0e5f2517. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-002-02 — PASS

Unknown required volume or expired supply — - **GIVEN** a required quantity is unknown or the submitted supply is expired - **WHEN** Record sample is selected - **THEN** the service refuses a valid collection claim with actionable field reasons, leaves quantities uninvented and offers an explicit immutable invalid disposition instead of silently losing the failed attempt.

Current proof: Required unknown quantities/expired supply refuse with named field errors and no collection record; explicit invalid disposition succeeds and preserves failed sample and linked retry.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_collection_rejects_forged_analytical_authority_and_invalid_metadata` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 388; 60 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_collection_chronology_and_handling_are_actual_events_not_form_progress` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 535; 35 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_invalid_collection_preserves_failure_and_linked_retry_allocates_new_sample` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 436; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 5e0a97cfa906f3ee03371a3acdfef81781b4a6d12b9d4f05320960189ba46821. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-002-03 — PASS

Protocol permits an unknown optional field — - **GIVEN** a field is optional and the released method permits an explicit unknown reason - **WHEN** the participant declines it - **THEN** null and that reason are preserved rather than storing zero or an assumed value.

Current proof: Optional collector uses null with exact approved unknown reason; fixture optional cartridge lot null/not_applicable is retained in immutable accepted request; no zero invented.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::specimen form records actual quantities, explicit unknowns and handling while offering no participant concentration entry` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 972; 4 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_positive_collection_without_ble_is_owned_immutable_and_pending` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 264; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 66177c60d7e94bbc4e656c98e6171a434f7f750d5fc6fcd303ea6d22ebf49f0c. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-002-04 — PASS

Unsupported or contradictory null reason — - **GIVEN** a missing field has a free-text or unapproved reason, or a present value also claims to be missing - **WHEN** collection is submitted - **THEN** exact null-reason validation rejects it; the service cannot manufacture permitted method semantics from caller text.

Current proof: Invented/unapproved null reasons and missing required data refuse; original attempt stays started and no collection record is created. ActualHTTPcollection/persistedreceipt and releasedtypedmodel required/optionalscope; noinventedpendingvalue, currentrequiredchemistryabandonfinalization refuses withoutjob; permittedothermodes preserve202; initialimporttarget/authority negatives at actualimportboundary.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_collection_rejects_forged_analytical_authority_and_invalid_metadata` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 388; 60 current observation(s).
- `apps/mobile/tests/participant-acquisition.test.ts::approved quantities and unknown reasons refuse contradictory or invented collection facts` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 223; 1 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_collection_first_late_submission_is_denied_but_exact_key_replay_stays_historical` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 301; 10 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_present_collection_value_cannot_also_claim_a_missing_reason` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 341; 10 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_pending_collection_cannot_satisfy_required_chemistry_and_does_not_invent_optional_values` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 788; 10 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_abandonment_cannot_finalize_when_current_model_requires_missing_chemistry` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 868; 25 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_initial_import_refuses_foreign_target_scope_not_only_source_creation` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 422; 15 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_initial_import_readmits_configuration_consent_staff_and_report_custody` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 457; 20 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Engineerednonchemicalchannels isolate directscopegate, not independently qualifiedendtoendmodel. PDFlab source uses explicitversionedtransportdouble; realstaff/assay/study approval unavailable.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA e122930c2ea51d75eda700d9f8d094f7acece420a96cc364b2a358e34e4843ce. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-003-01 — PARTIAL

One collection supplies multiple analytes — - **GIVEN** a started owned specimen attempt and its current instruction/start authority - **WHEN** the specimen is collected and later analyzed for several analytes - **THEN** every resulting report references the same original specimen and collection event, with separately identified analytical attempts.

Current proof: One admitted collection and one analytical import retain same specimen/original time with distinct analytical attempt and separate ownership.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_actual_http_collection_staff_report_import_refresh_and_finalize` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 906; 5 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_distinct_operator_creates_subject_owned_source_and_import` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 164; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- later analyzed for several analytes: multi-analyte initial import with all reports tied to that same collection is not directly exercised by these single-measurement flow bodies.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 122d496822d8cf75a051a5f1fb85265fc750e1d6c8ebc19a98214c4dc532cf6f. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-003-02 — PASS

Wrong specimen or impossible event time — - **GIVEN** the draft expects specimen A or the claimed collection time falls outside admitted chronology - **WHEN** specimen B or impossible time is submitted - **THEN** identity/chronology validation refuses without relabeling the sample or replacing its original event.

Current proof: Wrong sample returns STARTED_COLLECTION_ATTEMPT_REQUIRED; impossible future/before-start times refuse; no collection exists and original started attempt remains unchanged.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_collection_rejects_forged_analytical_authority_and_invalid_metadata` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 388; 60 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_collection_chronology_and_handling_are_actual_events_not_form_progress` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 535; 35 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 624d268c051664cfc6c9fbcc7d1b514a3b86784c815277f6dc3beaeb99007ad5. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-004-01 — PASS

Current complete sample record — - **GIVEN** an admitted participant collection with complete permitted metadata - **WHEN** Record sample succeeds - **THEN** the returned receipt binds the exact sample, attempt, protocol/configuration, current consent and original metadata digest without asserting a measured concentration.

Current proof: Receipt round-trips full original request/config digest and exact attempt; no concentrations in saliva projection; client rejects changed declaration, digest/version/revision and inconsistent lineage.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_positive_collection_without_ble_is_owned_immutable_and_pending` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 264; 5 current observation(s).
- `apps/mobile/tests/participant-acquisition.test.ts::accepted collection and export companions bind all declared facts and reject duplicate or inconsistent report lineage` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 364; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA d20fdbbf052e7e2e92b213d4d8b46fbc812419de8402c03009ac0a78def782b1. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-004-02 — PASS

Customer submits a quantified laboratory result — - **GIVEN** a participant collection form or manually edited request - **WHEN** it includes THC values or laboratory/import-role assertions - **THEN** the API rejects the added authority and no measured analyte or authorized laboratory receipt is created.

Current proof: THC value and self-declared laboratory fields fail strict validation with no collection; rendered form has no concentration input and submits no concentration field.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_collection_rejects_forged_analytical_authority_and_invalid_metadata` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 388; 60 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::specimen form records actual quantities, explicit unknowns and handling while offering no participant concentration entry` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 972; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 2d338995fcc189896fda3172bd9f56da113739b7de2001f6b756f84acfa489b0. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-004-03 — PARTIAL

Lost accepted response — - **GIVEN** collection was accepted but the response was lost - **WHEN** the exact retained body/key is retried - **THEN** the original immutable receipt is reconciled without creating a second specimen, changing collection time or reopening expired authority.

Current proof: Lost reply retries original body/key; backend exact retry returns identical receipt, changed-key/body cannot create second collection.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_positive_collection_without_ble_is_owned_immutable_and_pending` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 264; 5 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::unknown specimen receipt retries the immutable declaration and key; explicit analysis cancellation never erases collection` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1114; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- without reopening expired authority: exact receipt reconciliation after original authority expires is not asserted for collection operation.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA a37f73a792df8078e5c81ac079775d08bd0ff793530fa0d567b6ec7055516a37. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-005-01 — PASS

Distinct staff imports the participant report — - **GIVEN** an admitted collection remains in its participant-owned draft and a different currently authorized staff account verifies the matching participant-owned report - **WHEN** the existing laboratory import operation accepts it - **THEN** the participant can refresh the independently approved evidence while the original collection identity/time and analytical provenance remain intact.

Current proof: Different staff uploads/verifies explicitly doubled PDF then imports participant-owned report; participant refresh sees same collection event and separately identified analysis/provenance; original collection is unchanged.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_actual_http_collection_staff_report_import_refresh_and_finalize` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 906; 5 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_distinct_operator_creates_subject_owned_source_and_import` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 164; 5 current observation(s).
- `apps/mobile/tests/participant-acquisition.test.ts::actual Python protocol, immutable acknowledgement, specimen and imported report preserve separate truthful lineage` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 87; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::reference laboratory collection has no BLE acquisition, persists a recoverable pending draft, imports separate analysis then permits explicit finalization` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 870; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 3e4ff8cdc5d996e8d53c96c896c92aec33181488caf2b30df146a57e5d56ebc7. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-005-02 — PASS

Laboratory response is unavailable — - **GIVEN** a collected sample has no accepted report or the client is offline - **WHEN** the saved check is reviewed - **THEN** it shows analysis pending/not measured and no timer, prior reading or missing response becomes a concentration or impairment estimate.

Current proof: Pending draft persists/reviews with no concentration input, empty saliva and no estimate; save/refresh retains pending until actual admitted import fixture.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::pending laboratory UI preserves the draft, refreshes actual admitted analysis and requires explicit cancellation without inventing chemistry` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1041; 4 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::reference laboratory collection has no BLE acquisition, persists a recoverable pending draft, imports separate analysis then permits explicit finalization` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 870; 1 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_positive_collection_without_ble_is_owned_immutable_and_pending` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 264; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 762b2e598859dbae1bf3082ffc469a51d81282b27489fe41001d1b5674cb813b. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-005-03 — PASS

Foreign target or caller scope — - **GIVEN** an authorized staff caller but a target from another study/generation or a mismatching specimen/report - **WHEN** initial import is attempted - **THEN** target-scope validation refuses; the staff caller's owner/generation or supplied participant identifier cannot replace actual participant authority.

Current proof: Foreign target study/generation/self owner and sample/attempt/session fail source admission; wrong imported sample/operator/method/source refuses without lab_import record. ActualHTTPcollection/persistedreceipt and releasedtypedmodel required/optionalscope; noinventedpendingvalue, currentrequiredchemistryabandonfinalization refuses withoutjob; permittedothermodes preserve202; initialimporttarget/authority negatives at actualimportboundary.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_lab_handoff.py::test_current_target_and_genuine_operator_authority_required` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 184; 45 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_foreign_specimen_attempt_and_check_refused` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 212; 15 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_import_rejects_forged_or_incompatible_analytical_evidence` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 304; 40 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_collection_first_late_submission_is_denied_but_exact_key_replay_stays_historical` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 301; 10 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_present_collection_value_cannot_also_claim_a_missing_reason` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 341; 10 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_pending_collection_cannot_satisfy_required_chemistry_and_does_not_invent_optional_values` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 788; 10 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_abandonment_cannot_finalize_when_current_model_requires_missing_chemistry` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 868; 25 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_initial_import_refuses_foreign_target_scope_not_only_source_creation` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 422; 15 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_initial_import_readmits_configuration_consent_staff_and_report_custody` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 457; 20 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Engineerednonchemicalchannels isolate directscopegate, not independently qualifiedendtoendmodel. PDFlab source uses explicitversionedtransportdouble; realstaff/assay/study approval unavailable.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4cb7156b5e3dbeae75cf2bb436155a2257c0abac93e47848a471dcba0a62a798. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-005-04 — PASS

Consent changes before import — - **GIVEN** a collection was accepted under an earlier current scope - **WHEN** withdrawn consent, retired configuration or foreign staff/report is used for import - **THEN** current authority refuses; the historic collection receipt does not restore analysis access.

Current proof: Withdrawn consent blocks accepted import replay; retired configuration/foreign target fail source-ticket admission. ActualHTTPcollection/persistedreceipt and releasedtypedmodel required/optionalscope; noinventedpendingvalue, currentrequiredchemistryabandonfinalization refuses withoutjob; permittedothermodes preserve202; initialimporttarget/authority negatives at actualimportboundary.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_lab_handoff.py::test_actual_http_delegated_ticket_completion_import_and_minimal_dedup` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 501; 5 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_current_target_and_genuine_operator_authority_required` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 184; 45 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_collection_first_late_submission_is_denied_but_exact_key_replay_stays_historical` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 301; 10 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_present_collection_value_cannot_also_claim_a_missing_reason` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 341; 10 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_pending_collection_cannot_satisfy_required_chemistry_and_does_not_invent_optional_values` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 788; 10 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_abandonment_cannot_finalize_when_current_model_requires_missing_chemistry` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 868; 25 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_initial_import_refuses_foreign_target_scope_not_only_source_creation` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 422; 15 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_initial_import_readmits_configuration_consent_staff_and_report_custody` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 457; 20 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Engineerednonchemicalchannels isolate directscopegate, not independently qualifiedendtoendmodel. PDFlab source uses explicitversionedtransportdouble; realstaff/assay/study approval unavailable.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA d59d3591f212c9360edc9e93327cb3a45df24730a1b0f7aefd759c8e4d270ccb. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-006-01 — PASS

Inadequate volume before finalization — - **GIVEN** a collection fails its approved adequacy rule - **WHEN** the protocol permits retry - **THEN** a new sample/attempt links the failed one and obtains fresh current instructions/start without silently reusing the old specimen.

Current proof: Invalid unknown-volume specimen stays immutable; linked retry creates distinct sample and instruction receipt under fresh acknowledge/grant/start and supersedes original attempt.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_invalid_collection_preserves_failure_and_linked_retry_allocates_new_sample` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 436; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA ab26a61594cf3a23d549325d99a97cf625fbb442929cb922142c9d8e846b9b84. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-006-02 — PASS

Explicit invalid collection receipt — - **GIVEN** an inadequate or expired collection cannot be claimed valid - **WHEN** the participant records an invalid disposition with actual metadata and an explicit reason, or cancels its started attempt - **THEN** the failure lineage remains immutable and later retry cannot erase it or turn it into an accepted analytical concentration.

Current proof: Explicit invalid record retains actual unknown/observed invalid quantities and quality reason; linked accepted retry cannot erase old failed receipt or make old projection analytical.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_invalid_collection_preserves_failure_and_linked_retry_allocates_new_sample` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 436; 5 current observation(s).
- `apps/mobile/tests/participant-acquisition.test.ts::rounded approved dilution and explicit invalid observations retain the server's actual semantics` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 405; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA eed47c1e41c56b6034ccb71a3a110c47325bf10b0cfaf934d53ddb558024c041. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-006-03 — PASS

Corrected finalized laboratory report — - **GIVEN** a check and original report are finalized - **WHEN** authorized staff accepts a same-specimen correction - **THEN** the immutable original remains, a separately identified companion revision is added and later reanalysis retains its own lineage.

Current proof: Correction/reanalysis create separately hashed linked revisions; original snapshot/result/revision/digests byte-equivalent before/after; original report unit/qualifier and new lineage retained.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_report_revisions.py::test_correction_and_delayed_reanalysis_preserve_original_evidence_and_exact_units` — file SHA `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`, line 463; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 94dbbcd6a6d4d14e3488d05c484ab1588f226944eb8de9a3cf4cb70abfccb394. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-007-01 — PASS

Owned evidence review and export — - **GIVEN** accepted collection metadata and permitted immutable evidence - **WHEN** the participant reviews, explicitly uploads or exports the check - **THEN** specimen identity/time, protocol/receipt scope, null reasons, volumes/handling and analytical status survive with their digests and separate provenance.

Current proof: Typed instruction/collection/import companions validate; bounded archive inspection succeeds; changing lot/version/unknown field or duplicate/inconsistent lineage is refused, preserving scoped facts/digests.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/participant-acquisition.test.ts::actual Python protocol, immutable acknowledgement, specimen and imported report preserve separate truthful lineage` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 87; 1 current observation(s).
- `apps/mobile/tests/participant-acquisition.test.ts::accepted collection and export companions bind all declared facts and reject duplicate or inconsistent report lineage` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 364; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA d1a2a8111c32cd4cae6172c2e08bc31f33eb0b906404649a1054aa42856d9c93. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-007-02 — PASS

Withdrawal while collection response is delayed — - **GIVEN** the customer withdraws or switches workspace before a pending collection callback completes - **WHEN** that callback returns - **THEN** it cannot revive the old form, accepted specimen, queue or current collection authority in the replacement scope.

Current proof: Actual workspace-scope helper rejects delayed foreign-account response and publishes no data, and locking/background invalidates scope; specimen unknown response retry retains exact body/key. Inspected recordLabCollection wraps persisted declaration/request/receipt commit in scope.wait, while applyLabReceipt rejects canceled/frozen/different-attempt ledgers. Actual late accepted collection response held across withdrawal or account/workspace switch cannot repopulate specimen/receipt, full fenced workspace/queue or selected replacement. Native/service boundary declared fictional; real current serialized controller and transport cancellation execute.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/workspace-scope.test.ts::delayed history, job or study responses cannot publish into another account` — file SHA `d009b00717789b980a437f76ee379dbf1f3771aac46021d718f649b30544339d`, line 31; 1 current observation(s).
- `apps/mobile/tests/workspace-scope.test.ts::same-owner same-generation response succeeds; locking or backgrounding invalidates the scope` — file SHA `d009b00717789b980a437f76ee379dbf1f3771aac46021d718f649b30544339d`, line 94; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::unknown specimen receipt retries the immutable declaration and key; explicit analysis cancellation never erases collection` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1114; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::late fictional collection receipt across ${interruption} cannot replace current state or restore acquisition authority` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 924; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Fictional software fixtures; no installed OS, physical stop, real participant consent, assay qualification or clinical/model approval. Supplemental probes do not replace full local/CI gates.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA bf5b9ef69224eb0caa4dbbac41e9fb8ee3e6479cb94391d1a967813b9687ae12. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-008-01 — PASS

Save and resume a pending laboratory handoff — - **GIVEN** the immutable collection receipt exists but its genuine report is pending - **WHEN** the participant saves, leaves, resumes or continues to another supported stage - **THEN** the same sample/attempt and pending status remain, acquisition is not repeated and finalization reports `LAB_ANALYSIS_PENDING` without discarding the draft.

Current proof: Same pending specimen/attempt remains draft across save/select/refresh with no reacquisition, no queue; backend finalize409 LAB_ANALYSIS_PENDING retains collected data.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/acquisition.test.ts::reference laboratory collection has no BLE acquisition, persists a recoverable pending draft, imports separate analysis then permits explicit finalization` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 870; 1 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::pending laboratory UI preserves the draft, refreshes actual admitted analysis and requires explicit cancellation without inventing chemistry` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1041; 4 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_pending_sample_blocks_finalization_until_explicit_cancellation_without_erasing_history` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 719; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 7b713ca528bde75006d3ffd3ccd17564b4ff5b32f37e7741dcf0ec481eadb905. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-008-02 — PASS

Collection submission arrives too late — - **GIVEN** the released method's maximum submission delay has elapsed since actual collection - **WHEN** the original collection request is first admitted - **THEN** the service refuses a new valid receipt rather than substituting upload time; an already accepted exact-key response remains historical evidence only.

Current proof: Actual collection time/handling chronology rejects future/before-start cases; same-key immediate replay preserves receipt. ActualHTTPcollection/persistedreceipt and releasedtypedmodel required/optionalscope; noinventedpendingvalue, currentrequiredchemistryabandonfinalization refuses withoutjob; permittedothermodes preserve202; initialimporttarget/authority negatives at actualimportboundary.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_collection_chronology_and_handling_are_actual_events_not_form_progress` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 535; 35 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_positive_collection_without_ble_is_owned_immutable_and_pending` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 264; 5 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_collection_first_late_submission_is_denied_but_exact_key_replay_stays_historical` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 301; 10 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_present_collection_value_cannot_also_claim_a_missing_reason` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 341; 10 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_pending_collection_cannot_satisfy_required_chemistry_and_does_not_invent_optional_values` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 788; 10 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_abandonment_cannot_finalize_when_current_model_requires_missing_chemistry` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 868; 25 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_initial_import_refuses_foreign_target_scope_not_only_source_creation` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 422; 15 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_initial_import_readmits_configuration_consent_staff_and_report_custody` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 457; 20 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Engineerednonchemicalchannels isolate directscopegate, not independently qualifiedendtoendmodel. PDFlab source uses explicitversionedtransportdouble; realstaff/assay/study approval unavailable.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 2fbba09efb1329cd79379c5f4cb36afe33d64606402214335ec73ace55e0f394. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-008-03 — PASS

Delayed laboratory evidence is not current state — - **GIVEN** a report's actual analysis falls outside the approved collection-to-analysis interval, or current result acquisition/delivery bounds fail - **WHEN** staff imports evidence or research execution is considered - **THEN** the relevant chronology gate refuses rather than using import time as collection/analysis time or presenting delayed evidence as current impairment.

Current proof: Analysis beyond approved interval refuses independently; evaluation preserves original target despite later assay delivery and refuses acquisition/delivery bounds; import time never substitutes target in tested projections.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_lab_handoff.py::test_import_rejects_forged_or_incompatible_analytical_evidence` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 304; 40 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_same_check_observations_and_later_assay_delivery_preserve_original_target` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 319; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA cb669fc351d4434d55e4056b3848f05d0f2fdef0d4be15b86f289ebfe405221c. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-008-04 — PASS

Strict legacy companion compatibility — - **GIVEN** a sample is collected without measured analytical values - **WHEN** its Session 0.1 projection and typed companion evidence are generated - **THEN** the strict legacy projection retains empty/null/not-measured analytical values while protocol, instruction receipts and collection metadata remain in declared companion contracts; no unknown legacy field or forged lab provenance is inserted.

Current proof: Sample-only projection retains empty saliva; typed companion validates instructions/metadata separately; strict freeze/export reject unknown/inconsistent companion fields without adding legacy analytes.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_positive_collection_without_ble_is_owned_immutable_and_pending` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 264; 5 current observation(s).
- `apps/mobile/tests/participant-acquisition.test.ts::actual Python protocol, immutable acknowledgement, specimen and imported report preserve separate truthful lineage` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 87; 1 current observation(s).
- `apps/mobile/tests/participant-acquisition.test.ts::accepted collection and export companions bind all declared facts and reject duplicate or inconsistent report lineage` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 364; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA e7d5bb851aac14a13ae92a1914333afd9f3b238b02fa55cb38f156b75231aafd. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-008-05 — PARTIAL

Required versus optional model channel — - **GIVEN** a collection remains pending - **WHEN** an independently approved 1.1 manifest requires its chemical measurement or explicitly permits that channel to be missing - **THEN** pending collection cannot satisfy the required measurement; any separately eligible result still obeys exact approved missing-channel, provenance, tuple, freshness and delivery rules without deriving a value from pending status.

Current proof: Model scope refuses missing/censored required features, incompatible assay tuple/provenance and bad acquisition/delivery timing; complete baseline feature values are exact. Inspected scope_check requires exactly one quantified analyte and valid sample for each required chemical channel; no pending collection value is synthesized. ActualHTTPcollection/persistedreceipt and releasedtypedmodel required/optionalscope; noinventedpendingvalue, currentrequiredchemistryabandonfinalization refuses withoutjob; permittedothermodes preserve202; initialimporttarget/authority negatives at actualimportboundary.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_engine.py::test_every_acquisition_gate_has_rejection` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 364; 90 current observation(s).
- `services/api/tests/test_model_engine.py::test_feature_missingness_and_temporal_baseline_gates` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 410; 5 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_collection_first_late_submission_is_denied_but_exact_key_replay_stays_historical` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 301; 10 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_present_collection_value_cannot_also_claim_a_missing_reason` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 341; 10 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_pending_collection_cannot_satisfy_required_chemistry_and_does_not_invent_optional_values` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 788; 10 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_abandonment_cannot_finalize_when_current_model_requires_missing_chemistry` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 868; 25 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_initial_import_refuses_foreign_target_scope_not_only_source_creation` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 422; 15 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_initial_import_readmits_configuration_consent_staff_and_report_custody` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 457; 20 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Pending chemistry required-versus-optional admission, no invented value, delivery lateness and provenance/method refusal are directly tested at the real scope gate using an independently released typed manifest. A complete independently admitted result pipeline with the pending optional branch and all tuple/freshness rules is not executed by that isolated scope fixture.

Prerequisite/evidence type: software_integration_evidence, study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Scope limits: Engineerednonchemicalchannels isolate directscopegate, not independently qualifiedendtoendmodel. PDFlab source uses explicitversionedtransportdouble; realstaff/assay/study approval unavailable.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA cece3717cdc3a694082e05b25937048174fc353c0e3e8716bc9fdad548c3639f. Actual current source and raw evidence supply this disposition.

## OTGD-040-SALCOL-008-06 — PASS

Explicitly abandon pending analysis — - **GIVEN** an actual collected specimen is awaiting analysis and the participant explicitly confirms abandonment - **WHEN** a current owned immutable abandonment proof settles the pending analytical handoff - **THEN** the actual sample and original collection attempt remain unchanged, analysis is shown canceled, delayed report/replay cannot revive it, and finalization succeeds only when current configured minimum channels permit missing chemistry; otherwise it identifies the missing requirement.

Current proof: Abandonment preserves actual sample/original attempt/projection and shows canceled; old import replay403/410; missing-chemistry-permitted local save can freeze. ActualHTTPcollection/persistedreceipt and releasedtypedmodel required/optionalscope; noinventedpendingvalue, currentrequiredchemistryabandonfinalization refuses withoutjob; permittedothermodes preserve202; initialimporttarget/authority negatives at actualimportboundary.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_pending_sample_blocks_finalization_until_explicit_cancellation_without_erasing_history` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 719; 5 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::unknown analysis cancellation preserves its exact body and key and never relabels the collected specimen` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1005; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::refreshing analysis canceled on another device retains the original specimen and scoped abandonment proof` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1034; 1 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_http_abandonment_denies_same_key_import_replay` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 555; 5 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_collection_first_late_submission_is_denied_but_exact_key_replay_stays_historical` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 301; 10 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_present_collection_value_cannot_also_claim_a_missing_reason` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 341; 10 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_pending_collection_cannot_satisfy_required_chemistry_and_does_not_invent_optional_values` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 788; 10 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_abandonment_cannot_finalize_when_current_model_requires_missing_chemistry` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 868; 25 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_initial_import_refuses_foreign_target_scope_not_only_source_creation` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 422; 15 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_initial_import_readmits_configuration_consent_staff_and_report_custody` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 457; 20 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Engineerednonchemicalchannels isolate directscopegate, not independently qualifiedendtoendmodel. PDFlab source uses explicitversionedtransportdouble; realstaff/assay/study approval unavailable.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA fcab9adae48bd1fcecc6415eeb02922f020b211e1daeab3f60abe96e27bf868e. Actual current source and raw evidence supply this disposition.

