"""ASGI entrypoint: `uvicorn hi_api.main:app`."""

from fastapi import FastAPI

from hi_api.routes import health

app = FastAPI(title="Housing Intelligence API", version="0.0.1", openapi_url="/api/v1/openapi.json")
app.include_router(health.router, prefix="/api/v1")
