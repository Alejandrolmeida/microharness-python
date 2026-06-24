#!/usr/bin/env python3
"""Non-interactive client for the five-minute MicroHarness demo.

It calls the local FastAPI fallback endpoint and prints exactly the elements needed
on stage: prompt, response, generated artifact and session state. If the server is
not available, it uses the pregenerated fallback files so the demo can continue.
"""

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
    read_fallback_response,
    read_session_state,
    write_demo_summary,
)

DEMO_PROMPT = (
    "Explícame Agent Harness en 5 bullets para una audiencia técnica. "
    "Usa el contexto disponible y separa Agent Loop, Tools, Memory, Planning y Permissions."
)


def main() -> int:
    """Run the fixed demo request against the local server."""

    base_url = os.environ.get("MICROHARNESS_API_URL", "http://127.0.0.1:8000")
    prompt = " ".join(sys.argv[1:]).strip() or DEMO_PROMPT

    print("=== Prompt enviado ===")
    print(prompt)
    print()

    fallback_used = False
    try:
        response = httpx.post(
            f"{base_url.rstrip('/')}/api/chat",
            json={"prompt": prompt, "use_fallback": True},
            timeout=90.0,
        )
        response.raise_for_status()
        payload = response.json()
        answer = payload["response"]
        artifact_path = payload["artifact_path"]
        session_state = payload["session_state"]
        fallback_used = bool(payload.get("fallback_used"))
    except Exception as exc:
        # Plan B: permite enseñar la demo aunque no haya servidor, red o modelo.
        fallback_used = True
        answer = read_fallback_response().strip()
        session_state = write_demo_summary(prompt=prompt, summary=answer)
        artifact_path = str(SUMMARY_PATH.relative_to(ROOT))
        print(f"[plan B local activado: {exc}]\n")

    print("=== Respuesta del agente ===")
    print(answer)
    print()

    print("=== Artefacto generado ===")
    print(artifact_path)
    print()

    print("=== Estado de sesión ===")
    print(json.dumps(session_state or read_session_state(), ensure_ascii=False, indent=2))
    print()

    if fallback_used:
        print("Nota: se usó fallback para mantener la demo estable.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
