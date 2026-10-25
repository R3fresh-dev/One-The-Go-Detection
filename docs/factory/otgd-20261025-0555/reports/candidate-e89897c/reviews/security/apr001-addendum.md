# D012v1 / APR-001 independent security addendum

**AFFECTED. APR-001 is independently confirmed. My earlier OTGD-007 IMPLEMENTATION PASS is superseded by BLOCKED.** The other 46 security decisions remain unchanged: only OTGD-002 and OTGD-004 retain scoped PASS; the resulting disposition is **2 PASS / 45 BLOCKED**, overall **NEEDS_HUMAN** after final correction 2/2.

Reviewer `/root/replacement_security`, configured OpenAI `gpt-6.1-sol/high`; exact runtime model is not independently queryable. Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`, tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`, unchanged source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`. Observed 2026-10-25T11:51:18.200016+00:00. This is a narrow independent source/control-flow assessment, with no new runtime execution.

Canonical `openspec/changes/authorized-model-execution/specs/android-settings-accessibility/spec.md:4` expressly requires **About** to show the account's currently admitted scope as well as its environment. Whole-function inspection of `apps/mobile/src/ui/manage.tsx:1686–1766` confirms About shows the compiled environment and static generic measurement/research-reader limitations. Its only use of `model` is deciding the Back destination. Current identity, authenticated capabilities, account/data generation, offline state and research admission cannot affect its displayed scope.

I independently traced possible shared rendering: `components.tsx:567–650` Page renders supplied title/eyebrow/children and focus/scroll handling, with no current-scope insertion. `App.tsx:218–219` routes About and Status separately; chrome at385–413 displays ACCOUNT/environment/GUEST/OFFLINE. ContextStrip at547 onward accepts only browser/guest flags. None supplies About's missing currently admitted scope. Thus active admitted and ordinary/revoked/mismatched account capability states cannot be distinguished by About's scope content through these paths.

The existing passing assertions do not establish that clause. `e2e/fixtures/availability-component.tsx:8–25` selects About only with `about=true`, otherwise StatusScreen. At `e2e/raw-recordings.spec.ts:1407–1464`, conditional approved/unavailable channel and research-scope assertions call the default Status path. The subsequent About=true assertion verifies only static version1.1 reader/no-bundled-approval wording. Those two recorded scenario PASS observations remain valid; they do not cover the requirement's additional normative About clause. The released 782-case execution record is preserved rather than retrospectively falsified.

**APR-001 / P2** is a missing required status display, not a demonstrated authorization bypass, privilege grant or numeric disclosure. My prior OTGD-007 PASS and source-summary assertion of no remaining required source correction were too broad for this normative clause and are superseded to this exact extent. SEC-01 and SEC-02 remain closed, all seven current local gates and 14 CI jobs remain passed, and the other 46 per-spec judgments are unchanged. A test aggregate cannot cure the omitted display.

D012v1 was actually ACKed **AFFECTED** to PM after this independent trace. D011's source/evidence distinction is unchanged. No source repair, test, service, Git action or third correction was performed or authorized. Required next action is human scope/budget handling or existing direct proof of this exact About path; an automatic repair or new execution is not implied.

Original files are preserved verbatim:

- `report.md` SHA-256 `b0a639460cec207eba7a7b64d3f92be274b1e2d8e4a7afb9be3e9c16d8dd00e2`.
- `per-spec-decisions.json` SHA-256 `5d31f21b6ab80fb5924a45fd1c9529bc8ccaddb30a4b67296cf9e682c9289a91`.

This addendum and `apr001-addendum.json` provide the explicit supersession; neither original file nor its existing hash manifest was rewritten. The approver report independently inspected here hashes to `cfd31ee67e6e948bde6c1b123a77220367916e206f03345d30ad727520d19a31`. Actual current canonical/source hashes are in the JSON. No action was denied or left with an uncertain outcome by this reviewer.
