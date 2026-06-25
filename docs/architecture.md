# MicroHarness architecture

MicroHarness is a small Agent Framework harness with a deliberately narrow scope:
turn a configured chat model into an operational agent with controlled context,
typed skills, session persistence, lifecycle traceability and a FastAPI + AG-UI host.

The repository now contains two complementary paths:

- A didactic microharness path with tiny local implementations for context,
        memory, lifecycle tracing and deterministic sub-agents.
- A MAF-native path that uses Microsoft Agent Framework primitives for
        `AgentSession`, `ContextProvider`, `FileHistoryProvider`,
        `MemoryContextProvider`, `TodoProvider`, `ToolApprovalMiddleware` and
        agent/function middleware.

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
- `src/microharness/maf_native.py`: MAF-native context providers, session history,
  memory, todos and middleware.
- `src/microharness/server.py`: FastAPI app, `/agent`, `/api/chat`, `/health` and `/healthz`.

## MAF-native variant

The MAF-native variant keeps the same safe tools and model configuration, but
moves harness responsibilities into Agent Framework extension points:

| Responsibility | MAF-native primitive |
| --- | --- |
| Conversation continuity | `AgentSession` + `FileHistoryProvider` |
| Context injection | custom `ContextProvider` |
| Durable memory experiment | `MemoryContextProvider` + `MemoryFileStore` |
| Planning state | `TodoProvider` + `TodoFileStore` |
| Request tracing | `AgentMiddleware` |
| Tool tracing | `FunctionMiddleware` |
| Human approvals | `ToolApprovalMiddleware` + AG-UI wrapper |

It is exposed through `/api/chat/maf-native` for JSON calls and
`/agent/maf-native` for AG-UI streaming.

Some MAF harness APIs are currently preview/experimental. The code keeps them
isolated in `src/microharness/maf_native.py` so the didactic baseline remains
small and easy to review.

## Boundaries

- The repository does not store secrets.
- Tools are local, typed and non-destructive.
- External writes should pass through human approval.
- Runtime artifacts stay under `working/output/`.
