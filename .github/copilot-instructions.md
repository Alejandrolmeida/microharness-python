# Instrucciones para GitHub Copilot — MicroHarness Python

Este repositorio contiene una demo pública de Microsoft Agent Framework en Python.

## Objetivo

Explicar cómo un pequeño harness convierte un modelo en agente operativo con:

- Agent Loop,
- tools,
- contexto,
- sesión,
- FastAPI,
- AG-UI streaming.

## Reglas

- Mantén el proyecto mínimo, claro y pedagógico.
- No conviertas la demo en una plataforma grande salvo petición explícita.
- No inventes nombres de modelos, endpoints ni arquitectura privada.
- Prioriza ejemplos seguros y simulados.
- No incluyas secretos, tokens, claves, endpoints privados ni `.env`.
- Usa `.env.example` solo con placeholders y nombres de secretos.
- Si se cambia la configuración del modelo, conserva la compatibilidad con `scripts/load_model_from_akv.sh`.

## Estilo

- Código Python sencillo, tipado y fácil de narrar en directo.
- README orientado a demo pública.
- Cambios pequeños y revisables.
