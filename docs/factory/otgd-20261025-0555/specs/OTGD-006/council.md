# OTGD-006: Council — initial independent review

Canonical specification: `openspec/changes/authorized-model-execution/specs/android-results/spec.md`; SHA-256 `e5c8877a4b483fb47aa30fb9811536166d10764d83d15eaef950e0727dc93a8f`.

Reviewed implementation candidate: `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; source fingerprint `36ed8d800edcb560ac8ca189e98b64518b3342a29458d6e91a8d943085310f8c`.

Initial decision: **BLOCKED**. No independent final approval. Correction round1 is active; any subsequent source change requires affected fresh confirmations.

All six actual agents were explicitly dispatched with OpenAI gpt-6.1-sol/high; separate runtime attestation is unavailable. Full evidence, judgments and hashes are preserved under `../../reviews/candidate-28e0729/`.

| Role | Actual reviewer | Initial per-spec decision | Evidence |
|---|---|---|---|
| security | /root/review_security | BLOCKED | ../../reviews/candidate-28e0729/security/bindings.json |
| ux | /root/review_ux | BLOCKED | ../../reviews/candidate-28e0729/ux/review.json |
| ui | /root/review_ui | BLOCKED | ../../reviews/candidate-28e0729/ui/review-bindings.json |
| code | /root/review_code | BLOCKED | ../../reviews/candidate-28e0729/code/per-spec-decisions.json |
| product | /root/review_product | BLOCKED | ../../reviews/candidate-28e0729/product/product-signoff.json |
| engineering | /root/review_engineering | BLOCKED | ../../reviews/candidate-28e0729/engineering/engineering-signoffs.json |
Final required gates, explicit acceptance-case execution and applicable native/external evidence remain unresolved. Pending evidence is not a passing signoff; neither software tests nor reviews establish scientific, hardware, participant or release qualification.
Decision register: ../../decisions.md; correction plan: ../../correction-round-1.md.
