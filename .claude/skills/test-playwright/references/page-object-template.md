# Page Object Template

## Basic Page Object Pattern

```python
"""<Feature> page object."""

from playwright.async_api import Page

from tests.e2e.pages.base_page import BasePage
from tests.e2e.utils.test_paths import PrivatePaths


class FeatureListPage(BasePage):
    """Page object for feature list view."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        # === Selectors (all as instance variables) ===

        # Navigation and actions
        self.create_button = '[data-test-id="create-feature-button"]'
        self.refresh_button = '[data-test-id="refresh-button"]'

        # List container and items
        self.list_container = '[data-test-id="feature-list-container"]'
        self.list_items = '[data-test-id="feature-item"]'
        self.item_title = "h4"

        # States
        self.empty_state = ".card-empty-content"
        self.loading_spinner = "shared-loading-spinner"

    # === Navigation Methods ===

    async def goto_feature_list(self, group_id: str) -> None:
        """Navigate to feature list page."""
        await self.goto(PrivatePaths.group_features(group_id))
        await self.wait_for_page_loaded()

    async def wait_for_page_loaded(self) -> None:
        """Wait for page content to be ready."""
        # Wait for loading spinner to disappear
        await self.wait_for_element_hidden(self.loading_spinner, timeout=10000)

    # === Action Methods ===

    async def click_create(self) -> None:
        """Click create button and wait for navigation."""
        await self.click_element(self.create_button)
        await self.wait_for_url("**/create")

    async def click_item_by_title(self, title: str) -> None:
        """Click on an item by its title."""
        item_selector = f'{self.list_items}:has(h4:has-text("{title}"))'
        await self.click_element(item_selector)
        await self.wait_for_url("**/view")

    # === Query Methods ===

    async def get_item_titles(self) -> list[str]:
        """Get all item titles currently displayed."""
        title_elements = await self.page.locator(
            f"{self.list_container} {self.item_title}"
        ).all()
        titles = []
        for element in title_elements:
            title = await element.text_content()
            if title:
                titles.append(title.strip())
        return titles

    async def get_item_count(self) -> int:
        """Get number of items displayed."""
        return await self.get_element_count(self.list_items)

    async def is_item_visible(self, title: str) -> bool:
        """Check if an item with specific title is visible."""
        item_selector = f'{self.list_items}:has(h4:has-text("{title}"))'
        return await self.is_element_visible(item_selector)

    async def is_empty_state_visible(self) -> bool:
        """Check if empty state is displayed."""
        return await self.is_element_visible(self.empty_state)
```

## Form Page Object Pattern

