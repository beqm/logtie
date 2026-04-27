import logging
from dataclasses import dataclass

DEBUG    = logging.DEBUG
INFO     = logging.INFO
WARNING  = logging.WARNING
ERROR    = logging.ERROR
CRITICAL = logging.CRITICAL
NOTSET   = logging.NOTSET

DEFAULT_FMT     = "%(asctime)s %(name)s %(levelname)s - %(message)s"
DEFAULT_DATEFMT = "%d/%m/%Y %H:%M:%S"

RECORD_DEFAULTS: frozenset[str] = frozenset({
    "args", "asctime", "created", "exc_info", "exc_text",
    "filename", "funcName", "levelname", "levelno", "lineno",
    "module", "msecs", "message", "msg", "name", "pathname",
    "process", "processName", "relativeCreated", "stack_info",
    "thread", "threadName", "taskName",
})

DEFAULT_JSON_FMT: dict[str, str] = {
    "asctime":   "timestamp",
    "name":      "logger",
    "levelname": "level",
    "message":   "message",
    "funcName":  "function",
    "lineno":    "line",
}

# Internal placeholder used by TimeFmt to defer millisecond substitution
_MS_PLACEHOLDER = "__PYSTR_MS__"


class AnsiColor:
    """Standard ANSI terminal color escape codes."""

    BLACK          = "\033[30m"
    RED            = "\033[31m"
    GREEN          = "\033[32m"
    YELLOW         = "\033[33m"
    BLUE           = "\033[34m"
    MAGENTA        = "\033[35m"
    CYAN           = "\033[36m"
    WHITE          = "\033[37m"
    BRIGHT_BLACK   = "\033[90m"
    BRIGHT_RED     = "\033[91m"
    BRIGHT_GREEN   = "\033[92m"
    BRIGHT_YELLOW  = "\033[93m"
    BRIGHT_BLUE    = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN    = "\033[96m"
    BRIGHT_WHITE   = "\033[97m"
    RESET          = "\033[0m"


@dataclass
class Colors:
    """Per-level color configuration for colored terminal output.

    Each field accepts:

    - An ``AnsiColor`` constant  — e.g. ``AnsiColor.BRIGHT_GREEN``
    - A hex color string         — e.g. ``"#00D4AA"`` (requires truecolor terminal)
    """

    debug:    str = AnsiColor.BRIGHT_BLUE
    info:     str = AnsiColor.BRIGHT_GREEN
    warning:  str = AnsiColor.BRIGHT_YELLOW
    error:    str = AnsiColor.BRIGHT_RED
    critical: str = AnsiColor.BRIGHT_MAGENTA


class LogFmt:
    """Format descriptor for log line layout.

    Available tokens::

        [timestamp]  log timestamp (shaped by ``datefmt``)
        [name]       logger name
        [level]      log level name  (e.g. INFO, WARNING)
        [message]    log message body
        [module]     module name
        [function]   function name
        [line]       line number
        [path]       full file path
        [process]    process ID
        [thread]     thread ID

    Example::

        LogFmt("[timestamp] [name] [level] - [message]")
        LogFmt("[timestamp] [level] - [message] ([function]:[line])")
    """

    _TOKEN_MAP: dict[str, str] = {
        "[timestamp]": "%(asctime)s",
        "[name]":      "%(name)s",
        "[level]":     "%(levelname)s",
        "[message]":   "%(message)s",
        "[module]":    "%(module)s",
        "[function]":  "%(funcName)s",
        "[line]":      "%(lineno)d",
        "[path]":      "%(pathname)s",
        "[process]":   "%(process)d",
        "[thread]":    "%(thread)d",
    }

    def __init__(self, template: str) -> None:
        self._template = template

    def to_logging_fmt(self) -> str:
        result = self._template
        for token, fmt in self._TOKEN_MAP.items():
            result = result.replace(token, fmt)
        return result


class TimeFmt:
    """Format descriptor for timestamp formatting.

    Available tokens::

        [year]    4-digit year         (e.g. 2026)
        [month]   2-digit month        (01–12)
        [day]     2-digit day          (01–31)
        [hour]    2-digit hour, 24h    (00–23)
        [minute]  2-digit minute       (00–59)
        [second]  2-digit second       (00–59)
        [ms]      3-digit milliseconds (000–999)
        [tz]      timezone offset      (e.g. +03:00)

    Example::

        TimeFmt("[year]-[month]-[day] [hour]:[minute]:[second]")
        TimeFmt("[day]/[month]/[year] [hour]:[minute]:[second].[ms]")
    """

    _TOKEN_MAP: dict[str, str] = {
        "[year]":   "%Y",
        "[month]":  "%m",
        "[day]":    "%d",
        "[hour]":   "%H",
        "[minute]": "%M",
        "[second]": "%S",
        "[tz]":     "%z",
    }

    def __init__(self, template: str) -> None:
        self._template = template
        self.has_ms = "[ms]" in template

    def to_strftime(self) -> str:
        result = self._template
        for token, fmt in self._TOKEN_MAP.items():
            result = result.replace(token, fmt)
        if self.has_ms:
            result = result.replace("[ms]", _MS_PLACEHOLDER)
        return result
