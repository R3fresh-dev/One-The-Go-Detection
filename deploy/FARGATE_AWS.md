# Deploy OnGo containers to AWS

This is the preferred OnGo deployment process. The frontend, API, workers and
scheduling run as containers on AWS Fargate. AWS provides the private database,
identity, queues, encryption and storage. The target is account
**738470137867**, primary **us-east-1**, backup/recovery **us-west-2**,
environment **fargate-development**, and a
**$100 monthly budget** with notifications to **jacobtyrawa@mail.com**.
Resource selection is scoped to OnGo ownership and this account/region.
Company Generation is outside this deployment's target.

Ohio's previous single-region estimate does not qualify this regional layout.
The deployment cost admission must include East 1 application resources,
West 2 backup resources and retained Ohio resources within the **$100/month**
planning budget. Database activity, retained versions, copy traffic and storage
can change the actual cost. Cost plans do not establish measured bills or throughput.
The $100 AWS Budget provides alerts; it is not a spending cap. The account must
have an active AWS Paid Plan to use the retained Aurora configuration.
The regional budget uses the `project=one-the-go-detection` cost-allocation tag
across regions. Its configured filter does not prove the billing tag is active
or that earlier charges are already covered; verify those billing prerequisites.

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
The credentials action and target check use the primary region from the
authenticated source configuration. There is no dispatch input that overrides
the region independently of the reviewed source.

## Run the preferred deployment workflow

1. Review the change and wait for all 14 mandatory application jobs to pass for its
   exact revision before merging. Then wait for **Required application gates**
   to pass on the exact resulting `main` commit. A pull-request-only success does
   not admit a cloud deployment.
2. Manually run **Deploy OnGo containers to AWS** from the current default
   `main`. The workflow rejects a feature branch, stale main revision, dirty
   source, failed or unfinished latest qualifying gate run, missing aggregate
   evidence, or an over-budget plan before configuring AWS credentials.
3. Set `establish_new=true` only for the first empty OnGo deletion journal.
   Routine deployments leave it false. It is not a journal reset option.
4. For the first East 1 deployment, explicitly set `establish_new=true` and leave
   `recovery_run_id`, `continue_uninitialized_run_id` and
   `previous_continuation_run_id` empty. Ohio's historical receipts cannot
   authorize an import or journal initialization in another region.
5. Wait for the deployment and health verification to finish. Use the frontend,
   API and CloudWatch dashboard URLs recorded in the successful receipt and
   workflow summary. Confirm the SNS subscription through its email link.

The workflow creates an ignored `.local/fargateconfig/fargate.json` from the
reviewed example, with `releaseId` bound to its actual full source commit. It
calls `deploy/fargate.py plan` and then `deploy/fargate.py deploy`; the CLI owns
the image builds, resource adoption, stopped runtime maintenance, frontend image
publication, activation and actual health checks. Deployments for the same
development account are serialized across regions, and an in-progress attempt
is not cancelled
by a second dispatch.

The old **Deploy serverless development to AWS** workflow is a legacy deployment
record. Use the OnGo Fargate workflow for new work. The legacy run is referenced
only as verified historical Ohio recovery evidence. Keep that route disabled.

The example configuration requires `region=us-east-1` and
`backupRegion=us-west-2`. West 2 is not admitted as an application deployment
target. The legacy eight-field configuration remains valid only for Ohio and
has no `backupRegion`; legacy recovery and continuation inputs are rejected
before credentials for the East 1 configuration.

## Regional continuity and retained Ohio resources

East 1 establishes new regional resources and a new empty journal. Existing
Ohio resource ARNs, encryption keys, Cognito users, journal versions and SQL
continuity records keep their original identities. Changing a region string
does not migrate those identities. Ohio remains stopped and retained for the
current regional move; this workflow does not start its database or repair its
detached network resources.

Stopping Aurora is temporary: AWS automatically restarts a stopped cluster
after seven days. Storage, backups, keys, secrets, images and other retained
resources remain billable while compute is stopped. The regional cost plan
must include these charges and the automatic restart exposure until a
separately authorized maintenance or decommission action removes it.
See [Aurora stop/start behavior](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-cluster-stop-start.html).

West 2 is a backup/recovery destination without running application or database
compute or a standby network. The regional backup stack
`otgd-fargate-development-us-west-2-recovery` contains a dedicated symmetric KMS
key and alias, an encrypted backup vault and five private versioned S3 replica
buckets. Full-version replication covers the primary artifacts, exports,
deletion journal, web authority and deployment archive. The journal replica
retains at least 90 days of Object Lock protection. Daily Aurora AWS Backup
snapshots retain two days in East 1 and seven days of copied snapshots in West 2.
The deployment also creates and verifies one initial release-bound database
backup and West 2 copy, without waiting for the next daily schedule. Its
protected journal binds the actual job IDs, recovery points, database identity,
encryption keys and retention lifecycle; retries reconcile the admitted intent.
Aurora copies use warm snapshot storage; "cold recovery" describes the absence
of running compute. Ohio is excluded from this new backup selection.
Health-data and journal objects replicate under the verified West 2 KMS key.
Web assets and deployment archives preserve their source SSE-S3 (`AES256`)
encryption during replication, independently of the replica bucket's KMS
default. See [replication encryption behavior](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication-config-for-kms-objects.html).
The primary tombstone secret uses an encrypted West 2 replica; its actual
replication status must be in sync without exposing the secret value.

S3 replication does not propagate deletion of a specific source object version.
Artifact and export erasure therefore includes permanent deletion of the
corresponding West 2 versions and verified completion. Replicated delete markers
alone do not establish erasure. Journal copies keep their independent retention.
See [S3 replication behavior](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication-what-is-isnot-replicated.html).

Copying backup data does not establish a working standby, a recovery
time objective or a successful restore. Regional activation requires a
separately reviewed manual recovery contract and live verification of keys,
journal continuity, deletion replay and the restored application. Keep the
original journal bytes and Ohio authority unchanged. Automated West 2
activation and journal rebinding are unsupported. A configured backup plan or
replication rule does not prove that its first copy or a restore has completed.
The credential-free `regional-backup-configuration.json` records configuration
before journal initialization, and `regional-backup-initial-copy.json` records
the bounded initial database-copy intent and outcome. The final
`regional-backup.json` distinguishes copies pending from observed completed
Aurora copies, exact S3 replica versions, the established journal control
version's replica and synchronized secret replication. These receipts do not
prove a restore or authorize regional activation.

## Preserve the interrupted deployment's resources

The following recovery route is retained for the Ohio target only; it is not
used by the fresh East 1 deployment. Recovery uses the protected
`initial-recovery.json` from the failed trusted
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
  --account 738470137867 --region us-east-1 --profile YOUR_EXISTING_PROFILE
uv run --project services/api python deploy/fargate.py deploy \
  --config .local/fargateconfig/fargate.json \
  --gate-evidence .local/fargateconfig/gates/gates.json \
  --profile YOUR_EXISTING_PROFILE
uv run --project services/api python deploy/fargate.py health \
  --config .local/fargateconfig/fargate.json \
  --profile YOUR_EXISTING_PROFILE
```

Prepare the ignored configuration with the exact full reviewed commit, and
download its eligible aggregate `gates.json` first. For the fresh East 1
deployment, add only `--establish-new`; leave all recovery arguments absent.
For the separate historical Ohio verified adoption route, add `--establish-new`
and the separately validated
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
