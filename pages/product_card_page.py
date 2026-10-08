from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class ProductCardPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # --- Karta produktu (.product-information) ---
    @property
    def product_info(self) -> Locator:
        return self.page.locator(".product-information")

    @property
    def product_name(self) -> Locator:
        return self.product_info.locator("h2")

    @property
    def product_category(self) -> Locator:
        return self.product_info.locator("p").filter(has_text="Category:")

    @property
    def product_price(self) -> Locator:
        return self.product_info.locator("> span > span")

    @property
    def quantity_input(self) -> Locator:
        return self.page.locator("#quantity")

    @property
    def add_to_cart_button(self) -> Locator:
        return self.page.locator("button.cart")

    @property
    def availability(self) -> Locator:
        return self.product_info.locator("p").filter(has_text="Availability:")

    @property
    def condition(self) -> Locator:
        return self.product_info.locator("p").filter(has_text="Condition:")

    @property
    def brand(self) -> Locator:
        return self.product_info.locator("p").filter(has_text="Brand:")

    # --- Write Your Review (#review-form) ---
    @property
    def review_tab(self) -> Locator:
        return self.page.locator("a[href='#reviews']")

    @property
    def review_name_input(self) -> Locator:
        return self.page.locator("#name")

    @property
    def review_email_input(self) -> Locator:
        return self.page.locator("#email")

    @property
    def review_text_input(self) -> Locator:
        return self.page.locator("#review")

    @property
    def review_submit_button(self) -> Locator:
        return self.page.locator("#button-review")

    @property
    def review_success_message(self) -> Locator:
        return self.page.locator("#review-section .alert-success span")

    # --- Actions ---
    def open(self, product_id: int) -> None:
        self.goto(f"product_details/{product_id}")
