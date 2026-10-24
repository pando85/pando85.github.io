#!/usr/bin/env python3
"""Exercise the rendered homepage in Chromium, including links, menu and clipboard."""
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

    crab = page.locator(".nav-brand .crab-logo img")
    assert crab.count() == 1
    assert crab.evaluate("(image) => image.complete && image.naturalWidth > 0"), "Crab logo did not load"
    assert page.locator(".diagram-crab img").count() == 1
    cards = page.locator("a.capability-card")
    assert cards.count() == 6
    for i in range(cards.count()):
        card = cards.nth(i)
        assert card.locator("svg.landing-icon").count() == 1, f"Card {i} has no semantic SVG icon"
        assert "/docs/kaniop/" in card.get_attribute("href"), f"Card {i} has no docs link"

    backup = page.get_by_role("link", name="Backup & restore")
    assert backup.get_by_text("Experimental").is_visible()
    assert "not yet supported for production" in backup.inner_text().lower()

    # The examples must be real, navigable Kubernetes resources, not decorative tabs.
    tabs = page.get_by_role("tab")
    assert tabs.count() == 3
    cluster = page.get_by_role("tabpanel", name="Cluster")
    person = page.get_by_role("tabpanel", name="Person")
    oauth2 = page.get_by_role("tabpanel", name="OAuth2 client")
    assert cluster.is_visible() and not person.is_visible() and not oauth2.is_visible()

    # Capture the top of the page *before* interactions scroll the sticky header.
    if width in (1440, 390):
        Path("screenshots").mkdir(exist_ok=True)
        page.screenshot(path=f"screenshots/landing-{width}.png", full_page=True, animations="disabled")

    tabs.nth(0).focus()
    page.keyboard.press("ArrowRight")
    assert tabs.nth(1).get_attribute("aria-selected") == "true"
    assert person.is_visible() and not cluster.is_visible()
    assert "KanidmPersonAccount" in person.inner_text()
    assert page.locator("#hero-code-filename").inner_text() == "person.yaml"
    assert page.locator(".code-doc-link").get_attribute("href").endswith("/usage/person.html")

    page.keyboard.press("End")
    assert oauth2.is_visible() and not person.is_visible()
    assert "KanidmOAuth2Client" in oauth2.inner_text()
    assert page.locator(".code-doc-link").get_attribute("href").endswith("/usage/oauth2.html")
    page.keyboard.press("Home")
    assert cluster.is_visible()
    assert tabs.nth(0).get_attribute("aria-selected") == "true"

    # The page explains which component owns the identity server.
    explainer = page.locator(".hero-explainer")
    assert explainer.is_visible()
    assert explainer.get_by_role("link", name="Kanidm").get_attribute("href") == "https://kanidm.com"

    if width <= 540:
        # Reject unreadable < 12px labels that previously shipped in the mobile diagram.
        for selector in (".diagram-row small", ".diagram-disclaimer", ".diagram-process small"):
            size = page.locator(selector).first.evaluate(
                "(el) => parseFloat(getComputedStyle(el).fontSize)"
            )
            assert size >= 12, f"{selector} is only {size}px at {width}px"

    if width <= 820:
        assert page.locator(".mobile-menu summary").is_visible()
        assert not page.locator(".nav-right").is_visible()
        page.locator(".mobile-menu summary").click()
        assert page.locator(".mobile-menu-list a[href='/#features']").is_visible()
        page.locator(".mobile-menu-list a[href='/#features']").click()
        assert page.url.endswith("/#features")
        assert not page.locator(".mobile-menu").evaluate("(menu) => menu.open"), (
            "Mobile menu must close after choosing an anchor"
        )
        assert page.locator("#features-title").is_visible()
        page.locator(".mobile-menu summary").click()
        page.locator(".mobile-menu summary").press("Escape")
        assert not page.locator(".mobile-menu").evaluate("(menu) => menu.open"), (
            "Mobile menu must close on Escape"
        )
    else:
        assert page.locator(".nav-right").is_visible()
        assert not page.locator(".mobile-menu").is_visible()

    if width == 1440:
        page.context.grant_permissions(["clipboard-read", "clipboard-write"])
        page.get_by_role("button", name="Copy Helm installation commands").click()
        assert page.get_by_role("status").get_by_text("Commands copied to clipboard.").is_visible()
        copied = page.evaluate("navigator.clipboard.readText()")
        assert "helm install --create-namespace" in copied
        assert "kubectl get pods -n kaniop" in copied

    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"), (
        f"Unexpected horizontal page overflow at {width}px"
    )
    assert not errors, f"JavaScript errors at {width}px: {errors}"
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
            for width, height in ((1440, 900), (768, 900), (390, 844), (320, 700)):
                verify_page(browser, width, height)
        finally:
            browser.close()
    print("Desktop, tablet and mobile smoke tests passed; review screenshots are available.")


if __name__ == "__main__":
    main()
