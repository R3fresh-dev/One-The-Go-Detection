"""Adversarial regional cost admission; no AWS billing or copy measurements."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import unittest

from deploy import regional_budget as budget
from deploy.provenance import Gate

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 10, 13, 4, tzinfo=timezone.utc)


class RegionalBudgetTest(unittest.TestCase):
    def setUp(self):
        self.evidence = json.loads((ROOT / 'infra/costs/regional-fargate-estimate.json').read_text())
        self.config = {'environment': 'fargate-development', 'region': 'us-east-1',
                       'backupRegion': 'us-west-2', 'plannedMonthlyUsers': 10,
                       'monthlyBudgetUsd': 100}

    def cases(self, evidence=None, users=10):
        value = evidence or self.evidence
        return tuple(next(row for row in value[key] if row['monthly_active_users'] == users)
                     for key in ('scenarios', 'configured_maximum_1_acu_stress_scenarios'))

    def verify(self, evidence=None, config=None, *, now=NOW):
        value = self.evidence if evidence is None else evidence
        selected = self.config if config is None else config
        return budget.verify_regional_budget(selected, value, *self.cases(value, selected['plannedMonthlyUsers']), now=now)

    def test_complete_official_three_region_plan_preserves_capacity_stress(self):
        plan = self.verify()
        self.assertEqual(plan['component_monthly_usd'], {'primary': 65.61, 'backup': 5.24, 'retained_legacy': 5.77})
        self.assertEqual(plan['stress_component_monthly_usd'], {'primary': 86.90, 'backup': 5.24, 'retained_legacy': 5.77})
        self.assertEqual(self.cases()[0]['total_monthly_usd'], 76.62)
        self.assertEqual(self.cases()[1]['total_monthly_usd'], 97.91)
        self.assertFalse(plan['budget_is_a_spending_cap'])
        self.assertFalse(plan['copy_bytes_measured'])
        self.assertEqual(plan['cost_allocation_tag_activation'], 'not_verified')
        self.assertFalse(plan['retained_ohio_assumptions']['decommission_executed'])
        self.assertEqual(self.verify(config={**self.config, 'plannedMonthlyUsers': 0})['component_monthly_usd']['primary'], 62.75)

    def test_foreign_scope_missing_backup_and_retained_authority_are_rejected(self):
        for change in ({'region': 'us-east-2'}, {'backupRegion': 'us-east-1'}, {'environment': 'qa'}):
            with self.subTest(change=change), self.assertRaises(Gate):
                self.verify(config={**self.config, **change})
        for component in ('backup', 'retained_legacy'):
            evidence = deepcopy(self.evidence)
            selected, _ = self.cases(evidence)
            selected['items'] = [row for row in selected['items'] if row['component'] != component]
            selected['total_monthly_usd'] = round(sum(row['monthly_usd'] for row in selected['items']), 2)
            with self.subTest(component=component), self.assertRaises(Gate):
                self.verify(evidence)

    def test_reconciled_cheaper_primary_workload_cannot_weaken_the_model(self):
        evidence = deepcopy(self.evidence)
        selected, _ = self.cases(evidence)
        service = next(row for row in selected['items'] if row['rate'] == 'primary_fargate_vcpu_hour')
        selected['total_monthly_usd'] = round(selected['total_monthly_usd'] - service['monthly_usd'], 2)
        service.update(quantity=0, monthly_usd=0)
        with self.assertRaisesRegex(Gate, 'quantities'):
            self.verify(evidence)
        evidence = deepcopy(self.evidence)
        evidence['selected_scenario_assumptions']['configured_max_acu'] = .5
        with self.assertRaisesRegex(Gate, 'capacity stress'):
            self.verify(evidence)

    def test_rates_cannot_be_forged_or_stale_even_when_arithmetic_reconciles(self):
        evidence = deepcopy(self.evidence)
        evidence['rates']['primary_aurora_acu_hour']['usd'] /= 2
        for case in self.cases(evidence):
            row = next(row for row in case['items'] if row['rate'] == 'primary_aurora_acu_hour')
            difference = row['monthly_usd']
            row['monthly_usd'] = float(budget._money(row['quantity'] * evidence['rates'][row['rate']]['usd']))
            case['total_monthly_usd'] = round(case['total_monthly_usd'] - difference + row['monthly_usd'], 2)
        with self.assertRaisesRegex(Gate, 'source snapshot'):
            self.verify(evidence)
        with self.assertRaisesRegex(Gate, 'Refresh'):
            self.verify(now=datetime(2026, 12, 1, tzinfo=timezone.utc))

    def test_official_products_must_bind_the_charged_region_and_transfer_direction(self):
        rate = deepcopy(self.evidence['rates']['west2_kms_key_month'])
        rate['attributes']['regionCode'] = 'us-east-2'
        with self.assertRaisesRegex(Gate, 'charged region'):
            budget._rate(rate, 'us-west-2', NOW)
        rate = deepcopy(self.evidence['rates']['east1_to_west2_transfer_gb'])
        rate['attributes']['toRegionCode'] = 'us-east-2'
        with self.assertRaisesRegex(Gate, 'transfer'):
            budget._rate(rate, 'us-east-1', NOW)

    def test_duplicate_wrong_region_and_underpriced_line_items_fail(self):
        for change in ('duplicate', 'region', 'price'):
            evidence = deepcopy(self.evidence)
            selected, _ = self.cases(evidence)
            row = next(item for item in selected['items'] if item['component'] == 'backup')
            if change == 'duplicate':
                row['item'] = selected['items'][0]['item']
            elif change == 'region':
                row['region'] = 'us-east-2'
            else:
                row['monthly_usd'] -= .01
                selected['total_monthly_usd'] -= .01
            with self.subTest(change=change), self.assertRaises(Gate):
                self.verify(evidence)

    def test_full_daily_database_copy_exceeds_budget_without_lowering_stress(self):
        evidence = deepcopy(self.evidence)
        evidence['backup_assumptions']['database_changed_gb_per_day'] = 10.1
        selected, _ = self.cases(evidence)
        transfer = next(row for row in selected['items'] if row['rate'] == 'east1_to_west2_transfer_gb')
        transfer['quantity'] += 30 * 9.1
        transfer['monthly_usd'] = float(budget._money(transfer['quantity'] * .02))
        selected['total_monthly_usd'] = round(sum(row['monthly_usd'] for row in selected['items']), 2)
        stress = next(row for row in evidence['full_daily_database_copy_stress_sensitivity'] if row['monthly_active_users'] == 10)
        self.assertEqual(stress['total_monthly_usd'], 103.37)
        self.assertEqual(stress['active_database_acu_pricing_basis'], 1)
        with self.assertRaisesRegex(Gate, 'exceeds'):
            budget.verify_regional_budget(self.config, evidence, selected, stress, now=NOW)

    def test_backup_contract_cannot_drop_versions_secret_or_retention(self):
        for field, value in (('replicated_versioned_buckets', 4), ('destination_tombstone_secrets', 0),
                             ('journal_compliance_retention_days', 89), ('snapshot_destination_retention_days', 1),
                             ('changed_bytes_measured', True), ('changed_bytes_are_enforced_maxima', True)):
            evidence = deepcopy(self.evidence)
            evidence['backup_assumptions'][field] = value
            with self.subTest(field=field), self.assertRaises(Gate):
                self.verify(evidence)


if __name__ == '__main__':
    unittest.main()
