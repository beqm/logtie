import atexit
import logging
import queue
from dataclasses import dataclass
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from typing import Any

from ._constants import Colors, LogFmt, TimeFmt, DEFAULT_FMT, DEFAULT_DATEFMT
from ._formatters import CustomFormatter, JSONFormatter, LevelFilter, LineRotatingFileHandler


def _resolve_fmt(fmt: LogFmt | str | None) -> str:
    if isinstance(fmt, LogFmt):
        return fmt.to_logging_fmt()
    return fmt or DEFAULT_FMT


def _resolve_datefmt(datefmt: TimeFmt | str | None) -> str:
    if isinstance(datefmt, TimeFmt):
        return datefmt.to_strftime()
    return datefmt or DEFAULT_DATEFMT


@dataclass
class Stdout:
    """Configuration for the stdout (terminal) log handler.

    Pass ``True`` to ``configure(stdout=True)`` to use all defaults.

    Args:
        fmt:     Log line layout. Use ``LogFmt("[timestamp] [level] - [message]")``
                 or a raw ``logging`` format string.
        datefmt: Timestamp format. Use ``TimeFmt("[year]-[month]-[day]")``,
                 ``"iso"`` for ISO 8601, or a raw ``strftime`` format string.
        colored: Enable ANSI colored level names.
        colors:  Per-level color overrides (see ``Colors``).
        level:   Minimum level emitted by this handler. Defaults to ``DEBUG``.
        only:    Emit only records matching these exact levels.
                 Example: ``only=[log.WARNING, log.ERROR]``
        spacing: Pad level names to a fixed width so the message column aligns
                 across all levels (``DEBUG`` through ``CRITICAL``).
    """

    fmt:     LogFmt | str | None = None
    datefmt: TimeFmt | str | None = None
    colored: bool = False
    colors:  Colors | None = None
    level:   int = logging.DEBUG
    only:    list[int] | None = None
    spacing: bool = False


@dataclass
class File:
    """Configuration for the file log handler.

    Pass a path string to ``configure(file="app.log")`` to use all defaults.

    Args:
        path:         Destination file path.
        fmt:          Log line layout (ignored when ``json=True``).
        datefmt:      Timestamp format. Accepts ``TimeFmt``, ``"iso"``, or strftime string.
        level:        Minimum level emitted by this handler. Defaults to ``DEBUG``.
        only:         Emit only records matching these exact levels.
        json:         Write each record as a JSON object.
        json_fmt:     Mapping of ``logging.LogRecord`` field → JSON key name.
                      Defaults to ``DEFAULT_JSON_FMT`` when omitted.
        encoding:     File encoding. Defaults to ``"utf-8"``.
        rotate_size:  Rotate when the file reaches this many bytes
                      (e.g. ``5 * 1024 * 1024`` for 5 MB). Mutually exclusive
                      with ``rotate_lines``.
        rotate_lines: Rotate when the file reaches this many lines.
                      Mutually exclusive with ``rotate_size``.
        backup_count: Number of rotated backup files to keep. Defaults to ``5``.
    """

    path:         str = ""
    fmt:          LogFmt | str | None = None
    datefmt:      TimeFmt | str | None = None
    level:        int = logging.DEBUG
    only:         list[int] | None = None
    json:         bool = False
    json_fmt:     dict[str, str] | None = None
    encoding:     str = "utf-8"
    rotate_size:  int | None = None
    rotate_lines: int | None = None
    backup_count: int = 5


_instance: "LogConfig | None" = None