```python
"""<Feature> editor page object."""

from playwright.async_api import Page

from tests.e2e.pages.base_page import BasePage


class FeatureEditorPage(BasePage):
    """Page object for feature create/edit form."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        # === Form Fields ===
        self.title_input = '[data-test-id="feature-title-input"]'
        self.description_textarea = '[data-test-id="feature-description-input"]'
        self.status_select = '[data-test-id="feature-status-select"]'
        self.priority_input = '[data-test-id="feature-priority-input"]'

        # === Action Buttons ===
        self.save_button = '[data-test-id="save-button"]'
        self.cancel_button = '[data-test-id="cancel-button"]'
        self.delete_button = '[data-test-id="delete-button"]'

        # === States ===
        self.loading_spinner = "shared-loading-spinner"
        self.error_message = '[data-test-id="error-message"]'
        self.success_message = '[data-test-id="success-message"]'

    # === Navigation ===

    async def goto_create(self, group_id: str) -> None:
        """Navigate to create page."""
        await self.goto(f"/pri/group/{group_id}/features/create")
        await self.wait_for_form_loaded()

    async def goto_edit(self, group_id: str, feature_id: str) -> None:
        """Navigate to edit page."""
        await self.goto(f"/pri/group/{group_id}/features/{feature_id}/edit")
        await self.wait_for_form_loaded()

    async def wait_for_form_loaded(self) -> None:
        """Wait for form to be ready for interaction."""
        await self.wait_for_element_hidden(self.loading_spinner, timeout=10000)
        await self.wait_for_element(self.title_input)

    # === Form Field Methods ===

    async def fill_title(self, title: str) -> None:
        """Fill the title field."""
        await self.fill_input(self.title_input, title)

    async def fill_description(self, description: str) -> None:
        """Fill the description field."""
        await self.fill_input(self.description_textarea, description)

    async def select_status(self, status: str) -> None:
        """Select a status from the dropdown."""
        await self.select_mat_option(self.status_select, status)

    async def fill_priority(self, priority: int) -> None:
        """Fill the priority field."""
        await self.fill_input(self.priority_input, str(priority))

    # === Get Current Values ===

    async def get_title(self) -> str:
        """Get current title value."""
        return await self.get_input_value(self.title_input)

    async def get_description(self) -> str:
        """Get current description value."""
        return await self.get_input_value(self.description_textarea)

    # === Form Actions ===

    async def save(self) -> None:
        """Click save and wait for navigation to view page."""
        await self.click_element(self.save_button)
        await self.wait_for_url("**/view")

    async def cancel(self) -> None:
        """Click cancel and wait for navigation back."""
        await self.click_element(self.cancel_button)

    async def delete(self) -> None:
        """Click delete button."""
        await self.click_element(self.delete_button)

    # === Validation ===

    async def is_save_enabled(self) -> bool:
        """Check if save button is enabled."""
        return await self.is_element_enabled(self.save_button)

    async def is_error_visible(self) -> bool:
        """Check if error message is displayed."""
        return await self.is_element_visible(self.error_message)

    async def get_error_text(self) -> str:
        """Get error message text."""
        return await self.get_text(self.error_message)
```

## Login Page Object Pattern

```python
"""Login page object."""

from playwright.async_api import Page

from tests.e2e.pages.base_page import BasePage
from tests.e2e.utils.test_paths import LOGIN


class LoginPage(BasePage):
    """Page object for login functionality."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        # Selectors
        self.username_input = '[data-test-id="login-username-email-input"]'
        self.password_input = '[data-test-id="login-password-input"]'
        self.login_button = '[data-test-id="login-submit-button"]'
        self.error_message = '[data-test-id="login-error"]'
        self.user_menu = '[data-test-id="user-menu-trigger"]'
        self.logout_item = '[data-test-id="logout-menu-item"]'

    async def goto_login(self) -> None:
        """Navigate to login page."""
        await self.goto(LOGIN)

    async def login(self, username: str, password: str) -> None:
        """Fill login form and submit."""
        await self.fill_input(self.username_input, username)
        await self.fill_input(self.password_input, password)
        await self.click_element(self.login_button)

    async def login_and_wait(self, username: str, password: str) -> None:
        """Login and wait for successful redirect to home."""
        await self.goto_login()
        await self.login(username, password)
        await self.wait_for_url("**/home")

    async def clear_password(self) -> None:
        """Clear the password field."""
        await self.clear_input(self.password_input)

    async def is_error_visible(self) -> bool:
        """Check if login error is displayed."""
        return await self.is_element_visible(self.error_message)

    async def logout(self) -> None:
        """Perform logout."""
        await self.click_element(self.user_menu)
        await self.wait_for_element(self.logout_item)
        await self.click_element(self.logout_item)
        await self.wait_for_url("**/home")

    async def is_logged_in(self) -> bool:
        """Check if user is logged in (user menu visible)."""
        return await self.is_element_visible(self.user_menu, timeout=2000)
```

## Key Patterns

### Selector Strategy

1. **Primary**: `data-test-id` attributes
   ```python
   self.save_button = '[data-test-id="save-button"]'
   ```

2. **Secondary**: Playwright-specific selectors
   ```python
   self.item_with_title = f'[data-test-id="item"]:has(h4:has-text("{title}"))'
   ```

3. **Material components**: Use role selectors for options
   ```python
   await self.page.get_by_role("option", name=option_text, exact=True).click()
   ```

### Method Naming

- `goto_*` - Navigation methods
- `fill_*` - Input field methods
- `click_*` - Click action methods
- `get_*` - Query/retrieve methods
- `is_*` - Boolean state checks
- `wait_for_*` - Explicit wait methods
