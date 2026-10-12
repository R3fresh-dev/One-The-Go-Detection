# Deploy OnGo containers to AWS

This is the preferred OnGo deployment process. The frontend, API, workers and
scheduling run as containers on AWS Fargate. AWS provides the private database,
identity, queues, encryption and storage. The target is account
**738470137867**, **us-east-2**, environment **fargate-development**, and a
**$100 monthly budget** with notifications to **jacobtyrawa@mail.com**.
Resource selection is scoped to OnGo ownership and this account/region.
Company Generation is outside this deployment's target.

The reviewed low-volume estimate is approximately **$62–$66/month** before
credits; the published larger-capacity stress cases are approximately
**$84–$87/month**. These are planning cases, not measured bills or throughput
claims. Database activity, storage and traffic can change the actual cost.
The $100 AWS Budget provides alerts; it is not a spending cap. The account must
have an active AWS Paid Plan to use the retained Aurora configuration.

## Credentials already configured

GitHub Actions uses the existing repository secrets **`ACCESS_KEY_ID`** and
**`SECRET_ACCESS_KEY`**. Do not send their values in chat or add them to the
configuration, source, build arguments, receipts or deployment bundle.
`AWS_SESSION_TOKEN` is optional and is required when these credentials are a
temporary session; all three values must belong to that same session.

The commit-pinned official AWS credential action receives the secrets only after
current-main source admission, successful mandatory gate evidence, the budget
plan and any recovery artifact checks. The action and a separate STS check
reject credentials from another account. No OIDC token permission is granted.

The principal needs deployment access for the OnGo CloudFormation resources,
ECS/Fargate, image repositories, delivery/networking, Aurora, storage, queues,
identity, encryption, monitoring and budget notifications. Restrict
`iam:PassRole` to the deployment's task and execution roles. Application tasks
receive their own runtime role and do not receive the deployment keys.
An account identity check alone does not establish every deployment permission.

## Run the preferred deployment workflow

1. Review the change and wait for all mandatory application gates to pass for its
   exact revision before merging. Then wait for **Required application gates**
   to pass on the exact resulting `main` commit. A pull-request-only success does
   not admit a cloud deployment.
2. Manually run **Deploy OnGo containers to AWS** from the current default
   `main`. The workflow rejects a feature branch, stale main revision, dirty
   source, failed or unfinished latest qualifying gate run, missing aggregate
   evidence, or an over-budget plan before configuring AWS credentials.
3. Set `establish_new=true` only for the first empty OnGo deletion journal.
   Routine deployments leave it false. It is not a journal reset option.
4. For the current adoption of the interrupted initial deployment, retain
   `recovery_run_id=38272959415` and explicitly enable `establish_new`.
   After successful adoption, clear `recovery_run_id` for routine deployments.
5. Wait for the deployment and health verification to finish. Use the frontend,
   API and CloudWatch dashboard URLs recorded in the successful receipt and
   workflow summary. Confirm the SNS subscription through its email link.

The workflow creates an ignored `.local/fargateconfig/fargate.json` from the
reviewed example, with `releaseId` bound to its actual full source commit. It
calls `deploy/fargate.py plan` and then `deploy/fargate.py deploy`; the CLI owns
the image builds, resource adoption, stopped runtime maintenance, frontend image
publication, activation and actual health checks. Deployments for the same
account and region are serialized, and an in-progress attempt is not cancelled
by a second dispatch.

The old **Deploy serverless development to AWS** workflow is a legacy deployment
record. Use the OnGo Fargate workflow for new work. The legacy run is referenced
only as verified recovery evidence.

## Preserve the interrupted deployment's resources

Recovery uses the protected `initial-recovery.json` from the failed trusted
legacy main deployment. Its source ZIP must remain intact: the workflow checks
the run's repository, workflow, event, branch and failure state; identifies one
exact-source, non-expired artifact; downloads the original ZIP; and verifies its
GitHub SHA-256 digest. It extracts only the single bounded recovery journal.
Archive path traversal, duplicate journals and unsupported sizes are rejected.

The Python CLI receives the manifest path, original archive path, run ID and
artifact ID as separate arguments. Its recovery helper independently checks
live GitHub provenance and actual retained AWS state before adoption. A local
JSON claim cannot substitute for the trusted run or authorize a data reset.
Preserve the retained physical resource identifiers and recovery journal if an
operation is interrupted; inspect the actual state before retrying.

Artifacts uploaded by the Fargate workflow contain only credential-free plans,
gate/recovery provenance, deployment receipts and stage/recovery journals. The
legacy ZIP, application logs, source archives and image build directories are
excluded. A failed deployment is not evidence of rollback.

## Repeat the Python process locally

Use a clean checkout of the reviewed source and an existing AWS SDK/SSO profile.
A local SSO login authenticates that machine; the GitHub runner instead uses its
repository secrets.

```sh
uv sync --project services/api --locked
uv run --project services/api python deploy/fargate.py plan \
  --config infra/config/fargate.example.json
uv run --project services/api python deploy/check_access.py \
  --account 738470137867 --region us-east-2 --profile YOUR_EXISTING_PROFILE
uv run --project services/api python deploy/fargate.py deploy \
  --config .local/fargateconfig/fargate.json \
  --gate-evidence .local/fargateconfig/gates/gates.json \
  --profile YOUR_EXISTING_PROFILE
uv run --project services/api python deploy/fargate.py health \
  --config .local/fargateconfig/fargate.json \
  --profile YOUR_EXISTING_PROFILE
```

Prepare the ignored configuration with the exact full reviewed commit, and
download its eligible aggregate `gates.json` first. For the initial verified
adoption, add `--establish-new` and the separately validated
`--recovery-manifest`, `--recovery-archive`, `--recovery-run-id` and
`--recovery-artifact-id` arguments. Keep the original ZIP; do not rebuild it after
extraction. Authorized GitHub read access is required for live gate and artifact
verification. Docker/Buildx and the pinned Node/Python toolchain are required for
the builds. No AWS keys belong in these command arguments.

## What successful deployment evidence means

A successful `fargate_transport_and_health_verified` receipt records the actual
source, frontend/API addresses, CloudWatch dashboard and checks that executed.
Authenticated customer acceptance, actual signed object uploads, alarm delivery,
backup restore, physical-device qualification and production promotion need
their separate evidence. Do not infer these results from a healthy dashboard,
green source gates, successful infrastructure update or cost plan.
