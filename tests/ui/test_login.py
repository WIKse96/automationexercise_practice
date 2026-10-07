import pytest
from playwright.sync_api import Page
from pages.login_page import LoginPage


@pytest.mark.ui
class TestLoginPage:
    @pytest.mark.smoke
    def test_login_with_valid_credentials(self, page: Page, base_url: str, test_user: dict) -> None:
        page.goto(f"{base_url}/login")
        login = LoginPage(page)
        login.login(test_user["email"], test_user["password"])
        assert login.is_logged_in()

    def test_login_with_invalid_credentials(self, page: Page, base_url: str) -> None:
        page.goto(f"{base_url}/login")
        login = LoginPage(page)
        login.login("wrong@email.com", "wrongpassword")
        assert login.is_login_error_visible()

    def test_register_with_existing_email(self, page: Page, base_url: str, test_user: dict) -> None:
        page.goto(f"{base_url}/login")
        login = LoginPage(page)
        login.start_registration(test_user["name"], test_user["email"])
        assert login.is_register_error_visible()

    def test_logout_after_login(self, page: Page, base_url: str, test_user: dict) -> None:
        page.goto(f"{base_url}/login")
        login = LoginPage(page)
        login.login(test_user["email"], test_user["password"])
        login.nav_logout.click()
        assert page.url == f"{base_url}/login"
