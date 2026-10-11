"""Maintenance admission unit tests; fixture ECS is not live release evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('maintenance_deployment',ROOT/'deploy/platform.py')
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)


def fixture(operation='migrate'):
    cfg={'environment':'qa','account':'123456789012','region':'us-east-2','releaseId':'c'*40,'imageDigest':'sha256:'+'b'*64,'recoveryRequired':operation=='restore'}
    out={'Cluster':'arn:aws:ecs:us-east-2:123456789012:cluster/otgd-qa','MigrationTaskDefinition':'arn:aws:ecs:us-east-2:123456789012:task-definition/otgd-qa-maintenance:4'}
    receipt={'operation':operation,'status':'passed','environment':cfg['environment'],'account':cfg['account'],'region':cfg['region'],'release_id':cfg['releaseId'],'image_digest':cfg['imageDigest'],'task_arn':'arn:aws:ecs:us-east-2:123456789012:task/otgd-qa/test'}
    command=['uv','run','--no-sync','python','-m','otgd.migrate'];environment=[]
    if operation=='restore':
        receipt['backup_created_at']='2026-10-10T12:00:00Z'
        command=['uv','run','--no-sync','python','/app/scripts/restore-journal.py','--backup-created-at',receipt['backup_created_at'],'--confirm-quiesced']
        environment=[{'name':'OTGD_RECOVERY_REQUIRED','value':'true'}]
    task={'taskArn':receipt['task_arn'],'clusterArn':out['Cluster'],'taskDefinitionArn':out['MigrationTaskDefinition'],'startedBy':'otgd-reviewed-maintenance','lastStatus':'STOPPED',
          'containers':[{'name':'migration','exitCode':0}],'overrides':{'containerOverrides':[{'name':'migration','command':command,'environment':environment}]}}
    definition={'taskDefinitionArn':out['MigrationTaskDefinition'],'containerDefinitions':[{'name':'migration','image':f"{cfg['account']}.dkr.ecr.{cfg['region']}.amazonaws.com/otgd-qa@{cfg['imageDigest']}"}]}
    ecs=Mock();ecs.describe_tasks.return_value={'tasks':[task]};ecs.describe_task_definition.return_value={'taskDefinition':definition}
    aws=Mock();aws.client.return_value=ecs
    return cfg,out,receipt,task,definition,ecs,aws


class MaintenanceTest(unittest.TestCase):
    def verify(self,cfg,out,receipt,aws,operation):
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary)/'receipt.json';path.write_text(json.dumps(receipt))
            d.verify_maintenance(aws,out,path,cfg,operation)

    def test_exact_task_definition_container_command_and_receipt_required(self):
        cfg,out,receipt,task,definition,ecs,aws=fixture()
        self.verify(cfg,out,receipt,aws,'migrate')
        for field,value in [('account','987654321098'),('region','us-west-2'),('release_id','a'*40),('image_digest','sha256:'+'a'*64)]:
            with self.subTest(field=field),self.assertRaises(d.Gate):self.verify(cfg,out,{**receipt,field:value},aws,'migrate')
        changes=[{'taskDefinitionArn':out['MigrationTaskDefinition']+'other'}, {'clusterArn':'other-cluster'}, {'startedBy':'manual'},
                 {'taskArn':receipt['task_arn']+'other'}, {'containers':[{'name':'other','exitCode':0}]}, {'containers':[{'name':'migration','exitCode':1}]},
                 {'containers':[{'name':'migration','exitCode':0},{'name':'sidecar','exitCode':0}]},
                 {'overrides':{'containerOverrides':[{'name':'migration','command':['python','-c','pass','otgd.migrate']}]}},
                 {'overrides':{'taskRoleArn':'other-role','containerOverrides':task['overrides']['containerOverrides']}},
                 {'overrides':{'containerOverrides':[{'name':'migration','command':task['overrides']['containerOverrides'][0]['command'],'environment':[{'name':'OTGD_DATABASE_URL','value':'wrong-db'}]}]}}]
        for change in changes:
            ecs.describe_tasks.return_value={'tasks':[{**task,**change}]}
            with self.subTest(change=change),self.assertRaises(d.Gate):self.verify(cfg,out,receipt,aws,'migrate')
        ecs.describe_tasks.return_value={'tasks':[task]}
        ecs.describe_task_definition.return_value={'taskDefinition':{**definition,'taskDefinitionArn':'foreign-definition'}}
        with self.assertRaises(d.Gate):self.verify(cfg,out,receipt,aws,'migrate')

    def test_restore_requires_full_argv_and_recovery_environment(self):
        cfg,out,receipt,task,definition,ecs,aws=fixture('restore')
        self.verify(cfg,out,receipt,aws,'restore')
        for argv in (['python','-c','pass','/app/scripts/restore-journal.py'], task['overrides']['containerOverrides'][0]['command'][:-1]):
            changed=copy.deepcopy(task);changed['overrides']['containerOverrides'][0]['command']=argv
            ecs.describe_tasks.return_value={'tasks':[changed]}
            with self.assertRaises(d.Gate):self.verify(cfg,out,receipt,aws,'restore')
        changed=copy.deepcopy(task);changed['overrides']['containerOverrides'][0]['environment']=[]
        ecs.describe_tasks.return_value={'tasks':[changed]}
        with self.assertRaises(d.Gate):self.verify(cfg,out,receipt,aws,'restore')
        ecs.describe_tasks.return_value={'tasks':[task]}
        with self.assertRaises(d.Gate):self.verify({**cfg,'recoveryRequired':False},out,receipt,aws,'restore')
        for point in (None,'2026-10-10T12:00:00','2099-10-10T12:00:00Z'):
            with self.assertRaises(d.Gate):self.verify(cfg,out,{**receipt,'backup_created_at':point},aws,'restore')


if __name__=='__main__':unittest.main()
