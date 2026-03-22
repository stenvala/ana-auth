"""E2E test for the landing page."""

import pytest
from playwright.async_api import Page, expect

pytestmark = pytest.mark.e2e


@pytest.mark.asyncio
async def test_landing_page_displays_branding(page: Page, e2e_base_url: str) -> None:
    """Landing page should load and display ana-auth branding."""
    await page.goto(e2e_base_url)
    await page.wait_for_load_state("networkidle")

    title = page.locator("[data-test-id='landing-title']")
    await expect(title).to_be_visible()
    await expect(title).to_have_text("ana-auth")

    subtitle = page.locator("[data-test-id='landing-subtitle']")
    await expect(subtitle).to_be_visible()
    await expect(subtitle).to_have_text("Authentication Service")
