"""Small file-backed memory used by the MicroHarness runtime."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
WORKING_DIR = ROOT / "working"
OUTPUT_DIR = WORKING_DIR / "output"
CONTEXT_PATH = WORKING_DIR / "contexto_harness.md"
SUMMARY_PATH = OUTPUT_DIR / "agent_summary.md"
SESSION_STATE_PATH = OUTPUT_DIR / "session_state.json"
TRACE_PATH = OUTPUT_DIR / "lifecycle_trace.jsonl"
REFERENCE_DIR = WORKING_DIR / "reference"
REFERENCE_RESPONSE_PATH = REFERENCE_DIR / "expected_response.md"
REFERENCE_SUMMARY_PATH = REFERENCE_DIR / "expected_agent_summary.md"
REFERENCE_SESSION_STATE_PATH = REFERENCE_DIR / "expected_session_state.json"


def ensure_working_dirs() -> None:
    """Create local working folders if they do not exist."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)


def read_harness_context_file() -> str:
    """Read the controlled local context for the harness explanation."""

    if not CONTEXT_PATH.exists():
        raise FileNotFoundError(f"No existe el contexto del harness: {CONTEXT_PATH}")
    return CONTEXT_PATH.read_text(encoding="utf-8")


def read_session_state() -> dict[str, Any]:
    """Read the persisted session state, returning an empty initial state if needed."""

    ensure_working_dirs()
    if not SESSION_STATE_PATH.exists():
        return {
            "run_count": 0,
            "last_run_at": None,
            "last_prompt": None,
            "last_summary": None,
            "facts": {},
            "tool_trace": [],
        }
    return json.loads(SESSION_STATE_PATH.read_text(encoding="utf-8"))


def write_session_state(state: dict[str, Any]) -> dict[str, Any]:
    """Persist the complete session state."""

    ensure_working_dirs()
    SESSION_STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return state


def remember_fact(session_id: str, fact: str) -> dict[str, Any]:
    """Persist a short fact under a session identifier."""

    normalized_session = session_id.strip() or "default"
    normalized_fact = fact.strip()
    state = read_session_state()
    facts = state.setdefault("facts", {})
    session_facts = facts.setdefault(normalized_session, [])
    if normalized_fact and normalized_fact not in session_facts:
        session_facts.append(normalized_fact)
    return write_session_state(state)


def read_facts(session_id: str) -> list[str]:
    """Read persisted facts for a session identifier."""

    normalized_session = session_id.strip() or "default"
    state = read_session_state()
    facts = state.get("facts", {})
    if not isinstance(facts, dict):
        return []
    values = facts.get(normalized_session, [])
    return values if isinstance(values, list) else []


def append_tool_trace(tool_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Record a compact trace entry for a tool call."""

    state = read_session_state()
    trace = state.setdefault("tool_trace", [])
    entry = {
        "at": datetime.now(UTC).isoformat(),
        "tool": tool_name,
        "payload": payload,
    }
    trace.append(entry)
    state["tool_trace"] = trace[-50:]
    write_session_state(state)
    return entry


def write_agent_artifact(prompt: str, summary: str) -> dict[str, Any]:
    """Persist the markdown artifact and update the tiny JSON session state."""

    ensure_working_dirs()
    now = datetime.now(UTC).isoformat()
    state = read_session_state()
    run_count = int(state.get("run_count") or 0) + 1

    markdown = (
        "# MicroHarness agent summary\n\n"
        f"**Generated at:** {now}\n\n"
        "## Prompt\n\n"
        f"{prompt.strip()}\n\n"
        "## Agent response\n\n"
        f"{summary.strip()}\n"
    )
    SUMMARY_PATH.write_text(markdown, encoding="utf-8")

    new_state = {
        **state,
        "run_count": run_count,
        "last_run_at": now,
        "last_prompt": prompt,
        "last_summary": summary,
        "artifact_path": str(SUMMARY_PATH.relative_to(ROOT)),
    }
    return write_session_state(new_state)


def read_reference_response() -> str:
    """Return a reference response used when the model or network is unavailable."""

    if REFERENCE_RESPONSE_PATH.exists():
        return REFERENCE_RESPONSE_PATH.read_text(encoding="utf-8")
    return (
        "- **Agent Loop:** observa la petición, decide si necesita herramientas y sintetiza.\n"
        "- **Tools:** funciones controladas aportan capacidades verificables.\n"
        "- **Memory:** estado mínimo de sesión permite continuidad.\n"
        "- **Planning:** descompone objetivos antes de actuar.\n"
        "- **Permissions:** approvals separan acciones seguras de acciones sensibles."
    )


def append_lifecycle_event(event: dict[str, Any]) -> dict[str, Any]:
    """Append a lifecycle event to the JSONL trace."""

    ensure_working_dirs()
    enriched = {"at": datetime.now(UTC).isoformat(), **event}
    with TRACE_PATH.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(enriched, ensure_ascii=False) + "\n")
    return enriched
