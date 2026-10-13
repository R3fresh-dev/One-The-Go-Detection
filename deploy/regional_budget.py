"""Pure admission for the reviewed East 1 / West 2 / retained Ohio cost plan."""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
import math
from pathlib import Path
import re
from urllib.parse import urlsplit

from deploy.provenance import Gate, bounded_json, sha256

ROOT = Path(__file__).resolve().parents[1]
REGIONAL_SCOPE = {"primary": "us-east-1", "backup": "us-west-2", "retained_legacy": ["us-east-2"]}
BASE_MODEL = ROOT / "infra/costs/fargate-estimate.json"
PRICE_EVIDENCE = ROOT / "infra/costs/regional-fargate-price-evidence.json"
BACKUP_ASSUMPTIONS = {
    "destination_compute_count": 0, "destination_kms_keys": 1,
    "destination_tombstone_secrets": 1, "replicated_versioned_buckets": 5,
    "journal_compliance_retention_days": 90, "snapshot_interval_hours": 24,
    "snapshot_source_retention_days": 2, "snapshot_destination_retention_days": 7,
    "snapshot_copies_per_planning_month": 30, "initial_full_copy_included": True,
    "replica_permanent_deletion_verification_required": True,
    "transparent_regional_failover_supported": False,
    "changed_bytes_measured": False, "changed_bytes_are_enforced_maxima": False,
    "source_snapshot_costs_reserved_separately": True,
}
RETAINED_ASSUMPTIONS = {
    "region": "us-east-2", "database_storage_gb": 10, "backup_storage_gb": 10,
    "kms_keys": 3, "secrets": 3, "ecr_storage_gb": 3,
    "log_storage_gb": 1, "s3_versioned_storage_gb": 1.1,
    "database_compute_state": "stopped", "automatic_restart_after_days": 7,
    "permanent_zero_compute_guaranteed": False, "decommission_executed": False,
}


def _number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def _money(value):
    return Decimal(str(value)).quantize(Decimal(".01"), rounding=ROUND_HALF_UP)


def _utc(value):
    if not isinstance(value, str):
        raise Gate("Regional prices require actual UTC retrieval timestamps")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise Gate("Regional prices require actual UTC retrieval timestamps") from None
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise Gate("Regional prices require actual UTC retrieval timestamps")
    return parsed


def additional_lines(users, assumptions):
    """Priced quantities; these are planning allowances, never measured bytes."""
    if (not isinstance(assumptions, dict)
            or any(assumptions.get(key) != value for key, value in BACKUP_ASSUMPTIONS.items())):
        raise Gate("Backup prices must cover the complete reviewed cold recovery resources")
    db_changed = assumptions.get("database_changed_gb_per_day")
    s3_changed = assumptions.get("s3_changed_gb_per_day")
    if not all(_number(value) and value >= 1 for value in (db_changed, s3_changed)):
        raise Gate("Use an explicit conservative daily changed-byte allowance")
    database_gb = 10 + users * .01
    versioned_s3_gb = 1.1 + users * .01
    puts = 1000 + users * 64
    transfer = database_gb + versioned_s3_gb + 30 * (db_changed + s3_changed)
    return [
        ("backup", "us-east-1", "East 1 two full source recovery points reserve", "primary_aurora_excess_backup_gb_month", 2 * database_gb),
        ("backup", "us-west-2", "West 2 seven full daily Aurora recovery points", "west2_aurora_backup_gb_month", 7 * database_gb),
        ("backup", "us-west-2", "West 2 five buckets current/noncurrent version storage", "west2_s3_storage_gb_month", versioned_s3_gb),
        ("backup", "us-west-2", "West 2 version replication and permanent-erasure request allowance", "west2_s3_put_request", puts * 30),
        ("backup", "us-west-2", "West 2 replica version/read/erasure verification requests", "west2_s3_get_request", puts * 30),
        ("backup", "us-west-2", "West 2 cold backup and replica CMK", "west2_kms_key_month", 1),
        ("backup", "us-west-2", "West 2 encryption requests", "west2_kms_symmetric_request", 30000),
        ("backup", "us-west-2", "West 2 tombstone secret replica", "west2_secret_month", 1),
        ("backup", "us-west-2", "West 2 secret replication/read allowance", "west2_secret_request", 1000),
        ("backup", "us-east-1", "East 1 source replica reads", "primary_s3_get_request", puts * 30),
        ("backup", "us-east-1", "East 1 source backup encryption requests", "primary_kms_symmetric_request", 30000),
        ("backup", "us-east-1", "East 1 to West 2 initial and changed backup bytes", "east1_to_west2_transfer_gb", transfer),
        ("retained_legacy", "us-east-2", "Retained Ohio stopped Aurora storage", "ohio_aurora_storage_gb_month", 10),
        ("retained_legacy", "us-east-2", "Retained Ohio backup storage", "ohio_aurora_backup_gb_month", 10),
        ("retained_legacy", "us-east-2", "Retained Ohio three original keys", "ohio_kms_key_month", 3),
        ("retained_legacy", "us-east-2", "Retained Ohio three managed secrets", "ohio_secret_month", 3),
        ("retained_legacy", "us-east-2", "Retained Ohio immutable software", "ohio_ecr_storage_gb_month", 3),
        ("retained_legacy", "us-east-2", "Retained Ohio log storage", "ohio_log_storage_gb_month", 1),
        ("retained_legacy", "us-east-2", "Retained Ohio versioned S3 authority/evidence", "ohio_s3_storage_gb_month", 1.1),
    ]


