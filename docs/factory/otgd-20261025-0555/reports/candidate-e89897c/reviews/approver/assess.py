"""Read-only evidence reconciliation; writes only this owned approver directory.

This does not execute application tests, services, Git, builds or deployments.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import re
import xml.etree.ElementTree as ET

B = Path('/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a')
R = Path('/workspace/One-The-Go-Detection')
O = B / 'reviews/approver'
NOW = datetime.now(timezone.utc).isoformat()
SHA = lambda data: hashlib.sha256(data).hexdigest()
read = lambda p: json.loads(p.read_text())
errors = []
checked = []

def check_file(path, expected, size=None, kind='evidence'):
    path = Path(path)
    raw = path.read_bytes()
    actual = SHA(raw)
    ok = actual == expected and (size is None or len(raw) == size)
    checked.append({'path': str(path), 'sha256': actual, 'bytes': len(raw), 'kind': kind, 'matches': ok})
    if not ok:
        errors.append(str(path))
    return raw

binding = read(B/'candidate-binding.json')
release_path = B/'verification/release-manifest.json'
release = read(release_path)
check_file(release_path, '3f5ecef5a665738d27692a073e87377d1e65d48810408eedaec099cf5f7ce40d', kind='verifier-release')
for f in release['files']:
    check_file(B/'verification'/f['path'], f['sha256'], f['bytes'], 'verifier-release-member')

source = read(B/'verification/source-binding.json')
fingerprint = hashlib.sha256()
for name, expected in sorted(source['current_file_sha256'].items()):
    raw = check_file(R/name, expected, kind='source')
    fingerprint.update(name.encode()+b'\0'+raw)
assert fingerprint.hexdigest() == binding['source_fingerprint_sha256']
assert len(source['current_file_sha256']) == 1299

canonical = {}
for s in binding['canonical_specs']:
    raw = check_file(R/s['path'], s['sha256'], kind='canonical')
    text = raw.decode()
    canonical[s['id']] = {**s, 'requirement_headings': re.findall(r'^### Requirement: (.+)', text, re.M),
                           'scenario_headings': re.findall(r'^#### Scenario: (.+)', text, re.M)}

final_six = read(B/'final-six-reviews.json')
reviewers = {}
for f in final_six['reviews']:
    check_file(f['report'], f['report_sha256'], kind='review-report')
    check_file(f['decisions'], f['decisions_sha256'], kind='review-decisions')
    d = read(Path(f['decisions']))
    lists = [v for v in d.values() if isinstance(v, list) and len(v) == 47
             and all(isinstance(x, dict) and 'spec_id' in x for x in v)]
    assert len(lists) == 1, f['role']
    rows = {x['spec_id']: x for x in lists[0]}
    assert set(rows) == set(canonical)
    for sid, row in rows.items():
        assert row['canonical_sha256'] == canonical[sid]['sha256']
        assert row['canonical_path'] == canonical[sid]['path']
        assert row.get('candidate_revision', row.get('canonical_revision')) == binding['revision']
    reviewers[f['role']] = {'identity': f['reviewer'], 'provider': f['provider'],
                            'configured_model': f['configured_model'], 'reasoning': f['reasoning'],
                            'report': f['report'], 'report_sha256': f['report_sha256'],
                            'decisions': f['decisions'], 'decisions_sha256': f['decisions_sha256'], 'rows': rows}
assert len({x['identity'] for x in reviewers.values()}) == 6

local = read(B/'local-final-artifacts.json')
for f in local['artifacts']:
    check_file(f['path'], f['sha256'], f['bytes'], 'local-final')
assert local['source_before_after_equal'] and local['clean'] and local['exit_code'] == 0
assert len(local['gates']['passed']) == 7
ci = read(B/'ci-acceptance-summary.json')
assert len(ci['jobs']) == 14 and all(x['conclusion'] == 'success' for x in ci['jobs'])
assert ci['tree'] == binding['tree'] and ci['candidate'] == binding['revision']
for stage in [1, 2, 3]:
    for f in read(B/f'ci-artifacts-verified-stage{stage}.json'):
        check_file(f['archive'], f['sha256'], f['bytes'], 'ci-archive')
        for entry in f['entries']:
            check_file(entry['path'], entry['sha256'], entry['bytes'], 'ci-member')
for f in read(B/'supplemental/operations/manifest.json'):
    check_file(B/'supplemental/operations'/f['path'], f['sha256'], f.get('bytes'), 'operations')
for path, expected in read(B/'supplemental/semantics/artifact-manifest.json')['sha256'].items():
    check_file(B/'supplemental/semantics'/path, expected, kind='semantics')

parsed_xml = []
for p in sorted((B/'current-local').glob('*.xml')):
    root = ET.parse(p).getroot()
    counts = {tag: len(root.findall('.//'+tag)) for tag in ['testcase','failure','error','skipped']}
    parsed_xml.append({'path': str(p), **counts})
    assert not any(counts[x] for x in ['failure','error','skipped'])
coverage = read(B/'current-local/unit-coverage.json')['totals']
assert coverage['percent_covered'] > 80

case = read(B/'verification/case-evidence.json')
rows = case['rows']
assert len(rows) == 782 and len({x['case_id'] for x in rows}) == 782
assert all(x['audit_completed'] and x['candidate'] == binding['revision'] for x in rows)
requirements = read(B/'verification/requirement-evidence.json')['requirements']
assert len(requirements) == 411
assert Counter(x['status'] for x in rows) == {'PASS':260,'PARTIAL':420,'BLOCKED':82,'NOT_RUN':20}
assert all(x['unproved_then_clauses'] for x in rows if x['status'] != 'PASS')
assert all(not x['unproved_then_clauses'] for x in rows if x['status'] == 'PASS')
assert all(x['canonical_sha256'] == canonical[x['spec_id']]['sha256'] for x in rows)

assertions = read(B/'verification/source-assertions.json')
assertion_checks = []
for ref, a in assertions.items():
    p = Path(a['path'])
    if not p.is_absolute(): p = R/p
    raw = p.read_bytes()
    file_ok = SHA(raw) == a['file_sha256']
    body_ok = a['body'].strip() in raw.decode().replace('\r\n','\n')
    assertion_checks.append({'ref':ref, 'path':str(p), 'file_hash_matches':file_ok, 'literal_body_matches':body_ok})
    if not file_ok: errors.append('source assertion file '+ref)
    # Nonliteral derived parameterized/reference records are not independently
    # treated as literal source-body proofs; exact file binding remains checked.

pass_reasons = {
 'OTGD-002': 'PASS for complete canonical AND-DASH-001 software amendment. Actual Home JSX and workspaceScope assertions exercise active matching account/generation/current capabilities, revocation, offline, deleting and guest refusal. Verified immutable result/proof refusal prevents legacy/local/synthetic authority. Home preserves snapshot acquisition time; shared rendering and strict typed missingness/provenance controls retain unavailable channels. No surrounding dashboard/native/study approval follows.',
 'OTGD-004': 'PASS for complete canonical AND-HIST-003 software amendment. Actual row/History and result-detail production rendering preserves historical research scope; strict result verification binds original target/evaluation dates, endpoint/population, original immutable values and rejects changed proof/legacy/synthetic/owner linkage. Direct unchanged source renders original times/qualifiers/units and rejects unsupported research. This is a software historical-evidence reader, with no current sobriety or genuine study qualification claim.',
}

about_finding = {
 'finding_id':'APR-001', 'severity':'P2', 'status':'OPEN_AFTER_FINAL_CORRECTION_LIMIT',
 'spec_id':'OTGD-007', 'requirement_id':'AND-SET-004',
 'canonical_clause':"About SHALL show the actual environment and account's currently admitted scope.",
 'observed_source':'apps/mobile/src/ui/manage.tsx:1686–1768 AboutScreen reads model only for Back navigation. Its rendered environment is correct, but scope text is static generic release support; it does not consume current identity/capabilities/generation/offline state. apps/mobile/src/ui/components.tsx:567 Page adds no scope; apps/mobile/App.tsx chrome shows ACCOUNT/environment/GUEST/OFFLINE and ContextStrip only preview/guest, not current admitted research scope.',
 'assertion_boundary':'apps/mobile/e2e/fixtures/availability-component.tsx routes about=true to AboutScreen; raw-recordings.spec.ts conditional capability assertions use about=false StatusScreen, then about=true asserts only static format/no-bundled-model text. These meaningful passing assertions do not prove the separate normative About requirement.',
 'impact':'About cannot distinguish an independently admitted current research account from an ordinary, revoked or mismatched account. This is a missing required status presentation, not a demonstrated grant of research/capture authority.',
 'verification_method':'Read-only whole-function and shared-render-tree/control-flow inspection; no runtime/build/test executed.',
 'required_correction':'After explicit human handling of exhausted correction2/2, make About render a truthful current account scope using existing validated owner/generation/offline/capability guards. Do not grant capability or infer approval from sign-in/version.',
 'verification_criterion':'About distinguishes admitted versus ordinary/guest/offline/revoked/wrong-owner/generation states; existing shared workspaceScope assertions may be reused with direct production About call-path evidence. No duplicate test is required if current meaningful shared proof establishes the final integration.',
 'minimum_next_action':'Human scope/budget adjudication or already-existing evidence that this exact About clause is satisfied. Do not silently waive it or perform automatic correction round3.',
 'does_not_change_verifier_782_case_statuses':True,
 'disagrees_with':['security','code','ux','ui','product','engineering']
}
manage_source = (R/'apps/mobile/src/ui/manage.tsx').read_text()
about_body = manage_source.split('export function AboutScreen',1)[1].split('export function StatusScreen',1)[0]
about_finding['actual_about_source_excerpt'] = 'export function AboutScreen'+about_body
about_finding['actual_about_source_file_sha256'] = SHA((R/'apps/mobile/src/ui/manage.tsx').read_bytes())
about_finding['actual_wrapper_source_sha256'] = SHA((R/'apps/mobile/App.tsx').read_bytes())
about_finding['actual_page_source_sha256'] = SHA((R/'apps/mobile/src/ui/components.tsx').read_bytes())
about_finding['actual_fixture_source_sha256'] = SHA((R/'apps/mobile/e2e/fixtures/availability-component.tsx').read_bytes())

decisions = []
for sid, s in canonical.items():
    current = [x for x in rows if x['spec_id'] == sid]
    remaining = [x for x in current if x['status'] != 'PASS']
    votes = {role: info['rows'][sid]['decision'] for role, info in reviewers.items()}
    decision = 'PASS' if sid in pass_reasons else 'BLOCKED'
    assert (not remaining and all(x=='PASS' for x in votes.values())) if decision == 'PASS' else (bool(remaining) or sid=='OTGD-007')
    residuals = [{k:r[k] for k in ['case_id','requirement_id','status','expected_observation',
                    'unproved_then_clauses','remaining_prerequisite_types','current_assertions_proven',
                    'current_source_assertion_refs','minimal_next_evidence_or_action','open_implementation_defect']}
                 for r in remaining]
    decisions.append({'spec_id':sid, 'decision':decision, 'scope':'IMPLEMENTATION',
       'approval_kind':'SCOPED_CANONICAL_SOFTWARE_IMPLEMENTATION' if decision=='PASS' else None,
       'candidate_revision':binding['revision'], 'candidate_tree':binding['tree'],
       'canonical_path':s['path'], 'canonical_sha256':s['sha256'],
       'canonical_requirements':s['requirement_headings'] or s['criteria'],
       'canonical_scenarios':s['scenario_headings'],
       'rationale':('BLOCKED: APR-001. About does not display the account current admitted scope required by canonical AND-SET-004. The two recorded scenario PASS cases prove conditional Service presentation and legacy refusal, but omit this normative About clause. All six prior PASS votes are explicitly disagreed with on this exact source evidence.' if sid=='OTGD-007' else pass_reasons.get(sid, 'Required implementation acceptance remains unproved. The exact unmet clauses below prevent approval after final correction 2/2. Passing shared gates and closed prior source findings do not supply those clauses. This is an evidence block, not a newly reproduced source defect.')),
       'six_current_independent_decisions':votes,
       'case_counts':dict(Counter(x['status'] for x in current)),
       'all_current_case_ids':[x['case_id'] for x in current],
       'exact_remaining_clauses':residuals,
       'independent_normative_findings':[about_finding] if sid=='OTGD-007' else [],
       'minimum_next_inputs_or_actions':[
           {'case_id':r['case_id'], 'required_clause':r['unproved_then_clauses'],
            'types':r['remaining_prerequisite_types'], 'existing_evidence_first':True,
            'action':r['minimal_next_evidence_or_action']} for r in remaining] + ([{'finding_id':'APR-001','required_clause':about_finding['canonical_clause'],'action':about_finding['minimum_next_action'],'verification_criterion':about_finding['verification_criterion']}] if sid=='OTGD-007' else []),
       'escalation':None if decision=='PASS' else 'NEEDS_HUMAN: correction 2/2 exhausted; evidence/owner adjudication or explicit further scope/budget decision; no automatic third correction.',
       'approval_excludes':['whole application','broader contributing feature specs','installed native OS acceptance',
                           'qualified hardware/science/participant use','release readiness','merge/deploy/publish']})

identity = {'agent_id':'/root/final_approver','role':'independent final Factory council approver',
 'provider':'OpenAI','configured_model':'gpt-6.1-sol','configured_reasoning_effort':'high','fork_turns':'none',
 'evidence':'PM confirmed actual successful collaboration.spawn_agent arguments and returned canonical identity via native message during this assessment.',
 'runtime_model_independently_queryable':False,'independence':'Fresh separate context; no source/spec/test authorship, no PM role; only assigned approver output writes.'}
inspection = {'recorded_at':NOW, 'identity':identity, 'source_candidate':binding['revision'],
 'source_tree':binding['tree'],'fingerprint_recomputed':fingerprint.hexdigest(),
 'fingerprint_method':'Sorted 1299 verifier source-binding names + NUL + current bytes; every current byte independently rehashed. No Git command permitted/performed; completeness/clean-index enumeration relies on current PM/verifier/six reviewers exact-tree receipts, separately distinguished from this content rehash.',
 'canonical_specs_verified':47,'verifier_release_members_verified':len(release['files']),
 'actual_six_reviewers':[{k:v for k,v in info.items() if k!='rows'} for info in reviewers.values()],
 'parsed_current_local_xml':parsed_xml,'python_unit_coverage_percent':coverage['percent_covered'],
 'local_gates':local['gates'],'ci':{'run_id':ci['run_id'],'tested_merge':ci['tested_merge'],'tree':ci['tree'],'jobs':ci['jobs']},
 'case_statuses':dict(Counter(x['status'] for x in rows)),'cases':782,'requirements':411,'audit_pending':0,
 'independent_normative_findings':[about_finding],
 'assertions_file_bindings':assertion_checks,'checked_files':checked,'errors':errors,
 'raw_evidence_limits':['No application tests/build/runtime/services/Git/deployment rerun by approver.',
 'Recorded local/CI executions are admitted by exact hashed artifacts and observed named outputs; no test execution attributed to approver.',
 '623 source records were hash checked; literal body mismatch is disclosed, never fabricated as literal independent proof.',
 'D011v1 ACK AFFECTED sent before dependent disposition; source/evidence branches and counters unchanged.']}
assert not errors, errors
payload = {'recorded_at':NOW,'reviewer':identity,'factory_pin':binding['factory_revision'],
 'run_id':binding['run'],'source_candidate':binding['revision'],'source_tree':binding['tree'],
 'source_fingerprint_sha256':binding['source_fingerprint_sha256'],
 'verifier_release_manifest_sha256':SHA(release_path.read_bytes()),
 'scope':'IMPLEMENTATION across 47 unchanged canonical specification IDs; narrow amendment approvals retain full canonical scope.',
 'correction_round':2,'max_correction_rounds':2,'recovery_attempts':0,'max_recovery_attempts':3,
 'overall_decision':'NEEDS_HUMAN','decision_counts':dict(Counter(x['decision'] for x in decisions)),
 'outcome_dimensions':{'specification_readiness':'No new DESIGN/SPEC_READY decision issued by this implementation assessment.',
    'implementation':'2 narrow canonical amendments approved; 45 blocked; complete approved application scope unverified.',
    'APP_VERIFIED':False,'RELEASE_READY':False,'external_action_completed':False,
    'deliverable':'Final independent evidence disposition and 47 decisions released; evidence branch publication is PM-owned and separately recorded.'},
 'new_source_inspection_finding':'APR-001 normative About scope omission; no runtime reproduction claimed.',
 'independent_findings':[about_finding],'all_six_current_review_reports_admitted':True,
 'D011_v1_ack':'AFFECTED: auxiliary metadata-only records preserve primary tested e898 source, sole PM/run and counters; docs descendant not separately application-tested.',
 'remaining_action_status':'BLOCKED evidence/owner prerequisites, escalated NEEDS_HUMAN; no permission denial, pending mutation or uncertain external action.',
 'decisions':decisions}

def write(name, obj):
    (O/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')

write('inspection-evidence.json',inspection)
write('per-spec-decisions.json',payload)
table = ['| Spec | Final disposition | Exact scope / representative blocker |','|---|---|---|']
for d in decisions:
    rationale = d['rationale'] if d['decision']=='PASS' or d['spec_id']=='OTGD-007' else d['exact_remaining_clauses'][0]['case_id']+': '+' '.join(d['exact_remaining_clauses'][0]['unproved_then_clauses'])
    table.append(f"| {d['spec_id']} | {d['decision']} | {rationale.replace('|','/')} |")
report = f'''# Independent final Factory council disposition

**Overall: NEEDS_HUMAN. Two narrow canonical software amendments (OTGD-002/004) receive IMPLEMENTATION PASS; 45 specifications remain BLOCKED. APP_VERIFIED and RELEASE_READY are not granted.** All six actual independent reviewers voted for three scoped passes; I disagree with their OTGD-007 approval because its normative About clause is unmet (APR-001, source/control-flow inspection). The two recorded scenario PASS cases remain unchanged; they do not cover that entire requirement. Correction **2/2** is exhausted, recovery remains **0/3**, and no third automatic correction is authorized.

Reviewer `/root/final_approver`, fresh independent nonauthor context, configured OpenAI `gpt-6.1-sol/high`, `fork_turns=none`. The PM confirmed actual successful dispatch arguments and returned canonical identity through native message. No independent runtime-effective-model query is exposed; no UUID or runtime variant is invented. I am neither the PM nor an author/signatory of the six preceding reviews. Writes are limited to `reviews/approver/`; no source/test/build/runtime/service/Git/deployment actions were performed.

Candidate `{binding['revision']}`, tree `{binding['tree']}`, run `{binding['run']}`, primary branch `{binding['branch']}`, Factory pin `{binding['factory_revision']}`. Independently rehashed all **1,299 listed source files**, recomputed full fingerprint `{fingerprint.hexdigest()}`, and checked all **47 canonical file hashes**. The read-only content check uses the frozen source-name manifest; under the explicit no-Git instruction I did not independently enumerate the current index/untracked set. Current clean/index/tree completeness comes from the separately admitted exact-source PM/verifier/six-reviewer receipts. This limitation does not turn docs-only evidence publication into an application-tested candidate.

## Evidence admission and decision prerequisites

I read AGENTS.md, pinned Factory evidence/spec-council/model-policy contracts, actual decisions/impact register and current D008v3/D010v2/D006v10/v11/D011v1 boundaries; all six current reports and their 282 actual per-spec decisions; canonical inventory/requirements/scenarios; released case/requirement/remaining-clause and software/external split records; final local/CI/runtime records and bounded operations/semantics supplements. D011v1 was ACKed AFFECTED to PM before dependent decisions: final safe records may use the auxiliary evidence branch while tested primary e898, sole PM, run and counters remain fixed. A metadata descendant is not separately application-tested or a new run/supervisor.

Independent hash checks admit all **164** released verifier members under release-manifest SHA-256 `{SHA(release_path.read_bytes())}`, all six actual final report/decision hashes, **19** final-local files, **9** downloaded CI archives and **35** extracted members, **43** operations and **19** semantics supplement files, with **zero hash/byte-count errors**. Exact checks and source assertion file bindings are in inspection-evidence.json. Where a derived assertion body is not a literal substring, that fact remains explicit; no such mismatch is hidden as a literal proof. The six reviewer contexts are distinct `/root/replacement_security`, `/root/replacement_code`, `/root/replacement_ux`, `/root/replacement_ui`, `/root/replacement_product`, `/root/replacement_engineering`, each configured OpenAI gpt-6.1-sol/high and independently nonauthor by actual dispatch/ACK/report evidence. Earlier provisional/initial reports remain history.

Recorded current execution meets the required shared software gates: **all seven local gates**, wrapper exit **0**, end **11:23:32Z**, before/after exact fingerprint equal; **all 14 CI jobs** successful in **40185247204**. Tested merge `d75116afb2771e4d2841e3592f2784a455ba0a9f` has the identical tree. Independently parsed current XML retains 1,538 API testcase elements, 1,508 PostgreSQL, 80 components, 6 ATDD, 2 hosted preview, 2 authenticated-browser and 9 SDK cases, without failure/error/skip elements. The API aggregate's 208 successful subtests are not invented as additional XML methods. API executable coverage **{coverage['percent_covered']:.8f}%**, local mobile **91.2001543%** and CI mobile **90.9542408%** exceed the strict >80% requirement. Those are retained execution observations, not tests newly run by the approver.

Meaningful named assertion/control-flow evidence is accepted compositionally; no duplicate test is required just to match a case ID. Home/current matching account-generation-capability/refusal rendering and immutable original historical target/evaluation/endpoint/population proof justify the complete canonical software amendment clauses in OTGD-002/004. Exact source shows original times/provenance/missingness; parser/proof guards prevent local preferences, unsupported versions or public format support becoming research authority. These decisions do not pass separate broad dashboard/history specs OTGD-021/028 or qualify actual scientific authority/native OS behavior. OTGD-007's scenario evidence is valid at its conditional Service/legacy-refusal boundary but insufficient for its additional explicit About requirement.

The released **782 cases / 411 requirements / 47 specs** have zero unaudited rows: **260 scoped PASS, 420 PARTIAL, 82 BLOCKED, 20 NOT_RUN**. The 522 non-PASS cases are evidence classifications, not 522 implementation defects or instructions to expand tests. Every blocked decision preserves all exact unmet clauses, proven assertions, current source refs, prerequisite categories and minimum next evidence. No unmet requirement is relabeled inapplicable. Required independent votes exist for every spec; their BLOCKED conclusions cannot be converted to full feature PASS by green aggregate gates.

## Exact remaining work and boundaries

**APR-001 / P2 / OTGD-007 AND-SET-004 — BLOCKED after final2/2.** Canonical wording explicitly requires: “About SHALL show the actual environment and account's currently admitted scope.” Whole-function inspection of `apps/mobile/src/ui/manage.tsx:1686` shows About reads model only for Back navigation. It renders the correct compiled environment, static generic research limitations and static format/no-bundled-model support. No current identity/capabilities/generation/offline value reaches its scope presentation. `Page` adds no scope; actual `App.tsx` chrome supplies only ACCOUNT/environment/GUEST/OFFLINE and guest/browser context, so no shared render path repairs this omission. The actual availability fixture selects About only with about=true, and the passing About assertions concern static format support; conditional capability assertions execute StatusScreen with about=false. Thus About cannot distinguish current independently admitted versus ordinary/revoked/mismatched account scope. This is source/control-flow evidence of a missing required status display, not a runtime test or a grant-of-authority vulnerability. All six OTGD-007 PASS votes are explicitly rejected at that exact normative clause; their valid two scenario observations and the verifier's original782 dispositions are preserved. Minimum next action is human scope/budget handling or existing direct proof of that clause, not automatic round3. A subsequent authorized correction should reuse validated current scope guards and demonstrate the About call path; no duplicate test is required where meaningful shared proof suffices.

Per-spec-decisions.json is the authoritative full 47-disposition record. Its exact_remaining_clauses and minimum_next_inputs_or_actions preserve every unproved case condition. Before new execution, the responsible owner should inspect existing shared assertions, arithmetic, transactions, serialization and fencing control flow against the precise conjunction. A new fixture or separately named test is unnecessary when meaningful existing evidence supplies it. Cases such as training-before-fit held-out/later-session rejection, raw-copy selected-scope/ack/job cardinality, profile accepted-reply-loss, pre-ack protected-write fencing, visible frozen P1, selected local export association/Cancel zero side effects and unrelated-process survival remain unproved in this released record; these gaps are not newly confirmed defects.

**OTGD-020-AND-ENV-005-02:** actual orchestration supplement proves migration failure prevents activation/web publication. Source `deploy/orchestrate.py:181–186` calls deploy-stopped before migrate; platform deploy-stopped runs CDK and service task definitions can change while desired count is zero. Exact previous deployment/recorded rollback-target retention is still unproved. Missing serialization alone is not proof of provider loss. Minimum input is already-existing qualified provider/state evidence or a supported exact retention proof; a fixture that assumes provider retention cannot supply it, and no deployment is authorized.

Installed Android/iOS software acceptance remains separate: secure Keychain/Keystore/SQLCipher persistence/atomic commit/kill/restart/denied unlock/key loss; OS permissions/Settings/Back; actual browser/deep-link; camera/BLE/touch/background/brightness/cancel; share cleanup; TalkBack/VoiceOver and 200% text. Compilation, core tests and Chromium component checks do not qualify those OS cases. Physical/electrical/optical/task timing/PPG/vendor/reader/assay/ECG calibration and safety, independent owner/enrollment/consent/study/model/scientific authority, and genuine AWS IAM/KMS/network/DNS/deployment/backup/restore/RPO/RTO/signing/store outcomes remain separately typed prerequisites. Human action is to supply or arrange those exact owner-controlled inputs, or explicitly adjudicate consequential scope/budget; no implicit extra correction is allowed.

Local reconstructed H source/config/image/runtime evidence remains disclosed and source-bound; it does not establish original cloud/ECR image provenance. Passing actual CI Fargate runtime is its own software observation. Real local issuer/PostgreSQL/LocalStack/browser/worker evidence is admitted only at its executed boundary. Worker interruption proves its production120-second lease/visibility and5claim/receive boundaries; it does not prove unexecuted900-second/raw-revocation/complete privacy lifecycle. Supplemental real processes prove bounded startup refusal and same-PID live200/ready503 outage; mobile device/HTTP/native boundaries are declared doubles and HR pipelines remain fictional software evaluation. No participant or scientific authority follows from fixture signatures.

Measurement mode remains default, fictional provenance remains explicit, and research authority stays independent/current. The future alcohol channel remains a separately calibrated fuel-cell breath-alcohol channel in **mg/L**, with no blood/BAC conversion or fitness-to-drive claim.

## Per-spec final decisions

The representative blocker below never replaces the full exact clause set in JSON. PASS applies to complete declared canonical software amendment scope only.

{chr(10).join(table)}

## Outcome dimensions and release

Specification readiness: this assessment issues no new DESIGN/SPEC_READY decision. Implementation: two narrow amendment approvals, 45 blocked; full application acceptance is NEEDS_HUMAN. Release readiness: unproved and not granted. External action: none performed or authorized by this disposition; no merge, deployment, paid service, publication or participant use. Final evidence disposition files are released for PM metadata-only records handling under D011v1. Required next actions are APR-001 and evidence/owner/scope adjudication after the exhausted limit. No action was denied by approval review, left pending after a tool mutation, or has an uncertain external outcome. All approver-owned writes are released after the companion hash manifest is generated. The initial3/44 generated draft is preserved as provisional-before-normative-about-review history, superseded by this final disposition.
'''
(O/'report.md').write_text(report)
outputs = []
for p in sorted(O.rglob('*')):
    if not p.is_file(): continue
    if p in [O/'release-manifest.json', O/'SHA256SUMS']: continue
    raw = p.read_bytes(); outputs.append({'path':str(p.relative_to(O)),'sha256':SHA(raw),'bytes':len(raw)})
write('release-manifest.json',{'status':'RELEASED_IMMUTABLE','released_at':NOW,
 'identity':identity,'overall_decision':'NEEDS_HUMAN','decision_counts':payload['decision_counts'],
 'source_candidate':binding['revision'],'source_tree':binding['tree'],
 'source_fingerprint_sha256':binding['source_fingerprint_sha256'],
 'all_owned_writes_released':True,'files':outputs})
manifest_files = outputs + [{'path':'release-manifest.json','sha256':SHA((O/'release-manifest.json').read_bytes())}]
(O/'SHA256SUMS').write_text(''.join(f"{x['sha256']}  {x['path']}\n" for x in manifest_files))
print(json.dumps({'overall':'NEEDS_HUMAN','decisions':payload['decision_counts'],
 'hash_errors':errors,'verified_records':len(checked),'literal_assertion_body_matches':sum(x['literal_body_matches'] for x in assertion_checks),
 'assertion_records':len(assertion_checks),'outputs':manifest_files},indent=2))
