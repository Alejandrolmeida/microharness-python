"""Small, safe demo tools exposed to the Agent Framework agent."""

from __future__ import annotations

from typing import Annotated, Any

from agent_framework import tool
from pydantic import Field

_SESSION_FACTS: dict[str, list[str]] = {}


@tool
def explain_agent_framework_concept(
    concept: Annotated[
        str,
        Field(
            description=(
                "Concept to explain: loop, tools, context, session, approvals, "
                "MCP, memory, planning or Foundry."
            )
        ),
    ],
) -> dict[str, str]:
    """Explain a core Microsoft Agent Framework concept for the live demo."""

    key = concept.strip().lower()
    concepts = {
        "loop": (
            "Agent Loop: observe the user message, decide whether a tool is needed, "
            "execute it, incorporate the result and continue until the answer is ready."
        ),
        "tools": (
            "Tools: typed Python functions decorated with @tool. The model chooses "
            "when to call them and receives their result as context."
        ),
        "context": (
            "Context: the prompt, current user turn, tool outputs and relevant state "
            "provided to the model for the next decision."
        ),
        "session": (
            "Session: conversation continuity. The same thread keeps prior turns and "
            "lets the agent behave coherently across requests."
        ),
        "approvals": (
            "Approvals: human-in-the-loop gates for risky tools. AG-UI can surface "
            "approval requests before execution."
        ),
        "mcp": (
            "MCP: a path to connect external tools and data sources without "
            "hardwiring every integration into the app."
        ),
        "memory": (
            "Memory: durable or scoped state that can be added later so the agent "
            "remembers facts beyond one request."
        ),
        "planning": (
            "Planning: a layer above the loop that decomposes goals, chooses steps "
            "and checks progress before acting."
        ),
        "foundry": (
            "Foundry: the production path for model hosting, observability, "
            "evaluations, deployments and enterprise governance."
        ),
    }
    return {
        "concept": key,
        "explanation": concepts.get(
            key,
            "Concepto no reconocido. Prueba con loop, tools, context, session, "
            "approvals, MCP, memory, planning o Foundry.",
        ),
    }


@tool
def remember_session_fact(
    session_id: Annotated[
        str,
        Field(description="Demo session identifier, for example 'live-demo'."),
    ],
    fact: Annotated[
        str,
        Field(description="Short fact to keep in the in-memory demo context."),
    ],
) -> dict[str, Any]:
    """Store a short fact in volatile in-memory session context for the demo."""

    normalized_session = session_id.strip() or "default"
    normalized_fact = fact.strip()
    _SESSION_FACTS.setdefault(normalized_session, []).append(normalized_fact)
    return {
        "session_id": normalized_session,
        "stored_fact": normalized_fact,
        "facts_in_session": len(_SESSION_FACTS[normalized_session]),
        "scope": "process-memory-only",
    }


@tool
def read_session_context(
    session_id: Annotated[str, Field(description="Demo session identifier to inspect.")],
) -> dict[str, Any]:
    """Read the volatile in-memory context collected for a demo session."""

    normalized_session = session_id.strip() or "default"
    return {
        "session_id": normalized_session,
        "facts": _SESSION_FACTS.get(normalized_session, []),
        "scope": "process-memory-only",
    }


@tool
def draft_extension_plan(
    scenario: Annotated[
        str,
        Field(description="Advanced scenario to extend the micro harness toward."),
    ],
) -> dict[str, Any]:
    """Draft next steps to evolve the demo toward advanced agentic scenarios."""

    return {
        "scenario": scenario,
        "steps": [
            "Define the policy boundary: what the agent may decide and what needs "
            "user confirmation.",
            "Add durable session storage for conversation and tool traces.",
            "Introduce the new capability behind a small adapter, not inside the model prompt.",
            "Expose progress and decisions through AG-UI streaming events.",
            "Add evaluation prompts and smoke tests before moving to Foundry deployment.",
        ],
    }


@tool(approval_mode="always_require")
def propose_foundry_deployment(
    environment: Annotated[
        str,
        Field(description="Target environment name, for example dev, test or prod."),
    ],
    reason: Annotated[
        str,
        Field(description="Why this deployment should be approved."),
    ],
) -> dict[str, str]:
    """Propose a deployment action that demonstrates human-in-the-loop approval."""

    return {
        "environment": environment,
        "status": "deployment-proposal-recorded",
        "reason": reason,
        "note": "This is a safe demo tool; it does not deploy anything.",
    }


DEMO_TOOLS = [
    explain_agent_framework_concept,
    remember_session_fact,
    read_session_context,
    draft_extension_plan,
    propose_foundry_deployment,
]
