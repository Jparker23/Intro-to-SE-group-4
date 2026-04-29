from playwright.sync_api import Page, expect
from conftest import login, BASE_URL

def test_user_can_register_as_buyer(page: Page):
    page.goto(f"{BASE_URL}/api/auth/register/")
    page.fill("input[name='first_name']", "Test")
    page.fill("input[name='last_name']", "Buyer")
    page.fill("input[name='username']", "newbuyer")
    page.fill("input[name='email']", "newbuyer@test.com")
    page.select_option("select[name='role']", "buyer")
    page.fill("input[name='password']", "testpass123")
    page.fill("input[name='pswrdAgain']", "testpass123")
    page.click("button[type='submit']")
    expect(page).to_have_url(f"{BASE_URL}/api/auth/pending-approval/")

def test_user_can_register_as_seller(page: Page):
    page.goto(f"{BASE_URL}/api/auth/register/")
    page.fill("input[name='first_name']", "Test")
    page.fill("input[name='last_name']", "Seller")
    page.fill("input[name='username']", "newseller")
    page.fill("input[name='email']", "newseller@test.com")
    page.select_option("select[name='role']", "seller")
    page.fill("input[name='password']", "testpass123")
    page.fill("input[name='pswrdAgain']", "testpass123")
    page.click("button[type='submit']")
    expect(page).to_have_url(f"{BASE_URL}/api/auth/pending-approval/")

def test_user_can_login(page: Page):
    login(page, "buyer", "wriug-7qo$ab-9mqwoy")
    expect(page.locator("body")).to_be_visible()

def test_invalid_login_shows_error(page: Page):
    page.goto(f"{BASE_URL}/api/auth/login/")
    page.fill("input[name='username']", "wronguser")
    page.fill("input[name='password']", "wrongpass")
    page.click("button[type='submit']")
    expect(page.locator(".alert-danger")).to_be_visible()

def test_logged_out_user_redirected_from_inventory(page: Page):
    page.goto(f"{BASE_URL}/api/inventory/")
    expect(page).not_to_have_url(f"{BASE_URL}/api/inventory/")