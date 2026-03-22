"""Landing page object for E2E tests."""

from playwright.async_api import Page

from .base_page import BasePage


class LandingPage(BasePage):
    """Page object for the landing page."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    async def navigate(self) -> None:
        """Navigate to the landing page."""
        await self.goto("/")

    async def get_title(self) -> str:
        """Get the page title text."""
        return await self.get_text("[data-test-id='landing-title']")

    async def is_branding_visible(self) -> bool:
        """Check if ana-auth branding is visible."""
        return await self.is_element_visible("[data-test-id='landing-title']")
