"""Protection updates preserve existing policy and require actual read-back."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('merge_protection',ROOT/'scripts/configure_merge_protection.py')
policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)


class ProtectionTest(unittest.TestCase):
 def test_existing_checks_reviews_and_actor_restrictions_are_preserved(self):
  existing={'required_status_checks':{'contexts':['security'],'checks':[{'context':'security','app_id':44}]},'required_pull_request_reviews':{'required_approving_review_count':2,'require_code_owner_reviews':True,'dismissal_restrictions':{'users':[{'login':'reviewer'}],'teams':[{'slug':'owners'}],'apps':[]}},'restrictions':{'users':[{'login':'maintainer'}],'teams':[],'apps':[]},'required_linear_history':{'enabled':True}}
  value=policy.protection(existing)
  self.assertIn({'context':'security','app_id':44},value['required_status_checks']['checks'])
  self.assertIn({'context':'merge-gate','app_id':15368},value['required_status_checks']['checks'])
  self.assertEqual(value['required_pull_request_reviews']['required_approving_review_count'],2)
  self.assertEqual(value['required_pull_request_reviews']['dismissal_restrictions']['users'],['reviewer'])
  self.assertTrue(value['required_pull_request_reviews']['require_code_owner_reviews'])
  self.assertEqual(value['restrictions']['users'],['maintainer'])
  self.assertTrue(value['required_linear_history'])
  self.assertTrue(value['enforce_admins'])
  self.assertFalse(value['allow_force_pushes'])
  self.assertFalse(value['allow_deletions'])

 def test_bound_secret_never_enters_command_arguments(self):
  with patch.dict(policy.os.environ,{'GH_ADMIN_TOKEN':'fictional-test-only'}),patch.object(policy.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout='{}')) as run:
   policy.github('owner/repo','PUT',{'strict':True})
  arguments=run.call_args.args[0]
  self.assertNotIn('fictional-test-only',str(arguments))
  self.assertEqual(run.call_args.kwargs['env']['GH_TOKEN'],'fictional-test-only')

 def test_forbidden_and_failed_updates_never_mean_unprotected(self):
  for method,message,missing in [('GET','HTTP 404',True),('GET','HTTP 403',False),('PUT','HTTP 404',False)]:
   with self.subTest(method=method,message=message),patch.object(policy.subprocess,'run',return_value=SimpleNamespace(returncode=1,stderr=message)):
    if missing:self.assertIsNone(policy.github('owner/repo',method))
    else:
     with self.assertRaises(RuntimeError):policy.github('owner/repo',method)

 def test_apply_verifies_strict_actions_bound_admin_and_review_policy(self):
  observed={'required_status_checks':{'strict':True,'checks':[{'context':'merge-gate','app_id':15368}]},'enforce_admins':{'enabled':True},'required_pull_request_reviews':{'dismiss_stale_reviews':True,'required_approving_review_count':1}}
  with patch.object(policy,'github',side_effect=[None,{},observed]) as github:
   self.assertTrue(policy.apply('owner/repo')['verified'])
   self.assertEqual([call.args[1] for call in github.call_args_list],['GET','PUT','GET'])
  for changed in [{}, {**observed,'enforce_admins':{'enabled':False}},{**observed,'required_status_checks':{'strict':True,'checks':[{'context':'merge-gate','app_id':99}]}}]:
   with self.subTest(observed=changed),patch.object(policy,'github',side_effect=[None,{},changed]):
    with self.assertRaises(RuntimeError):policy.apply('owner/repo')

 def test_missing_existing_review_restriction_cannot_verify(self):
  previous={'required_pull_request_reviews':{'dismissal_restrictions':{'users':[{'login':'reviewer'}]}}}
  observed={'required_status_checks':{'strict':True,'checks':[{'context':'merge-gate','app_id':15368}]},'enforce_admins':{'enabled':True},'required_pull_request_reviews':{'dismiss_stale_reviews':True,'required_approving_review_count':1}}
  with patch.object(policy,'github',side_effect=[previous,{},observed]):
   with self.assertRaisesRegex(RuntimeError,'actor restrictions'):policy.apply('owner/repo')

 def test_invalid_repository_rejected_before_api(self):
  with patch.object(policy,'github') as github:
   with self.assertRaises(ValueError):policy.apply('bad/../../repository')
   github.assert_not_called()


if __name__=='__main__':unittest.main()
