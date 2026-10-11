"""Require the GitHub Actions merge gate while preserving existing main protections."""
import argparse
import json
import os
import re
import subprocess

def actors(value):
 """Convert GitHub response actor objects to update-API identifiers."""
 return {key:[item[field] if isinstance(item,dict) else item for item in value.get(key,[])] for key,field in [('users','login'),('teams','slug'),('apps','slug')]}

def protection(existing=None):
 existing=existing or {};old=existing.get('required_status_checks') or {}
 checks={item['context']:item.get('app_id',-1) for item in old.get('checks',[])}
 for context in old.get('contexts',[]):checks.setdefault(context,-1)
 checks['merge-gate']=15368
 reviews=existing.get('required_pull_request_reviews') or {}
 review={key:reviews[key] for key in ['require_code_owner_reviews','require_last_push_approval'] if key in reviews}
 for key in ['dismissal_restrictions','bypass_pull_request_allowances']:
  if key in reviews:review[key]=actors(reviews[key] or {})
 review.update(required_approving_review_count=reviews.get('required_approving_review_count',0),dismiss_stale_reviews=True)
 restrictions=existing.get('restrictions')
 if restrictions:restrictions=actors(restrictions)
 result={'required_status_checks':{'strict':True,'checks':[{'context':key,'app_id':app} for key,app in sorted(checks.items())]},'enforce_admins':True,'required_pull_request_reviews':review,'restrictions':restrictions,'allow_force_pushes':False,'allow_deletions':False}
 for key in ['required_linear_history','required_conversation_resolution','lock_branch','allow_fork_syncing']:
  if key in existing:result[key]=bool(existing[key].get('enabled'))
 return result

def github(repository,method,payload=None):
 environment=dict(os.environ)
 if environment.get('GH_ADMIN_TOKEN'):environment['GH_TOKEN']=environment['GH_ADMIN_TOKEN']
 arguments=['gh','api','--method',method,f'repos/{repository}/branches/main/protection']
 if payload is not None:arguments+=['--input','-']
 response=subprocess.run(arguments,input=json.dumps(payload) if payload is not None else None,text=True,capture_output=True,env=environment)
 if response.returncode:
  if method=='GET' and 'HTTP 404' in response.stderr:return None
  raise RuntimeError('GitHub branch-protection access failed; authorized repository Administration permission required')
 return json.loads(response.stdout)

def apply(repository):
 if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repository):raise ValueError('Invalid repository identifier')
 previous=github(repository,'GET');requested=protection(previous)
 github(repository,'PUT',requested)
 observed=github(repository,'GET');status=observed.get('required_status_checks') or {}
 contexts={item['context']:item.get('app_id') for item in status.get('checks',[])}
 if not status.get('strict') or contexts.get('merge-gate')!=15368 or not observed.get('enforce_admins',{}).get('enabled') or not observed.get('required_pull_request_reviews',{}).get('dismiss_stale_reviews'):
  raise RuntimeError('Required merge protection did not verify after update')
 observed_reviews=observed.get('required_pull_request_reviews') or {}
 for key in ['dismissal_restrictions','bypass_pull_request_allowances']:
  if key in requested['required_pull_request_reviews'] and actors(observed_reviews.get(key) or {})!=requested['required_pull_request_reviews'][key]:
   raise RuntimeError('Existing review actor restrictions did not verify after update')
 if any(contexts.get(item['context'])!=item['app_id'] for item in requested['required_status_checks']['checks']):
  raise RuntimeError('Existing required checks did not verify after update')
 if observed_reviews.get('required_approving_review_count',0)<requested['required_pull_request_reviews']['required_approving_review_count']:
  raise RuntimeError('Existing review approval count did not verify after update')
 return {'repository':repository,'branch':'main','merge_gate_required':True,'github_actions_bound':True,'strict':True,'administrators_enforced':True,'verified':True}

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--repository',default='R3fresh-dev/One-The-Go-Detection');parser.add_argument('--apply',action='store_true');arguments=parser.parse_args()
 if arguments.apply:print(json.dumps(apply(arguments.repository),indent=2))
 else:print(json.dumps({'repository':arguments.repository,'branch':'main','protection':protection(),'existing_protections_preserved_on_apply':True},indent=2))
if __name__=='__main__':main()
