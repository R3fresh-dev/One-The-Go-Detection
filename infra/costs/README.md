# AWS monthly planning estimate — US East (Ohio)

**Prices checked 11 October 2026. No AWS resources have been deployed.** All amounts are USD per 730-hour month, before credits, shared free tiers, tax and discounts. These are workload estimates, not a quote or a tested capacity claim.

These totals describe the larger QA/production architecture. The owner-selected $50 development profile has its own [smaller estimate and assumptions](DEVELOPMENT.md), [JSON](development-estimate.json) and repeatable `python infra/costs/build_development_estimate.py` recomputation command.

## Monthly totals

| Environment | Idle, no users | 100 monthly users | 1,000 monthly users |
|---|---:|---:|---:|
| QA | $125.35 | $130.66 | $171.68 |
| PROD | $263.90 | $271.13 | $319.85 |

The production baseline runs two API tasks and one worker task with a metrics sidecar, one multi-AZ PostgreSQL instance, an ALB and two NAT gateways. QA runs one smaller API task, one worker/sidecar, single-AZ PostgreSQL, an ALB and one NAT gateway. Both use private task networking, three versioned KMS-encrypted data buckets plus a fourth versioned S3-encrypted static web bucket, a CloudFront distribution and navigation function, SQS source/dead-letter queues, a Cognito Lite pool, managed secrets and separate data/journal keys. Each environment includes one custom CloudWatch dashboard.

## Assumptions and limits

- 730-hour planning month; services stay provisioned at zero users. A stopped ECS service does not stop ALB/NAT/RDS costs.
- 100/1000-user scenarios are engineering workload models, not validated capacity or permission to collect/retain human data.
- RDS storage models 12 months at 30 checks/user/month and 128 KiB/check plus 20 GB baseline, rounded up to 10 GB; approved retention can require less.
- Raw eye/ECG/lab uploads are unavailable in this release; enabling them requires a new estimate.
- RDS Multi-AZ instance/storage rates already include the standby; they are not doubled again.
- Automated backup retention is QA 7 days and production 35 days. Additional charged snapshot allowances are explicit line items.
- KMS annual key rotations can add retained key-version charges; reprice as keys rotate.
- CloudWatch Container Insights and paid CloudFront additional metrics are disabled. Basic service metrics plus three custom metrics, one custom dashboard and the two active-only health alarms are included.
- Static web hosting uses a fourth private versioned S3 bucket and the default CloudFront HTTPS domain; optional custom DNS is priced separately below.
- CloudFront pricing depends on viewer edge location, not the Ohio origin region. These scenarios assume United States viewers and pay-as-you-go pricing; other edge locations or pricing plans require a revised estimate.
- The CloudFront cache is disabled in the actual stack, so every viewer request is budgeted as an S3 GET/HEAD and viewer-request function execution.
- Web retained release/version storage is a 1 GB planning allowance (four 0.25 GB releases, including noncurrent-version allowance). No automatic expiry is configured; storage grows beyond this allowance as releases accumulate.
- ALB aliases in an existing Route 53 zone add no ALB alias-query charge. The optional web CNAME has standard DNS query charges; domain registration and hosted zone ownership costs remain excluded.
- AWS Budget alerts notify; they do not stop spending. The required monthly budget remains an owner input.
- Free-tier allowances are account-wide and can reduce these gross estimates; no availability is assumed.

Each nonzero workload case assumes 30 checks per user each month, two exports per user, a 128 KiB database footprint per check, S3 storage of 1 + 0.01 × users GB, log ingestion of 1 + 0.003 × users GB, NAT processing of 5 + 0.01 × users GB, internet egress of 5 + 0.05 × users GB, and average ALB use of 0.1 + 0.0009 × users LCUs. The CPU-credit allowance is 0.1 surplus vCPU-hours per user. A load test must replace these assumptions before capacity commitments.

Web hosting adds 1 GB retained release/version storage, four monthly publishes with 500 S3 PUTs each, and one wildcard invalidation path per publish. It assumes 5,000 automated/probe HTTPS requests plus 30 browser sessions/user/month with 20 objects/session (600 requests/user), and 1 GB automated/probe transfer plus 5 MB/session (0.15 GB/user). Viewer transfer is charged separately from API egress, avoiding double counting. These are explicit planning inputs; replace them with measured artifact sizes and traffic before capacity commitments.

Active QA has 10 evaluated standard alarm metric-months; active production has 15. This includes the second underlying metric in the API error-rate alarm, two health-absence alarms and production autoscaling alarms. CloudWatch Container Insights and CloudFront additional metrics remain disabled. Each dashboard is budgeted at its gross $3/month rate.

The optional web CNAME in an existing Route 53 zone costs $0.40 per million standard DNS queries at the first paid tier. DNS query volume depends on resolver caching and is not the browser request count. Add that usage to the totals when selecting a custom hostname; the default CloudFront domain adds no owner-managed DNS record.

## Selected verified unit prices

