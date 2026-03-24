from playwright.sync_api import Page

BASE_URL = "http://127.0.0.1:8000"

def login(page, username, password):
    page.goto(f"{BASE_URL}/api/auth/login/")
    page.fill("input[name='username']", username)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")