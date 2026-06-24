"""Small AG-UI terminal client for the MicroHarness demo."""

from __future__ import annotations

import asyncio
import os

from agent_framework import Agent, ToolCallContent, ToolResultContent
from agent_framework_ag_ui import AGUIChatClient
from dotenv import load_dotenv


async def run_client() -> None:
    """Run an interactive streaming terminal client."""

    load_dotenv()
    server_url = os.environ.get("AGUI_SERVER_URL", "http://127.0.0.1:8888/agent")
    print(f"Conectando a AG-UI en: {server_url}\n")

    chat_client = AGUIChatClient(server_url=server_url)
    agent = Agent(
        name="MicroHarnessClient",
        client=chat_client,
        instructions="Eres un cliente de demo. Mantén la conversación en español.",
    )
    session = agent.create_session()

    try:
        while True:
            message = input("\nUsuario (:q o quit para salir): ").strip()
            if not message:
                print("La petición no puede estar vacía.")
                continue
            if message.lower() in {":q", "quit", "exit"}:
                break

            print("\nAgente: ", end="", flush=True)
            async for update in agent.run(message, session=session, stream=True):
                if update.text:
                    print(update.text, end="", flush=True)

                for content in update.contents:
                    if isinstance(content, ToolCallContent):
                        print(f"\n[tool call: {content.name}]", flush=True)
                    elif isinstance(content, ToolResultContent):
                        print(f"\n[tool result: {content.result}]", flush=True)

            print()
    except KeyboardInterrupt:
        print("\nSaliendo...")


def main() -> None:
    """CLI entry point."""

    asyncio.run(run_client())


if __name__ == "__main__":
    main()
