from contextvars import ContextVar
from typing import Any

_log_context: ContextVar[dict[str, Any]] = ContextVar("_log_context", default={})


def bind(**kwargs: Any) -> None:
    """Inject key-value pairs into all subsequent log records within the current context.

    Thread-safe and async-safe (backed by ``contextvars``).

    Example::

        log.bind(request_id="abc-123", user_id=42)
        log.info("processing request")  # record includes request_id and user_id
    """
    current = _log_context.get().copy()
    current.update(kwargs)
    _log_context.set(current)


def unbind(*keys: str) -> None:
    """Remove specific keys from the current log context.

    Example::

        log.unbind("request_id", "user_id")
    """
    current = _log_context.get().copy()
    for key in keys:
        current.pop(key, None)
    _log_context.set(current)


def clear_binds() -> None:
    """Clear all injected context fields."""
    _log_context.set({})


def get_context() -> dict[str, Any]:
    return _log_context.get().copy()
