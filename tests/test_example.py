import re
from playwright.sync_api import Page, expect

def test_has_title(page: Page):
    page.goto("https://playwright.dev/")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Playwright"))

def test_get_started_link(page: Page):
    page.goto("https://playwright.dev/")

    # Click the get started link.
    page.get_by_role("link", name="Get started").click()

    # Expects page to have a heading with the name of Installation.
    expect(page.get_by_role("heading", name="Installationt")).to_be_visible()

def test_error_occured(page: Page):
    page.goto("https://playwright.dev/")

    # Click the get started link.
    page.get_by_text("API").click()

    # Expects page to have a heading with the name of Installation.
    expect(page.get_by_role("heading", name="Installationt")).to_be_visible()

def test_visible_locator(page: Page):
    page.goto("https://playwright.dev/")

    # Expects page to have a heading with the name of Installation.
    expect(page.get_by_role("heading", name="Installationtt")).to_be_visible()

def test_visible_locator2(page: Page):
    page.goto("https://playwright.dev/")

    # Expects page to have a heading with the name of Installation.
    expect(page.get_by_role("heading", name="Installationtt")).to_be_visible()