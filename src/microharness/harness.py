"""The small harness that turns a model into an operational agent."""

from __future__ import annotations

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient
from agent_framework_ag_ui import AgentFrameworkAgent
from azure.identity import AzureCliCredential

from microharness.config import Settings, load_settings
from microharness.tools import DEMO_TOOLS

INSTRUCTIONS = """
Eres MicroHarness, un agente de demostración para explicar Microsoft Agent Framework.
Responde en español, de forma breve, visual y didáctica.

Objetivo de la demo:
- Mostrar el Agent Loop: observar, decidir, usar herramientas y sintetizar.
- Explicar herramientas, contexto y sesión con ejemplos concretos.
- Mantener el foco en una demo mínima en Python, FastAPI y AG-UI.
- Si el usuario pregunta por memoria, planificación, approvals, MCP o Foundry,
  explica que son extensiones naturales del harness.
- Usa herramientas cuando aporten trazabilidad a la explicación.
""".strip()


def build_chat_client(settings: Settings | None = None) -> OpenAIChatCompletionClient:
    """Build an Agent Framework chat client for the configured model."""

    settings = settings or load_settings()
    kwargs: dict[str, object] = {"model": settings.model}

    if settings.base_url:
        kwargs["base_url"] = settings.base_url
        if settings.api_key:
            kwargs["api_key"] = settings.api_key
    else:
        kwargs["azure_endpoint"] = settings.azure_endpoint
        if settings.api_version:
            kwargs["api_version"] = settings.api_version
        if settings.api_key:
            kwargs["api_key"] = settings.api_key
        else:
            kwargs["credential"] = AzureCliCredential()

    return OpenAIChatCompletionClient(**kwargs)


def build_agent(settings: Settings | None = None) -> Agent:
    """Create the Microsoft Agent Framework agent with the demo tool belt."""

    return Agent(
        name="MicroHarness",
        instructions=INSTRUCTIONS,
        client=build_chat_client(settings),
        tools=DEMO_TOOLS,
    )


def build_agui_agent(settings: Settings | None = None) -> Agent | AgentFrameworkAgent:
    """Wrap the agent for AG-UI when protocol features such as approvals are enabled."""

    settings = settings or load_settings()
    agent = build_agent(settings)

    if settings.require_confirmation:
        return AgentFrameworkAgent(agent=agent, require_confirmation=True)

    return agent
