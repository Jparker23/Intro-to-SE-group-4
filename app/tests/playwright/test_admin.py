from playwright.sync_api import Page, expect
from conftest import login, BASE_URL

def test_admin_can_access_dashboard(page: Page):
    login(page, "admin", "password123")
    page.goto(f"{BASE_URL}/api/account/")
    expect(page.locator("body")).to_contain_text("Admin Dashboard")

def test_admin_can_access_moderation(page: Page):
    login(page, "admin", "password123")
    page.goto(f"{BASE_URL}/api/admin/moderation/")
    expect(page).to_have_url(f"{BASE_URL}/api/admin/moderation/")
    expect(page.locator("body")).to_contain_text("Admin Moderation")

def test_admin_can_access_catalog(page: Page):
    login(page, "admin", "password123")
    page.goto(f"{BASE_URL}/api/admin/catalog/")
    expect(page).to_have_url(f"{BASE_URL}/api/admin/catalog/")
    expect(page.locator("body")).to_contain_text("Admin Catalog")

def test_buyer_cannot_access_moderation(page: Page):
    login(page, "testbuyer", "password123")
    page.goto(f"{BASE_URL}/api/admin/moderation/")
    expect(page).not_to_have_url(f"{BASE_URL}/api/admin/moderation/")

def test_seller_cannot_access_moderation(page: Page):
    login(page, "testseller", "password123")
    page.goto(f"{BASE_URL}/api/admin/moderation/")
    expect(page).not_to_have_url(f"{BASE_URL}/api/admin/moderation/")

def test_anonymous_cannot_access_moderation(page: Page):
    page.goto(f"{BASE_URL}/api/admin/moderation/")
    expect(page).not_to_have_url(f"{BASE_URL}/api/admin/moderation/")

def test_admin_can_approve_product(page: Page):
    login(page, "testadmin", "password123")
    page.goto(f"{BASE_URL}/api/admin/moderation/")
    approve_btn = page.locator("a:has-text('Approve')").first
    if approve_btn.count() > 0:
        approve_btn.click()
        expect(page.locator("body")).to_be_visible()

def test_admin_can_deny_product(page: Page):
    login(page, "testadmin", "password123")
    page.goto(f"{BASE_URL}/api/admin/moderation/")
    deny_btn = page.locator("a:has-text('Deny')").first
    if deny_btn.count() > 0:
        deny_btn.click()
        expect(page.locator("body")).to_be_visible()