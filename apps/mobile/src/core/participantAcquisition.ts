import {
  assertBytes,
  clone,
  digest,
  digestText,
  IntegrityError,
  knownKeys,
  requireObject,
  requiredString,
  safeInteger,
} from "./integrity";
import type { ApprovedConfiguration } from "./acquisition";
import type { CaptureAttempt, CheckRecord, JsonObject } from "./types";
import { validateSnapshot } from "./domain";
import { verifyAttemptProjection } from "./exportProjection";
import {
  verifyCollectionRecord,
  verifyCollectionAbandonment,
} from "./labEvidence";
export interface Confirmation {
  id: string;
  text: string;
}
export interface CollectionMethod {
  id: string;
  version: string;
  instructions: string;
  saliva_volume_required: boolean;
  buffer_volume_required: boolean;
  dilution_factor_required: boolean;
  dilution_definition:
    "total_mixture_over_saliva" | "undiluted" | "fixed_factor" | null;
  fixed_dilution_factor: number | null;
  saliva_volume_min_ml: number | null;
  saliva_volume_max_ml: number | null;
  buffer_volume_min_ml: number | null;
  buffer_volume_max_ml: number | null;
  collector_lot_required: boolean;
  container_required: boolean;
  expiry_required: boolean;
  permitted_containers: string[];
  required_handling_events: string[];
  permitted_null_reasons: ("unknown" | "declined" | "not_applicable")[];
}
export interface ParticipantProtocol {
  schema_version: "1.0.0";
  instruction_id: string;
  version: string;
  text: string;
  sha256: string;
  required_confirmations: Confirmation[];
  maximum_acknowledgment_age_seconds: number;
  kind: "cardiac" | "reference_lab";
  operating_scope?: "engineering_bench" | "human_participant";
  operating_state_verifier?:
    "participant_declaration_only" | "device_attested_v1";
  rest_duration_seconds?: number;
  posture_instruction?: string;
  activity_instruction?: string;
  contact_instruction?: string;
  isolation_instruction?: string;
  permitted_setups?: {
    id: string;
    description: string;
    power_state: string;
    charging_state: string;
    cable_state: string;
    contact_or_lead_configuration: string;
  }[];
  methods?: CollectionMethod[];
  maximum_collection_submission_delay_seconds?: number;
  maximum_analysis_delay_seconds?: number;
}
export interface InstructionInput {
  participant_protocol_sha256: string;
  acknowledged_at: string;
  confirmed: true;
  confirmations: string[];
  setup_id: string | null;
  rest_started_at: string | null;
  collection_method_id: string | null;
  collection_method_version: string | null;
}
export interface LabCollectionLedger {
  attempt_id: string;
  sample_id: string;
  collection_method_id: string;
  collection_method_version: string;
  state: "collecting" | "pending_lab" | "imported" | "invalid" | "canceled";
  body: JsonObject | null;
  key: string;
  receipt: JsonObject | null;
  draft?: JsonObject;
  abandon_key?: string;
  abandon_body?: JsonObject;
}
const fail = (message: string): never => {
  throw new IntegrityError("PARTICIPANT_PROTOCOL_INVALID", message);
};
const text = (value: unknown, max = 256) => requiredString(value, max);
function instant(value: unknown): number {
  const v = text(value, 40),
    m = /^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})(?:\.(\d{1,6}))?Z$/.exec(v),
    n = Date.parse(v);
  if (
    !m ||
    !Number.isFinite(n) ||
    new Date(n).toISOString() !==
      `${m[1]}T${m[2]}.${(m[3] ?? "").padEnd(3, "0").slice(0, 3)}Z`
  )
    fail("A recorded event requires a valid UTC calendar timestamp.");
  return n;
}
const unique = (value: unknown, max: number): string[] => {
  if (!Array.isArray(value) || value.length > max)
    fail("The approved choices exceed their bound.");
  const items = (value as unknown[]).map((item) => text(item));
  if (new Set(items).size !== items.length)
    fail("Approved choices must be unique.");
  return items;
};
export function participantProtocol(
  config: ApprovedConfiguration,
): ParticipantProtocol {
  const p = requireObject(config.participant_protocol);
  assertBytes(p, 32768);
  const common = [
    "schema_version",
    "instruction_id",
    "version",
    "text",
    "sha256",
    "required_confirmations",
    "maximum_acknowledgment_age_seconds",
    "kind",
  ];
  knownKeys(p, [
    ...common,
    ...(p.kind === "cardiac"
      ? [
          "operating_scope",
          "operating_state_verifier",
          "rest_duration_seconds",
          "posture_instruction",
          "activity_instruction",
          "contact_instruction",
          "isolation_instruction",
          "permitted_setups",
        ]
      : [
          "methods",
          "maximum_collection_submission_delay_seconds",
          "maximum_analysis_delay_seconds",
        ]),
  ]);
  if (
    p.schema_version !== "1.0.0" ||
    !["cardiac", "reference_lab"].includes(String(p.kind)) ||
    !/^[a-f0-9]{64}$/.test(String(config.participant_protocol_sha256)) ||
    digest(p) !== config.participant_protocol_sha256 ||
    digestText(text(p.text, 8192)) !== p.sha256
  )
    fail(
      "The approved instruction body differs from its exact policy or text digest.",
    );
  text(p.instruction_id);
  text(p.version);
  if (safeInteger(p.maximum_acknowledgment_age_seconds, 1) > 300)
    fail("The instruction freshness limit is unsupported.");
  if (
    !Array.isArray(p.required_confirmations) ||
    p.required_confirmations.length < 1 ||
    p.required_confirmations.length > 8
  )
    fail("The exact required confirmations are missing.");
  const ids = (p.required_confirmations as unknown[]).map((value) => {
    const c = requireObject(value);
    knownKeys(c, ["id", "text"]);
    if (!/^[a-z][a-z0-9_]{0,63}$/.test(text(c.id)))
      fail("A confirmation identity is unsupported.");
    text(c.text, 1024);
    return c.id;
  });
  if (new Set(ids).size !== ids.length)
    fail("The instruction repeats a confirmation.");
  if (p.kind === "cardiac") {
    if (
      !["engineering_bench", "human_participant"].includes(
        String(p.operating_scope),
      ) ||
      !["participant_declaration_only", "device_attested_v1"].includes(
        String(p.operating_state_verifier),
      ) ||
      safeInteger(p.rest_duration_seconds) > 3600
    )
      fail("The cardiac preparation scope is unsupported.");
    for (const key of [
      "posture_instruction",
      "activity_instruction",
      "contact_instruction",
      "isolation_instruction",
    ])
      text(p[key], 2048);
    for (const id of [
      "rest_completed",
      "posture_confirmed",
      "activity_confirmed",
      "contact_confirmed",
      "isolation_confirmed",
    ])
      if (!ids.includes(id))
        fail("A required cardiac preparation declaration is missing.");
    if (
      !Array.isArray(p.permitted_setups) ||
      p.permitted_setups.length < 1 ||
      p.permitted_setups.length > 16
    )
      fail("The approved whole-system setup choices are missing.");
    const setups = (p.permitted_setups as unknown[]).map((value) => {
      const setup = requireObject(value);
      knownKeys(setup, [
        "id",
        "description",
        "power_state",
        "charging_state",
        "cable_state",
        "contact_or_lead_configuration",
      ]);
      for (const key of [
        "id",
        "description",
        "power_state",
        "charging_state",
        "cable_state",
        "contact_or_lead_configuration",
      ])
        text(setup[key], key === "description" ? 2048 : 256);
      return setup.id;
    });
    if (new Set(setups).size !== setups.length)
      fail("Approved setup identities must be unique.");
  } else {
    if (
      safeInteger(p.maximum_collection_submission_delay_seconds, 1) > 3600 ||
      safeInteger(p.maximum_analysis_delay_seconds, 1) > 604800
    )
      fail("The collection or analysis lifetime exceeds its bound.");
    if (
      !Array.isArray(p.methods) ||
      p.methods.length < 1 ||
      p.methods.length > 16
    )
      fail("No approved collection method is available.");
    const methods = (p.methods as unknown[]).map((value) => {
      const m = requireObject(value);
      knownKeys(m, [
        "id",
        "version",
        "instructions",
        "saliva_volume_required",
        "buffer_volume_required",
        "dilution_factor_required",
        "dilution_definition",
        "fixed_dilution_factor",
        "saliva_volume_min_ml",
        "saliva_volume_max_ml",
        "buffer_volume_min_ml",
        "buffer_volume_max_ml",
        "collector_lot_required",
        "container_required",
        "expiry_required",
        "permitted_containers",
        "required_handling_events",
        "permitted_null_reasons",
      ]);
      text(m.id);
      text(m.version);
      text(m.instructions, 4096);
      for (const key of [
        "saliva_volume_required",
        "buffer_volume_required",
        "dilution_factor_required",
        "collector_lot_required",
        "container_required",
        "expiry_required",
      ])
        if (typeof m[key] !== "boolean")
          fail("The method's required fields are unsupported.");
      for (const kind of ["saliva", "buffer"]) {
        const low = m[`${kind}_volume_min_ml`],
          high = m[`${kind}_volume_max_ml`];
        if (
          (low === null) !== (high === null) ||
          (low !== null &&
            (typeof low !== "number" ||
              typeof high !== "number" ||
              !Number.isFinite(low) ||
              !Number.isFinite(high) ||
              low < 0 ||
              high <= 0 ||
              high > 100 ||
              low > high))
        )
          fail("The approved volume limits are incomplete or unordered.");
      }
      if (
        m.dilution_definition !== null &&
        !["total_mixture_over_saliva", "undiluted", "fixed_factor"].includes(
          String(m.dilution_definition),
        )
      )
        fail("Unsupported dilution convention.");
      if (
        (m.dilution_definition === "fixed_factor") !==
          (m.fixed_dilution_factor !== null) ||
        (m.fixed_dilution_factor !== null &&
          (typeof m.fixed_dilution_factor !== "number" ||
            !Number.isFinite(m.fixed_dilution_factor) ||
            m.fixed_dilution_factor < 1 ||
            m.fixed_dilution_factor > 100000))
      )
        fail("Fixed dilution needs its exact approved finite factor.");
      if (m.dilution_factor_required && m.dilution_definition === null)
        fail("The dilution convention is missing.");
      unique(m.permitted_containers, 32);
      unique(m.required_handling_events, 16);
      if (
        !unique(m.permitted_null_reasons, 3).length ||
        unique(m.permitted_null_reasons, 3).some(
          (reason) =>
            !["unknown", "declined", "not_applicable"].includes(reason),
        )
      )
        fail("The approved null reason is unsupported.");
      return m.id;
    });
    if (new Set(methods).size !== methods.length)
      fail("Approved method identities must be unique.");
  }
  return clone(p) as unknown as ParticipantProtocol;
}
export function validateInstructionInput(
  config: ApprovedConfiguration,
  input: InstructionInput,
  channel: string,
): ParticipantProtocol {
  const p = participantProtocol(config);
  if (
    (["cardiac", "ecg"].includes(channel) && p.kind !== "cardiac") ||
    (channel === "saliva" && p.kind !== "reference_lab")
  )
    fail(
      "These instructions do not describe the requested acquisition channel.",
    );
  knownKeys(requireObject(input), [
    "participant_protocol_sha256",
    "acknowledged_at",
    "confirmed",
    "confirmations",
    "setup_id",
    "rest_started_at",
    "collection_method_id",
    "collection_method_version",
  ]);
  if (
    input.confirmed !== true ||
    input.participant_protocol_sha256 !== config.participant_protocol_sha256 ||
    digest([...unique(input.confirmations, 8)].sort()) !==
      digest(p.required_confirmations.map((c) => c.id).sort()) ||
    instant(input.acknowledged_at) > Date.now() + 5000 ||
    instant(input.acknowledged_at) <
      Date.now() - p.maximum_acknowledgment_age_seconds * 1000
  )
    fail("Confirm the exact current instructions before starting.");
  if (p.kind === "cardiac") {
    if (
      input.collection_method_id !== null ||
      input.collection_method_version !== null ||
      !p.permitted_setups!.some((s) => s.id === input.setup_id) ||
      !input.rest_started_at ||
      instant(input.rest_started_at) >
        instant(input.acknowledged_at) - p.rest_duration_seconds! * 1000 ||
      instant(input.rest_started_at) <
        instant(input.acknowledged_at) -
          p.rest_duration_seconds! * 1000 -
          300000
    )
      fail("Complete the approved rest period and select the exact setup.");
    if (channel === "ecg" && p.operating_scope === "human_participant")
      throw new IntegrityError(
        "ECG_OPERATING_STATE_VERIFIER_UNAVAILABLE",
        "This human ECG setup requires independently verified power, charging, cable and isolation state. Participant declarations do not establish those hardware states.",
      );
  } else if (
    input.setup_id !== null ||
    input.rest_started_at !== null ||
    !p.methods!.some(
      (m) =>
        m.id === input.collection_method_id &&
        m.version === input.collection_method_version,
    )
  )
    fail(
      "Reference-laboratory collection must not claim a cardiac preparation setup.",
    );
  return p;
}
export function verifyInstructionReceipt(
  value: unknown,
  body: JsonObject,
  sessionId: string,
  consentId: string,
): JsonObject {
  const receipt = requireObject(value);
  knownKeys(receipt, [
    ...Object.keys(body),
    "instruction_receipt_id",
    "session_id",
    "consent_record_id",
    "accepted_at",
  ]);
  if (
    receipt.session_id !== sessionId ||
    receipt.consent_record_id !== consentId ||
    !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
      String(receipt.instruction_receipt_id),
    ) ||
    instant(receipt.accepted_at) > Date.now() + 5000 ||
    Object.entries(body).some(
      ([key, value]) => digest(receipt[key]) !== digest(value),
    )
  )
    throw new IntegrityError(
      "INSTRUCTION_RECEIPT_MISMATCH",
      "The service acknowledged different instructions or ownership. Acquisition remains stopped.",
    );
  return clone(receipt) as JsonObject;
}

