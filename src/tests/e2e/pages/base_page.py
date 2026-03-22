"""Base page object that provides common functionality for all page objects."""

from abc import ABC
from typing import Optional

from playwright.async_api import Page, expect


class BasePage(ABC):
    """Base class for all page objects."""

    def __init__(self, page: Page) -> None:
        self.page = page

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

    async def click_element(self, selector: str) -> None:
        """Click an element."""
        await self.page.locator(selector).click()

    async def fill_input(self, selector: str, value: str) -> None:
        """Fill an input field."""
        await self.page.locator(selector).fill(value)

    async def get_text(self, selector: str) -> str:
        """Get text content from an element."""
        return await self.page.locator(selector).text_content() or ""

    async def is_element_visible(self, selector: str, timeout: int = 1000) -> bool:
        """Check if an element is visible."""
        try:
            await expect(self.page.locator(selector)).to_be_visible(timeout=timeout)
            return True
        except Exception:
            return False

    async def wait_for_element(self, selector: str, timeout: int = 10000) -> None:
        """Wait for an element to be visible."""
        await expect(self.page.locator(selector)).to_be_visible(timeout=timeout)

    async def wait_for_text(self, text: str, timeout: int = 10000) -> None:
        """Wait for text to be visible on the page."""
        await expect(self.page.get_by_text(text)).to_be_visible(timeout=timeout)

    async def get_element_attribute(
        self, selector: str, attribute: str
    ) -> Optional[str]:
        """Get an attribute value from an element."""
        return await self.page.locator(selector).get_attribute(attribute)
