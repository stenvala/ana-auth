"""Base model mixin for SQLModel classes."""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID


class BaseDBModelMixin:
    """Mixin providing common functionality for SQLModel classes.

    All SQLModel classes should inherit from this mixin to get:
    - dump_to_dto_dict() for converting to DTOs
    - update_from_dict() for updating from DTOs
    """

    def dump_to_dto_dict(self) -> dict[str, Any]:
        """Convert model to dictionary suitable for DTO construction.

        Handles conversion of:
        - datetime -> ISO format string
        - date -> YYYY-MM-DD string
        - time -> HH:MM string
        - UUID -> string
        - Decimal -> float
        """
        result = {}
        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue
            result[key] = self._convert_value(value)
        return result

    def _convert_value(self, value: Any) -> Any:
        """Convert a single value to DTO-compatible format."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return value.strftime("%Y-%m-%d")
        if isinstance(value, time):
            return value.strftime("%H:%M")
        if isinstance(value, UUID):
            return str(value)
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, list):
            return [self._convert_value(item) for item in value]
        if isinstance(value, dict):
            return {k: self._convert_value(v) for k, v in value.items()}
        return value

    def update_from_dict(self, data: dict[str, Any]) -> None:
        """Update model fields from dictionary.

        Only updates fields that exist on the model and are not None in data.
        """
        for key, value in data.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
