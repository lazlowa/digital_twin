import pytest

from app.config import Settings


def test_settings_read_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_MODEL", "test/model")
    monkeypatch.setenv("NOTIFY_TO", "someone@example.com")

    settings = Settings(_env_file=None)

    assert settings.openrouter_model == "test/model"
    assert settings.notify_to == "someone@example.com"
