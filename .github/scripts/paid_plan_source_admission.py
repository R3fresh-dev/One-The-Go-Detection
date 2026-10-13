import hashlib, io, json, os, re, subprocess, zipfile
SOURCE = '0844868aa543af4ab75ac5065ad48cf807b86bb3'
TREE = '1afe65b4d2a6ba3a4c541c9ecf7bc61f287ee908'
RUN = 38350430258
ARTIFACT = 11790454913
RAW_SHA256 = '9338903893d1bb1d82097cca4ea7a59cd81579d1f85cb853310c981592a2d165'
REPOSITORY = 'R3fresh-dev/One-The-Go-Detection'
WORKFLOW = '.github/workflows/merge-gate.yml'
JOBS = {'unit-coverage', 'components', 'atdd', 'preview / ios', 'platform / postgres-integration',
    'native / android', 'native / protected-reader', 'native / ios', 'platform / localstack-integration',
    'native / shared-and-firmware', 'platform / contracts-and-synthesis', 'platform / fargate-container-runtime',
    'preview / android', 'merge-gate'}
LABELS = {'unit-coverage', 'atdd', 'components', 'performance', 'live-dependencies', 'docker-health',
    'localstack-api', 'specifications', 'native-android', 'native-ios', 'firmware', 'hosted-android', 'hosted-ios'}

def require(condition, reason):
    if not condition:
        raise SystemExit('Regional read-only admission blocked: ' + reason)

def command(args, binary=False):
    result = subprocess.run(args, capture_output=True, text=not binary, timeout=30)
    require(result.returncode == 0 and len(result.stdout if binary else result.stdout.encode()) <= 1048576,
        'bounded authenticated command unavailable')
    return result.stdout

def api(path):
    return json.loads(command(['gh', 'api', (f'repos/{REPOSITORY}/' + path).rstrip('/')]))

def latest():
    response = api('actions/workflows/merge-gate.yml/runs?head_sha=' + SOURCE + '&per_page=100')
    require(response.get('total_count', 101) <= 100, 'gate inventory exceeds bound')
    candidates = [r for r in response['workflow_runs'] if r.get('head_sha') == SOURCE
        and r.get('path') == WORKFLOW and r.get('head_branch') == 'main' and r.get('event') == 'push']
    require(candidates and max(r['id'] for r in candidates) == RUN, 'latest trusted main gate differs')

require(ARTIFACT > 0 and re.fullmatch(r'[0-9a-f]{64}', RAW_SHA256), 'root gate/artifact bindings pending')
require(os.environ['GH_REPO'] == REPOSITORY and os.environ['GITHUB_EVENT_NAME'] == 'workflow_dispatch'
    and os.environ['GITHUB_REF'] == 'refs/heads/work-aws-regional-diagnostic', 'repository/trigger differs')
require(command(['git', 'rev-parse', 'HEAD']).strip() == SOURCE
    and command(['git', 'rev-parse', 'HEAD^{tree}']).strip() == TREE
    and not command(['git', 'status', '--porcelain']).strip(), 'immutable source/tree differs')
require(api('')['default_branch'] == 'main' and api('git/ref/heads/main')['object']['sha'] == SOURCE,
    'current default main differs')
run = api(f'actions/runs/{RUN}')
require(run.get('id') == RUN and run.get('head_sha') == SOURCE and run.get('path') == WORKFLOW
    and run.get('head_branch') == 'main' and run.get('event') == 'push'
    and run.get('status') == 'completed' and run.get('conclusion') == 'success'
    and run.get('run_attempt') == 1
    and run.get('repository', {}).get('full_name') == REPOSITORY
    and run.get('head_repository', {}).get('full_name') == REPOSITORY, 'trusted main gate differs')
workflow = api(f"actions/workflows/{run['workflow_id']}")
require(workflow.get('path') == WORKFLOW and workflow.get('state') == 'active', 'gate workflow differs')
latest()
response = api(f"actions/runs/{RUN}/attempts/{run['run_attempt']}/jobs?per_page=100")
jobs = response.get('jobs', [])
require(response.get('total_count') == 14 and len(jobs) == 14 and {j['name'] for j in jobs} == JOBS
    and len({j['id'] for j in jobs}) == 14
    and all(j.get('head_sha') == SOURCE and j.get('run_id') == RUN and j.get('run_attempt') == run['run_attempt']
        and j.get('status') == 'completed' and j.get('conclusion') == 'success' for j in jobs), 'all14 jobs differ')
response = api(f'actions/runs/{RUN}/artifacts?per_page=100')
rows = [a for a in response.get('artifacts', []) if a.get('name') == 'exact-revision-merge-evidence']
require(response.get('total_count', 101) <= 100 and len(rows) == 1, 'aggregate artifact is ambiguous')
artifact = rows[0]
job = next(j for j in jobs if j['name'] == 'merge-gate')
require(artifact.get('id') == ARTIFACT and artifact.get('expired') is False
    and artifact.get('digest') == 'sha256:' + RAW_SHA256 and artifact.get('size_in_bytes') == 393
    and artifact.get('workflow_run', {}).get('id') == RUN and artifact.get('workflow_run', {}).get('head_sha') == SOURCE
    and job['started_at'] <= artifact.get('created_at', '') <= job['completed_at'], 'raw artifact binding differs')
raw = command(['gh', 'api', f'repos/{REPOSITORY}/actions/artifacts/{ARTIFACT}/zip'], binary=True)
require(len(raw) == artifact['size_in_bytes'] and hashlib.sha256(raw).hexdigest() == RAW_SHA256,
    'raw aggregate ZIP digest differs')
with zipfile.ZipFile(io.BytesIO(raw)) as archive:
    members = [m for m in archive.infolist() if not m.is_dir()]
    require(len(members) == 1 and members[0].filename == 'gates.json' and members[0].file_size <= 262144
        and (members[0].external_attr >> 16) & 0o170000 != 0o120000, 'aggregate member differs')
    evidence = json.loads(archive.read(members[0]))
require(evidence.get('revision') == SOURCE and evidence.get('run_url') == f'https://github.com/{REPOSITORY}/actions/runs/{RUN}'
    and isinstance(evidence.get('passed'), list) and len(evidence['passed']) == 13 and set(evidence['passed']) == LABELS,
    'aggregate exact revision/jobs differ')
after = api(f'actions/artifacts/{ARTIFACT}')
require(all(after.get(k) == artifact.get(k) for k in ['id','name','expired','digest','size_in_bytes','created_at','workflow_run']),
    'aggregate changed after download')
current = api(f'actions/runs/{RUN}')
require(all(current.get(k) == run.get(k) for k in ['id','head_sha','run_attempt','status','conclusion','workflow_id']),
    'gate changed after download')
latest()
require(api('git/ref/heads/main')['object']['sha'] == SOURCE and not command(['git','status','--porcelain']).strip(),
    'current main/source changed')
print(json.dumps({'admitted_revision': SOURCE, 'admitted_tree': TREE, 'gate_run_id': RUN,
    'gate_attempt': run['run_attempt'], 'successful_jobs': 14, 'raw_aggregate_sha256': RAW_SHA256,
    'admission_scope': 'READ_ONLY_EAST1_WEST2_PREFLIGHT_AND_OHIO_ACCOUNT_PLAN_ONLY'}))
