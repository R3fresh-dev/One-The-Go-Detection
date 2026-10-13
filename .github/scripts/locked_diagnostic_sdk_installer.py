import os, subprocess, tomllib
from pathlib import Path
packages = {'boto3', 'botocore', 's3transfer', 'jmespath', 'python-dateutil', 'six', 'urllib3'}
lock = tomllib.loads(Path('services/api/uv.lock').read_text())
rows = [p for p in lock['package'] if p['name'] in packages]
if len(rows) != len(packages) or {p['name'] for p in rows} != packages:
    raise SystemExit('SDK lock inventory differs')
if any(p['version'] != '1.43.111' for p in rows if p['name'] in ('boto3', 'botocore')):
    raise SystemExit('Native diagnostic SDK model differs from qualified source')
root = Path(os.environ['RUNNER_TEMP'])
requirements = root / 'regional-diagnostic-sdk-requirements.txt'
requirements.write_text('\n'.join(p['name'] + '==' + p['version'] + ' ' + ' '.join(
    '--hash=' + w['hash'] for w in p.get('wheels', [])) for p in rows) + '\n')
if any(not p.get('wheels') for p in rows):
    raise SystemExit('SDK wheel hash is unavailable')
subprocess.run(['python3', '-m', 'pip', 'install', '--disable-pip-version-check', '--no-input',
    '--require-hashes', '--no-deps', '--only-binary=:all:', '--target', str(root / 'regional-diagnostic-sdk'),
    '-r', str(requirements)], check=True, timeout=90)
