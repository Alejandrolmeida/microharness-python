# MicroHarness architecture

MicroHarness is a small Agent Framework harness with a deliberately narrow scope:
turn a configured chat model into an operational agent with controlled context,
typed skills, session persistence, lifecycle traceability and a FastAPI + AG-UI host.

## Runtime layers

```text
Browser / CLI / Notebook
        ↓
FastAPI + AG-UI endpoint
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

## Files

- `src/microharness/config.py`: environment loading without committing secrets.
- `src/microharness/context.py`: context package assembled from local knowledge and session facts.
- `src/microharness/tools.py`: Agent Framework tools exposed as harness skills.
- `src/microharness/subagents.py`: bounded specialist delegation.
- `src/microharness/memory.py`: local JSON and Markdown persistence under `working/output/`.
- `src/microharness/lifecycle.py`: JSONL event trace for request and tool hooks.
- `src/microharness/harness.py`: model client, instructions and Agent construction.
- `src/microharness/server.py`: FastAPI app, `/agent`, `/api/chat`, `/health` and `/healthz`.

## Boundaries

- The repository does not store secrets.
- Tools are local, typed and non-destructive.
- External writes should pass through human approval.
- Runtime artifacts stay under `working/output/`.
