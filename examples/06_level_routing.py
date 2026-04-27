"""Level routing: send different levels to different destinations."""

from logtie import log

# Route DEBUG+INFO to stdout, WARNING+ to a separate file.
# Both handlers share the same queue for non-blocking writes.

log.configure(
    name="routing",
    level=log.DEBUG,
    stdout=log.Stdout(
        fmt=log.LogFmt("[timestamp] [level] - [message]"),
        datefmt=log.TimeFmt("[hour]:[minute]:[second]"),
        colored=True,
        only=[log.DEBUG, log.INFO],         # terminal shows only low-severity
    ),
    file=log.File(
        path="examples/warnings.log",
        datefmt="iso",
        json=True,
        only=[log.WARNING, log.ERROR, log.CRITICAL],  # file captures alerts only
    ),
    queue=True,
)

log.debug("verbose debug — stdout only")
log.info("normal event — stdout only")
log.warning("something's off — file only")
log.error("request failed — file only", status=500)
log.critical("service down — file only")
