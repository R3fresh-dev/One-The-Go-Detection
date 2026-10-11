import assert from "node:assert/strict";
import test from "node:test";
import { assessStudyConsent } from "../src/ui/study-consent";
import { digestText } from "../src/core/integrity";
import type { JsonObject } from "../src/core/types";

const study: JsonObject = {
  study_id: "fictional-study",
  invitation_id: "invitation-one",
  document_version: "v2",
  document_text: "Fictional approved study document",
  document_sha256: digestText("Fictional approved study document"),
  consent: null,
};
const receipt: JsonObject = {
  study_id: study.study_id!,
  invitation_id: study.invitation_id!,
  document_version: study.document_version!,
  document_sha256: study.document_sha256!,
  accepted: true,
  state: "active",
  acknowledged_at: "2026-10-11T10:00:00Z",
};

test("only an active exact affirmative receipt suppresses new study consent", () => {
  assert.equal(assessStudyConsent(study).mayAccept, true);
  assert.equal(
    assessStudyConsent({ ...study, consent: receipt }).current,
    true,
  );
  assert.equal(
    assessStudyConsent({ ...study, consent: receipt }).mayAccept,
    false,
  );
  const changes: JsonObject[] = [
    { study_id: "other-study" },
    { invitation_id: "old-invitation" },
    { document_version: "v1" },
    { document_sha256: "0".repeat(64) },
    { accepted: false },
    { state: "pending" },
  ];
  for (const change of changes) {
    const assessment = assessStudyConsent({
      ...study,
      consent: { ...receipt, ...change },
    });
    assert.equal(assessment.current, false);
    assert.equal(assessment.mayAccept, true);
  }
});

test("withdrawal requires a fresh invitation, and local pending withdrawal blocks reconsent", () => {
  const withdrawn = { ...receipt, state: "withdrawn" };
  assert.equal(
    assessStudyConsent({ ...study, consent: withdrawn }).needsFreshInvitation,
    true,
  );
  assert.equal(
    assessStudyConsent({ ...study, consent: withdrawn }).mayAccept,
    false,
  );
  assert.equal(
    assessStudyConsent({
      ...study,
      invitation_id: "invitation-two",
      consent: withdrawn,
    }).mayAccept,
    true,
  );
  assert.equal(
    assessStudyConsent({ ...study, local_withdrawal_pending: true }).mayAccept,
    false,
  );
});

test("missing, oversized or tampered documents never permit consent", () => {
  const changes: JsonObject[] = [
    { document_text: "tampered" },
    { document_text: "" },
    { document_text: "x".repeat(65_537) },
    { invitation_id: "" },
    { document_version: null },
    { document_text: {}, document_sha256: digestText("[object Object]") },
  ];
  for (const change of changes) {
    const assessment = assessStudyConsent({ ...study, ...change });
    assert.equal(assessment.documentValid, false);
    assert.equal(assessment.mayAccept, false);
  }
});
