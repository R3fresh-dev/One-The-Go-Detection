import {
  assertBytes,
  digest,
  IntegrityError,
  requireObject,
  knownKeys,
} from "./integrity";
import Ajv2020 from "ajv/dist/2020";
import addFormats from "ajv-formats";
import collectionSchema from "../contracts/CollectionReceipt.schema.json";
import type { CaptureAttempt, CheckRecord, JsonObject } from "./types";
const ajv = new Ajv2020({
  strict: false,
  allErrors: true,
  allowUnionTypes: true,
});
addFormats(ajv);
const collectionValidator = ajv.compile(collectionSchema);
const instructionValidator = ajv.compile({
  $defs: collectionSchema.$defs,
  $ref: "#/$defs/InstructionReceipt",
});
export function verifyCollectionAbandonment(
  value: unknown,
  collection: JsonObject,
  sessionId: string,
): JsonObject {
  const row = requireObject(value),
    request = requireObject(collection.request);
  assertBytes(row, 32768);
  knownKeys(row, [
    "abandonment_id",
    "session_id",
    "sample_id",
    "collection_receipt_id",
    "collection_sha256",
    "configuration_submitted_sha256",
    "accepted_at",
    "confirmation",
    "reason",
    "state",
  ]);
  const utc =
      typeof row.accepted_at === "string"
        ? /^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,6}))?Z$/.exec(
            row.accepted_at,
          )
        : null,
    time = Date.parse(String(row.accepted_at));
  if (
    !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
      String(row.abandonment_id),
    ) ||
    row.session_id !== sessionId ||
    row.sample_id !== request.sample_id ||
    row.collection_receipt_id !== collection.collection_receipt_id ||
    row.confirmation !== true ||
    row.state !== "analysis_canceled" ||
    !["USER_CANCELED", "PARTICIPANT_DECLINED", "SPECIMEN_UNAVAILABLE"].includes(
      String(row.reason),
    ) ||
    row.collection_sha256 !== digest(collection) ||
    row.configuration_submitted_sha256 !==
      collection.configuration_submitted_sha256 ||
    !utc ||
    !Number.isFinite(time) ||
    new Date(time).toISOString() !==
      `${utc[1]}.${(utc[2] ?? "").padEnd(3, "0").slice(0, 3)}Z` ||
    time < Date.parse(String(collection.accepted_at))
  )
    throw new IntegrityError(
      "LAB_ABANDONMENT_MISMATCH",
      "The analysis cancellation differs from its original owned specimen or immutable receipt.",
    );
  return row as JsonObject;
}
export function verifyCollectionRecord(value: unknown): void {
  if (!collectionValidator(value))
    throw new IntegrityError(
      "PARTICIPANT_EVIDENCE_INVALID",
      "The immutable specimen receipt has unsupported fields or identity.",
    );
  const row = requireObject(value),
    attempt = requireObject(row.attempt),
    metadata = requireObject(attempt.component_metadata);
  if (
    metadata.collection_request_sha256 !== digest(row.request) ||
    row.attempt_sha256 !== digest(attempt)
  )
    throw new IntegrityError(
      "PARTICIPANT_EVIDENCE_INVALID",
      "The specimen receipt no longer pins its complete declaration and attempt.",
    );
}

/** Only an exact admitted analysis of the retained specimen may supersede a valid collection. */
export function laboratorySupersession(
  check: CheckRecord,
  attempt: CaptureAttempt,
  previous: CaptureAttempt,
): boolean {
  try {
    const projection = requireObject(attempt.component_metadata.projection),
      prior = requireObject(previous.component_metadata.projection);
    const receipts =
      check.collections ??
      (check.labCollection?.receipt ? [check.labCollection.receipt] : []);
    const receipt = receipts.find(
      (value) =>
        value.collection_receipt_id ===
        attempt.component_metadata.collection_receipt_id,
    );
    return (
      !!receipt &&
      digest(receipt.attempt) === digest(previous) &&
      previous.status === "valid" &&
      attempt.status === "valid" &&
      previous.source === "reference_lab" &&
      attempt.source === "reference_lab" &&
      previous.component === "saliva" &&
      attempt.component === "saliva" &&
      attempt.supersedes_attempt_id === previous.attempt_id &&
      attempt.component_metadata.collection_attempt_id ===
        previous.attempt_id &&
      attempt.configuration_id === previous.configuration_id &&
      attempt.configuration_hash === previous.configuration_hash &&
      attempt.record_id === previous.record_id &&
      digest(projection.sample) === digest(prior.sample) &&
      digest(attempt.component_metadata.instruction_receipt) ===
        digest(previous.component_metadata.instruction_receipt) &&
      typeof attempt.component_metadata.lab_import_id === "string" &&
      attempt.artifact_refs.length > 0 &&
      Array.isArray(prior.saliva) &&
      prior.saliva.length === 0 &&
      Array.isArray(projection.saliva) &&
      projection.saliva.length > 0 &&
      projection.saliva.every(
        (value) => requireObject(value).source === "reference_lab",
      )
    );
  } catch {
    return false;
  }
}

export function verifyParticipantCompanions(check: CheckRecord): void {
  const fail = () => {
    throw new IntegrityError(
      "PARTICIPANT_EVIDENCE_INVALID",
      "The retained preparation or specimen receipt differs from its owned attempt.",
    );
  };
  const seen = new Set<string>();
  for (const [kind, rows] of [
    ["instruction", check.instruction_receipts ?? []],
    ["collection", check.collections ?? []],
    ["abandon", check.collection_abandons ?? []],
  ] as const) {
    if (!Array.isArray(rows) || rows.length > 128) fail();
    for (const value of rows) {
      assertBytes(value, 524288);
      const row = requireObject(value),
        id = String(
          row[
            kind === "instruction"
              ? "instruction_receipt_id"
              : kind === "collection"
                ? "collection_receipt_id"
                : "abandonment_id"
          ],
        );
      if (
        !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
          id,
        ) ||
        seen.has(id) ||
        row.session_id !== check.id
      )
        fail();
      seen.add(id);
      if (kind === "instruction") {
        if (!instructionValidator(row)) fail();
        const attempt = check.attempts.find(
          (a) => a.attempt_id === row.attempt_id,
        );
        if (
          !attempt ||
          row.configuration_id !== attempt.configuration_id ||
          row.configuration_hash !== attempt.configuration_hash ||
          digest(attempt.component_metadata.instruction_receipt) !== digest(row)
        )
          fail();
      } else if (kind === "collection") {
        verifyCollectionRecord(row);
        const body = requireObject(row.request),
          attempt = check.attempts.find(
            (a) => a.attempt_id === body.attempt_id,
          );
        if (
          !attempt ||
          digest(row.attempt) !== digest(attempt) ||
          attempt.record_id !== body.sample_id ||
          row.instruction_receipt == null ||
          digest(row.instruction_receipt) !==
            digest(attempt.component_metadata.instruction_receipt) ||
          row.collection_receipt_id !==
            attempt.component_metadata.collection_receipt_id ||
          digest(row.projection) !==
            digest(attempt.component_metadata.projection) ||
          attempt.component_metadata.collection_request_sha256 !== digest(body)
        )
          fail();
      } else {
        const collection = check.collections?.find(
          (value) => value.collection_receipt_id === row.collection_receipt_id,
        );
        if (!collection) fail();
        verifyCollectionAbandonment(row, collection!, check.id);
      }
    }
  }
}
