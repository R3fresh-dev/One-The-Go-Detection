# Small development monthly estimate — US East (Ohio)

**Prices reviewed 11 October 2026. No AWS deployment is recorded by this estimate.** Gross USD per 730-hour month; no free tier, credits or discounts assumed. The owner selected a $50 monthly budget and a smaller development profile.

| Monthly users | Gross monthly estimate | Headroom below $50 |
|---:|---:|---:|
| 0 | $48.14 | $1.86 |
| 10 | $48.42 | $1.58 |
| 100 | $50.86 | $-0.86 |

The intended planning case is **10 monthly users**. This leaves a small allowance for unexpected usage. AWS Budgets sends alerts; it cannot guarantee the account stays below $50. The 100-user case is shown to make the budget limit visible, and does not establish that this host can sustain that load.

This profile uses a private Linux `t3a.medium` host for the API, worker and self-managed PostgreSQL, and a public ARM `t4g.nano` NAT host with one charged IPv4 address. Two CloudFront distributions expose the private API and private static origin over HTTPS. It has no ALB, API Gateway, managed NAT gateway or RDS instance. It provides reduced availability and requires operator-managed backups, patches and recovery.

## Assumptions and limits

- Development has one application node and one small NAT node in one availability zone. PostgreSQL is self-managed on the app node; there is no RDS standby or automatic database failover.
- Two pay-as-you-go CloudFront distributions serve the private EC2 API VPC origin and private S3 web origin. There is no ALB, API Gateway, managed NAT gateway, Fargate reservation or paid interface endpoint.
- Only the NAT node has a charged public IPv4 address. Application ingress is restricted to the CloudFront VPC origin. App-to-NAT traffic stays in the same availability zone; reprice cross-AZ routes if this changes.
- A 730-hour month keeps both nodes provisioned at zero users. The $50 AWS Budget is a notification threshold, not a spending cap; workload and retained-data growth can exceed it.
- Standard CPU credits prevent paid surplus CPU-credit charges; depletion throttles the app and NAT node. The 4 GiB app host shares memory among PostgreSQL, API, worker and monitoring. This is a small development workload, not tested capacity or production availability.
- Five custom metrics cover three worker aggregate values and app host memory/disk usage. The worker publishes every minute and the host publisher every five minutes, totaling 52,560 PutMetricData requests/month. Native EC2 status/CPU and basic CloudFront/SQS metrics add no paid custom metric ingestion.
- Ten single-metric operational alarms and one custom dashboard are included. CloudWatch Container Insights, EC2 detailed monitoring and paid CloudFront additional metrics are disabled.
- App and NAT gp3 volumes allocate 30 GB and 8 GB at included baseline IOPS/throughput. Ten GB-months of incremental EBS snapshots is an explicit allowance, not two full 30 GB snapshot charges. Measure changed blocks and deletion timing before extending retention.
- Nightly database dumps have seven-day current/noncurrent backup-prefix retention. Dumps and immutable deployment packages share a 1 + 0.03 x users GB-month planning allowance; package prefixes are retained and need operator-managed cleanup. Snapshot retention requires an actual reviewed backup policy and restore test; pricing a backup does not establish recoverability.
- Web storage allows 1 GB retained immutable releases/versions, four publishes per month with 500 objects each and one wildcard invalidation path per publish. Release retention must be bounded operationally or storage will grow.
- All viewer traffic is priced at United States CloudFront edge rates. Other viewer regions or CloudFront pricing plans need a revised estimate. Cache-disabled static hosting budgets an S3 GET for every viewer request.
- API responses and static web responses are both charged once through CloudFront. No second generic internet-egress or managed NAT processing fee is added to that traffic. Transfers from AWS origins to CloudFront have no separate internet transfer-out charge. CloudFront transfer toward origins, including POST/PUT uploads, is separately budgeted at 0.1 + 0.005 x users GB/month and the published US $0.02/GB rate.
- The default AWS-generated CloudFront HTTPS names need no owner-managed DNS record. An optional CNAME in an existing Route 53 zone costs $0.40 per million standard queries; resolver caching determines query count.
- Three KMS keys include data, journal and asymmetric capture signing even though raw human capture remains disabled. Key rotation, additional retained versions, excess logs/images, traffic, snapshots or records increase costs.
- One Secrets Manager master seed supplies independently derived database/application/tombstone credentials. Adding separate stored secrets increases the estimate by $0.40 per secret-month before request charges.
- The runtime builds its service image on the app node from the immutable source package. No ECR repository or ECR image-storage charge is included in this development profile.
- Gross on-demand rates exclude account-wide free tiers, credits, taxes and discounts. Both the original regional review date and new exact UTC offer retrieval timestamps are preserved.

