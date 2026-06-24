"""Configuration helpers for the MicroHarness demo.

The project deliberately keeps secrets outside the repository. Values can come from:
1. a local .env file (ignored by git),
2. shell variables loaded by scripts/load_model_from_akv.sh, or
3. the user's existing Azure CLI session when no API key is supplied.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the agent harness."""

    model: str
    api_key: str | None
    base_url: str | None
    azure_endpoint: str | None
    api_version: str | None
    max_completion_tokens: int | None
    host: str
    port: int
    require_confirmation: bool

    @property
    def uses_openai_compatible_url(self) -> bool:
        """Return true when the app should route through a full /openai/v1 base URL."""

        return bool(self.base_url)


def _optional(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _parse_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _parse_int(value: str | None) -> int | None:
    if not value or not value.strip():
        return None
    return int(value)


def load_settings() -> Settings:
    """Load settings from environment variables and an optional local .env file."""

    load_dotenv()

    model = _optional(
        os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL")
        or os.getenv("AZURE_OPENAI_MODEL")
        or os.getenv("OPENAI_CHAT_COMPLETION_MODEL")
        or os.getenv("OPENAI_MODEL")
    )
    if not model:
        raise RuntimeError(
            "Falta AZURE_OPENAI_CHAT_COMPLETION_MODEL o AZURE_OPENAI_MODEL. "
            "Ejecuta scripts/load_model_from_akv.sh o crea un .env local."
        )

    base_url = _optional(os.getenv("AZURE_OPENAI_BASE_URL") or os.getenv("OPENAI_BASE_URL"))
    azure_endpoint = _optional(os.getenv("AZURE_OPENAI_ENDPOINT"))

    if not base_url and not azure_endpoint:
        raise RuntimeError(
            "Falta AZURE_OPENAI_BASE_URL o AZURE_OPENAI_ENDPOINT. "
            "Para la configuración Azurebrains usa AZURE_OPENAI_BASE_URL con la URL /openai/v1."
        )

    port = int(os.getenv("MICROHARNESS_PORT", "8000"))

    return Settings(
        model=model,
        api_key=_optional(os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")),
        base_url=base_url.rstrip("/") if base_url else None,
        azure_endpoint=azure_endpoint.rstrip("/") if azure_endpoint else None,
        api_version=_optional(os.getenv("AZURE_OPENAI_API_VERSION")),
        max_completion_tokens=_parse_int(os.getenv("AZURE_OPENAI_MAX_COMPLETION_TOKENS")),
        host=os.getenv("MICROHARNESS_HOST", "127.0.0.1"),
        port=port,
        require_confirmation=_parse_bool(os.getenv("MICROHARNESS_REQUIRE_CONFIRMATION")),
    )
