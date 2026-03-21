# Common Query Patterns

## Simple Queries

```python
# Get by ID
def get_by_id(self, id: str) -> Optional[TableName]:
    return self.session.get(TableName, id)

# Get by unique field
def get_by_username(self, username: str) -> Optional[TableName]:
    statement = select(TableName).where(TableName.username == username)
    return self.session.exec(statement).first()
```

## Filtered Queries

```python
# Filter by enum
def get_by_status(self, status: StatusEnum) -> List[TableName]:
    statement = select(TableName).where(TableName.status == status)
    return list(self.session.exec(statement).all())

# Filter by multiple conditions
def get_active_by_group(self, group_id: str) -> List[TableName]:
    statement = select(TableName).where(
        TableName.group_id == group_id,
        TableName.status == StatusEnum.ACTIVE
    )
    return list(self.session.exec(statement).all())
```

## Date Range Queries

```python
def get_by_date_range(self, start_date: date, end_date: date) -> List[TableName]:
    statement = select(TableName).where(
        TableName.start_date >= start_date,
        TableName.start_date <= end_date
    )
    return list(self.session.exec(statement).all())
```

## IN Queries

```python
from sqlmodel import col

def get_by_ids(self, ids: List[str]) -> List[TableName]:
    statement = select(TableName).where(col(TableName.id).in_(ids))
    return list(self.session.exec(statement).all())

def get_by_statuses(self, statuses: List[StatusEnum]) -> List[TableName]:
    statement = select(TableName).where(col(TableName.status).in_(statuses))
    return list(self.session.exec(statement).all())
```

## Ordered Queries

```python
def get_recent(self, limit: int = 10) -> List[TableName]:
    statement = (
        select(TableName)
        .order_by(col(TableName.created_at).desc())
        .limit(limit)
    )
    return list(self.session.exec(statement).all())
```

## Join Queries

```python
from typing import Tuple

def get_with_parent(self, id: str) -> Optional[Tuple[TableName, ParentTable]]:
    statement = (
        select(TableName, ParentTable)
        .join(ParentTable)
        .where(TableName.id == id)
    )
    return self.session.exec(statement).first()
```

## Existence Check

```python
def exists(self, id: str) -> bool:
    return self.session.get(TableName, id) is not None

def exists_by_unique_field(self, unique_value: str) -> bool:
    statement = select(TableName).where(TableName.unique_field == unique_value)
    return self.session.exec(statement).first() is not None
```

## Repository Models (for complex queries)

If repository needs custom return types, create them in `<table_name>_repository_models.py`:

```python
"""Repository models for TableName repository."""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class TableNameSummary:
    """Lightweight summary for list views."""

    id: str
    name: str
    status: str
    created_at: date


@dataclass
class TableNamePermissionInfo:
    """Minimal info for permission checking."""

    group_id: str
    owner_id: str
```
