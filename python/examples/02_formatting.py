"""Formatting: LogFmt tokens, TimeFmt tokens, raw format strings, ISO 8601."""

from python.src.logtie import log

# ── LogFmt + TimeFmt tokens ───────────────────────────────────────────────────
log.configure(
    name="fmt_demo",
    level=log.DEBUG,
    stdout=log.Stdout(
        fmt=log.LogFmt("[timestamp] [level] [function]:[line] - [message]"),
        datefmt=log.TimeFmt("[day]/[month]/[year] [hour]:[minute]:[second].[ms]"),
    ),
)

log.info("timestamp includes milliseconds")
log.debug("caller location in format")


# ── ISO 8601 timestamp ────────────────────────────────────────────────────────
log.configure(
    name="fmt_iso",
    level=log.DEBUG,
    stdout=log.Stdout(
        fmt=log.LogFmt("[timestamp] [level] - [message]"),
        datefmt="iso",
    ),
)

log.info("ISO 8601 timestamp: 2026-04-26T14:30:00.123+03:00")


# ── Raw logging format string (if you prefer) ─────────────────────────────────
log.configure(
    name="fmt_raw",
    level=log.INFO,
    stdout=log.Stdout(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    ),
)

log.info("raw strftime / logging format strings also accepted")


# ── Available LogFmt tokens ───────────────────────────────────────────────────
#
#   [timestamp]  formatted timestamp           [name]      logger name
#   [level]      level name (INFO, WARNING…)   [message]   log body
#   [module]     module name                   [function]  function name
#   [line]       line number                   [path]      full file path
#   [process]    process ID                    [thread]    thread ID
#
# Available TimeFmt tokens:
#   [year] [month] [day] [hour] [minute] [second] [ms] [tz]
