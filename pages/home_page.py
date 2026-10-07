from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class HomePage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # --- DOM selectors ---
    @property
    def slider(self) -> Locator:
        return self.page.locator("#slider")

    @property
    def features_items(self) -> Locator:
        return self.page.locator(".features_items .product-image-wrapper")

    @property
    def category_sidebar(self) -> Locator:
        return self.page.locator("#accordian")

    @property
    def subscription_email(self) -> Locator:
        return self.page.locator("#susbscribe_email")

    @property
    def subscription_button(self) -> Locator:
        return self.page.locator("#subscribe")

    @property
    def subscription_success(self) -> Locator:
        return self.page.locator("#success-subscribe")

    # --- Actions ---
    def open(self) -> None:
        self.goto("")

    def subscribe(self, email: str) -> None:
        self.subscription_email.fill(email)
        self.subscription_button.click()

    def get_featured_product_count(self) -> int:
        return self.features_items.count()

    def click_category(self, category_name: str) -> None:
        self.page.locator(f"#accordian a:has-text('{category_name}')").click()

    def add_first_product_to_cart(self) -> None:
        first = self.features_items.first
        first.hover()
        first.locator(".add-to-cart").first.click()
