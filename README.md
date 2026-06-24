# MicroHarness Python

MicroHarness Python es una demo pequeña y cronometrada para explicar cómo un **Agent Harness** convierte un modelo en un agente operativo: añade tools, contexto controlado, estado de sesión y una capa de interacción mediante **FastAPI + AG-UI**.

La demo está pensada para una explicación de **5 minutos** inspirada en la sesión BRK243 de Microsoft Build, pero implementada en Python para que sea fácil de narrar y modificar.

## Qué demuestra

- **Agent Loop**: observar, decidir, usar tools y sintetizar.
- **Tools**: funciones Python tipadas que aportan capacidades verificables.
- **Contexto controlado**: lectura de `working/contexto_harness.md` mediante una tool.
- **Sesión simple**: estado persistido en `working/output/session_state.json`.
- **Artefactos**: resumen guardado en `working/output/demo_summary.md`.
- **FastAPI + AG-UI**: endpoint principal de agente y fallback REST estable.

## Arquitectura

```text
Webapp / Notebook / Cliente
        ↓
FastAPI + AG-UI
        ↓
Microsoft Agent Framework
        ↓
MicroHarness
  ├─ tools
  ├─ contexto
  ├─ estado simple
  └─ artefactos
        ↓
Azure OpenAI / Foundry model
```

Estructura principal:

```text
src/microharness/
  config.py      # carga segura de configuración local
  harness.py     # convierte modelo + tools + instrucciones en Agent
  memory.py      # persistencia simple para sesión y artefactos
  server.py      # FastAPI + AG-UI + fallback REST
  client.py      # cliente terminal AG-UI interactivo
  tools.py       # tools de contexto, resumen y demo
working/
  contexto_harness.md
  fallback/
  output/
notebooks/
  01_agent_loop_basico.ipynb
  02_tools_y_contexto.ipynb
  03_microharness_fastapi_agui.ipynb
  04_guion_demo_5_minutos.ipynb
scripts/
  load_model_from_akv.sh
  run_demo_client.py
  smoke_agui.py
web/static/
  index.html
```

## Requisitos

- Python 3.10+
- Acceso a un modelo Azure OpenAI / Microsoft Foundry
- Azure CLI autenticado si cargas secretos desde Azure Key Vault

No instales dependencias durante la demo. Prepara el entorno antes.

## Configuración

Instalación local:

```bash
cd /home/alejandrolmeida/source/github/alejandrolmeida/microharness-python
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --pre -e '.[dev]'
```

El repositorio no contiene secretos. La forma recomendada es reutilizar la configuración local de Azurebrains:

```bash
source scripts/load_model_from_akv.sh
```

También puedes copiar `.env.example` a `.env` y rellenar solo valores locales. Variables soportadas:

```bash
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_DEPLOYMENT=
AZURE_OPENAI_CHAT_COMPLETION_MODEL=
AZURE_OPENAI_MODEL=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_API_VERSION=
AZURE_OPENAI_BASE_URL=
MICROHARNESS_HOST=127.0.0.1
MICROHARNESS_PORT=8000
```

## Ejecución rápida

Arranca el servidor:

```bash
source .venv/bin/activate
source scripts/load_model_from_akv.sh
python -m microharness.server
```

Endpoints:

- Webapp: `http://127.0.0.1:8000/ui/`
- AG-UI: `http://127.0.0.1:8000/agent`
- Health: `http://127.0.0.1:8000/health`
- Health extendido: `http://127.0.0.1:8000/healthz`
- Fallback REST: `http://127.0.0.1:8000/api/chat`

Ejecuta el cliente de demo en otra terminal:

```bash
source .venv/bin/activate
python scripts/run_demo_client.py
```

El cliente imprime:

1. prompt enviado,
2. respuesta del agente,
3. ruta del artefacto generado,
4. estado de sesión.

## Demo en 5 minutos

### 0:00–0:45 — Presentación

> Vamos a ver una versión mínima de un harness en Python. No busca enseñar todas las capacidades de Agent Framework, sino el patrón: modelo, agente, tools, contexto, estado y endpoint.

### 0:45–1:45 — Código del agente

Mostrar:

- `src/microharness/harness.py`
- creación del agente,
- instrucciones,
- tools registradas.

Mensaje:

> Aquí está el paso del modelo al agente.

### 1:45–2:45 — Tools y contexto

Mostrar:

- `src/microharness/tools.py`
- `working/contexto_harness.md`

Mensaje:

> El agente puede consultar contexto controlado y generar artefactos.

### 2:45–3:45 — FastAPI / AG-UI

Mostrar:

- `src/microharness/server.py`
- `/agent`
- `/api/chat`
- `/health`

Mensaje:

> Esta es la capa que permitiría integrar el agente con una webapp, una app móvil o CopilotKit.

### 3:45–4:40 — Ejecución

Ejecutar:

```bash
python scripts/run_demo_client.py
```

Mostrar:

- respuesta,
- `working/output/demo_summary.md`,
- `working/output/session_state.json`.

### 4:40–5:00 — Cierre

> Esto es un micro-harness: modelo + agente + tools + contexto + sesión + endpoint de interacción. A partir de aquí se pueden añadir memoria persistente, planning, approvals, subagentes, MCP, CodeAct o despliegue en Foundry.

## Uso de notebooks

Los notebooks están pensados para una demo controlada por celdas:

1. `notebooks/01_agent_loop_basico.ipynb`: llamada básica o simulación.
2. `notebooks/02_tools_y_contexto.ipynb`: lectura de contexto y guardado de artefacto.
3. `notebooks/03_microharness_fastapi_agui.ipynb`: servidor, `/health` y `/api/chat`.
4. `notebooks/04_guion_demo_5_minutos.ipynb`: guion principal con plan B.

## Plan B

La demo no depende al 100% de la red. Si falla el modelo, AG-UI o FastAPI, usa:

- `working/fallback/expected_response.md`
- `working/fallback/expected_session_state.json`
- `working/fallback/expected_demo_summary.md`

El cliente `scripts/run_demo_client.py` también activa un plan B local si el servidor no responde.

## Camino principal y fallback

Camino principal:

1. Microsoft Agent Framework crea el agente.
2. AG-UI transmite eventos del agente.
3. FastAPI expone `/agent`.
4. La webapp o cliente consume el stream.

Fallback estable:

1. FastAPI expone `/api/chat`.
2. El endpoint ejecuta el agente y siempre guarda artefacto y estado.
3. Si el modelo falla, usa la respuesta pregenerada.

## Cómo extenderlo

Siguientes pasos naturales:

- memoria persistente en Cosmos DB, Blob Storage, PostgreSQL o Redis,
- approvals más visibles desde AG-UI,
- subagentes especializados,
- MCP servers para fuentes externas,
- observabilidad y evals,
- despliegue en Microsoft Foundry,
- UI React o integración con CopilotKit.

## Relación con BRK243

Esta demo no replica toda la arquitectura de la sesión BRK243. Toma el patrón conceptual —modelo + harness + tools + contexto + sesión + UI— y lo reduce a un proyecto Python pequeño, seguro y explicable en directo.

## Validación

```bash
python -m compileall src tests scripts
python -m pytest
python -m ruff check .
```

## Seguridad

- No se commitean claves, tokens, endpoints privados ni `.env`.
- `.env.example` contiene solo placeholders.
- Las tools son locales, simuladas y no destructivas.
- `scripts/load_model_from_akv.sh` oculta valores sensibles al imprimir.
