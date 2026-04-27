import logging
from typing import Any

from ._config import configure, LogConfig, Stdout, File, _get_logger_name
from ._context import bind, unbind, clear_binds, get_context
from ._constants import (
    AnsiColor, Colors, LogFmt, TimeFmt,
    DEBUG, INFO, WARNING, ERROR, CRITICAL, NOTSET,
)

__all__ = [
    # configuration
    "configure",
    "Stdout", "File",
    # format descriptors
    "LogFmt", "TimeFmt",
    # color helpers
    "AnsiColor", "Colors",
    # context injection
    "bind", "unbind", "clear_binds",
    # levels
    "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NOTSET",
    # log functions
    "log", "debug", "info", "warning", "error", "exception", "critical",
    # utilities
    "get",
]

_LOGGING_RESERVED = frozenset({"exc_info", "stack_info", "stacklevel", "extra"})


def _split_kwargs(
    kwargs: dict[str, Any],
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    ctx = get_context()
    extra = {k: v for k, v in kwargs.items() if k not in _LOGGING_RESERVED}
    log_kwargs = {k: v for k, v in kwargs.items() if k in _LOGGING_RESERVED}
    merged = {**ctx, **extra}
    return (merged if merged else None), log_kwargs


def _logger() -> logging.Logger:
    return logging.getLogger(_get_logger_name())


def log(level: int, msg: str, *args: Any, stacklevel: int = 2, **kwargs: Any) -> None:
    """Emit a record at an arbitrary level.

    Use when the level is determined at runtime (e.g. read from config).
    For fixed levels prefer the dedicated functions below.

    Extra keyword arguments are attached to the record as structured fields::

        log.log(log.INFO, "event", user_id=42)
    """
    extra, lkw = _split_kwargs(kwargs)
    _logger().log(level, msg, *args, stacklevel=stacklevel, extra=extra, **lkw)


def debug(msg: str, *args: Any, stacklevel: int = 2, **kwargs: Any) -> None:
    """Emit a DEBUG record.

    Use for detailed diagnostic information that is only useful when tracing
    a problem: variable values, internal state, control-flow checkpoints.
    Typically disabled in production.

    Extra keyword arguments are attached to the record as structured fields::

        log.debug("cache miss", key="user:42", ttl=300)
    """
    extra, lkw = _split_kwargs(kwargs)
    _logger().debug(msg, *args, stacklevel=stacklevel, extra=extra, **lkw)


def info(msg: str, *args: Any, stacklevel: int = 2, **kwargs: Any) -> None:
    """Emit an INFO record.

    Use for normal operational events that confirm the application is
    behaving as expected: service started, request handled, job completed.

    Extra keyword arguments are attached to the record as structured fields::

        log.info("user logged in", user_id=42, method="oauth")
    """
    extra, lkw = _split_kwargs(kwargs)
    _logger().info(msg, *args, stacklevel=stacklevel, extra=extra, **lkw)


def warning(msg: str, *args: Any, stacklevel: int = 2, **kwargs: Any) -> None:
    """Emit a WARNING record.

    Use when something unexpected happened but the application can continue.
    Examples: deprecated usage, recoverable failures, threshold approaching.

    Extra keyword arguments are attached to the record as structured fields::

        log.warning("disk space low", used_pct=91, path="/var")
    """
    extra, lkw = _split_kwargs(kwargs)
    _logger().warning(msg, *args, stacklevel=stacklevel, extra=extra, **lkw)


def error(msg: str, *args: Any, stacklevel: int = 2, **kwargs: Any) -> None:
    """Emit an ERROR record.

    Use when the application failed to perform an operation but is still
    running. Examples: unhandled request, failed external call, invalid input.

    Extra keyword arguments are attached to the record as structured fields::

        log.error("payment failed", order_id="ORD-99", reason="timeout")
    """
    extra, lkw = _split_kwargs(kwargs)
    _logger().error(msg, *args, stacklevel=stacklevel, extra=extra, **lkw)


def exception(msg: str, *args: Any, stacklevel: int = 2, **kwargs: Any) -> None:
    """Emit an ERROR record with the current exception traceback appended.

    Must be called from inside an ``except`` block. The full traceback is
    captured automatically from ``sys.exc_info()`` — no need to pass it
    manually.

    In plain-text output the traceback is printed below the message.
    In JSON output it is serialised into the ``"exc_info"`` field as a string.

    Extra keyword arguments are attached to the record as structured fields::

        try:
            response = requests.get(url, timeout=5)
        except requests.Timeout:
            log.exception("upstream timed out", url=url, timeout=5)
    """
    extra, lkw = _split_kwargs(kwargs)
    _logger().exception(msg, *args, stacklevel=stacklevel, extra=extra, **lkw)


def critical(msg: str, *args: Any, stacklevel: int = 2, **kwargs: Any) -> None:
    """Emit a CRITICAL record.

    Use for severe failures that require immediate attention and likely
    mean the application cannot continue. Examples: database unreachable,
    out of memory, corrupted essential state.

    Extra keyword arguments are attached to the record as structured fields::

        log.critical("database connection lost", host="db-primary", retries=3)
    """
    extra, lkw = _split_kwargs(kwargs)
    _logger().critical(msg, *args, stacklevel=stacklevel, extra=extra, **lkw)


def get(name: str) -> logging.Logger:
    """Return a named ``logging.Logger`` directly, bypassing pystruments configuration."""
    return logging.getLogger(name)

