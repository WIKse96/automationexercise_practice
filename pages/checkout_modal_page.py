from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class CheckoutModalPage(BasePage):
    # Modal proszący o zalogowanie się — pojawia się po kliknięciu
    # "Proceed To Checkout" na koszyku, gdy użytkownik nie jest zalogowany.

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # --- DOM selectors ---
    @property
    def modal(self) -> Locator:
        return self.page.locator("#checkoutModal")

    @property
    def title(self) -> Locator:
        return self.modal.locator(".modal-title")

    @property
    def login_link(self) -> Locator:
        return self.modal.locator('a[href="/login"]')

    @property
    def continue_on_cart_button(self) -> Locator:
        return self.modal.locator(".close-checkout-modal")

    # --- Actions ---
    def is_open(self) -> bool:
        return self.modal.is_visible()

    def click_login(self) -> None:
        self.login_link.click()

    def continue_on_cart(self) -> None:
        self.continue_on_cart_button.click()
