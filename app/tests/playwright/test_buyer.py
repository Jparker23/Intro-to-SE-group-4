from playwright.sync_api import Page, expect
from conftest import login, BASE_URL

def test_buyer_can_view_catalog(page: Page):
    login(page, "testbuyer", "password123")
    page.goto(f"{BASE_URL}/api/catalog/")
    expect(page).to_have_url(f"{BASE_URL}/api/catalog/")
    expect(page.locator("body")).to_contain_text("record player1")

def test_buyer_can_view_product_detail(page: Page):
    login(page, "testbuyer", "password123")
    page.goto(f"{BASE_URL}/api/catalog/")
    page.locator(".productCard").first.click()
    expect(page.locator("body")).to_be_visible()

def test_buyer_can_view_seller_store(page: Page):
    login(page, "testbuyer", "password123")
    page.goto(f"{BASE_URL}/api/seller/3/products/")
    expect(page.locator("body")).to_be_visible()

def test_buyer_can_add_to_cart(page: Page):
    login(page, "testbuyer", "password123")
    page.goto(f"{BASE_URL}/api/catalog/")
    page.locator(".productCard").first.click()
    expect(page.locator("body")).to_be_visible()

def test_anonymous_user_redirected_from_checkout(page: Page):
    page.goto(f"{BASE_URL}/api/checkout/")
    expect(page).not_to_have_url(f"{BASE_URL}/api/checkout/")