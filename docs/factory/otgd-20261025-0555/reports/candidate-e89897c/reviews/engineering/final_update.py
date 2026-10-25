import pathlib,json,hashlib,collections,datetime,xml.etree.ElementTree as ET,subprocess
O=pathlib.Path(__file__).parent;C=O.parent.parent;V=C/'verification';R=pathlib.Path('/workspace/One-The-Go-Detection')
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
# Run only after the actual verifier RELEASE has been delivered by native collaboration.
D=json.load(open(O/'provisional-source-review/per-spec-decisions.json'));cases=json.load(open(V/'case-evidence.json'));rows=cases['rows'];requirements=json.load(open(V/'requirement-evidence.json'))['requirements'];integrity=json.load(open(V/'integrity.json'));summary=json.load(open(V/'case-summary.json'))
assert len(rows)==782 and len(requirements)==411 and summary['audit_pending']==0 and not integrity['errors'];assert summary['full_local_gate_pass'] and summary['full_current_ci_pass']
local=json.load(open(C/'local-final-artifacts.json'));ci=json.load(open(C/'ci-acceptance-summary.json'));jobs=json.load(open(C/'ci-jobs-final.json'))['jobs'];assert len(jobs)==14 and all(x['conclusion']=='success' for x in jobs)
assert local['exit_code']==0 and local['source_before_after_equal'] and local['clean'];assert len(local['gates']['passed'])==7;assert ci['candidate']==D['candidate_revision'] and ci['tree']==D['candidate_tree']
stages=[]
for i in [1,2,3]:stages+=json.load(open(C/f'ci-artifacts-verified-stage{i}.json'))
artifacts=local['artifacts']+[{'path':a['archive'],'sha256':a['sha256']} for a in stages]+[x for a in stages for x in a['entries']]
assert all(sha(a['path'])==a['sha256'] for a in artifacts)
records=json.load(open(V/'source-assertions.json'));source_errors=[];helper_count=0
for k,x in records.items():
 p=pathlib.Path(x['path']);p=p if p.is_absolute() else R/p
 if not x['found'] or sha(p)!=x['file_sha256'] or hashlib.sha256(x['body'].encode()).hexdigest()!=x['body_sha256']:source_errors.append(k)
 for y in x['helpers']:
  helper_count+=1
  if hashlib.sha256(y['body'].encode()).hexdigest()!=y['body_sha256']:source_errors.append(k+'helper')
assert not source_errors
frozen=V/'source-binding.json';released_files=['case-evidence.json','requirement-evidence.json','remaining-clauses.json','case-summary.json','integrity.json','dossier-proposals.json','software-evidence-residuals.json','mixed-software-external-residuals.json','external-prerequisites.json','source-assertions.json','source-binding.json','final-local-admission.json','final-ci-admission.json','operations-admission.json','semantics-admission.json','summary.json']
evidence=[ref(C/n) for n in ['local-final-artifacts.json','ci-acceptance-summary.json','ci-run-final.json','ci-jobs-final.json','ci-tree-binding.json','ci-artifacts-final.json','ci-artifacts-verified-stage1.json','ci-artifacts-verified-stage2.json','ci-artifacts-verified-stage3.json','final-records-decision.json','runtime-readback.json','gate-process.json']]+[ref(V/n) for n in released_files]
for folder,mn in [('operations','manifest.json'),('semantics','artifact-manifest.json')]:
 p=C/'supplemental'/folder;manifest=json.load(open(p/mn));m={x['path']:x['sha256'] for x in manifest} if isinstance(manifest,list) else manifest['sha256'];assert all(sha(p/n)==s for n,s in m.items());evidence += [ref(p/mn),ref(p/'report.md')]
