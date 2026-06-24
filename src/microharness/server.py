"""FastAPI + AG-UI host for the MicroHarness agent."""

from __future__ import annotations

from pathlib import Path

import uvicorn
from agent_framework_ag_ui import add_agent_framework_fastapi_endpoint
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from microharness.config import Settings, load_settings
from microharness.harness import build_agent, build_agui_agent
from microharness.memory import (
    SUMMARY_PATH,
    read_fallback_response,
    read_session_state,
    write_demo_summary,
)

ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = ROOT / "web" / "static"

DEMO_PROMPT = (
    "Explícame Agent Harness en 5 bullets para una audiencia técnica. "
    "Usa el contexto disponible y separa Agent Loop, Tools, Memory, Planning y Permissions."
)


class ChatRequest(BaseModel):
    """Stable REST payload for the fallback demo endpoint."""

    prompt: str = Field(default=DEMO_PROMPT, min_length=1)
    use_fallback: bool = True


class ChatResponse(BaseModel):
    """Stable REST response printed by the demo client."""

    prompt: str
    response: str
    artifact_path: str
    session_state: dict[str, object]
    fallback_used: bool = False


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the ASGI app and register the AG-UI endpoint."""

    settings = settings or load_settings()
    app = FastAPI(
        title="MicroHarness Python",
        description="Demo mínima de Microsoft Agent Framework con FastAPI y AG-UI.",
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/healthz")
    async def healthz() -> dict[str, object]:
        return {
            "status": "ok",
            "agent": "MicroHarness",
            "model": settings.model,
            "route": "base_url" if settings.uses_openai_compatible_url else "azure_endpoint",
            "approvals_enabled": settings.require_confirmation,
        }

    @app.get("/health")
    async def health() -> dict[str, str]:
        """Health endpoint requested by the five-minute demo instructions."""

        return {"status": "ok"}

    @app.post("/api/chat", response_model=ChatResponse)
    async def api_chat(request: ChatRequest) -> ChatResponse:
        """Stable REST fallback when the official AG-UI path is not the focus."""

        agent = build_agent(settings)
        fallback_used = False

        try:
            chunks: list[str] = []
            async for update in agent.run(request.prompt, stream=True):
                if update.text:
                    chunks.append(update.text)
            response_text = "".join(chunks).strip()
            if not response_text:
                raise RuntimeError("El modelo no devolvió texto.")
        except Exception:
            if not request.use_fallback:
                raise
            fallback_used = True
            response_text = read_fallback_response().strip()

        # Garantiza que la demo siempre deja un artefacto y estado persistido,
        # incluso si el agente no invocó la tool durante el plan B.
        session_state = write_demo_summary(prompt=request.prompt, summary=response_text)

        return ChatResponse(
            prompt=request.prompt,
            response=response_text,
            artifact_path=str(SUMMARY_PATH.relative_to(ROOT)),
            session_state=read_session_state() or session_state,
            fallback_used=fallback_used,
        )

    @app.get("/")
    async def root() -> RedirectResponse:
        return RedirectResponse(url="/ui/")

    if STATIC_DIR.exists():
        app.mount("/ui", StaticFiles(directory=STATIC_DIR, html=True), name="ui")

    add_agent_framework_fastapi_endpoint(app, build_agui_agent(settings), "/agent")
    return app


app = create_app()


def main() -> None:
    """Run the local development server."""

    settings = load_settings()
    uvicorn.run("microharness.server:app", host=settings.host, port=settings.port, reload=False)


if __name__ == "__main__":
    main()
