# PostgreSQL and independent journal continuity

The database is bound to the independently versioned `control/established.json` marker. Its original canonical control body retains `schema_version`, environment, UTC establishment time, 90-day minimum retention and 35-day maximum recovery age. SystemState `journal_establishment` pins environment, AWS region, journal bucket, control key, exact non-null VersionId and SHA256. Runtime SQL identities can read this anchor and cannot create or change it.

Resource initialization connects as the maintenance database identity and checks continuity **before creating any missing bucket**. If the database already has a binding, a missing marker, replaced version, different bytes or different location stops initialization. Existing accounts in an unbound database also stop automatic adoption. Only a confirmed empty first deployment can establish a new marker and have the migration bind it. API/readiness admission rechecks the actual current and exact pinned marker; local deployments have this barrier even without opting into full recovery activation. QA/prod additionally require independently retained deletion/recovery authority and verified Object Lock according to their recovery contract.

An existing pre-binding deployment can be upgraded by an administrator who has independently verified the original retained journal receipt. Supply both `OTGD_JOURNAL_ESTABLISHMENT_VERSION_ID` and `OTGD_JOURNAL_ESTABLISHMENT_SHA256` through the protected migration environment. They are proof inputs, never an instruction to recreate a missing journal. Both must match the current independently retained object. Resource preflight may verify this receipt without changing SQL; only the migration writes the binding. Subsequent runs compare the established binding and cannot replace it with another receipt.

Inspect the original marker without exposing application secrets:

```sh
aws s3api head-object --bucket "$REVIEWED_JOURNAL_BUCKET" --key control/established.json \
  --query '{VersionId:VersionId,ContentLength:ContentLength}'
aws s3api get-object --bucket "$REVIEWED_JOURNAL_BUCKET" --key control/established.json \
  --version-id "$REVIEWED_MARKER_VERSION" /tmp/reviewed-established.json
sha256sum /tmp/reviewed-established.json
```

For local commands only, supply the configured LocalStack endpoint to those AWS CLI reads. Verify the canonical bytes, original independent provenance, environment, region, bucket and version before exporting the two proof inputs. A fresh replacement marker in the same bucket is not sufficient provenance. Compose forwards these inputs to `resource-init` and `migrate`; the latter retains the binding transactionally with the additive migrations. Keep the migration-role password in the ignored environment file and do not paste it into logs or shell examples. Clear optional proof inputs after a successful reviewed migration; repeat startup uses the SQL binding.

When continuity fails, preserve both the PostgreSQL and storage volumes for investigation. Do not run reset, regenerate a marker, change an existing binding or downgrade the check to resume data admission. Reconcile the independently retained journal and complete the authorized restore/activation process. If the disposable community emulator lost its objects, use a separate empty fictional project for further UI tests while preserving the failed deployment.

## Upgrade a retained local runtime

Use this sequence for the canonical `otgd-local` project after reviewing the final image. Its initialization jobs are named `resource-init` and `migrate`. Do not run a full `up`, `down`, `reset`, emulator replacement or volume removal to resolve an upgrade failure. Keep the existing PostgreSQL and LocalStack processes running; the community emulator has no qualified durable journal persistence across restart.

1. Preserve `infra/local/.env`, the tombstone secret, `secrets/identity-key.pem`, both named volumes and the original independently retained control receipt. For a pre-binding database, verify the original marker using the reads above, then supply **both** proof inputs in the protected environment used by Compose. They must match the existing exact current VersionId and canonical bytes. A newly created marker with matching-looking metadata is insufficient. An already bound database compares its established receipt and cannot replace it.
2. Preserve any existing `secrets/capture-signing-key.pem`. If this is the first signing-key migration and there is no bound descriptor, `scripts/local-platform.py prepare` can create the new P256 key once. Its file must be private mode `0600` and owned by the UID that runs API/migration. Reconcile `OTGD_LOCAL_UID`/`OTGD_LOCAL_GID` in an older protected `.env` with the actual key-file owner; do not run preparation under a different owner. Migration records its actual public descriptor, while runtime can only read that anchor. A missing or changed **already bound** key is a recovery incident; generating a replacement cannot repair it.
3. Stop only the three application services and inspect their actual state. Leave the existing database and emulator running:

   ```bash
   docker compose --project-name otgd-local --env-file infra/local/.env \
     -f infra/local/compose.yml stop api identity worker
   ```

4. Build or obtain the reviewed final `otgd-api:local` image separately. Using that image, run resource verification first and the additive migration second, without starting dependencies:

   ```bash
   docker compose --project-name otgd-local --env-file infra/local/.env \
     -f infra/local/compose.yml run --rm --no-deps resource-init
   docker compose --project-name otgd-local --env-file infra/local/.env \
     -f infra/local/compose.yml run --rm --no-deps migrate
   ```

   Require both actual commands to exit zero and retain their nonsecret outcome evidence. Resource preflight verifies retained journal continuity before bucket creation. Migration transactionally binds the journal/public signing descriptor and preserves an existing matching anchor. Either failure leaves application admission closed; do not alter the old anchors to make the command pass.
5. Only after successful maintenance, recreate the application services from that image:

   ```bash
   docker compose --project-name otgd-local --env-file infra/local/.env \
     -f infra/local/compose.yml up --no-build --no-deps --detach --wait \
     --wait-timeout 180 identity api worker
   python scripts/local-platform.py check
   ```

   Inspect all five long-running services' actual health and retain the new one-shot outcomes. `check-canonical-health.py` additionally checks the project's persistent initializer containers; `run --rm` does not update their historical exit evidence, so retain and review the just-executed maintenance outcomes separately during this narrow upgrade. The disposable `check-app` probe deletes Fictional Account A's data and requires its explicit confirmation; do not use it on a retained workspace needing that data.
6. Clear optional receipt-import proof inputs after a successful migration. Subsequent admission uses the pinned SQL anchor and exact retained object. A signing anchor permits verified software capture grants; it does not approve a physical configuration, study or scientific model.

If licensed local persistence was selected, preserve the same reviewed preset and credentials for every command; its actual restart/recovery acceptance remains separate. For QA/prod, use the stopped migration/restore and fresh `verify-admission`/activation sequence in the [operator runbook](../infra/runbooks/OPERATIONS.md), with current exact-source gate evidence and signed production QA approval.

The pinned LocalStack community release still has no qualified persistent S3/SQS snapshot capability. Binding prevents silent reseeding; it does not restore missing data or supply persistence. Licensed local persistence needs its own actual restart/recovery qualification. Isolated continuity tests cover an empty first database, existing unbound accounts, exact administrator receipt import, missing/replaced/same-bytes-new-version markers, malformed/oversized control and unchanged SQL on preflight. No shared-stack restart or actual AWS restore was performed for this change.
