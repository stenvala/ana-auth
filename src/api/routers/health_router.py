"""Health check router."""

from fastapi import APIRouter
from pydantic import Field

from shared.base_dto import BaseDTO

router = APIRouter()


class HealthDTO(BaseDTO):
    """Health check response."""

    status: str = Field(..., description="Service health status")


@router.get("/api/health")
def health_check() -> HealthDTO:
    """Health check endpoint."""
    return HealthDTO(status="ok")
