import {
  digest,
  digestText,
  IntegrityError,
  knownKeys,
  requireObject,
  requiredString,
  safeInteger,
  utf8,
} from "./integrity";
import type { JsonObject } from "./types";

export const RAW_KINDS = ["eye_video", "ecg_waveform"] as const;
export type RawKind = (typeof RAW_KINDS)[number];
export type RawChoices = Record<RawKind, { record: boolean; upload: boolean }>;
export const rawChoicesOff = (): RawChoices => ({
  eye_video: { record: false, upload: false },
  ecg_waveform: { record: false, upload: false },
});
export interface RawPolicy {
  policy_id: string;
  version: string;
  sha256: string;
  purpose_id: string;
  purpose: string;
  raw_kinds: (RawKind | "source_lab_report")[];
  max_retention_days: number;
  expires_at: string;
  retention_basis: "first_owned_acquisition_start";
  access_roles: string[];
  withdrawal_behavior: string;
  exceptions: string[];
  raw_notice: { version: string; sha256: string; content: string };
  content: JsonObject;
}
export interface RawRecordingStatus {
  study_id: string;
  consent_record_id: string | null;
  receipt_id: string | null;
  choices: RawChoices;
  preference_receipt: {
    receipt_id: string;
    consent_record_id: string;
    policy_id: string;
    policy_version: string;
    policy_sha256: string;
    raw_notice_version: string;
    raw_notice_sha256: string;
    acknowledged_at: string;
    accepted_at: string;
    choices: RawChoices;
  } | null;
  policy: RawPolicy | null;
  availability: Record<
    RawKind,
    { record_allowed: boolean; upload_allowed: boolean; reasons: string[] }
  >;
  artifacts: {
    artifact_id: string;
    artifact_kind: RawKind;
    state: string;
    upload_state: string;
    retention_due_at: string;
    cleanup_completed_at: string | null;
  }[];
  revocations: {
    receipt_id: string;
    artifact_kinds: RawKind[];
    accepted_at: string;
    state: "cleanup_pending" | "completed";
  }[];
  has_more_artifacts: boolean;
  next_artifact_cursor: string | null;
  accepted_receipt_id?: string;
}
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
function id(value: unknown): string {
  const text = requiredString(value, 36);
  if (!UUID.test(text))
    throw new IntegrityError(
      "RAW_RECEIPT_INVALID",
      "A raw-recording receipt identity is invalid.",
    );
  return text;
}
function sha(value: unknown): string {
  const text = requiredString(value, 64);
  if (!/^[a-f0-9]{64}$/.test(text))
    throw new IntegrityError(
      "RAW_POLICY_INVALID",
      "The raw-recording policy digest is invalid.",
    );
  return text;
}
function utc(value: unknown): string {
  const text = requiredString(value, 64);
  if (!text.endsWith("Z") || !Number.isFinite(Date.parse(text)))
    throw new IntegrityError(
      "RAW_TIME_INVALID",
      "A raw-recording timestamp is invalid.",
    );
  return text;
}
function strings(value: unknown, max = 32): string[] {
  if (!Array.isArray(value) || value.length > max)
    throw new IntegrityError(
      "RAW_METADATA_INVALID",
      "Raw-recording metadata exceeds its permitted bound.",
    );
  return value.map((item) => requiredString(item, 4096));
}
function kinds(value: unknown): RawKind[] {
  const values = strings(value, 2);
  if (
    new Set(values).size !== values.length ||
    values.some((kind) => !RAW_KINDS.includes(kind as RawKind))
  )
    throw new IntegrityError(
      "RAW_KIND_UNSUPPORTED",
      "An unsupported recording kind was returned.",
    );
  return values as RawKind[];
}
export function parseRawChoices(value: unknown): RawChoices {
  const object = requireObject(value);
  knownKeys(object, [...RAW_KINDS]);
  const result = rawChoicesOff();
  for (const kind of RAW_KINDS) {
    const item = requireObject(object[kind]);
    knownKeys(item, ["record", "upload"]);
    if (
      typeof item.record !== "boolean" ||
      typeof item.upload !== "boolean" ||
      (item.upload && !item.record)
    )
      throw new IntegrityError(
        "RAW_CHOICE_INVALID",
        "Raw upload requires an explicit recording choice.",
      );
    result[kind] = { record: item.record, upload: item.upload };
  }
  return result;
}
export function parseRawRecordingStatus(
  value: unknown,
  studyId: string,
): RawRecordingStatus {
  const object = requireObject(value);
  knownKeys(object, [
    "study_id",
    "consent_record_id",
    "receipt_id",
    "preference_receipt",
    "choices",
    "policy",
    "availability",
    "artifacts",
    "revocations",
    "accepted_receipt_id",
    "has_more_artifacts",
    "next_artifact_cursor",
  ]);
  if (object.study_id !== studyId)
    throw new IntegrityError(
      "RAW_STUDY_MISMATCH",
      "Recording status belongs to a different study.",
    );
  const choices = parseRawChoices(object.choices),
    availability = {} as RawRecordingStatus["availability"],
    available = requireObject(object.availability);
  knownKeys(available, [...RAW_KINDS]);
  for (const kind of RAW_KINDS) {
    const item = requireObject(available[kind]);
    knownKeys(item, ["record_allowed", "upload_allowed", "reasons"]);
    if (
      typeof item.record_allowed !== "boolean" ||
      typeof item.upload_allowed !== "boolean" ||
      (item.upload_allowed && !item.record_allowed)
    )
      throw new IntegrityError(
        "RAW_AVAILABILITY_INVALID",
        "Recording availability is invalid.",
      );
    availability[kind] = {
      record_allowed: item.record_allowed,
      upload_allowed: item.upload_allowed,
      reasons: strings(item.reasons),
    };
  }
  let policy: RawPolicy | null = null;
  if (object.policy !== null) {
    const p = requireObject(object.policy);
    knownKeys(p, [
      "policy_id",
      "version",
      "sha256",
      "purpose_id",
      "purpose",
      "raw_kinds",
      "max_retention_days",
      "expires_at",
      "access_roles",
      "withdrawal_behavior",
      "exceptions",
      "retention_basis",
      "raw_notice",
      "content",
    ]);
    if (p.retention_basis !== "first_owned_acquisition_start")
      throw new IntegrityError(
        "RAW_RETENTION_BASIS_INVALID",
        "Recording retention must begin at actual acquisition.",
      );
    const content = requireObject(p.content) as JsonObject,
      notice = requireObject(p.raw_notice);
    knownKeys(notice, ["version", "sha256", "content"]);
    const policySha = sha(p.sha256),
      noticeSha = sha(notice.sha256),
      noticeText = requiredString(notice.content, 65536);
    if (
      utf8(noticeText).length > 65536 ||
      digestText(noticeText) !== noticeSha ||
      digest(content) !== policySha
    )
      throw new IntegrityError(
        "RAW_POLICY_HASH_MISMATCH",
        "The approved recording policy or exact data notice could not be verified.",
      );
    for (const key of [
      "policy_id",
      "version",
      "purpose_id",
      "raw_kinds",
      "max_retention_days",
      "access_roles",
      "withdrawal_behavior",
      "exceptions",
    ])
      if (digest(p[key]) !== digest(content[key]))
        throw new IntegrityError(
          "RAW_POLICY_PROJECTION_MISMATCH",
          "The displayed retention terms differ from the verified policy.",
        );
    if (p.purpose !== content.purpose_text)
      throw new IntegrityError(
        "RAW_POLICY_PROJECTION_MISMATCH",
        "The displayed purpose differs from the approved policy.",
      );
    const expiry = utc(p.expires_at);
    if (
      typeof content.expires_at !== "number" ||
      Math.abs(Date.parse(expiry) / 1000 - content.expires_at) > 0.001 ||
      content.raw_notice_version !== notice.version ||
      content.raw_notice_sha256 !== noticeSha ||
      content.raw_notice_text !== noticeText
    )
      throw new IntegrityError(
        "RAW_POLICY_PROJECTION_MISMATCH",
        "The displayed recording notice differs from the verified policy.",
      );
    policy = {
      retention_basis: "first_owned_acquisition_start",
      policy_id: requiredString(p.policy_id),
      version: requiredString(p.version),
      sha256: policySha,
      purpose_id: requiredString(p.purpose_id),
      purpose: requiredString(p.purpose, 4096),
      raw_kinds: strings(p.raw_kinds, 3).map((kind) => {
        if (![...RAW_KINDS, "source_lab_report"].includes(kind))
          throw new IntegrityError(
            "RAW_KIND_UNSUPPORTED",
            "The policy contains an unsupported kind.",
          );
        return kind as RawKind | "source_lab_report";
      }),
      max_retention_days: safeInteger(p.max_retention_days, 1),
      expires_at: expiry,
      access_roles: strings(p.access_roles),
      withdrawal_behavior: requiredString(p.withdrawal_behavior, 4096),
      exceptions: strings(p.exceptions),
      raw_notice: {
        version: requiredString(notice.version),
        sha256: noticeSha,
        content: noticeText,
      },
      content,
    };
  }
  const receiptId = object.receipt_id === null ? null : id(object.receipt_id),
    consentId =
      object.consent_record_id === null ? null : id(object.consent_record_id);
  let receipt: RawRecordingStatus["preference_receipt"] = null;
  if (object.preference_receipt !== null) {
    const r = requireObject(object.preference_receipt);
    knownKeys(r, [
      "receipt_id",
      "consent_record_id",
      "policy_id",
      "policy_version",
      "policy_sha256",
      "raw_notice_version",
      "raw_notice_sha256",
      "acknowledged_at",
      "accepted_at",
      "choices",
    ]);
    receipt = {
      receipt_id: id(r.receipt_id),
      consent_record_id: id(r.consent_record_id),
      policy_id: requiredString(r.policy_id),
      policy_version: requiredString(r.policy_version),
      policy_sha256: sha(r.policy_sha256),
      raw_notice_version: requiredString(r.raw_notice_version),
      raw_notice_sha256: sha(r.raw_notice_sha256),
      acknowledged_at: utc(r.acknowledged_at),
      accepted_at: utc(r.accepted_at),
      choices: parseRawChoices(r.choices),
    };
    if (
      receipt.receipt_id !== receiptId ||
      receipt.consent_record_id !== consentId ||
      receipt.policy_id !== policy?.policy_id ||
      receipt.policy_version !== policy?.version ||
      receipt.policy_sha256 !== policy?.sha256 ||
      receipt.raw_notice_version !== policy?.raw_notice.version ||
      receipt.raw_notice_sha256 !== policy?.raw_notice.sha256 ||
      Date.parse(receipt.accepted_at) <
        Date.parse(receipt.acknowledged_at) - 5000
    )
      throw new IntegrityError(
        "RAW_RECEIPT_MISMATCH",
        "The optional-purpose receipt differs from the current exact policy or consent.",
      );
  }
  if (
    receipt &&
    RAW_KINDS.some(
      (kind) =>
        (choices[kind].record && !receipt.choices[kind].record) ||
        (choices[kind].upload && !receipt.choices[kind].upload),
    )
  )
    throw new IntegrityError(
      "RAW_CHOICE_WIDENED",
      "Effective recording choices cannot exceed the immutable receipt you confirmed.",
    );
  if (
    (receiptId && !receipt) ||
    (!receipt &&
      RAW_KINDS.some((kind) => choices[kind].record || choices[kind].upload))
  )
    throw new IntegrityError(
      "RAW_RECEIPT_REQUIRED",
      "Recording choices require a verified immutable receipt.",
    );
  if (
    !policy &&
    RAW_KINDS.some(
      (kind) =>
        availability[kind].record_allowed || availability[kind].upload_allowed,
    )
  )
    throw new IntegrityError(
      "RAW_POLICY_REQUIRED",
      "Recording requires an approved retention policy.",
    );
  if (
    !Array.isArray(object.artifacts) ||
    object.artifacts.length > 500 ||
    !Array.isArray(object.revocations) ||
    object.revocations.length > 100
  )
    throw new IntegrityError(
      "RAW_STATUS_LIMIT",
      "Recording status exceeds its bounded list size.",
    );
  const artifacts = object.artifacts.map((value) => {
    const a = requireObject(value);
    knownKeys(a, [
      "artifact_id",
      "artifact_kind",
      "state",
      "upload_state",
      "retention_due_at",
      "cleanup_completed_at",
    ]);
    if (
      !RAW_KINDS.includes(a.artifact_kind as RawKind) ||
      !["retained", "cleanup_pending", "purged"].includes(String(a.state))
    )
      throw new IntegrityError(
        "RAW_ARTIFACT_STATE_UNSUPPORTED",
        "A recording state is unsupported.",
      );
    if (
      !["quarantine", "verified", "cleanup_pending", "purged"].includes(
        String(a.upload_state),
      )
    )
      throw new IntegrityError(
        "RAW_UPLOAD_STATE_UNSUPPORTED",
        "Recording upload status is unsupported.",
      );
    return {
      upload_state: String(a.upload_state),
      artifact_id: id(a.artifact_id),
      artifact_kind: a.artifact_kind as RawKind,
      state: String(a.state),
      retention_due_at: utc(a.retention_due_at),
      cleanup_completed_at:
        a.cleanup_completed_at === null ? null : utc(a.cleanup_completed_at),
    };
  });
  const revocations = object.revocations.map((value) => {
    const r = requireObject(value);
    knownKeys(r, ["receipt_id", "artifact_kinds", "accepted_at", "state"]);
    if (!["cleanup_pending", "completed"].includes(String(r.state)))
      throw new IntegrityError(
        "RAW_REVOCATION_STATE_UNSUPPORTED",
        "The revocation cleanup state is unsupported.",
      );
    return {
      receipt_id: id(r.receipt_id),
      artifact_kinds: kinds(r.artifact_kinds),
      accepted_at: utc(r.accepted_at),
      state: r.state as "cleanup_pending" | "completed",
    };
  });
  if (
    typeof object.has_more_artifacts !== "boolean" ||
    (object.has_more_artifacts && object.next_artifact_cursor === null)
  )
    throw new IntegrityError(
      "RAW_STATUS_CURSOR_INVALID",
      "Recording history pagination is invalid.",
    );
  return {
    has_more_artifacts: object.has_more_artifacts,
    next_artifact_cursor:
      object.next_artifact_cursor === null
        ? null
        : id(object.next_artifact_cursor),
    study_id: studyId,
    consent_record_id: consentId,
    receipt_id: receiptId,
    preference_receipt: receipt,
    choices,
    policy,
    availability,
    artifacts,
    revocations,
    ...(object.accepted_receipt_id === undefined
      ? {}
      : { accepted_receipt_id: id(object.accepted_receipt_id) }),
  };
}
export function assertRawChoicesAllowed(
  status: RawRecordingStatus,
  choices: RawChoices,
  fenced: RawKind[] = [],
  at = Date.now(),
): void {
  parseRawChoices(choices);
  if (
    !status.policy ||
    Date.parse(status.policy.expires_at) <= at ||
    !status.consent_record_id
  )
    throw new IntegrityError(
      "RAW_POLICY_UNAVAILABLE",
      "Review a current approved recording policy and consent receipt before changing choices.",
    );
  for (const kind of RAW_KINDS)
    if (
      (choices[kind].record &&
        (!status.availability[kind].record_allowed || fenced.includes(kind))) ||
      (choices[kind].upload && !status.availability[kind].upload_allowed)
    )
      throw new IntegrityError(
        "RAW_SCOPE_UNAVAILABLE",
        "This recording choice is unavailable or its revocation is still pending.",
      );
}
