# Contexto controlado para MicroHarness Python

Este fichero representa una fuente de conocimiento controlada por el harness. En una demo real podría ser SharePoint, GitHub, Azure DevOps, Cost Management, Business Central o un MCP server.

## Agent Loop

El Agent Loop es el ciclo observar → decidir → actuar → sintetizar. El modelo no responde una sola vez: puede decidir usar tools, incorporar resultados y continuar hasta producir una respuesta útil.

## Context Management

El contexto es la información que el harness decide entregar al modelo: instrucciones, turno actual, historial relevante, resultados de tools, políticas y datos de negocio. Gestionarlo evita depender únicamente del conocimiento general del modelo.

## Skills and Tools

Las tools son funciones controladas que el agente puede invocar para leer datos, ejecutar validaciones o generar artefactos. En Python se modelan como funciones tipadas y seguras.

## Sub-agents

Los subagentes permiten delegar tareas especializadas. No son necesarios en esta demo, pero son un siguiente paso natural cuando una solución crece.

## Memory and Session Persistence

La memoria o estado de sesión permite conservar información entre ejecuciones: último prompt, resumen generado, contador de ejecuciones o trazas de tools. En producción podría vivir en Cosmos DB, Blob Storage, PostgreSQL o Redis.

## Lifecycle Hooks

Los lifecycle hooks permiten observar o intervenir en momentos clave: antes de llamar al modelo, antes o después de ejecutar una tool, al finalizar una respuesta o al registrar telemetría.

## Permissions and Human-in-the-loop

Las permissions y approvals separan acciones seguras de acciones sensibles. Una lectura de contexto puede ser automática; un despliegue, borrado o compra debería requerir confirmación humana.

## Microsoft Agent Framework

Microsoft Agent Framework proporciona primitivas para construir agentes: instrucciones, tools, sesiones, modelos, streaming y patrones de integración.

## AG-UI

AG-UI es un protocolo para conectar agentes con interfaces. Permite transmitir eventos como texto incremental, llamadas a tools, resultados, errores y solicitudes de aprobación.

## Foundry

Microsoft Foundry es el camino de producción para modelos, evaluaciones, observabilidad, seguridad y despliegue empresarial de soluciones de IA generativa.
