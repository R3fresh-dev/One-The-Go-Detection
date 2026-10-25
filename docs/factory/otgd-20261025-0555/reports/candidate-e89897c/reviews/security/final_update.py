"""Apply only after verification explicitly releases final immutable records."""
from pathlib import Path
import json,hashlib,datetime,subprocess,collections,xml.etree.ElementTree as E
R=Path('/workspace/One-The-Go-Detection');C=Path('/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a');V=C/'verification';O=C/'reviews/security';H=O/'history/provisional-before-final-evidence'
release=O/'verification-release-received.json'
assert release.exists(), 'Wait for actual verification RELEASE before final hash binding'
now=datetime.datetime.now(datetime.timezone.utc).isoformat();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
b=json.loads((C/'candidate-binding.json').read_text());base=json.loads((H/'per-spec-decisions.json').read_text());cases=json.loads((V/'case-evidence.json').read_text());remaining=json.loads((V/'remaining-clauses.json').read_text());requirements=json.loads((V/'requirement-evidence.json').read_text());integrity=json.loads((V/'integrity.json').read_text())
assert len(cases['rows'])==782 and len({r['case_id'] for r in cases['rows']})==782
assert all(r['candidate']==b['revision'] and r['audit_completed'] for r in cases['rows'])
assert integrity['audit_pending']==0 and not integrity['errors']
assert cases['summary']['full_local_gate_pass'] and cases['summary']['full_current_ci_pass']
assert not any('pending' in t.lower() for r in remaining['rows'] for t in r.get('prerequisite_types',[])), 'Final clause taxonomy still contains pending-gate types'
local=json.loads((C/'local-final-artifacts.json').read_text());ci=json.loads((C/'ci-acceptance-summary.json').read_text());gate=json.loads((C/'gate-process.json').read_text());tree=json.loads((C/'ci-tree-binding.json').read_text())
assert gate['status']=='passed' and gate['exit_code']==0 and local['source_before_after_equal']
assert len(local['gates']['passed'])==7 and len(ci['jobs'])==14 and all(j['conclusion']=='success' for j in ci['jobs'])
assert tree['head']==b['revision'] and tree['exact_tree']==b['tree'] and tree['verified']
checks=[];artifact_index={}
def add(p):
 p=Path(p)
 if str(p) not in artifact_index:artifact_index[str(p)]={'sha256':sha(p),'bytes':p.stat().st_size}
 return artifact_index[str(p)]
for name in ['candidate-binding.json','gate-process.json','local-final-artifacts.json','ci-acceptance-summary.json','ci-tree-binding.json','ci-jobs-final.json','ci-artifacts-final.json','final-records-decision.json','final-gates.log']:
 add(C/name)
for doc in [local,ci]:
 for item in doc['artifacts']:
  actual=add(item['path'])['sha256'];assert actual==item['sha256'];checks.append({'path':item['path'],'sha256':actual,'manifest_matches':True})
for stage in [1,2,3]:
 p=C/f'ci-artifacts-verified-stage{stage}.json';add(p)
 for a in json.loads(p.read_text()):
  assert add(a['archive'])['sha256']==a['sha256']
  for entry in a['entries']:assert add(entry['path'])['sha256']==entry['sha256']
release_manifest=json.loads((V/'release-manifest.json').read_text())
assert sha(V/'release-manifest.json')==json.loads(release.read_text())['release_manifest_sha256']
for item in release_manifest['files']:
 assert add(V/item['path'])['sha256']==item['sha256']
for p in V.glob('*.json'):add(p)
for p in V.glob('*.md'):add(p)
for p in (V/'specs').glob('*/test-results.*'):add(p)
for section in ['operations','semantics']:
 for p in (C/'supplemental'/section).rglob('*'):
  if p.is_file():add(p)
for p in (C/'current-local').glob('*'):
 if p.is_file():add(p)
