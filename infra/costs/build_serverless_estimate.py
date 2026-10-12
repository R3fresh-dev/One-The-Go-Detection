#!/usr/bin/env python3
"""Recompute the reviewed serverless Ohio profile from saved AWS price evidence.

No network or AWS mutations. Recomputing never refreshes price-review dates.
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
)
SOURCES = [source for name in EVIDENCE_FILES for source in json.loads((HERE / name).read_text())]
# The old regional rates still underpin this estimate. Supplemental retrieval
# timestamps are retained individually; they don't renew that older review.
CHECKED_AT = json.loads((HERE / 'us-east-2-estimate.json').read_text())['checked_at']


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
            if 'retrieved_at' in source:
                rate['retrieved_at'] = source['retrieved_at']
            matches.append(rate)
    if not matches:
        raise ValueError(f'Missing official verified rate: {service} {usage} {attributes}')
    # Gross estimates don't consume account-wide free tiers. All modeled use is
    # below the first paid-tier upper bound; use that tier's highest unit price.
    return max(matches, key=lambda row: row['usd'])


RATES = {
    'aurora_acu_hour': verified_rate('AmazonRDS', 'USE2-Aurora:ServerlessV2Usage', databaseEngine='Aurora PostgreSQL'),
    'aurora_storage_gb_month': verified_rate('AmazonRDS', 'USE2-Aurora:StorageUsage', databaseEngine='Aurora PostgreSQL'),
    'aurora_io_request': verified_rate('AmazonRDS', 'USE2-Aurora:StorageIOUsage', databaseEngine='Aurora PostgreSQL'),
    'aurora_excess_backup_gb_month': verified_rate('AmazonRDS', 'USE2-Aurora:BackupUsage', databaseEngine='Aurora PostgreSQL'),
    'lambda_x86_gb_second': verified_rate('AWSLambda', 'USE2-Lambda-GB-Second'),
    'lambda_request': verified_rate('AWSLambda', 'USE2-Request'),
    'lambda_stream_processed_gib': verified_rate('AWSLambda', 'USE2-Lambda-Streaming-Response-Processed-Bytes'),
    'rest_api_request_unit': verified_rate('AmazonApiGateway', 'USE2-ApiGatewayRequest'),
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
    'aurora_min_capacity': 0,
    'aurora_max_capacity': 1,
    'seconds_until_auto_pause': 300,
    'idle_safety_sweep_interval_seconds': 3600,
    'retained_privacy_cleanup_interval_seconds': 900,
    'maintenance_resume_and_work_seconds': 45,
    'isolated_database_sessions_per_user_per_month': 30,
    'extra_database_awake_fraction': 0.15,
    'control_interval_seconds': 60,
    'control_memory_gb': 0.125,
    'control_duration_seconds': 1,
    'control_db_queries_while_idle': 0,
    'api_memory_gb': 1,
    'api_timeout_seconds': 900,
    'api_ordinary_duration_seconds': 2,
    'worker_memory_gb': 2,
    'worker_timeout_seconds': 180,
    'worker_check_duration_seconds': 5,
    'worker_export_duration_seconds': 29,
    'maintenance_memory_gb': 0.5,
    'dispatcher_memory_gb': 0.5,
    'dispatcher_timeout_seconds': 180,
    'dispatcher_user_job_seconds': 5,
    'release_maintenance_invocations_per_month': 4,
    'release_maintenance_duration_seconds': 300,
    'checks_per_user_per_month': 30,
    'exports_per_user_per_month': 2,
    'api_requests_per_check': 3,
    'api_requests_per_export': 5,
    'other_api_requests_per_user_per_month': 3,
    'deployment_api_probes_per_month': 100,
    'deployment_probe_database_windows': 'batched inside already-active maintenance/deployment sessions',
    'web_sessions_per_user_per_month': 30,
    'web_requests_per_session': 20,
    'web_transferred_gb_per_session': 0.005,
    'baseline_web_requests_per_month': 1000,
    'baseline_web_transfer_gb': 0.1,
    'baseline_api_transfer_gib': 0.1,
    'ordinary_api_transfer_gib_per_user': 0.01,
    'export_response_bytes': 64 * 1024 * 1024,
    'rest_stream_request_increment_bytes': 10_000_000,
    'lambda_first_stream_bytes_per_response': 6 * 1024 * 1024,
    'api_cold_resume_seconds_per_session': 15,
    'aurora_storage_gb_baseline': 10,
    'extra_retained_backup_gb': 10,
    'custom_metrics': 3,
    'alarm_metric_months': 10,
    'custom_dashboards': 1,
    'kms_initial_key_versions': 3,
    'secrets': 3,
    'retained_ecr_image_gb': 2,
    'retained_web_release_gb': 1,
    'retained_deployment_artifact_gb': 0.1,
    'web_publishes_per_month': 4,
    'web_objects_per_publish': 500,
    'web_invalidation_paths_per_publish': 1,
    'ddb_control_storage_gb': 0.01,
    'ddb_control_read_units_per_tick': 3,
    'ddb_control_write_units_per_tick': 1,
    'ddb_lease_write_units_per_sql_invocation': 6,
    'viewer_edge_location': 'United States',
    'cloudfront_distributions': 2,
    'cloudfront_pricing_plan': 'pay-as-you-go',
}


def money(value) -> float:
    return float(Decimal(str(value)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))


def scenario(users: int, active_acu: float = .5, retained_privacy_cleanup: bool = True) -> dict:
    a = ASSUMPTIONS
    hours = a['hours_per_month']
    checks = users * a['checks_per_user_per_month']
    exports = users * a['exports_per_user_per_month']
    control = hours * 3600 // a['control_interval_seconds']
    sql_interval = a['retained_privacy_cleanup_interval_seconds'] if retained_privacy_cleanup else a['idle_safety_sweep_interval_seconds']
    maintenance = hours * 3600 // sql_interval
    isolated_sessions = users * a['isolated_database_sessions_per_user_per_month']
    wake_window = a['maintenance_resume_and_work_seconds'] + a['seconds_until_auto_pause']
    # Separate windows deliberately ignore overlap savings. The 15% allowance
    # also budgets extra wakes/extended activity caused by asynchronous work.
    base_awake_hours = (maintenance + isolated_sessions) * wake_window / 3600
    awake_hours = min(hours, base_awake_hours * (1 + a['extra_database_awake_fraction']))
    api_requests = a['deployment_api_probes_per_month'] + checks * a['api_requests_per_check'] + exports * a['api_requests_per_export'] + users * a['other_api_requests_per_user_per_month']
    web_requests = a['baseline_web_requests_per_month'] + users * a['web_sessions_per_user_per_month'] * a['web_requests_per_session']
    api_gib = a['baseline_api_transfer_gib'] + users * a['ordinary_api_transfer_gib_per_user'] + exports * a['export_response_bytes'] / 1024 ** 3
    web_gb = a['baseline_web_transfer_gb'] + users * a['web_sessions_per_user_per_month'] * a['web_transferred_gb_per_session']
    export_rest_units = math.ceil(a['export_response_bytes'] / a['rest_stream_request_increment_bytes'])
    api_billable_units = api_requests + exports * (export_rest_units - 1)
    sql_invocations = api_requests + 2 * (checks + exports) + maintenance + a['release_maintenance_invocations_per_month']
    logs_gb = 1 + users * .003
    items = []

    def add(name: str, quantity, rate: str):
        if not math.isfinite(float(quantity)) or quantity < 0:
            raise ValueError('Nonfinite or negative planning quantity')
        cost = money(Decimal(str(quantity)) * Decimal(str(RATES[rate]['usd'])))
        items.append({'item': name, 'quantity': quantity, 'rate': rate, 'monthly_usd': cost})

    add('Aurora serverless PostgreSQL active ACU-hours incl. 15% wake/activity allowance', awake_hours * active_acu, 'aurora_acu_hour')
    add('Aurora consumed storage GB-months incl. minimum 10 GB', a['aurora_storage_gb_baseline'] + users * .01, 'aurora_storage_gb_month')
    add('Aurora billable storage I/O requests', 100000 + checks * 1000, 'aurora_io_request')
    add('Aurora retained backup GB-months above included storage allocation', a['extra_retained_backup_gb'], 'aurora_excess_backup_gb_month')
    add('Lambda API ordinary invocation GB-seconds', api_requests * a['api_memory_gb'] * a['api_ordinary_duration_seconds'], 'lambda_x86_gb_second')
    add('Lambda API 64 MiB export additional stream GB-seconds', exports * a['api_memory_gb'] * 29, 'lambda_x86_gb_second')
    add('Lambda API cold database resume GB-seconds', isolated_sessions * a['api_memory_gb'] * a['api_cold_resume_seconds_per_session'], 'lambda_x86_gb_second')
    add('Lambda SQS check worker GB-seconds', checks * a['worker_memory_gb'] * a['worker_check_duration_seconds'], 'lambda_x86_gb_second')
    add('Lambda export worker GB-seconds', exports * a['worker_memory_gb'] * a['worker_export_duration_seconds'], 'lambda_x86_gb_second')
    add('Lambda scheduled SQL dispatcher/resume GB-seconds', maintenance * a['dispatcher_memory_gb'] * a['maintenance_resume_and_work_seconds'], 'lambda_x86_gb_second')
    add('Lambda pending-work dispatcher GB-seconds', (checks + exports) * a['dispatcher_memory_gb'] * a['dispatcher_user_job_seconds'], 'lambda_x86_gb_second')
    add('Lambda release maintenance/migration GB-seconds', a['release_maintenance_invocations_per_month'] * a['maintenance_memory_gb'] * a['release_maintenance_duration_seconds'], 'lambda_x86_gb_second')
    add('Lambda metadata-only minute control GB-seconds', control * a['control_memory_gb'] * a['control_duration_seconds'], 'lambda_x86_gb_second')
    add('Lambda API/worker/dispatcher/maintenance/control invocation units', api_requests + 2 * (checks + exports) + maintenance + control + a['release_maintenance_invocations_per_month'], 'lambda_request')
    add('Lambda charged streamed response GiB after first 6 MiB per export', exports * (a['export_response_bytes'] - a['lambda_first_stream_bytes_per_response']) / 1024 ** 3, 'lambda_stream_processed_gib')
    add('REST API request units incl. seven units per 64 MiB streamed export', api_billable_units, 'rest_api_request_unit')
    add('DynamoDB metadata strongly consistent <=4 KiB read units', control * a['ddb_control_read_units_per_tick'] + sql_invocations * 2, 'ddb_read_unit')
    add('DynamoDB metadata <=1 KiB control/transactional lease/epoch write units', control * a['ddb_control_write_units_per_tick'] + sql_invocations * a['ddb_lease_write_units_per_sql_invocation'], 'ddb_write_unit')
    add('DynamoDB metadata control state GB-months', a['ddb_control_storage_gb'], 'ddb_storage_gb_month')
    add('DynamoDB metadata point-in-time recovery GB-months', a['ddb_control_storage_gb'], 'ddb_pitr_gb_month')
    add('CloudFront US static and API HTTPS viewer requests', web_requests + api_requests, 'cloudfront_us_https_request')
    # AWS-origin-to-CloudFront transfer is exempt. Charge the viewer response
    # once through CloudFront, avoiding a second API Gateway internet-egress fee.
    add('CloudFront US static and API viewer transfer GB', web_gb + api_gib, 'cloudfront_us_egress_gb')
    add('CloudFront US origin-bound request/body transfer GB', .1 + users * .005, 'cloudfront_us_origin_transfer_gb')
    add('CloudFront static SPA viewer-request function executions', web_requests, 'cloudfront_function')
    add('CloudFront static wildcard invalidation paths', a['web_publishes_per_month'] * a['web_invalidation_paths_per_publish'], 'cloudfront_invalidation_path')
    add('S3 data/journal/export current and noncurrent GB-months', 1 + users * .01, 's3_storage_gb_month')
    add('S3 retained private static release/version GB-months', a['retained_web_release_gb'], 's3_storage_gb_month')
    add('S3 registry deployment artifact current/noncurrent GB-months', a['retained_deployment_artifact_gb'], 's3_storage_gb_month')
    add('S3 data/journal/export PUT/LIST requests', 1000 + checks * 2 + users * 4, 's3_put_request')
    add('S3 static release PUT requests', a['web_publishes_per_month'] * a['web_objects_per_publish'], 's3_put_request')
    add('S3 data/journal/export GET/HEAD requests', 1000 + checks * 2 + users * 20, 's3_get_request')
    add('S3 uncached static origin GET/HEAD requests', web_requests, 's3_get_request')
    add('SQS 64 KiB request units incl. two idle long-poll mapping consumers', 262800 + checks * 4 + exports * 4 + users, 'sqs_request')
    add('Cognito Lite MAU before shared free tier', users, 'cognito_lite_mau')
    add('Secrets Manager RDS master/application/tombstone secrets', a['secrets'], 'secret_month')
    add('Secrets Manager SQL function requests; metadata control reads no secret', 2 * (api_requests + 2 * (checks + exports) + maintenance) + 3 * a['release_maintenance_invocations_per_month'] + 1000, 'secret_request')
    add('KMS data/journal/capture-signing initial key versions', a['kms_initial_key_versions'], 'kms_initial_key_version_month')
    add('KMS symmetric requests', 30000 + checks * 4 + users * 20, 'kms_symmetric_request')
    add('KMS ECC signing request allowance', checks, 'kms_ecc_sign_request')
    add('CloudWatch application/database/function logs GB ingested', logs_gb, 'log_ingest_gb')
    add('CloudWatch seven-day retained log GB-months', logs_gb * 7 / 30, 'log_storage_gb_month')
    add('CloudWatch custom actual-work aggregate metrics', a['custom_metrics'], 'cw_custom_metric_month')
    add('CloudWatch evaluated standard alarm metric-month allowance', a['alarm_metric_months'], 'cw_alarm_metric_month')
    add('CloudWatch custom system health dashboard', a['custom_dashboards'], 'cw_dashboard_month')
    add('ECR retained Lambda software image GB-months', a['retained_ecr_image_gb'], 'ecr_storage_gb_month')
    add('SNS alarm API requests', 100, 'sns_request')
    add('SNS email notifications', 100, 'sns_email_notification')
    add('Cross-AZ directional database traffic planning allowance GB', 2 + users * .02, 'cross_az_directional_gb')
    total = money(sum(Decimal(str(item['monthly_usd'])) for item in items))
    return {
        'environment': 'serverless-development', 'monthly_active_users': users,
        'checks_per_month': checks, 'exports_per_month': exports,
        'api_requests_per_month': api_requests, 'rest_billable_request_units': api_billable_units,
        'control_invocations_per_month': control, 'maintenance_invocations_per_month': maintenance,
        'retained_privacy_cleanup_present': retained_privacy_cleanup,
        'scheduled_sql_interval_seconds': sql_interval,
        'database_awake_hours_before_allowance': base_awake_hours,
        'database_awake_hours_including_allowance': awake_hours,
        'active_database_acu_pricing_basis': active_acu,
        'aurora_acu_hours': awake_hours * active_acu,
        'raw_human_capture_enabled': False, 'items': items,
        'total_monthly_usd': total, 'owner_budget_usd': 50,
        'within_owner_budget': total <= 50,
        'budget_headroom_usd': money(Decimal('50') - Decimal(str(total))),
    }


def main():
    # The configured maximum remains the documented minimum MaxCapacity=1.
    # Low-volume average-0.5-ACU pricing is an assumption, not a capacity cap.
    cases = [scenario(users, .5, True) for users in (0, 10, 100)]
    stress = [scenario(users, 1, True) for users in (0, 10, 100)]
    hourly_only = [scenario(users, .5, False) for users in (0, 10, 100)]
    notes = [
        'Selected scenarios price a reviewed low-volume average of 0.5 ACU while the database is active. The actual configuration is MinCapacity=0, MaxCapacity=1 and SecondsUntilAutoPause=300. AWS documents maximum capacity of 1 ACU or higher; 0.5 is not a claimed supported maximum or a spending cap.',
        'Main scenarios include retained completed account-deletion jobs, which the existing cleanup contract resweeps every 900 seconds indefinitely. Thus there are 2,920 scheduled SQL sweeps/month even with zero currently active users. The hourly-only phase is a separate favorable case valid only before retained recurring cleanup exists.',
        'Scheduled SQL windows include 45 seconds of resume/work plus the five-minute idle countdown. Each user has 30 separate check/web sessions with the same 345-second database window. A 15% allowance increases all modeled awake hours for asynchronous messages, retries and longer activity. Overlap savings are not assumed.',
        'At one active ACU for those same wake windows, the ten-user stress case exceeds $50. Both the low-volume selected case and the larger-capacity stress case are published so the budget assumption is reviewable. Actual average ACUs, awake time, durations, storage and traffic must be measured during cloud admission before deployment costs are claimed.',
        'The minute control Lambda queries DynamoDB metadata only while SQL work is idle. The metadata-only table tracks epochs, in-flight leases and next-due work; pending work/retries may wake the database earlier. Completed privacy cleanup retains its 15-minute SQL schedule; it is not delayed to make the estimate smaller.',
        'Physical PostgreSQL connections must close after each Lambda invocation/request. Persistent SQL pools, an RDS Proxy, continuous SQL health/metrics polling, replication or frequent work can prevent auto-pause and invalidate the estimate.',
        'Database resume is typically about 15 seconds; longer pauses can require 30 seconds or more. API Lambda time includes a 15-second cold resume for every separate user session. Actual connection/request timeout behavior is validated during cloud admission.',
        'API Lambda is 1 GB with a 900-second timeout; SQS worker is 2 GB/180 seconds; dispatcher is 512 MB/180 seconds; release maintenance is 512 MB/900 seconds; minute control is 128 MB/30 seconds. Four release maintenance/migration calls at 300 seconds each are budgeted separately. Duration assumptions are engineering planning inputs, not tested capacity.',
        'REST response streaming preserves the 64 MiB export allowance. Each export is conservatively charged as seven 10 MB REST request units, full response transfer, Lambda stream bytes after the first 6 MiB and 29 additional seconds of API streaming. Export workers separately budget 29 seconds at 2 GB.',
        'Two pay-as-you-go CloudFront distributions serve static assets and the regional streaming REST API. AWS-origin-to-CloudFront data transfer is $0/GB; viewer transfer is charged once through CloudFront, and origin-bound POST/PUT/body transfer is priced separately.',
        'Private dual-stack Lambda subnets use an IPv6 egress-only internet gateway plus an S3 gateway endpoint. The model has no EC2 instances, NAT gateway, ALB, paid interface endpoint, RDS Proxy or provisioned Lambda concurrency. Required public service/issuer paths must use the supported configured IPv6 or gateway routes.',
        'API probes are limited to 100 per planning month and batched in deployment/already-active database windows. This is not a plan for 5,000 separate SQL-readiness probes; repeated probes can keep the database awake.',
        'DynamoDB PAY_PER_REQUEST quantities include three <=4 KiB strongly consistent reads and a conservative one <=1 KiB write allowance per minute-control tick. Each SQL invocation additionally budgets two read units and six write units for transactional lease entry, deletion and epoch/due updates. Metadata storage and PITR each budget 0.01 GB-month. Larger items/queries/indexes/control loops require revised quantities. Minute scheduling uses an AWS::Events::Rule, not a paid Scheduler resource.',
        'Three customer-managed KMS keys and three managed secrets remain provisioned. Native Lambda/Aurora/API Gateway/SQS/DynamoDB/CloudFront metrics, one custom dashboard, three actual-SQL-work custom metrics and ten single-metric alarms are included. Custom metrics use Embedded Metric Format logs already included in ingestion; there is no separate PutMetricData request charge. Container Insights, paid CloudFront additional metrics and detailed API Gateway metrics are disabled.',
        'Aurora Standard storage includes its minimum 10 GB plus 0.01 GB/user. Billable I/O is 100,000 plus 1,000 per check. Ten GB-months of additional retained backup storage is charged above the included allocation; paid snapshot export and cross-region backup copying are excluded.',
        'Static origin storage budgets 1 GB across current/noncurrent immutable releases; the registry deployment bucket adds 0.1 GB. Four publishes/month with 500 objects and one wildcard invalidation each are included. Retained releases, deployment objects, images, records, backups and rotated key versions can grow beyond the allowances.',
        'CloudFront viewer pricing assumes United States edges; an Ohio origin does not fix the viewer price. Account-wide free tiers and credits are not assumed. Domain registration, optional DNS, support plans, taxes and external services are excluded.',
        'The $50 AWS Budget is a planning target with alerts, not a guaranteed spending cap. One ACU held active for all 730 hours costs $87.60 in database compute alone. The ten-user selected case fits under the stated low-volume average-capacity, awake-time, duration, storage and traffic assumptions; higher usage can exceed the target.',
        'This is a single-writer development profile with cold resumes and no read replica. At 0.5 active ACU the database has approximately 1 GiB of memory; this is a capacity limitation, not a validated throughput claim. Network/database/worker behavior and load are measured during cloud admission. AWS restore and application release acceptance remain separate checks.',
        'Supplemental sources retain actual UTC retrieval timestamps and full-offer hashes. The original regional checked_at date is preserved because those rates still underpin this profile; recomputation does not refresh evidence.',
    ]
    output = {
        'schema_version': '1.0.0', 'deployment_profile': 'serverless-development',
        'region': 'us-east-2', 'currency': 'USD', 'checked_at': CHECKED_AT,
        'pricing_basis': 'On-demand gross before shared free tiers/credits, tax and discounts; reviewed low-volume average 0.5 active ACU with configured maximum 1 ACU',
        'unverified_rates': [], 'rates': RATES, 'scenarios': cases,
        'configured_maximum_1_acu_stress_scenarios': stress,
        'hourly_safety_only_no_retained_privacy_cleanup_scenarios': hourly_only,
        'selected_scenario_assumptions': {
            'average_active_acu': 0.5, 'configured_min_acu': 0,
            'configured_max_acu': 1, 'recurring_privacy_cleanup_interval_seconds': 900,
            'retained_privacy_cleanup_included': True, 'extra_awake_fraction': 0.15,
            'capacity_or_spending_guarantee': False, 'actual_cloud_measurement_required': True,
        },
        'workload_assumptions': ASSUMPTIONS, 'notes': notes,
        'price_evidence_files': list(EVIDENCE_FILES),
        'resource_inventory': {
            'lambda_functions': 5, 'aurora_clusters': 1, 'aurora_serverless_writers': 1,
            's3_buckets_including_registry': 5, 'ecr_repositories': 1,
            'dynamodb_metadata_tables': 1, 'dynamodb_pitr_enabled': True,
            'cloudfront_distributions': 2, 'cloudwatch_dashboards': 1,
            'cloudwatch_single_metric_alarms': 10, 'kms_keys': 3,
            'explicit_secrets': 2, 'rds_managed_master_secrets': 1,
            'egress_only_internet_gateways': 1, 's3_gateway_endpoints': 1,
        },
        'owner_budget_usd': 50, 'planned_monthly_active_users': 10,
        'budget_is_a_spending_cap': False,
        'continuous_max_capacity_database_compute_monthly_usd': money(730 * RATES['aurora_acu_hour']['usd']),
    }
    (HERE / 'serverless-estimate.json').write_text(json.dumps(output, indent=2) + '\n')
    lines = [
        '# Serverless development monthly estimate — US East (Ohio)', '',
        f'**Original regional review timestamp preserved: `{CHECKED_AT}`. This estimate records no AWS deployment.** USD per 730-hour planning month before shared free tiers, credits, taxes and discounts. Supplemental sources carry their actual UTC retrieval timestamps.', '',
        '| Monthly users | Selected low-volume average 0.5 ACU, recurring cleanup | Stress: 1 active ACU, recurring cleanup | Favorable hourly-only phase at 0.5 ACU | Selected-case headroom below $50 |',
        '|---:|---:|---:|---:|---:|',
    ]
    for case, larger, favorable in zip(cases, stress, hourly_only):
        lines.append(f"| {case['monthly_active_users']} | ${case['total_monthly_usd']:.2f} | ${larger['total_monthly_usd']:.2f} | ${favorable['total_monthly_usd']:.2f} | ${case['budget_headroom_usd']:.2f} |")
    lines += ['', 'The intended planning case is **10 monthly users**, using a reviewed **average 0.5 active ACU** for a small workload. The actual Aurora configuration remains **minimum 0, maximum 1 ACU**. The selected case includes recurring 15-minute cleanup after account deletion, and fits the $50 planning target. The one-ACU stress case exceeds that target. AWS Budgets supplies alerts; these estimates provide no spending or capacity guarantee.', '',
              'API, SQS worker, dispatcher, release maintenance and metadata control run as five Lambda functions. Private Aurora PostgreSQL Serverless v2 supplies the existing relational database. A metadata-only DynamoDB table lets minute control check due/in-flight work without touching an idle database. Hourly SQL safety sweeps apply before recurring privacy cleanup exists; completed deletion jobs continue their 15-minute cleanup contract. CloudFront fronts the streaming REST API and private static website; a custom CloudWatch dashboard shows health.', '',
              '## Assumptions and limits', '']
    lines += ['- ' + note for note in notes]
    case = cases[1]
    db_cost = next(item['monthly_usd'] for item in case['items'] if item['rate'] == 'aurora_acu_hour')
    lines += ['', f"The main database awake-time model is `(2,920 recurring privacy-cleanup sweeps + 30 × users isolated sessions) × (45 seconds resume/work + 300 seconds until pause) / 3600`, increased by 15% and capped at 730 hours. At ten users this is {case['database_awake_hours_before_allowance']:.2f} hours before the allowance and {case['database_awake_hours_including_allowance']:.2f} after it. At average 0.5 ACU × $0.12, the database-compute line is ${db_cost:.2f}. The favorable phase uses 730 hourly safety sweeps, but cannot represent the full retained-deletion workload. Actual wake windows, average ACUs, durations and retries are measured during cloud admission.", '',
              'Each user makes 30 checks, two exports, three API calls/check, five API calls/export and three other calls/month. Check workers assume five seconds at 2 GB. Each user makes 30 web sessions with 20 objects and 5 MB/session. Static probes add 1,000 requests and 0.1 GB; API deployment probes add 100 requests and 0.1 GiB, batched while the database is already active. API responses add 0.01 GiB/user plus two full 64 MiB exports/user. Log ingestion is 1 + 0.003 × users GB/month with seven-day retention.', '',
              '## Selected verified prices', '', '| Resource | Unit | USD | Source |', '|---|---|---:|---|']
    for name, rate in RATES.items():
        lines.append(f"| {name.replace('_', ' ')} | {rate['unit']} | {rate['usd']:.8f} | [AWS]({rate['source']}) |")
    lines += ['', '## Evidence and recomputation', '',
              'The [machine-readable estimate](serverless-estimate.json) records every quantity, rate, SKU/rate code and rounded item. [Serverless evidence](aws-serverless-price-evidence.json) saves official regional offer rows, original Aurora CSV rows, publication dates, exact retrieval timestamps and full-offer hashes, plus official CloudFront transfer, API Gateway streaming and Aurora capacity/auto-pause statements. Existing [primary regional](aws-price-list-evidence.json) and [additional regional](aws-additional-price-evidence.json) evidence supplies S3, SQS, Cognito, KMS, logs, ECR and SNS rates.', '',
              'Recompute with `python infra/costs/build_serverless_estimate.py`. It performs no network calls, advances no review date and makes no AWS changes. The separate [QA/production estimate](README.md) describes a different architecture.', '',
              'A different origin region, viewer geography, workload, schedule, connection lifecycle, average capacity, memory/duration, storage retention or observability inventory requires a revised estimate. Required repository gates and real AWS admission/release validation remain separate from price reconciliation.']
    (HERE / 'SERVERLESS.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps([{'users': case['monthly_active_users'], 'selected_average_0_5_acu_monthly_usd': case['total_monthly_usd'], 'configured_maximum_1_acu_stress_monthly_usd': larger['total_monthly_usd'], 'hourly_only_phase_monthly_usd': favorable['total_monthly_usd']} for case, larger, favorable in zip(cases, stress, hourly_only)]))


if __name__ == '__main__':
    main()
