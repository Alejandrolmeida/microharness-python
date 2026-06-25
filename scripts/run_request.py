#!/usr/bin/env python3
"""Non-interactive client for the MicroHarness HTTP endpoint."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from microharness.memory import (  # noqa: E402
    SUMMARY_PATH,
    read_reference_response,
    read_session_state,
    write_agent_artifact,
)

DEFAULT_PROMPT = (
    "Explica cómo este harness convierte un modelo en agente operativo. "
    "Separa Agent Loop, Context Manager, Skills, Sub-agents, Memory y Lifecycle Hooks."
)


def main() -> int:
    """Run one request against the local server."""

    base_url = os.environ.get("MICROHARNESS_API_URL", "http://127.0.0.1:8000")
    prompt = " ".join(sys.argv[1:]).strip() or DEFAULT_PROMPT

    print("=== Prompt enviado ===")
    print(prompt)
    print()

    reference_response_used = False
    try:
        response = httpx.post(
            f"{base_url.rstrip('/')}/api/chat",
            json={"prompt": prompt, "session_id": "cli", "allow_reference_response": True},
            timeout=90.0,
        )
        response.raise_for_status()
        payload = response.json()
        answer = payload["response"]
        artifact_path = payload["artifact_path"]
        session_state = payload["session_state"]
        reference_response_used = bool(payload.get("reference_response_used"))
    except Exception as exc:
        reference_response_used = True
        answer = read_reference_response().strip()
        session_state = write_agent_artifact(prompt=prompt, summary=answer)
        artifact_path = str(SUMMARY_PATH.relative_to(ROOT))
        print(f"[respuesta de referencia local activada: {exc}]\n")

    print("=== Respuesta del agente ===")
    print(answer)
    print()

    print("=== Artefacto generado ===")
    print(artifact_path)
    print()

    print("=== Estado de sesión ===")
    print(json.dumps(session_state or read_session_state(), ensure_ascii=False, indent=2))
    print()

    if reference_response_used:
        print("Nota: se usó una respuesta de referencia porque el modelo no respondió.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())