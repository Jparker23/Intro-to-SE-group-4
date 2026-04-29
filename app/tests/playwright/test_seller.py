from playwright.sync_api import Page, expect
from conftest import login, BASE_URL

def test_seller_can_view_inventory(page: Page):
    login(page, "vinylvault", "wriug-7qo$ab-9mqwoy")
    page.goto(f"{BASE_URL}/api/inventory/")
    expect(page).to_have_url(f"{BASE_URL}/api/inventory/")
    expect(page.locator("body")).to_be_visible()

def test_seller_can_create_product(page: Page):
    login(page, "vinylvault", "wriug-7qo$ab-9mqwoy")
    page.goto(f"{BASE_URL}/api/seller/products/new/")
    page.select_option("select[name='category']", label="Record")
    page.fill("input[name='name']", "Playwright Test Record")
    page.fill("textarea[name='description']", "Created by Playwright")
    page.fill("input[name='price']", "19.99")
    page.fill("input[name='stock']", "5")
    page.click("button[type='submit']")
    expect(page).to_have_url(f"{BASE_URL}/api/inventory/")

def test_seller_can_edit_price_and_stock(page: Page):
    login(page, "vinylvault", "wriug-7qo$ab-9mqwoy")
    page.goto(f"{BASE_URL}/api/inventory/")
    edit_link = page.locator("a:has-text('Edit')").first
    edit_link.evaluate("el => el.click()")
    page.fill("input[name='price']", "29.99")
    page.fill("input[name='stock']", "10")
    page.click("button[type='submit']")
    expect(page).to_have_url(f"{BASE_URL}/api/inventory/")

def test_seller_can_edit_name_sets_pending(page: Page):
    login(page, "vinylvault", "wriug-7qo$ab-9mqwoy")
    page.goto(f"{BASE_URL}/api/inventory/")
    edit_link = page.locator("a:has-text('Edit')").first
    edit_link.evaluate("el => el.click()")
    page.fill("input[name='name']", "Updated Name")
    page.click("button[type='submit']")
    expect(page).to_have_url(f"{BASE_URL}/api/inventory/")
    expect(page.locator("body")).to_contain_text("Pending")

def test_seller_can_delist_product(page: Page):
    login(page, "vinylvault", "wriug-7qo$ab-9mqwoy")
    page.goto(f"{BASE_URL}/api/inventory/")
    delist_button = page.locator("button:has-text('Delist')").first
    delist_button.evaluate("el => el.click()")
    expect(page).to_have_url(f"{BASE_URL}/api/inventory/")
    
def test_buyer_cannot_access_inventory(page: Page):
    login(page, "buyer", "wriug-7qo$ab-9mqwoy")
    page.goto(f"{BASE_URL}/api/inventory/")
    expect(page).not_to_have_url(f"{BASE_URL}/api/inventory/")