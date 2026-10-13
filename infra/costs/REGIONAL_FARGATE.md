# East 1 application, West 2 cold recovery and retained Ohio costs

The owner-selected planning budget is **$100/month** for OnGo. These amounts
use actual official AWS price-list evidence retrieved on 2026-10-13, before
shared free tiers, credits, discounts and taxes. They are planning amounts, not
measured bills or an enforced spending limit.

| Monthly users | East 1 selected | Cold backup | Retained Ohio | Combined selected | Combined 1 ACU stress |
|---:|---:|---:|---:|---:|---:|
| 0 | $62.75 | $5.10 | $5.77 | $73.62 | $92.93 |
| 10 | $65.61 | $5.24 | $5.77 | $76.62 | $97.91 |
| 100 | $91.54 | $6.47 | $5.77 | $103.78 | $142.92 |

The admitted workloads remain zero or ten monthly users. The larger scenario
is shown for comparison and exceeds the budget. The primary 730-hour service,
180-second workers, 900-second privacy sweeps, database awake-time allowance,
0.5 average active ACU and configured maximum **1 ACU** are unchanged. Regional
rates reprice those original quantities; the capacity stress is not reduced.

At ten users, the $5.24 backup allowance includes:

- Seven full 10.1 GB Aurora recovery points in West 2: **$1.48/month**.
  Two full source recovery points receive another **$0.42** reserve, without
  removing the existing primary backup allowance or assuming free coverage.
- One West 2 CMK and the replicated tombstone secret: **$1.40/month**, plus
  encryption and secret requests. No West 2 application/database compute,
  network, warm standby or multi-region signing key is selected.
- All five primary S3 buckets' current and noncurrent replica bytes, replication
  PUTs, replica read/permanent-erasure verification requests and source reads.
  The source/destination KMS requests are both charged. Journal authority keeps
  its 90-day COMPLIANCE minimum; artifact/export replicas require permanent
  version erasure before privacy completion. ECR images and Git source remain
  retained in the primary region; this plan does not claim West ECR replication.
- First full database/S3 copies, followed by **planned, unmeasured 1 GB/day
  changed-database and 1 GB/day S3 replication allowances**. At ten users this
  prices 71.3 GB of East 1 to West 2 transfer at the verified **$0.02/GB** rate.
  Aurora incremental copies can avoid retransferring unchanged blocks; the
  assumptions are not measured byte counts or enforced maxima.

The retained Ohio reserve includes 10 GB database storage, 10 GB backup
storage, all three original KMS keys and managed secrets, 3 GB ECR images,
1 GB logs and 1.1 GB versioned S3 authority/evidence: **$5.77/month**. Its
database compute is modeled as stopped. [Aurora automatically restarts after
seven days](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-cluster-stop-start.html);
future zero compute is not guaranteed and restart charges are outside the
stopped-state case. No Ohio resource, key, journal version or continuity binding
is removed by this model. Actual decommission requires its separate review.

If each daily database copy transfers the whole 10.1 GB again, the unchanged
ten-user capacity stress rises to **$103.37/month**, which fails the $100 plan.
This sensitivity is preserved in the machine-readable estimate. Changed-byte
growth above the daily allowances, copy retries/full-copy fallback, Ohio
restart, more retained versions or recovery exercises require immediate cost
review and a revised estimate. Budget alerts do not prevent these charges.

The single East 1 budget uses the exact `project=one-the-go-detection` tag filter
across East 1, West 2 and retained Ohio. Company Generation is outside that
scope. Configuring this filter does **not** establish actual cost-allocation
tag activation, historical coverage or that billing/tag propagation lag has
cleared. Runtime budget evidence reports that distinction.

The source files are [regional-fargate-estimate.json](regional-fargate-estimate.json),
[regional-fargate-price-evidence.json](regional-fargate-price-evidence.json) and
[regional-price-list-evidence.json](regional-price-list-evidence.json). Each
selected rate retains its official product attributes, region, SKU, rate code,
unit, actual retrieval timestamp and full-offer SHA256. The global catalog host
`pricing.us-east-1.amazonaws.com` does not identify the charged region; product
region/direction attributes do. Global CloudFront charges are counted once.

Recompute from captured official evidence with
[build_regional_fargate_estimate.py](build_regional_fargate_estimate.py). It has
no network calls and does not refresh evidence timestamps. Admission verifies
the committed price snapshot, all primary/backup/retained quantities, regional
bindings, arithmetic and both selected/stress totals. Pricing evidence does
not qualify copy readiness, achieved RPO/RTO, a restore or customer acceptance.
