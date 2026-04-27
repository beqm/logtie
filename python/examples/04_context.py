"""Context injection: bind / unbind / clear_binds for structured logging."""

from python.src.logtie import log

log.configure(
    name="context",
    level=log.DEBUG,
    stdout=log.Stdout(
        spacing=True,
        # %(status)s is a raw logging token — rendered only when the field is present
        fmt=log.LogFmt("[timestamp] [level] - [%(status)s] [message]"),
        datefmt="iso",
        colored=True,
    ),
    file=log.File(path="examples/context.log", datefmt="iso", json=True),
)

# ── bind: inject fields into every subsequent record ─────────────────────────
log.bind(request_id="req-abc123", env="production")

log.info("handling request")                    # record includes request_id + env + status
log.warning("slow query", duration_ms=340)      # + extra per-call field

# ── unbind: remove specific keys ──────────────────────────────────────────────
log.unbind("env")

log.info("env gone, request_id + status still present")

# ── clear_binds: wipe everything ─────────────────────────────────────────────
log.clear_binds()

log.info("context cleared — no injected fields")

# ── typical web-request pattern ──────────────────────────────────────────────
def handle_request(request_id: str, user_id: int, status: int) -> None:
    log.bind(request_id=request_id, user_id=user_id)
    log.info("request started")
    log.debug("validating payload")
    log.info("request finished", status=status)
    log.clear_binds()

handle_request("req-001", 42, 200)
handle_request("req-002", 99, 404)
handle_request("req-003", 7, 500)
