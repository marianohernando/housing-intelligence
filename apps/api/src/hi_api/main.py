"""ASGI entrypoint: `uvicorn hi_api.main:app`."""

from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from hi_api import logs, privacy
from hi_api.routes import datasets, features, gaps, geo, health, investors, places, search
from hi_api.settings import ApiSettings

privacy.install()
logs.install()

app = FastAPI(title="Housing Intelligence API", version="0.0.1", openapi_url="/api/v1/openapi.json")


@app.exception_handler(RequestValidationError)
async def validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse | Response:
    """The parcel search's 422s are private and never echo what was typed (D-252b)."""
    if privacy.PARCELS in request.url.path:
        return privacy.private_validation_error(exc)
    return await request_validation_exception_handler(request, exc)


app.add_middleware(
    CORSMiddleware,
    allow_origins=ApiSettings().cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(health.router, prefix="/api/v1")
app.include_router(geo.router, prefix="/api/v1")
app.include_router(features.router, prefix="/api/v1")
app.include_router(places.router, prefix="/api/v1")
app.include_router(gaps.router, prefix="/api/v1")
app.include_router(datasets.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(investors.router, prefix="/api/v1")