class LogConfig:
    def __init__(
        self,
        name: str,
        level: int,
        stdout: bool | Stdout,
        file: str | File | None,
        queue_mode: bool,
    ) -> None:
        self._name = name
        self._queue_listener: QueueListener | None = None
        self._setup(level, stdout, file, queue_mode)
        atexit.register(self._shutdown)

    @property
    def name(self) -> str:
        return self._name

    def _setup(
        self,
        level: int,
        stdout_cfg: bool | Stdout,
        file_cfg: str | File | None,
        queue_mode: bool,
    ) -> None:
        logger = logging.getLogger(self._name)
        logger.setLevel(level)
        logger.handlers.clear()
        logger.propagate = False

        handlers: list[logging.Handler] = []

        if stdout_cfg is not False:
            cfg = stdout_cfg if isinstance(stdout_cfg, Stdout) else Stdout()
            handlers.append(self._build_stdout_handler(cfg))

        if file_cfg is not None:
            cfg_file = file_cfg if isinstance(file_cfg, File) else File(path=file_cfg)
            handlers.append(self._build_file_handler(cfg_file))

        if queue_mode and handlers:
            log_queue: queue.Queue[Any] = queue.Queue()
            self._queue_listener = QueueListener(
                log_queue, *handlers, respect_handler_level=True
            )
            self._queue_listener.start()
            logger.addHandler(QueueHandler(log_queue))
        else:
            for h in handlers:
                logger.addHandler(h)

    def _build_stdout_handler(self, cfg: Stdout) -> logging.Handler:
        formatter = CustomFormatter(
            _resolve_fmt(cfg.fmt),
            _resolve_datefmt(cfg.datefmt),
            colored=cfg.colored,
            colors=cfg.colors,
            spacing=cfg.spacing,
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.setLevel(cfg.level)
        if cfg.only:
            handler.addFilter(LevelFilter(cfg.only))
        return handler

    def _build_file_handler(self, cfg: File) -> logging.Handler:
        datefmt = _resolve_datefmt(cfg.datefmt)
        if cfg.json:
            formatter: logging.Formatter = JSONFormatter(
                datefmt=datefmt, json_fmt=cfg.json_fmt
            )
        else:
            formatter = CustomFormatter(_resolve_fmt(cfg.fmt), datefmt)

        if cfg.rotate_size is not None:
            handler: logging.Handler = RotatingFileHandler(
                cfg.path,
                maxBytes=cfg.rotate_size,
                backupCount=cfg.backup_count,
                encoding=cfg.encoding,
            )
        elif cfg.rotate_lines is not None:
            handler = LineRotatingFileHandler(
                cfg.path,
                max_lines=cfg.rotate_lines,
                backup_count=cfg.backup_count,
                encoding=cfg.encoding,
            )
        else:
            handler = logging.FileHandler(cfg.path, encoding=cfg.encoding)

        handler.setFormatter(formatter)
        handler.setLevel(cfg.level)
        if cfg.only:
            handler.addFilter(LevelFilter(cfg.only))
        return handler

    def _shutdown(self) -> None:
        if self._queue_listener:
            self._queue_listener.stop()


def configure(
    name: str = "app",
    level: int = logging.DEBUG,
    stdout: bool | Stdout = False,
    file: str | File | None = None,
    queue: bool = False,
) -> LogConfig:
    """Configure the pystruments logger. Call once at application startup.

    Args:
        name:   Logger name. Defaults to ``"app"``.
        level:  Global minimum level. Nothing below this is processed by any handler.
        stdout: Terminal handler. ``True`` for defaults, or a ``Stdout`` instance.
        file:   File handler. A path string for defaults, or a ``File`` instance.
        queue:  Route all handlers through a background queue (async-safe logging).

    Returns:
        ``LogConfig`` instance (can be safely ignored).

    Example::

        log.configure(
            name="myapp",
            level=log.DEBUG,
            stdout=log.Stdout(
                fmt=log.LogFmt("[timestamp] [level] - [message]"),
                datefmt=log.TimeFmt("[day]/[month]/[year] [hour]:[minute]:[second]"),
                colored=True,
            ),
            file=log.File(path="app.log", datefmt="iso", json=True),
            queue=True,
        )
    """
    global _instance
    _instance = LogConfig(name, level, stdout, file, queue)
    return _instance


def _get_logger_name() -> str:
    return _instance.name if _instance else "app"
