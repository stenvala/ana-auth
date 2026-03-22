"""FastAPI main application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from api.middleware import ApiMiddleware
from api.routers import health_router
from shared.logging import get_logger

logger = get_logger("api.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management."""
    logger.info("Starting ana-auth API server...")
    yield
    logger.info("Shutting down ana-auth API server...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="ana-auth API",
        description="Private SSO/OAuth authentication service",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    app.add_middleware(ApiMiddleware)  # type: ignore[arg-type]

    app.include_router(health_router.router)

    return app


app = create_app()
