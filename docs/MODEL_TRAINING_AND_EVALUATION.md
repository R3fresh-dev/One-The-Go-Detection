# Offline model training and evaluation

[model_evaluation.py](../tools/model_evaluation.py) implements a bounded, reproducible logistic model workflow for MOD-004/005/006/012/014 and the PRD's independent prediction scorecard. It fits the four prescribed combined-channel configurations, or a separately prespecified HR-only configuration with retained server-interval evidence, and evaluates whole held-out people and their later sessions. It does not collect a cohort, establish clinical ground truth, authorize a study, approve a model or activate inference. No human dataset or scientifically qualified weights are supplied by this repository.

All repository tests use explicitly marked **engineering_synthetic** data. Their numerical performance is evidence that the software computes the prescribed operations, and provides no evidence about cannabis impairment, assay validity or human performance. Real inputs require a qualified prospective protocol, independent endpoint/reference standard, authorized data handling and clinical/statistical review.

## Install and generate exact input contracts

Use the locked API Python environment; the toolkit uses its existing Pydantic, RFC8785 and data-only model schemas. It does not install a second ML framework or execute serialized Python models.

```bash
uv sync --project services/api --locked
uv run --project services/api python tools/model_evaluation.py schemas \
  --output /protected/research/model-input-schemas
```

The new directory contains strict dataset, outcome-blind cohort index and analysis-plan JSON Schemas. Unknown fields are rejected. Inputs must be regular JSON files without duplicate keys or nonfinite numbers, at most 16 MiB. A dataset has at most 2,000 sessions and 1,000 participants, with at most sixteen named predictors per session. Use opaque participant/session references rather than direct identifying information. Keep datasets, predictions and reports in approved protected storage; the evaluation evidence includes endpoint labels and session-level probabilities.

The dataset requires `data_kind` (`engineering_synthetic` or `authorized_research`), a supplied authorization reference, endpoint identity/definition/source, a claimed UTC dataset lock, pinned acquisition/assay/task hashes, and input/feature versions. Each session requires:

- A unique session ID, participant reference, immutable UTC assessment target, actual `capture_completed_at` and separately declared `information_cutoff_at`.
- Acquisition status and retained quality flags.
- Named feature records with `status`, finite `value` or null, `observed_at` and `available_at` or null. Missing, censored and invalid values remain null. Valid values require observation/availability timestamps. Only the engine's existing `FEATURE_CHANNELS` names are accepted; exposure/outcome labels cannot be added as predictors.
- A separate integer endpoint label (0 or 1), endpoint ID/source/assessor references, assessment/availability times and an explicit independent-assessment assertion. Boolean labels, mismatched endpoint sources and observations after the claimed dataset lock are rejected.
- All six stratification dimensions: route, use frequency, co-use/confounding, device, baseline and population. Their bounded categories must already be defined in the analysis. If information is absent, include an explicit prespecified missing category rather than silently excluding the row.

The original physiological target does not move to delayed feature processing or assay delivery. Target ≤ capture completion ≤ information cutoff remains required. Combined-channel plans apply the frozen acquisition-span and post-capture delivery bounds to those timestamps. The explicit HR-only mode preserves the original timestamps and applies its numerical gates to the conservative server interval instead, as described below. Acquisition-channel observations must occur by capture completion; their values must be available by the declared information cutoff. Profile features must be observed and available by the original target. The checks cover unused and invalid-row predictors as well. Cutoffs are supplied under the approved protocol; the tool never chooses them from outcome labels. Independent endpoints remain aligned to the original target.

The toolkit does not derive features from raw streams, convert arbitrary units, replace censored values with zero or invent a personal baseline. Input feature units and construction must already satisfy the pinned `otgd.features.v1` contract and qualified extraction/assay procedures. A missing independent endpoint prevents a complete report rather than silently dropping an unlabelled check.

## Prespecify the analysis

Prepare the analysis JSON under the statistical lead's control before releasing confirmatory outcomes. Required choices include:

