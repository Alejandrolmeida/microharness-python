"""MAF-native harness variant built with Microsoft Agent Framework primitives."""

from __future__ import annotations

from typing import Any

from agent_framework import (
    Agent,
    AgentContext,
    AgentMiddleware,
    AgentSession,
    ContextProvider,
    FileHistoryProvider,
    FunctionInvocationContext,
    FunctionMiddleware,
    MemoryContextProvider,
    MemoryFileStore,
    TodoFileStore,
    TodoProvider,
    ToolApprovalMiddleware,
)
from agent_framework_ag_ui import AgentFrameworkAgent

from microharness.config import Settings, load_settings
from microharness.context import ContextManager
from microharness.harness import INSTRUCTIONS, build_chat_client
from microharness.memory import ROOT, append_lifecycle_event, append_tool_trace
from microharness.tools import HARNESS_TOOLS

MAF_NATIVE_DIR = ROOT / "working" / "output" / "maf_native"


def _ensure_native_dirs() -> None:
    """Create the local folders used by the MAF-native providers."""

    MAF_NATIVE_DIR.mkdir(parents=True, exist_ok=True)


def _message_chars(messages: list[Any]) -> int:
    """Return a compact text-length estimate for lifecycle traces."""

    return sum(len(str(message)) for message in messages)


def _safe_arguments(arguments: Any) -> dict[str, Any]:
    """Convert function arguments to a JSON-friendly compact dictionary."""

    if hasattr(arguments, "model_dump"):
        dumped = arguments.model_dump()
    elif isinstance(arguments, dict):
        dumped = arguments
    else:
        dumped = {"value": str(arguments)}
    return {str(key): str(value)[:300] for key, value in dumped.items()}


class HarnessKnowledgeProvider(ContextProvider):
    """Inject controlled harness knowledge through the MAF context pipeline."""

    def __init__(self) -> None:
        super().__init__(source_id="microharness_context")

    async def before_run(
        self,
        *,
        agent: Any,
        session: AgentSession,
        context: Any,
        state: dict[str, Any],
    ) -> None:
        """Add the local context snapshot as provider instructions."""

        session.state.setdefault("microharness", "microharness")
        snapshot = ContextManager().build(session.session_id or "default")
        state["last_context_source"] = snapshot.source
        state["last_run_count"] = snapshot.run_count
        context.extend_instructions(
            self.source_id,
            (
                "Contexto inyectado por ContextProvider nativo de MAF.\n"
                "Usa este bloque como conocimiento controlado del harness:\n\n"
                f"{snapshot.as_prompt_block()}"
            ),
        )

    async def after_run(
        self,
        *,
        agent: Any,
        session: AgentSession,
        context: Any,
        state: dict[str, Any],
    ) -> None:
        """Record lightweight provider state after the invocation."""

        response = context.response
        text = getattr(response, "text", "") if response is not None else ""
        state["last_response_chars"] = len(text or "")


class HarnessLifecycleMiddleware(AgentMiddleware):
    """Trace agent invocations through MAF agent middleware."""

    async def process(self, context: AgentContext, call_next: Any) -> None:
        """Record before/after dispatch events without replacing the agent result."""

        session_id = context.session.session_id if context.session else "default"
        append_lifecycle_event(
            {
                "type": "maf_before_agent",
                "session_id": session_id,
                "stream": context.stream,
                "message_chars": _message_chars(context.messages),
            }
        )
        await call_next()
        append_lifecycle_event(
            {
                "type": "maf_after_agent_dispatch",
                "session_id": session_id,
                "stream": context.stream,
                "result_type": (
                    type(context.result).__name__ if context.result is not None else None
                ),
            }
        )


class HarnessToolTraceMiddleware(FunctionMiddleware):
    """Trace tool invocations through MAF function middleware."""

    async def process(self, context: FunctionInvocationContext, call_next: Any) -> None:
        """Record function-call metadata before and after MAF invokes a tool."""

        tool_name = context.function.name
        arguments = _safe_arguments(context.arguments)
        append_lifecycle_event(
            {"type": "maf_before_tool", "tool": tool_name, "payload": arguments}
        )
        await call_next()
        append_tool_trace(
            "maf_function_middleware",
            {
                "tool": tool_name,
                "arguments": arguments,
                "result_type": type(context.result).__name__,
            },
        )
        append_lifecycle_event(
            {
                "type": "maf_after_tool",
                "tool": tool_name,
                "payload": {"result_type": type(context.result).__name__},
            }
        )


def build_native_context_providers() -> list[ContextProvider]:
    """Build MAF context providers for history, memory, todos and local knowledge."""

    _ensure_native_dirs()
    return [
        FileHistoryProvider(MAF_NATIVE_DIR / "history"),
        HarnessKnowledgeProvider(),
        TodoProvider(
            store=TodoFileStore(MAF_NATIVE_DIR / "todos", owner_state_key="microharness")
        ),
        MemoryContextProvider(
            store=MemoryFileStore(MAF_NATIVE_DIR / "memory", owner_state_key="microharness"),
            recent_turns=2,
        ),
    ]


def build_native_middleware() -> list[Any]:
    """Build MAF middleware used by the native harness variant."""

    return [
        HarnessLifecycleMiddleware(),
        HarnessToolTraceMiddleware(),
        ToolApprovalMiddleware(),
    ]


def build_maf_native_agent(settings: Settings | None = None) -> Agent:
    """Create an agent using MAF-native context providers and middleware."""

    settings = settings or load_settings(require_model=True)
    return Agent(
        name="MicroHarnessMAFNative",
        instructions=(
            f"{INSTRUCTIONS}\n\n"
            "Variante MAF-native: usa ContextProvider, FileHistoryProvider, "
            "MemoryContextProvider, TodoProvider y middleware nativos de Microsoft Agent Framework."
        ),
        client=build_chat_client(settings),
        tools=HARNESS_TOOLS,
        context_providers=build_native_context_providers(),
        middleware=build_native_middleware(),
    )


def build_maf_native_agui_agent(settings: Settings | None = None) -> Agent | AgentFrameworkAgent:
    """Wrap the MAF-native agent for AG-UI when approvals are enabled."""

    settings = settings or load_settings()
    agent = build_maf_native_agent(settings)
    if settings.require_confirmation:
        return AgentFrameworkAgent(agent=agent, require_confirmation=True)
    return agent