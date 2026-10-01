from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any

try:
    from langfuse import get_client, observe, propagate_attributes

    LANGFUSE_SDK_AVAILABLE = True
except ImportError:  # pragma: no cover - chỉ dùng khi chưa cài requirements
    LANGFUSE_SDK_AVAILABLE = False

    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func

        return decorator

    class _DummySpan:
        """Dummy span that supports context manager and update/end calls."""

        def update(self, **kwargs: Any) -> "_DummySpan":
            return self

        def end(self) -> None:
            return None

        def __enter__(self) -> "_DummySpan":
            return self

        def __exit__(self, *args: Any) -> None:
            return None

    class _DummyClient:
        def update_current_span(self, **kwargs: Any) -> None:
            return None

        def update_current_generation(self, **kwargs: Any) -> None:
            return None

        def start_as_current_observation(self, **kwargs: Any) -> _DummySpan:
            return _DummySpan()

        def get_prompt(self, *args: Any, **kwargs: Any) -> None:
            return None

        def flush(self) -> None:
            return None

    def get_client():
        return _DummyClient()

    @contextmanager
    def propagate_attributes(**kwargs: Any):
        yield


def get_langfuse_client():
    return get_client()


def tracing_enabled() -> bool:
    return LANGFUSE_SDK_AVAILABLE and bool(
        os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")
    )


def score_current_trace(
    *,
    name: str,
    value: float,
    comment: str | None = None,
) -> None:
    """Report a score on the current trace (no-op if tracing is disabled)."""
    if not tracing_enabled():
        return
    try:
        client = get_langfuse_client()
        client.update_current_span(
            scores=[{"name": name, "value": value, "comment": comment}],
        )
    except Exception:
        # Scoring is best-effort; never fail a request because of it.
        pass


def flush_langfuse() -> None:
    """Flush any pending Langfuse events. Call before process exit."""
    if not tracing_enabled():
        return
    try:
        get_langfuse_client().flush()
    except Exception:
        pass
