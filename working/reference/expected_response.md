# Reference response

- **Agent Loop:** observa la petición, decide si necesita skills, incorpora resultados y sintetiza.
- **Context Manager:** empaqueta instrucciones, conocimiento local y hechos persistidos por sesión.
- **Skills:** herramientas Python tipadas para leer contexto, recordar hechos, delegar y generar artefactos.
- **Sub-agents:** especialistas acotados para arquitectura, fiabilidad y seguridad.
- **Memory:** estado JSON y artefactos Markdown bajo `working/output/`.
- **Lifecycle Hooks:** eventos JSONL alrededor de peticiones y tools para trazabilidad.
