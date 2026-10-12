import test from "node:test";
import assert from "node:assert/strict";
import fixture from "../testfixtures/backend-participant-acquisition.json";
import base from "../testfixtures/backend-research-result.json";
import {
  clone,
  digest,
  digestText,
  requireObject,
} from "../src/core/integrity";
import {
  participantProtocol,
  validateInstructionInput,
  validateCollectionBody,
  verifyInstructionReceipt,
  collectionReceipt,
} from "../src/core/participantAcquisition";
import { PreparationClock } from "../src/core/preparationClock";
import { freezeCheck, verifyCheck } from "../src/core/domain";
import {
  laboratorySupersession,
  verifyParticipantCompanions,
} from "../src/core/labEvidence";
import {
  createLocalExport,
  inspectExportArchive,
} from "../src/services/export";
import { queueCheck } from "../src/services/sync";
import type { ApprovedConfiguration } from "../src/core/acquisition";
import type { CheckRecord, JsonObject } from "../src/core/types";
import { randomUUID } from "node:crypto";

const flow = fixture.import_flow;
function config(): ApprovedConfiguration {
  return clone(
    flow.capabilities.channels.saliva.configurations[0],
  ) as unknown as ApprovedConfiguration;
}
function owned() {
  const check = clone(base.check) as unknown as CheckRecord,
    terminal = clone(flow.collection_receipt.attempt);
  Object.assign(check, {
    id: flow.frozen_snapshot.session_id,
    frozen: false,
    snapshot: clone(flow.frozen_snapshot),
    context: clone(flow.context),
    attempts: [terminal],
    manifest: null,
    result: null,
    snapshot_sha256: null,
    evidence_sha256: null,
    delivery: "local_draft",
    selected_cardiac_attempt_id: null,
    instruction_receipts: [clone(flow.instruction_receipt)],
    collections: [clone(flow.collection_receipt)],
    collection_abandons: [],
  });
  check.snapshot.saliva = [];
  check.snapshot.sample = clone(
    flow.collection_receipt.projection.sample,
  ) as typeof check.snapshot.sample;
  check.alcohol = null;
  check.acquisition = {
    register_key: randomUUID(),
    context_key: randomUUID(),
    registered: true,
    context_registered: true,
    attempts: {
      [terminal.attempt_id]: {
        start_key: randomUUID(),
        grant_key: randomUUID(),
        invoke_key: randomUUID(),
        terminal_key: randomUUID(),
        attestation_key: randomUUID(),
        started_body: {
          ...terminal,
          started_at: terminal.component_metadata.armed_at,
        } as unknown as JsonObject,
        remote_revision: 2,
        authorization: clone(flow.authorization),
        instruction_receipt: clone(flow.instruction_receipt),
      },
    },
  };
  return check;
}
test("actual Python protocol, immutable acknowledgement, specimen and imported report preserve separate truthful lineage", (t) => {
  t.mock.timers.enable({
    apis: ["Date"],
    now: Date.parse(flow.import_status.accepted_at),
  });
  const current = config(),
    protocol = participantProtocol(current);
  const body = validateCollectionBody(
    flow.collection_request,
    protocol.methods![0]!,
    protocol,
  );
  const {
    attempt_id,
    configuration_id,
    configuration_version,
    configuration_hash,
    configuration_submitted_sha256,
    ...input
  } = flow.ack_request;
  validateInstructionInput(current, input as any, "saliva");
  verifyInstructionReceipt(
    flow.instruction_receipt,
    flow.ack_request,
    flow.context.session_id,
    flow.instruction_receipt.consent_record_id,
  );
  const check = owned();
  assert.equal(
    collectionReceipt(flow.pending_status, check, body).state,
    "pending_lab",
  );
  const result = collectionReceipt(flow.import_status, check, body);
  assert.equal(result.state, "imported");
  assert.notEqual(
    result.attempt.attempt_id,
    result.collectionAttempt.attempt_id,
  );
  check.attempts.push(result.attempt);
  check.snapshot.saliva = clone(
    requireObject(result.attempt.component_metadata.projection).saliva,
  ) as JsonObject[];
  assert.equal(
    laboratorySupersession(check, result.attempt, result.collectionAttempt),
    true,
  );
  verifyParticipantCompanions(check);
  const frozen = freezeCheck(check, new Date().toISOString(), randomUUID);
  verifyCheck(frozen);
  const workspace: any = {
    workspace: check.workspace,
    generation: check.generation,
    checks: [frozen],
    profile: null,
    capabilities: { account_ref: frozen.snapshot.subject_ref },
    queue: [],
    rawArtifacts: [],
    rawRecordingFences: {},
  };
  const archive = createLocalExport(
    workspace,
    { kind: "single", session_ids: [check.id] },
    new Date().toISOString(),
  );
  assert.ok(inspectExportArchive(archive).fileCount > 0);
});
test("pending specimen cannot freeze or enqueue finalization and cancellation keeps its actual valid collected sample", (t) => {
  t.mock.timers.enable({
    apis: ["Date"],
    now: Date.parse(fixture.abandon_flow.abandon_status.accepted_at),
  });
  const check = owned();
  check.labCollection = {
    attempt_id: check.attempts[0]!.attempt_id,
    sample_id: check.snapshot.sample.sample_id,
    collection_method_id: flow.collection_request.collection_method_id,
    collection_method_version: "v1",
    state: "pending_lab",
    body: clone(flow.collection_request),
    receipt: clone(flow.pending_status),
    key: randomUUID(),
  };
  assert.throws(
    () => freezeCheck(check, new Date().toISOString(), randomUUID),
    /draft/,
  );
  assert.throws(
    () =>
      queueCheck(
        { checks: [check] } as any,
        check.id,
        randomUUID,
        new Date().toISOString(),
      ),
    /Laboratory/,
  );
  const f = fixture.abandon_flow,
    canceled = owned();
  Object.assign(canceled, {
    id: f.context.session_id,
    context: clone(f.context),
    attempts: [clone(f.collection_receipt.attempt)],
  });
  canceled.snapshot.session_id = canceled.id;
  canceled.snapshot.created_at = f.context.context_confirmed_at;
  canceled.snapshot.target_at = f.context.context_confirmed_at;
  canceled.snapshot.sample = clone(
    f.collection_receipt.projection.sample,
  ) as typeof canceled.snapshot.sample;
  canceled.acquisition!.attempts = {
    [f.collection_request.attempt_id]: {
      ...Object.values(canceled.acquisition!.attempts)[0]!,
      started_body: {
        started_at: f.collection_receipt.attempt.component_metadata.armed_at,
      },
      authorization: clone(f.authorization),
      instruction_receipt: clone(f.instruction_receipt),
    },
  };
  const result = collectionReceipt(
    f.abandon_status,
    canceled,
    f.collection_request,
  );
  assert.equal(result.state, "canceled");
  assert.equal(
    requireObject(result.attempt.component_metadata.projection)
      .saliva instanceof Array,
    true,
  );
  assert.equal(result.attempt.status, "valid");
  assert.equal(
    canceled.snapshot.sample.collected_at,
    f.collection_request.collected_at,
  );
});
test("approved quantities and unknown reasons refuse contradictory or invented collection facts", (t) => {
  t.mock.timers.enable({
    apis: ["Date"],
    now: Date.parse(flow.collection_request.collected_at),
  });
  const p = participantProtocol(config()),
    method = p.methods![0]!;
  for (const change of [
    { dilution_factor: 900 },
    { saliva_volume_ml: null },
    { missing_reasons: { collector_id: "declined" } },
    { saliva_volume_ml: Infinity },
    { container_id: "unapproved-container" },
    { cartridge_expiry: "2026-02-30T00:00:00Z" },
    { storage_handling_events: [] },
  ])
    assert.throws(() =>
      validateCollectionBody(
        { ...flow.collection_request, ...change },
        method,
        p,
      ),
    );
  const wrong = clone(flow.import_status) as any;
  wrong.imports[0].attempt.supersedes_attempt_id = randomUUID();
  assert.throws(() =>
    collectionReceipt(wrong, owned(), flow.collection_request),
  );
  wrong.imports[0].attempt = clone(flow.import_status.imports[0]!.attempt);
  wrong.imports[0].measurements = [];
  assert.throws(() =>
    collectionReceipt(wrong, owned(), flow.collection_request),
  );
});
test("document digest, selected method, exact UUID/calendar and electrical setup boundaries are enforced", (t) => {
  t.mock.timers.enable({
    apis: ["Date"],
    now: Date.parse(flow.ack_request.acknowledged_at),
  });
  const c = config(),
    bad = clone(c);
  bad.participant_protocol!.text = "Changed instructions";
  assert.throws(() => participantProtocol(bad));
  const {
    attempt_id,
    configuration_id,
    configuration_version,
    configuration_hash,
    configuration_submitted_sha256,
    ...input
  } = flow.ack_request;
  assert.throws(() =>
    validateInstructionInput(
      c,
      { ...input, collection_method_id: "other-method" } as any,
      "saliva",
    ),
  );
  for (const change of [
    { instruction_receipt_id: "-".repeat(36) },
    { accepted_at: "2026-02-30T00:00:00Z" },
    { configuration_hash: "f".repeat(64) },
  ])
    assert.throws(() =>
      verifyInstructionReceipt(
        { ...flow.instruction_receipt, ...change },
        flow.ack_request,
        flow.context.session_id,
        flow.instruction_receipt.consent_record_id,
      ),
    );
  const p: any = {
    schema_version: "1.0.0",
    instruction_id: "test",
    version: "v1",
    text: "Fictional cardiac preparation",
    sha256: digestText("Fictional cardiac preparation"),
    maximum_acknowledgment_age_seconds: 120,
    required_confirmations: [
      "rest_completed",
      "posture_confirmed",
      "activity_confirmed",
      "contact_confirmed",
      "isolation_confirmed",
    ].map((id) => ({ id, text: id })),
    kind: "cardiac",
    operating_scope: "human_participant",
    operating_state_verifier: "device_attested_v1",
    rest_duration_seconds: 0,
    posture_instruction: "test",
    activity_instruction: "test",
    contact_instruction: "test",
    isolation_instruction: "test",
    permitted_setups: [
      {
        id: "test",
        description: "test",
        power_state: "battery",
        charging_state: "off",
        cable_state: "none",
        contact_or_lead_configuration: "test",
      },
    ],
  };
  const cardiac = {
    ...c,
    participant_protocol: p,
    participant_protocol_sha256: digest(p),
  };
  const ack: any = {
    participant_protocol_sha256: digest(p),
    acknowledged_at: new Date().toISOString(),
    confirmed: true,
    confirmations: p.required_confirmations.map((item: any) => item.id),
    setup_id: "test",
    rest_started_at: new Date().toISOString(),
    collection_method_id: null,
    collection_method_version: null,
  };
  assert.throws(
    () => validateInstructionInput(cardiac, ack, "ecg"),
    /independently verified/,
  );
  for (const key of [
    "description",
    "power_state",
    "charging_state",
    "cable_state",
    "contact_or_lead_configuration",
  ]) {
    const value = clone(p);
    delete value.permitted_setups[0][key];
    assert.throws(() =>
      participantProtocol({
        ...c,
        participant_protocol: value,
        participant_protocol_sha256: digest(value),
      }),
    );
  }
});
test("accepted collection and export companions bind all declared facts and reject duplicate or inconsistent report lineage", (t) => {
  t.mock.timers.enable({
    apis: ["Date"],
    now: Date.parse(flow.import_status.accepted_at),
  });
  for (const mutate of [
    (v: any) => v.imports.push(clone(v.imports[0])),
    (v: any) => (v.imports[0].import_id = randomUUID()),
    (v: any) => (v.imports[0].attempt_revision = 127),
    (v: any) => (v.imports[0].attempt_sha256 = "0".repeat(64)),
    (v: any) => (v.attempt_revision = 0),
    (v: any) => (v.attempt_revision = 1.5),
    (v: any) => (v.attempt = clone(v.collection_attempt)),
  ]) {
    const value: any = clone(flow.import_status);
    mutate(value);
    assert.throws(() =>
      collectionReceipt(value, owned(), flow.collection_request),
    );
  }
  const pending: any = clone(flow.pending_status);
  pending.imports = [clone(flow.import_status.imports[0])];
  assert.throws(() =>
    collectionReceipt(pending, owned(), flow.collection_request),
  );
  for (const mutate of [
    (row: any) => (row.request.collector_lot = "OTHER-LOT"),
    (row: any) => (row.configuration_version = null),
    (row: any) => (row.unknown_field = true),
    (row: any) => (row.attempt_revision = 0),
  ]) {
    const value = owned();
    mutate(value.collections![0]);
    assert.throws(() => verifyParticipantCompanions(value));
  }
  const declaration = clone(flow.collection_request);
  declaration.collector_lot = "OTHER-LOT";
  const value: any = clone(flow.pending_status);
  value.request = declaration;
  assert.throws(() => collectionReceipt(value, owned(), declaration));
});
test("rounded approved dilution and explicit invalid observations retain the server's actual semantics", (t) => {
  t.mock.timers.enable({
    apis: ["Date"],
    now: Date.parse(flow.collection_request.collected_at),
  });
  const protocol = participantProtocol(config()),
    method = protocol.methods![0]!;
  assert.equal(
    validateCollectionBody(
      { ...flow.collection_request, dilution_factor: 2.000001 },
      method,
      protocol,
    ).dilution_factor,
    2.000001,
  );
  assert.equal(
    validateCollectionBody(
      {
        ...flow.collection_request,
        status: "invalid",
        quality_flags: ["OBSERVED_DILUTION_MISMATCH"],
        dilution_factor: 900,
      },
      method,
      protocol,
    ).dilution_factor,
    900,
  );
  assert.throws(() =>
    validateCollectionBody(
      { ...flow.collection_request, dilution_factor: 2.0001 },
      method,
      protocol,
    ),
  );
  assert.throws(() =>
    validateCollectionBody(
      flow.collection_request,
      {
        ...method,
        dilution_definition: "undiluted",
        buffer_volume_required: false,
      },
      protocol,
    ),
  );
  const bad = config();
  requireObject(
    requireObject(bad.participant_protocol).methods instanceof Array
      ? (requireObject(bad.participant_protocol).methods as unknown[])[0]
      : null,
  ).permitted_null_reasons = [];
  bad.participant_protocol_sha256 = digest(bad.participant_protocol);
  assert.throws(() => participantProtocol(bad));
});
test("foreground rest requires monotonic elapsed time and interruption invalidates prior wait", () => {
  let mono = 100;
  const clock = new PreparationClock(() => mono);
  assert.equal(clock.remaining(30), 30);
  clock.start();
  mono += 10000;
  assert.equal(clock.remaining(30), 20);
  const original = Date.now;
  Date.now = () => 9999999999999;
  assert.equal(clock.remaining(30), 20);
  Date.now = original;
  mono += 20000;
  assert.equal(clock.remaining(30), 0);
  clock.reset();
  assert.equal(clock.remaining(30), 30);
  mono = 100;
  clock.start();
  mono = 50;
  assert.equal(clock.remaining(30), 30);
  mono = 99999;
  assert.equal(clock.remaining(30), 30);
  clock.start();
  mono += 30000;
  assert.equal(clock.remaining(30), 0);
  mono = 100;
  clock.start();
  mono = 500;
  assert.equal(clock.remaining(30), 30);
  mono = 300;
  assert.equal(clock.remaining(30), 30);
  assert.equal(clock.active, false);
  mono = 99999;
  assert.equal(clock.remaining(30), 30);
  assert.throws(() => new PreparationClock(() => NaN).start());
  mono = 0;
  clock.start();
  mono = NaN;
  assert.equal(clock.remaining(0), 0);
  assert.equal(clock.active, false);
  mono = 500;
  assert.equal(clock.active, false);
  clock.start();
  assert.equal(clock.active, true);
});
