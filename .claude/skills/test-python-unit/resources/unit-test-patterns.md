# Unit Test Patterns

Unit tests use **mocking** for dependencies and test **all scenarios** including error cases.

## Key Principles

1. **Use mocking** - MagicMock, Mock, patch for dependencies
2. **Test all scenarios** - happy path, edge cases, error handling
3. **Use `db_session` fixture** - auto-rollbacks changes at end of test
4. **Isolate the unit under test** - mock everything else

## Router Unit Test

```python
"""Tests for the create_event endpoint."""

import pytest
from unittest.mock import Mock

from api.routers.private_event_router import create_event
from api.dtos.event_dtos import EventCreateDTO


@pytest.fixture
def mock_event_service():
    """Create mock event service."""
    service = Mock()
    service.create_event.return_value = Mock(id="event123", title="Test Event")
    return service


@pytest.fixture
def mock_current_user():
    """Create mock authenticated user."""
    return Mock(id="user123", full_name="Test User")


def test_create_event_success(mock_event_service, mock_current_user) -> None:
    """Test successful event creation."""
    # Arrange
    data = EventCreateDTO(title="Test Event", date="2024-06-15", country="FI")

    # Act
    result = create_event(
        data=data,
        current_user=mock_current_user,
        event_service=mock_event_service,
    )

    # Assert
    assert result.id == "event123"
    mock_event_service.create_event.assert_called_once()
```

## Service Unit Test

```python
"""Tests for the create_event method of EventEditorService."""

import pytest
from unittest.mock import Mock, patch

from shared.services.event_services.event_editor_service import EventEditorService
from shared.models.minimal_user import MinimalUser


@pytest.fixture
def mock_session():
    """Create mock database session."""
    return Mock()


@pytest.fixture
def event_editor_service(mock_session) -> EventEditorService:
    """Create service with mocked dependencies."""
    with patch('shared.services.event_services.event_editor_service.EventRepository') as mock_repo, \
         patch('shared.services.event_services.event_editor_service.EventAuditRepository') as mock_audit:
        service = EventEditorService(mock_session)
        service.event_repo = mock_repo.return_value
        service.audit_repo = mock_audit.return_value
        return service


def test_create_event_success(event_editor_service: EventEditorService) -> None:
    """Test successful event creation."""
    # Arrange
    data = Mock(title="Test Event", date="2024-06-15", country="FI")
    user = MinimalUser(id="user123", full_name="Test User")
    event_editor_service.event_repo.create.return_value = Mock(
        id="event123", title="Test Event"
    )

    # Act
    result = event_editor_service.create_event(data, user)

    # Assert
    assert result.id == "event123"
    event_editor_service.event_repo.create.assert_called_once()
    event_editor_service.audit_repo.create.assert_called_once()
```

## Repository Unit Test

```python
"""Tests for the get_by_id method of EventRepository."""

import pytest
from sqlmodel import Session

from shared.db.repositories.event_repository.event_repository import EventRepository
from shared.db.models.event_models.event import Event


def test_get_by_id_found(db_session: Session) -> None:
    """Test getting event by ID when it exists."""
    # Arrange
    repo = EventRepository(db_session)
    event = Event(id="event123", title="Test Event", group_id="group123")
    db_session.add(event)
    db_session.commit()

    # Act
    result = repo.get_by_id("event123")

    # Assert
    assert result is not None
    assert result.id == "event123"
    assert result.title == "Test Event"


def test_get_by_id_not_found(db_session: Session) -> None:
    """Test getting event by ID when it doesn't exist."""
    # Arrange
    repo = EventRepository(db_session)

    # Act
    result = repo.get_by_id("nonexistent")

    # Assert
    assert result is None
```

## Shared Fixtures (conftest.py)

```python
"""Shared fixtures for event_editor_service tests."""

import pytest
from unittest.mock import Mock

from shared.models.minimal_user import MinimalUser


@pytest.fixture
def mock_session():
    """Create mock database session."""
    return Mock()


@pytest.fixture
def mock_event_repo():
    """Create mock event repository."""
    repo = Mock()
    repo.get_by_id.return_value = Mock(id="event123", title="Test Event")
    return repo


@pytest.fixture
def test_user():
    """Create test user for audit operations."""
    return MinimalUser(id="user123", full_name="Test User")
```
