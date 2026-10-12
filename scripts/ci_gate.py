"""Canonical application merge checks. Mandatory skipped/xfail tests fail closed."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
REPORTS=ROOT/'reports'
SERVERLESS_DEPLOYMENT_SOURCES=(
    'deploy/serverless.py',
    'deploy/serverless_gates.py',
    'deploy/serverless_recovery.py',
    'deploy/serverless_template.py',
)


def require_junit(path):
    try:root=ET.parse(path).getroot()
    except (OSError,ET.ParseError):raise RuntimeError('Missing or invalid current test report') from None
    cases=root.findall('.//testcase')
    if not cases or any(case.find(tag)is not None for case in cases for tag in ('skipped','failure','error')):raise RuntimeError('Every mandatory test must execute and pass; skipped/xfail checks are failures')
    return len(cases)


def require_coverage(path):
    value=json.loads(Path(path).read_text());totals=value['totals']
    statements=totals['num_statements'];covered=totals['covered_lines']
    if not statements or 100*covered<=80*statements:raise RuntimeError('Unit statement coverage must be strictly greater than 80%')
    return 100*covered/statements


def require_file_coverage(path,source):
    value=json.loads(Path(path).read_text())
    expected=(ROOT/source).resolve()
    matches=[entry for name,entry in value.get('files',{}).items() if (ROOT/name).resolve()==expected]
    if len(matches)!=1:raise RuntimeError('Required release-tool source is absent from current coverage')
    totals=matches[0]['summary'];statements=totals['num_statements'];covered=totals['covered_lines']
    if totals.get('excluded_lines',0) or totals.get('num_excluded',0) or not statements or 100*covered<=80*statements:
        raise RuntimeError('Each release tool must exceed 80% without excluded source')
    return 100*covered/statements


def require_serverless_coverage(path):
    """A healthy aggregate cannot hide an unmeasured deployment entry point."""
    value=json.loads(Path(path).read_text())
    files=value.get('files',{})
    expected={(ROOT/source).resolve() for source in SERVERLESS_DEPLOYMENT_SOURCES}
    measured=[(ROOT/name).resolve() for name in files]
    if len(measured)!=len(expected) or set(measured)!=expected:
        raise RuntimeError('Serverless deployment coverage must contain every canonical source exactly once')
    if any(entry.get('excluded_lines') for entry in files.values()):
        raise RuntimeError('Serverless deployment coverage cannot exclude source lines')
    return {source:require_file_coverage(path,source) for source in SERVERLESS_DEPLOYMENT_SOURCES}


def child_environment(env=None, *, local_compose=False):
    values={**os.environ,**(env or {})}
    if local_compose:
        # Compose gives the parent environment precedence over --env-file.
        # The disposable database's test key must not replace the retained
        # project's independently anchored key from infra/local/.env.
        values.pop('OTGD_TOMBSTONE_KEY',None)
    return values


def call(*args,cwd=ROOT,env=None,local_compose=False):
    subprocess.run(args,cwd=cwd,env=child_environment(env,local_compose=local_compose),check=True)


def require_unittest(result):
    if not result.testsRun or result.skipped or result.expectedFailures or result.unexpectedSuccesses or not result.wasSuccessful():
        raise RuntimeError('Every infrastructure unit test must execute and pass')


def infrastructure_unit_gate():
    # Executing this file sets sys.path[0] to scripts/. Operational tests import
    # canonical repository packages independently of test discovery order.
    sys.path.insert(0, str(ROOT))
    # Test discovery imports deployment modules, so tracing must start first.
    # Keep these data and reports separate from the API/store coverage evidence.
    from coverage import Coverage
    REPORTS.mkdir(parents=True,exist_ok=True)
    report=REPORTS/'infra-serverless-coverage.json'
    xml=REPORTS/'infra-serverless-coverage.xml'
    report.unlink(missing_ok=True);xml.unlink(missing_ok=True)
    coverage=Coverage(source=[str(ROOT/'deploy')],config_file=False,
                      data_file=str(REPORTS/'.coverage.infra-serverless'))
    coverage.erase()
    coverage.start()
    try:
        suite=unittest.defaultTestLoader.discover(str(ROOT/'infra/test'),pattern='test_*.py')
        result=unittest.TextTestRunner(verbosity=2).run(suite)
    finally:
        coverage.stop()
        coverage.save()
        sources=[str(ROOT/source) for source in SERVERLESS_DEPLOYMENT_SOURCES]
        coverage.json_report(morfs=sources,outfile=str(report))
        coverage.xml_report(morfs=sources,outfile=str(xml))
    require_unittest(result)
    require_serverless_coverage(report)
    pytest_gate('secure-sdk', 'infra/test/test_secure_reader_build.py')


def pytest_gate(name,*args,env=None):
    report=REPORTS/(name+'.xml');report.unlink(missing_ok=True)
    call('uv','run','--project','services/api','python','-m','pytest',*args,'--junitxml='+str(report),'-q',env=env)
    require_junit(report)


def browser_gate(name):
    report=REPORTS/(name+'.xml');report.unlink(missing_ok=True)
    paths=['e2e/mobile.spec.ts'] if name=='atdd' else ['e2e/components.spec.ts','e2e/raw-recordings.spec.ts']
    call('npm','run','test:e2e','--',*paths,'--reporter=line,junit',cwd=ROOT/'apps/mobile',env={'PLAYWRIGHT_JUNIT_OUTPUT_FILE':str(report)})
    require_junit(report)
    if name=='atdd':
        # A separate source export proves the deployed guest-only boundary.
        preview=REPORTS/'hosted-preview.xml';preview.unlink(missing_ok=True)
        call('npm','run','export:preview',cwd=ROOT/'apps/mobile')
        call('npm','run','test:e2e','--','--config=playwright.preview.config.ts','--reporter=line,junit',cwd=ROOT/'apps/mobile',env={'PLAYWRIGHT_JUNIT_OUTPUT_FILE':str(preview)})
        require_junit(preview)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('gate',choices=['unit-coverage','atdd','components','live-dependencies','docker-health','localstack-api','performance','verify-junit','infra-unit']);parser.add_argument('paths',nargs='*');args=parser.parse_args();REPORTS.mkdir(exist_ok=True)
    if args.gate=='unit-coverage':
        coverage=REPORTS/'unit-coverage.json';coverage.unlink(missing_ok=True)
        pytest_gate('unit','services/api/tests','infra/test/test_store_inputs.py','-m','not postgres','--cov=otgd','--cov=spec_validation','--cov=model_evaluation','--cov=store_release','--cov=store_inputs','--cov-report=json:'+str(coverage),'--cov-report=xml:'+str(REPORTS/'coverage.xml'),env={'OTGD_ENVIRONMENT':'test','OTGD_DATABASE_URL':'sqlite://'})
        require_coverage(coverage)
        for source in ('apps/mobile/modules/scripts/store_release.py','apps/mobile/modules/scripts/store_inputs.py'):
            require_file_coverage(coverage,source)
        call('uv','run','--project','services/api','python','scripts/ci_gate.py','infra-unit',env={'OTGD_ENVIRONMENT':'test','OTGD_DATABASE_URL':'sqlite://'})
        call('npm','run','test:coverage',cwd=ROOT/'apps/mobile')
    elif args.gate in ('atdd','components'):browser_gate(args.gate)
    elif args.gate=='live-dependencies':
        value=os.getenv('OTGD_DATABASE_URL','')
        if not value.startswith('postgresql+psycopg://') or os.getenv('OTGD_DISPOSABLE_DATABASE')!='true':raise RuntimeError('Explicit disposable real PostgreSQL required')
        pytest_gate('postgres','services/api/tests')
        call('uv','run','--project','services/api','python','infra/test/postgres_roles.py')
    elif args.gate=='docker-health':call(sys.executable,'scripts/check-canonical-health.py',local_compose=True)
    elif args.gate=='localstack-api':
        call(sys.executable,'scripts/local-platform.py','check',local_compose=True)
        call(sys.executable,'scripts/local-platform.py','check-app','--confirm-fictional-workspace',local_compose=True)
        call('docker','compose','--project-name','otgd-local','--env-file','infra/local/.env','-f','infra/local/compose.yml','run','--rm','--no-deps','api','uv','run','--no-sync','python','/app/infra/local/raw_version_probe.py',local_compose=True)
        call('docker','compose','--project-name','otgd-local','--env-file','infra/local/.env','-f','infra/local/compose.yml','run','--rm','--no-deps','migrate','uv','run','--no-sync','python','/app/infra/local/participant_probe.py','--confirm-fictional-workspace',local_compose=True)
    elif args.gate=='performance':
        report=REPORTS/'performance.json';report.unlink(missing_ok=True)
        result=subprocess.run(['docker','compose','--project-name','otgd-local','--env-file','infra/local/.env','-f','infra/local/compose.yml','run','--rm','--no-deps','api','uv','run','--no-sync','python','/app/infra/local/performance.py'],cwd=ROOT,env=child_environment(local_compose=True),text=True,stdout=subprocess.PIPE,check=True)
        evidence=json.loads(result.stdout)
        report.write_text(json.dumps(evidence,indent=2)+'\n')
        print(json.dumps(evidence))
    elif args.gate=='infra-unit':infrastructure_unit_gate()
    else:
        if not args.paths:raise RuntimeError('At least one current JUnit report required')
        for path in args.paths:require_junit(path)

if __name__=='__main__':main()
