"""Context manager for assembling the information sent to the agent."""

from __future__ import annotations

from dataclasses import dataclass

from microharness.memory import read_facts, read_harness_context_file, read_session_state


@dataclass(frozen=True)
class HarnessContext:
    """Context package prepared by the harness before an agent turn."""

    session_id: str
    source: str
    knowledge: str
    facts: list[str]
    run_count: int

    def as_prompt_block(self) -> str:
        """Render the context as a compact block suitable for model instructions."""

        facts = "\n".join(f"- {fact}" for fact in self.facts) or "- Sin hechos persistidos."
        return (
            f"Session: {self.session_id}\n"
            f"Runs: {self.run_count}\n"
            f"Source: {self.source}\n\n"
            f"Persisted facts:\n{facts}\n\n"
            f"Knowledge:\n{self.knowledge.strip()}"
        )


class ContextManager:
    """Load controlled knowledge and scoped session memory."""

    def build(self, session_id: str = "default") -> HarnessContext:
        """Build the context package for one agent turn."""

        state = read_session_state()
        return HarnessContext(
            session_id=session_id.strip() or "default",
            source="working/contexto_harness.md",
            knowledge=read_harness_context_file(),
            facts=read_facts(session_id),
            run_count=int(state.get("run_count") or 0),
        )