#!/usr/bin/env python3
"""Recompute the reviewed Ohio scenarios from saved official price evidence.

Refreshing prices is a separate source-review task; running this script never
changes the checked_at date to imply newer retrieval than actually performed.
"""
import json
import math
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
HERE=Path(__file__).resolve().parent
SOURCES=json.loads((HERE/'aws-price-list-evidence.json').read_text())+json.loads((HERE/'aws-additional-price-evidence.json').read_text())


def lookup(service,usage,**attributes):
    matches=[]
    for source in SOURCES:
        if source['service']!=service:continue
        for row in source.get('rates',[]):
            a=row['attributes'];p=row['price'];value=Decimal(p['pricePerUnit']['USD'])
            if a.get('usagetype')==usage and value>0 and all(a.get(k)==v for k,v in attributes.items()):
                matches.append({'usd':float(value),'unit':p['unit'],'source':source['source'],'published_at':source['published_at'],'sku':row['sku'],'rate_code':p['rateCode'],'description':p['description']})
    if not matches:raise ValueError('Missing verified rate: '+service+' '+usage)
    # All scenarios fit the first paid tier; avoid accidentally selecting higher tiers.
    return max(matches,key=lambda x:x['usd'])


RATES={
 'fargate_vcpu_hour':lookup('AmazonECS','USE2-Fargate-vCPU-Hours:perCPU'),
 'fargate_gb_hour':lookup('AmazonECS','USE2-Fargate-GB-Hours'),
 'alb_hour':lookup('AWSELB','USE2-LoadBalancerUsage',operation='LoadBalancing:Application'),
 'alb_lcu_hour':lookup('AWSELB','USE2-LCUUsage'),
 'rds_qa_hour':lookup('AmazonRDS','USE2-InstanceUsage:db.t4g.small',databaseEngine='PostgreSQL'),
 'rds_prod_hour':lookup('AmazonRDS','USE2-Multi-AZUsage:db.t4g.medium',databaseEngine='PostgreSQL'),
 'rds_qa_gb_month':lookup('AmazonRDS','USE2-RDS:GP3-Storage',databaseEngine='PostgreSQL'),
 'rds_prod_gb_month':lookup('AmazonRDS','USE2-RDS:Multi-AZ-GP3-Storage',databaseEngine='PostgreSQL'),
 'rds_backup_gb_month':lookup('AmazonRDS','USE2-RDS:ChargedBackupUsage',databaseEngine='PostgreSQL'),
 'rds_credit_vcpu_hour':lookup('AmazonRDS','USE2-CPUCredits:db.t4g',databaseEngine='PostgreSQL'),
 'ipv4_hour':lookup('AmazonVPC','USE2-PublicIPv4:InUseAddress'),
 's3_gb_month':lookup('AmazonS3','USE2-TimedStorage-ByteHrs'),
 's3_put':lookup('AmazonS3','USE2-Requests-Tier1'),
 's3_get':lookup('AmazonS3','USE2-Requests-Tier2'),
 'sqs_request':lookup('AWSQueueService','USE2-Requests-Tier1'),
 'cognito_mau':lookup('AmazonCognito','USE2-CognitoLiteMAU'),
 'secret_month':lookup('AWSSecretsManager','USE2-AWSSecretsManager-Secrets'),
 'secret_request':lookup('AWSSecretsManager','USE2-AWSSecretsManagerAPIRequest'),
 'kms_key_version_month':lookup('awskms','us-east-2-KMS-Keys'),
 'kms_request':lookup('awskms','us-east-2-KMS-Requests'),
 'log_ingest_gb':lookup('AmazonCloudWatch','USE2-DataProcessing-Bytes'),
 'log_store_gb_month':lookup('AmazonCloudWatch','USE2-TimedStorage-ByteHrs'),
 'cw_metric_month':lookup('AmazonCloudWatch','USE2-CW:MetricMonitorUsage'),
 'cw_alarm_metric_month':lookup('AmazonCloudWatch','USE2-CW:AlarmMonitorUsage'),
 'cw_request':lookup('AmazonCloudWatch','USE2-CW:Requests'),
 'ecr_gb_month':lookup('AmazonECR','USE2-TimedStorage-ByteHrs'),
 'sns_request':lookup('AmazonSNS','USE2-Requests-Tier1'),
 'sns_email':lookup('AmazonSNS-email','USE2-DeliveryAttempts-SMTP'),
 'internet_egress_gb':lookup('AWSDataTransfer','USE2-DataTransfer-Out-Bytes'),
 'regional_directional_gb':lookup('AWSDataTransfer','USE2-DataTransfer-Regional-Bytes'),
 'nat_hour':{'usd':0.045,'unit':'Hrs','source':'https://aws.amazon.com/vpc/pricing/','description':'Official US East (Ohio) NAT gateway example, retrieved 2026-10-11'},
 'nat_gb':{'usd':0.045,'unit':'GB','source':'https://aws.amazon.com/vpc/pricing/','description':'Official US East (Ohio) NAT gateway data-processing example, retrieved 2026-10-11'},
}


