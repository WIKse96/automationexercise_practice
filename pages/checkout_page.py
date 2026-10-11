from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class CheckoutPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # --- DOM selectors ---
    @property
    def delivery_address_block(self) -> Locator:
        return self.page.locator("#address_delivery")

    @property
    def billing_address_block(self) -> Locator:
        return self.page.locator("#address_invoice")

    @property
    def checkout_button(self) -> Locator:
        return self.page.locator("a.check_out")

    @property
    def view_cart_modal_link(self) -> Locator:
        return self.page.locator(".modal-content a:has-text('View Cart')")

    # --- Actions ---
    def add_first_product_to_cart(self) -> None:
        self.goto("products")
        first = self.page.locator(".product-image-wrapper").first
        first.hover()
        first.locator(".add-to-cart").first.click()
        # Czekamy na realne pojawienie się modala (potwierdza, że AJAX dodania
        # do koszyka się zakończył) — bez tego bywa race condition i koszyk
        # bywa pusty mimo kliknięcia "Add to cart".
        self.page.wait_for_selector(".modal-content", state="visible")
        self.view_cart_modal_link.click()
        self.page.wait_for_selector("#cart_info_table tbody tr", state="visible")

    def go_to_checkout(self) -> None:
        self.checkout_button.click()

    def delivery_address_text(self) -> str:
        return self.delivery_address_block.inner_text()

    def billing_address_text(self) -> str:
        return self.billing_address_block.inner_text()
