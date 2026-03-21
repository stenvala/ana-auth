# Repository Template

## Basic Repository Structure

```python
"""<TableName> repository operations."""

from datetime import date, datetime
from typing import List, Optional

from sqlmodel import Session, col, select

from ...models.<domain>_models.<table_name> import TableName
from ...models.<domain>_models.<domain>_enums import StatusEnum


class TableNameRepository:
    """Repository for TableName operations."""

    def __init__(self, session: Session):
        self.session = session

    # === READ OPERATIONS ===

    def get_by_id(self, id: str) -> Optional[TableName]:
        """Get record by ID."""
        return self.session.get(TableName, id)

    def get_all(self) -> List[TableName]:
        """Get all records."""
        statement = select(TableName)
        return list(self.session.exec(statement).all())

    def get_by_foreign_key(self, parent_id: str) -> List[TableName]:
        """Get records by foreign key."""
        statement = select(TableName).where(TableName.parent_id == parent_id)
        return list(self.session.exec(statement).all())

    def get_by_status(self, status: StatusEnum) -> List[TableName]:
        """Get records by status."""
        statement = select(TableName).where(TableName.status == status)
        return list(self.session.exec(statement).all())

    # === CREATE OPERATIONS ===

    def create(self, entity: TableName) -> TableName:
        """Create new record."""
        self.session.add(entity)
        self.session.flush()  # Flush without commit - transaction managed at service layer
        self.session.refresh(entity)
        return entity

    # === UPDATE OPERATIONS ===

    def update(self, entity: TableName) -> TableName:
        """Update existing record."""
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)
        return entity

    # === DELETE OPERATIONS ===

    def delete(self, id: str) -> bool:
        """Delete record by ID. Returns True if deleted, False if not found."""
        entity = self.session.get(TableName, id)
        if entity:
            self.session.delete(entity)
            self.session.flush()
            return True
        return False
```
