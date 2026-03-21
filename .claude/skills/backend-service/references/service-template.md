# Backend Service Template

## Complete Service Implementation

```python
"""Service for <feature> operations."""

from fastapi import HTTPException, status
from sqlmodel import Session

from shared.dtos.<domain>.<feature>_dtos import (
    <Feature>CreateDTO,
    <Feature>DTO,
    <Feature>UpdateDTO,
)
from shared.services.<domain>.audit_trail_service import AuditTrailService
from shared.db.models.<domain>_models import <Feature>
from shared.db.repositories.<domain>_repository import <Feature>Repository


class <Feature>Service:
    """Service for <feature> business logic."""

    def __init__(
        self,
        session: Session,
        audit_trail: AuditTrailService | None = None,
    ) -> None:
        self.session = session
        self.repository = <Feature>Repository(session)
        self.audit_trail = audit_trail

    def list_all(self) -> list[<Feature>DTO]:
        """Get all <feature>s."""
        entities = self.repository.get_all()
        return [<Feature>DTO(**e.model_dump()) for e in entities]

    def get_by_id(self, <feature>_id: str) -> <Feature>DTO:
        """Get a <feature> by ID.

        Raises:
            HTTPException: If <feature> not found.
        """
        entity = self.repository.get_by_id(<feature>_id)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "NOT_FOUND", "message": "<Feature> not found"},
            )
        return <Feature>DTO(**entity.model_dump())

    def create(self, dto: <Feature>CreateDTO) -> <Feature>DTO:
        """Create a new <feature>.

        Args:
            dto: Creation data

        Returns:
            Created <feature>.

        Raises:
            ValueError: If validation fails.
        """
        # Business validation
        # e.g., check references exist, validate data

        entity = <Feature>(
            name=dto.name,
            # ... map other fields from dto
        )
        entity = self.repository.create(entity)

        if self.audit_trail:
            self.audit_trail.log_create("<feature>", entity.id, entity.name)

        return <Feature>DTO(**entity.model_dump())

    def update(self, <feature>_id: str, dto: <Feature>UpdateDTO) -> <Feature>DTO:
        """Update an existing <feature>.

        Args:
            <feature>_id: ID of the <feature> to update
            dto: Update data

        Returns:
            Updated <feature>.

        Raises:
            HTTPException: If <feature> not found.
        """
        entity = self.repository.get_by_id(<feature>_id)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "NOT_FOUND", "message": "<Feature> not found"},
            )

        # Update fields if provided
        if dto.name is not None:
            entity.name = dto.name
        # ... update other fields

        entity = self.repository.update(entity)

        if self.audit_trail:
            self.audit_trail.log_edit("<feature>", <feature>_id)

        return <Feature>DTO(**entity.model_dump())

    def delete(self, <feature>_id: str) -> None:
        """Delete a <feature>.

        Args:
            <feature>_id: ID of the <feature> to delete

        Raises:
            HTTPException: If <feature> not found.
        """
        entity = self.repository.get_by_id(<feature>_id)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "NOT_FOUND", "message": "<Feature> not found"},
            )

        # Business validation before delete
        # e.g., check if entity can be deleted

        self.repository.delete(entity)

        if self.audit_trail:
            self.audit_trail.log_delete("<feature>", <feature>_id)
```

## AuditTrailService Usage

Services receive `AuditTrailService` via dependency injection:

```python
def __init__(
    self,
    session: Session,
    audit_trail: AuditTrailService | None = None,
) -> None:
    self.session = session
    self.audit_trail = audit_trail

# In methods:
if self.audit_trail:
    self.audit_trail.log_create("entity_type", entity.id, "description")
    self.audit_trail.log_edit("entity_type", entity_id)
    self.audit_trail.log_delete("entity_type", entity_id)
```

## Error Handling Pattern

Services use `HTTPException` for not-found errors and let middleware handle everything else:

```python
# Not found - use HTTPException
if not entity:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error": "NOT_FOUND", "message": "Entity not found"},
    )

# Validation errors - use ValueError (middleware converts to 400)
if not valid:
    raise ValueError("Validation failed: reason")

# Other errors - let them bubble up (middleware handles as 500)
```
