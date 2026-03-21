# E2E Test Base Infrastructure

This file contains the foundational classes needed for E2E testing with the Page Object pattern.

## Directory Structure

```
src/tests/e2e/
├── conftest.py
├── pages/
│   ├── __init__.py
│   └── base_page.py
└── utils/
    ├── __init__.py
    ├── test_paths.py
    ├── page_utils.py
    └── screenshot_on_failure.py
```

## 1. Base Page Class (src/tests/e2e/pages/base_page.py)

```python
"""Base page object that provides common functionality for all page objects."""

from abc import ABC
from typing import Optional

from playwright.async_api import Page, expect


class BasePage(ABC):
    """Base class for all page objects."""

    def __init__(self, page: Page) -> None:
        self.page = page

    # === Navigation ===

    async def goto(self, path: str) -> None:
        """Navigate to a specific path."""
        normalized_path = path if path.startswith("/") else f"/{path}"
        await self.page.goto(normalized_path)
        await self.wait_for_page_load()

    async def wait_for_page_load(self) -> None:
        """Wait for the page to be fully loaded."""
        await self.page.wait_for_load_state("networkidle")

    async def get_current_url(self) -> str:
        """Get the current URL."""
        return self.page.url

    # === Element Interaction ===

    async def click_element(self, selector: str) -> None:
        """Click an element."""
        await self.page.locator(selector).click()

    async def fill_input(self, selector: str, value: str) -> None:
        """Fill an input field."""
        await self.page.locator(selector).fill(value)

    async def clear_input(self, selector: str) -> None:
        """Clear an input field."""
        await self.page.locator(selector).clear()

    async def get_text(self, selector: str) -> str:
        """Get text content from an element."""
        return await self.page.locator(selector).text_content() or ""

    async def get_input_value(self, selector: str) -> str:
        """Get the current value of an input field."""
        return await self.page.locator(selector).input_value()

    # === Element Visibility/State ===

    async def is_element_visible(self, selector: str, timeout: int = 1000) -> bool:
        """Check if an element is visible."""
        try:
            await expect(self.page.locator(selector)).to_be_visible(timeout=timeout)
            return True
        except Exception:
            return False

    async def is_element_enabled(self, selector: str, timeout: int = 1000) -> bool:
        """Check if an element is enabled."""
        try:
            await expect(self.page.locator(selector)).to_be_enabled(timeout=timeout)
            return True
        except Exception:
            return False

    # === Waiting/Assertions ===

    async def wait_for_element(self, selector: str, timeout: int = 10000) -> None:
        """Wait for an element to be visible."""
        await expect(self.page.locator(selector)).to_be_visible(timeout=timeout)

    async def wait_for_element_hidden(self, selector: str, timeout: int = 10000) -> None:
        """Wait for an element to be hidden."""
        await self.page.wait_for_selector(selector, state="hidden", timeout=timeout)

    async def wait_for_text(self, text: str, timeout: int = 10000) -> None:
        """Wait for text to be visible on the page."""
        await expect(self.page.get_by_text(text)).to_be_visible(timeout=timeout)

    async def wait_for_url(self, url_pattern: str, timeout: int = 10000) -> None:
        """Wait for URL to match pattern."""
        await self.page.wait_for_url(url_pattern, timeout=timeout)

    async def expect_url(self, url_pattern: str) -> None:
        """Assert current URL matches pattern."""
        await expect(self.page).to_have_url(url_pattern)

    # === Dropdown/Selection ===

    async def select_dropdown_option(self, selector: str, option_value: str) -> None:
        """Select an option from a native dropdown."""
        await self.page.locator(selector).select_option(option_value)

    async def select_mat_option(self, trigger_selector: str, option_text: str) -> None:
        """Select an option from Angular Material dropdown."""
        await self.click_element(trigger_selector)
        await self.page.get_by_role("option", name=option_text, exact=True).click()

    # === Attributes ===

    async def get_element_attribute(
        self, selector: str, attribute: str
    ) -> Optional[str]:
        """Get an attribute value from an element."""
        return await self.page.locator(selector).get_attribute(attribute)

    # === Count ===

    async def get_element_count(self, selector: str) -> int:
        """Get count of elements matching selector."""
        return await self.page.locator(selector).count()
```

## 2. Pytest Configuration (src/tests/e2e/conftest.py)

```python
"""Pytest configuration and fixtures for E2E tests."""

import uuid
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from playwright.async_api import Playwright, async_playwright
from sqlalchemy import create_engine
from sqlmodel import Session

# Import your models as needed
# from shared.db.models.user_models.user_account import UserAccount


# === Configuration ===

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"
BASE_URL = "http://localhost:4467"  # Your Angular dev server
E2E_SCHEMA = "e2e"


@pytest.fixture(scope="function")
def e2e_test_schema() -> str:
    """Schema name for E2E test database isolation."""
    return E2E_SCHEMA


@pytest.fixture(scope="function")
def e2e_db_session(e2e_test_schema: str) -> Generator[Session, None, None]:
    """Database session for E2E test data setup."""
    schema_name = f"your-app-{e2e_test_schema}"
    test_engine = create_engine(
        f"{DATABASE_URL}?options=-csearch_path%3D{schema_name}"
    )
    try:
        with Session(test_engine) as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()
    finally:
        test_engine.dispose()


# === Browser Configuration ===

@pytest.fixture(scope="session")
def headless_mode() -> bool:
    """Run browser in headless mode. Override with --headed flag."""
    return True


@pytest.fixture(scope="session")
def slowmo_delay() -> int:
    """Slow motion delay in ms for debugging. Set to 0 for normal speed."""
    return 0


@pytest_asyncio.fixture(scope="session")
async def playwright() -> AsyncGenerator[Playwright, None]:
    """Playwright instance for E2E tests."""
    async with async_playwright() as p:
        yield p


# === Test User Fixtures ===

@pytest.fixture(scope="function")
def test_user(e2e_db_session: Session):
    """Create a test user in the database.

    Customize based on your UserAccount model.
    """
    from shared.db.models.user_models.user_account import UserAccount

    username = f"testuser-{uuid.uuid4().hex[:6]}"

    user = UserAccount(
        id=f"e2e-user-{uuid.uuid4().hex[:8]}",
        user_name=username,
        # Add other required fields...
    )

    e2e_db_session.add(user)
    e2e_db_session.commit()
    e2e_db_session.refresh(user)

    return user
```

