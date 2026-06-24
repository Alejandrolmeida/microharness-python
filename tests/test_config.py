from __future__ import annotations

from microharness.config import load_settings


def test_load_settings_from_openai_compatible_base_url(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_BASE_URL", "https://example.invalid/openai/v1")
    monkeypatch.setenv("AZURE_OPENAI_MODEL", "gpt-5-5-thinking")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "not-a-real-key")
    monkeypatch.setenv("AZURE_OPENAI_MAX_COMPLETION_TOKENS", "1024")

    settings = load_settings()

    assert settings.model == "gpt-5-5-thinking"
    assert settings.base_url == "https://example.invalid/openai/v1"
    assert settings.uses_openai_compatible_url is True
    assert settings.max_completion_tokens == 1024


def test_load_settings_requires_model(monkeypatch):
    monkeypatch.delenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_CHAT_COMPLETION_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.setenv("AZURE_OPENAI_BASE_URL", "https://example.invalid/openai/v1")

    try:
        load_settings()
    except RuntimeError as exc:
        assert "Falta AZURE_OPENAI_CHAT_COMPLETION_MODEL" in str(exc)
    else:
        raise AssertionError("load_settings should fail without a model")
