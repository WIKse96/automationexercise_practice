from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # --- DOM selectors — headings ---
    @property
    def heading_login(self) -> Locator:
        return self.page.locator("h2:has-text('Login to your account')")

    @property
    def heading_signup(self) -> Locator:
        return self.page.locator("h2:has-text('New User Signup!')")

    # --- DOM selectors — login form ---
    @property
    def login_email(self) -> Locator:
        return self.page.locator("input[data-qa='login-email']")

    @property
    def login_password(self) -> Locator:
        return self.page.locator("input[data-qa='login-password']")

    @property
    def login_button(self) -> Locator:
        return self.page.locator("button[data-qa='login-button']")

    @property
    def login_error(self) -> Locator:
        return self.page.locator("p:has-text('Your email or password is incorrect')")

    # --- DOM selectors — register form ---
    @property
    def register_name(self) -> Locator:
        return self.page.locator("input[data-qa='signup-name']")

    @property
    def register_email(self) -> Locator:
        return self.page.locator("input[data-qa='signup-email']")

    @property
    def register_button(self) -> Locator:
        return self.page.locator("button[data-qa='signup-button']")

    @property
    def register_error(self) -> Locator:
        return self.page.locator("p:has-text('Email Address already exist')")

    # --- Actions ---
    def open(self) -> None:
        self.goto("login")

    def login(self, email: str, password: str) -> None:
        self.login_email.fill(email)
        self.login_password.fill(password)
        self.login_button.click()

    def start_registration(self, name: str, email: str) -> None:
        self.register_name.fill(name)
        self.register_email.fill(email)
        self.register_button.click()

    def is_login_error_visible(self) -> bool:
        return self.login_error.is_visible()

    def is_register_error_visible(self) -> bool:
        return self.register_error.is_visible()
