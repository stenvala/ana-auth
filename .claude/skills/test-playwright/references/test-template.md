# Test Template

## Test File Structure

```python
"""E2E tests for <feature> functionality."""

from pathlib import Path

import pytest
from playwright.async_api import async_playwright

from shared.db.models.user_models.user_account import UserAccount
from tests.e2e.pages.login_page import LoginPage
from tests.e2e.pages.features.feature_list_page import FeatureListPage
from tests.e2e.pages.features.feature_editor_page import FeatureEditorPage
from tests.e2e.utils.page_utils import ignore_fonts
from tests.e2e.utils.screenshot_on_failure import (
    get_test_dir,
    register_context,
    register_page,
    run_with_screenshot_on_failure,
    setup_console_logging,
    setup_network_logging,
)


@pytest.mark.e2e
class TestFeatureCRUD:
    """Feature CRUD operation tests."""

    @pytest.mark.asyncio
    async def test_create_feature(
        self,
        e2e_test_schema: str,
        test_user: UserAccount,
        headless_mode: bool,
        slowmo_delay: int,
    ) -> None:
        """Test user can create a new feature."""

        async def run(playwright):
            test_dir = get_test_dir()

            # === Browser Setup ===
            browser = await playwright.chromium.launch(
                headless=headless_mode,
                slow_mo=slowmo_delay,
            )
            context = await browser.new_context(
                base_url="http://localhost:4467",
                extra_http_headers={"x-schema": e2e_test_schema},
                record_video_dir=str(test_dir),
            )
            register_context(context)

            page = await context.new_page()
            register_page(page)
            await setup_console_logging(page)
            await setup_network_logging(page)
            await ignore_fonts(page)

            # === Initialize Page Objects ===
            login_page = LoginPage(page)
            feature_list_page = FeatureListPage(page)
            feature_editor_page = FeatureEditorPage(page)

            # === Test Scenario ===

            # 1. Login
            await login_page.login_and_wait(
                test_user.user_name,
                "TestPassword123!",
            )

            # 2. Navigate to feature list
            await feature_list_page.goto_feature_list(test_user.group_id)

            # 3. Click create
            await feature_list_page.click_create()

            # 4. Fill form
            await feature_editor_page.fill_title("Test Feature")
            await feature_editor_page.fill_description("Test description")
            await feature_editor_page.select_status("Active")

            # 5. Save
            await feature_editor_page.save()

            # 6. Verify feature appears in list
            await feature_list_page.goto_feature_list(test_user.group_id)
            assert await feature_list_page.is_item_visible("Test Feature")

            # === Cleanup ===
            await login_page.logout()
            await browser.close()

        # Run with artifact capture
        async with async_playwright() as playwright:
            await run_with_screenshot_on_failure(run, Path(__file__).stem)(playwright)

    @pytest.mark.asyncio
    async def test_edit_feature(
        self,
        e2e_test_schema: str,
        test_user_with_feature: tuple,  # Custom fixture with pre-created feature
        headless_mode: bool,
        slowmo_delay: int,
    ) -> None:
        """Test user can edit an existing feature."""

        user, feature = test_user_with_feature

        async def run(playwright):
            test_dir = get_test_dir()

            browser = await playwright.chromium.launch(
                headless=headless_mode,
                slow_mo=slowmo_delay,
            )
            context = await browser.new_context(
                base_url="http://localhost:4467",
                extra_http_headers={"x-schema": e2e_test_schema},
                record_video_dir=str(test_dir),
            )
            register_context(context)

            page = await context.new_page()
            register_page(page)
            await setup_console_logging(page)
            await setup_network_logging(page)
            await ignore_fonts(page)

            login_page = LoginPage(page)
            feature_editor_page = FeatureEditorPage(page)

            # Login
            await login_page.login_and_wait(user.user_name, "TestPassword123!")

            # Navigate directly to edit page
            await feature_editor_page.goto_edit(user.group_id, feature.id)

            # Verify current values
            assert await feature_editor_page.get_title() == feature.title

            # Update title
            await feature_editor_page.fill_title("Updated Title")
            await feature_editor_page.save()

            # Verify update persisted
            await feature_editor_page.goto_edit(user.group_id, feature.id)
            assert await feature_editor_page.get_title() == "Updated Title"

            await login_page.logout()
            await browser.close()

        async with async_playwright() as playwright:
            await run_with_screenshot_on_failure(run, Path(__file__).stem)(playwright)

    @pytest.mark.asyncio
    async def test_delete_feature(
        self,
        e2e_test_schema: str,
        test_user_with_feature: tuple,
        headless_mode: bool,
        slowmo_delay: int,
    ) -> None:
        """Test user can delete a feature."""

        user, feature = test_user_with_feature

        async def run(playwright):
            # ... similar setup ...

            login_page = LoginPage(page)
            feature_list_page = FeatureListPage(page)
            feature_editor_page = FeatureEditorPage(page)

            await login_page.login_and_wait(user.user_name, "TestPassword123!")

            # Verify feature exists
            await feature_list_page.goto_feature_list(user.group_id)
            assert await feature_list_page.is_item_visible(feature.title)

            # Navigate to edit and delete
            await feature_editor_page.goto_edit(user.group_id, feature.id)
            await feature_editor_page.delete()

            # Confirm deletion dialog if needed
            # await page.click('[data-test-id="confirm-delete"]')

            # Verify feature is gone
            await feature_list_page.goto_feature_list(user.group_id)
            assert not await feature_list_page.is_item_visible(feature.title)

            await login_page.logout()
            await browser.close()

        async with async_playwright() as playwright:
            await run_with_screenshot_on_failure(run, Path(__file__).stem)(playwright)
```

## Test Patterns

### 1. Test Structure

```python
async def test_<scenario>(self, fixtures...) -> None:
    """Test description."""

    async def run(playwright):
        # 1. Browser setup
        # 2. Page object initialization
        # 3. Test scenario (Arrange-Act-Assert)
        # 4. Cleanup

    async with async_playwright() as playwright:
        await run_with_screenshot_on_failure(run, Path(__file__).stem)(playwright)
```

### 2. Fixture Usage

```python
# Use database fixtures for test data setup
@pytest.fixture(scope="function")
def test_user_with_feature(e2e_db_session: Session):
    """Create user and feature via database, not UI."""
    user = create_test_user(e2e_db_session)
    feature = create_test_feature(e2e_db_session, user.group_id)
    return (user, feature)
```

### 3. Assertions

```python
# Use page object methods for assertions
assert await feature_list_page.is_item_visible("Test Feature")
assert await feature_editor_page.get_title() == "Expected Title"
assert not await login_page.is_error_visible()
```

### 4. Error Scenario Testing

```python
@pytest.mark.asyncio
async def test_login_with_invalid_password(self, ...):
    """Test error handling for invalid credentials."""

    async def run(playwright):
        # ... setup ...

        login_page = LoginPage(page)

        await login_page.goto_login()
        await login_page.login("validuser", "wrongpassword")

        # Verify error is shown
        assert await login_page.is_error_visible()

        # Verify still on login page
        await login_page.expect_url("**/login")
```

### 5. Running Tests

```bash
# Run single test file
uv run pytest src/tests/e2e/tests/features/test_feature_crud.py -v

# Run single test method
uv run pytest src/tests/e2e/tests/features/test_feature_crud.py::TestFeatureCRUD::test_create_feature -v

# Run with visible browser
uv run pytest src/tests/e2e/tests/features/test_feature_crud.py -v --headed

# Run with slow motion for debugging
SLOWMO=500 uv run pytest src/tests/e2e/tests/features/test_feature_crud.py -v --headed
```
