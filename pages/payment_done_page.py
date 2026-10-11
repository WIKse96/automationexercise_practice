from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class PaymentDonePage(BasePage):
    # Przycisk "Continue" (href="/") to ten sam [data-qa="continue-button"]
    # co na account_created — dziedziczony z BasePage.continue_button.

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # --- DOM selectors ---
    @property
    def order_placed_heading(self) -> Locator:
        return self.page.locator("[data-qa='order-placed']")

    @property
    def confirmation_text(self) -> Locator:
        return self.page.locator("p:has-text('Congratulations! Your order has been confirmed!')")

    @property
    def download_invoice_link(self) -> Locator:
        return self.page.locator("a:has-text('Download Invoice')")