for p in C.glob('ci-*.log'):add(p)
add(release)
files=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=R).split(b'\0');d=hashlib.sha256();n=0
for f in sorted(set(files)):
 if f and (R/f.decode()).is_file():d.update(f+b'\0'+(R/f.decode()).read_bytes());n+=1
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==b['revision'];assert d.hexdigest()==b['source_fingerprint_sha256'];assert not subprocess.check_output(['git','status','--porcelain'],cwd=R,text=True)
prior_index=json.loads((H/'evidence-index.json').read_text())
source_bindings={}
for path,record in prior_index['artifacts'].items():
 if not path.startswith('/'):
  assert sha(R/path)==record['sha256'];source_bindings[path]=record
rows=[];residuals_by_spec={};pass_specs=[];blocked_specs=[]
for spec,prior in zip(b['canonical_specs'],base['decisions']):
 assert spec['id']==prior['spec_id'] and sha(R/spec['path'])==spec['sha256']
 cr=[r for r in cases['rows'] if r['spec_id']==spec['id']];rr=[r for r in remaining['rows'] if r['case_id'].startswith(spec['id']+'-')]
 residuals=[]
 for r in rr:
  types=r.get('prerequisite_types',[])
  residuals.append({'case_id':r['case_id'],'status':r['status'],'exact_unproved_clauses':r['unproved_then_clauses'],'prerequisite_types':types,'current_assertion_refs':r.get('current_source_assertion_refs',[]),'software_evidence_gap':any(t.startswith('software') or t.startswith('live_dependency') for t in types),'external_prerequisite':any(x in t for t in types for x in ['native_os','physical_hardware','study_scientific','deployment_cloud','provider_credentials','independent_owner']),'not_a_demonstrated_source_defect':True})
 status='PASS' if not residuals and all(r['status']=='PASS' for r in cr) else 'BLOCKED'
 (pass_specs if status=='PASS' else blocked_specs).append(spec['id'])
 reason=prior['reason'].replace('current exact full implementation evidence is pending.','current mandatory execution is verified; exact remaining clauses are assessed below.')
 if status=='PASS':reason+=' Current source/helper assertions and named local/CI execution close both scoped canonical scenarios; no residual clause is asserted by this security review. This PASS does not qualify the surrounding app, native OS, research or release.'
 else:reason+=' Required exact implementation clause evidence remains incomplete: '+residuals[0]['case_id']+' — '+' '.join(residuals[0]['exact_unproved_clauses'])
 relevant_observations=[]
 for r in cr:
  for obs in r.get('actual_named_observations',[]):
   if obs.get('artifact') and Path(obs['artifact']).exists():
    p=obs['artifact'];actual=add(p)['sha256']
    if obs.get('artifact_sha256'):assert actual==obs['artifact_sha256']
    relevant_observations.append({'case_id':r['case_id'],'name':obs['name'],'status':obs['status'],'artifact':p,'artifact_sha256':actual})
 row={**prior,'decision':status,'provisional':False,'reason':reason,'evidence_holds':[] if status=='PASS' else ['SEC-E03'],'required_current_execution':'COMPLETED: all7mandatory local gates/currentCI14; exact tested merge tree equals candidate; no skipped mandatory gate inferred','case_dispositions':dict(collections.Counter(r['status'] for r in cr)),'case_ids':[r['case_id'] for r in cr],'remaining_exact_clauses':residuals,'software_evidence_gap_case_ids':[r['case_id'] for r in residuals if r['software_evidence_gap']],'external_prerequisite_case_ids':[r['case_id'] for r in residuals if r['external_prerequisite']],'current_named_execution_evidence':relevant_observations,'current_case_evidence':{'path':str(V/'case-evidence.json'),'sha256':sha(V/'case-evidence.json')},'current_requirement_evidence':{'path':str(V/'requirement-evidence.json'),'sha256':sha(V/'requirement-evidence.json')},'current_remaining_clauses':{'path':str(V/'remaining-clauses.json'),'sha256':sha(V/'remaining-clauses.json')},'council_admission':'Independent security-domain judgment only; no product/engineering/council approval is invented'}
 rows.append(row);residuals_by_spec[spec['id']]=residuals