| Resource | Unit | USD | Source |
|---|---|---:|---|
| fargate vcpu hour | hours | 0.04048000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonECS/current/us-east-2/index.json) |
| fargate gb hour | hours | 0.00444500 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonECS/current/us-east-2/index.json) |
| alb hour | Hrs | 0.02250000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSELB/current/us-east-2/index.json) |
| alb lcu hour | LCU-Hrs | 0.00800000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSELB/current/us-east-2/index.json) |
| rds qa hour | Hrs | 0.03200000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-2/index.json) |
| rds prod hour | Hrs | 0.12900000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-2/index.json) |
| rds qa gb month | GB-Mo | 0.11500000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-2/index.json) |
| rds prod gb month | GB-Mo | 0.23000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-2/index.json) |
| rds backup gb month | GB-Mo | 0.09500000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-2/index.json) |
| rds credit vcpu hour | vCPU-Hours | 0.07500000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-2/index.json) |
| ipv4 hour | Hrs | 0.00500000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonVPC/current/us-east-2/index.json) |
| s3 gb month | GB-Mo | 0.02300000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-2/index.json) |
| s3 put | Requests | 0.00000500 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-2/index.json) |
| s3 get | Requests | 0.00000040 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-2/index.json) |
| sqs request | Requests | 0.00000040 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSQueueService/current/us-east-2/index.json) |
| cognito mau | CognitoUserPoolsMAU | 0.00550000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCognito/current/us-east-2/index.json) |
| secret month | Secrets | 0.40000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSSecretsManager/current/us-east-2/index.json) |
| secret request | API Requests | 0.00000500 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSSecretsManager/current/us-east-2/index.json) |
| kms key version month | Keys | 1.00000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/awskms/current/us-east-2/index.json) |
| kms request | Requests | 0.00000300 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/awskms/current/us-east-2/index.json) |
| log ingest gb | GB | 0.50000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/us-east-2/index.json) |
| log store gb month | GB-Mo | 0.03000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/us-east-2/index.json) |
| cw metric month | Metrics | 0.30000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/us-east-2/index.json) |
| cw alarm metric month | Alarms | 0.10000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/us-east-2/index.json) |
| cw dashboard month | Dashboards | 3.00000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/aws-other/index.json) |
| cw request | Requests | 0.00001000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/us-east-2/index.json) |
| ecr gb month | GB-Mo | 0.10000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonECR/current/us-east-2/index.json) |
| sns request | Requests | 0.00000050 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonSNS/current/us-east-2/index.json) |
| sns email | Notifications | 0.00002000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonSNS/current/us-east-2/index.json) |
| internet egress gb | GB | 0.09000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSDataTransfer/current/us-east-2/index.json) |
| regional directional gb | GB | 0.01000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSDataTransfer/current/us-east-2/index.json) |
| cloudfront us https request | Requests | 0.00000100 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudFront/current/index.json) |
| cloudfront us egress gb | GB | 0.08500000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudFront/current/index.json) |
| cloudfront us origin transfer gb | GB | 0.02000000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudFront/current/index.json) |
| cloudfront function | FunctionExecutions | 0.00000010 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudFront/current/index.json) |
| cloudfront invalidation path | URL | 0.00500000 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudFront/current/index.json) |
| route53 standard dns query | Queries | 0.00000040 | [AWS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRoute53/current/index.json) |
| nat hour | Hrs | 0.04500000 | [AWS](https://aws.amazon.com/vpc/pricing/) |
| nat gb | GB | 0.04500000 | [AWS](https://aws.amazon.com/vpc/pricing/) |

## Detailed line items

The [machine-readable estimate](us-east-2-estimate.json) includes every quantity, selected price, SKU/rate code and line item for all six scenarios. The source evidence is saved in [primary regional prices](aws-price-list-evidence.json), [additional regional prices](aws-additional-price-evidence.json) and [web hosting, DNS and dashboard prices](aws-hosting-price-evidence.json). Supplemental sources were retrieved on 11 October 2026 (America/Chicago); their exact UTC `retrieved_at` timestamps and source offer hashes are recorded separately. The original regional `checked_at` date is preserved. Recompute totals with `python infra/costs/build_estimate.py`; it neither fetches current prices nor renews the review date.

## Costs outside these totals

- Domain registration and an existing optional Route 53 hosted zone.
- Optional custom web CNAME DNS query usage at the published standard-query rate.
- Paid AWS support, LocalStack licensing, CI/macOS runners, app store accounts and taxes.
- Human study/laboratory/clinical validation, shipping and hardware.
- WAF, CloudTrail paid data-event selectors, externally selected audit archive, additional observability tools and independent security review.
- Excess load above stated LCU/traffic/log/storage/CPU-credit assumptions and autoscaling above baseline.

One 0.5-vCPU/1-GB Fargate task adds about $18.02/month at baseline rates; both additional production API tasks plus one worker at maximum steady autoscaling add about $54.06/month before traffic, CPU credits or extra logs. A 200% deployment overlap is temporary and billed while present. RDS autoscaling cannot be shrunk in place, so a storage increase can persist after demand falls. Retained snapshots, buckets, keys, secrets, images and log groups continue to cost money after QA compute is removed.

Budget monitoring is configured at 50%, 80% and 100% actual spend and 100% forecast spend, using the supplied destination and the activated `deployment` cost-allocation tag. These totals do not choose a budget for the owner. The deployment CLI requires a positive budget, a real destination, a region-matching estimate no more than 31 days old, and available exact instance/database versions.

Official supporting pages: [Fargate](https://aws.amazon.com/fargate/pricing/), [RDS PostgreSQL](https://aws.amazon.com/rds/postgresql/pricing/), [VPC/NAT and IPv4](https://aws.amazon.com/vpc/pricing/), [CloudWatch](https://aws.amazon.com/cloudwatch/pricing/), [CloudFront](https://aws.amazon.com/cloudfront/pricing/), [Route 53](https://aws.amazon.com/route53/pricing/), [Cognito](https://aws.amazon.com/cognito/pricing/), [KMS](https://aws.amazon.com/kms/pricing/), [SNS](https://aws.amazon.com/sns/pricing/), [AWS Budgets](https://aws.amazon.com/aws-cost-management/aws-budgets/pricing/).
