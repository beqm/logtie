from python.src.logtie import log

# ── configure ────────────────────────────────────────────────────────────────

log.configure(
    name="playground",
    level=log.DEBUG,
    stdout=log.Stdout(
        fmt=log.LogFmt("[timestamp] [level] - [message]"),
        datefmt=log.TimeFmt("[day]/[month]/[year] [hour]:[minute]:[second].[ms]"),
        colored=True,
        colors=log.Colors(
            debug=log.AnsiColor.BRIGHT_BLACK,
            info="#00D4AA",
            warning="#FFA500",
            error=log.AnsiColor.BRIGHT_RED,
            critical="#FF0000",
        ),
    ),
    file=log.File(
        path="./src/dev/playground.log",
        datefmt="iso",
        json=True,
    ),
)

# ── basic levels ─────────────────────────────────────────────────────────────

log.debug("debug message")
log.info("info message")
log.warning("warning message")
log.error("error message")
log.critical("critical message")

# ── per-call extra fields ─────────────────────────────────────────────────────

log.info("user logged in", user_id=42, action="login")

# ── context injection ─────────────────────────────────────────────────────────

log.bind(request_id="abc-123", env="dev")

log.info("processing request")
log.warning("something odd", code=404)

log.unbind("env")
log.info("env removed from context")

log.clear_binds()
log.info("context cleared")

# ── exc_info ──────────────────────────────────────────────────────────────────

try:
    1 / 0
except ZeroDivisionError:
    log.exception("caught an exception")
