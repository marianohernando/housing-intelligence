"""ASGI entrypoint: `uvicorn hi_api.main:app`."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hi_api.routes import geo, health
from hi_api.settings import ApiSettings

app = FastAPI(title="Housing Intelligence API", version="0.0.1", openapi_url="/api/v1/openapi.json")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ApiSettings().cors_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.include_router(health.router, prefix="/api/v1")
app.include_router(geo.router, prefix="/api/v1")
