#!/usr/bin/env python3
"""Smoke-test desktop/mobile layout and navigation against a locally served Jekyll build."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

SITE = "http://127.0.0.1:8765/"


def verify_page(browser, width, height):
    page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    response = page.goto(SITE, wait_until="load", timeout=30000)
    assert response and response.ok, f"Homepage returned {response.status if response else 'no response'}"
    assert page.locator("#hero-title").is_visible()
    assert page.locator(".code-window").is_visible()
    assert page.locator(".capability-card").count() == 6
    assert page.locator("a[href*='quickstart.html']").count() >= 2

    if width <= 820:
        assert page.locator(".mobile-menu summary").is_visible()
        assert not page.locator(".nav-right").is_visible()
        page.locator(".mobile-menu summary").click()
        assert page.locator(".mobile-menu-list a[href='/#features']").is_visible()
        page.locator(".mobile-menu-list a[href='/#features']").click()
        assert page.url.endswith("/#features")
        assert page.locator("#features-title").is_visible()
    else:
        assert page.locator(".nav-right").is_visible()
        assert not page.locator(".mobile-menu").is_visible()

    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"), (
        f"Unexpected horizontal page overflow at {width}px"
    )
    assert not errors, f"JavaScript errors at {width}px: {errors}"
    Path("screenshots").mkdir(exist_ok=True)
    page.screenshot(path=f"screenshots/landing-{width}.png", full_page=True, animations="disabled")
    page.close()


def main():
    chrome = next((path for name in ("google-chrome", "google-chrome-stable", "chromium")
                   if (path := shutil.which(name))), None)
    if chrome is None:
        raise RuntimeError("Chrome/Chromium must be installed on the CI runner")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=chrome, headless=True,
                                             args=["--no-sandbox"])
        try:
            verify_page(browser, 1440, 900)
            verify_page(browser, 390, 844)
        finally:
            browser.close()
    print("Desktop and mobile smoke tests passed; snapshots written to screenshots/")


if __name__ == "__main__":
    main()
