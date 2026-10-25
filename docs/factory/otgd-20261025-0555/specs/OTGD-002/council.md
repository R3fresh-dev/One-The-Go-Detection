# OTGD-002: Council — initial independent review

Canonical specification: `openspec/changes/authorized-model-execution/specs/android-dashboard/spec.md`; SHA-256 `c8e2d63aad6f7f973a181d917ef645e8d32b012ca41df1f2abd7d7a0b7525fe4`.

Reviewed implementation candidate: `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; source fingerprint `36ed8d800edcb560ac8ca189e98b64518b3342a29458d6e91a8d943085310f8c`.

Initial decision: **CHANGES_REQUIRED**. No independent final approval. Correction round1 is active; any subsequent source change requires affected fresh confirmations.

All six actual agents were explicitly dispatched with OpenAI gpt-6.1-sol/high; separate runtime attestation is unavailable. Full evidence, judgments and hashes are preserved under `../../reviews/candidate-28e0729/`.

| Role | Actual reviewer | Initial per-spec decision | Evidence |
|---|---|---|---|
| security | /root/review_security | BLOCKED | ../../reviews/candidate-28e0729/security/bindings.json |
| ux | /root/review_ux | CHANGES_REQUIRED | ../../reviews/candidate-28e0729/ux/review.json |
| ui | /root/review_ui | BLOCKED | ../../reviews/candidate-28e0729/ui/review-bindings.json |
| code | /root/review_code | BLOCKED | ../../reviews/candidate-28e0729/code/per-spec-decisions.json |
| product | /root/review_product | CHANGES_REQUIRED | ../../reviews/candidate-28e0729/product/product-signoff.json |
| engineering | /root/review_engineering | BLOCKED | ../../reviews/candidate-28e0729/engineering/engineering-signoffs.json |
Final required gates, explicit acceptance-case execution and applicable native/external evidence remain unresolved. Pending evidence is not a passing signoff; neither software tests nor reviews establish scientific, hardware, participant or release qualification.
Decision register: ../../decisions.md; correction plan: ../../correction-round-1.md.

## Candidate cf74fcf independent replacement review

Exact candidate cf74fcff6ad19e639538d260f223ec18d618658d; current canonical SHA256 c8e2d63aad6f7f973a181d917ef645e8d32b012ca41df1f2abd7d7a0b7525fe4. All six real OpenAI independent reviewers completed their provisional implementation assessments. Decisions are preserved at ../../reviews/candidate-cf74fcf/<role>/per-spec-decisions.json. security: BLOCKED; ux: CHANGES_REQUIRED; ui: CHANGES_REQUIRED; code: BLOCKED; product: CHANGES_REQUIRED; engineering: CHANGES_REQUIRED. No final council approval. Four consolidated source findings require correction round 2/2; execution and external prerequisites remain distinct.

## Final six independent reviews — e89897cc852a

All required current local7/CI14 gates passed. Exact current criteria and unproved clauses remain in test-results.json and the immutable verifier release; aggregate gates do not replace acceptance.

| Review | Decision | Actual independent identity |
|---|---|---|
| security | PASS | /root/replacement_security |
| code | PASS | /root/replacement_code |
| ux | PASS | /root/replacement_ux |
| ui | PASS | /root/replacement_ui |
| product | PASS | /root/replacement_product |
| engineering | PASS | /root/replacement_engineering |

The exact unchanged review rows are preserved in [final-reviews.json](final-reviews.json). Independent approver /root/final_approver is active; no final council decision is recorded in checkpoint13. Correction2/2, recovery0/3. Source and metadata identities are separate under D011v1.
