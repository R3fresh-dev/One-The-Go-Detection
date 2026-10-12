#!/usr/bin/env python3
"""Repeatable development deployment; separate from admitted QA/production releases."""
from __future__ import annotations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:] = [entry for entry in sys.path if Path(entry).resolve() != ROOT / 'deploy']
sys.path.insert(0, str(ROOT))

import argparse
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
import math
import re
import subprocess
import tarfile
import tempfile
import time
import uuid

from botocore.exceptions import ClientError
import httpx
from deploy import platform, web_artifact
from deploy.check_access import identity_selection
from deploy.health import BoundedSession, METRICS, pages
from deploy.orchestrate import StageJournal
from deploy.provenance import Gate, bounded_json

STACK = 'otgd-development'
CONFIG_FIELDS = {'environment', 'account', 'region', 'alarmEmail', 'monthlyBudgetUsd',
                 'releaseId', 'plannedMonthlyUsers', 'costEstimatePath'}


def read_config(path):
    c = bounded_json(path)
    if set(c) != CONFIG_FIELDS or c['environment'] != 'development':
        raise Gate('Use the explicit development configuration fields')
    if not re.fullmatch(r'\d{12}', c['account']) or c['region'] != 'us-east-2':
        raise Gate('Development pricing and topology are qualified only for Ohio; supply the actual account')
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', c['alarmEmail']):
        raise Gate('Supply the actual alarm destination')
    if not re.fullmatch(r'[0-9a-f]{40}', c['releaseId']):
        raise Gate('Supply the full reviewed source commit')
    if type(c['monthlyBudgetUsd']) not in (int, float) or not 0 < c['monthlyBudgetUsd'] <= 50:
        raise Gate('This development plan requires a positive budget no greater than $50')
    if type(c['plannedMonthlyUsers']) is not int or c['plannedMonthlyUsers'] not in (0, 10):
        raise Gate('The development plan supports a 0 or 10 user cost assumption, not a capacity claim')
    return c


def budget_plan(c):
    estimate_path = Path(c['costEstimatePath'])
    if not estimate_path.is_absolute():
        estimate_path = ROOT / estimate_path
    estimate = bounded_json(estimate_path, limit=262_144)
    if (estimate.get('region') != c['region'] or estimate.get('unverified_rates') != []
            or estimate.get('deployment_profile') != 'development-single-node'
            or not isinstance(estimate.get('rates'), dict) or not estimate['rates']):
        raise Gate('Supply complete verified development pricing for the selected region')
    checked = datetime.fromisoformat(estimate['checked_at'].replace('Z', '+00:00'))
    if checked.tzinfo is None:
        checked = checked.replace(tzinfo=timezone.utc)
    age = (datetime.now(timezone.utc) - checked).total_seconds()
    if not -86400 <= age <= 31 * 86400:
        raise Gate('Refresh development prices; estimate must be no more than 31 days old')
    rows = [row for row in estimate['scenarios']
            if row['monthly_active_users'] == c['plannedMonthlyUsers']]
    if len(rows) != 1:
        raise Gate('The estimate must identify one actual development workload')
    row = rows[0]
    def number(value):
        return type(value) in (int, float) and math.isfinite(value) and value >= 0
    if not number(row.get('total_monthly_usd')) or not row.get('items'):
        raise Gate('Development pricing must contain finite reconciled line items')
    total = Decimal('0')
    for item in row['items']:
        rate = estimate['rates'].get(item.get('rate'), {})
        if (not number(item.get('quantity')) or not number(item.get('monthly_usd')) or not number(rate.get('usd'))
                or not all(isinstance(rate.get(key), str) and rate[key] for key in ('unit', 'source', 'sku', 'rate_code'))
                or not rate['source'].startswith('https://pricing.us-east-1.amazonaws.com/')):
            raise Gate('Every development line item requires verified official rate evidence')
        amount = (Decimal(str(item['quantity'])) * Decimal(str(rate['usd']))).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        if amount != Decimal(str(item['monthly_usd'])):
            raise Gate('Development quantities and rate calculations do not reconcile')
        total += amount
    if total != Decimal(str(row['total_monthly_usd'])):
        raise Gate('Development monthly total does not reconcile')
    if row['total_monthly_usd'] > c['monthlyBudgetUsd']:
        raise Gate('The estimated workload exceeds the owner budget; deployment is blocked')
    return {'estimated_monthly_usd': rows[0]['total_monthly_usd'],
            'budget_usd': c['monthlyBudgetUsd'], 'planned_monthly_users': c['plannedMonthlyUsers'],
            'estimate_sha256': hashlib.sha256(estimate_path.read_bytes()).hexdigest(),
            'budget_is_a_spending_cap': False}


