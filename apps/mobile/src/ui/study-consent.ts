import type { JsonObject } from "../core/types";
import { digestText, utf8 } from "../core/integrity";

export function assessStudyConsent(study: JsonObject) {
  const value = study.consent;
  const receipt =
    value && typeof value === "object" && !Array.isArray(value)
      ? (value as JsonObject)
      : null;
  const text = String(study.document_text ?? "");
  const hash = String(study.document_sha256 ?? "");
  const documentValid =
    typeof study.document_text === "string" &&
    typeof study.document_sha256 === "string" &&
    typeof study.study_id === "string" &&
    !!study.study_id &&
    typeof study.invitation_id === "string" &&
    !!study.invitation_id &&
    typeof study.document_version === "string" &&
    !!study.document_version &&
    !!text &&
    utf8(text).length <= 65_536 &&
    digestText(text) === hash;
  const current =
    documentValid &&
    receipt?.state === "active" &&
    receipt.accepted === true &&
    ["study_id", "invitation_id", "document_version", "document_sha256"].every(
      (field) => receipt[field] === study[field],
    );
  const needsFreshInvitation =
    receipt?.state === "withdrawn" &&
    receipt.invitation_id === study.invitation_id;
  return {
    receipt,
    current,
    documentValid,
    needsFreshInvitation,
    mayAccept:
      documentValid &&
      !current &&
      !needsFreshInvitation &&
      !study.local_withdrawal_pending,
  };
}
