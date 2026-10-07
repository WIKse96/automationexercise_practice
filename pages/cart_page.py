from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class CartPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # --- DOM selectors ---
    @property
    def cart_rows(self) -> Locator:
        return self.page.locator("tr.cart_menu ~ tr")

    @property
    def proceed_to_checkout_button(self) -> Locator:
        return self.page.locator("a.btn.btn-default.check_out")

    @property
    def continue_on_cart_modal(self) -> Locator:
        return self.page.locator("a:has-text('Continue On Cart')")

    @property
    def register_login_link(self) -> Locator:
        return self.page.locator("a:has-text('Register / Login')")

    @property
    def empty_cart_message(self) -> Locator:
        return self.page.locator("#empty_cart")

    # --- Actions ---
    def open(self) -> None:
        self.goto("view_cart")

    def get_cart_item_count(self) -> int:
        return self.cart_rows.count()

    def remove_product(self, index: int = 0) -> None:
        self.cart_rows.nth(index).locator(".cart_quantity_delete").click()

    def get_product_name(self, index: int = 0) -> str:
        return self.cart_rows.nth(index).locator("h4 a").inner_text()

    def get_product_price(self, index: int = 0) -> str:
        return self.cart_rows.nth(index).locator(".cart_price p").inner_text()

    def get_product_quantity(self, index: int = 0) -> str:
        return self.cart_rows.nth(index).locator(".cart_quantity button").inner_text()

    def proceed_to_checkout(self) -> None:
        self.proceed_to_checkout_button.click()

    def is_empty(self) -> bool:
        return self.empty_cart_message.is_visible()
