# SQLModel Template

## Basic Model Structure

```python
"""<TableName> SQLModel."""

from datetime import date, datetime, time, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from ..base_model import BaseDBModelMixin
from .<domain>_enums import StatusEnum, TypeEnum

if TYPE_CHECKING:
    # Import related models for type hints only (avoids circular imports)
    from .related_model import RelatedModel


class TableName(SQLModel, BaseDBModelMixin, table=True):
    """Brief description of the table purpose."""

    __tablename__ = "table_name"

    # Primary key - always string with default=None (DB generates UUID)
    id: str = Field(primary_key=True, default=None)

    # Required fields
    name: str
    status: StatusEnum
    type: TypeEnum

    # Optional fields
    description: Optional[str] = Field(default=None)
    priority: Optional[int] = Field(default=None)

    # Foreign keys - always use index=True for query performance
    parent_id: str = Field(foreign_key="parent_table.id", index=True)
    optional_ref_id: Optional[str] = Field(
        default=None, foreign_key="other_table.id", index=True
    )

    # Timestamps - always use UTC
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships (optional, for ORM navigation)
    children: List["ChildModel"] = Relationship(back_populates="parent")
    parent: Optional["ParentModel"] = Relationship(back_populates="children")
```

## Field Type Mapping

| SQL Type                     | Python Type | Field Definition                                      |
| ---------------------------- | ----------- | ----------------------------------------------------- |
| VARCHAR(255) PRIMARY KEY     | str         | `Field(primary_key=True, default=None)`               |
| VARCHAR(255)                 | str         | Plain field or `Field(max_length=255)`                |
| VARCHAR(255) NOT NULL UNIQUE | str         | `Field(unique=True, index=True)`                      |
| TEXT                         | str         | Plain field                                           |
| INTEGER                      | int         | Plain field                                           |
| BOOLEAN                      | bool        | `Field(default=False)`                                |
| DATE                         | date        | Plain field or `Field(default=None)`                  |
| TIME                         | time        | `Optional[time] = Field(default=None)`                |
| TIMESTAMP                    | datetime    | `Field(default_factory=lambda: datetime.now(tz.utc))` |
| FLOAT/DECIMAL                | float       | Plain field                                           |
| JSONB                        | TypeAlias   | `Field(sa_type=JSON)` with type alias                 |
| FOREIGN KEY                  | str         | `Field(foreign_key="table.id", index=True)`           |
