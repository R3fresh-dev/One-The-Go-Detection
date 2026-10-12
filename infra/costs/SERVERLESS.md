# Serverless development monthly estimate — US East (Ohio)

**Original regional review timestamp preserved: `2026-10-11T00:00:00Z`. This estimate records no AWS deployment.** USD per 730-hour planning month before shared free tiers, credits, taxes and discounts. Supplemental sources carry their actual UTC retrieval timestamps.

| Monthly users | Selected low-volume average 0.5 ACU, recurring cleanup | Stress: 1 active ACU, recurring cleanup | Favorable hourly-only phase at 0.5 ACU | Selected-case headroom below $50 |
|---:|---:|---:|---:|---:|
| 0 | $31.98 | $51.29 | $16.63 | $18.02 |
| 10 | $34.60 | $55.89 | $19.27 | $15.40 |
| 100 | $58.29 | $97.43 | $42.94 | $-8.29 |

The intended planning case is **10 monthly users**, using a reviewed **average 0.5 active ACU** for a small workload. The actual Aurora configuration remains **minimum 0, maximum 1 ACU**. The selected case includes recurring 15-minute cleanup after account deletion, and fits the $50 planning target. The one-ACU stress case exceeds that target. AWS Budgets supplies alerts; these estimates provide no spending or capacity guarantee.

API, SQS worker, dispatcher, release maintenance and metadata control run as five Lambda functions. Private Aurora PostgreSQL Serverless v2 supplies the existing relational database. A metadata-only DynamoDB table lets minute control check due/in-flight work without touching an idle database. Hourly SQL safety sweeps apply before recurring privacy cleanup exists; completed deletion jobs continue their 15-minute cleanup contract. CloudFront fronts the streaming REST API and private static website; a custom CloudWatch dashboard shows health.

## Assumptions and limits

