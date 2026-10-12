# Connect AWS and repeat the deployment

The requested target is AWS account **738470137867**, region **us-east-2** (Ohio),
and repository `https://github.com/R3fresh-dev/One-The-Go-Detection`.
The account screenshot identifies this target. This workspace's AWS identity
check currently returns `NoCredentialsError`; no AWS resources have been deployed.

The selected profile is **development**, with self-managed PostgreSQL, alert
destination **jacobtyrawa@mail.com**, and a **$50/month** budget. The reviewed
10-user planning estimate is **$48.42/month**, before tax, with no free tier
assumed. This leaves only $1.58 of headroom. AWS Budgets sends notifications;
it does not cap spending. The separate existing managed QA/production profiles
exceed this budget.

## Deploy using the existing GitHub secrets

The selected credential route is now **GitHub Actions**. The repository already
has the operator-supplied secrets `ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
The [deployment workflow](../.github/workflows/deploy-development.yml) references
those exact names. GitHub injects their values on its runner; neither chat nor
this managed environment needs to receive them. `AWS_SESSION_TOKEN` is optional
for an existing temporary credential session. The GitHub connection cannot list
secret names (HTTP 403), so the two names above were confirmed by the operator.

The workflow admits the latest successful exact-source aggregate CI run before
it loads AWS credentials, verifies account `738470137867`, and uses the same
Python deployment command below. It only runs from current default `main` and
serializes all deployments to this account/region. First merge the reviewed
change after every required gate passes; then run **Deploy reduced-cost
development to AWS** from the repository's Actions tab. For its first empty
journal, set `establish_new` to true; keep it false on later deployments.
The workflow publishes the web/API/dashboard URLs in its summary and saves
credential-free receipts as an artifact. A failed later stage does not imply
earlier AWS operations were rolled back.

The direct environment/workstation options further below are alternatives.

## Selected development deployment

The new [development.py](development.py) command provisions a private 4 GiB
application host for the API, worker and PostgreSQL, a small public NAT host,
real Cognito, S3, KMS, SQS, CloudFront web/API hosting and a CloudWatch dashboard.
CloudFront supplies the HTTPS API and web hostnames. No domain purchase or
operator-supplied ACM certificate is required for this selected profile.
The API port is private and reachable through CloudFront's VPC-origin security
group; SSH and database ports are not exposed publicly.

```bash
npm ci --ignore-scripts --prefix infra
uv sync --project services/api --locked
uv run --project services/api python deploy/development.py plan \
  --config infra/config/development.example.json
```

After AWS access is configured and the reviewed source has passing exact-commit
CI, copy the development example to an ignored `development.local.json` and
set `releaseId` to that actual full commit. Run:

```bash
uv run --project services/api python deploy/development.py deploy \
  --config infra/config/development.local.json \
  --gate-evidence /protected/gates-REVIEWED_COMMIT.json --establish-new
```

Use `--establish-new` only for the first empty journal. Omit it on later
deployments. `--profile` selects an existing SDK/SSO profile; `--identity`
selects a configured managed AWS alias. The command checks account and pricing,
requires clean exact-source CI, preserves the database volume and journal,
builds the locked source, runs migration and independent admission before
activation, publishes the web bytes, and waits for actual health evidence.
It records private recovery state and receipts under `.local/deploy/development`.

```bash
uv run --project services/api python deploy/development.py health \
  --config infra/config/development.local.json
```

The receipt includes actual web/API URLs and the CloudWatch dashboard URL.
Confirm the SNS email subscription and test alarm delivery after provisioning.
Nightly PostgreSQL dumps are uploaded to private versioned S3; an actual restore
test and operator-managed EBS snapshots remain required. A health snapshot does
not establish recovery or customer acceptance.

This profile has one application host and one NAT host in a single availability
zone, operator-managed database maintenance and a shared host IAM boundary.
Container AWS permissions are combined on the development host rather than
the separate managed task roles. The application uses its existing `qa` cloud
settings to enforce verified database TLS and independent journal admission;
this does not make the development deployment QA-approved or eligible for
production promotion. Do not run a managed QA stack concurrently in this
account/region, since the runtime metric namespace and registry role names are
shared. Native mobile builds and physical firmware retain their separate gates.

## Give the managed environment access

1. If the environment configuration offers an AWS identity connection, connect
   an authorized deployment role using that flow's supplied trust details. Apply
   the reviewed environment configuration. The agent will check its readiness
   and select the actual configured identity alias.
2. Otherwise, in the AWS access portal, open the account's assigned permission
   set and choose **Access keys** for command-line or programmatic access. Obtain
   a temporary session authorized for deployment. A read-only permission set
   cannot provision the system.
3. Enter each temporary value separately into the managed environment's secret
   configuration: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and
   `AWS_SESSION_TOKEN`. Apply the configuration so the runtime receives them.
   Keep these values out of chat, source files, screenshots and shell arguments.
4. The agent will recheck environment readiness and run this read-only command:

   ```bash
   uv run --project services/api python deploy/check_access.py \
     --account 738470137867 --region us-east-2
   ```

The result reports the confirmed account and principal ARN. It performs no AWS
writes and does not establish that every deployment permission is available.
Expired temporary credentials must be renewed through the same secure setup.
An AWS identity alias can be checked with `--identity YOUR_CONFIGURED_ALIAS`;
the command reads only the non-secret manifest and uses its SDK profile selector.
That selector must also be used for subsequent deployment commands through
`AWS_PROFILE` and `AWS_CONFIG_FILE`, as supplied by the manifest.

Exact environment setting labels depend on the client. If it provides neither
identity connection nor secret configuration, run the scripts on an authorized
workstation instead. A local SSO login does not authenticate this remote runtime.

## Workstation alternative using IAM Identity Center

Use the AWS CLI installed on your workstation:

```bash
aws configure sso --profile otgd-qa
aws sso login --profile otgd-qa
uv run --project services/api python deploy/check_access.py \
  --account 738470137867 --region us-east-2 --profile otgd-qa