def money(value):return float(Decimal(str(value)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))


def scenario(environment,users):
    prod=environment=='prod';hours=730;checks=30*users;exports=2*users
    # A stress planning horizon, never an authorization to retain human records.
    database_gb=20+10*math.ceil((users*30*12*128/1024/1024)/10)
    logs_gb=1+users*.003;storage_gb=1+users*.01;nat_gb=5+users*.01;egress_gb=5+users*.05
    items=[]
    def add(name,quantity,rate):items.append({'item':name,'quantity':quantity,'rate':rate,'monthly_usd':money(Decimal(str(quantity))*Decimal(str(RATES[rate]['usd'])))})
    add('Fargate Linux/x86 vCPU',hours*(1.5 if prod else .75),'fargate_vcpu_hour')
    add('Fargate memory (metrics sidecar shares worker reservation)',hours*(3 if prod else 1.5),'fargate_gb_hour')
    add('ALB provisioned hours',hours,'alb_hour');add('ALB used LCU-hours',hours*(.1+users*.0009),'alb_lcu_hour')
    add('RDS PostgreSQL db.t4g.medium Multi-AZ' if prod else 'RDS PostgreSQL db.t4g.small Single-AZ',hours,'rds_prod_hour' if prod else 'rds_qa_hour')
    add('RDS gp3 allocated logical storage',database_gb,'rds_prod_gb_month' if prod else 'rds_qa_gb_month')
    add('Additional billable retained backup/snapshot GB-months',(20 if prod else 5)+(database_gb-20)*(1 if prod else .2),'rds_backup_gb_month')
    add('Illustrative T4g surplus CPU-credit vCPU-hours',users*.1,'rds_credit_vcpu_hour')
    add('NAT gateway hours (2 prod / 1 QA)',hours*(2 if prod else 1),'nat_hour');add('NAT processed GB',nat_gb,'nat_gb')
    add('Public IPv4 hours (2 ALB plus NAT addresses)',hours*(4 if prod else 3),'ipv4_hour')
    add('Cross-AZ charged directional GB (includes NAT/DB planning allowance)',(2 if prod else 5)+users*.02,'regional_directional_gb')
    add('Internet data transfer out GB',egress_gb,'internet_egress_gb')
    add('S3 current/noncurrent/journal/export storage GB-months',storage_gb,'s3_gb_month')
    add('S3 PUT/LIST requests',1000+checks*2+users*4,'s3_put');add('S3 GET/HEAD requests',5000+checks*2+users*20,'s3_get')
    add('SQS 64-KiB request units incl. 2 idle long-poll consumers',262800+checks*4+exports*4+users,'sqs_request')
    add('Cognito Lite MAU before shared free-tier allowance',users,'cognito_mau')
    add('Secrets Manager secrets',3,'secret_month');add('Secrets Manager API requests',1000+users,'secret_request')
    add('KMS data/journal key versions (initial year)',2,'kms_key_version_month');add('KMS symmetric requests',30000+checks*4+users*20,'kms_request')
    add('CloudWatch log GB ingested incl. DB/application',logs_gb,'log_ingest_gb');add('CloudWatch retained log GB-months',logs_gb*(1 if prod else 7/30),'log_store_gb_month')
    add('CloudWatch custom aggregate metrics',3,'cw_metric_month')
    # API error alarm evaluates two metrics; autoscaling creates additional metrics/alarms.
    add('CloudWatch standard alarm metric-months',13 if prod else 8,'cw_alarm_metric_month');add('CloudWatch PutMetricData requests',43800,'cw_request')
    add('ECR retained software image GB-months',2,'ecr_gb_month');add('SNS alarm API requests',100,'sns_request');add('SNS email notifications',100,'sns_email')
    return {'environment':environment,'monthly_active_users':users,'checks_per_month':checks,'raw_human_capture_enabled':False,'database_allocated_gb':database_gb,'items':items,'total_monthly_usd':money(sum(Decimal(str(i['monthly_usd'])) for i in items))}


