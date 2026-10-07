from playwright.sync_api import Page, Locator


class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page

    # --- Navigation ---
    def goto(self, path: str = "") -> None:
        self.page.goto(path.lstrip("/"))

    def get_title(self) -> str:
        return self.page.title()

    def get_url(self) -> str:
        return self.page.url

    # --- DOM helpers ---
    def find(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def click(self, selector: str) -> None:
        self.page.locator(selector).click()

    def fill(self, selector: str, value: str) -> None:
        self.page.locator(selector).fill(value)

    def get_text(self, selector: str) -> str:
        return self.page.locator(selector).inner_text()

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).is_visible()

    def wait_for(self, selector: str, timeout: int = 5000) -> None:
        self.page.locator(selector).wait_for(timeout=timeout)

    # --- Header nav ---
    @property
    def nav_home(self) -> Locator:
        return self.page.locator("a[href='/']")

    @property
    def nav_products(self) -> Locator:
        return self.page.locator("a[href='/products']")

    @property
    def nav_cart(self) -> Locator:
        return self.page.locator("a[href='/view_cart']")

    @property
    def nav_login(self) -> Locator:
        return self.page.locator("a[href='/login']")

    @property
    def nav_logout(self) -> Locator:
        return self.page.locator("a[href='/logout']")

    @property
    def logged_in_as(self) -> Locator:
        return self.page.locator('a:has-text("Logged in as") b')

    @property
    def nav_contact(self) -> Locator:
        return self.page.locator("a[href='/contact_us']")

    def go_to_products(self) -> None:
        self.nav_products.click()

    def go_to_cart(self) -> None:
        self.nav_cart.click()

    def go_to_login(self) -> None:
        self.nav_login.click()

    def is_logged_in(self) -> bool:
        return self.page.locator("a[href='/logout']").is_visible()

    # --- Confirmation pages (account_created, delete_account) ---
    @property
    def continue_button(self) -> Locator:
        return self.page.locator('[data-qa="continue-button"]')

    def click_continue(self) -> None:
        self.continue_button.click()
