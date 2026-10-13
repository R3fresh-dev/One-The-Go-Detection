"""Reprice unchanged demand with captured official rates; performs no network/AWS calls."""
from __future__ import annotations

import argparse
from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'services/api'))
sys.path.insert(0, str(ROOT))
from deploy.provenance import sha256
from deploy.regional_budget import BACKUP_ASSUMPTIONS, REGIONAL_SCOPE, RETAINED_ASSUMPTIONS, additional_lines


def build(primary, supplemental, collections):
    baseline = json.loads((ROOT / 'infra/costs/fargate-estimate.json').read_text())
    if primary.get('missing_rates') != [] or supplemental.get('missing_rates') != []:
        raise ValueError('All official regional prices must be present')
    rates = {}
    for name, value in primary['rates'].items():
        rate = deepcopy(value)
        if rate['region'] == 'aws-other':
            rate['catalog_region'] = 'aws-other'
            rate['region'] = 'global'
        rates['primary_' + name] = rate
    assumptions = {**BACKUP_ASSUMPTIONS, 'database_changed_gb_per_day': 1,
                   's3_changed_gb_per_day': 1, 'changed_bytes_measured': False,
                   'changed_bytes_are_enforced_maxima': False,
                   'source_snapshot_costs_reserved_separately': True}
    for _, _, _, rate, _ in additional_lines(10, assumptions):
        if not rate.startswith('primary_'):
            rates[rate] = deepcopy(supplemental['rates'][rate])
    price_snapshot = {'schema_version': '1.0.0', 'rates': rates,
                      'source_collections_sha256': sha256(collections)}
    result = {'schema_version': '1.0.0', 'deployment_profile': 'fargate-development',
              'region': 'us-east-1', 'currency': 'USD', 'regional_scope': deepcopy(REGIONAL_SCOPE),
              'checked_at': min(rate['retrieved_at'] for rate in rates.values()),
              'unverified_rates': [], 'rates': rates, 'price_evidence_sha256': sha256(price_snapshot),
              'selected_scenario_assumptions': deepcopy(baseline['selected_scenario_assumptions']),
              'workload_assumptions': deepcopy(baseline['workload_assumptions']),
              'backup_assumptions': assumptions, 'retained_ohio_assumptions': deepcopy(RETAINED_ASSUMPTIONS)}

    def scenario(original, backup=assumptions):
        case = deepcopy(original)
        rows = []
        for item in original['items']:
            key = 'primary_' + item['rate']
            rows.append({**item, 'component': 'primary', 'region': rates[key]['region'], 'rate': key})
        for component, region, item, rate, quantity in additional_lines(original['monthly_active_users'], backup):
            rows.append({'component': component, 'region': region, 'item': item, 'rate': rate, 'quantity': quantity})
        for item in rows:
            item['monthly_usd'] = float((Decimal(str(item['quantity'])) * Decimal(str(rates[item['rate']]['usd']))).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))
        total = sum(Decimal(str(item['monthly_usd'])) for item in rows)
        case.update(items=rows, total_monthly_usd=float(total), within_owner_budget=total <= 100,
                    budget_headroom_usd=float(100 - total))
        return case

    for kind in ('scenarios', 'configured_maximum_1_acu_stress_scenarios'):
        result[kind] = [scenario(case) for case in baseline[kind]]
    result['full_daily_database_copy_stress_sensitivity'] = [scenario(case, {**assumptions,
        'database_changed_gb_per_day': 10 + case['monthly_active_users'] * .01})
        for case in baseline['configured_maximum_1_acu_stress_scenarios']]
    result['notes'] = [
        'Official East1 rates reprice the unchanged primary demand, 180-second worker and 1ACU capacity stress quantities. No primary workload or cleanup interval is lowered.',
        'Daily Aurora copies use PLANNED, UNMEASURED 1GB/day changed-database and 1GB/day S3 replication allowances plus first full database/S3 copies. These are neither enforced maxima nor measured transfer bytes.',
        'Seven full target database recovery points and two full source points are charged conservatively; the existing primary backup allowance is retained.',
        'All five S3 bucket replicas retain versioned bytes and metadata. Artifact/export permanent replica erasure must be verified; journal COMPLIANCE authority remains retained.',
        'Ohio storage, three keys/secrets, images, logs and S3 remain charged until separately authorized actual decommission. Stopped Aurora automatically restarts after seven days; zero future compute is not guaranteed.',
        'At10users the full-daily-database-copy sensitivity preserves primary 1ACU stress and exceeds the100USD plan. Copy-byte growth, retry/full-copy fallback, Ohio restart or additional recoveries trigger immediate cost review.',
        'Costs are planning amounts before free tiers/credits; alerts do not cap bills. Source-configured project CostFilters do not prove billing-tag activation or cost-allocation lag has cleared.',
    ]
    return result, price_snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--primary-rates', type=Path, required=True)
    parser.add_argument('--supplemental-rates', type=Path, required=True)
    parser.add_argument('--source-collections', type=Path, required=True)
    args = parser.parse_args()
    collections = json.loads(args.source_collections.read_text())
    estimate, snapshot = build(json.loads(args.primary_rates.read_text()),
                               json.loads(args.supplemental_rates.read_text()), collections)
    target = ROOT / 'infra/costs'
    for name, value in (('regional-fargate-estimate.json', estimate),
                        ('regional-fargate-price-evidence.json', snapshot),
                        ('regional-price-list-evidence.json', collections)):
        (target / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'selected': [(r['monthly_active_users'], r['total_monthly_usd']) for r in estimate['scenarios']],
                      'stress': [(r['monthly_active_users'], r['total_monthly_usd']) for r in estimate['configured_maximum_1_acu_stress_scenarios']],
                      'full_copy_stress': [(r['monthly_active_users'], r['total_monthly_usd']) for r in estimate['full_daily_database_copy_stress_sensitivity']]}))


if __name__ == '__main__':
    main()
