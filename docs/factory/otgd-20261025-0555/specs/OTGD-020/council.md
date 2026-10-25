# OTGD-020: Council — initial independent review

Canonical specification: `openspec/changes/production-mobile-platform/specs/android-app-environment/spec.md`; SHA-256 `7cd3451fd8c13cd25bdc66403e879de3f9fe0e127e3655f2ed40017869916f76`.

Reviewed implementation candidate: `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; source fingerprint `36ed8d800edcb560ac8ca189e98b64518b3342a29458d6e91a8d943085310f8c`.

Initial decision: **CHANGES_REQUIRED**. No independent final approval. Correction round1 is active; any subsequent source change requires affected fresh confirmations.

All six actual agents were explicitly dispatched with OpenAI gpt-6.1-sol/high; separate runtime attestation is unavailable. Full evidence, judgments and hashes are preserved under `../../reviews/candidate-28e0729/`.

| Role | Actual reviewer | Initial per-spec decision | Evidence |
|---|---|---|---|
| security | /root/review_security | CHANGES_REQUIRED | ../../reviews/candidate-28e0729/security/bindings.json |
| ux | /root/review_ux | BLOCKED | ../../reviews/candidate-28e0729/ux/review.json |
| ui | /root/review_ui | BLOCKED | ../../reviews/candidate-28e0729/ui/review-bindings.json |
| code | /root/review_code | CHANGES_REQUIRED | ../../reviews/candidate-28e0729/code/per-spec-decisions.json |
| product | /root/review_product | BLOCKED | ../../reviews/candidate-28e0729/product/product-signoff.json |
| engineering | /root/review_engineering | BLOCKED | ../../reviews/candidate-28e0729/engineering/engineering-signoffs.json |
Final required gates, explicit acceptance-case execution and applicable native/external evidence remain unresolved. Pending evidence is not a passing signoff; neither software tests nor reviews establish scientific, hardware, participant or release qualification.
Decision register: ../../decisions.md; correction plan: ../../correction-round-1.md.

## Candidate cf74fcf independent replacement review

Exact candidate cf74fcff6ad19e639538d260f223ec18d618658d; current canonical SHA256 6cef683b7ac1b04bdf104e0b87aa36badf61e905580d32223c05a39ce8efac35. All six real OpenAI independent reviewers completed their provisional implementation assessments. Decisions are preserved at ../../reviews/candidate-cf74fcf/<role>/per-spec-decisions.json. security: CHANGES_REQUIRED; ux: BLOCKED; ui: BLOCKED; code: BLOCKED; product: BLOCKED; engineering: CHANGES_REQUIRED. No final council approval. Four consolidated source findings require correction round 2/2; execution and external prerequisites remain distinct.

## Final six independent reviews — e89897cc852a

All required current local7/CI14 gates passed. Exact current criteria and unproved clauses remain in test-results.json and the immutable verifier release; aggregate gates do not replace acceptance.

| Review | Decision | Actual independent identity |
|---|---|---|
| security | BLOCKED | /root/replacement_security |
| code | BLOCKED | /root/replacement_code |
| ux | BLOCKED | /root/replacement_ux |
| ui | BLOCKED | /root/replacement_ui |
| product | BLOCKED | /root/replacement_product |
| engineering | BLOCKED | /root/replacement_engineering |

The exact unchanged review rows are preserved in [final-reviews.json](final-reviews.json). Independent approver /root/final_approver is active; no final council decision is recorded in checkpoint13. Correction2/2, recovery0/3. Source and metadata identities are separate under D011v1.