| Input | Meaning |
|---|---|
| `dataset_sha256`, `versions`, endpoint ID/definition hash | Exact canonical dataset and scientific input identities; dataset and analysis must agree. |
| `plan_lock_ref`, `independent_endpoint_evidence_ref`, `prespecified_at` | Actual external lock/reference evidence and claimed UTC prespecification time. |
| `seed`, `training_participant_count` | Frozen deterministic whole-person allocation, chosen without test outcomes. |
| `training_cutoff`, `later_session_boundary` | Training observations/labels must be available by the first cutoff; later held-out sessions follow the second boundary. |
| `maximum_endpoint_offset_seconds` | Prespecified acceptable assessment window around the current functional target. No clinical default is supplied. |
| `max_acquisition_span_ms`, `max_delivery_delay_ms` | Combined-channel bounds for target-to-capture duration and capture-to-cutoff delay; HR-only bounds use target-to-server-receipt and original-server-issue-to-cutoff, with reviewed UTC error and outward rounding. |
| `comparator_kind` | Accepted reference standard or prespecified independent comparator; the evidence names sensitivity/specificity or positive/negative percent agreement accordingly. |
| `feature_names`, `feature_limits` | Combined-channel plans require chemistry, an app feature and ECG for the four comparisons. Explicit HR-only plans require exactly `cardiac.heart_rate_bpm` and its raw-HR or personal-delta limits. |
| `iterations`, `learning_rate`, `l2_penalty` | Fixed full-batch ridge logistic fitting parameters; no outcome-based stopping or hyperparameter search. |
| `calibration_id`, `calibration_method` | Named `prespecified_identity` calibration: slope 1, intercept 0. It is not an empirically qualified calibration merely because it is named. |
| `operating_threshold`, `uncertainty_policy` | Frozen classification threshold and optional probability-band abstention, shared by all comparisons. |
| `calibration_bins`, `confidence_level`, `bootstrap_replicates`, `minimum_defined_bootstrap_replicates` | Frozen reliability bins and participant-cluster uncertainty analysis; at least 200 bootstrap draws. |
| `denominator_policy`, `invalid_score_loss` | Required all-session convention and conservative invalid score penalty of 1, described below. |
| `strata` | Frozen allowed categories for every route/use-frequency/co-use/device/baseline/population dimension; unplanned categories fail admission. |

The schema bounds computation and invalid parameter combinations. These bounds are engineering limits, not scientific success criteria. The clinical/statistical leads must choose acceptance limits and justify sample size, cohort coverage, endpoint timing, calibration and uncertainty before qualification. The explicit HR-only mode can fit raw HR or a prespecified personal-baseline delta; the tool does not qualify the baseline, clock, reader or blinded assessment.

## Prespecify HR-only server-interval evidence

This mode requires a separately released runtime policy and independently reviewed retained custody records. It accepts original prototype PPG snapshots from `otgd_esp32_adc_v1` or `otgd_sparkfun_max32664_v1`; it does not add ECG, RMSSD, SpO2, chemistry, physiological onset or waveform cadence authority.

The analysis plan requires these additional fields:

| Field | Required content |
|---|---|
| `cardiac_timing_policy` | Exact runtime `CardiacTimingPolicy`: method `server_issue_to_attestation_receipt_v1`, independently governed `calibration_id`, maximum interval and explicit `allow_baseline_delta`. |
| `cardiac_provenance` | `reviewed_source_bundle_ref` and SHA, `independent_review_ref` and SHA, plus exact `calibration_registry_sha256`, `calibration_scope_sha256`, `qualification_registry_sha256`, `device_registry_sha256` and `configuration_submitted_sha256`. |
| `max_baseline_age_ms` | Required only when `allow_baseline_delta=true`; the conservative maximum age of the separately retained baseline. |

Every row retains `cardiac_evidence` containing the complete unchanged `snapshot` and `snapshot_sha256`, typed runtime `authority` (`CardiacAuthority`) and `authority_sha256`, `source_bundle_ref` and `source_bundle_sha256`, and explicit `baseline_snapshot`/`baseline_snapshot_sha256` (null for a population/raw-HR plan). The row's session, subject, target, completion time and quality flags must match that original snapshot. Its sole predictor is derived from the original HR, or from current HR minus the explicit baseline's original HR. Predictor observation retains the original component end timestamp; availability cannot precede the original server receipt. Mixed-channel predictor rows are refused.

The retained authority includes the original server issue and signature-verified attestation receipt, immutable record/manifest hashes, exact device/key/configuration/calibration scope, reviewed UTC error and the preserved flags. SDK evidence also requires signed monotonic acquisition duration and the independently reviewed rate-error bound; ADC evidence requires both fields null. The toolkit uses the same runtime validators and exact Decimal/outward-rounding arithmetic at each row's historical `information_cutoff_at`. Interval width includes twice the UTC error; acquisition and delivery bounds retain that uncertainty. It preserves unqualified client timestamps and clock flags rather than replacing them with zero uncertainty. Only the exact adapter's known preserved flags may receive this numerical exception; fault, cleaned or changed flags remain ineligible.

A personalized row must include its explicit earlier original snapshot and typed baseline interval. Both snapshots must have the same participant, study, protocol and reviewed device/key/configuration/calibration scope; reused capture identities, an absent or arbitrary inferred prior row, overlapping intervals and excessive conservative age are refused. Baseline evidence bypasses only current-delivery freshness. Its interval, signed duration, scope and historical age remain checked.

