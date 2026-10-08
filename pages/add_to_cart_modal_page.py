from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class AddToCartModalPage(BasePage):
    # Modal "Added!" po kliknięciu Add to cart — ten sam #cartModal pojawia się
    # zarówno na listingu (/products), jak i na karcie produktu (/product_details/<id>).

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # --- DOM selectors ---
    @property
    def modal(self) -> Locator:
        return self.page.locator("#cartModal")

    @property
    def title(self) -> Locator:
        return self.modal.locator(".modal-title")

    @property
    def body_text(self) -> Locator:
        return self.modal.locator(".modal-body p").first

    @property
    def view_cart_link(self) -> Locator:
        return self.modal.locator("a[href='/view_cart']")

    @property
    def continue_shopping_button(self) -> Locator:
        return self.modal.locator(".close-modal")

    # --- Actions ---
    def is_open(self) -> bool:
        return self.modal.is_visible()

    def click_view_cart(self) -> None:
        self.view_cart_link.click()

    def continue_shopping(self) -> None:
        self.continue_shopping_button.click()
