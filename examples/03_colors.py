"""Colors: AnsiColor constants, hex truecolor, per-level overrides."""

from logtie import log

# ── Default Colors instance (built-in palette) ────────────────────────────────
log.configure(
    name="colors_default",
    level=log.DEBUG,
    stdout=log.Stdout(
        fmt=log.LogFmt("[timestamp] [level] - [message]"),
        datefmt=log.TimeFmt("[hour]:[minute]:[second]"),
        colored=True,
        # Colors() defaults:
        #   debug    → BRIGHT_BLUE
        #   info     → BRIGHT_GREEN
        #   warning  → BRIGHT_YELLOW
        #   error    → BRIGHT_RED
        #   critical → BRIGHT_MAGENTA
    ),
)

log.debug("default blue debug")
log.info("default green info")
log.warning("default yellow warning")
log.error("default red error")
log.critical("default magenta critical")


# ── Custom palette with hex truecolor + AnsiColor mix ────────────────────────
log.configure(
    name="colors_custom",
    level=log.DEBUG,
    stdout=log.Stdout(
        fmt=log.LogFmt("[level] - [message]"),
        colored=True,
        colors=log.Colors(
            debug=log.AnsiColor.BRIGHT_BLACK,   # muted gray for debug noise
            info="#00D4AA",                      # teal (truecolor)
            warning="#FFA500",                   # orange (truecolor)
            error=log.AnsiColor.BRIGHT_RED,
            critical="#FF0000",                  # bright red (truecolor)
        ),
    ),
)

log.debug("muted gray — low-priority noise")
log.info("teal info")
log.warning("orange warning")
log.error("bright red error")
log.critical("pure red critical")
