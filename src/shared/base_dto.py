"""Base DTO class with camelCase conversion."""

from pydantic import BaseModel, ConfigDict


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class BaseDTO(BaseModel):
    """Base class for all DTOs.

    Provides:
    - Automatic snake_case to camelCase conversion for JSON serialization
    - Validation on assignment
    """

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        from_attributes=True,
    )
