"""JSON file output: structured logs for ingestion by log aggregators."""

from python.src.logtie import log

# ── Default JSON field mapping ─────────────────────────────────────────────────
# asctime  → "timestamp"
# name     → "logger"
# levelname→ "level"
# message  → "message"
# funcName → "function"
# lineno   → "line"
# (any extra kwargs are added as-is)

log.configure(
    name="json_demo",
    level=log.DEBUG,
    stdout=log.Stdout(
        fmt=log.LogFmt("[timestamp] [level] - [message]"),
        datefmt="iso",
        colored=True,
        spacing=True,
    ),
    file=log.File(
        path="examples/app.jsonl",
        datefmt="iso",
        json=True,
    ),
)

log.info("server started", port=8080, env="staging")
log.warning("high memory usage", used_mb=1800, limit_mb=2048)

try:
    raise ValueError("bad config value")
except ValueError:
    log.exception("startup failed")


# ── Custom JSON field mapping ─────────────────────────────────────────────────
log.configure(
    name="json_custom",
    level=log.INFO,
    file=log.File(
        path="examples/custom.jsonl",
        datefmt="iso",
        json=True,
        json_fmt={
            "asctime":   "ts",
            "levelname": "severity",
            "message":   "msg",
            "name":      "src",
        },
    ),
)

log.info("compact JSON with renamed keys", trace_id="t-001")
