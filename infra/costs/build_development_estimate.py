#!/usr/bin/env python3
"""Recompute the small development profile from saved official AWS prices.

This script never fetches prices or advances their review date. Development is
separate from the existing QA/production architecture and capacity assumptions.
"""
import json
from decimal import Decimal
from pathlib import Path
from build_estimate import RATES as BASE_RATES, SOURCES, lookup, money

HERE = Path(__file__).resolve().parent
SOURCES.extend(json.loads((HERE / 'aws-development-price-evidence.json').read_text()))
RATES = {
    **BASE_RATES,
    'ec2_app_hour': lookup('AmazonEC2', 'USE2-BoxUsage:t3a.medium', operatingSystem='Linux', tenancy='Shared', capacitystatus='Used'),
    'ec2_nat_hour': lookup('AmazonEC2', 'USE2-BoxUsage:t4g.nano', operatingSystem='Linux', tenancy='Shared', capacitystatus='Used'),
    'ebs_gp3_gb_month': lookup('AmazonEC2', 'USE2-EBS:VolumeUsage.gp3'),
    'ebs_snapshot_gb_month': lookup('AmazonEC2', 'USE2-EBS:SnapshotUsage'),
    'ec2_t3_linux_credit_vcpu_hour': lookup('AmazonEC2', 'USE2-CPUCredits:t3', operatingSystem='Linux'),
}


def scenario(users):
    hours = 730
    checks = users * 30
    exports = users * 2
    web_requests = 5000 + users * 600
    api_requests = 5000 + checks * 10 + exports * 5
    web_gb = 1 + users * .15
    api_gb = 1 + users * .05
    logs_gb = 1 + users * .003
    items = []

    def add(name, quantity, rate):
        cost = money(Decimal(str(quantity)) * Decimal(str(RATES[rate]['usd'])))
        items.append({'item': name, 'quantity': quantity, 'rate': rate, 'monthly_usd': cost})

    add('Private Linux/x86 app/worker/PostgreSQL t3a.medium instance', hours, 'ec2_app_hour')
    add('Public Linux/arm64 t4g.nano NAT instance', hours, 'ec2_nat_hour')
    add('One NAT elastic public IPv4 address', hours, 'ipv4_hour')
    add('Encrypted gp3 app/root/data 30 GB plus NAT root 8 GB', 38, 'ebs_gp3_gb_month')
    add('Incremental retained EBS snapshot GB-months (planning allowance)', 10, 'ebs_snapshot_gb_month')
    # Both instances use Standard credits. A depleted balance throttles CPU;
    # this model does not assume paid Unlimited-mode burst capacity.
    add('T3 surplus CPU-credit vCPU-hours (Standard mode)', 0, 'ec2_t3_linux_credit_vcpu_hour')
    add('S3 current/noncurrent data/journal/export GB-months', 1 + users * .01, 's3_gb_month')
    add('S3 encrypted database-dump/deployment artifact GB-months', 1 + users * .03, 's3_gb_month')
    add('S3 retained private static release/version GB-months', 1, 's3_gb_month')
    add('S3 data/journal/export/backup PUT/LIST requests', 1030 + checks * 2 + users * 4, 's3_put')
    add('S3 data/journal/export/backup GET/HEAD requests', 5000 + checks * 2 + users * 20, 's3_get')
    add('S3 web release PUT requests (4 releases x 500 objects)', 2000, 's3_put')
    add('S3 uncached static origin GET/HEAD requests', web_requests, 's3_get')
    add('CloudFront US web and API HTTPS viewer requests', web_requests + api_requests, 'cloudfront_us_https_request')
    add('CloudFront US web and API internet transfer GB', web_gb + api_gb, 'cloudfront_us_egress_gb')
    add('CloudFront US transfer to origins incl. API POST/PUT GB', .1 + users * .005, 'cloudfront_us_origin_transfer_gb')
    add('CloudFront static navigation function executions', web_requests, 'cloudfront_function')
    add('CloudFront wildcard static invalidation paths', 4, 'cloudfront_invalidation_path')
    add('SQS 64-KiB request units incl. two idle long-poll consumers', 262800 + checks * 4 + exports * 4 + users, 'sqs_request')
    add('Cognito Lite monthly active users before shared free tier', users, 'cognito_mau')
    add('Secrets Manager independently derived credential master seed', 1, 'secret_month')
    add('Secrets Manager API requests', 1000 + users, 'secret_request')
    add('KMS data/journal/capture-signing key versions (initial year)', 3, 'kms_key_version_month')
    add('KMS symmetric requests', 30000 + checks * 4 + users * 20, 'kms_request')
    add('CloudWatch application/PostgreSQL/host log GB ingested', logs_gb, 'log_ingest_gb')
    add('CloudWatch seven-day retained log GB-months', logs_gb * 7 / 30, 'log_store_gb_month')
    add('CloudWatch three worker and two host custom metrics', 5, 'cw_metric_month')
    add('CloudWatch standard evaluated alarm metric-months (allowance)', 10, 'cw_alarm_metric_month')
    add('CloudWatch custom system health dashboard', 1, 'cw_dashboard_month')
    add('CloudWatch worker minute-rate plus host five-minute PutMetricData requests', 52560, 'cw_request')
    add('SNS operational alarm API requests', 100, 'sns_request')
    add('SNS email notifications', 100, 'sns_email')
    total = money(sum(Decimal(str(item['monthly_usd'])) for item in items))
    return {
        'environment': 'dev', 'monthly_active_users': users, 'checks_per_month': checks,
        'raw_human_capture_enabled': False, 'items': items, 'total_monthly_usd': total,
        'owner_budget_usd': 50, 'within_owner_budget': total <= 50,
        'budget_headroom_usd': money(Decimal('50') - Decimal(str(total))),
    }