def _rate(rate, region, now):
    if (not isinstance(rate, dict) or not _number(rate.get("usd")) or rate["usd"] <= 0
            or any(not isinstance(rate.get(key), str) or not rate[key]
                   for key in ("unit", "source", "sku", "rate_code", "service"))
            or not re.fullmatch("[0-9a-f]{64}", rate.get("offer_sha256", ""))
            or rate.get("region") != region or not isinstance(rate.get("attributes"), dict)):
        raise Gate("Each regional line needs exact official regional price evidence")
    uri = urlsplit(rate["source"])
    catalog_service = "AmazonSNS" if rate["service"] == "AmazonSNS-email" else rate["service"]
    if (uri.scheme != "https" or uri.netloc != "pricing.us-east-1.amazonaws.com"
            or uri.query or uri.fragment or not uri.path.startswith("/offers/v1.0/aws/" + catalog_service + "/current/")):
        raise Gate("Regional rates must reference the official service price catalog")
    attrs = rate["attributes"]
    if region == "global":
        if not ((rate["service"] == "AmazonCloudFront" and attrs.get("usagetype") in {
                    "US-Requests-Tier2-HTTPS", "US-DataTransfer-Out-Bytes", "US-DataTransfer-Out-OBytes",
                    "Executions-CloudFrontFunctions", "Invalidations"})
                or (rate["service"] == "AmazonCloudWatch" and attrs.get("group") == "Dashboard")):
            raise Gate("Only reviewed CloudFront and dashboard costs are global")
    elif rate["service"] == "AWSDataTransfer":
        intra = attrs.get("transferType") == "IntraRegion" and attrs.get("toRegionCode") == region
        backup = attrs.get("transferType") == "InterRegion Outbound" and attrs.get("toRegionCode") == "us-west-2"
        if attrs.get("fromRegionCode") != region or not (intra or backup):
            raise Gate("Backup transfer must price the exact East 1 to West 2 direction")
    elif attrs.get("regionCode") != region:
        raise Gate("Price product attributes differ from the charged region")
    age = now - _utc(rate.get("retrieved_at"))
    if not -timedelta(days=1) <= age <= timedelta(days=31):
        raise Gate("Refresh the actual regional price evidence")