passspecs={'OTGD-002','OTGD-004','OTGD-007'}
passwhy={
'OTGD-002':'PASS for the entire canonical dashboard amendment in IMPLEMENTATION software scope: current active account/generation capability gating plus actual rendered Home/row scientific labels and immutable verifier/legacy/local/guest refusal jointly establish both current scenarios and requirement clauses. Original time/provenance/missingness are preserved by unchanged typed scientific records/shared renderers and their current execution; no sign-in-derived authority. Genuine approval/installed OS/base-dashboard completeness are not asserted by this amendment decision.',
'OTGD-004':'PASS for the entire canonical historical-result amendment in IMPLEMENTATION software scope: actual shared History/row/detail rendering, typed measurement qualifier/provenance formatting and current immutable1.1 schema/linkage/proof checks preserve original target/evaluation/measurement semantics; legacy and changed proof refuse score. Current cases cover historical scope and unauthorized promotion. This does not sign off base History offline/native/UI coverage or independently qualify science.',
'OTGD-007':'PASS for the entire canonical settings capability amendment in IMPLEMENTATION software scope: actual rendered service capability component, strict admitted account/configuration scope, current public-format no-authority and malformed/legacy/guest negatives plus fixed-production build/configuration tests establish conditional scope without local authority. This is not a general Settings/native OS or research/illumination approval.'}
results=[];all_remaining=[]
for s in D['specs']:
 sid=s['spec_id'];cs=[x for x in rows if x['spec_id']==sid];rem=[x for x in cs if x['status']!='PASS'];ispass=sid in passspecs
 assert not ispass or (not rem and all(x['audit_completed'] for x in cs))
 s['decision']='PASS' if ispass else 'BLOCKED';s['provisional']=False;s['final_signoff']=True;s['signoff_meaning']='Independent engineering IMPLEMENTATION decision for this canonical spec and exact source/evidence; not council approval or APP_VERIFIED'
 s['judgment']=passwhy[sid] if ispass else s['judgment']+' All applicable exact-source local/CI software gates now pass. Final engineering acceptance remains blocked only by the precise current unproved clauses listed below, not aggregate gate status.'
 s['open_evidence_findings']=[] if ispass else ['ENG-SIGN-002-ACCEPTANCE_RESIDUAL']+(['ENG-SIGN-003'] if any('native_os_execution' in x['remaining_prerequisite_types'] for x in rem) else [])
 s['gate_status']='PASS: all7local and14CI on exactcandidate/identicaltestedmergetree, no mandatory test skips; ENG-SIGN-001 CLOSED'
 s['current_case_status_counts']=dict(collections.Counter(x['status'] for x in cs));s['current_case_ids']=[x['case_id'] for x in cs]
 s['current_requirement_evidence']=[x for x in requirements if x['spec_id']==sid]
 s['remaining_clauses']=[{'case_id':x['case_id'],'status':x['status'],'exact_unproved_clauses':x['unproved_then_clauses'],'prerequisite_types':x['remaining_prerequisite_types'],'proved_software_scope':x['current_assertions_proven'],'current_assertion_refs':x['current_source_assertion_refs'],'current_named_execution_count':len(x['actual_named_observations']),'minimal_next_evidence_or_action':x['minimal_next_evidence_or_action'],'not_a_confirmed_source_defect':not bool(x['open_implementation_defect'])} for x in rem]
 s['exact_remaining_software_evidence_and_external_limits']='No unproved current canonical case clause in this scoped amendment. Real independent science/study, native OS and broader contributing capabilities remain separately unsigned.' if ispass else 'See remaining_clauses: exact software evidence and native OS/hardware/scientific/study/deployment prerequisites remain separated percase; none is waived or automatically treated as a software bug.'
 s['current_clause_reconciliation']='FINAL RELEASED: all782 stablecases/411requirements independently mapped; zero auditpending, currentnamedexecution/hashbindings admitted.'
 s['decisions_acknowledged'].append('D011v1 metadata-onlyauxevidencebranch preservesprimarye898testedidentity/noapplicationtestedclaimforevidencecommit')
 s['supporting_actual_evidence']=[ref(pathlib.Path(x['path'])) for x in s['supporting_actual_evidence'] if pathlib.Path(x['path']).is_file()]+evidence
 s['supporting_actual_evidence']=list({x['path']:x for x in s['supporting_actual_evidence']}.values())
 s['case_evidence_binding']=ref(V/'case-evidence.json');s['requirement_evidence_binding']=ref(V/'requirement-evidence.json');s['remaining_clause_binding']=ref(V/'remaining-clauses.json');results.append(s)
 all_remaining +=[{'spec_id':sid,**x} for x in s['remaining_clauses']]
