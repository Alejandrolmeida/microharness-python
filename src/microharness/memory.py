"""Tiny local persistence used by the live MicroHarness demo.

This is intentionally simple: the goal is to explain session/state in five minutes,
not to build a production memory service.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
WORKING_DIR = ROOT / "working"
OUTPUT_DIR = WORKING_DIR / "output"
CONTEXT_PATH = WORKING_DIR / "contexto_harness.md"
SUMMARY_PATH = OUTPUT_DIR / "demo_summary.md"
SESSION_STATE_PATH = OUTPUT_DIR / "session_state.json"
FALLBACK_DIR = WORKING_DIR / "fallback"
FALLBACK_RESPONSE_PATH = FALLBACK_DIR / "expected_response.md"
FALLBACK_SUMMARY_PATH = FALLBACK_DIR / "expected_demo_summary.md"
FALLBACK_SESSION_STATE_PATH = FALLBACK_DIR / "expected_session_state.json"


def ensure_working_dirs() -> None:
    """Create local working folders used by the demo if they do not exist."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FALLBACK_DIR.mkdir(parents=True, exist_ok=True)


def read_harness_context_file() -> str:
    """Read the controlled local context for the harness explanation."""

    if not CONTEXT_PATH.exists():
        raise FileNotFoundError(f"No existe el contexto de demo: {CONTEXT_PATH}")
    return CONTEXT_PATH.read_text(encoding="utf-8")


def read_session_state() -> dict[str, Any]:
    """Read the persisted session state, returning an empty initial state if needed."""

    ensure_working_dirs()
    if not SESSION_STATE_PATH.exists():
        return {"run_count": 0, "last_run_at": None, "last_prompt": None, "last_summary": None}
    return json.loads(SESSION_STATE_PATH.read_text(encoding="utf-8"))


def write_demo_summary(prompt: str, summary: str) -> dict[str, Any]:
    """Persist the markdown artifact and update the tiny JSON session state."""

    ensure_working_dirs()
    now = datetime.now(UTC).isoformat()
    state = read_session_state()
    run_count = int(state.get("run_count") or 0) + 1

    markdown = (
        "# MicroHarness demo summary\n\n"
        f"**Generated at:** {now}\n\n"
        "## Prompt\n\n"
        f"{prompt.strip()}\n\n"
        "## Agent response\n\n"
        f"{summary.strip()}\n"
    )
    SUMMARY_PATH.write_text(markdown, encoding="utf-8")

    new_state = {
        "run_count": run_count,
        "last_run_at": now,
        "last_prompt": prompt,
        "last_summary": summary,
        "artifact_path": str(SUMMARY_PATH.relative_to(ROOT)),
    }
    SESSION_STATE_PATH.write_text(
        json.dumps(new_state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return new_state


def read_fallback_response() -> str:
    """Return the pregenerated response used when the model or network is unavailable."""

    if FALLBACK_RESPONSE_PATH.exists():
        return FALLBACK_RESPONSE_PATH.read_text(encoding="utf-8")
    return (
        "- **Agent Loop:** observa la petición, decide si necesita herramientas y sintetiza.\n"
        "- **Tools:** funciones controladas aportan capacidades verificables.\n"
        "- **Memory:** estado mínimo de sesión permite continuidad.\n"
        "- **Planning:** descompone objetivos antes de actuar.\n"
        "- **Permissions:** approvals separan acciones seguras de acciones sensibles."
    )
