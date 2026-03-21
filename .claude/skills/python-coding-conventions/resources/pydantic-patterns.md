# Pydantic Patterns and Best Practices

## DTO Inheritance Hierarchy

```python
from shared.base_dto import BaseDTO
from pydantic import Field

# Base pattern
class UserDTO(BaseDTO):
    """Full user information."""
    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")

# Safe variant excludes sensitive data
class SafeUserDTO(BaseDTO):
    """User information safe for public APIs."""
    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    # Note: email excluded for privacy

# Create from database model
def to_safe_user(user: UserModel) -> SafeUserDTO:
    return SafeUserDTO(**user.model_dump())
```

## Converting Models to DTOs

### Pattern 1: Selective Field Extraction
```python
class AuthService:
    def authenticate(self, username: str, password: str) -> tuple[str, SafeUserDTO]:
        user = self.user_repo.get_by_username(username)

        # Create DTO with only needed fields
        safe_user = SafeUserDTO(
            id=user.id,
            username=user.username,
        )
        return session_id, safe_user
```

### Pattern 2: Using model_dump()
```python
class UserService:
    def get_by_id(self, user_id: str) -> UserDTO:
        user = self.user_repo.get_by_id(user_id)
        # model_dump() extracts all non-private fields
        return UserDTO(**user.model_dump())
```

### Pattern 3: Exclude Sensitive Fields
```python
class UserService:
    def get_by_id(self, user_id: str) -> SafeUserDTO:
        user = self.user_repo.get_by_id(user_id)
        # Exclude password_hash from output
        return SafeUserDTO(**user.model_dump(exclude={"password_hash"}))
```

## List Response Patterns

### Standard List Response
```python
from typing import Optional

class ItemListResponseDTO(BaseDTO):
    """Response for listing items."""
    items: list[ItemDTO] = Field(..., description="List of items")
    total: int = Field(..., description="Total count")

class ItemService:
    def list_all(self) -> ItemListResponseDTO:
        items = self.item_repo.list_all()
        return ItemListResponseDTO(
            items=[ItemDTO(**item.model_dump()) for item in items],
            total=len(items),
        )
```

### Paginated Response
```python
class ItemListResponseDTO(BaseDTO):
    """Response for listing items with pagination."""
    items: list[ItemDTO] = Field(..., description="List of items")
    total: int = Field(..., description="Total count")
    offset: int = Field(default=0, description="Pagination offset")
    limit: int = Field(default=50, description="Pagination limit")

class ItemService:
    def list_paginated(
        self, offset: int = 0, limit: int = 50
    ) -> ItemListResponseDTO:
        items = self.item_repo.list_paginated(offset, limit)
        total = self.item_repo.count()

        return ItemListResponseDTO(
            items=[ItemDTO(**item.model_dump()) for item in items],
            total=total,
            offset=offset,
            limit=limit,
        )
```

## Optional and Sensitive Fields

```python
class UserDTO(BaseDTO):
    id: str = Field(...)
    username: str = Field(...)
    bio: Optional[str] = Field(default=None, description="User bio")

# Full model (database layer)
class User(SQLModel, table=True):
    id: str
    username: str
    password_hash: str  # Never expose this
    email: str

# Full DTO for internal services (password_hash excluded)
class UserDTO(BaseDTO):
    id: str
    username: str
    email: str

# Safe DTO for public APIs (email also excluded)
class SafeUserDTO(BaseDTO):
    id: str
    username: str
```

## When to Create New DTOs

- Returning data from functions/methods
- Request bodies for API endpoints
- Response bodies for API endpoints
- Dependency injection returns

## Generic Service Pattern

```python
from typing import TypeVar, Generic
from shared.base_dto import BaseDTO

T = TypeVar('T', bound=BaseDTO)

class BaseService(Generic[T]):
    """Generic service pattern for CRUD operations."""

    def __init__(self, repo, audit_trail):
        self.repo = repo
        self.audit_trail = audit_trail

    def get_by_id(self, item_id: str) -> T:
        """Get item by ID."""
        item = self.repo.get_by_id(item_id)
        return self._to_dto(item)

    def list_all(self) -> list[T]:
        """List all items."""
        items = self.repo.list_all()
        return [self._to_dto(item) for item in items]

    def _to_dto(self, model) -> T:
        """Convert model to DTO - override in subclass."""
        return T(**model.model_dump())

# Usage
class UserService(BaseService[UserDTO]):
    def _to_dto(self, user) -> UserDTO:
        return UserDTO(**user.model_dump())
```

## Anti-Patterns to Avoid

### Returning Dicts
```python
# WRONG: Untyped dict return
def get_user(user_id: str) -> dict:
    user = db.get_user(user_id)
    return {"id": user.id, "name": user.name}
```

### Returning Database Models
```python
# WRONG: Exposing database model
def get_user(user_id: str) -> UserModel:
    return db.get_user(user_id)
```

### Mixing Models and DTOs
```python
# WRONG: Inconsistent types
def process_user(user: UserDTO) -> UserModel:
    # Bad: switching between types
    return UserModel(**user.model_dump())
```

### Untyped Lists
```python
# WRONG: List without type parameter
def list_users() -> list:
    return [UserDTO(...) for user in users]

# CORRECT
def list_users() -> list[UserDTO]:
    return [UserDTO(...) for user in users]
```

## Testing with DTOs

```python
import pytest
from shared.dtos.core.auth_dtos import SafeUserDTO

def test_auth_service_validate_session():
    service = AuthService(mock_session)

    result = service.validate_session("valid-session-id")

    # Result is strongly typed
    assert isinstance(result, SafeUserDTO)
    assert result.id == "user-123"
    assert result.username == "john"

    # Type hints work in IDE
    assert isinstance(result.username, str)
```

## FastAPI Integration

```python
from fastapi import FastAPI
from shared.dtos.core.auth_dtos import SafeUserDTO

app = FastAPI()

# FastAPI automatically serializes DTOs using model_dump()
@app.get("/me")
def get_current_user(
    user: SafeUserDTO = Depends(get_current_user),
) -> SafeUserDTO:
    """Get current user. FastAPI handles JSON serialization."""
    return user  # Type safe, auto-documented in OpenAPI

# Response model automatically validates and serializes
@app.get("/users/{user_id}")
def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> UserDTO:  # FastAPI validates response matches UserDTO
    """Get user by ID."""
    return service.get_by_id(user_id)
```
