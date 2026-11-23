"""D-252b: our own log lines reach the platform's logs. Without this, the `hi_api` loggers have no
level and inherit the root's WARNING, so every `log.info` (the parcel timeline among them) was
dropped in production; uvicorn only configures its own loggers. One handler to stdout, at INFO,
with the same filter that redacts a typed address (privacy.py)."""

import logging
import sys

from hi_api.privacy import RedactTypedAddress

FORMAT = "%(levelname)s %(name)s %(message)s"


def install() -> None:
    log = logging.getLogger("hi_api")
    log.setLevel(logging.INFO)
    if not any(isinstance(h, logging.StreamHandler) for h in log.handlers):  # once
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(FORMAT))
        handler.addFilter(RedactTypedAddress())
        log.addHandler(handler)
