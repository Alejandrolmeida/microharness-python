"""Lifecycle hooks for observable harness execution."""

from __future__ import annotations

from typing import Any

from microharness.memory import append_lifecycle_event


class LifecycleHooks:
    """Minimal hook surface around requests and tools."""

    def before_request(self, session_id: str, prompt: str) -> dict[str, Any]:
        """Record the start of an agent request."""

        return append_lifecycle_event(
            {"type": "before_request", "session_id": session_id, "prompt_chars": len(prompt)}
        )

    def after_request(self, session_id: str, response: str) -> dict[str, Any]:
        """Record the end of an agent request."""

        return append_lifecycle_event(
            {"type": "after_request", "session_id": session_id, "response_chars": len(response)}
        )

    def before_tool(self, tool_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Record a tool invocation before it runs."""

        return append_lifecycle_event(
            {"type": "before_tool", "tool": tool_name, "payload": payload}
        )

    def after_tool(self, tool_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Record a tool invocation after it runs."""

        return append_lifecycle_event({"type": "after_tool", "tool": tool_name, "payload": payload})


HOOKS = LifecycleHooks()