# MicroHarness Python

MicroHarness Python es un ejemplo pequeño de **Agent Harness** con Microsoft Agent Framework. El repositorio muestra cómo pasar de un modelo de chat a un agente operativo añadiendo contexto controlado, skills, subagentes, memoria de sesión, lifecycle hooks y publicación con **FastAPI + AG-UI**.

El objetivo es que cualquier usuario que llegue desde GitHub pueda entender la arquitectura, ejecutar una prueba mínima y recorrer los notebooks para ver cómo se construye cada pieza.

## Qué incluye

- **Agent Loop**: observar la petición, decidir si necesita skills, incorporar resultados y sintetizar.
- **Context Manager**: empaqueta conocimiento local y hechos persistidos antes de un turno.
- **Skills / Tools**: funciones Python tipadas expuestas al agente con `@tool`.
- **Sub-agents**: especialistas deterministas para arquitectura, fiabilidad y seguridad.
- **Memory**: estado JSON, facts por sesión, trazas de tools y artefactos Markdown.
- **Lifecycle Hooks**: eventos `before_request`, `after_request`, `before_tool` y `after_tool` en JSONL.
- **FastAPI + AG-UI**: endpoint streaming `/agent`, endpoint JSON `/api/chat` y web local `/ui/`.

## Arquitectura

```text
Browser / CLI / Notebook
        ↓
FastAPI + AG-UI
        ↓
Microsoft Agent Framework Agent
        ↓
MicroHarness runtime
  ├─ configuration
  ├─ context manager
  ├─ skills / tools
  ├─ deterministic sub-agents
  ├─ file-backed memory
  └─ lifecycle hooks
        ↓
Azure OpenAI / compatible model endpoint
```

Estructura principal:

```text
src/microharness/
  config.py       # carga segura de configuración local
  context.py      # context manager
  lifecycle.py    # hooks y trazas JSONL
  subagents.py    # especialistas acotados
  tools.py        # skills del agente
  memory.py       # persistencia local
  harness.py      # construcción del Agent Framework Agent
  server.py       # FastAPI + AG-UI + endpoint JSON
  client.py       # cliente terminal AG-UI interactivo
docs/
  architecture.md
notebooks/
  01_configuracion_entorno.ipynb
  02_context_manager.ipynb
  03_skills_y_tools.ipynb
  04_subagentes.ipynb
  05_memoria_y_sesiones.ipynb
  06_lifecycle_hooks.ipynb
  07_fastapi_agui.ipynb
working/
  contexto_harness.md
  reference/
  output/
web/static/
  index.html
```

## Requisitos

- Python 3.10+
- Un despliegue Azure OpenAI o endpoint compatible con OpenAI
- Azure CLI autenticado si cargas valores desde Azure Key Vault

El repositorio no contiene secretos. Usa `.env` local, variables de entorno o `scripts/load_model_from_akv.sh`.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --pre -e '.[dev]'
```

Configura el modelo con una de estas opciones:

```bash
source scripts/load_model_from_akv.sh
```

o copia `.env.example` a `.env` y rellena valores locales:

```bash
AZURE_OPENAI_BASE_URL="https://<resource>.openai.azure.com/openai/v1"
AZURE_OPENAI_API_KEY="<your-api-key>"
AZURE_OPENAI_CHAT_COMPLETION_MODEL="<your-deployment-name>"
MICROHARNESS_HOST="127.0.0.1"
MICROHARNESS_PORT="8000"
```

## Ejecución

Arranca el servidor:

```bash
source .venv/bin/activate
source scripts/load_model_from_akv.sh
python -m microharness.server
```

Endpoints:

- Web: `http://127.0.0.1:8000/ui/`
- AG-UI: `http://127.0.0.1:8000/agent`
- JSON: `http://127.0.0.1:8000/api/chat`
- Health: `http://127.0.0.1:8000/health`
- Health extendido: `http://127.0.0.1:8000/healthz`

Prueba rápida del endpoint JSON:

```bash
python scripts/run_request.py
```

Prueba rápida del stream AG-UI:

```bash
python scripts/smoke_agui.py "Explica el context manager del harness"
```

## Notebooks

Los notebooks están pensados como un recorrido incremental por la construcción del harness:

1. `notebooks/01_configuracion_entorno.ipynb`: variables, `.env`, Key Vault y `Settings`.
2. `notebooks/02_context_manager.ipynb`: lectura de conocimiento local y composición del contexto.
3. `notebooks/03_skills_y_tools.ipynb`: tools tipadas, artefactos y permisos.
4. `notebooks/04_subagentes.ipynb`: delegación a especialistas acotados.
5. `notebooks/05_memoria_y_sesiones.ipynb`: facts, estado JSON y continuidad.
6. `notebooks/06_lifecycle_hooks.ipynb`: trazas alrededor de peticiones y tools.
7. `notebooks/07_fastapi_agui.ipynb`: publicación con FastAPI, `/api/chat` y `/agent`.

## Artefactos de ejecución

El runtime escribe únicamente en `working/output/`:

- `agent_summary.md`: último artefacto generado.
- `session_state.json`: contador de ejecuciones, facts y trazas de tools.
- `lifecycle_trace.jsonl`: eventos de hooks.

`working/reference/` contiene respuestas reproducibles para ejecutar el recorrido sin credenciales de modelo.

## Validación

```bash
python -m compileall src scripts tests
PYTHONPATH=src python -m pytest
python -m ruff check .
```

## Seguridad

- No se commitean claves, tokens, endpoints privados ni `.env`.
- `.env.example` contiene solo placeholders.
- Las skills incluidas son locales y no destructivas.
- Las acciones sensibles deben modelarse con aprobación humana.
