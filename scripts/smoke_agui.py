#!/usr/bin/env python3
"""Minimal AG-UI smoke client that prints SSE events from the local server."""

from __future__ import annotations

import json
import os
import sys

import httpx


def main() -> int:
    url = os.environ.get("AGUI_SERVER_URL", "http://127.0.0.1:8888/agent")
    prompt = " ".join(sys.argv[1:]) or "Explica el agent loop en una frase."
    payload = {"messages": [{"role": "user", "content": prompt}]}

    with httpx.stream(
        "POST",
        url,
        json=payload,
        headers={"Accept": "text/event-stream"},
        timeout=90.0,
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line.startswith("data: "):
                continue
            event = json.loads(line.removeprefix("data: "))
            event_type = event.get("type")
            if event_type == "TEXT_MESSAGE_CONTENT":
                print(event.get("delta", ""), end="", flush=True)
            elif event_type in {"TOOL_CALL_START", "TOOL_CALL_RESULT", "RUN_ERROR"}:
                print(f"\n[{event_type}: {event}]", flush=True)
            elif event_type == "RUN_FINISHED":
                print("\n[RUN_FINISHED]", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
