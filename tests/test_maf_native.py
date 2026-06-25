from __future__ import annotations

from microharness.maf_native import build_native_context_providers, build_native_middleware


def test_build_native_context_providers():
    providers = build_native_context_providers()

    source_ids = [provider.source_id for provider in providers]

    assert "file_history" in source_ids
    assert "microharness_context" in source_ids
    assert "todo" in source_ids
    assert "memory" in source_ids


def test_build_native_middleware():
    middleware = build_native_middleware()

    middleware_names = {type(item).__name__ for item in middleware}

    assert "HarnessLifecycleMiddleware" in middleware_names
    assert "HarnessToolTraceMiddleware" in middleware_names
    assert "ToolApprovalMiddleware" in middleware_names