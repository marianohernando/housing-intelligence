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

DESCRIPTION = (
    "API pública y gratuita, de solo lectura, sobre datos abiertos de la Comunidad de Madrid: "
    "dónde vivir, qué falta en cada zona y la ficha de un barrio o una parcela. Cada cifra lleva "
    "su fuente y su licencia (campos `datasets` y `attribution_text`). El código es Apache-2.0; "
    "los datos llevan la licencia de cada fuente (CC BY 4.0 en el portal de datos abiertos de la "
    "Comunidad de Madrid)."
)
REPO_URL = "https://github.com/marianohernando/housing-intelligence"
PUBLIC_URL = "https://vidafacil-madrid.vercel.app"

app = FastAPI(
    title="Vida Fácil API",
    description=DESCRIPTION,
    version="0.0.1",
    openapi_url="/api/v1/openapi.json",
    license_info={"name": "Apache-2.0", "identifier": "Apache-2.0"},
    contact={"name": "Vida Fácil", "url": REPO_URL},
    servers=[{"url": PUBLIC_URL, "description": "Demo pública"}],
)


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
