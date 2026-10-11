"""Operational cleanup alarms remain active while a failed cleanup is claimed."""

import importlib.util
import os
from pathlib import Path
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

os.environ['OTGD_ENVIRONMENT'] = 'test'
os.environ['OTGD_DATABASE_URL'] = 'sqlite://'
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('metrics', ROOT / 'scripts/publish-metrics.py')
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)
from otgd.db import Account, Artifact, Base


class CleanupMetricsTest(unittest.TestCase):
    def test_failed_cleanup_claim_remains_overdue_until_success(self):
        engine = create_engine('sqlite://')
        Base.metadata.create_all(engine)
        with Session(engine) as db:
            db.add(Account(id='00000000-0000-4000-8000-000000000001', subject_hash='a' * 64))
            db.flush()
            artifact = Artifact(
                id='00000000-0000-4000-8000-000000000002',
                account_id='00000000-0000-4000-8000-000000000001',
                generation=1,
                session_id='00000000-0000-4000-8000-000000000003',
                bucket='fictional-artifact-bucket', key='quarantine/fictional',
                sha256='b' * 64, size=1024,
                media_type='application/octet-stream', kind='ecg_waveform',
                state='quarantine', expires=1, scope={},
            )
            db.add(artifact)
            db.flush()

            def overdue():
                return next(
                    item['Value'] for item in metrics.collect(db, 90000)
                    if item['MetricName'] == 'CleanupOverdueCount'
                )

            self.assertEqual(overdue(), 1)
            artifact.state = 'cleanup_pending'
            db.flush()
            self.assertEqual(overdue(), 1)
            artifact.state = 'purged'
            artifact.cleanup_last_success = 90000
            db.flush()
            self.assertEqual(overdue(), 0)
        engine.dispose()


if __name__ == '__main__':
    unittest.main()
