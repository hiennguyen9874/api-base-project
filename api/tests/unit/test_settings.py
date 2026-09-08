"""Unit tests for environment and YAML settings precedence."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from app.core.settings import Settings

API_ROOT = Path(__file__).resolve().parents[2]
SETTINGS_ENV_PREFIXES = (
    "APP__",
    "TOKEN__",
    "POSTGRES__",
    "TASKIQ__",
    "USER__",
    "SENTRY__",
)


@pytest.mark.unit
def test_shell_user_variable_does_not_override_nested_user_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("USER", "host-account")
    monkeypatch.setenv("USER__FIRST_USER_EMAIL", "override@example.com")
    monkeypatch.setenv("USER__FIRST_USER_PASSWORD", "nested-test-password")

    configured = Settings()

    assert str(configured.USER.FIRST_USER_EMAIL) == "override@example.com"
    assert configured.USER.FIRST_USER_PASSWORD == "nested-test-password"


@pytest.mark.unit
def test_user_nested_environment_variables_still_override_yaml(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("USER", raising=False)
    monkeypatch.setenv("USER__OPEN_REGISTRATION", "true")

    configured = Settings()

    assert configured.USER.OPEN_REGISTRATION is True


@pytest.mark.unit
def test_app_import_succeeds_without_settings_environment() -> None:
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(SETTINGS_ENV_PREFIXES) and key != "APP_CONFIG_FILE"
    }

    result = subprocess.run(
        [sys.executable, "-c", "from app.main import app; assert app.title == 'CashLens'"],
        cwd=API_ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