def verify_regional_budget(config, evidence, selected, stress, *, now=None):
    """Validate all component quantities and totals after caller selects its cases."""
    now = now or datetime.now(timezone.utc)
    if (config.get("region") != "us-east-1" or config.get("backupRegion") != "us-west-2"
            or config.get("environment") != "fargate-development"
            or evidence.get("deployment_profile") != "fargate-development"
            or evidence.get("currency") != "USD"
            or evidence.get("regional_scope") != REGIONAL_SCOPE
            or evidence.get("region") != "us-east-1" or evidence.get("unverified_rates") != []):
        raise Gate("Regional admission needs East 1, West 2 and retained Ohio prices")
    users = config.get("plannedMonthlyUsers")
    if type(users) is not int or users not in (0, 10):
        raise Gate("The regional plan supports only the reviewed low-volume workloads")
    baseline = bounded_json(BASE_MODEL, 262144)
    if evidence.get("selected_scenario_assumptions") != baseline["selected_scenario_assumptions"]:
        raise Gate("Regional pricing cannot weaken the reviewed workload or capacity stress")
    if evidence.get("retained_ohio_assumptions") != RETAINED_ASSUMPTIONS:
        raise Gate("Price the retained Ohio resources until actual decommission")
    extra = additional_lines(users, evidence.get("backup_assumptions", {}))
    rates = evidence.get("rates")
    if not isinstance(rates, dict):
        raise Gate("Regional prices are incomplete")
    snapshot = bounded_json(PRICE_EVIDENCE, 262144)
    if rates != snapshot.get("rates") or evidence.get("price_evidence_sha256") != sha256(snapshot):
        raise Gate("Regional rates differ from their reviewed official source snapshot")
    components = []
    for case, key in ((selected, "scenarios"), (stress, "configured_maximum_1_acu_stress_scenarios")):
        if not isinstance(case, dict):
            raise Gate("Regional workload cases must be complete objects")
        legacy = next(row for row in baseline[key] if row["monthly_active_users"] == users)
        expected = [("primary", "global" if item["rate"].startswith("cloudfront_") or item["rate"] == "cw_dashboard_month" else "us-east-1",
                     item["item"], "primary_" + item["rate"], item["quantity"])
                    for item in legacy["items"]] + extra
        rows = case.get("items", []) if isinstance(case, dict) else []
        if case.get("monthly_active_users") != users or not isinstance(rows, list) or len(rows) != len(expected):
            raise Gate("Regional scenarios must price every primary, backup and retained item")
        observed, by_component = {}, defaultdict(Decimal)
        for row in rows:
            name = row.get("item") if isinstance(row, dict) else None
            if not isinstance(name, str) or name in observed:
                raise Gate("Regional cost items are malformed or duplicated")
            observed[name] = row
        for component, region, name, rate_name, quantity in expected:
            row = observed.get(name, {})
            if (row.get("component") != component or row.get("region") != region
                    or row.get("rate") != rate_name or not _number(row.get("quantity"))
                    or Decimal(str(row["quantity"])) != Decimal(str(quantity))
                    or not _number(row.get("monthly_usd"))):
                raise Gate("Regional quantities or ownership scope differ from the reviewed model")
            rate = rates.get(rate_name)
            _rate(rate, region, now)
            amount = _money(Decimal(str(quantity)) * Decimal(str(rate["usd"])))
            if amount != Decimal(str(row["monthly_usd"])):
                raise Gate("Regional price arithmetic does not reconcile")
            by_component[component] += amount
        total = sum(by_component.values())
        if (not _number(case.get("total_monthly_usd")) or total != Decimal(str(case["total_monthly_usd"]))
                or not _number(config.get("monthlyBudgetUsd")) or not 0 < config["monthlyBudgetUsd"] <= 100
                or total > Decimal(str(config["monthlyBudgetUsd"]))):
            raise Gate("Combined regional workload or unchanged capacity stress exceeds the approved budget")
        components.append({name: float(value) for name, value in by_component.items()})
    return {"regional_scope": deepcopy(REGIONAL_SCOPE), "component_monthly_usd": components[0],
            "stress_component_monthly_usd": components[1],
            "backup_assumptions": evidence["backup_assumptions"].copy(),
            "retained_ohio_assumptions": RETAINED_ASSUMPTIONS.copy(),
            "budget_is_a_spending_cap": False, "copy_bytes_measured": False,
            "cost_allocation_tag_activation": "not_verified"}
