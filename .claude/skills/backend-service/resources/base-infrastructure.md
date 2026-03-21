# Base Infrastructure for Backend Services

This file contains foundational classes needed before creating services in a fresh project.

## Directory Structure

```
src/shared/
├── __init__.py
├── models/
│   ├── __init__.py
│   └── minimal_user.py              # MinimalUser for audit
├── services/
│   ├── __init__.py
│   └── <domain>_services/
│       ├── __init__.py
│       └── <feature>_editor_service.py
├── logging/
│   ├── __init__.py
│   └── logger.py                    # Structured logging
└── db/
    ├── models/
    │   └── audit_models/
    │       ├── __init__.py
    │       ├── audit_enums.py       # Audit action enums
    │       └── <feature>_audit.py   # Audit trail model
    └── repositories/
        └── audit_repository/
            ├── __init__.py
            └── <feature>_audit_repository.py
```

## 1. MinimalUser (src/shared/models/minimal_user.py)

```python
"""Minimal user model for audit trails."""

from pydantic import BaseModel, Field


class MinimalUser(BaseModel):
    """Minimal user information for audit logging.

    Used to track who performed actions without coupling to full user model.
    Services receive this from routers, which convert from the full EnrichedUser.
    """

    id: str = Field(..., description="User ID")
    full_name: str = Field(..., description="User's full name for display")
    email: str | None = Field(default=None, description="User's email (optional)")
```

## 2. Logger (src/shared/logging/logger.py)

```python
"""Structured logging utilities."""

import logging
import sys
from typing import Any


class StructuredLogger:
    """Logger with structured context support."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(
                logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )
            self.logger.addHandler(handler)

    def _format_message(self, message: str, **kwargs: Any) -> str:
        """Format message with context."""
        if kwargs:
            context = " ".join(f"{k}={v}" for k, v in kwargs.items())
            return f"{message} | {context}"
        return message

    def debug(self, message: str, **kwargs: Any) -> None:
        self.logger.debug(self._format_message(message, **kwargs))

    def info(self, message: str, **kwargs: Any) -> None:
        self.logger.info(self._format_message(message, **kwargs))

    def warning(self, message: str, **kwargs: Any) -> None:
        self.logger.warning(self._format_message(message, **kwargs))

    def error(self, message: str, **kwargs: Any) -> None:
        self.logger.error(self._format_message(message, **kwargs))


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)
```

## 3. Audit Enums (src/shared/db/models/audit_models/audit_enums.py)

```python
"""Audit action enumerations."""

from enum import Enum


class FeatureAuditActionCodeEnum(str, Enum):
    """Audit action codes for Feature entity."""

    FEATURE_CREATED = "FEATURE_CREATED"
    FEATURE_UPDATED = "FEATURE_UPDATED"
    FEATURE_DELETED = "FEATURE_DELETED"
    FEATURE_RESTORED = "FEATURE_RESTORED"
```

## 4. Audit Model (src/shared/db/models/audit_models/<feature>_audit.py)

```python
"""Feature audit trail model."""

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import JSON
from sqlmodel import Field, SQLModel

from ..base_model import BaseDBModelMixin
from .audit_enums import FeatureAuditActionCodeEnum


class FeatureAudit(SQLModel, BaseDBModelMixin, table=True):
    """Audit trail for Feature entity changes."""

    __tablename__ = "feature_audit"

    id: str = Field(primary_key=True, default=None)
    feature_id: str = Field(foreign_key="feature.id", index=True)
    performed_by_user_id: str = Field(index=True)
    performed_by_user_name: str
    action_code: FeatureAuditActionCodeEnum
    description: str
    data_snapshot: Optional[dict[str, Any]] = Field(default=None, sa_type=JSON)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

## 5. Audit Repository (src/shared/db/repositories/audit_repository/<feature>_audit_repository.py)

```python
"""Feature audit repository operations."""

from typing import List

from sqlmodel import Session, select

from shared.db.models.audit_models.feature_audit import FeatureAudit


class FeatureAuditRepository:
    """Repository for Feature audit operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, audit: FeatureAudit) -> FeatureAudit:
        """Create new audit entry."""
        self.session.add(audit)
        self.session.flush()
        self.session.refresh(audit)
        return audit

    def get_by_feature_id(self, feature_id: str) -> List[FeatureAudit]:
        """Get all audit entries for a feature."""
        statement = (
            select(FeatureAudit)
            .where(FeatureAudit.feature_id == feature_id)
            .order_by(FeatureAudit.created_at.desc())
        )
        return list(self.session.exec(statement).all())
```

## Usage in Service

```python
from shared.logging.logger import get_logger
from shared.models.minimal_user import MinimalUser

class FeatureEditorService:
    def __init__(self, session: Session):
        self.session = session
        self.feature_repo = FeatureRepository(session)
        self.audit_repo = FeatureAuditRepository(session)
        self.logger = get_logger(__name__)

    def create_feature(self, data: CreateFeatureDTO, created_by_user: MinimalUser) -> Feature:
        # ... implementation
```

## Usage in Router

```python
from shared.models.minimal_user import MinimalUser

@router.post("/features", response_model=FeatureDTO)
def create_feature(
    data: CreateFeatureDTO,
    current_user: EnrichedUser = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> FeatureDTO:
    service = FeatureEditorService(session)
    # Convert EnrichedUser to MinimalUser for service
    created = service.create_feature(
        data=data,
        created_by_user=MinimalUser(**current_user.model_dump()),
    )
    return FeatureDTO(**created.dump_to_dto_dict())
```