## 3. Screenshot on Failure Utility (src/tests/e2e/utils/screenshot_on_failure.py)

```python
"""Artifact capture utilities for E2E test debugging."""

import contextvars
import datetime
import json
from functools import wraps
from pathlib import Path
from typing import Any, Callable

from playwright.async_api import BrowserContext, Page

# Context variables for artifact capture
_current_page: contextvars.ContextVar[Page | None] = contextvars.ContextVar(
    "current_page", default=None
)
_current_context: contextvars.ContextVar[BrowserContext | None] = contextvars.ContextVar(
    "current_context", default=None
)

# Console and network logs storage
_console_logs: contextvars.ContextVar[list[dict]] = contextvars.ContextVar(
    "console_logs", default=[]
)
_network_logs: contextvars.ContextVar[list[dict]] = contextvars.ContextVar(
    "network_logs", default=[]
)

# Artifact directory
ARTIFACT_DIR = Path(__file__).parent.parent.parent.parent / "test-screenshots"


def register_page(page: Page) -> None:
    """Register a page for artifact capture on failure."""
    _current_page.set(page)


def register_context(context: BrowserContext) -> None:
    """Register a browser context for artifact capture."""
    _current_context.set(context)


def get_test_dir() -> Path:
    """Get directory for test artifacts."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    test_dir = ARTIFACT_DIR / timestamp
    test_dir.mkdir(parents=True, exist_ok=True)
    return test_dir


async def setup_console_logging(page: Page) -> None:
    """Set up console log capture."""
    logs: list[dict] = []
    _console_logs.set(logs)

    async def handle_console(msg: Any) -> None:
        logs.append({
            "type": msg.type,
            "text": msg.text,
            "timestamp": datetime.datetime.now().isoformat(),
        })

    page.on("console", handle_console)


async def setup_network_logging(page: Page) -> None:
    """Set up network request logging (XHR only)."""
    requests: list[dict] = []
    _network_logs.set(requests)

    async def handle_request(request: Any) -> None:
        if request.resource_type == "xhr":
            requests.append({
                "method": request.method,
                "url": request.url,
                "timestamp": datetime.datetime.now().isoformat(),
            })

    page.on("request", handle_request)


async def _save_artifacts(test_name: str) -> None:
    """Save all artifacts on test failure."""
    page = _current_page.get()
    if not page:
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    artifact_dir = ARTIFACT_DIR / f"{test_name}_{timestamp}"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    # Screenshot
    try:
        await page.screenshot(path=artifact_dir / "screenshot.png", full_page=True)
    except Exception:
        pass

    # Console logs
    console_logs = _console_logs.get()
    if console_logs:
        with open(artifact_dir / "console.json", "w") as f:
            json.dump(console_logs, f, indent=2)

    # Network logs
    network_logs = _network_logs.get()
    if network_logs:
        with open(artifact_dir / "network.json", "w") as f:
            json.dump(network_logs, f, indent=2)


def run_with_screenshot_on_failure(
    run_func: Callable[..., Any], test_name: str
) -> Callable[..., Any]:
    """Decorator to capture artifacts on test failure."""

    @wraps(run_func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await run_func(*args, **kwargs)
        except Exception:
            await _save_artifacts(test_name)
            raise

    return wrapper
```

## 4. Page Utilities (src/tests/e2e/utils/page_utils.py)

```python
"""Page utility functions."""

from playwright.async_api import Page


async def ignore_fonts(page: Page) -> None:
    """Ignore Google Fonts requests to avoid warnings."""
    await page.route("**/fonts.googleapis.com/**", lambda route: route.abort())
    await page.route("**/fonts.google.com/**", lambda route: route.abort())
```

## 5. Test Paths (src/tests/e2e/utils/test_paths.py)

```python
"""URL path constants for E2E tests.

Mirror your frontend PATHS constants here.
"""

from typing import Final


def build_url(path: str) -> str:
    """Build URL from path."""
    return f"/{path}" if not path.startswith("/") else path


# Common paths
LOGIN: Final[str] = build_url("auth/login")
REGISTER: Final[str] = build_url("auth/register")
HOME: Final[str] = build_url("home")


class PrivatePaths:
    """Private (authenticated) paths."""

    HOME: Final[str] = build_url("pri/home")

    @staticmethod
    def group_events(group_id: str) -> str:
        """Build group events URL."""
        return build_url(f"pri/group/{group_id}/events")

    @staticmethod
    def event_view(group_id: str, event_id: str) -> str:
        """Build event view URL."""
        return build_url(f"pri/group/{group_id}/events/{event_id}/view")

    @staticmethod
    def event_edit(group_id: str, event_id: str) -> str:
        """Build event edit URL."""
        return build_url(f"pri/group/{group_id}/events/{event_id}/edit")
```