- Selected scenarios price a reviewed low-volume average of 0.5 ACU while the database is active. The actual configuration is MinCapacity=0, MaxCapacity=1 and SecondsUntilAutoPause=300. AWS documents maximum capacity of 1 ACU or higher; 0.5 is not a claimed supported maximum or a spending cap.
- Main scenarios include retained completed account-deletion jobs, which the existing cleanup contract resweeps every 900 seconds indefinitely. Thus there are 2,920 scheduled SQL sweeps/month even with zero currently active users. The hourly-only phase is a separate favorable case valid only before retained recurring cleanup exists.
- Scheduled SQL windows include 45 seconds of resume/work plus the five-minute idle countdown. Each user has 30 separate check/web sessions with the same 345-second database window. A 15% allowance increases all modeled awake hours for asynchronous messages, retries and longer activity. Overlap savings are not assumed.
- At one active ACU for those same wake windows, the ten-user stress case exceeds $50. Both the low-volume selected case and the larger-capacity stress case are published so the budget assumption is reviewable. Actual average ACUs, awake time, durations, storage and traffic must be measured during cloud admission before deployment costs are claimed.
- The minute control Lambda queries DynamoDB metadata only while SQL work is idle. The metadata-only table tracks epochs, in-flight leases and next-due work; pending work/retries may wake the database earlier. Completed privacy cleanup retains its 15-minute SQL schedule; it is not delayed to make the estimate smaller.
- Physical PostgreSQL connections must close after each Lambda invocation/request. Persistent SQL pools, an RDS Proxy, continuous SQL health/metrics polling, replication or frequent work can prevent auto-pause and invalidate the estimate.
- Database resume is typically about 15 seconds; longer pauses can require 30 seconds or more. API Lambda time includes a 15-second cold resume for every separate user session. Actual connection/request timeout behavior is validated during cloud admission.
- API Lambda is 1 GB with a 900-second timeout; SQS worker is 2 GB/180 seconds; dispatcher is 512 MB/180 seconds; release maintenance is 512 MB/900 seconds; minute control is 128 MB/30 seconds. Four release maintenance/migration calls at 300 seconds each are budgeted separately. Duration assumptions are engineering planning inputs, not tested capacity.
- REST response streaming preserves the 64 MiB export allowance. Each export is conservatively charged as seven 10 MB REST request units, full response transfer, Lambda stream bytes after the first 6 MiB and 29 additional seconds of API streaming. Export workers separately budget 29 seconds at 2 GB.
- Two pay-as-you-go CloudFront distributions serve static assets and the regional streaming REST API. AWS-origin-to-CloudFront data transfer is $0/GB; viewer transfer is charged once through CloudFront, and origin-bound POST/PUT/body transfer is priced separately.
- Private dual-stack Lambda subnets use an IPv6 egress-only internet gateway plus an S3 gateway endpoint. The model has no EC2 instances, NAT gateway, ALB, paid interface endpoint, RDS Proxy or provisioned Lambda concurrency. Required public service/issuer paths must use the supported configured IPv6 or gateway routes.
- API probes are limited to 100 per planning month and batched in deployment/already-active database windows. This is not a plan for 5,000 separate SQL-readiness probes; repeated probes can keep the database awake.
- DynamoDB PAY_PER_REQUEST quantities include three <=4 KiB strongly consistent reads and a conservative one <=1 KiB write allowance per minute-control tick. Each SQL invocation additionally budgets two read units and six write units for transactional lease entry, deletion and epoch/due updates. Metadata storage and PITR each budget 0.01 GB-month. Larger items/queries/indexes/control loops require revised quantities. Minute scheduling uses an AWS::Events::Rule, not a paid Scheduler resource.
- Three customer-managed KMS keys and three managed secrets remain provisioned. Native Lambda/Aurora/API Gateway/SQS/DynamoDB/CloudFront metrics, one custom dashboard, three actual-SQL-work custom metrics and ten single-metric alarms are included. Custom metrics use Embedded Metric Format logs already included in ingestion; there is no separate PutMetricData request charge. Container Insights, paid CloudFront additional metrics and detailed API Gateway metrics are disabled.
- Aurora Standard storage includes its minimum 10 GB plus 0.01 GB/user. Billable I/O is 100,000 plus 1,000 per check. Ten GB-months of additional retained backup storage is charged above the included allocation; paid snapshot export and cross-region backup copying are excluded.
- Static origin storage budgets 1 GB across current/noncurrent immutable releases; the registry deployment bucket adds 0.1 GB. Four publishes/month with 500 objects and one wildcard invalidation each are included. Retained releases, deployment objects, images, records, backups and rotated key versions can grow beyond the allowances.
- CloudFront viewer pricing assumes United States edges; an Ohio origin does not fix the viewer price. Account-wide free tiers and credits are not assumed. Domain registration, optional DNS, support plans, taxes and external services are excluded.
- The $50 AWS Budget is a planning target with alerts, not a guaranteed spending cap. One ACU held active for all 730 hours costs $87.60 in database compute alone. The ten-user selected case fits under the stated low-volume average-capacity, awake-time, duration, storage and traffic assumptions; higher usage can exceed the target.
- This is a single-writer development profile with cold resumes and no read replica. At 0.5 active ACU the database has approximately 1 GiB of memory; this is a capacity limitation, not a validated throughput claim. Network/database/worker behavior and load are measured during cloud admission. AWS restore and application release acceptance remain separate checks.
- Supplemental sources retain actual UTC retrieval timestamps and full-offer hashes. The original regional checked_at date is preserved because those rates still underpin this profile; recomputation does not refresh evidence.

The main database awake-time model is `(2,920 recurring privacy-cleanup sweeps + 30 × users isolated sessions) × (45 seconds resume/work + 300 seconds until pause) / 3600`, increased by 15% and capped at 730 hours. At ten users this is 308.58 hours before the allowance and 354.87 after it. At average 0.5 ACU × $0.12, the database-compute line is $21.29. The favorable phase uses 730 hourly safety sweeps, but cannot represent the full retained-deletion workload. Actual wake windows, average ACUs, durations and retries are measured during cloud admission.

Each user makes 30 checks, two exports, three API calls/check, five API calls/export and three other calls/month. Check workers assume five seconds at 2 GB. Each user makes 30 web sessions with 20 objects and 5 MB/session. Static probes add 1,000 requests and 0.1 GB; API deployment probes add 100 requests and 0.1 GiB, batched while the database is already active. API responses add 0.01 GiB/user plus two full 64 MiB exports/user. Log ingestion is 1 + 0.003 × users GB/month with seven-day retention.

## Selected verified prices