def main():
    scenarios=[scenario(env,users) for env in ('qa','prod') for users in (0,100,1000)]
    output={'schema_version':'1.0.0','checked_at':'2026-10-11T00:00:00Z','region':'us-east-2','currency':'USD','pricing_basis':'On-demand gross before shared free tiers/credits, tax, negotiated discounts or savings plans','unverified_rates':[],'rates':RATES,'scenarios':scenarios,
        'exclusions':['Domain registration and an existing optional Route 53 hosted zone','Paid AWS support, LocalStack licensing, CI/macOS runners, app store accounts and taxes','Human study/laboratory/clinical validation, shipping and hardware','WAF, CloudTrail paid data-event selectors, externally selected audit archive, additional observability tools and independent security review','Excess load above stated LCU/traffic/log/storage/CPU-credit assumptions and autoscaling above baseline'],
        'notes':['730-hour planning month; services stay provisioned at zero users. A stopped ECS service does not stop ALB/NAT/RDS costs.','100/1000-user scenarios are engineering workload models, not validated capacity or permission to collect/retain human data.','RDS storage models 12 months at 30 checks/user/month and 128 KiB/check plus 20 GB baseline, rounded up to 10 GB; approved retention can require less.','Raw eye/ECG/lab uploads are unavailable in this release; enabling them requires a new estimate.','RDS Multi-AZ instance/storage rates already include the standby; they are not doubled again.','Automated backup retention is QA 7 days and production 35 days. Additional charged snapshot allowances are explicit line items.','KMS annual key rotations can add retained key-version charges; reprice as keys rotate.','CloudWatch Container Insights is disabled. Basic AWS service metrics plus three custom metrics are used.','ALB aliases in an existing Route 53 zone add no ALB alias-query charge; hosting/domain costs belong to the owner supplied domain and are excluded.','AWS Budget alerts notify; they do not stop spending. The required monthly budget remains an owner input.','Free-tier allowances are account-wide and can reduce these gross estimates; no availability is assumed.']}
    (HERE/'us-east-2-estimate.json').write_text(json.dumps(output,indent=2)+'\n')
    lines=['# AWS monthly planning estimate — US East (Ohio)','','**Prices checked 11 October 2026. No AWS resources have been deployed.** All amounts are USD per 730-hour month, before credits, shared free tiers, tax and discounts. These are workload estimates, not a quote or a tested capacity claim.','','## Monthly totals','','| Environment | Idle, no users | 100 monthly users | 1,000 monthly users |','|---|---:|---:|---:|']
    for env in ('qa','prod'):
        values=[x['total_monthly_usd'] for x in scenarios if x['environment']==env]
        lines.append('| '+env.upper()+' | '+' | '.join(f'${v:,.2f}' for v in values)+' |')
    lines+=['','The production baseline runs two API tasks and one worker task with a metrics sidecar, one multi-AZ PostgreSQL instance, an ALB and two NAT gateways. QA runs one smaller API task, one worker/sidecar, single-AZ PostgreSQL, an ALB and one NAT gateway. Both use private task networking, three versioned encrypted buckets, SQS source/dead-letter queues, a Cognito Lite pool, managed secrets and separate data/journal keys.','','## Assumptions and limits','']
    lines+=['- '+x for x in output['notes']]
    lines+=['','Each nonzero workload case assumes 30 checks per user each month, two exports per user, a 128 KiB database footprint per check, S3 storage of 1 + 0.01 × users GB, log ingestion of 1 + 0.003 × users GB, NAT processing of 5 + 0.01 × users GB, internet egress of 5 + 0.05 × users GB, and average ALB use of 0.1 + 0.0009 × users LCUs. The CPU-credit allowance is 0.1 surplus vCPU-hours per user. A load test must replace these assumptions before capacity commitments.','','## Selected verified unit prices','','| Resource | Unit | USD | Source |','|---|---|---:|---|']
    for name,rate in RATES.items():
        lines.append(f"| {name.replace('_',' ')} | {rate['unit']} | {rate['usd']:.8f} | [AWS]({rate['source']}) |")
    lines+=['','## Detailed line items','','The [machine-readable estimate](us-east-2-estimate.json) includes every quantity, selected price, SKU/rate code and line item for all six scenarios. The source evidence is saved in [primary regional prices](aws-price-list-evidence.json) and [additional regional prices](aws-additional-price-evidence.json). Recompute totals with `python infra/costs/build_estimate.py`. That command preserves the retrieval date; it does not pretend to refresh prices.','','## Costs outside these totals','']
    lines+=['- '+x+'.' for x in output['exclusions']]
    lines+=['','One 0.5-vCPU/1-GB Fargate task adds about $18.02/month at baseline rates; both additional production API tasks plus one worker at maximum steady autoscaling add about $54.06/month before traffic, CPU credits or extra logs. A 200% deployment overlap is temporary and billed while present. RDS autoscaling cannot be shrunk in place, so a storage increase can persist after demand falls. Retained snapshots, buckets, keys, secrets, images and log groups continue to cost money after QA compute is removed.','','Budget monitoring is configured at 50%, 80% and 100% actual spend and 100% forecast spend, using the supplied destination and the activated `deployment` cost-allocation tag. These totals do not choose a budget for the owner. The deployment CLI requires a positive budget, a real destination, a region-matching estimate no more than 31 days old, and available exact instance/database versions.','','Official supporting pages: [Fargate](https://aws.amazon.com/fargate/pricing/), [RDS PostgreSQL](https://aws.amazon.com/rds/postgresql/pricing/), [VPC/NAT and IPv4](https://aws.amazon.com/vpc/pricing/), [CloudWatch](https://aws.amazon.com/cloudwatch/pricing/), [Cognito](https://aws.amazon.com/cognito/pricing/), [KMS](https://aws.amazon.com/kms/pricing/), [SNS](https://aws.amazon.com/sns/pricing/), [AWS Budgets](https://aws.amazon.com/aws-cost-management/aws-budgets/pricing/).']
    (HERE/'README.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps([{'environment':x['environment'],'users':x['monthly_active_users'],'monthly_usd':x['total_monthly_usd']} for x in scenarios]))

if __name__=='__main__':main()
