import json
import logging
import datetime as dt
from logging.handlers import RotatingFileHandler
from typing import Any

from ._constants import AnsiColor, Colors, RECORD_DEFAULTS, DEFAULT_JSON_FMT, _MS_PLACEHOLDER
from ._context import get_context


def _resolve_color(color: str) -> str:
    """Convert ``#RRGGBB`` hex to an ANSI truecolor escape, or return an ANSI code as-is."""
    if color.startswith("#") and len(color) == 7:
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        return f"\033[38;2;{r};{g};{b}m"
    return color


def _format_iso(timestamp: float) -> str:
    local_tz = dt.datetime.now().astimezone().tzinfo
    ms = int((timestamp % 1) * 1000)
    return (
        dt.datetime.fromtimestamp(timestamp, tz=local_tz)
        .replace(microsecond=ms * 1000)
        .isoformat(timespec="milliseconds")
    )


class LevelFilter(logging.Filter):
    """Restricts a handler to only emit records whose level is in the given set."""

    def __init__(self, levels: list[int]) -> None:
        super().__init__()
        self._levels = frozenset(levels)

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno in self._levels


class _BaseFormatter(logging.Formatter):
    """Shared timestamp handling for all formatters."""

    def __init__(self, fmt: str | None = None, datefmt: str | None = None) -> None:
        self._iso = datefmt == "iso"
        self._datefmt_internal = None if self._iso else datefmt
        super().__init__(fmt=fmt, datefmt=self._datefmt_internal)

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        if self._iso:
            return _format_iso(record.created)

        effective = datefmt or self._datefmt_internal

        if effective and _MS_PLACEHOLDER in effective:
            local_tz = dt.datetime.now().astimezone().tzinfo
            d = dt.datetime.fromtimestamp(record.created, tz=local_tz)
            return d.strftime(effective).replace(_MS_PLACEHOLDER, f"{int(record.msecs):03d}")

        return super().formatTime(record, effective)


_LEVEL_NAME_WIDTH = len("CRITICAL")  # longest standard level name


class CustomFormatter(_BaseFormatter):
    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        colored: bool = False,
        colors: Colors | None = None,
        spacing: bool = False,
    ) -> None:
        super().__init__(fmt, datefmt)
        self._colored = colored
        self._colors = colors or Colors()
        self._spacing = spacing

    _LEVEL_COLOR_ATTR: dict[str, str] = {
        "DEBUG":    "debug",
        "INFO":     "info",
        "WARNING":  "warning",
        "ERROR":    "error",
        "CRITICAL": "critical",
    }

    def formatMessage(self, record: logging.LogRecord) -> str:
        # Use a defaultdict so that %(field)s tokens present in the format
        # string but absent from the record render as "" instead of raising.
        class _Defaulted(dict):  # type: ignore[type-arg]
            def __missing__(self, key: str) -> str:
                return ""

        return self._style._fmt % _Defaulted(record.__dict__)  # type: ignore[attr-defined]

    def format(self, record: logging.LogRecord) -> str:
        original_levelname = record.levelname

        if self._spacing:
            record.levelname = original_levelname.rjust(_LEVEL_NAME_WIDTH)

        message = super().format(record)
        record.levelname = original_levelname  # always restore

        if self._colored:
            attr = self._LEVEL_COLOR_ATTR.get(original_levelname)
            if attr:
                ansi = _resolve_color(getattr(self._colors, attr))
                if self._spacing:
                    # Padding goes outside the color escape so terminal width is correct
                    padding = " " * (_LEVEL_NAME_WIDTH - len(original_levelname))
                    colored_level = f"{padding}{ansi}{original_levelname}{AnsiColor.RESET}"
                    message = message.replace(original_levelname.rjust(_LEVEL_NAME_WIDTH), colored_level, 1)
                else:
                    colored_level = f"{ansi}{original_levelname}{AnsiColor.RESET}"
                    message = message.replace(original_levelname, colored_level, 1)

        return message


class JSONFormatter(_BaseFormatter):
    def __init__(
        self,
        datefmt: str | None = None,
        json_fmt: dict[str, str] | None = None,
    ) -> None:
        super().__init__(datefmt=datefmt)
        self._json_fmt = json_fmt or DEFAULT_JSON_FMT

    def format(self, record: logging.LogRecord) -> str:
        log_record: dict[str, Any] = {}

        for record_field, json_key in self._json_fmt.items():
            if record_field == "asctime":
                log_record[json_key] = self.formatTime(record)
            elif record_field == "message":
                log_record[json_key] = record.getMessage()
            else:
                log_record[json_key] = getattr(record, record_field, None)

        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info:
            log_record["stack_info"] = self.formatStack(record.stack_info)

        for key, val in record.__dict__.items():
            if key not in RECORD_DEFAULTS and not key.startswith("_"):
                log_record[key] = val

        return json.dumps(log_record, default=str)


class LineRotatingFileHandler(RotatingFileHandler):
    """Rotates the log file when the written line count exceeds ``max_lines``.

    Backed by :class:`logging.handlers.RotatingFileHandler` for the actual
    rename/backup logic; only the rollover trigger is replaced.
    """

    def __init__(
        self,
        filename: str,
        max_lines: int = 1000,
        backup_count: int = 5,
        encoding: str = "utf-8",
    ) -> None:
        # maxBytes=0 disables RotatingFileHandler's own size check
        super().__init__(
            filename, maxBytes=0, backupCount=backup_count,
            encoding=encoding, delay=True,
        )
        self._max_lines = max_lines
        self._line_count = self._count_existing_lines()

    def _count_existing_lines(self) -> int:
        try:
            with open(self.baseFilename, encoding=self.encoding) as f:
                return sum(1 for _ in f)
        except (FileNotFoundError, OSError):
            return 0

    # Disable parent's size-based check — rotation is driven from emit()
    def shouldRollover(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        return False

    def emit(self, record: logging.LogRecord) -> None:
        try:
            if self._line_count >= self._max_lines:
                super().doRollover()
                self._line_count = 0
            logging.FileHandler.emit(self, record)
            self._line_count += 1
        except Exception:
            self.handleError(record)
