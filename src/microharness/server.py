"""FastAPI + AG-UI host for the MicroHarness agent."""

from __future__ import annotations

from pathlib import Path

import uvicorn
from agent_framework_ag_ui import add_agent_framework_fastapi_endpoint
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from microharness.config import Settings, load_settings
from microharness.harness import build_agui_agent

ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = ROOT / "web" / "static"


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
