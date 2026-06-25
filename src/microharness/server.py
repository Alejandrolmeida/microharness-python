"""FastAPI + AG-UI host for the MicroHarness agent."""

from __future__ import annotations

from pathlib import Path

import uvicorn
from agent_framework_ag_ui import add_agent_framework_fastapi_endpoint
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from microharness.config import Settings, load_settings
from microharness.harness import build_agent, build_agui_agent
from microharness.lifecycle import HOOKS
from microharness.memory import (
    SUMMARY_PATH,
    read_reference_response,
    read_session_state,
    write_agent_artifact,
)

ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = ROOT / "web" / "static"

DEFAULT_PROMPT = (
    "Explica cómo este harness convierte un modelo en agente operativo. "
    "Separa Agent Loop, Context Manager, Skills, Sub-agents, Memory y Lifecycle Hooks."
)


class ChatRequest(BaseModel):
    """Stable REST payload for the HTTP agent endpoint."""

    prompt: str = Field(default=DEFAULT_PROMPT, min_length=1)
    session_id: str = Field(default="default", min_length=1)
    allow_reference_response: bool = True


class ChatResponse(BaseModel):
    """Stable REST response returned by the HTTP agent endpoint."""

    prompt: str
    response: str
    artifact_path: str
    session_state: dict[str, object]
    reference_response_used: bool = False


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the ASGI app and register the AG-UI endpoint."""

    settings = settings or load_settings()
    app = FastAPI(
        title="MicroHarness Python",
        description="Minimal Agent Framework harness with FastAPI and AG-UI.",
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
            "model_configured": settings.is_model_configured,
            "route": "base_url" if settings.uses_openai_compatible_url else "azure_endpoint",
            "approvals_enabled": settings.require_confirmation,
        }

    @app.get("/health")
    async def health() -> dict[str, str]:
        """Health endpoint for lightweight checks."""

        return {"status": "ok"}

    @app.post("/api/chat", response_model=ChatResponse)
    async def api_chat(request: ChatRequest) -> ChatResponse:
        """Run the agent through a simple JSON endpoint."""

        reference_response_used = False
        HOOKS.before_request(request.session_id, request.prompt)

        try:
            if not settings.is_model_configured:
                raise RuntimeError("El modelo no está configurado.")
            agent = build_agent(settings)
            chunks: list[str] = []
            async for update in agent.run(request.prompt, stream=True):
                if update.text:
                    chunks.append(update.text)
            response_text = "".join(chunks).strip()
            if not response_text:
                raise RuntimeError("El modelo no devolvió texto.")
        except Exception:
            if not request.allow_reference_response:
                raise
            reference_response_used = True
            response_text = read_reference_response().strip()

        session_state = write_agent_artifact(prompt=request.prompt, summary=response_text)
        HOOKS.after_request(request.session_id, response_text)

        return ChatResponse(
            prompt=request.prompt,
            response=response_text,
            artifact_path=str(SUMMARY_PATH.relative_to(ROOT)),
            session_state=read_session_state() or session_state,
            reference_response_used=reference_response_used,
        )

    @app.get("/")
    async def root() -> RedirectResponse:
        return RedirectResponse(url="/ui/")

    if STATIC_DIR.exists():
        app.mount("/ui", StaticFiles(directory=STATIC_DIR, html=True), name="ui")

    if settings.is_model_configured:
        add_agent_framework_fastapi_endpoint(app, build_agui_agent(settings), "/agent")
    else:

        @app.post("/agent")
        async def agent_requires_configuration() -> None:
            raise HTTPException(
                status_code=503,
                detail="Configura un modelo para habilitar el endpoint AG-UI.",
            )

    return app


app = create_app()


def main() -> None:
    """Run the local development server."""

    settings = load_settings()
    uvicorn.run("microharness.server:app", host=settings.host, port=settings.port, reload=False)


if __name__ == "__main__":
    main()