Each user makes 30 checks and two exports/month. Static assets add 30 web sessions with 20 requests and 5 MB per session; web probes add 5,000 requests and 1 GB/month. API probes add 5,000 requests and 1 GB/month; user API traffic adds 10 requests/check, five requests/export and 0.05 GB/user. Log ingestion is 1 + 0.003 x users GB/month. Database-dump/deployment storage is 1 + 0.03 x users GB-months. Replace these engineering assumptions with measured usage before increasing access.

## Verified prices

| Resource | Unit | USD | Source |
|---|---|---:|---|
| cloudfront function | FunctionExecutions | 0.00000010 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudFront/current/index.json) |
| cloudfront invalidation path | URL | 0.00500000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudFront/current/index.json) |
| cloudfront us egress gb | GB | 0.08500000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudFront/current/index.json) |
| cloudfront us https request | Requests | 0.00000100 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudFront/current/index.json) |
| cloudfront us origin transfer gb | GB | 0.02000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudFront/current/index.json) |
| cognito mau | CognitoUserPoolsMAU | 0.00550000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCognito/current/us-east-2/index.json) |
| cw alarm metric month | Alarms | 0.10000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/us-east-2/index.json) |
| cw dashboard month | Dashboards | 3.00000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/aws-other/index.json) |
| cw metric month | Metrics | 0.30000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/us-east-2/index.json) |
| cw request | Requests | 0.00001000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/us-east-2/index.json) |
| ebs gp3 gb month | GB-Mo | 0.08000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/us-east-2/index.csv) |
| ebs snapshot gb month | GB-Mo | 0.05000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/us-east-2/index.csv) |
| ec2 app hour | Hrs | 0.03760000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/us-east-2/index.csv) |
| ec2 nat hour | Hrs | 0.00420000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/us-east-2/index.csv) |
| ec2 t3 linux credit vcpu hour | vCPU-Hours | 0.05000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/us-east-2/index.csv) |
| ipv4 hour | Hrs | 0.00500000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonVPC/current/us-east-2/index.json) |
| kms key version month | Keys | 1.00000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/awskms/current/us-east-2/index.json) |
| kms request | Requests | 0.00000300 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/awskms/current/us-east-2/index.json) |
| log ingest gb | GB | 0.50000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/us-east-2/index.json) |
| log store gb month | GB-Mo | 0.03000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/us-east-2/index.json) |
| route53 standard dns query | Queries | 0.00000040 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRoute53/current/index.json) |
| s3 gb month | GB-Mo | 0.02300000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-2/index.json) |
| s3 get | Requests | 0.00000040 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-2/index.json) |
| s3 put | Requests | 0.00000500 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-2/index.json) |
| secret month | Secrets | 0.40000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSSecretsManager/current/us-east-2/index.json) |
| secret request | API Requests | 0.00000500 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSSecretsManager/current/us-east-2/index.json) |
| sns email | Notifications | 0.00002000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonSNS/current/us-east-2/index.json) |
| sns request | Requests | 0.00000050 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonSNS/current/us-east-2/index.json) |
| sqs request | Requests | 0.00000040 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSQueueService/current/us-east-2/index.json) |

## Evidence and recomputation

The [machine-readable development estimate](development-estimate.json) contains all selected source rates, quantities and line items. [Official development price evidence](aws-development-price-evidence.json) records the original AWS EC2 Ohio offer CSV rows, publication date, exact UTC retrieval date and full-offer SHA-256. [Hosting/dashboard evidence](aws-hosting-price-evidence.json) and the existing regional evidence supply the remaining prices. Supplemental prices were fetched on 11 October 2026 (America/Chicago).

Run `python infra/costs/build_development_estimate.py` to recompute this profile from saved evidence. It does not refresh prices or advance `checked_at`. Run `python infra/costs/build_estimate.py` for the separate [QA/production profile](README.md); those larger environments exceed a $50 budget.

Ohio is the only reviewed origin region. A different origin region, private hosted zone, paid support plan, extra metrics/alarms, changed storage retention or different viewer geography requires an updated estimate before deployment.
