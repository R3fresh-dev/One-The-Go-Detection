"""Run every mandatory local gate and preserve evidence. Does not assert GitHub enforcement."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

GATES=['unit-coverage','atdd','performance','components','live-dependencies','docker-health','localstack-api']

def source_identity():
 revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 files=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=ROOT).split(b'\0')
 digest=hashlib.sha256()
 for name in sorted(set(files)):
  if not name:continue
  path=ROOT/name.decode()
  if path.is_file():digest.update(name+b'\0'+path.read_bytes())
 return revision,digest.hexdigest()

def run():
 reports=ROOT/'reports';reports.mkdir(exist_ok=True)
 revision,fingerprint=source_identity()
 evidence={'revision':revision,'working_tree_sha256':fingerprint,'passed':[],'scope':'local software checks; not cloud/store/native qualification or GitHub enforcement'}
 for gate in GATES:
  print('RUN '+gate,flush=True)
  result=subprocess.run([sys.executable,str(ROOT/'scripts/ci_gate.py'),gate],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  (reports/(gate+'.log')).write_text(result.stdout)
  print(result.stdout,flush=True)
  if result.returncode:
   evidence['failed']=gate;(reports/'local-gates.json').write_text(json.dumps(evidence,indent=2));raise SystemExit(result.returncode)
  evidence['passed'].append(gate)
 after_revision,after_fingerprint=source_identity()
 if (after_revision,after_fingerprint)!=(revision,fingerprint):
  evidence.update(failed='SOURCE_CHANGED_DURING_GATES',observed_revision=after_revision,observed_working_tree_sha256=after_fingerprint)
  (reports/'local-gates.json').write_text(json.dumps(evidence,indent=2))
  raise SystemExit('Source changed during required gates; all checks must rerun for a stable revision')
 (reports/'local-gates.json').write_text(json.dumps(evidence,indent=2))
 return evidence
if __name__=='__main__':run()
