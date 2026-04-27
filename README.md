# logtie

Lightweight, zero-dependency logging wrapper for Python. Structured output, context injection, colored terminal, JSON files, and file rotation — all configured in one call.

```python
import logtie.log as log

log.configure(
    name="myapp",
    level=log.DEBUG,
    stdout=log.Stdout(
        fmt=log.LogFmt("[timestamp] [level] - [message]"),
        datefmt=log.TimeFmt("[year]-[month]-[day] [hour]:[minute]:[second]"),
        colored=True,
    ),
    file=log.File(path="app.log", datefmt="iso", json=True),
)

log.bind(request_id="abc-123")
log.info("user logged in", user_id=42)
log.warning("slow query", duration_ms=340)
```

## Installation

```bash
pip install logtie
```

Requires Python 3.14+. No external dependencies.

## Quick start

### 1. Configure once at startup

```python
import logtie.log as log

log.configure(
    name="myapp",       # logger name
    level=log.DEBUG,    # global minimum level
    stdout=True,        # terminal output with defaults
)
```

`configure()` accepts `True` / a plain path string as shorthand for either handler with default settings. Pass a `Stdout` or `File` instance to customise.

### 2. Log

```python
log.debug("connecting to database")
log.info("server started", port=8080)
log.warning("high memory usage", used_mb=1800)
log.error("request failed", status=500, path="/checkout")
log.critical("service unreachable")

try:
    ...
except Exception:
    log.exception("unexpected error")   # includes full traceback
```

Keyword arguments are attached to the log record as extra fields — they appear in JSON output automatically.

### 3. Context injection

Inject fields once; they're included in every subsequent record until removed.

```python
log.bind(request_id="req-001", user_id=42)

log.info("request started")     # → includes request_id + user_id
log.debug("validating payload") # → same

log.unbind("user_id")           # remove one key
log.clear_binds()               # remove all
```

Context is backed by `contextvars`, so it's thread-safe and asyncio-safe — `bind()` inside an asyncio task only affects that task.

## Handlers

### Terminal (`Stdout`)

```python
log.Stdout(
    fmt=log.LogFmt("[timestamp] [level] - [message]"),
    datefmt=log.TimeFmt("[year]-[month]-[day] [hour]:[minute]:[second].[ms]"),
    colored=True,
    colors=log.Colors(
        debug=log.AnsiColor.BRIGHT_BLACK,
        info="#00D4AA",          # hex truecolor
        warning="#FFA500",
    ),
    level=log.DEBUG,
    only=[log.DEBUG, log.INFO],  # restrict to specific levels
)
```

### File (`File`)

```python
log.File(
    path="app.log",
    datefmt="iso",      # ISO 8601 timestamps
    json=True,          # one JSON object per line
    level=log.WARNING,
    rotate_size=5 * 1024 * 1024,  # rotate at 5 MB
    backup_count=7,
)
```

#### File rotation

| Parameter | Behaviour |
|---|---|
| `rotate_size=N` | Rotate when file reaches N bytes |
| `rotate_lines=N` | Rotate when file reaches N lines |
| `backup_count=N` | Number of backup files to keep (default `5`) |

Both use the same rename scheme: `app.log` → `app.log.1` → `app.log.2` …

### JSON field mapping

By default JSON records use:

```
asctime → "timestamp",  name → "logger",  levelname → "level",
message → "message",    funcName → "function",  lineno → "line"
```

Override with `json_fmt`:

```python
log.File(
    path="app.log",
    json=True,
    json_fmt={"asctime": "ts", "levelname": "severity", "message": "msg"},
)
```

Any extra kwargs passed to log calls are added to the JSON object as-is.

## Format tokens

**`LogFmt`** — log line layout:

| Token | Value |
|---|---|
| `[timestamp]` | formatted timestamp |
| `[level]` | level name (`INFO`, `WARNING` …) |
| `[message]` | log body |
| `[name]` | logger name |
| `[function]` | function name |
| `[line]` | line number |
| `[module]` | module name |
| `[path]` | full file path |
| `[process]` | process ID |
| `[thread]` | thread ID |

**`TimeFmt`** — timestamp format:

| Token | Value |
|---|---|
| `[year]` | 4-digit year |
| `[month]` | 2-digit month |
| `[day]` | 2-digit day |
| `[hour]` | hour (24 h) |
| `[minute]` | minute |
| `[second]` | second |
| `[ms]` | milliseconds |
| `[tz]` | timezone offset |

Pass `datefmt="iso"` to either handler for ISO 8601 output instead.

## Level routing

Send different levels to different destinations:

```python
log.configure(
    name="myapp",
    level=log.DEBUG,
    stdout=log.Stdout(only=[log.DEBUG, log.INFO]),          # terminal: verbose
    file=log.File(path="alerts.log", only=[log.WARNING, log.ERROR, log.CRITICAL]),
)
```

## Asyncio

logtie is asyncio-safe out of the box. Use `queue=True` to offload handler I/O to a background thread and keep the event loop unblocked:

```python
log.configure(name="myapp", level=log.DEBUG, stdout=True, queue=True)
```

`bind()` is task-local — context set inside one coroutine doesn't leak into sibling tasks.

## Examples

The [`examples/`](examples/) directory has runnable scripts covering every feature.

## License

MIT
