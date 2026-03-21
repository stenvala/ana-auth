# Enum Template

Create enums at: `src/shared/db/models/<domain>_models/<domain>_enums.py`

## Basic Enum Pattern

```python
"""Enums for <domain> domain."""

from enum import Enum


class StatusEnum(str, Enum):
    """Status values for entities in this domain."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"


class TypeEnum(str, Enum):
    """Type classification for entities."""

    TYPE_A = "TYPE_A"
    TYPE_B = "TYPE_B"
    TYPE_C = "TYPE_C"


class PriorityEnum(str, Enum):
    """Priority levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
```

## Key Rules

1. **Always inherit from `str, Enum`** - This ensures JSON serialization works correctly
2. **Value equals name** - `ACTIVE = "ACTIVE"` (matches database CHECK constraint)
3. **Add docstrings** - Describe the purpose of each enum
4. **One file per domain** - Group all domain enums together