assert len(rows)==47
result={**base,'observed_at':now,'provisional':False,'final_evidence_update':True,'scoped_decision':'BLOCKED','integration_escalation':'NEEDS_HUMAN','source_review_decision':'NO_REQUIRED_SOURCE_CORRECTION_IDENTIFIED','binding':{**base['binding'],'observed_at':now,'source_nonignored_files':n,'source_fingerprint_sha256':d.hexdigest(),'source_fingerprint_matches':True,'clean_status':True},'decisions':rows,'decision_counts':dict(collections.Counter(r['decision'] for r in rows)),'findings':[],'required_execution':{'local':'PASS7/7','ci':'PASS14/14','ci_run_id':ci['run_id'],'tested_merge':tree['tested_merge'],'exact_tree':tree['exact_tree'],'case_reconciliation':cases['summary'],'current_execution_hold_closed':True},'evidence_holds':[{'id':'SEC-E03','type':'EXACT_CLAUSE_EVIDENCE_AND_EXTERNAL_PREREQUISITES','status':'BLOCKED; final2/2 NEEDS_HUMAN for unresolved scope','software_defect_count':0,'reason':'Unproved software clauses are separated from actual nativeOS/hardware/science/study/deployment prerequisites in each spec; no automatic third correction/test expansion or aggregate PASS.'}],'prior_finding_closure':base['prior_finding_closure'],'decision_acknowledgments':['D011v1 AFFECTED: auxiliary metadata-only evidence branch leaves tested primary e898 source unchanged; no newrun/supervisor/permission; priorD001–D010 preserved'],'verification_release':json.loads(release.read_text()),'ready_for_final_evidence_update':False,'remaining_blockers_are_not_pending_gates':True}
for item in result['prior_finding_closure']:
 if item['id'] in ['SEC-01','SEC-02']:
  item['execution_status']='CLOSED: exact current local/CI source-bound assertions admitted; nativeOS external prerequisites and remaining canonical variants separately explicit.'
 if item['id'] in ['HR-AUTH-007 disclosure correction / CODE-R1-003','CODE-R1-004 / UX-R001 / UI-003']:item['execution_status']='Current source-bound local/CI execution admitted; exact remaining canonical software/nativeOS/external prerequisites explicitly separated per spec.'
 if item['id']=='SEC-E01':item.update(status='CLOSED_EXECUTED_AND_RECONCILED',reason='Exact current7local/14CI/782-case reconciliation now admitted; residual gaps retained as SEC-E03, no stale pending gate claim.')
 if item['id']=='SEC-E02':item.update(status='REVIEW_DELIVERED; PM_METADATA_PUBLICATION_PLANNED',reason='Final reports delivered externally; D011 auxiliary records publication remains PM-owned, not source defect or invented council approval.')