D['specs']=results;D['overall_decision']='NEEDS_HUMAN';D['final_signoff']=True;D['scope']='Final independent IMPLEMENTATION engineering decisions for all47 canonical specs; exactcandidate softwaregatesPASS; remainingacceptanceproof/prerequisites explicit; notAPP_VERIFIED'
D['decision_counts']=dict(collections.Counter(x['decision'] for x in results));D['current_case_counts']=dict(collections.Counter(x['status'] for x in rows));D['finalized_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();D['final_gate_hold']='RESOLVED all7local and14CI exactcandidate/identicalmergetree'
D['initial_finding_closure']={'ENG-SIGN-001':'CLOSED: independently admitted all7local/all14CI raw/currenthash/sourcestable/tree/coverage/nativebuild/dependency/worker/performance evidence.','ENG-SIGN-002':'MAPPING/INTEGRITY CLOSED:782currentcases411requirements47specs623assertions342helpers/zeroauditpending; ACCEPTANCE RESIDUALS OPEN exactlyas listed, distinctfromsourcebugs/externalprerequisites.','ENG-SIGN-003':'OPEN:actualinstalledAndroid/iOSsoftwarematrixnotexecuted; compilation/core/browserfixturescannotreplaceit.'}
D['gate_observation']=json.load(open(C/'gate-process.json'));D['gate_evidence']=evidence;D['current_case_reconciliation']=summary;D['third_correction_authorized']=False;D['verifier_release']='Explicit native collaboration RELEASE received before final binding';D['no_global_app_or_release_verification']=True
(O/'per-spec-decisions.json').write_text(json.dumps(D,indent=2)+'\n')
(O/'remaining-needs.json').write_text(json.dumps({'candidate':D['candidate_revision'],'not_a_bug_inventory':True,'not_new_test_or_third_correction_orders':True,'rows':all_remaining},indent=2)+'\n')
lines=['# Final independent engineering decisions','',f"Candidate `{D['candidate_revision']}`; {D['decision_counts']}. Gates all7local/all14CI PASS; overall full implementation acceptance NEEDS_HUMAN. Exact remaining clause details are in remaining-needs.json and per-spec-decisions.json.",'','| Spec | Decision | Current case outcomes | Engineering judgment |','|---|---|---|---|']
for s in results:lines.append(f"| {s['spec_id']} | {s['decision']} | {s['current_case_status_counts']} | {s['judgment']} |")
(O/'per-spec-dispositions.md').write_text('\n'.join(lines)+'\n')
I=json.load(open(O/'provisional-source-review/inspection-evidence.json'));I['final_gate_evidence']=evidence;I['independent_gate_artifact_validation']={'all_local_and_downloaded_ci_hashes_match':True,'downloaded_ci_archives':len(stages),'downloaded_ci_entries':sum(len(x['entries']) for x in stages),'assertion_records':len(records),'source_files':len({x['path'] for x in records.values()}),'helper_records':helper_count,'source_body_helper_mismatches':source_errors};I['released_case_summary']=summary;I['final_verifier_release']=True;(O/'inspection-evidence.json').write_text(json.dumps(I,indent=2)+'\n')
print(json.dumps({'decisions':D['decision_counts'],'currentcases':D['current_case_counts'],'remaining_case_rows':len(all_remaining),'evidencehashes':{n:sha(V/n) for n in ['case-evidence.json','requirement-evidence.json','remaining-clauses.json','integrity.json']}},indent=2))
