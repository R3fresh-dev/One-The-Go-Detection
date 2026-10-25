from pathlib import Path
import json,hashlib,subprocess,datetime,xml.etree.ElementTree as E
R=Path('/workspace/One-The-Go-Detection'); L=Path('/workspace/scratch/otgd-20261025-0555-live'); C=L/'candidate-e89897cc852a';O=C/'reviews/security'; OLD=L/'candidate-cf74fcff6ad1/reviews/security'
b=json.loads((C/'candidate-binding.json').read_text()); old=json.loads((OLD/'per-spec-decisions.json').read_text()); now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=R).split(b'\0'); d=hashlib.sha256();count=0
for n in sorted(set(files)):
 if n and (R/n.decode()).is_file():d.update(n+b'\0'+(R/n.decode()).read_bytes());count+=1
binding={'observed_at':now,'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'tree':subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=R,text=True).strip(),'source_nonignored_files':count,'source_fingerprint_sha256':d.hexdigest(),'source_fingerprint_matches':d.hexdigest()==b['source_fingerprint_sha256'],'clean_status':not subprocess.check_output(['git','status','--porcelain'],cwd=R,text=True),'runtime_image':b['runtime_image']}
assert binding['revision']==b['revision'] and binding['tree']==b['tree'] and binding['source_fingerprint_matches'] and binding['clean_status']
identity={**old['reviewer'],'configuration_source':'Explicit OpenAI gpt-6.1-sol/high dispatch confirmed by PM; same independent reviewer reactivated for final candidate','independence':'Independent security reviewer; no candidate authoring or runtime execution; no agents spawned'}
updates={
'OTGD-001':'SEC-001–007 identity, least privilege, explicit upload and protected custody remain. SEC-01 and SEC-02 corrections are verified in source/focused evidence; current exact full implementation evidence is pending.',
'OTGD-020':'Independent hosted OAuth origin and callback pins remain build-time identity. Actual returned callback now matches exact selected target before exchange; no environment override or endpoint guard was loosened.',
'OTGD-021':'Home separates current physical/synthetic reader connection from owner/generation/online/config-expiry conditional channel availability; display cannot enable qualified capture.',
'OTGD-022':'Owned selected numeric HR/nonHR exports now use generic validated empty revision heads without gaining administrative revision eligibility; current HR re-admission and separate raw scope remain.',
'OTGD-023':'Connected signed-reader presentation is truthful while binding/provisioning and current per-channel authorization remain separate; secure BLE/origin protocol and actual start gates are unchanged.',
'OTGD-028':'Bounded owner/generation HMAC history cursor and immutable evidence remain; generic exports preserve selected original numeric results and exact empty revision companion.',
'OTGD-034':'Result view now tracks exact saved-result digest so first HR arrival and explicit refresh obtain current admission; existing offline/leaving/late-response/mismatch fences remain.',
'OTGD-036':'Home and Device share conditional channel display without mutating capability admission; Settings/privacy/raw ownership unchanged. Diagnostics and build identity remain protected.',
'OTGD-037':'SEC-01 independent endpoint pins and SEC-02 exact returned callback checks verified. Matching-state wrong target/ambiguous query refuses before all HTTP and identity mutation; replay/refresh/logout assertions preserved.',
'OTGD-042':'Current HR authority still governs stored reads, worker build/commit and download, plus view-bound client display and independently admitted local export. Numeric generic cloud export positive now proves unchanged exact result; no authority widening.',
}
extra_refs={
'OTGD-001':['apps/mobile/tests/auth-callback.test.ts'],
'OTGD-020':['apps/mobile/tests/auth-callback.test.ts'],
'OTGD-021':['apps/mobile/src/core/devicePresentation.ts','apps/mobile/src/ui/device-summary.tsx'],
'OTGD-022':['services/api/otgd/report_revisions.py','services/api/tests/test_current_result_readback.py'],
'OTGD-023':['apps/mobile/src/core/devicePresentation.ts','apps/mobile/tests/device-presentation.test.ts'],
'OTGD-028':['services/api/otgd/report_revisions.py','services/api/tests/test_current_result_readback.py'],
'OTGD-034':['apps/mobile/e2e/components.spec.ts','apps/mobile/tests/hr-read-admission.test.ts'],
'OTGD-036':['apps/mobile/src/core/devicePresentation.ts','apps/mobile/src/ui/device-summary.tsx'],
'OTGD-037':['apps/mobile/tests/auth-callback.test.ts'],
'OTGD-042':['services/api/otgd/report_revisions.py','apps/mobile/e2e/components.spec.ts'],
}
refs=set()
for row in old['decisions']:
 refs.update(x['path'] for x in row['supporting_evidence'])
for values in extra_refs.values():refs.update(values)
refs.update(['docs/factory/otgd-20261025-0555/decisions.md','docs/factory/otgd-20261025-0555/impact-register.md','docs/factory/otgd-20261025-0555/correction-round-2.md','docs/factory/otgd-20261025-0555/reports/correction-round2-auth.md','docs/factory/otgd-20261025-0555/reports/correction-round2-export.md','docs/factory/otgd-20261025-0555/reports/correction-round2-mobile.md','docs/factory/otgd-20261025-0555/reports/runtime-source-refresh-h.md'])
for p in (R/'docs/factory/otgd-20261025-0555/evidence/image-h-adoption').glob('*.json'):refs.add(str(p.relative_to(R)))
rawfiles={
'auth':['source-evidence-hashes.json','callback-red.log','red-native-observation.json','auth-release-final.log','auth-release.xml'],
'export':['red.xml','red-http-observations.json','focused-green.xml','focused-green-summary.json','green-source-bindings.json','final-handoff.json','unit-execution.json','unit.xml','unit-coverage.json'],
'mobile':['source-bindings.json','evidence-manifest.json','hr-mounted-red2.log','hr-manual-red.log','focused-green.log','full-unit.log','coverage.log','mobile-unit-coverage.json','focused-browser-green.log','full-browser.log'],
}
for area,names in rawfiles.items():
 for name in names:refs.add(str(L/f'correction-round2-{area}'/name))
refs.update([str(C/'candidate-binding.json'),str(C/'gate-process.json'),str(C/'final-gates.log'),str(OLD/'report.md'),str(OLD/'per-spec-decisions.json')])
evidence={}
for name in sorted(refs):
 p=Path(name) if name.startswith('/') else R/name
 evidence[name]={'sha256':sha(p),'bytes':p.stat().st_size} if p.is_file() else {'missing':True}
assert not [k for k,v in evidence.items() if v.get('missing')]
manifest_checks=[]
for area,name,fields in [('auth','source-evidence-hashes.json',['owned_source_sha256','dependency_sha256']),('export','final-handoff.json',['released_copy_sha256'])]:
 j=json.loads((L/f'correction-round2-{area}'/name).read_text())
 for field in fields:
  for path,expected in j[field].items():
   actual=sha(R/path);manifest_checks.append({'manifest':str(L/f'correction-round2-{area}'/name),'field':field,'path':path,'expected_sha256':expected,'actual_sha256':actual,'matches':actual==expected})
for item in json.loads((L/'correction-round2-mobile/source-bindings.json').read_text())['files']:
 actual=sha(R/item['path']);manifest_checks.append({'manifest':str(L/'correction-round2-mobile/source-bindings.json'),'path':item['path'],'expected_sha256':item['sha256'],'actual_sha256':actual,'matches':actual==item['sha256']})
assert all(x['matches'] for x in manifest_checks)
xmlchecks=[]
for area,name in [('auth','auth-release.xml'),('export','focused-green.xml'),('export','unit.xml')]:
 p=L/f'correction-round2-{area}'/name;root=E.parse(p).getroot();xmlchecks.append({'path':str(p),'sha256':sha(p),'testcase_elements':len(root.findall('.//testcase')),'failure_elements':len(root.findall('.//failure')),'error_elements':len(root.findall('.//error')),'skipped_elements':len(root.findall('.//skipped')),'scope':'Focused author execution, independently inspected; not current aggregate gates/native OS/live cloud'})
source_delta=[]
for path in subprocess.check_output(['git','diff','--name-only',old['binding']['revision'],b['revision'],'--','apps/mobile/src','services/api/otgd','firmware','deploy','infra','apps/mobile/modules'],cwd=R,text=True).splitlines():
 source_delta.append({'path':path,'sha256':sha(R/path),'disposition':'Current changed source/assertion inspected in this confirmation'})
rows=[]
for s,prior in zip(b['canonical_specs'],old['decisions']):
 assert s['id']==prior['spec_id'];actual=sha(R/s['path']);assert actual==s['sha256'];paths=list(dict.fromkeys([x['path'] for x in prior['supporting_evidence']]+extra_refs.get(s['id'],[])))
 reason=updates.get(s['id'],prior['reason'])
 if s['id'] in ['OTGD-006','OTGD-027']:reason+=' Final view-effect change is bound to exact saved result bytes; no cached admission is persisted.'
 n=int(s['id'][-3:]);prereqs=[]
 if n in [1,12,13,19,23,24,25,27,33,39,43]:prereqs.append('Physical/device sensing, electrical/optical safety, actual BLE/provisioning or native timing qualification as specified; software evidence cannot establish them.')
 if n in [1,8,9,11,16,19,24,25,26,27,30,35,38,39,40,41,42,43]:prereqs.append('Independent study/scientific/calibration/clinical or recovery authority where required; fictional fixture approval is not genuine authority.')
 if n in [1,14,15,20,44,45,46,47]:prereqs.append('Actual QA/prod IAM/KMS/private route/release/store signing or hosting execution as applicable; no deployment/merge/submission authorization.')
 if n in [1,12,17,18,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,36,37,38,39,40,47]:prereqs.append('Actual Android/iOS OS browser/permission/secure-storage/share/lifecycle/accessibility integration where required; host fixture/browser execution does not replace it.')
 rows.append({'spec_id':s['id'],'canonical_path':s['path'],'canonical_sha256':actual,'canonical_matches_candidate':True,'candidate_revision':b['revision'],'scope':'IMPLEMENTATION','review_domain':'SECURITY','decision':'BLOCKED','provisional':True,'source_review_decision':'NO_REQUIRED_SOURCE_CORRECTION_IDENTIFIED','reason':reason,'findings':[],'evidence_holds':['SEC-E01','SEC-E02'],'supporting_evidence':[{'path':x,**evidence[x]} for x in paths],'requirements':s['criteria'],'required_current_execution':'PENDING exact-candidate mandatory local/all14CI plus applicable clause/assertion reconciliation; focused author executions are supporting evidence only','external_prerequisites':prereqs,'carried_forward_source_scope':'Prior security trust-boundary inspection reaffirmed only for unchanged hashed source and unchanged canonical criteria; final source deltas independently inspected; historical runtime PASS not carried forward'})
closures=[{'id':'SEC-01','source_status':'CLOSED_IMPLEMENTATION_CONFIRMED','execution_status':'Focused pinning/refresh/restored/revocation/logout assertions present in99GREEN; full exact-candidate gates pending','evidence':['apps/mobile/src/core/oauthPolicy.ts','apps/mobile/src/services/auth.ts',str(L/'correction-round2-auth/auth-release.xml')]},{'id':'SEC-02','source_status':'CLOSED_IMPLEMENTATION_CONFIRMED','execution_status':'Real software-fixture RED inspected;42refusals/5positives plus99focusedGREEN match current source; native OS and final full gates pending','evidence':['apps/mobile/src/services/auth.ts:34-59','apps/mobile/src/services/auth.ts:134-158','apps/mobile/tests/auth-callback.test.ts',str(L/'correction-round2-auth/red-native-observation.json'),str(L/'correction-round2-auth/auth-release.xml')]},{'id':'HR-AUTH-007 disclosure correction / CODE-R1-003','source_status':'NO_SECURITY_REGRESSION_IDENTIFIED','execution_status':'21focused current source author cases include exact numericHR/nonHR export positive and retained currentHR refusals; real PG/S3/full gates pending','evidence':['services/api/otgd/report_revisions.py:247-289','services/api/otgd/report_revisions.py:815-835','services/api/tests/test_current_result_readback.py',str(L/'correction-round2-export/focused-green.xml')]},{'id':'CODE-R1-004 / UX-R001 / UI-003','source_status':'NO_SECURITY_REGRESSION_IDENTIFIED','execution_status':'Current394mobile and80browser author execution inspected; source-bound pending->HR/admission and current scope/expiry display assertions; actual native integration pending','evidence':['apps/mobile/src/ui/checks.tsx:1674-1695','apps/mobile/src/controller.ts:4070-4085','apps/mobile/src/core/devicePresentation.ts',str(L/'correction-round2-mobile/focused-browser-green.log')]},{'id':'SEC-E01','status':'OPEN_PENDING','reason':'Exact e89897c full7local/all14CI and782case reconciliation unavailable at this snapshot; no aggregate/historical substitution.'},{'id':'SEC-E02','status':'OPEN_PENDING_IMPORT','reason':'External final candidate reports/signoffs must be imported with current bindings at coherent boundary and independent council prerequisites; historical headers are not current signoff.'}]
obj={'schema_version':'1.0.0','observed_at':now,'reviewer':identity,'binding':binding,'scope':'IMPLEMENTATION','scoped_decision':'BLOCKED','source_review_decision':'NO_REQUIRED_SOURCE_CORRECTION_IDENTIFIED','provisional':True,'correction_round':2,'max_correction_rounds':2,'recovery_attempts':0,'no_tests_or_runtime_probes_run':True,'no_repository_writes':True,'all_specs_count':47,'decisions':rows,'findings':[],'prior_finding_closure':closures,'ready_for_final_evidence_update':True,'unresolved_after_final_round_policy':'No third repair/reset; exact unresolved source or mandatory evidence must remain NEEDS_HUMAN/BLOCKED for PM/council.'}
(O/'per-spec-decisions.json').write_text(json.dumps(obj,indent=2)+'\n')
(O/'evidence-index.json').write_text(json.dumps({'observed_at':now,'hash_algorithm':'SHA-256 over actual file bytes','candidate':binding,'artifacts':evidence,'author_source_manifest_verification':manifest_checks,'independent_xml_observation':xmlchecks,'source_delta_reinspection':source_delta},indent=2)+'\n')
(O/'evidence-snapshot.json').write_text(json.dumps({'observed_at':now,'gate_process':json.loads((C/'gate-process.json').read_text()),'final_gate_log':(C/'final-gates.log').read_text(),'current_completed_gates_not_inferred':True},indent=2)+'\n')
report=f'''# Independent final-candidate SECURITY confirmation

Reviewer `/root/replacement_security`, configured **OpenAI gpt-6.1-sol/high**, explicit PM-confirmed dispatch, separate independent reviewer context. Exact runtime model cannot independently be queried. No candidate authorship, test/runtime probe, service/Docker mutation or additional agents. Only new external `candidate-e89897cc852a/reviews/security/` outputs were written; cf74fcf history is preserved. Observed {now}.

**Security source review: no required source correction identified. Implementation security decision: BLOCKED, provisional pending current evidence.** SEC-01 and SEC-02 source corrections are independently confirmed below. All47 individual canonical path/hash/security decisions remain explicit in `per-spec-decisions.json`. This is neither global app completion, release approval, product/engineering signoff nor council approval. Correction **2/2**, recovery **0/3**; no third automatic correction.

Candidate `{b['revision']}`, tree `{binding['tree']}`, Factory `{b['factory_revision']}`, runtime local H `{b['runtime_image']}`. Actual HEAD/tree and all47 canonical hashes match. Independent full nonignored-source SHA-256 across **{count} files** is `{d.hexdigest()}`, equal to binding; git status is clean. All prior spec IDs/criteria remain unchanged. `evidence-index.json` records actual source/raw evidence hashes,31 author source/dependency bindings independently checked against current bytes, runner XML observations and final eight-file source/assertion delta. No prior CI/gates were promoted to current evidence.

## SEC-02 independently confirmed

`auth.ts:34–59` now compares the original returned target bytes to the **selected pending callback**, before URL normalization can admit suffix/userinfo/default-port/dot-segment variants. It refuses missing/nonstring/fragment/malformed-percent inputs and requires exactly one code and one state, two query pairs only, both equal to successful SDK params/current request. `auth.ts:134–158` runs this guard before attempt consume/token exchange. The error contains no callback query/code/token. Outgoing exact hosted-origin pins, state, PKCE S256, expiry/replay, coordinated refresh and captured-family logout behavior remain unchanged.

The actual pre-fix `red-native-observation.json` records Android platform-fixture selected `otgd-local://oauth/callback`, matching state/code delivered at `.../callback-extra`, sign-in true,1tokenexchange,1protectedlookup and fixture account switched. This confirms the original software path; it is not an Android/iOS OS exploit, provider redirect-policy bypass or arbitrary takeover claim.

Inspected `auth-callback.test.ts:9–166` directly. Three platform loops pair exact web/Android/iOS successes with9target variants each; the final case tests15invalid/missing/ambiguous query deliveries and a fresh exact retry. Thus42refusals and5successful controls are meaningful: each refusal asserts zeroHTTP and unchanged UI/Auth identity/auth generation. Runtime fixture does not manufacture missing override URLs. Focused runner JUnit contains **99testcase elements,0failure/error/skip**; raw log99PASS,0cancel/todo. All7owned+7dependency SHA values match this candidate. These focused author executions support source closure; final frozen aggregate/native OS evidence remains pending. Existing callback replay/three-loopback401-one-refresh/exact operation body/key/generation/ETag and endpoint/restored/revoke/logout controls were included, not replaced.

## Export, HR view and reader authority boundaries

`report_revisions.py:247–289` separates generic `_validated_base` from administrative `_base`. Generic validation retains finalized snapshot/result/owner/study/protocol/digest/target/manifest and **safe_result with currentHR context**. Administrative `_base` keeps its narrower outcome restrictions. `freeze_head:815–835` returns an empty companion only when neither report nor result revision exists in this owner/generation/check scope; any existing companion still uses full chain validation. No administrative reanalysis permission or data rewrite follows.

The prior security report's treatment of abstention-only export as valid generic policy was incomplete; admitted numeric export is required by the superseding shared contract. Current focused source/assertions now prove the numeric positive. `test_current_result_readback.py:126–194` uses actual authenticated current-authority HR and nonHR accepted worker results, obtains202export, completes worker, obtains200ZIP and compares **exact original result and all selected linked fields**, manifest size/hash and empty bound revision index. Controls retain numeric administrative refusal, both orphan/malformed companion refusals, legacy numeric422 and retiredHR request/build/transactional-commit/download refusal. Current safe_result and per-chunk download admission were not weakened. Parsed focused XML is21cases/0failure/error/skip; full unit XML has1538testcase elements/0failure/error/skip, with208subtests separately reported by author. Backend coverage89.925666812418% is supporting unit evidence; SQLite/explicit object-store doubles do not establish real PG/S3/SQS or final gates.

The Result effect (`checks.tsx:1674–1695`) owns a view beforeHR availability and depends on exact saved result digest, preserving original epoch/check identity. Explicit service refresh (`controller.ts:4070–4085`) can establish admission without a prior token only on the active same Result route; current view/new-result behavior retains newest-request, owner/generation/offline/background/leave and mismatch fences. Existing local export retains its **independent** every-selected-result admission before archive creation and final share release. Browser assertions `components.spec.ts:169–243` show pending/local-measurement->HR through actual SyncEngine/controller, withheld until separate admitted read, stable ID/epoch and exactly2reads without loop; manual refresh recovers absent prior token. These are browser/controller software fixtures, not actual native OS or scientific approvals.

Reader presentation now handles connected signed physical protocol truthfully, while explicitly stating binding/connection is not capture authority. Shared channel presentation (`devicePresentation.ts:215–293`, `device-summary.tsx:70–116`) uses active matching owner/generation/online capabilities and a configuration expiry strictly later than now. Physical connection is not an input and no presentation function enables Start. Supplied expiry rerender is a display timer, not an invented scientificTTL. Home/Device remain consistent for current/revoked/expired/unbound/offline states; scoped DeviceScreen changes leave Settings/privacy/raw admissions unchanged.

Inspected raw mobile coverage/source manifest and browser execution logs: all15mobile source/test SHA values match,394mobile tests/0skip and executable91.20015429866436% with unloaded native-sharing adapter countedzero; focused8browser and full80browser pass. These are focused/current-source author records, not the final frozen seven-gate/all14CI or actual OS proof.

## Reaffirmed source and provenance limits

All eight final source/assertion changes were inspected. Unchanged source/spec trust boundaries are reaffirmed only with current byte hashes: API RS256/issuer/client/access/current-family/account ownership; independently current model/capture/calibration/baseline authority; signed scoped reader grants and nonce/boot/origin fences; raw consent/upload/export separation, SQLCipher/SecureStore no-plaintext custody, deletion generation barrier, truthful retained-category/null-expiry receipts, recurring version erasure and diagnostics allowlist. Native/firmware signer/storage code did not change in round2; prior bounded source inspection remains applicable, while actual native OS, protected provisioning/BLE/sensor/electrical/optical/scientific requirements remain unverified. Software fixtures never create genuine independent approval.

Release sources are unchanged: current provenance defaults require all14live jobs; signed historical projections do not satisfy current admission. H packaging report records224exactCOPY entries and unchanged outsideCOPY metadata/serialized Config/platform; initial capacity-blocked proof is historical preparation, not the final adoption state. Actual adoption receipts separately record successful H load/tag/serial identityAPIworker refresh and preserved PostgreSQL/LocalStack identities/volumes; obsoleteG receipt records zero-reference nonforce cache removal and matching retained archive hash. This review inspected records, did not independently runDocker or adopt an image. H is reconstructed **local** evidence, not original ECR/cloud provenance. No denied or uncertain operation occurred under this reviewer.

## Current evidence holds and per-spec decisions

**SEC-E01 OPEN_PENDING:** current `gate-process.json` is bound to e89897c/H and running. At snapshot final log contains `RUN unit-coverage`; no final local-gates/all14CI or782-case current clause/assertion reconciliation is established. Current mandatory checks, strict>80coverage, unchanged120second lease/fullDLQ/browser/live dependencies cannot be replaced by focused counts, old candidate passes or PARTIAL classifications. A meaningful shared assertion may cover multiple clauses; no duplicate test is demanded simply for separate naming. Exact unproved software clauses remain with verifier; nativeOS/hardware/science/deployment prerequisites are separately retained per spec.

**SEC-E02 OPEN_PENDING_IMPORT:** final external reports require coherent PM import/current tested identity and actual independent council prerequisites. Historical dossier/review records are preserved and cannot substitute for these confirmations. No missing report or author evidence is invented as a signoff.

Actual decision ACK sent before dependent confirmation: D008v3 AFFECTED; D006v10/v11 AFFECTED; D010v2 AFFECTED; preserved D001/D003/D004/D005/D007/D009v11 AFFECTED, D002 NOT_AFFECTED. Read current brief, AGENTS, correction2, prior pinned council/evidence instructions and current decisions/impact. No authority/claim/correction-budget waiver.

Every row below is a security-domain **IMPLEMENTATION** decision for this exact candidate, provisional BLOCKED by required current evidence; source review for each identifies no required correction. External prerequisites are itemized independently in JSON rather than silently excluding any spec.

| Spec | Security implementation | Current source assessment |
|---|---|---|
'''
for row in rows:report+=f"| {row['spec_id']} | BLOCKED | {row['reason']} |\n"
report+='''\nReady for an actual final evidence update in these stable files when PM supplies completed exact-candidate gate/CI/case evidence. No source defect identified by this bounded confirmation remains open; pending execution/import and applicable external prerequisites remain blockers. Any unresolved required source/evidence condition after round2 must stay BLOCKED/NEEDS_HUMAN, with no silent third repair, merge, deployment, participant use, hardware/clinical/fitness-to-drive claim.\n'''
(O/'report.md').write_text(report)
checks=[]
for name in ['report.md','per-spec-decisions.json','evidence-index.json','evidence-snapshot.json']:checks.append(f'{sha(O/name)}  {name}')
(O/'SHA256SUMS').write_text('\n'.join(checks)+'\n')
print(json.dumps({'specs':len(rows),'unique_specs':len(set(x['spec_id'] for x in rows)),'source_manifest_checks':len(manifest_checks),'source_match':binding['source_fingerprint_matches'],'decisions':{'BLOCKED':47},'xml_observations':xmlchecks,'deliverables':str(O)}))
