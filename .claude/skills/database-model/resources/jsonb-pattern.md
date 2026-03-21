# JSONB Fields Pattern

JSONB fields store complex nested data. The pattern involves:
1. **Type definitions** - Pydantic models in a separate `<domain>_types.py` file
2. **Type alias** - Used as the field type hint
3. **Property helper** - Converts stored dicts back to Pydantic models when reading

**IMPORTANT**: SQLAlchemy stores JSONB as Python dicts/lists, not Pydantic models. The type hint is for documentation/IDE support only.

## Step 1: Create Type Definitions

Create `src/shared/db/models/<domain>_models/<domain>_types.py`:

```python
"""Pydantic types for <domain> JSONB fields."""

from typing import List, Optional
from pydantic import BaseModel, Field
from ..base_model import BaseDBModelMixin


class NestedItem(BaseModel, BaseDBModelMixin):
    """Nested item within the JSONB structure."""

    name: str = Field(..., description="Item name")
    value: int = Field(..., description="Item value")
    options: Optional[List[str]] = Field(default=None)


class ParentItem(BaseModel, BaseDBModelMixin):
    """Parent item containing nested items."""

    category: str = Field(..., description="Category name")
    items: List[NestedItem] = Field(..., description="List of nested items")


# Type alias for the JSONB field
ItemsList = List[ParentItem]
```

## Step 2: Use in SQLModel

```python
from sqlmodel import JSON, Field, SQLModel
from .<domain>_types import ItemsList, ParentItem

class MyTable(SQLModel, BaseDBModelMixin, table=True):
    __tablename__ = "my_table"

    id: str = Field(primary_key=True, default=None)

    # JSONB field - stored as dicts, type hint for IDE support
    items: ItemsList = Field(sa_type=JSON)

    # Optional JSONB field
    metadata: Optional[ItemsList] = Field(default=None, sa_type=JSON)

    @property
    def items_pydantic(self) -> List[ParentItem]:
        """Get items as validated Pydantic model instances.

        Use this when you need Pydantic validation/methods.
        For simple dict access, use self.items directly.
        """
        return [
            item if isinstance(item, ParentItem) else ParentItem(**item)
            for item in self.items
        ]
```

## Step 3: Service Layer Usage

```python
# READING - use property for Pydantic models
items = entity.items_pydantic  # List[ParentItem]

# WRITING - convert Pydantic to dicts
new_items: List[ParentItem] = [...]  # Pydantic models
entity.items = [item.model_dump() for item in new_items]

# Or pass dicts directly
entity.items = [{"category": "A", "items": [...]}]
```
