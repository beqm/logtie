"""File rotation: size-based (bytes) and line-based rotation."""

from python.src.logtie import log

# ── Size-based rotation ───────────────────────────────────────────────────────
# Rotates app.log → app.log.1 → app.log.2 … when file hits 1 MB.

log.configure(
    name="rotate_size",
    level=log.DEBUG,
    file=log.File(
        path="examples/size_rotate.log",
        datefmt="iso",
        rotate_size=1 * 1024 * 1024,  # 1 MB
        backup_count=3,               # keep .log, .log.1, .log.2, .log.3
    ),
)

for i in range(50):
    log.info(f"event {i:04d}", index=i)


# ── Line-based rotation ───────────────────────────────────────────────────────
# Rotates after every 100 lines.

log.configure(
    name="rotate_lines",
    level=log.DEBUG,
    file=log.File(
        path="examples/line_rotate.log",
        datefmt="iso",
        rotate_lines=100,
        backup_count=5,
    ),
)

for i in range(250):
    log.debug(f"line {i:04d}")

# After this loop: line_rotate.log has the last 100 lines,
# line_rotate.log.1 the previous 100, line_rotate.log.2 the 50 before that.


# ── JSON + size rotation ──────────────────────────────────────────────────────
log.configure(
    name="rotate_json",
    level=log.INFO,
    stdout=log.Stdout(colored=True),
    file=log.File(
        path="examples/events.log",
        datefmt="iso",
        json=True,
        rotate_size=512 * 1024,   # 512 KB per file
        backup_count=10,
    ),
)

log.info("structured + rotating", service="payments", version="2.1.0")