The canonical cohort custody inventory binds the plan, all dataset rows (including rejected and excluded rows), source/review references and hashes, original snapshot/authority hashes and captured-session manifest hashes. The report's `cardiac_evidence.evidence_manifest_sha256` hashes this complete inventory; it is distinct from each runtime interval's individual `evidence_manifest_sha256`. The inventory explicitly states that signatures, registry release and independent review are **not authenticated by the tool**. Editable JSON and consistent hashes cannot authenticate those retained records or their principals; independent custody/review verification and current runtime governance remain required.

## Run the distinct custodian, freeze, training and evaluation stages

The custodian creates a canonical index containing identities, dates and hashes, without endpoint values or feature values:

```bash
uv run --project services/api python tools/model_evaluation.py index \
  --dataset /protected/research/locked-dataset.json \
  --output /protected/research/cohort-index.json
```

Use the actual index's `dataset_sha256` in the independently frozen analysis plan. `freeze` accepts only that outcome-blind index and the analysis plan; it does not receive the full dataset:

```bash
uv run --project services/api python tools/model_evaluation.py freeze \
  --index /protected/research/cohort-index.json \
  --analysis /protected/research/analysis-plan.json \
  --output /protected/research/split-plan.json
```

Participant assignment ranks SHA-256 of RFC8785 `[seed, participant_ref]`; the first prespecified count is training. It uses no labels or predictor values. Every row is enumerated exactly once in training, confirmatory, later sessions or the explicit exclusion list. Post-cutoff rows from training participants remain recorded as excluded from this held-out design. A later held-out session requires an earlier held-out session from the same person; train/evaluation participant overlap is forbidden. The training/confirmatory/later partitions must all exist.

Then train and evaluate in new protected directories:

```bash
uv run --project services/api python tools/model_evaluation.py train \
  --dataset /protected/research/locked-dataset.json \
  --analysis /protected/research/analysis-plan.json \
  --split /protected/research/split-plan.json \
  --output /protected/research/training-attempt-1

uv run --project services/api python tools/model_evaluation.py evaluate \
  --dataset /protected/research/locked-dataset.json \
  --analysis /protected/research/analysis-plan.json \
  --split /protected/research/split-plan.json \
  --training-directory /protected/research/training-attempt-1 \
  --output /protected/research/evaluation-attempt-1

uv run --project services/api python tools/model_evaluation.py verify \
  --dataset /protected/research/locked-dataset.json \
  --analysis /protected/research/analysis-plan.json \
  --split /protected/research/split-plan.json \
  --training-directory /protected/research/training-attempt-1 \
  --evaluation-directory /protected/research/evaluation-attempt-1
```

Only valid, complete, in-range training rows enter any fit. All variants use the same eligible training rows; rejected training rows retain explicit reasons. Means and population standard deviations use those rows alone; constant features have scale 1. No imputation, test-derived preprocessing, feature selection, calibration fitting or threshold optimization occurs. Fixed full-batch gradient descent starts with zero coefficients/intercept and applies the prespecified ridge penalty.

Combined-channel plans produce the four canonical `logistic_linear_v1` artifacts `chemical_only`, `app_only`, `combined` and `ecg_removed`. An explicit HR-only plan produces only `cardiac_hr_only.artifact.json`, with the single runtime HR feature. Both modes use the same commands above. Artifacts conform to the existing data-only `Artifact` schema, contain no executable code and carry the training time. `training.json` binds their hashes to the exact dataset, analysis, split and eligible/rejected rows; HR-only receipts additionally bind the complete cohort custody inventory. It distinguishes `dataset_custody_locked_at` from `pipeline_locked_at`: dataset custody lock ≤ training ≤ pipeline lock ≤ evaluation. Neither timestamp constitutes independently authentic historical evidence by itself. Later evaluation uses the same frozen models and policies. Each evaluation cohort must contain both endpoint classes and at least two whole held-out participants for cluster intervals.

`evaluate` independently re-fits the exact deterministic training specification before accepting supplied artifacts and its receipt. `verify` re-fits and reproduces the full report/evidence using the stored execution timestamps. Changes to weights, rows, scientific versions, thresholds, training receipts, reports or evidence are refused unless the new inputs produce a new coherent attempt. Identical frozen inputs and recorded timestamps reproduce identical RFC8785 bytes on the supported locked Python environment. Fresh execution timestamps distinguish new CLI attempts.

