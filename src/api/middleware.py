"""Centralized API middleware for database sessions, logging, and error handling.

Handles all cross-cutting concerns including:
- Database session and transaction management (commit/rollback)
- Request/response logging with correlation IDs
- Centralized error handling

IMPORTANT: This is the ONLY place for error handling.
Let all exceptions bubble up here -- do NOT catch them in routes or services.
"""

import json
import traceback
import uuid
from typing import Any, Awaitable, Callable

from fastapi import HTTPException, Request, Response
from pydantic import ValidationError
from sqlmodel import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from shared.config import Config
from shared.db.db_context import DBContext
from shared.logging import StructuredLogger, get_file_logger, set_transaction_id

api_logger = get_file_logger("api")


class ApiMiddleware(BaseHTTPMiddleware):
    """Central API middleware handling DB sessions, logging, and errors.

    IMPORTANT: This is the ONLY place for error handling.
    Let all exceptions bubble up here.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.logger = StructuredLogger(api_logger)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request within a single DB transaction."""
        request_id = str(uuid.uuid4())
        set_transaction_id(request_id)

        request.state.logger = api_logger
        request.state.request_id = request_id

        # Determine schema suffix: allow X-Schema header override in non-prod
        schema_suffix = Config.SCHEMA_SUFFIX
        if Config.ENV_TYPE != "PROD":
            header_schema = request.headers.get("X-Schema")
            if header_schema:
                schema_suffix = header_schema

        try:
            db_context = DBContext(schema_suffix)
            with db_context.get_session() as db_session:
                request.state.db_session = db_session

                self.logger.info(
                    "REQUEST_START",
                    method=request.method,
                    path=str(request.url.path),
                )

                response = await call_next(request)

                self.logger.info(
                    "REQUEST_END",
                    method=request.method,
                    path=str(request.url.path),
                    status_code=response.status_code,
                )

                return response

        except Exception as e:
            self.logger.error(
                "REQUEST_ERROR",
                method=request.method,
                path=str(request.url.path),
                error_type=type(e).__name__,
                error_message=str(e),
                error_traceback=traceback.format_exc(),
            )

            status_code, error_response = self._handle_exception(e, request_id)

            return Response(
                content=error_response,
                status_code=status_code,
                media_type="application/json",
            )

    def _handle_exception(
        self, exception: Exception, request_id: str
    ) -> tuple[int, str]:
        """Handle different exception types with appropriate HTTP status codes."""
        if isinstance(exception, HTTPException):
            return self._handle_http_exception(exception, request_id)
        if isinstance(exception, ValidationError):
            return self._handle_validation_error(exception, request_id)
        if isinstance(exception, ValueError):
            return self._handle_value_error(exception, request_id)
        if isinstance(exception, PermissionError):
            return self._handle_permission_error(request_id)
        if (
            isinstance(exception, FileNotFoundError)
            or "not found" in str(exception).lower()
        ):
            return self._handle_not_found_error(exception, request_id)
        return self._handle_system_error(request_id)

    def _handle_http_exception(
        self, exception: HTTPException, request_id: str
    ) -> tuple[int, str]:
        """Handle FastAPI HTTPException."""
        error_data = {"error": exception.detail, "request_id": request_id}
        return exception.status_code, json.dumps(error_data)

    def _handle_validation_error(
        self, exception: ValidationError, request_id: str
    ) -> tuple[int, str]:
        """Handle Pydantic validation errors."""
        error_data: dict[str, Any] = {
            "error": "Validation failed",
            "details": exception.errors(),
            "request_id": request_id,
        }
        return 422, json.dumps(error_data)

    def _handle_value_error(
        self, exception: Exception, request_id: str
    ) -> tuple[int, str]:
        """Handle business logic validation errors."""
        error_data = {"error": str(exception), "request_id": request_id}
        return 400, json.dumps(error_data)

    def _handle_permission_error(self, request_id: str) -> tuple[int, str]:
        """Handle permission/authorization errors."""
        error_data = {"error": "Insufficient permissions", "request_id": request_id}
        return 403, json.dumps(error_data)

    def _handle_not_found_error(
        self, exception: Exception, request_id: str
    ) -> tuple[int, str]:
        """Handle resource not found errors."""
        error_data = {
            "error": str(exception) if str(exception) else "Resource not found",
            "request_id": request_id,
        }
        return 404, json.dumps(error_data)

    def _handle_system_error(self, request_id: str) -> tuple[int, str]:
        """Handle unhandled system errors."""
        self.logger.critical(
            "SYSTEM_ERROR_500",
            request_id=request_id,
            traceback=traceback.format_exc(),
        )
        error_data = {"error": "System error", "request_id": request_id}
        return 500, json.dumps(error_data)


def get_db_from_request(request: Request) -> Session:
    """Get database session from request state."""
    return request.state.db_session