def main():
    scenarios = [scenario(users) for users in (0, 10, 100)]
    used_rates = {item['rate'] for case in scenarios for item in case['items']}
    used_rates.add('route53_standard_dns_query')
    notes = [
        'Development has one application node and one small NAT node in one availability zone. PostgreSQL is self-managed on the app node; there is no RDS standby or automatic database failover.',
        'Two pay-as-you-go CloudFront distributions serve the private EC2 API VPC origin and private S3 web origin. There is no ALB, API Gateway, managed NAT gateway, Fargate reservation or paid interface endpoint.',
        'Only the NAT node has a charged public IPv4 address. Application ingress is restricted to the CloudFront VPC origin. App-to-NAT traffic stays in the same availability zone; reprice cross-AZ routes if this changes.',
        'A 730-hour month keeps both nodes provisioned at zero users. The $50 AWS Budget is a notification threshold, not a spending cap; workload and retained-data growth can exceed it.',
        'Standard CPU credits prevent paid surplus CPU-credit charges; depletion throttles the app and NAT node. The 4 GiB app host shares memory among PostgreSQL, API, worker and monitoring. This is a small development workload, not tested capacity or production availability.',
        'Five custom metrics cover three worker aggregate values and app host memory/disk usage. The worker publishes every minute and the host publisher every five minutes, totaling 52,560 PutMetricData requests/month. Native EC2 status/CPU and basic CloudFront/SQS metrics add no paid custom metric ingestion.',
        'Ten single-metric operational alarms and one custom dashboard are included. CloudWatch Container Insights, EC2 detailed monitoring and paid CloudFront additional metrics are disabled.',
        'App and NAT gp3 volumes allocate 30 GB and 8 GB at included baseline IOPS/throughput. Ten GB-months of incremental EBS snapshots is an explicit allowance, not two full 30 GB snapshot charges. Measure changed blocks and deletion timing before extending retention.',
        'Nightly database dumps have seven-day current/noncurrent backup-prefix retention. Dumps and immutable deployment packages share a 1 + 0.03 x users GB-month planning allowance; package prefixes are retained and need operator-managed cleanup. Snapshot retention requires an actual reviewed backup policy and restore test; pricing a backup does not establish recoverability.',
        'Web storage allows 1 GB retained immutable releases/versions, four publishes per month with 500 objects each and one wildcard invalidation path per publish. Release retention must be bounded operationally or storage will grow.',
        'All viewer traffic is priced at United States CloudFront edge rates. Other viewer regions or CloudFront pricing plans need a revised estimate. Cache-disabled static hosting budgets an S3 GET for every viewer request.',
        'API responses and static web responses are both charged once through CloudFront. No second generic internet-egress or managed NAT processing fee is added to that traffic. Transfers from AWS origins to CloudFront have no separate internet transfer-out charge. CloudFront transfer toward origins, including POST/PUT uploads, is separately budgeted at 0.1 + 0.005 x users GB/month and the published US $0.02/GB rate.',
        'The default AWS-generated CloudFront HTTPS names need no owner-managed DNS record. An optional CNAME in an existing Route 53 zone costs $0.40 per million standard queries; resolver caching determines query count.',
        'Three KMS keys include data, journal and asymmetric capture signing even though raw human capture remains disabled. Key rotation, additional retained versions, excess logs/images, traffic, snapshots or records increase costs.',
        'One Secrets Manager master seed supplies independently derived database/application/tombstone credentials. Adding separate stored secrets increases the estimate by $0.40 per secret-month before request charges.',
        'The runtime builds its service image on the app node from the immutable source package. No ECR repository or ECR image-storage charge is included in this development profile.',
        'Gross on-demand rates exclude account-wide free tiers, credits, taxes and discounts. Both the original regional review date and new exact UTC offer retrieval timestamps are preserved.',
    ]
    output = {
        'schema_version': '1.0.0', 'checked_at': '2026-10-11T00:00:00Z',
        'region': 'us-east-2', 'currency': 'USD',
        'deployment_profile': 'development-single-node',
        'pricing_basis': 'On-demand gross before shared free tiers/credits, tax or negotiated discounts',
        'unverified_rates': [], 'rates': {name: RATES[name] for name in sorted(used_rates)},
        'owner_budget_usd': 50, 'planned_monthly_active_users': 10,
        'scenarios': scenarios, 'notes': notes,
        'workload_assumptions': {
            'hours_per_month': 730, 'app_instance_type': 't3a.medium', 'nat_instance_type': 't4g.nano',
            'availability_zones': 1, 'cpu_credit_mode': 'standard',
            'checks_per_user_per_month': 30, 'exports_per_user_per_month': 2,
            'web_sessions_per_user_per_month': 30, 'web_requests_per_session': 20,
            'web_gb_per_session': 0.005, 'baseline_web_https_requests_per_month': 5000,
            'baseline_api_https_requests_per_month': 5000, 'api_requests_per_check': 10,
            'api_requests_per_export': 5, 'baseline_web_transfer_gb_per_month': 1,
            'baseline_api_transfer_gb_per_month': 1, 'api_transfer_gb_per_user_per_month': 0.05,
            'baseline_cloudfront_origin_bound_transfer_gb': 0.1, 'cloudfront_origin_bound_gb_per_user': 0.005,
            'baseline_log_ingestion_gb_per_month': 1, 'log_gb_per_user_per_month': 0.003,
            'app_ebs_gb': 30, 'nat_ebs_gb': 8, 'retained_incremental_snapshot_gb': 10,
            'database_dump_retention_days': 7, 'deployment_package_retention': 'operator-managed',
            'viewer_edge_location': 'United States',
            'worker_custom_metrics': 3, 'host_custom_metrics': 2, 'custom_dashboards': 1,
            'standard_alarm_metric_months': 10, 'put_metric_data_requests_per_month': 52560,
            'worker_metric_publish_seconds': 60, 'host_metric_publish_seconds': 300,
            'secrets_manager_secret_count': 1, 'kms_initial_key_version_count': 3,
        },
        'exclusions': ['Domain registration and optional Route 53 zone/CNAME query usage', 'Paid AWS support, CI runners, app stores, taxes and external services', 'Workload or retained storage above the stated allowances', 'Production availability and recovery obligations'],
    }
    (HERE / 'development-estimate.json').write_text(json.dumps(output, indent=2) + '\n')
    lines = [
        '# Small development monthly estimate — US East (Ohio)', '',
        '**Prices reviewed 11 October 2026. No AWS deployment is recorded by this estimate.** Gross USD per 730-hour month; no free tier, credits or discounts assumed. The owner selected a $50 monthly budget and a smaller development profile.', '',
        '| Monthly users | Gross monthly estimate | Headroom below $50 |', '|---:|---:|---:|',
    ]
    for case in scenarios:
        lines.append(f"| {case['monthly_active_users']} | ${case['total_monthly_usd']:.2f} | ${case['budget_headroom_usd']:.2f} |")
    lines += ['', 'The intended planning case is **10 monthly users**. This leaves a small allowance for unexpected usage. AWS Budgets sends alerts; it cannot guarantee the account stays below $50. The 100-user case is shown to make the budget limit visible, and does not establish that this host can sustain that load.', '',
              'This profile uses a private Linux `t3a.medium` host for the API, worker and self-managed PostgreSQL, and a public ARM `t4g.nano` NAT host with one charged IPv4 address. Two CloudFront distributions expose the private API and private static origin over HTTPS. It has no ALB, API Gateway, managed NAT gateway or RDS instance. It provides reduced availability and requires operator-managed backups, patches and recovery.', '',
              '## Assumptions and limits', '']
    lines += ['- ' + note for note in notes]
    lines += ['', 'Each user makes 30 checks and two exports/month. Static assets add 30 web sessions with 20 requests and 5 MB per session; web probes add 5,000 requests and 1 GB/month. API probes add 5,000 requests and 1 GB/month; user API traffic adds 10 requests/check, five requests/export and 0.05 GB/user. Log ingestion is 1 + 0.003 x users GB/month. Database-dump/deployment storage is 1 + 0.03 x users GB-months. Replace these engineering assumptions with measured usage before increasing access.', '',
              '## Verified prices', '', '| Resource | Unit | USD | Source |', '|---|---|---:|---|']
    for name, rate in output['rates'].items():
        lines.append(f"| {name.replace('_', ' ')} | {rate['unit']} | {rate['usd']:.8f} | [AWS]({rate['source']}) |")
    lines += ['', '## Evidence and recomputation', '',
              'The [machine-readable development estimate](development-estimate.json) contains all selected source rates, quantities and line items. [Official development price evidence](aws-development-price-evidence.json) records the original AWS EC2 Ohio offer CSV rows, publication date, exact UTC retrieval date and full-offer SHA-256. [Hosting/dashboard evidence](aws-hosting-price-evidence.json) and the existing regional evidence supply the remaining prices. Supplemental prices were fetched on 11 October 2026 (America/Chicago).', '',
              'Run `python infra/costs/build_development_estimate.py` to recompute this profile from saved evidence. It does not refresh prices or advance `checked_at`. Run `python infra/costs/build_estimate.py` for the separate [QA/production profile](README.md); those larger environments exceed a $50 budget.', '',
              'Ohio is the only reviewed origin region. A different origin region, private hosted zone, paid support plan, extra metrics/alarms, changed storage retention or different viewer geography requires an updated estimate before deployment.']
    (HERE / 'DEVELOPMENT.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps([{key: case[key] for key in ('monthly_active_users', 'total_monthly_usd', 'within_owner_budget', 'budget_headroom_usd')} for case in scenarios]))


if __name__ == '__main__':
    main()
