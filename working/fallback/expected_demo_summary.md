# MicroHarness demo summary

**Generated at:** fallback

## Prompt

Explícame Agent Harness en 5 bullets para una audiencia técnica. Usa el contexto disponible y separa Agent Loop, Tools, Memory, Planning y Permissions.

## Agent response

- **Agent Loop:** el harness organiza el ciclo observar, decidir, usar tools y sintetizar una respuesta breve.
- **Tools:** el agente consulta `working/contexto_harness.md` mediante una tool, en vez de depender solo del conocimiento del modelo.
- **Memory:** se guarda estado simple en `working/output/session_state.json` con timestamp, prompt, resumen y contador.
- **Planning:** el harness puede evolucionar hacia planificación explícita para dividir objetivos en pasos controlados.
- **Permissions:** las acciones sensibles deberían pasar por approvals o human-in-the-loop antes de ejecutarse.
