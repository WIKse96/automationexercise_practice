import pytest
from playwright.sync_api import Page
from pages.products_page import ProductsPage
from pages.cart_page import CartPage


@pytest.mark.ui
class TestCartPage:
    def _add_item_to_cart(self, page: Page, base_url: str) -> None:
        page.goto(f"{base_url}/products")
        products = ProductsPage(page)
        products.add_to_cart(0)
        page.locator("button:has-text('Continue Shopping')").click()

    @pytest.mark.smoke
    def test_cart_is_empty_by_default(self, page: Page, base_url: str) -> None:
        page.goto(f"{base_url}/view_cart")
        cart = CartPage(page)
        assert cart.is_empty()

    def test_product_appears_in_cart(self, page: Page, base_url: str) -> None:
        self._add_item_to_cart(page, base_url)
        cart = CartPage(page)
        cart.open()
        assert cart.get_cart_item_count() == 1

    def test_remove_product_from_cart(self, page: Page, base_url: str) -> None:
        self._add_item_to_cart(page, base_url)
        cart = CartPage(page)
        cart.open()
        cart.remove_product(0)
        page.wait_for_timeout(500)
        assert cart.is_empty()

    def test_proceed_to_checkout_redirects_to_login(self, page: Page, base_url: str) -> None:
        self._add_item_to_cart(page, base_url)
        cart = CartPage(page)
        cart.open()
        cart.proceed_to_checkout()
        cart.register_login_link.click()
        assert "/login" in page.url
