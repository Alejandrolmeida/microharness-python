"""The harness that turns a configured model into an operational agent."""

from __future__ import annotations

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient
from agent_framework_ag_ui import AgentFrameworkAgent
from azure.identity import AzureCliCredential

from microharness.config import Settings, load_settings
from microharness.tools import HARNESS_TOOLS

INSTRUCTIONS = """
Eres MicroHarness, un agente de referencia construido con Microsoft Agent Framework.
Responde en español, de forma breve, práctica y trazable.

Responsabilidades del harness:
- Mantener el Agent Loop: observar, decidir, usar herramientas y sintetizar.
- Usar read_harness_context o build_context_snapshot cuando la respuesta dependa del contexto local.
- Usar skills tipadas para memoria, explicación de conceptos, delegación y artefactos.
- Delegar en subagentes cuando una tarea pida arquitectura, fiabilidad o seguridad.
- Guardar un artefacto con save_agent_artifact cuando produzcas una respuesta reutilizable.
- Tratar operaciones sensibles como propuestas que requieren aprobación humana.
""".strip()


def build_chat_client(settings: Settings | None = None) -> OpenAIChatCompletionClient:
    """Build an Agent Framework chat client for the configured model."""

    settings = settings or load_settings(require_model=True)
    if not settings.model:
        raise RuntimeError("El modelo no está configurado.")
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
    """Create the Microsoft Agent Framework agent with the harness skills."""

    return Agent(
        name="MicroHarness",
        instructions=INSTRUCTIONS,
        client=build_chat_client(settings),
        tools=HARNESS_TOOLS,
    )


def build_agui_agent(settings: Settings | None = None) -> Agent | AgentFrameworkAgent:
    """Wrap the agent for AG-UI when protocol features such as approvals are enabled."""

    settings = settings or load_settings()
    agent = build_agent(settings)

    if settings.require_confirmation:
        return AgentFrameworkAgent(agent=agent, require_confirmation=True)

    return agent
