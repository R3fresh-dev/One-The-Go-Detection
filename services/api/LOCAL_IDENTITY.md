# Fictional local issuer

`otgd.local_identity:app` serves the local engineering OAuth flow. It starts only
with `OTGD_ENVIRONMENT=local`; QA and production use their configured Cognito
issuer. The named `fixture_a`, `fixture_b` and twenty `perf_01`–`perf_20` subjects
contain fictional data. This service does not enroll actual people or grant
research permissions.

Start it through the [local platform scripts](../../infra/README.md), together
with PostgreSQL, the API, worker and LocalStack. The identity origin and callback
allowlist must agree with the public host selected by `local-platform.py prepare`.
Keep the generated local signing-key directory and PostgreSQL data volume;
replacing identity or retained journal configuration is not a recovery procedure.

## Browser authorization

`GET /oauth2/authorize` checks the exact client, callback, response type, bounded
state and S256 PKCE challenge. It creates a five-minute authorization record and
sets a five-minute, HTTP-only, SameSite=Lax cookie scoped to `/oauth2/authorize`.
HTTPS identity origins also receive the Secure flag. The record contains the
cookie's SHA-256 digest, not the cookie secret.

The chooser's `POST /oauth2/authorize` requires the same browser cookie, the
unconsumed authorization identifier and an `Origin` exactly equal to the
configured identity origin without its trailing slash. Missing, `null`, foreign
or mismatched session requests fail. Each successful selection creates one
two-minute, single-use code. Tokens and codes are not logged or stored as raw
secrets. Scripted clients must preserve the GET cookie and send the exact Origin
on the chooser POST; [app_flow.py](../../infra/local/app_flow.py) implements this
for the live application and performance gates.

## Families, revocation and deletion

RS256 access tokens last fifteen minutes. The initial selection establishes a
thirty-day absolute refresh-family deadline. Rotation issues a fresh opaque
refresh token but retains that deadline and the original authentication time.
Reusing a spent refresh token revokes the entire family, including its winning
rotation and access tokens issued before the account was first provisioned.
Revocation and API logout also prevent subsequent refresh. The API requires a
live, subject-bound local family before account creation and checks it again
under identity serialization, so a delayed read cannot provision a revoked
subject. Narrow existing logout/deletion receipt exceptions retain their normal
behavior; ordinary API access does not bypass revocation.

Existing account operations lock the account before the fictional identity,
family and grant. First account provisioning serializes on the identity because
an absent account row cannot provide a row lock. Locked ORM reads refresh cached
values after waiting. Account deletion disables the allowlisted fictional
identity in the same transaction that publishes the deleted account state;
failure rolls back both changes. All-data deletion leaves the fictional identity
available for a later explicitly acknowledged generation.

Issuance and revocation clean up at most 128 expired transient records in a
separate transaction with PostgreSQL `SKIP LOCKED`. Persistent disabled identity
records are excluded. Expired family state remains for the possible final access
token lifetime, then can be reclaimed. These limits bound one cleanup operation;
they do not turn this engineering issuer into a managed production identity
service. Existing legacy families without the new durable family state require
a fresh local sign-in after upgrading; no data-volume reset is required.

## Key custody

The generated RSA private key uses a new, exclusive file with mode `0600`.
Subsequent reads use `O_NOFOLLOW` and nonblocking opening, require a regular file
owned by the process with one link and no group/other permissions, and read at
most 16 KiB. File metadata must remain unchanged during the read. RSA keys must
be 2048–4096 bits with exponent 65537. Symlinks, FIFOs, hardlinks, public file
modes, foreign ownership, oversized data, EC keys and weak RSA keys fail closed.
This is local file custody; no production key-management claim is made.

## Verification

The HTTP/security suite exercises actual RSA signing, cookies, PKCE and SQL
state. The explicitly marked PostgreSQL tests also exercise simultaneous refresh
reuse, delayed pre-provision admission and a refresh blocked on the account
deletion transaction. Run only against an explicitly disposable database:

```bash
OTGD_DISPOSABLE_DATABASE=true OTGD_DATABASE_URL="$DISPOSABLE_TEST_DATABASE_URL" \
  uv run --project services/api pytest services/api/tests/test_local_identity.py \
  services/api/tests/test_local_oauth_security.py --junitxml=reports/local-oauth-postgres.xml
```

The test fixture resets that disposable schema. Its API infrastructure remains
in test mode; it does not substitute for the independent live LocalStack/journal,
Docker health, API and performance gates required before merge.
