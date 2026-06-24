# MicroHarness Python

Demo mínima de Microsoft Agent Framework que muestra cómo convertir un modelo en un agente operativo mediante un pequeño harness en Python. El proyecto expone el agente con FastAPI y AG-UI para interacción en streaming desde una webapp o cliente externo.

## Qué enseña

- **Agent Loop**: observar, decidir, usar herramientas y responder.
- **Tools**: funciones Python tipadas y seguras invocadas por el agente.
- **Contexto**: prompt, turno actual, salidas de herramientas y estado temporal.
- **Sesión**: continuidad conversacional a través de AG-UI.
- **Extensiones**: memoria, planificación, approvals, MCP y despliegue en Foundry.

## Estructura

```text
src/microharness/
  config.py      # carga segura de configuración local
  harness.py     # convierte modelo + tools + instrucciones en Agent
  server.py      # FastAPI + endpoint AG-UI
  client.py      # cliente terminal AG-UI
  tools.py       # herramientas seguras de demo
web/static/      # webapp mínima para streaming
scripts/         # carga local desde Azure Key Vault
```

## Requisitos

- Python 3.10+
- Azure CLI autenticado si cargas secretos desde Azure Key Vault
- Acceso local a la configuración del modelo Azure GPT-5.5 Thinking

## Instalación local

```bash
cd /home/alejandrolmeida/source/github/alejandrolmeida/microharness-python
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --pre -e '.[dev]'
```

> Microsoft Agent Framework y su integración AG-UI pueden publicarse como paquetes prerelease; por eso se usa `--pre`.

## Configuración del modelo custom Azure GPT-5.5 Thinking

El repositorio no contiene secretos. La forma recomendada es reutilizar la configuración local de Azurebrains:

```bash
source scripts/load_model_from_akv.sh
```

Ese script lee por defecto `~/.config/azurebrains/copilot-azurebrains.env`, toma de ahí el nombre del Key Vault y carga estos secretos:

- `azure-openai-base-url`
- `azure-openai-model`
- `azure-openai-api-key`
- `azure-openai-max-completion-tokens`

También puedes crear un `.env` local desde `.env.example`. Los archivos `.env` y `.env.*` están ignorados por git.

## Ejecutar servidor FastAPI + AG-UI

```bash
source .venv/bin/activate
source scripts/load_model_from_akv.sh
python -m microharness.server
```

Endpoints locales:

- Webapp: `http://127.0.0.1:8888/ui/`
- AG-UI: `http://127.0.0.1:8888/agent`
- Health: `http://127.0.0.1:8888/healthz`

## Ejecutar cliente terminal

En otra terminal:

```bash
source .venv/bin/activate
export AGUI_SERVER_URL="http://127.0.0.1:8888/agent"
python -m microharness.client
```

Prompts útiles para la demo:

- “Explica el agent loop y usa una herramienta.”
- “Recuerda que esta sesión es para una charla pública.”
- “Lee el contexto de la sesión live-demo.”
- “Propón cómo extender esto a MCP y Foundry.”

## Approvals

La herramienta `propose_foundry_deployment` está marcada con aprobación obligatoria, pero el flujo human-in-the-loop se activa solo si defines:

```bash
export MICROHARNESS_REQUIRE_CONFIRMATION=true
```

Así la demo básica permanece fluida y puedes activar approvals cuando quieras explicar el patrón.

## Seguridad

- No se commitean claves, tokens, endpoints privados ni `.env`.
- `.env.example` contiene solo placeholders y nombres de secretos.
- `scripts/load_model_from_akv.sh` imprime valores sensibles ocultos.
- Las herramientas incluidas son simuladas y no ejecutan acciones destructivas.

## Validación

```bash
python -m compileall src tests
python -m pytest
python -m ruff check .
```

## Recursos

- [Microsoft Agent Framework](https://learn.microsoft.com/agent-framework/)
- [AG-UI integration](https://learn.microsoft.com/agent-framework/integrations/ag-ui/)