```

During SSO configuration, use your organization's actual start URL, Identity
Center region, account and authorized permission set. The SSO region can differ
from the deployment region. Permanent IAM access keys are unnecessary.

## Deployment permissions

An AWS administrator should authorize a deployment role for the selected
environment and review the CloudFormation execution role before CDK bootstrap.
It needs the platform's CloudFormation, ECR, ECS, VPC/EC2 networking, ALB, RDS,
S3, KMS, Cognito, SQS, Secrets Manager, CloudWatch dashboards/alarms/logs, SNS,
Budgets, ACM inspection and optional Route 53 operations. Limit `iam:PassRole`
to the reviewed bootstrap/execution and task roles. Creating bootstrap IAM
roles and installing their policies requires separate authorized IAM actions.
Do not substitute an unreviewed blanket administrator policy.

The read-only health command needs STS identity, stack outputs/resources, ECS
services/tasks, RDS instance status and CloudWatch dashboard/alarm/metric reads.
These permissions belong to an operator role; application task roles retain
their existing limited runtime permissions.

## Inputs still needed

- Authenticated AWS deployment access for account `738470137867`.
- Fresh passing exact-source GitHub aggregate gate evidence. The inspected
  `4f046941176c7a42f6275b346c68bb619f6f67b1` run
  [38202849451](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38202849451)
  failed PostgreSQL integration; that run cannot authorize a release.

## Existing managed QA/production alternative

This is the larger alternative, not the selected $50 development profile. It
requires an owned API hostname and issued regional certificate, trusted signing
authority, higher budget and actual separate-account QA acceptance before
production. See [README.md](README.md) for the full admitted release process.

The existing deployment scripts orchestrate the full hosted system: private
Fargate API/worker, PostgreSQL, Cognito, encrypted/versioned storage, queues,
TLS ingress, CloudFront web hosting, CloudWatch monitoring and budget alerts.
Android/iOS binaries and physical firmware need their separate release process.

```bash
npm ci --ignore-scripts --prefix infra
uv sync --project services/api --locked
# Copy qa.example.json to an ignored qa.local.json and fill real operator inputs.
uv run --project services/api python deploy/qa.py \
  --config infra/config/qa.local.json --plan
uv run --project services/api python deploy/platform.py validate \
  --config infra/config/qa.local.json
```

After the exact release commit is clean, admitted and CI-green, use the documented
`deploy/qa.py` command in [README.md](README.md), supplying its gate evidence and
trusted release authority. The workflow builds and signs immutable service/web
artifacts, deploys services stopped, verifies the independent journal, migrates,
verifies admission, activates, waits for worker progress and verifies published
HTTPS bytes. Use `--establish-new` only for the first empty environment.
Subsequent deployments preserve prior receipts and journal continuity.

The deployment receipt includes `cloudwatch_dashboard_name` and
`cloudwatch_dashboard_url`. Then run:

```bash
uv run --project services/api python deploy/health.py \
  --config .local/deploy/qa/COMMIT/ATTEMPT/active.local.json
```

The health command performs live read-only checks and returns nonzero on degraded
or unavailable evidence. A passing health snapshot does not replace the required
authenticated QA, privacy/recovery, security or alarm-delivery acceptance probes.
Production uses `deploy/prod.py`, the same reviewed service digest, a separate
account and the actual signed QA approval. Existing release gates stay enforced.

No deployment or all-gates-passed result is claimed by this guide. Review the
protected stage journal on failures; it records completed operations and never
assumes that a failed later operation rolled back earlier infrastructure.