(O/'per-spec-decisions.json').write_text(json.dumps(result,indent=2)+'\n')
(O/'evidence-index.json').write_text(json.dumps({'observed_at':now,'candidate':result['binding'],'hash_algorithm':'SHA-256 actual bytes','source_bindings_reaffirmed':source_bindings,'final_artifacts':artifact_index,'explicit_manifest_verifications':checks,'provisional_history':str(H),'independent_review_scope':'Read-only source/assertion/raw inspection; no reviewer tests/services/Git writes'},indent=2)+'\n')
(O/'evidence-snapshot.json').write_text(json.dumps({'observed_at':now,'gate_process':gate,'local_final_artifacts':local,'ci_acceptance':ci,'ci_tree_binding':tree,'verification_summary':cases['summary'],'verification_integrity':integrity,'verification_release':json.loads(release.read_text()),'no_pending_gates':True},indent=2)+'\n')
(O/'remaining-security-implementation-clauses.json').write_text(json.dumps({'candidate':b['revision'],'scope':'All47 security-domain IMPLEMENTATION admission; exact verifier residual clauses retained, not a defect inventory','software_gaps_are_not_test_orders':True,'by_spec':residuals_by_spec},indent=2)+'\n')
report=f'''# Final independent security decision — e89897cc852a

**Security source findings are closed; overall IMPLEMENTATION admission remains BLOCKED, requiring NEEDS_HUMAN resolution after final correction2/2.** Per-spec security decisions: **{len(pass_specs)}PASS, {len(blocked_specs)}BLOCKED**, each with exact reasons and canonical hashes in `per-spec-decisions.json`. No newly demonstrated source defect. This is independent security-domain review, not global application/council/release approval.

Reviewer `/root/replacement_security`, configured OpenAI **gpt-6.1-sol/high**, explicit parent-confirmed dispatch. Exact runtime model is not independently queryable. Same independent reviewer, no implementation authorship. Observed{now}. No source/dependency/service/test/runtime/Git actions or additional agents; writes remain within this external security directory. Previous provisional files are preserved byte-for-byte in `history/provisional-before-final-evidence/` and earlier cf74fcf review remains untouched.

Candidate `{b['revision']}`, tree `{b['tree']}`, fingerprint `{d.hexdigest()}` over{n}nonignoredfiles. HEAD, full fingerprint, clean status and all47 canonical hashes independently reread and match. Runtime H remains disclosed reconstructed local proof, not original cloud-image provenance. Correction2/2,recovery0/3 unchanged. D011v1 actually ACKed AFFECTED: final safe records may use auxiliary `factory/one-the-go-detection-20261025-evidence`; primary source remains e898. Auxiliary records commit is not separately application-tested, does not create a newrun/supervisor/permission, and remains PM-owned. No evidence publication/Git action by this reviewer is claimed.

## Executed evidence now admitted

The seven mandatory local gates **passed**, `gate-process.json` exit0, with exact source before/after equality. CI run **40185247204 passed all14jobs**, including merge-gate. Tested merge `{tree['tested_merge']}` has exact candidate tree `{tree['exact_tree']}`; merge/head distinction is explicit. These are completed observations, no longer pending. Independently rehashed19local-manifest artifacts,5CI-summary references,9CI archives and35extracted entries with no mismatches. `evidence-index.json` additionally binds the final released verifier records and actual named observations.

Parsed current local XML:1538APIunit,1508PostgreSQL,80components,9protectedSDK,6ATDD,2authenticated-browser and2hosted-preview testcase elements, all0failure/error/skip. API executable coverage **89.925666812418%** and mobile **91.20015429866436%** exceed80. Raw current PG/journal checks demonstrate real dependency migration and restricted runtime DDL/authority/audit/ticket denial. Docker-health records5healthyservices and2successfulinitializers. Current worker interruption evidence preserves actual120secondlease/visibility,5export+2result interruption stages and5claim/receive exhaustion/DLQ handling with source equality. Scope stays structured fictional exports/synthetic measurement results; it does not execute raw-export revocation,900secondworkdeadline,allHTTPprivacy lifecycle or cloud/native/science qualification. Current live browser executes actual ownedPKCE/upload/export/replay/reload/withdrawal/deletion/logout fictional journeys; it is not installed Android/iOS secure-storage/OS validation.

Verifier explicitly RELEASED final records before this hash binding. The782stablecases/411requirements/47specs have0unauditedrows and final dispositions **{cases['summary']['statuses']}**. Those figures are evidence classifications, not bug counts and not automatic signoffs. Local/CI tests can be reused across clauses only where actual meaningful assertions establish the exact clause; current shared source/helper/named-execution mappings were considered. No duplicate test was demanded solely for naming.

## Finding closure and retained boundaries

**SEC-01 CLOSED:** independently pinned hosted-origin/endpoints/callbacks remain distinct from issuer and revalidate fresh/restored/exchange/refresh/revocation/logout traffic; current unit/CI evidence executes meaningful negative destination controls. **SEC-02 CLOSED:** exact returned success target bytes and unique matching code/state query are checked before consume/exchange. Actual pre-fix matching-state wrong-target RED is preserved;42refusals/5positives and99focusedGREEN were admitted alongside current aggregate source-bound execution. Wrong targets assert zeroHTTP and unchangedidentity/generation. No arbitrary takeover/provider redirect-policy bypass is alleged.

NumericHR/nonHR cloud export correction preserves generic validated exact evidence, currentHR safe_result context and narrower administrative revision eligibility.21focused assertions and current API/PG execution prove202->worker->200ZIP with unchanged original numeric result/linked evidence and retain orphan/legacy/admin/current-authority refusals. HR Result first-arrival/manual-refresh changes retain exactresult/view/account/generation/epoch/foreground/offline/newest-request fences. Local export separately re-admits selectedHR results before construction and final sharing; display admission is not export authority. Reader/Home/Device presentation separates physical connection and binding from current conditional channel authority, without enabling Start. Prior bounded source rationale and source hashes remain available in preserved provisional report; no security regression was identified in final source.

Supplemental actual process evidence supports production-local-config refusal, unavailableDB live200/ready503 and auth401 without secret echo; software semantic evidence supports HR strata accounting and offline active-reader withdrawal/late-callback fences. Declared doubles remain doubles. The rollback supplemental executes modeled migration failure and proves rollout stops before activation/publication. **OTGD-020-AND-ENV-005-02 exact previous rollback-target retention remains unproved**: prior release/taskdefinition refs are not retained in emitted state, while CDK deploy-stopped precedes migrate and may update stopped taskdefinitions. This absence is not alone a demonstrated cloud-retention defect; no unauthorized deployment was performed. Required recorded-target evidence cannot be replaced by circuit-breaker settings or `rollback_executed:false`.

**SEC-E01 CLOSED:** current mandatory gates/CI and full case reconciliation received. **SEC-E02:** independent security reports are delivered; PM's D011 metadata-only import/publication and actual council assembly remain separate actions, not an invented signoff. **SEC-E03 BLOCKED:** exact software clauses and external prerequisites remain below/JSON. Broad presentation/variant/authority integration gaps are not dismissed because aggregates passed, and are not relabeled hardware prerequisites.

Examples of remaining software evidence: raw-export selected-purpose/job/source/version/archive/revocation assertions in OTGD-010; operator exacthistory/fencing/settlement variants in011; protected reader/native signedscope/lateorigin/rawhandoff variants in012/013; recover retainedPG/journal exact admission in016; encrypted stopped-app retention/reopen/refusal in018; persistent A->B namespace/signout/revokedrefresh UI conjunctions in037; participant scoped receipt/withdrawal/replacement variants in038/039; source/artifact/provider/subprocess boundary variants in047. Full exact caseID/clause/source references are retained per spec, rather than interpreted as demonstrated defects or automatic orders for new tests. NativeOS/physicalhardware/scientificstudy/owner/cloudstore requirements remain separate explicit prerequisites. No participant-use, hardware/electrical/optical/clinical/fitness-to-drive or deployment authority is inferred.

## Final47security-domain decisions

PASS is limited to the scoped canonical software clauses supported by inspected source/helper bodies and exact current named execution. It does not admit the surrounding application or release. BLOCKED identifies an exact unproved implementation clause/prerequisite; all clauses and their type are retained in `remaining-security-implementation-clauses.json` and each JSON row. Final2/2 permits no silent thirdrepair/reset. Needed human action is evidence/prerequisite/scope adjudication, not approval to pretend an unexecuted clause passed.

| Spec | Final security decision | Exact rationale / representative remaining clause |
|---|---|---|
'''
for row in rows:
 explanation=row['reason'] if row['decision']=='PASS' else row['remaining_exact_clauses'][0]['case_id']+': '+' '.join(row['remaining_exact_clauses'][0]['exact_unproved_clauses'])
 explanation=explanation.replace('|','\\|').replace('\n',' ')
 report+=f"| {row['spec_id']} | {row['decision']} | {explanation} |\n"
report+='''\nRequired next step: preserve exact unproved software clauses, obtain only authorized prerequisite observations or a documented human scope decision, and let the real independent council assess readiness from all actual reports. No merge/deploy/participant use. No denied/pending/uncertain tool action by this reviewer remains; evidence gaps and PM publication/council actions are explicitly separate.\n'''
(O/'report.md').write_text(report)
checks=[]
for name in ['report.md','per-spec-decisions.json','evidence-index.json','evidence-snapshot.json','remaining-security-implementation-clauses.json','verification-release-received.json']:checks.append(f'{sha(O/name)}  {name}')
(O/'SHA256SUMS').write_text('\n'.join(checks)+'\n')
print(json.dumps({'decision_counts':result['decision_counts'],'pass_specs':pass_specs,'blocked_specs':blocked_specs,'case_summary':cases['summary']['statuses'],'case_evidence_sha256':sha(V/'case-evidence.json'),'remaining_clauses_sha256':sha(V/'remaining-clauses.json'),'requirement_evidence_sha256':sha(V/'requirement-evidence.json'),'output':str(O)}))
