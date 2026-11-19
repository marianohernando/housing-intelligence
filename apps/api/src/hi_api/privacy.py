"""What a person types never reaches our logs (D-250): the address of the parcel search travels in
the query string (`/investors/parcels?address=`, `/parcels/candidates?q=`), and uvicorn's access
log writes every path with its query. This filter replaces those values before the line is
written; the clients' own request logs (httpx, at INFO) are kept at WARNING."""

import logging
import re

TYPED = re.compile(r"(?<=[?&])(address|q)=[^&\s\"]*")
PARCELS = "/api/v1/investors/parcels"
REDACTED = "[redactado]"


def redact(path: str) -> str:
    return TYPED.sub(rf"\1={REDACTED}", path) if PARCELS in path else path


class RedactTypedAddress(logging.Filter):
    """uvicorn.access records carry (client, method, path with query, version, status)."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.args, tuple):
            record.args = tuple(redact(a) if isinstance(a, str) else a for a in record.args)
        if isinstance(record.msg, str):
            record.msg = redact(record.msg)
        return True


def install() -> None:
    logging.getLogger("uvicorn.access").addFilter(RedactTypedAddress())
    for name in ("httpx", "httpcore"):
        logging.getLogger(name).setLevel(logging.WARNING)
