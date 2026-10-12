#!/usr/bin/env python3
"""Recompute the Ohio Fargate development estimate from saved AWS evidence.

No network calls or AWS changes. Recomputing preserves the oldest underlying
regional review date and the actual retrieval timestamps of supplemental rates.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE_FILES = (
    'aws-price-list-evidence.json',
    'aws-additional-price-evidence.json',
    'aws-serverless-price-evidence.json',
    'aws-fargate-price-evidence.json',
)
SOURCES = [source for name in EVIDENCE_FILES for source in json.loads((HERE / name).read_text())]
CHECKED_AT = json.loads((HERE / 'us-east-2-estimate.json').read_text())['checked_at']
OWNER_BUDGET_USD = 100


def verified_rate(service: str, usage: str, **attributes) -> dict:
    matches = []
    for source in SOURCES:
        if source['service'] != service:
            continue
        for row in source.get('rates', []):
            attrs, price = row['attributes'], row['price']
            usd = Decimal(price['pricePerUnit']['USD'])
            if attrs.get('usagetype') != usage or usd <= 0:
                continue
            if not all(attrs.get(name) == value for name, value in attributes.items()):
                continue
            rate = {
                'usd': float(usd), 'unit': price['unit'], 'source': source['source'],
                'published_at': source['published_at'], 'sku': row['sku'],
                'rate_code': price['rateCode'], 'description': price['description'],
                'begin_range': price['beginRange'], 'end_range': price['endRange'],
            }
            for field in ('retrieved_at', 'offer_sha256'):
                if field in source:
                    rate[field] = source[field]
            matches.append(rate)
    if not matches:
        raise ValueError(f'Missing official verified rate: {service} {usage} {attributes}')
    # Exclude shared free tiers, then select the first paid tier's highest rate.
    # Where duplicate evidence agrees, preserve the newest actual retrieval.
    return max(matches, key=lambda row: (row['usd'], row.get('retrieved_at', '')))


RATES = {
    'fargate_vcpu_hour': verified_rate('AmazonECS', 'USE2-Fargate-vCPU-Hours:perCPU'),
    'fargate_memory_gb_hour': verified_rate('AmazonECS', 'USE2-Fargate-GB-Hours'),
    'alb_hour': verified_rate('AWSELB', 'USE2-LoadBalancerUsage', operation='LoadBalancing:Application', locationType='AWS Region'),
    'alb_lcu_hour': verified_rate('AWSELB', 'USE2-LCUUsage', operation='LoadBalancing:Application', locationType='AWS Region'),
    'aurora_acu_hour': verified_rate('AmazonRDS', 'USE2-Aurora:ServerlessV2Usage', databaseEngine='Aurora PostgreSQL'),
    'aurora_storage_gb_month': verified_rate('AmazonRDS', 'USE2-Aurora:StorageUsage', databaseEngine='Aurora PostgreSQL'),
    'aurora_io_request': verified_rate('AmazonRDS', 'USE2-Aurora:StorageIOUsage', databaseEngine='Aurora PostgreSQL'),
    'aurora_excess_backup_gb_month': verified_rate('AmazonRDS', 'USE2-Aurora:BackupUsage', databaseEngine='Aurora PostgreSQL'),
    'ddb_read_unit': verified_rate('AmazonDynamoDB', 'USE2-ReadRequestUnits'),
    'ddb_write_unit': verified_rate('AmazonDynamoDB', 'USE2-WriteRequestUnits'),
    'ddb_storage_gb_month': verified_rate('AmazonDynamoDB', 'USE2-TimedStorage-ByteHrs'),
    'ddb_pitr_gb_month': verified_rate('AmazonDynamoDB', 'USE2-TimedPITRStorage-ByteHrs'),
    'cloudfront_us_https_request': verified_rate('AmazonCloudFront', 'US-Requests-Tier2-HTTPS'),
    'cloudfront_us_egress_gb': verified_rate('AmazonCloudFront', 'US-DataTransfer-Out-Bytes'),
    'cloudfront_us_origin_transfer_gb': verified_rate('AmazonCloudFront', 'US-DataTransfer-Out-OBytes'),
    'cloudfront_function': verified_rate('AmazonCloudFront', 'Executions-CloudFrontFunctions'),
    'cloudfront_invalidation_path': verified_rate('AmazonCloudFront', 'Invalidations'),
    's3_storage_gb_month': verified_rate('AmazonS3', 'USE2-TimedStorage-ByteHrs'),
    's3_put_request': verified_rate('AmazonS3', 'USE2-Requests-Tier1'),
    's3_get_request': verified_rate('AmazonS3', 'USE2-Requests-Tier2'),
    'sqs_request': verified_rate('AWSQueueService', 'USE2-Requests-Tier1'),
    'cognito_lite_mau': verified_rate('AmazonCognito', 'USE2-CognitoLiteMAU'),
    'secret_month': verified_rate('AWSSecretsManager', 'USE2-AWSSecretsManager-Secrets'),
    'secret_request': verified_rate('AWSSecretsManager', 'USE2-AWSSecretsManagerAPIRequest'),
    'kms_initial_key_version_month': verified_rate('awskms', 'us-east-2-KMS-Keys'),
    'kms_symmetric_request': verified_rate('awskms', 'us-east-2-KMS-Requests'),
    'kms_ecc_sign_request': verified_rate('awskms', 'us-east-2-KMS-Requests-Asymmetric'),
    'log_ingest_gb': verified_rate('AmazonCloudWatch', 'USE2-DataProcessing-Bytes'),
    'log_storage_gb_month': verified_rate('AmazonCloudWatch', 'USE2-TimedStorage-ByteHrs'),
    'cw_custom_metric_month': verified_rate('AmazonCloudWatch', 'USE2-CW:MetricMonitorUsage'),
    'cw_alarm_metric_month': verified_rate('AmazonCloudWatch', 'USE2-CW:AlarmMonitorUsage'),
    'cw_dashboard_month': verified_rate('AmazonCloudWatch', 'DashboardsUsageHour-Basic'),
    'ecr_storage_gb_month': verified_rate('AmazonECR', 'USE2-TimedStorage-ByteHrs'),
    'sns_request': verified_rate('AmazonSNS', 'USE2-Requests-Tier1'),
    'sns_email_notification': verified_rate('AmazonSNS-email', 'USE2-DeliveryAttempts-SMTP'),
    'cross_az_directional_gb': verified_rate('AWSDataTransfer', 'USE2-DataTransfer-Regional-Bytes'),
}

ASSUMPTIONS = {
    'hours_per_month': 730,
    'service_vcpu': 0.25, 'service_memory_gb': 1, 'service_desired_count': 1,
    'worker_vcpu': 0.5, 'worker_memory_gb': 2,
    'worker_charged_seconds': 180, 'favorable_worker_charged_seconds': 60,
    'maintenance_vcpu': 0.5, 'maintenance_memory_gb': 1,
    'release_maintenance_invocations_per_month': 4,
    'release_maintenance_duration_seconds': 300,
    'fargate_linux_minimum_billed_seconds': 60,
    'alb_count': 1, 'alb_average_lcu_allowance': 0.1,
    'aurora_min_capacity': 0, 'aurora_max_capacity': 1,
    'seconds_until_auto_pause': 300,
    'idle_safety_sweep_interval_seconds': 3600,
    'retained_privacy_cleanup_interval_seconds': 900,
    'maintenance_resume_and_work_seconds': 45,
    'isolated_database_sessions_per_user_per_month': 30,
    'extra_database_awake_fraction': 0.15,
    'control_interval_seconds': 60, 'control_db_queries_while_idle': 0,
    'checks_per_user_per_month': 30, 'exports_per_user_per_month': 2,
    'api_requests_per_check': 3, 'api_requests_per_export': 5,
    'other_api_requests_per_user_per_month': 3,
    'deployment_api_probes_per_month': 100,
    'deployment_probe_database_windows': 'batched inside already-active maintenance/deployment sessions',
    'web_sessions_per_user_per_month': 30, 'web_requests_per_session': 20,
    'web_transferred_gb_per_session': 0.005,
    'baseline_web_requests_per_month': 1000, 'baseline_web_transfer_gb': 0.1,
    'baseline_api_transfer_gib': 0.1, 'ordinary_api_transfer_gib_per_user': 0.01,
    'export_response_bytes': 67108864,
    'aurora_storage_gb_baseline': 10, 'extra_retained_backup_gb': 10,
    'custom_metrics': 3, 'alarm_metric_months': 10, 'custom_dashboards': 1,
    'kms_initial_key_versions': 3, 'secrets': 3,
    'retained_ecr_image_gb': 3, 'retained_deployment_artifact_gb': 0.1,
    'retained_unused_web_bucket_gb': 0,
    'web_publishes_per_month': 4, 'web_invalidation_paths_per_publish': 1,
    'ddb_control_storage_gb': 0.01, 'ddb_control_read_units_per_tick': 3,
    'ddb_control_write_units_per_tick': 1,
    'ddb_lease_write_units_per_sql_invocation': 6,
    'sqs_idle_poll_allowance_per_month': 262800,
    'viewer_edge_location': 'United States', 'cloudfront_pricing_plan': 'pay-as-you-go',
    'task_network_mode': 'ipv6-only', 'public_ipv4_addresses': 0,
    'nat_gateways': 0, 'paid_interface_endpoints': 0,
    'container_insights_enabled': False,
}


def money(value) -> float:
    return float(Decimal(str(value)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))


def scenario(users: int, active_acu: float = .5, worker_charged_seconds: int = 180) -> dict:
    if type(users) is not int or users < 0 or active_acu not in (.5, 1):
        raise ValueError('A nonnegative integer workload and supported capacity scenario are required')
    if type(worker_charged_seconds) is not int or worker_charged_seconds < 60:
        raise ValueError('Linux Fargate tasks have a minimum billed duration of 60 seconds')
    a = ASSUMPTIONS
    hours = a['hours_per_month']
    checks = users * a['checks_per_user_per_month']
    exports = users * a['exports_per_user_per_month']
    control = hours * 3600 // a['control_interval_seconds']
    sql_interval = a['retained_privacy_cleanup_interval_seconds']
    sweeps = hours * 3600 // sql_interval
    isolated_sessions = users * a['isolated_database_sessions_per_user_per_month']
    wake_window = a['maintenance_resume_and_work_seconds'] + a['seconds_until_auto_pause']
    base_awake = Decimal(sweeps + isolated_sessions) * wake_window / 3600
    awake = min(Decimal(hours), base_awake * (1 + Decimal(str(a['extra_database_awake_fraction']))))
    api_requests = a['deployment_api_probes_per_month'] + checks * a['api_requests_per_check'] + exports * a['api_requests_per_export'] + users * a['other_api_requests_per_user_per_month']
    web_requests = a['baseline_web_requests_per_month'] + users * a['web_sessions_per_user_per_month'] * a['web_requests_per_session']
    api_gib = Decimal(str(a['baseline_api_transfer_gib'])) + users * Decimal(str(a['ordinary_api_transfer_gib_per_user'])) + Decimal(exports * a['export_response_bytes']) / 1024 ** 3
    web_gb = Decimal(str(a['baseline_web_transfer_gb'])) + users * a['web_sessions_per_user_per_month'] * Decimal(str(a['web_transferred_gb_per_session']))
    worker_tasks = sweeps + checks + exports
    worker_hours = Decimal(worker_tasks * worker_charged_seconds) / 3600
    maintenance_hours = Decimal(a['release_maintenance_invocations_per_month'] * a['release_maintenance_duration_seconds']) / 3600
    sql_invocations = api_requests + 2 * (checks + exports) + sweeps + a['release_maintenance_invocations_per_month']
    logs_gb = Decimal('1') + users * Decimal('.003')
    items = []

    def add(name: str, quantity, rate: str):
        if not math.isfinite(float(quantity)) or quantity < 0:
            raise ValueError('Nonfinite or negative planning quantity')
        # Calculate against the serialized quantity so a consumer can reproduce
        # every line with Decimal(str(quantity)) without hidden precision.
        serialized = int(quantity) if Decimal(str(quantity)) == int(quantity) else float(quantity)
        cost = money(Decimal(str(serialized)) * Decimal(str(RATES[rate]['usd'])))
        items.append({'item': name, 'quantity': serialized, 'rate': rate,
                      'cost_method': 'quantity_x_rate_round_half_up_to_cents',
                      'monthly_usd': cost})

    add('Fargate always-available UI/API/controller vCPU-hours', hours * a['service_desired_count'] * a['service_vcpu'], 'fargate_vcpu_hour')
    add('Fargate always-available UI/API/controller memory GB-hours', hours * a['service_desired_count'] * a['service_memory_gb'], 'fargate_memory_gb_hour')
    add('Fargate bounded work/sweep task vCPU-hours including billed image-pull time', worker_hours * Decimal(str(a['worker_vcpu'])), 'fargate_vcpu_hour')
    add('Fargate bounded work/sweep task memory GB-hours including billed image-pull time', worker_hours * a['worker_memory_gb'], 'fargate_memory_gb_hour')
    add('Fargate release maintenance/migration vCPU-hours', maintenance_hours * Decimal(str(a['maintenance_vcpu'])), 'fargate_vcpu_hour')
    add('Fargate release maintenance/migration memory GB-hours', maintenance_hours * a['maintenance_memory_gb'], 'fargate_memory_gb_hour')
    add('Internal Application Load Balancer hours', hours * a['alb_count'], 'alb_hour')
    add('Application Load Balancer LCU-hours planning allowance', hours * a['alb_count'] * a['alb_average_lcu_allowance'], 'alb_lcu_hour')
    add('Aurora serverless PostgreSQL active ACU-hours incl. 15% wake/activity allowance', awake * Decimal(str(active_acu)), 'aurora_acu_hour')
    add('Aurora consumed storage GB-months incl. minimum 10 GB', Decimal(a['aurora_storage_gb_baseline']) + users * Decimal('.01'), 'aurora_storage_gb_month')
    add('Aurora billable storage I/O requests', 100000 + checks * 1000, 'aurora_io_request')
    add('Aurora retained backup GB-months above included storage allocation', a['extra_retained_backup_gb'], 'aurora_excess_backup_gb_month')
    add('DynamoDB metadata strongly consistent <=4 KiB read units', control * a['ddb_control_read_units_per_tick'] + sql_invocations * 2, 'ddb_read_unit')
    add('DynamoDB metadata <=1 KiB control/transactional lease/epoch write units', control * a['ddb_control_write_units_per_tick'] + sql_invocations * a['ddb_lease_write_units_per_sql_invocation'], 'ddb_write_unit')
    add('DynamoDB metadata control state GB-months', a['ddb_control_storage_gb'], 'ddb_storage_gb_month')
    add('DynamoDB metadata point-in-time recovery GB-months', a['ddb_control_storage_gb'], 'ddb_pitr_gb_month')
    add('CloudFront US UI and API HTTPS viewer requests', web_requests + api_requests, 'cloudfront_us_https_request')
    add('CloudFront US UI and API viewer transfer GB', web_gb + api_gib, 'cloudfront_us_egress_gb')
    add('CloudFront US origin-bound request/body transfer GB', Decimal('.1') + users * Decimal('.005'), 'cloudfront_us_origin_transfer_gb')
    add('CloudFront UI SPA viewer-request function execution allowance', web_requests, 'cloudfront_function')
    add('CloudFront UI wildcard invalidation paths', a['web_publishes_per_month'] * a['web_invalidation_paths_per_publish'], 'cloudfront_invalidation_path')
    add('S3 data/journal/export current and noncurrent GB-months', Decimal('1') + users * Decimal('.01'), 's3_storage_gb_month')
    add('S3 registry deployment artifact current/noncurrent GB-months', a['retained_deployment_artifact_gb'], 's3_storage_gb_month')
    add('S3 retained unused web authority bucket GB-months', a['retained_unused_web_bucket_gb'], 's3_storage_gb_month')
    add('S3 data/journal/export PUT/LIST requests', 1000 + checks * 2 + users * 4, 's3_put_request')
    add('S3 data/journal/export GET/HEAD requests', 1000 + checks * 2 + users * 20, 's3_get_request')
    add('SQS 64 KiB request units including conservative idle-poll allowance', a['sqs_idle_poll_allowance_per_month'] + checks * 4 + exports * 4 + users, 'sqs_request')
    add('Cognito Lite MAU before shared free tier', users, 'cognito_lite_mau')
    add('Secrets Manager RDS master/application/tombstone secrets', a['secrets'], 'secret_month')
    add('Secrets Manager SQL task requests; idle metadata controller reads no secret', 2 * (api_requests + 2 * (checks + exports) + sweeps) + 3 * a['release_maintenance_invocations_per_month'] + 1000, 'secret_request')
    add('KMS data/journal/capture-signing initial key versions', a['kms_initial_key_versions'], 'kms_initial_key_version_month')
    add('KMS symmetric requests', 30000 + checks * 4 + users * 20, 'kms_symmetric_request')
    add('KMS ECC signing request allowance', checks, 'kms_ecc_sign_request')
    add('CloudWatch application/database/container logs GB ingested', logs_gb, 'log_ingest_gb')
    add('CloudWatch seven-day retained log GB-months', logs_gb * 7 / 30, 'log_storage_gb_month')
    add('CloudWatch custom actual-work aggregate metrics', a['custom_metrics'], 'cw_custom_metric_month')
    add('CloudWatch evaluated standard alarm metric-month allowance', a['alarm_metric_months'], 'cw_alarm_metric_month')
    add('CloudWatch custom system health dashboard', a['custom_dashboards'], 'cw_dashboard_month')
    add('ECR retained Fargate software image GB-months', a['retained_ecr_image_gb'], 'ecr_storage_gb_month')
    add('SNS alarm API requests', 100, 'sns_request')
    add('SNS email notifications', 100, 'sns_email_notification')
    add('Cross-AZ directional database traffic planning allowance GB', Decimal('2') + users * Decimal('.02'), 'cross_az_directional_gb')
    total = money(sum(Decimal(str(item['monthly_usd'])) for item in items))
    return {
        'environment': 'fargate-development', 'monthly_active_users': users,
        'checks_per_month': checks, 'exports_per_month': exports,
        'api_requests_per_month': api_requests, 'control_ticks_per_month': control,
        'maintenance_invocations_per_month': sweeps, 'worker_tasks_per_month': worker_tasks,
        'worker_charged_seconds': worker_charged_seconds,
        'worker_billed_hours': float(worker_hours),
        'retained_privacy_cleanup_present': True,
        'scheduled_sql_interval_seconds': sql_interval,
        'database_awake_hours_before_allowance': float(base_awake),
        'database_awake_hours_including_allowance': float(awake),
        'active_database_acu_pricing_basis': active_acu,
        'aurora_acu_hours': float(awake * Decimal(str(active_acu))),
        'raw_human_capture_enabled': False, 'items': items,
        'total_cost_method': 'sum_individually_rounded_line_items',
        'total_monthly_usd': total, 'owner_budget_usd': OWNER_BUDGET_USD,
        'within_owner_budget': total <= OWNER_BUDGET_USD,
        'budget_headroom_usd': money(Decimal(OWNER_BUDGET_USD) - Decimal(str(total))),
    }


def build_estimate() -> dict:
    cases = [scenario(users, .5, ASSUMPTIONS['worker_charged_seconds']) for users in (0, 10, 100)]
    stress = [scenario(users, 1, ASSUMPTIONS['worker_charged_seconds']) for users in (0, 10, 100)]
    favorable = [scenario(users, .5, ASSUMPTIONS['favorable_worker_charged_seconds']) for users in (0, 10, 100)]
    return {
        'schema_version': '1.0.0', 'deployment_profile': 'fargate-development',
        'region': 'us-east-2', 'currency': 'USD', 'checked_at': CHECKED_AT,
        'pricing_basis': 'On-demand gross before shared free tiers/credits, taxes and discounts; average 0.5 active ACU with configured maximum 1 ACU; 180 charged seconds per bounded worker task',
        'unverified_rates': [], 'rates': RATES, 'scenarios': cases,
        'configured_maximum_1_acu_stress_scenarios': stress,
        'favorable_60_second_worker_scenarios': favorable,
        'selected_scenario_assumptions': {
            'service_vcpu': 0.25, 'service_memory_gb': 1, 'service_desired_count': 1,
            'worker_vcpu': 0.5, 'worker_memory_gb': 2, 'worker_charged_seconds': 180,
            'average_active_acu': 0.5, 'configured_min_acu': 0, 'configured_max_acu': 1,
            'recurring_privacy_cleanup_interval_seconds': 900,
            'retained_privacy_cleanup_included': True, 'extra_awake_fraction': 0.15,
            'alb_average_lcu_allowance': 0.1,
            'capacity_or_spending_guarantee': False,
            'actual_cloud_measurement_required': True,
        },
        'workload_assumptions': ASSUMPTIONS,
        'notes': [
            'UI, API and metadata-only controller share one always-available Fargate service task. Worker/sweep and release-maintenance tasks run on Fargate only when needed. This estimate has no application Lambda compute or API Gateway.',
            'The selected service is 0.25 vCPU/1 GB and bounded worker is 0.5 vCPU/2 GB. Memory, throughput, startup and task durations are planning assumptions requiring real deployment validation. A 512 MiB combined service has not been validated and is not selected.',
            'Linux Fargate charges per second with a 60-second minimum, from image-download start until task termination. Selected worker tasks budget 180 charged seconds; favorable cases budget 60 seconds. Neither duration is a billing cap or proof of actual startup time.',
            'The selected cases preserve retained completed deletion cleanup every 900 seconds indefinitely: 2,920 SQL sweeps/month, plus separate user checks and exports. Minute metadata checks run in the existing service and do not create minutely Fargate tasks or idle SQL queries.',
            'Each SQL wake window remains 45 seconds of resume/work plus the 300-second auto-pause countdown. Thirty isolated sessions per user and all scheduled sweeps receive a 15% awake-time allowance, with no overlap savings; modeled awake time is capped at 730 hours.',
            'Aurora PostgreSQL Serverless v2 is configured MinCapacity=0, MaxCapacity=1. Average active capacity of 0.5 ACU is a low-volume assumption, not a supported maximum or spending cap. Stress cases price the same awake windows at 1 ACU.',
            'Physical PostgreSQL connections must close at work boundaries. Persistent service pools, readiness polling, metrics queries, replication or other background SQL can prevent auto-pause and invalidate the estimate. One ACU continuously active costs $87.60/month in database compute alone.',
            'Tasks use IPv6-only networking; the internal ALB has no billed public IPv4 addresses. There are no NAT gateways, paid interface endpoints, EC2 compute instances or RDS Proxy. ECR/service dual-stack reachability and dual-stack Aurora access must pass real deployment admission.',
            'The 0.1 average ALB LCU allowance is an engineering planning quantity, not verified capacity. AWS charges the maximum LCU dimension across new connections, active connections, processed bytes and rule evaluations; actual traffic and rules can change this cost.',
            'CloudFront viewer pricing assumes United States edges. AWS-origin-to-CloudFront transfer is exempt; viewer responses are charged once, including full 64 MiB exports. UI assets are served by the ECS task rather than a static S3 website.',
            'Three customer-managed KMS keys, three managed secrets, one custom dashboard, three aggregate SQL-work custom metrics and ten standard alarm metric-months are included. EMF ingestion shares the log allowance. Container Insights and paid CloudFront additional metrics are disabled.',
            'Aurora includes minimum 10 GB consumed storage, 10 GB of additional billable retained backups, modeled I/O and cross-AZ traffic. Five S3 buckets include the retained unused web authority bucket, currently budgeted at 0 GB; UI files are in the container image. Deployment archives budget 0.1 GB and API/worker/UI images together budget 3 GB in one ECR repository. Retained data, releases, keys and backups may grow.',
            'DynamoDB metadata reads/writes, storage and PITR retain the prior conservative quantities. SQS includes a conservative 262,800-request idle-poll allowance even though bounded jobs do not require continuously running worker consumers.',
            'The $100 AWS Budget is authorized for On-The-Go Detection only. It supplies alerts rather than a spending cap. Shared account workloads, free tiers, credits, discounts, taxes, domains, support plans and external services are excluded.',
            'Supplemental Fargate/ALB evidence retains actual retrieval timestamps and full-offer hashes. The oldest regional review date is preserved; recomputation does not refresh evidence. Pricing does not prove AWS deployment, functional acceptance, restore testing or production eligibility.',
        ],
        'price_evidence_files': list(EVIDENCE_FILES),
        'resource_inventory': {
            'lambda_functions': 0, 'ecs_clusters': 1, 'ecs_services': 1,
            'always_available_fargate_tasks': 1, 'internal_application_load_balancers': 1,
            'aurora_clusters': 1, 'aurora_serverless_writers': 1,
            's3_buckets_including_registry': 5, 'ecr_repositories': 1,
            'cloudfront_distributions': 2, 'cloudfront_vpc_origins': 1,
            'dynamodb_metadata_tables': 1, 'dynamodb_pitr_enabled': True,
            'cloudwatch_dashboards': 1, 'cloudwatch_single_metric_alarms': 10,
            'kms_keys': 3, 'explicit_secrets': 2, 'rds_managed_master_secrets': 1,
            'public_ipv4_addresses': 0, 'nat_gateways': 0, 'paid_interface_endpoints': 0,
        },
        'owner_budget_usd': OWNER_BUDGET_USD, 'planned_monthly_active_users': 10,
        'budget_is_a_spending_cap': False,
        'continuous_max_capacity_database_compute_monthly_usd': money(Decimal(730) * Decimal(str(RATES['aurora_acu_hour']['usd']))),
    }


def render_document(estimate: dict) -> str:
    lines = [
        '# Fargate development monthly estimate — US East (Ohio)', '',
        f"**Original regional review timestamp preserved: `{CHECKED_AT}`. This estimate records no AWS deployment.** USD per 730-hour planning month before shared free tiers, credits, taxes and discounts. Supplemental evidence records actual UTC retrieval timestamps.", '',
        '| Monthly users | Selected: 180-second jobs, average 0.5 active ACU | Stress: 180-second jobs, 1 active ACU | Favorable: 60-second jobs, average 0.5 active ACU | Selected headroom below $100 |',
        '|---:|---:|---:|---:|---:|',
    ]
    for case, stress, favorable in zip(estimate['scenarios'], estimate['configured_maximum_1_acu_stress_scenarios'], estimate['favorable_60_second_worker_scenarios']):
        lines.append(f"| {case['monthly_active_users']} | ${case['total_monthly_usd']:.2f} | ${stress['total_monthly_usd']:.2f} | ${favorable['total_monthly_usd']:.2f} | ${case['budget_headroom_usd']:.2f} |")
    lines += ['',
              'The intended planning case is **10 monthly users** with an authorized **$100/month On-The-Go Detection budget**. One ECS Fargate task serves the UI and API and runs a metadata-only controller. Bounded Fargate tasks process jobs, recurring cleanup and release maintenance. An internal ALB behind CloudFront supplies HTTPS access; private Aurora PostgreSQL Serverless v2 retains the relational database. Application compute uses no Lambda.', '',
              '## Assumptions and limits', '']
    lines += ['- ' + note for note in estimate['notes']]
    case = estimate['scenarios'][1]
    lines += ['',
              f"At ten users, `(2,920 recurring privacy sweeps + 300 isolated user sessions) × (45 seconds resume/work + 300 seconds until pause) / 3,600`, increased by 15%, yields **{case['database_awake_hours_including_allowance']:.2f} awake database hours**. At average 0.5 ACU × $0.12/ACU-hour, Aurora compute costs **${next(item['monthly_usd'] for item in case['items'] if item['rate'] == 'aurora_acu_hour'):.2f}**. This preserves the 15-minute retained cleanup contract and the prior database wake assumptions.", '',
              f"There are **{case['worker_tasks_per_month']:,} bounded worker/sweep tasks/month**: 2,920 recurring privacy sweeps, 300 checks and 20 exports. At 180 charged seconds each, these use **{case['worker_billed_hours']:.2f} task-hours** at 0.5 vCPU/2 GB. Four administrative tasks separately budget 300 seconds at 0.5 vCPU/1 GB. A single service stays available for all 730 hours at 0.25 vCPU/1 GB. The favorable table changes only worker charged duration to the Linux minimum of 60 seconds; it does not remove cleanup.", '',
              'Each user makes 30 checks, two exports, three API calls/check, five API calls/export and three other calls/month. Web use budgets 30 sessions/user, 20 objects/session and 5 MB/session. Deployment probes add 100 API and 1,000 UI requests, batched in already-active database windows. API transfer includes two full 64 MiB exports/user. Logs budget 1 + 0.003 × users GB/month with seven-day retention.', '',
              '## Selected verified prices', '', '| Resource | Unit | USD | Source |', '|---|---|---:|---|']
    for name, rate in estimate['rates'].items():
        lines.append(f"| {name.replace('_', ' ')} | {rate['unit']} | {rate['usd']:.8f} | [AWS]({rate['source']}) |")
    lines += ['', '## Evidence and recomputation', '',
              'The [machine-readable estimate](fargate-estimate.json) records every quantity, rate, SKU/rate code and rounded line item. [Fargate supplemental evidence](aws-fargate-price-evidence.json) saves actual official Ohio Fargate and ALB offer rows, publication dates, retrieval timestamps and complete-offer hashes, together with the official Linux task-billing statement. Existing regional and serverless evidence supplies Aurora, S3, SQS, Cognito, KMS, DynamoDB, CloudFront and observability prices without advancing their review date.', '',
              'Recompute with `python infra/costs/build_fargate_estimate.py`. It writes this document and JSON deterministically, performs no network calls and makes no AWS changes. Each line is `Decimal(str(quantity)) × Decimal(str(rate))`, rounded to cents with `ROUND_HALF_UP`; totals sum those individually rounded line items. No separate early rounding or hidden precision is used.', '',
              'The [Lambda serverless estimate](SERVERLESS.md) and [managed QA/production estimate](README.md) describe separate profiles. A different region, viewer geography, workload, task shape, charged duration, connection lifecycle, capacity, storage or observability inventory requires a revised Fargate estimate. Repository gates and actual AWS admission remain separate requirements.', '']
    return '\n'.join(lines)


def main():
    estimate = build_estimate()
    (HERE / 'fargate-estimate.json').write_text(json.dumps(estimate, indent=2) + '\n')
    (HERE / 'FARGATE.md').write_text(render_document(estimate))
    print(json.dumps([{'users': case['monthly_active_users'],
                       'selected_monthly_usd': case['total_monthly_usd'],
                       'configured_maximum_1_acu_stress_monthly_usd': stress['total_monthly_usd'],
                       'favorable_60_second_worker_monthly_usd': favorable['total_monthly_usd']}
                      for case, stress, favorable in zip(estimate['scenarios'], estimate['configured_maximum_1_acu_stress_scenarios'], estimate['favorable_60_second_worker_scenarios'])]))


if __name__ == '__main__':
    main()
