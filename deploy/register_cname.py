#!/usr/bin/env python3
"""Register only the configured UI name against its actual admitted CloudFront distribution."""
from __future__ import annotations
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:]=[entry for entry in sys.path if Path(entry).resolve()!=ROOT/'deploy']
sys.path.insert(0,str(ROOT))
import argparse
import json
from deploy import platform
from deploy.provenance import Gate


def change(aws,c,out,zone_id,apply=False):
    name=c.get('webDomain')
    if not name:raise Gate('Configure webDomain and its us-east-1 certificate before CNAME registration')
    name=name.lower().rstrip('.')
    zone=aws.client('route53').get_hosted_zone(Id=zone_id)['HostedZone']
    root=zone['Name'].lower().rstrip('.')
    if zone.get('Config',{}).get('PrivateZone') or name==root or not name.endswith('.'+root):raise Gate('UI CNAME must be a subdomain of this public hosted zone')
    if c.get('hostedZoneName') and root!=c['hostedZoneName'].lower().rstrip('.'):raise Gate('Hosted zone differs from the deployment configuration')
    distribution=aws.client('cloudfront').get_distribution(Id=out['WebDistributionId'])['Distribution']
    config=distribution['DistributionConfig'];target=out['WebDistributionDomain'].lower().rstrip('.')
    if (distribution.get('Status')!='Deployed' or distribution.get('DomainName','').lower().rstrip('.')!=target or
        name not in [alias.lower().rstrip('.') for alias in config.get('Aliases',{}).get('Items',[])] or config.get('ViewerCertificate',{}).get('ACMCertificateArn')!=c['webCertificateArn'] or
        out['WebOrigin'].lower()!='https://'+name or not target.endswith('.cloudfront.net')):raise Gate('Actual distribution/TLS alias does not match this exact web deployment')
    certificate=aws.client('acm',region_name='us-east-1').describe_certificate(CertificateArn=c['webCertificateArn'])['Certificate']
    if certificate.get('Status')!='ISSUED' or not any(domain==name or (domain.startswith('*.') and name.split('.',1)[1:]==[domain[2:]]) for domain in certificate.get('SubjectAlternativeNames',[])):
        raise Gate('Web TLS certificate is not issued for this UI name')
    route53=aws.client('route53')
    existing=route53.list_resource_record_sets(HostedZoneId=zone_id,StartRecordName=name+'.',MaxItems='1')['ResourceRecordSets']
    if existing and existing[0]['Name'].lower().rstrip('.')==name:
        records=existing[0].get('ResourceRecords',[])
        if existing[0].get('Type')!='CNAME' or len(records)!=1 or records[0].get('Value','').lower().rstrip('.')!=target:raise Gate('Existing DNS belongs to a different target/type; no overwrite is authorized')
    record={'Name':name+'.','Type':'CNAME','TTL':300,'ResourceRecords':[{'Value':target}]}
    result={'action':'UPSERT','hosted_zone_id':zone_id,'record':record,'applied':False,'release_id':out['ReleaseId']}
    if apply:
        response=route53.change_resource_record_sets(HostedZoneId=zone_id,ChangeBatch={'Comment':'Reviewed exact-release UI CloudFront CNAME','Changes':[{'Action':'UPSERT','ResourceRecordSet':record}]})
        route53.get_waiter('resource_record_sets_changed').wait(Id=response['ChangeInfo']['Id'],WaiterConfig={'Delay':10,'MaxAttempts':60})
        result.update(applied=True,change_id=response['ChangeInfo']['Id'])
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('config','release','gate-evidence','trusted-public-key'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--qa-evidence',type=Path);p.add_argument('--hosted-zone-id');p.add_argument('--apply',action='store_true')
    args=p.parse_args(argv);c=platform.read_config(args.config);aws=platform.preflight(c)
    platform.require_release(args,c,aws);out=platform.stack_outputs(aws,c)
    if out.get('ReleaseId')!=c['releaseId'] or out.get('ImageDigest')!=c['imageDigest']:raise Gate('DNS target stack is not this admitted release')
    zone=args.hosted_zone_id or c.get('hostedZoneId')
    if not zone:raise Gate('Supply the actual hosted-zone-id for the public UI domain')
    result=change(aws,c,out,zone,args.apply);print(json.dumps(result,indent=2));return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except Gate as error:print('BLOCKED: '+str(error),file=sys.stderr);raise SystemExit(2)
    except Exception as error:print('BLOCKED: '+type(error).__name__+'; inspect protected AWS operation logs',file=sys.stderr);raise SystemExit(2)
