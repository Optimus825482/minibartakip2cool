import importlib
import sys
from pathlib import Path

import pytest


def reload_config(monkeypatch, env=None, secret_key=None):
    """Reload the config module with fresh environment variables."""
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    for var in ("SECRET_KEY", "FLASK_ENV", "ENV"):
        monkeypatch.delenv(var, raising=False)

    if env is not None:
        monkeypatch.setenv("FLASK_ENV", env)
    if secret_key is not None:
        monkeypatch.setenv("SECRET_KEY", secret_key)

    sys.modules.pop("config", None)
    return importlib.import_module("config")


def test_dev_env_uses_fallback_secret(monkeypatch):
    module = reload_config(monkeypatch, env="development")

    assert module.Config.SECRET_KEY == "development-secret-key-change-in-production"
    assert module.Config.SESSION_COOKIE_SECURE is False


def test_prod_env_requires_secret_key(monkeypatch):
    with pytest.raises(ValueError, match="SECRET_KEY environment variable is required"):
        reload_config(monkeypatch, env="production")


def test_prod_env_rejects_short_secret(monkeypatch):
    with pytest.raises(ValueError, match="SECRET_KEY must be at least 32 characters"):
        reload_config(monkeypatch, env="production", secret_key="short-secret")


def test_prod_env_accepts_long_secret(monkeypatch):
    long_secret = "x" * 40
    module = reload_config(monkeypatch, env="production", secret_key=long_secret)

    assert module.Config.SECRET_KEY == long_secret
    assert module.Config.SESSION_COOKIE_SECURE is True
