import pytest
from playwright.sync_api import Page
from pages.products_page import ProductsPage
from pages.cart_page import CartPage


@pytest.mark.ui
class TestProductsPage:
    @pytest.mark.smoke
    def test_products_page_loads(self, page: Page, base_url: str) -> None:
        page.goto(f"{base_url}/products")
        products = ProductsPage(page)
        assert "Products" in products.get_title()
        assert products.get_product_count() > 0

    def test_search_returns_results(self, page: Page, base_url: str) -> None:
        page.goto(f"{base_url}/products")
        products = ProductsPage(page)
        products.search("dress")
        assert products.searched_products_header.is_visible()
        assert products.get_product_count() > 0

    def test_search_shows_no_results_for_garbage(self, page: Page, base_url: str) -> None:
        page.goto(f"{base_url}/products")
        products = ProductsPage(page)
        products.search("xyznonexistentproduct999")
        assert products.searched_products_header.is_visible()
        assert products.get_product_count() == 0

    def test_product_detail_page_opens(self, page: Page, base_url: str) -> None:
        page.goto(f"{base_url}/products")
        products = ProductsPage(page)
        products.open_product(0)
        assert "/product_details/" in page.url

    def test_add_product_to_cart(self, page: Page, base_url: str) -> None:
        page.goto(f"{base_url}/products")
        products = ProductsPage(page)
        products.add_to_cart(0)
        page.locator("button:has-text('Continue Shopping')").click()
        cart = CartPage(page)
        cart.open()
        assert cart.get_cart_item_count() >= 1
