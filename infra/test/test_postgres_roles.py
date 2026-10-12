"""Destructive role-test setup must reject every non-disposable target."""

import importlib.util
import os
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SOURCE = Path(__file__).with_name("postgres_roles.py")
SPEC = importlib.util.spec_from_file_location("disposable_postgres_roles", SOURCE)
roles = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(roles)


def configuration(**changes):
    return SimpleNamespace(
        **{
            "environment": "test",
            "database_name": "otgd_ci",
            "app_database_user": "otgd_app_ci",
            "app_database_password": "fictional_runtime_password",
            "db_url": lambda: "postgresql+psycopg://ci_admin:fictional@127.0.0.1:5432/otgd_ci",
            **changes,
        }
    )


class DisposableRolesTest(unittest.TestCase):
    def test_only_explicit_dedicated_loopback_targets_are_admitted(self):
        env = {"OTGD_DISPOSABLE_DATABASE": "true", "OTGD_LIVE_S3_ENDPOINT": "http://localhost:4566"}
        url, endpoint = roles.disposable_target(configuration(), env)
        self.assertEqual(url.database, "otgd_ci")
        self.assertEqual(endpoint, "http://localhost:4566")
        for change in (
            {"environment": "local"}, {"environment": "qa"}, {"environment": "prod"},
            {"database_name": "otgd"}, {"app_database_user": "otgd_app"},
            {"app_database_user": "ci_admin"}, {"app_database_password": ""},
            {"db_url": lambda: "sqlite://"},
            {"db_url": lambda: "postgresql+psycopg://ci_admin:fictional@localhost/otgd"},
            {"db_url": lambda: "postgresql+psycopg://ci_admin:fictional@db.example/otgd_ci"},
            {"db_url": lambda: "postgresql+psycopg://ci_admin:fictional@localhost/otgd_ci?host=production.example"},
            {"db_url": lambda: "postgresql+psycopg://ci_admin:fictional@localhost/otgd_ci?dbname=otgd"},
        ):
            with self.subTest(change=change), self.assertRaises(RuntimeError):
                roles.disposable_target(configuration(**change), env)
        for endpoint in (
            "", "https://localhost:4566", "http://example.com:4566",
            "http://user:pass@localhost:4566", "http://localhost:4566/private",
            "http://localhost:4566/?target=cloud", "http://localhost:4566/#cloud",
        ):
            with self.subTest(endpoint=endpoint), self.assertRaises(RuntimeError):
                roles.disposable_target(configuration(), {**env, "OTGD_LIVE_S3_ENDPOINT": endpoint})
        with self.assertRaises(RuntimeError):
            roles.disposable_target(configuration(), {**env, "OTGD_DISPOSABLE_DATABASE": "false"})

    def test_exception_restores_the_callers_credentials_and_journal_environment(self):
        with patch.dict(os.environ, {"AWS_PROFILE": "existing-profile", "OTGD_JOURNAL_BUCKET": "existing-journal"}):
            before = dict(os.environ)
            with self.assertRaisesRegex(RuntimeError, "fictional setup failed"):
                with roles.environment({"AWS_PROFILE": None, "OTGD_JOURNAL_BUCKET": "owned-test-journal"}):
                    self.assertNotIn("AWS_PROFILE", os.environ)
                    self.assertEqual(os.environ["OTGD_JOURNAL_BUCKET"], "owned-test-journal")
                    raise RuntimeError("fictional setup failed")
            self.assertEqual(dict(os.environ), before)


if __name__ == "__main__":
    unittest.main()
