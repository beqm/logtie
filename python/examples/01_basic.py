"""Basic usage: configure once, log at all levels, attach extra fields."""

from python.src.logtie import log

log.configure(
    name="basic",
    level=log.DEBUG,
    stdout=log.Stdout(
        fmt=log.LogFmt("[timestamp] [level] - [message]"),
        datefmt=log.TimeFmt("[year]-[month]-[day] [hour]:[minute]:[second]"),
        colored=True,
    ),
)

# Standard levels
log.debug("debug message")
log.info("info message")
log.warning("warning message")
log.error("error message")
log.critical("critical message")

# Extra fields are attached to the log record (visible in JSON / structured output)
log.info("user logged in", user_id=42, action="login")
log.error("payment failed", order_id="ORD-9981", amount=99.90, reason="insufficient_funds")

# Exception with traceback
try:
    result = 1 / 0
except ZeroDivisionError:
    log.exception("division blew up")