| Resource | Unit | USD | Source |
|---|---|---:|---|
| aurora acu hour | ACU-Hr | 0.12000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-2/index.csv) |
| aurora storage gb month | GB-Mo | 0.10000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-2/index.csv) |
| aurora io request | IOs | 0.00000020 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-2/index.csv) |
| aurora excess backup gb month | GB-Mo | 0.02100000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-2/index.json) |
| lambda x86 gb second | Lambda-GB-Second | 0.00001667 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSLambda/current/us-east-2/index.json) |
| lambda request | Request | 0.00000020 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSLambda/current/us-east-2/index.json) |
| lambda stream processed gib | Processed-Gigabytes | 0.00800000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSLambda/current/us-east-2/index.json) |
| rest api request unit | Requests | 0.00000350 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonApiGateway/current/us-east-2/index.json) |
| ddb read unit | ReadRequestUnits | 0.00000012 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonDynamoDB/current/us-east-2/index.json) |
| ddb write unit | WriteRequestUnits | 0.00000063 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonDynamoDB/current/us-east-2/index.json) |
| ddb storage gb month | GB-Mo | 0.25000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonDynamoDB/current/us-east-2/index.json) |
| ddb pitr gb month | GB-Mo | 0.20000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonDynamoDB/current/us-east-2/index.json) |
| cloudfront us https request | Requests | 0.00000100 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudFront/current/index.json) |
| cloudfront us egress gb | GB | 0.08500000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudFront/current/index.json) |
| cloudfront us origin transfer gb | GB | 0.02000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudFront/current/index.json) |
| cloudfront function | FunctionExecutions | 0.00000010 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudFront/current/index.json) |
| cloudfront invalidation path | URL | 0.00500000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudFront/current/index.json) |
| s3 storage gb month | GB-Mo | 0.02300000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-2/index.json) |
| s3 put request | Requests | 0.00000500 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-2/index.json) |
| s3 get request | Requests | 0.00000040 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-2/index.json) |
| sqs request | Requests | 0.00000040 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSQueueService/current/us-east-2/index.json) |
| cognito lite mau | CognitoUserPoolsMAU | 0.00550000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCognito/current/us-east-2/index.json) |
| secret month | Secrets | 0.40000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSSecretsManager/current/us-east-2/index.json) |
| secret request | API Requests | 0.00000500 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSSecretsManager/current/us-east-2/index.json) |
| kms initial key version month | Keys | 1.00000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/awskms/current/us-east-2/index.json) |
| kms symmetric request | Requests | 0.00000300 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/awskms/current/us-east-2/index.json) |
| kms ecc sign request | Requests | 0.00001500 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/awskms/current/us-east-2/index.json) |
| log ingest gb | GB | 0.50000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/us-east-2/index.json) |
| log storage gb month | GB-Mo | 0.03000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/us-east-2/index.json) |
| cw custom metric month | Metrics | 0.30000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/us-east-2/index.json) |
| cw alarm metric month | Alarms | 0.10000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/us-east-2/index.json) |
| cw dashboard month | Dashboards | 3.00000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/aws-other/index.json) |
| ecr storage gb month | GB-Mo | 0.10000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonECR/current/us-east-2/index.json) |
| sns request | Requests | 0.00000050 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonSNS/current/us-east-2/index.json) |
| sns email notification | Notifications | 0.00002000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonSNS/current/us-east-2/index.json) |
| cross az directional gb | GB | 0.01000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSDataTransfer/current/us-east-2/index.json) |

## Evidence and recomputation

The [machine-readable estimate](serverless-estimate.json) records every quantity, rate, SKU/rate code and rounded item. [Serverless evidence](aws-serverless-price-evidence.json) saves official regional offer rows, original Aurora CSV rows, publication dates, exact retrieval timestamps and full-offer hashes, plus official CloudFront transfer, API Gateway streaming and Aurora capacity/auto-pause statements. Existing [primary regional](aws-price-list-evidence.json) and [additional regional](aws-additional-price-evidence.json) evidence supplies S3, SQS, Cognito, KMS, logs, ECR and SNS rates.

Recompute with `python infra/costs/build_serverless_estimate.py`. It performs no network calls, advances no review date and makes no AWS changes. The separate [QA/production estimate](README.md) describes a different architecture.

A different origin region, viewer geography, workload, schedule, connection lifecycle, average capacity, memory/duration, storage retention or observability inventory requires a revised estimate. Required repository gates and real AWS admission/release validation remain separate from price reconciliation.
