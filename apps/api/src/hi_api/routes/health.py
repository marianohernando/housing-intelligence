"""Liveness endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

from hi_contracts.api.envelope import Envelope

router = APIRouter(tags=["health"])


class HealthStatus(BaseModel):
    status: str
    service: str


@router.get("/health")
def health() -> Envelope[HealthStatus]:
    return Envelope(data=HealthStatus(status="ok", service="hi-api"))
