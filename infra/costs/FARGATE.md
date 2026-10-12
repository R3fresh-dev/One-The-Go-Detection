# Fargate development monthly estimate — US East (Ohio)

**Original regional review timestamp preserved: `2026-10-11T00:00:00Z`. This estimate records no AWS deployment.** USD per 730-hour planning month before shared free tiers, credits, taxes and discounts. Supplemental evidence records actual UTC retrieval timestamps.

| Monthly users | Selected: 180-second jobs, average 0.5 active ACU | Stress: 180-second jobs, 1 active ACU | Favorable: 60-second jobs, average 0.5 active ACU | Selected headroom below $100 |
|---:|---:|---:|---:|---:|
| 0 | $62.75 | $82.06 | $59.91 | $37.25 |
| 10 | $65.61 | $86.90 | $62.46 | $34.39 |
| 100 | $91.54 | $130.68 | $85.60 | $8.46 |

The intended planning case is **10 monthly users** with an authorized **$100/month On-The-Go Detection budget**. One ECS Fargate task serves the UI and API and runs a metadata-only controller. Bounded Fargate tasks process jobs, recurring cleanup and release maintenance. An internal ALB behind CloudFront supplies HTTPS access; private Aurora PostgreSQL Serverless v2 retains the relational database. Application compute uses no Lambda.

## Assumptions and limits

- UI, API and metadata-only controller share one always-available Fargate service task. Worker/sweep and release-maintenance tasks run on Fargate only when needed. This estimate has no application Lambda compute or API Gateway.
- The selected service is 0.25 vCPU/1 GB and bounded worker is 0.5 vCPU/2 GB. Memory, throughput, startup and task durations are planning assumptions requiring real deployment validation. A 512 MiB combined service has not been validated and is not selected.
- Linux Fargate charges per second with a 60-second minimum, from image-download start until task termination. Selected worker tasks budget 180 charged seconds; favorable cases budget 60 seconds. Neither duration is a billing cap or proof of actual startup time.
- The selected cases preserve retained completed deletion cleanup every 900 seconds indefinitely: 2,920 SQL sweeps/month, plus separate user checks and exports. Minute metadata checks run in the existing service and do not create minutely Fargate tasks or idle SQL queries.
- Each SQL wake window remains 45 seconds of resume/work plus the 300-second auto-pause countdown. Thirty isolated sessions per user and all scheduled sweeps receive a 15% awake-time allowance, with no overlap savings; modeled awake time is capped at 730 hours.
- Aurora PostgreSQL Serverless v2 is configured MinCapacity=0, MaxCapacity=1. Average active capacity of 0.5 ACU is a low-volume assumption, not a supported maximum or spending cap. Stress cases price the same awake windows at 1 ACU.
- Physical PostgreSQL connections must close at work boundaries. Persistent service pools, readiness polling, metrics queries, replication or other background SQL can prevent auto-pause and invalidate the estimate. One ACU continuously active costs $87.60/month in database compute alone.
- Tasks use IPv6-only networking; the internal ALB has no billed public IPv4 addresses. There are no NAT gateways, paid interface endpoints, EC2 compute instances or RDS Proxy. ECR/service dual-stack reachability and dual-stack Aurora access must pass real deployment admission.
- The 0.1 average ALB LCU allowance is an engineering planning quantity, not verified capacity. AWS charges the maximum LCU dimension across new connections, active connections, processed bytes and rule evaluations; actual traffic and rules can change this cost.
- CloudFront viewer pricing assumes United States edges. AWS-origin-to-CloudFront transfer is exempt; viewer responses are charged once, including full 64 MiB exports. UI assets are served by the ECS task rather than a static S3 website.
- Three customer-managed KMS keys, three managed secrets, one custom dashboard, three aggregate SQL-work custom metrics and ten standard alarm metric-months are included. EMF ingestion shares the log allowance. Container Insights and paid CloudFront additional metrics are disabled.
- Aurora includes minimum 10 GB consumed storage, 10 GB of additional billable retained backups, modeled I/O and cross-AZ traffic. Five S3 buckets include the retained unused web authority bucket, currently budgeted at 0 GB; UI files are in the container image. Deployment archives budget 0.1 GB and API/worker/UI images together budget 3 GB in one ECR repository. Retained data, releases, keys and backups may grow.
- DynamoDB metadata reads/writes, storage and PITR retain the prior conservative quantities. SQS includes a conservative 262,800-request idle-poll allowance even though bounded jobs do not require continuously running worker consumers.
- The $100 AWS Budget is authorized for On-The-Go Detection only. It supplies alerts rather than a spending cap. Shared account workloads, free tiers, credits, discounts, taxes, domains, support plans and external services are excluded.
- Supplemental Fargate/ALB evidence retains actual retrieval timestamps and full-offer hashes. The oldest regional review date is preserved; recomputation does not refresh evidence. Pricing does not prove AWS deployment, functional acceptance, restore testing or production eligibility.

