"""Deterministic sub-agents used by the harness for delegated reasoning."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SubAgentResult:
    """Result returned by a specialized sub-agent."""

    name: str
    focus: str
    result: str


class SubAgentRegistry:
    """Small registry that keeps delegation explicit and testable."""

    def run(self, name: str, task: str) -> SubAgentResult:
        """Delegate a task to a named specialist."""

        normalized = name.strip().lower() or "architect"
        handlers = {
            "architect": self._architect,
            "reliability": self._reliability,
            "security": self._security,
        }
        handler = handlers.get(normalized, self._architect)
        return handler(task.strip())

    def _architect(self, task: str) -> SubAgentResult:
        return SubAgentResult(
            name="architect",
            focus="system decomposition",
            result=(
                "Mantén el harness en capas: configuración, contexto, skills, subagentes, "
                "memoria, lifecycle hooks y transporte HTTP/AG-UI. "
                f"Tarea analizada: {task}"
            ),
        )

    def _reliability(self, task: str) -> SubAgentResult:
        return SubAgentResult(
            name="reliability",
            focus="runtime stability",
            result=(
                "Valida entradas, registra trazas compactas, conserva respuestas de referencia "
                "para entornos sin credenciales y limita efectos laterales a working/output. "
                f"Tarea analizada: {task}"
            ),
        )

    def _security(self, task: str) -> SubAgentResult:
        return SubAgentResult(
            name="security",
            focus="permission boundaries",
            result=(
                "Separa lectura segura de acciones sensibles, no persistas secretos y usa "
                "aprobación humana para operaciones de despliegue o escritura externa. "
                f"Tarea analizada: {task}"
            ),
        )


SUBAGENTS = SubAgentRegistry()