export const COLLECTION_NULL_FIELDS = [
  "saliva_volume_ml",
  "buffer_volume_ml",
  "dilution_factor",
  "collector_id",
  "collector_lot",
  "container_id",
  "cartridge_lot",
  "cartridge_expiry",
] as const;
export function validateCollectionBody(
  value: unknown,
  method: CollectionMethod,
  protocol: ParticipantProtocol,
): JsonObject {
  const body = requireObject(value);
  assertBytes(body, 65536);
  knownKeys(body, [
    "attempt_id",
    "sample_id",
    "instruction_receipt_id",
    "collection_method_id",
    "collection_method_version",
    "collected_at",
    "status",
    "quality_flags",
    ...COLLECTION_NULL_FIELDS,
    "missing_reasons",
    "storage_handling_events",
  ]);
  if (
    body.collection_method_id !== method.id ||
    body.collection_method_version !== method.version ||
    !["valid", "invalid"].includes(String(body.status))
  )
    fail("The declared specimen does not match the reviewed method.");
  const collected = instant(body.collected_at);
  if (
    collected > Date.now() + 5000 ||
    Date.now() - collected >
      protocol.maximum_collection_submission_delay_seconds! * 1000
  )
    fail("Collection time is outside the approved submission interval.");
  const missing = requireObject(body.missing_reasons);
  if (
    digest(Object.keys(missing).sort()) !==
      digest(COLLECTION_NULL_FIELDS.filter((k) => body[k] === null).sort()) ||
    Object.values(missing).some(
      (reason) => !method.permitted_null_reasons.includes(reason as never),
    )
  )
    fail("Every unknown collection field needs its approved explicit reason.");
  for (const field of COLLECTION_NULL_FIELDS) {
    if (body[field] === null) continue;
    if (
      ["saliva_volume_ml", "buffer_volume_ml", "dilution_factor"].includes(
        field,
      )
    ) {
      if (
        typeof body[field] !== "number" ||
        !Number.isFinite(body[field]) ||
        Number(body[field]) <
          (field === "buffer_volume_ml" ? 0 : Number.MIN_VALUE) ||
        Number(body[field]) > (field === "dilution_factor" ? 100000 : 100)
      )
        fail("Collection quantities are outside their finite bounds.");
    } else if (field === "cartridge_expiry") instant(body[field]);
    else text(body[field]);
  }
  const flags = unique(body.quality_flags, 64);
  if (body.status === "invalid" && !flags.length)
    fail("An inadequate collection needs its actual reason.");
  if (
    !Array.isArray(body.storage_handling_events) ||
    body.storage_handling_events.length > 64
  )
    fail("Collection handling exceeds its bound.");
  const events = (body.storage_handling_events as unknown[]).map((value) => {
    const event = requireObject(value);
    knownKeys(event, ["event", "occurred_at", "temperature_c", "duration_min"]);
    const at = instant(event.occurred_at);
    if (
      at < collected ||
      at > Date.now() + 5000 ||
      !method.required_handling_events.includes(text(event.event))
    )
      fail("Handling must retain an actual approved event and time.");
    for (const [field, low, high] of [
      ["temperature_c", -273.15, 100],
      ["duration_min", 0, 525600],
    ] as const)
      if (
        event[field] !== null &&
        (typeof event[field] !== "number" ||
          !Number.isFinite(event[field]) ||
          Number(event[field]) < low ||
          Number(event[field]) > high)
      )
        fail("Handling observations are outside finite limits.");
    return event.event;
  });
  if (new Set(events).size !== events.length)
    fail("Handling events must not repeat.");
  if (body.status === "valid") {
    for (const [field, required] of [
      ["saliva_volume_ml", method.saliva_volume_required],
      ["buffer_volume_ml", method.buffer_volume_required],
      ["dilution_factor", method.dilution_factor_required],
      ["collector_lot", method.collector_lot_required],
      ["container_id", method.container_required],
      ["cartridge_expiry", method.expiry_required],
    ] as const)
      if (required && body[field] === null)
        fail("This method cannot accept an unknown required collection value.");
    for (const kind of ["saliva", "buffer"] as const) {
      const value = body[`${kind}_volume_ml`],
        low = method[`${kind}_volume_min_ml`],
        high = method[`${kind}_volume_max_ml`];
      if (
        value !== null &&
        low !== null &&
        (Number(value) < low || Number(value) > high!)
      )
        fail("The observed volume is outside the approved method.");
    }
    if (
      (body.container_id !== null &&
        !method.permitted_containers.includes(String(body.container_id))) ||
      (body.cartridge_expiry !== null &&
        instant(body.cartridge_expiry) <= collected) ||
      digest([...events].sort()) !==
        digest([...method.required_handling_events].sort())
    )
      fail("Collection supplies or required handling do not match the method.");
  }
  if (body.status === "valid" && body.dilution_factor !== null) {
    const expected =
      method.dilution_definition === "undiluted"
        ? 1
        : method.dilution_definition === "fixed_factor"
          ? method.fixed_dilution_factor
          : body.saliva_volume_ml !== null && body.buffer_volume_ml !== null
            ? (Number(body.saliva_volume_ml) + Number(body.buffer_volume_ml)) /
              Number(body.saliva_volume_ml)
            : null;
    if (
      (method.dilution_definition === "undiluted" &&
        body.buffer_volume_ml !== null &&
        body.buffer_volume_ml !== 0) ||
      expected === null ||
      Math.abs(Number(body.dilution_factor) - Number(expected)) >
        Math.max(1e-8, Math.abs(Number(expected)) * 1e-6)
    )
      fail(
        "The recorded dilution factor contradicts the approved convention and observed volumes.",
      );
  }
  return clone(body) as JsonObject;
}

