---
name: python-coding-conventions
description: Python coding standards for type safety and maintainability
---

# Python Coding Conventions

Enforce type safety and consistency across the backend codebase through Pydantic objects and strict return types.

## Core Rules

### 1. NEVER Return `dict` or `list[dict]`

Always return Pydantic DTO objects instead of dictionaries.

```python
# WRONG
def get_user(user_id: str) -> dict:
    return {"id": user.id, "username": user.username}

# CORRECT
def get_user(user_id: str) -> UserDTO:
    return UserDTO(**user.model_dump())
```

### 2. Always Use Pydantic DTOs as Return Types

- Services return Pydantic DTOs
- Dependencies return Pydantic DTOs
- Routers return Pydantic DTOs (FastAPI handles serialization)
- Never unpack Pydantic objects into dicts for return values

### 3. Always Specify Explicit Return Types

```python
# WRONG
def get_user(user_id: str):           # No return type
def get_user(user_id: str) -> dict:   # Too generic
def list_users() -> list:             # Not typed

# CORRECT
def get_user(user_id: str) -> UserDTO: ...
def list_users() -> list[UserDTO]: ...
```

### 4. Never Return Raw Lists from API Endpoints

Wrap in a response DTO with `items` and `total` fields:

```python
class UsersListResponseDTO(BaseDTO):
    items: list[UserDTO] = Field(...)
    total: int = Field(...)

@router.get("/users")
def list_users(service: UserService = Depends(...)) -> UsersListResponseDTO:
    users = service.list_all()
    return UsersListResponseDTO(items=users, total=len(users))
```

### 5. Services Must Not Return Database Models

Convert to DTOs using `model_dump()`:

```python
return UserDTO(**user.model_dump())
# Or exclude sensitive fields:
return SafeUserDTO(**user.model_dump(exclude={"password_hash"}))
```

## Checklist for Code Review

- All functions have explicit return types
- No functions return `dict` or `list[dict]`
- All functions return Pydantic objects or basic types (str, int, bool)
- Services return DTOs, not database models
- List endpoints return wrapper objects with `items` and `total` fields
- Sensitive fields excluded from public DTOs
- Type hints match actual return values

## Resources

- `resources/pydantic-patterns.md` - Complete examples: DTO hierarchy, model-to-DTO conversion, list responses, optional/sensitive fields, generic service pattern, anti-patterns, testing, FastAPI integration