def outputs(aws, c):
    stack = aws.client('cloudformation').describe_stacks(StackName=STACK)['Stacks'][0]
    if stack['StackStatus'] not in ('CREATE_COMPLETE', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE'):
        raise Gate('Development stack is not stable')
    out = {row['OutputKey']: row['OutputValue'] for row in stack.get('Outputs', [])}
    if out.get('ReleaseId') != c['releaseId']:
        raise Gate('Development stack source differs from the selected release')
    return out


def preserve_images(aws, template, prior):
    """Freeze actual AMIs so normal source updates cannot replace the database host."""
    ec2 = aws.client('ec2')
    for logical, output, architecture, parameter in (
        ('AppInstance', 'InstanceId', 'x86_64', '/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64'),
        ('NatInstance', 'NatInstanceId', 'arm64', '/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-arm64')):
        if prior:
            if output not in prior:
                raise Gate('Existing development instance identity is unavailable; recovery requires review')
            rows = [r for reservation in ec2.describe_instances(InstanceIds=[prior[output]])['Reservations']
                    for r in reservation['Instances']]
            if len(rows) != 1 or rows[0]['InstanceId'] != prior[output] or rows[0]['State']['Name'] != 'running':
                raise Gate('Existing development host must be running; do not replace its retained database')
            image = rows[0]['ImageId']
        else:
            image = aws.client('ssm').get_parameter(Name=parameter)['Parameter']['Value']
        images = ec2.describe_images(ImageIds=[image])['Images']
        if (len(images) != 1 or images[0]['ImageId'] != image or images[0]['Architecture'] != architecture
                or images[0]['State'] != 'available' or images[0]['RootDeviceType'] != 'ebs'):
            raise Gate('Selected development AMI is not an available matching EBS-backed image')
        template['Resources'][logical]['Properties']['ImageId'] = image
    return template


def admit_changes(changes):
    protected_types = {'AWS::EC2::Instance', 'AWS::CloudFront::VpcOrigin', 'AWS::S3::Bucket',
                       'AWS::KMS::Key', 'AWS::SecretsManager::Secret', 'AWS::Cognito::UserPool'}
    for change in changes:
        resource = change.get('ResourceChange', {})
        if resource.get('ResourceType') in protected_types and (
            resource.get('Action') == 'Remove' or resource.get('Replacement') in ('True', 'Conditional')):
            raise Gate('Development update would replace or remove retained infrastructure; use reviewed recovery')


def stack_deploy(aws, c, template):
    cf = aws.client('cloudformation')
    # This profile retains the existing qa runtime namespace/registry names.
    try:
        cf.describe_stacks(StackName='otgd-qa-platform')
    except ClientError as error:
        if error.response.get('Error', {}).get('Code') != 'ValidationError' or 'does not exist' not in error.response.get('Error', {}).get('Message', ''):
            raise
    else:
        raise Gate('A managed QA stack already uses this account/region; development cannot share its runtime namespace')
    prior = None
    creating = False
    try:
        current = cf.describe_stacks(StackName=STACK)['Stacks'][0]
    except ClientError as error:
        if error.response.get('Error', {}).get('Code') != 'ValidationError' or 'does not exist' not in error.response.get('Error', {}).get('Message', ''):
            raise
        creating = True
    else:
        status = current['StackStatus']
        if status in ('CREATE_IN_PROGRESS', 'UPDATE_IN_PROGRESS', 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS'):
            waiter = 'stack_create_complete' if status == 'CREATE_IN_PROGRESS' else 'stack_update_complete'
            cf.get_waiter(waiter).wait(StackName=STACK, WaiterConfig={'Delay': 15, 'MaxAttempts': 240})
            current = cf.describe_stacks(StackName=STACK)['Stacks'][0]
        if current['StackStatus'] not in ('CREATE_COMPLETE', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE'):
            raise Gate('Existing development stack needs recovery before another deployment')
        prior = {row['OutputKey']: row['OutputValue'] for row in current.get('Outputs', [])}
    template = preserve_images(aws, template, prior)
    body = json.dumps(template, separators=(',', ':'))
    if len(body.encode()) > 51_200:
        raise Gate('Development template exceeds the direct CloudFormation request limit')
    request = {'StackName': STACK, 'TemplateBody': body, 'ChangeSetName': 'development-' + uuid.uuid4().hex,
               'ChangeSetType': 'CREATE' if creating else 'UPDATE',
               'Capabilities': ['CAPABILITY_NAMED_IAM'],
               'Tags': [{'Key': 'deployment', 'Value': STACK},
                        {'Key': 'purpose', 'Value': 'development'}]}
    change_set = cf.create_change_set(**request)['Id']
    try:
        cf.get_waiter('change_set_create_complete').wait(ChangeSetName=change_set, StackName=STACK,
            WaiterConfig={'Delay': 3, 'MaxAttempts': 200})
    except Exception:
        observed = cf.describe_change_set(ChangeSetName=change_set, StackName=STACK)
        if observed.get('Status') == 'FAILED' and "didn't contain changes" in observed.get('StatusReason', ''):
            cf.delete_change_set(ChangeSetName=change_set, StackName=STACK)
            return outputs(aws, c)
        raise
    changes = [change for page in pages(cf, 'describe_change_set', ChangeSetName=change_set, StackName=STACK)
               for change in page.get('Changes', [])]
    try:
        admit_changes(changes)
    except Gate:
        cf.delete_change_set(ChangeSetName=change_set, StackName=STACK)
        raise
    cf.update_termination_protection(EnableTerminationProtection=True, StackName=STACK)
    cf.execute_change_set(ChangeSetName=change_set, StackName=STACK)
    cf.get_waiter('stack_create_complete' if creating else 'stack_update_complete').wait(
        StackName=STACK, WaiterConfig={'Delay': 15, 'MaxAttempts': 240})
    return outputs(aws, c)


def connect_origin(aws, out):
    """Only the CloudFront VPC-origin service group may reach the private API."""
    ec2 = aws.client('ec2')
    groups = ec2.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values': [out['VpcId']]},
        {'Name': 'group-name', 'Values': ['CloudFront-VPCOrigins-Service-SG']}])['SecurityGroups']
    if len(groups) != 1:
        raise Gate('CloudFront did not establish its unique VPC-origin security group')
    permission = {'IpProtocol': 'tcp', 'FromPort': 8000, 'ToPort': 8000,
                  'UserIdGroupPairs': [{'GroupId': groups[0]['GroupId'], 'Description': 'Private CloudFront origin only'}]}
    try:
        ec2.authorize_security_group_ingress(GroupId=out['ApplicationSecurityGroupId'], IpPermissions=[permission])
    except ClientError as error:
        if error.response.get('Error', {}).get('Code') != 'InvalidPermission.Duplicate':
            raise
    return {'origin_access': 'private_cloudfront_service_group'}


def run_host(aws, out, command):
    ssm = aws.client('ssm')
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        rows = ssm.describe_instance_information(Filters=[{'Key': 'InstanceIds', 'Values': [out['InstanceId']]}])['InstanceInformationList']
        if len(rows) == 1 and rows[0].get('PingStatus') == 'Online':
            break
        time.sleep(10)
    else:
        raise Gate('Private development host did not become SSM-ready')
    sent = ssm.send_command(InstanceIds=[out['InstanceId']], DocumentName='AWS-RunShellScript',
        Parameters={'commands': [command], 'executionTimeout': ['3600']}, TimeoutSeconds=60,
        CloudWatchOutputConfig={'CloudWatchLogGroupName': out['LogGroup'], 'CloudWatchOutputEnabled': True})
    command_id = sent['Command']['CommandId']
    deadline = time.monotonic() + 3700
    while time.monotonic() < deadline:
        try:
            row = ssm.get_command_invocation(CommandId=command_id, InstanceId=out['InstanceId'])
        except ClientError as error:
            if error.response.get('Error', {}).get('Code') != 'InvocationDoesNotExist':
                raise
        else:
            status = row['Status']
            if status == 'Success' and row['ResponseCode'] == 0:
                return {'command_id': command_id, 'instance_id': out['InstanceId'], 'status': 'passed'}
            if status not in ('Pending', 'InProgress', 'Delayed'):
                raise Gate('Private host operation failed; inspect protected SSM logs for command ' + command_id)
        time.sleep(10)
    ssm.cancel_command(CommandId=command_id, InstanceIds=[out['InstanceId']])
    raise Gate('Private host operation exceeded its deadline; inspect its stage state before retrying')


def build_web(source, out, archive):
    with tempfile.TemporaryDirectory(prefix='otgd-dev-web-') as temporary:
        root = Path(temporary)
        with tarfile.open(source) as packed:
            packed.extractall(root, filter='data')
        mobile = root / 'apps/mobile'
        runtime = {'environment': 'qa', 'api_url': out['ApiOrigin'],
                   'issuer': out['Issuer'], 'client_id': out['ClientId']}
        env = web_artifact.build_environment(runtime)
        subprocess.run(['npm', 'ci'], cwd=mobile, env=env, check=True)
        subprocess.run(['npm', 'run', 'export:web', '--', '--clear'], cwd=mobile, env=env, check=True)
        manifest = web_artifact.package(mobile / 'dist', archive)
    return manifest


def publish_web(aws, c, out, manifest, files):
    """Publish development bytes without asserting production image provenance."""
    prefix = 'releases/' + c['releaseId']
    if out.get('ReleaseId') != c['releaseId'] or out.get('WebReleasePrefix') != prefix:
        raise Gate('Development web target differs from its reviewed source')
    cf = aws.client('cloudfront')
    distribution = cf.get_distribution(Id=out['WebDistributionId'])['Distribution']
    config = distribution['DistributionConfig']
    behavior = config['DefaultCacheBehavior']
    origin_matches = any(origin.get('Id') == behavior.get('TargetOriginId') == 'web'
        and origin.get('OriginAccessControlId') and origin.get('OriginPath') == '/' + prefix
        and origin['DomainName'].startswith(out['WebBucket'] + '.s3.')
        for origin in config['Origins']['Items'])
    if (distribution['Status'] != 'Deployed' or distribution['DomainName'] != out['WebDistributionDomain']
            or behavior.get('ViewerProtocolPolicy') != 'redirect-to-https' or not origin_matches):
        raise Gate('Development CloudFront private web origin is unverified')
    s3 = aws.client('s3')
    for name in sorted(files, key=lambda name: (name == 'index.html', name)):
        record = web_artifact.file_record(name, files[name])
        web_artifact.put_immutable(s3, out['WebBucket'], prefix + '/' + name, files[name], record['content_type'])
    digest = platform.sha256(manifest)
    invalidation = cf.create_invalidation(DistributionId=out['WebDistributionId'],
        InvalidationBatch={'Paths': {'Quantity': 1, 'Items': ['/*']},
                           'CallerReference': 'otgd-development-' + digest})['Invalidation']['Id']
    cf.get_waiter('invalidation_completed').wait(DistributionId=out['WebDistributionId'], Id=invalidation,
                                               WaiterConfig={'Delay': 20, 'MaxAttempts': 45})
    return {'distribution_id': out['WebDistributionId'], 'invalidation_id': invalidation,
            'manifest_sha256': digest, 'production_promotion_eligible': False}


def observe(aws, c, out):
    instance = aws.client('ec2').describe_instance_status(InstanceIds=[out['InstanceId']], IncludeAllInstances=True)['InstanceStatuses']
    if len(instance) != 1:
        raise Gate('AWS did not report the actual development instance')
    host_ok = all(instance[0].get(key, {}).get('Status') == 'ok' for key in ('InstanceStatus', 'SystemStatus'))
    cw = aws.client('cloudwatch')
    dashboard = cw.get_dashboard(DashboardName=out['CloudWatchDashboardName'])
    if not json.loads(dashboard['DashboardBody']).get('widgets'):
        raise Gate('Development dashboard has no health widgets')
    resources = [r for page in pages(aws.client('cloudformation'), 'list_stack_resources', StackName=STACK)
                 for r in page.get('StackResourceSummaries', []) if r['ResourceType'] == 'AWS::CloudWatch::Alarm']
    alarm_names = [r['PhysicalResourceId'] for r in resources]
    if not alarm_names or len(alarm_names) > 100:
        raise Gate('Development stack lacks a bounded health-alarm inventory')
    alarms = cw.describe_alarms(AlarmNames=alarm_names)['MetricAlarms']
    if len(alarms) != len(alarm_names) or {r['AlarmName'] for r in alarms} != set(alarm_names):
        raise Gate('AWS did not report every development alarm')
    states = {r['AlarmName']: r['StateValue'] for r in alarms}
    instant = datetime.now(timezone.utc)
    from datetime import timedelta
    metrics = {}
    for name in METRICS:
        rows = cw.get_metric_statistics(Namespace='OTGD/qa', MetricName=name,
            StartTime=instant - timedelta(minutes=5), EndTime=instant,
            Period=60, Statistics=['Maximum'])['Datapoints']
        fresh = [r for r in rows if 0 <= (instant - r['Timestamp']).total_seconds() <= 180]
        metrics[name] = 'fresh' if fresh else 'missing'
    host_metrics = {}
    for name in ('MemoryUsedPercent', 'DiskUsedPercent'):
        rows = cw.get_metric_statistics(Namespace='OTGD/development', MetricName=name,
            Dimensions=[{'Name': 'InstanceId', 'Value': out['InstanceId']}],
            StartTime=instant - timedelta(minutes=15), EndTime=instant,
            Period=300, Statistics=['Maximum'])['Datapoints']
        fresh = [r for r in rows if 0 <= (instant - r['Timestamp']).total_seconds() <= 600]
        host_metrics[name] = 'fresh' if fresh else 'missing'
    with httpx.Client(timeout=15, follow_redirects=False) as client:
        api_ready = client.get(out['ApiOrigin'] + '/health/ready').status_code == 200
        web_ready = client.get(out['WebOrigin'] + '/').status_code == 200
    healthy = (host_ok and api_ready and web_ready and all(v == 'OK' for v in states.values())
               and all(v == 'fresh' for v in metrics.values()) and all(v == 'fresh' for v in host_metrics.values()))
    return {'status': 'healthy' if healthy else 'degraded', 'observed_at': instant.isoformat(),
            'account': c['account'], 'region': c['region'], 'release_id': c['releaseId'],
            'host_checks': 'passed' if host_ok else 'failed', 'api_ready': api_ready,
            'web_ready': web_ready, 'alarm_states': states, 'operational_metrics': metrics,
            'host_metrics': host_metrics,
            'dashboard_url': out['CloudWatchDashboardUrl'], 'qa_acceptance': 'not_executed'}


def deploy(args, c, aws, plan):
    if not args.gate_evidence:
        raise Gate('Development deployment requires passing exact-source GitHub gate evidence')
    platform.require_clean_source(c['releaseId'])
    platform.verify_gate_file(args.gate_evidence, c['releaseId'])
    from deploy.development_template import build_template
    from deploy.development_runtime import package_runtime, startup_script
    work = ROOT / '.local/deploy/development' / c['releaseId'] / uuid.uuid4().hex
    work.mkdir(parents=True, mode=0o700)
    with StageJournal(work, c) as journal:
        out = journal.call('development-infrastructure', stack_deploy, aws, c, build_template(c))
        journal.call('private-origin-ingress', connect_origin, aws, out)
        source = work / 'source.tar'
        journal.call('exact-source-archive', platform.run, ['git', 'archive', '--format=tar', '--output', str(source), c['releaseId']])
        package = work / 'runtime.tar.gz'
        journal.call('runtime-package', package_runtime, package, c, out, source, establish_new=args.establish_new)
        digest = hashlib.sha256(package.read_bytes()).hexdigest()
        key = 'runtime/' + c['releaseId'] + '/' + digest + '.tar.gz'
        journal.call('immutable-runtime-upload', web_artifact.put_immutable, aws.client('s3'), out['DeploymentBucket'], key, package.read_bytes(), 'application/gzip')
        # Recheck the live CI attempt after infrastructure work and before activation.
        journal.call('source-readmission', platform.require_clean_source, c['releaseId'])
        journal.call('gate-readmission', platform.verify_gate_file, args.gate_evidence, c['releaseId'])
        command = startup_script(c['region'], c['account'], out['DeploymentBucket'], key, digest)
        host = journal.call('private-runtime-activation', run_host, aws, out, command)
        archive = work / 'web.zip'
        manifest = journal.call('exact-source-web', build_web, source, out, archive)
        files = web_artifact.contents(archive, manifest)
        publication = journal.call('publish-web', publish_web, aws, c, out, manifest, files)
        public = journal.call('verify-public-access', web_artifact.verify_access, out, {}, files)
        # CloudWatch starts empty. Bounded polling waits for actual fresh data.
        deadline = time.monotonic() + 600
        snapshot = None
        while time.monotonic() < deadline:
            snapshot = journal.call('observe-development-health', observe, aws, c, out)
            if snapshot['status'] == 'healthy':
                break
            time.sleep(30)
        if not snapshot or snapshot['status'] != 'healthy':
            raise Gate('Development health did not stabilize; inspect actual dashboard and stage state')
        receipt = {'schema_version': '1.0.0', 'operation': 'development-deploy',
            'status': 'development_transport_and_health_verified', 'environment': 'development',
            'account': c['account'], 'region': c['region'], 'release_id': c['releaseId'],
            'api_origin': out['ApiOrigin'], 'web_origin': out['WebOrigin'],
            'cloudwatch_dashboard_url': out['CloudWatchDashboardUrl'], 'runtime_sha256': digest,
            'web_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
            'host_operation': host, 'publication': publication, 'public_checks': public,
            'health': snapshot, 'budget_plan': plan, 'production_promotion_eligible': False,
            'qa_acceptance': 'not_executed', 'alarm_delivery': 'not_executed'}
        journal.call('write-development-receipt', platform.write_receipt, work / 'deployment.json', receipt)
        journal.finish()
        return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['plan', 'deploy', 'health'])
    parser.add_argument('--config', required=True, type=Path)
    selectors = parser.add_mutually_exclusive_group()
    selectors.add_argument('--profile')
    selectors.add_argument('--identity')
    parser.add_argument('--gate-evidence', type=Path)
    parser.add_argument('--establish-new', action='store_true', help='Only the first empty development journal')
    args = parser.parse_args(argv)
    try:
        c = read_config(args.config)
        plan = budget_plan(c)
        if args.operation == 'plan':
            result = {'environment': 'development', 'deployment_executed': False,
                'account': c['account'], 'region': c['region'], 'budget_plan': plan,
                'ingress': 'AWS-generated CloudFront HTTPS with a private EC2 VPC origin',
                'database': 'Self-managed PostgreSQL on one application host',
                'availability': 'One application host and one small NAT instance in one availability zone',
                'missing_requirements': ['AWS identity', 'clean reviewed source and passing exact-commit CI',
                    'actual cloud health, backup restore and alarm-delivery verification']}
        else:
            with identity_selection(args.identity) as selected:
                aws = BoundedSession(platform.CloudSession(c['region'], selected or args.profile))
                if aws.client('sts').get_caller_identity()['Account'] != c['account']:
                    raise Gate('AWS credentials do not match the development account')
                result = deploy(args, c, aws, plan) if args.operation == 'deploy' else observe(aws, c, outputs(aws, c))
        print(json.dumps(result, indent=2))
        return 0 if result.get('status') != 'degraded' else 2
    except Exception as error:
        message = str(error) if isinstance(error, Gate) else type(error).__name__ + '; inspect protected stage evidence'
        print(json.dumps({'status': 'blocked', 'reason': message, 'deployment_completed': False,
                          'mutations_may_have_executed': args.operation == 'deploy'}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
