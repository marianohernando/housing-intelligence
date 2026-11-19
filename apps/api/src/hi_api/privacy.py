"""What a person types never reaches our logs (D-250): the address of the parcel search travels in
the query string (`/investors/parcels?address=`, `/parcels/candidates?q=`), and uvicorn's access
log writes every path with its query. This filter replaces those values before the line is
written; the clients' own request logs (httpx, at INFO) are kept at WARNING."""

import logging
import re
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

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


PRIVATE = "private, no-store"


def private_validation_error(exc: RequestValidationError) -> JSONResponse:
    """A 422 of the parcel search (D-252b, review of #111, R-05): never kept by a shared cache,
    and without the `input` FastAPI echoes, which can be the typed address."""
    errors: list[dict[str, Any]] = [
        {k: v for k, v in error.items() if k not in ("input", "url")} for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={"detail": jsonable_encoder(errors)},
        headers={"Cache-Control": PRIVATE},
    )


def install() -> None:
    logging.getLogger("uvicorn.access").addFilter(RedactTypedAddress())
    for name in ("httpx", "httpcore"):
        logging.getLogger(name).setLevel(logging.WARNING)
