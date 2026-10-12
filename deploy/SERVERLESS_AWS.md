# Repeatable serverless AWS deployment

Target: account **738470137867**, **us-east-2** (Ohio), environment
**serverless-development**, notification address **jacobtyrawa@mail.com**, and
a reviewed monthly estimate no greater than **$50**. The budget is an alert and
admission threshold, not a spending cap. Actual charges depend on usage and on
how long the database remains active.

The serverless path deploys Lambda application functions, Aurora Serverless v2
PostgreSQL, managed queues and identity, S3 storage, the web frontend, and a
CloudWatch health dashboard. AWS generates the HTTPS service addresses. The
database version and zero-capacity auto-pause support must be verified in the
selected region before creating the application stack. A paused database can
add resume latency; periodic work and open connections can affect its ability
to pause. The deployment receipt records observed health, rather than inferring
health from a successful infrastructure update.

## AWS credentials already supplied through GitHub

The repository contains the two secret names the owner confirmed:

- `ACCESS_KEY_ID`
- `SECRET_ACCESS_KEY`

GitHub stores secret names in uppercase; this is the owner-provided
`Secret_access_key` name.

The workflow reads those exact names. It does not rename them or require their
values in chat, a configuration file, source control, or a deployment bundle.
GitHub injects them into the official, commit-pinned AWS credential action after
the reviewed source, required gate evidence, and budget have passed admission.
`AWS_SESSION_TOKEN` is optional and is needed only when the configured key and
secret are temporary credentials. All three values must belong to the same
temporary session when a session token is used.

No additional credentials need to be sent to this chat or configured in this
chat's runtime to use the GitHub workflow. Repository administrators can manage
the values in the repository's Actions secrets settings. Keep their values
private. The credential action and a separate STS check reject an AWS identity
whose account differs from `738470137867`.

The AWS principal needs deployment access for the CloudFormation stack and its
managed resources, including image repositories, Lambda, API delivery, Aurora,
storage, queues, identity, encryption, logs, metrics, alerts, budget notifications,
and networking. Restrict `iam:PassRole` to the roles created for this deployment.
Application roles have separate runtime permissions and do not receive the
deployment keys. A successful account identity check does not prove that every
deployment API is authorized. An authorization failure blocks its stage and
leaves a credential-free recovery journal.

## Deploy through GitHub Actions

1. Review and merge the serverless change only after every mandatory gate passes
   for its exact revision. After merging, wait for **Required application gates**
   to pass on the exact resulting `main` commit. A green pull-request run alone
   does not admit an AWS release.
2. Run **Deploy serverless development to AWS** from `main`. The workflow is
   manually dispatched; it is not a push-triggered deployment. It rejects a
   branch other than the current default `main` revision.
3. Leave `establish_new` false for routine deployments. Set it true only when
   establishing the first empty development deletion journal. It is not a
   recovery or data-reset option.
4. Wait for the workflow to finish. It downloads the most recent qualifying
   exact-source aggregate gate artifact and verifies the actual current GitHub
   job results. A newer failed or unfinished qualifying run blocks deployment;
   an older success cannot substitute for it. Admission occurs before AWS
   credentials are configured, and the deployment CLI checks its gate evidence
   again at the cloud mutation boundaries.
5. Use the verified HTTPS frontend, API, and CloudWatch dashboard URLs in the
   workflow summary and deployment receipt. Confirm the SNS email subscription
   and complete the separate alarm delivery and backup restore checks.

The workflow binds `releaseId` to the actual checked-out commit in the ignored
`.local/serverlessconfig/serverless.json`. It calls the repeatable Python CLI,
which builds the reviewed source into its application images, deploys the AWS
resources, publishes the frontend, and checks actual system health. Runner
Docker and Buildx availability is required. Source archives, container build
directories, credentials, and AWS application logs are not uploaded as workflow
artifacts. The uploaded plan, gate admission proof, deployment receipts, and
stage journals are credential-free.

Concurrent attempts for this account and region are serialized. A failed run is
not evidence of rollback: inspect its stage journal and actual AWS state before
retrying. Do not enable `establish_new` to bypass a continuity failure.

## Repeat the Python process locally

Use a clean checkout of the exact reviewed `main` commit, the locked toolchain,
and an existing AWS SDK profile or IAM Identity Center session. A local AWS
login authenticates that local machine; it does not authenticate the remote
GitHub runner. The GitHub workflow uses the repository secrets described above.

```sh
uv sync --project services/api --locked
uv run --project services/api python deploy/serverless.py plan \
  --config infra/config/serverless.example.json
```

`plan` validates the configuration and reviewed estimate without deploying to
AWS. Prepare an ignored configuration file with `releaseId` set to the full
reviewed commit. Download `gates.json` from that commit's eligible successful
**Required application gates** aggregate run. Then use the existing profile:

```sh
uv run --project services/api python deploy/check_access.py \
  --account 738470137867 --region us-east-2 --profile YOUR_EXISTING_PROFILE
uv run --project services/api python deploy/serverless.py deploy \
  --config .local/serverlessconfig/serverless.json \
  --gate-evidence .local/serverlessconfig/gates/gates.json \
  --profile YOUR_EXISTING_PROFILE
uv run --project services/api python deploy/serverless.py health \
  --config .local/serverlessconfig/serverless.json \
  --profile YOUR_EXISTING_PROFILE
```

Add `--establish-new` only for the first empty journal. Use authorized GitHub
read access for the CLI's live evidence verification. Do not print credential
provider output or add AWS keys to the configuration.

## Evidence and release limits

Successful application gates establish the required repository checks for their
exact source. A successful deployment receipt establishes only the AWS checks
that actually executed for that deployment. Database resume behavior, fresh
CloudWatch measurements, API/frontend transport, restore and alarm delivery
need their own observed evidence. Physical-device qualification and production
promotion remain separate requirements. A workflow file, a local plan, or an
untested dashboard template does not establish a deployed or healthy system.