At ten users, `(2,920 recurring privacy sweeps + 300 isolated user sessions) × (45 seconds resume/work + 300 seconds until pause) / 3,600`, increased by 15%, yields **354.87 awake database hours**. At average 0.5 ACU × $0.12/ACU-hour, Aurora compute costs **$21.29**. This preserves the 15-minute retained cleanup contract and the prior database wake assumptions.

There are **3,240 bounded worker/sweep tasks/month**: 2,920 recurring privacy sweeps, 300 checks and 20 exports. At 180 charged seconds each, these use **162.00 task-hours** at 0.5 vCPU/2 GB. Four administrative tasks separately budget 300 seconds at 0.5 vCPU/1 GB. A single service stays available for all 730 hours at 0.25 vCPU/1 GB. The favorable table changes only worker charged duration to the Linux minimum of 60 seconds; it does not remove cleanup.

Each user makes 30 checks, two exports, three API calls/check, five API calls/export and three other calls/month. Web use budgets 30 sessions/user, 20 objects/session and 5 MB/session. Deployment probes add 100 API and 1,000 UI requests, batched in already-active database windows. API transfer includes two full 64 MiB exports/user. Logs budget 1 + 0.003 × users GB/month with seven-day retention.

## Selected verified prices

| Resource | Unit | USD | Source |
|---|---|---:|---|
| fargate vcpu hour | hours | 0.04048000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonECS/current/us-east-2/index.json) |
| fargate memory gb hour | hours | 0.00444500 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonECS/current/us-east-2/index.json) |
| alb hour | Hrs | 0.02250000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSELB/current/us-east-2/index.json) |
| alb lcu hour | LCU-Hrs | 0.00800000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSELB/current/us-east-2/index.json) |
| aurora acu hour | ACU-Hr | 0.12000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-2/index.csv) |
| aurora storage gb month | GB-Mo | 0.10000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-2/index.csv) |
| aurora io request | IOs | 0.00000020 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-2/index.csv) |
| aurora excess backup gb month | GB-Mo | 0.02100000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-2/index.csv) |
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

The [machine-readable estimate](fargate-estimate.json) records every quantity, rate, SKU/rate code and rounded line item. [Fargate supplemental evidence](aws-fargate-price-evidence.json) saves actual official Ohio Fargate and ALB offer rows, publication dates, retrieval timestamps and complete-offer hashes, together with the official Linux task-billing statement. Existing regional and serverless evidence supplies Aurora, S3, SQS, Cognito, KMS, DynamoDB, CloudFront and observability prices without advancing their review date.

Recompute with `python infra/costs/build_fargate_estimate.py`. It writes this document and JSON deterministically, performs no network calls and makes no AWS changes. Each line is `Decimal(str(quantity)) × Decimal(str(rate))`, rounded to cents with `ROUND_HALF_UP`; totals sum those individually rounded line items. No separate early rounding or hidden precision is used.

The [Lambda serverless estimate](SERVERLESS.md) and [managed QA/production estimate](README.md) describe separate profiles. A different region, viewer geography, workload, task shape, charged duration, connection lifecycle, capacity, storage or observability inventory requires a revised Fargate estimate. Repository gates and actual AWS admission remain separate requirements.
