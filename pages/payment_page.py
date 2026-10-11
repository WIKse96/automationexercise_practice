from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class PaymentPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # --- DOM selectors ---
    @property
    def name_on_card_input(self) -> Locator:
        return self.page.locator("[data-qa='name-on-card']")

    @property
    def card_number_input(self) -> Locator:
        return self.page.locator("[data-qa='card-number']")

    @property
    def cvc_input(self) -> Locator:
        return self.page.locator("[data-qa='cvc']")

    @property
    def expiry_month_input(self) -> Locator:
        return self.page.locator("[data-qa='expiry-month']")

    @property
    def expiry_year_input(self) -> Locator:
        return self.page.locator("[data-qa='expiry-year']")

    @property
    def pay_button(self) -> Locator:
        return self.page.locator("[data-qa='pay-button']")

    # --- Actions ---
    def fill_card_details(
        self,
        name_on_card: str,
        card_number: str,
        cvc: str,
        expiry_month: str,
        expiry_year: str,
    ) -> None:
        self.name_on_card_input.fill(name_on_card)
        self.card_number_input.fill(card_number)
        self.cvc_input.fill(cvc)
        self.expiry_month_input.fill(expiry_month)
        self.expiry_year_input.fill(expiry_year)

    def pay(self) -> None:
        self.pay_button.click()
