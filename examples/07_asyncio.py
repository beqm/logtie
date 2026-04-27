"""Asyncio usage: context injection is task-local, queue=True avoids blocking."""

import asyncio
from logtie import log

log.configure(
    name="async_app",
    level=log.DEBUG,
    stdout=log.Stdout(
        fmt=log.LogFmt("[timestamp] [level] [function] - [message]"),
        datefmt=log.TimeFmt("[hour]:[minute]:[second].[ms]"),
        colored=True,
    ),
    queue=True,   # offloads I/O to a background thread — recommended for asyncio
)

# ── Context is per-task ───────────────────────────────────────────────────────
# Each asyncio Task starts with a COPY of the spawning context.
# bind() inside a task only affects that task and its sub-tasks.

async def handle_request(request_id: str, user_id: int) -> None:
    log.bind(request_id=request_id, user_id=user_id)
    log.info("request started")
    await asyncio.sleep(0.01)           # simulate async work
    log.debug("processing payload")
    await asyncio.sleep(0.01)
    log.info("request finished", status=200)
    # No need to clear — bind is scoped to this task

async def main() -> None:
    # Global bind visible to tasks created AFTER this point
    log.bind(service="api")

    # Tasks run concurrently; their bind() calls don't bleed into each other
    await asyncio.gather(
        handle_request("req-001", 42),
        handle_request("req-002", 99),
        handle_request("req-003", 7),
    )

    log.info("all requests done")

asyncio.run(main())

# ── Key properties ────────────────────────────────────────────────────────────
# 1. contextvars (used by bind/unbind) are natively asyncio-safe.
#    Each Task inherits a snapshot of the parent context at creation time.
# 2. bind() called inside a coroutine updates only that task's context.
# 3. queue=True routes all handler I/O through a background thread,
#    so log calls never block the event loop.