/** A server-admitted owned lab report is reconciled; participant fields never create analytes. */
export function collectionReceipt(
  value: unknown,
  check: CheckRecord,
  body: JsonObject,
): {
  receipt: JsonObject;
  attempt: CaptureAttempt;
  collectionAttempt: CaptureAttempt;
  state: LabCollectionLedger["state"];
} {
  const receipt = requireObject(value);
  assertBytes(receipt, 524288);
  knownKeys(receipt, [
    "collection_receipt_id",
    "session_id",
    "request",
    "state",
    "accepted_at",
    "authorization_id",
    "configuration_submitted_sha256",
    "configuration_version",
    "participant_protocol_sha256",
    "instruction_receipt",
    "projection",
    "attempt",
    "imports",
    "attempt_revision",
    "attempt_sha256",
    "abandonment",
    "collection_attempt",
    "collection_attempt_revision",
    "collection_attempt_sha256",
  ]);
  const original = check.attempts.find((a) => a.attempt_id === body.attempt_id),
    ledger = check.acquisition?.attempts[String(body.attempt_id)],
    grant = ledger?.authorization;
  if (
    !original ||
    !grant ||
    receipt.session_id !== check.id ||
    digest(receipt.request) !== digest(body) ||
    receipt.authorization_id !== grant.authorization_id ||
    receipt.configuration_submitted_sha256 !==
      grant.configuration_submitted_sha256 ||
    receipt.configuration_version !== grant.configuration_version ||
    receipt.participant_protocol_sha256 !== grant.participant_protocol_sha256 ||
    digest(receipt.instruction_receipt) !==
      digest(ledger!.instruction_receipt) ||
    ![
      "pending_lab",
      "invalid_collection",
      "analysis_available",
      "analysis_canceled",
    ].includes(String(receipt.state))
  )
    fail(
      "The collection receipt changes the owned specimen, method or authorization.",
    );
  instant(receipt.accepted_at);
  const imports = receipt.imports ?? [];
  if (
    !Array.isArray(imports) ||
    imports.length !== (receipt.state === "analysis_available" ? 1 : 0)
  )
    fail("The laboratory status exceeds its bounded lineage.");
  const validRevision = (value: unknown) =>
    Number.isSafeInteger(value) && Number(value) >= 1 && Number(value) <= 128;
  if (
    !validRevision(receipt.attempt_revision) ||
    (receipt.collection_attempt_revision !== undefined &&
      !validRevision(receipt.collection_attempt_revision))
  )
    fail("The laboratory revision is outside its immutable bound.");
  const terminal =
    receipt.state === "analysis_available"
      ? requireObject((imports as unknown[])[0]).attempt
      : receipt.attempt;
  const attempt = requireObject(terminal) as unknown as CaptureAttempt;
  if (
    (receipt.state === "analysis_available"
      ? attempt.attempt_id === original!.attempt_id ||
        attempt.supersedes_attempt_id !== original!.attempt_id ||
        attempt.component_metadata.collection_attempt_id !==
          original!.attempt_id
      : attempt.attempt_id !== original!.attempt_id) ||
    attempt.record_id !== body.sample_id ||
    attempt.session_id !== check.id ||
    attempt.component !== "saliva" ||
    attempt.configuration_id !== original!.configuration_id ||
    attempt.configuration_hash !== original!.configuration_hash ||
    !["valid", "invalid", "canceled"].includes(attempt.status) ||
    attempt.source !== "reference_lab" ||
    attempt.component_metadata.armed_at !== ledger!.started_body.started_at ||
    digest(attempt.component_metadata.instruction_receipt) !==
      digest(ledger!.instruction_receipt)
  )
    fail(
      "The laboratory attempt differs from its immutable collection lineage.",
    );
  const collectedAttempt = requireObject(
    receipt.collection_attempt ?? receipt.attempt,
  ) as unknown as CaptureAttempt;
  const immutableCollection = {
    collection_receipt_id: receipt.collection_receipt_id,
    session_id: receipt.session_id,
    request: receipt.request,
    state: body.status === "valid" ? "pending_lab" : "invalid_collection",
    accepted_at: receipt.accepted_at,
    authorization_id: receipt.authorization_id,
    configuration_submitted_sha256: receipt.configuration_submitted_sha256,
    configuration_version: receipt.configuration_version,
    participant_protocol_sha256: receipt.participant_protocol_sha256,
    instruction_receipt: receipt.instruction_receipt,
    projection: receipt.projection,
    attempt: collectedAttempt,
    attempt_revision:
      receipt.collection_attempt_revision ?? receipt.attempt_revision,
    attempt_sha256: receipt.collection_attempt_sha256 ?? receipt.attempt_sha256,
  };
  verifyCollectionRecord(immutableCollection);
  if (receipt.state === "analysis_canceled")
    verifyCollectionAbandonment(
      receipt.abandonment,
      immutableCollection as unknown as JsonObject,
      check.id,
    );
  else if (receipt.abandonment !== undefined && receipt.abandonment !== null)
    fail(
      "A pending or imported specimen cannot silently carry cancellation evidence.",
    );
  if (
    collectedAttempt.attempt_id !== original!.attempt_id ||
    collectedAttempt.record_id !== body.sample_id ||
    collectedAttempt.source !== "reference_lab" ||
    collectedAttempt.component !== "saliva" ||
    collectedAttempt.configuration_id !== original!.configuration_id ||
    collectedAttempt.configuration_hash !== original!.configuration_hash ||
    collectedAttempt.component_metadata.armed_at !==
      ledger!.started_body.started_at ||
    digest(collectedAttempt.component_metadata.instruction_receipt) !==
      digest(ledger!.instruction_receipt) ||
    collectedAttempt.component_metadata.collection_receipt_id !==
      receipt.collection_receipt_id ||
    collectedAttempt.component_metadata.collection_request_sha256 !==
      digest(body) ||
    digest(collectedAttempt.component_metadata.projection) !==
      digest(receipt.projection) ||
    digest(collectedAttempt) !==
      (receipt.collection_attempt_sha256 ?? receipt.attempt_sha256) ||
    digest(attempt) !== receipt.attempt_sha256
  )
    fail("Collection and analysis immutable digests or lineage differ.");
  verifyAttemptProjection(collectedAttempt, check.snapshot);
  if (
    original!.status !== "started" &&
    digest(original) !== digest(collectedAttempt)
  )
    fail("Analysis changes the already retained collection attempt.");
  const projection = verifyAttemptProjection(attempt, check.snapshot),
    sample = requireObject(projection.sample);
  if (
    sample.sample_id !== body.sample_id ||
    sample.collection_method_id !== body.collection_method_id ||
    sample.collected_at !== body.collected_at
  )
    fail(
      "Laboratory analysis changes the original specimen identity or collection time.",
    );
  if (
    receipt.state !== "analysis_available" &&
    digest(projection.saliva) !== digest([])
  )
    fail(
      "A pending or canceled collection must not invent laboratory analytes.",
    );
  if (receipt.state === "analysis_available") {
    const imported = requireObject((imports as unknown[])[0]);
    knownKeys(imported, [
      "import_id",
      "measurements",
      "attempt",
      "source_report_artifact_id",
      "attempt_revision",
      "attempt_sha256",
    ]);
    if (
      imported.import_id !== attempt.component_metadata.lab_import_id ||
      digest(imported.attempt) !== digest(receipt.attempt) ||
      imported.attempt_revision !== receipt.attempt_revision ||
      imported.attempt_sha256 !== receipt.attempt_sha256 ||
      !imported.source_report_artifact_id ||
      !attempt.artifact_refs.includes(
        String(imported.source_report_artifact_id),
      ) ||
      digest(imported.measurements) !== digest(projection.saliva) ||
      !Array.isArray(projection.saliva) ||
      !projection.saliva.length ||
      projection.saliva.some((m) => requireObject(m).source !== "reference_lab")
    )
      fail(
        "Analysis requires the independently admitted report and unchanged measurements.",
      );
  }
  const snapshot = clone(check.snapshot);
  snapshot.sample = clone(projection.sample) as typeof snapshot.sample;
  snapshot.saliva = clone(projection.saliva) as JsonObject[];
  snapshot.capture_completed_at = new Date(
    Math.max(Date.now(), Date.parse(String(attempt.ended_at))),
  ).toISOString();
  validateSnapshot(snapshot);
  return {
    receipt: clone(receipt) as JsonObject,
    attempt: clone(attempt),
    collectionAttempt: clone(
      requireObject(receipt.collection_attempt ?? receipt.attempt),
    ) as unknown as CaptureAttempt,
    state:
      receipt.state === "analysis_available"
        ? "imported"
        : receipt.state === "pending_lab"
          ? "pending_lab"
          : receipt.state === "analysis_canceled"
            ? "canceled"
            : "invalid",
  };
}