Output directories are created with mode 0700 and files with mode 0600, never overwritten. Keep their parent storage/access controls appropriately protected. A failed attempt may leave partial private files; only a successful full `verify` establishes internal reproducibility. CLI success reports only digests/status, not participant records. Retain original inputs and all output files together.

## Interpret denominators, calibration and uncertainty

Every variant evaluates the same frozen session IDs and endpoint labels. Missing/out-of-range predictors and acquisition failures yield `invalid` with null probability; uncertainty-band rows retain their scientific offline score and are `abstained`, with no classification. Neither category disappears from the positive/negative denominator.

Sensitivity is successfully classified positives divided by **all** endpoint-positive rows; specificity is successfully classified negatives divided by **all** endpoint-negative rows. Invalid and abstained sessions count as unsuccessful classifications in their respective class. These are operational all-session rates; they must not be relabeled as complete-case diagnostic rates. The report retains total/valid/invalid/abstained/positive/negative counts and reason frequencies.

The engine schema's fixed rate fields are interpreted as positive/negative percent agreement when the frozen plan declares an independent comparator rather than an accepted reference standard. The evidence records these semantic labels. PPV and NPV use classified-positive and classified-negative denominators, respectively, because invalid/abstained rows have no classification. Their observed locked-cohort prevalence, decision/probability coverage, full-row failures and effective bootstrap counts remain explicit. These values are conditional on classified checks and observed cohort prevalence; case-control or restricted cohorts do not establish target-population predictive values. Undefined values/intervals remain null instead of becoming zero or a fictitious certainty.

The engine report's `brier` and `calibration_error` fields use prespecified failure-penalized, all-session summaries: valid probabilities contribute squared error/reliability-bin error, invalid rows contribute penalty 1, and normalization uses all rows. Abstained valid probabilities remain included. The evidence separately reports eligible-only Brier and ordinary eligible-only binned calibration error (null if no valid probabilities), plus each bin's count, mean probability and observed fraction. The failure-penalized values are operational composites and must not be presented as ordinary complete-case calibration statistics.

Sensitivity/specificity intervals resample **participants**, retaining all their sessions and invalid/abstained outcomes. A draw lacking one endpoint class has an undefined corresponding ratio; that ratio alone is omitted, its effective draw count is reported, and the prespecified minimum is enforced. The named method is a participant-cluster percentile bootstrap, not an exact small-sample guarantee. All variants use identical cluster draws. Paired combined-minus-variant score differences and their cluster intervals quantify the matched comparisons; negative values favor combined under the declared failure-penalized score. No numerical clinical pass threshold or population generalization claim is inferred.

Every prespecified subgroup appears for every configured variant and both evaluation cohorts. Its session IDs/counts reconcile to the aggregate for each dimension, including invalid and abstained checks. Empty, single-class or small-participant categories retain counts and explicit unestimable reasons; unsupported rates/cluster intervals remain null. These limitations are reviewable findings, not permission to pool or drop strata after observing results. Predictive-value intervals use the same participant-cluster approach and retain their own defined-draw counts.

`evaluation-report.json` conforms to the current `EvaluationReport` schema and binds the selected primary artifact, dataset and plans. HR-only reports explicitly declare `analysis_scope=cardiac_hr_only`, exactly one `cardiac_hr_only` ablation entry and seven policy/scope/inventory SHA bindings; they do not invent chemistry/ECG comparisons. Their evidence marks paired comparisons as inapplicable and retains original row flags and provenance hashes. Combined-channel reports keep all four comparisons. `evaluation-evidence.json` additionally binds every artifact, training/report hashes, tool source hash, later-session metrics, raw evaluation-row accounting, calibration details and uncertainty policy. Reports are explicitly **unvalidated**, with `authority_granted=false` and `clinical_success_claimed=false`.

## External evidence and release boundary

The toolkit verifies byte/content bindings, deterministic calculations, timestamp consistency, participant separation and the declared temporal/denominator rules. It cannot prove that a supplied historical timestamp is authentic, that an assessor was truly independent, that a researcher did not see held-out outcomes earlier, or that an authorization reference represents a real approval. The evidence explicitly marks those assertions as unverified. Retain independently controlled, immutable/signed plan locks and dataset custody/access records; reviewers must check them alongside protocol, endpoint, cohort/device strata, assay compatibility, acquisition quality, calibration and adequate uncertainty evidence.

To consider a model for research use, publish its canonical artifact to the separately governed pinned model namespace, retain all supplied evidence, create the actual registry submission and pass independent operator review/release. The registry's authorization/cohort/policy gates remain required, and synthetic data cannot establish scientific approval. This offline tool has no database, AWS or application activation path and does not alter the current measurement-only release boundary.
