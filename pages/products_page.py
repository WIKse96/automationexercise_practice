from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class ProductsPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # --- DOM selectors ---
    @property
    def search_input(self) -> Locator:
        return self.page.locator("input#search_product")

    @property
    def search_button(self) -> Locator:
        return self.page.locator("button#submit_search")

    @property
    def product_list(self) -> Locator:
        return self.page.locator(".product-image-wrapper")

    @property
    def searched_products_header(self) -> Locator:
        return self.page.locator("h2:has-text('Searched Products')")

    # --- Actions ---
    def open(self) -> None:
        self.goto("products")

    def search(self, query: str) -> None:
        self.search_input.fill(query)
        self.search_button.click()

    def get_product_count(self) -> int:
        return self.product_list.count()

    def open_product(self, index: int = 0) -> None:
        self.product_list.nth(index).locator("a:has-text('View Product')").click()

    def add_to_cart(self, index: int = 0) -> None:
        item = self.product_list.nth(index)
        item.hover()
        item.locator(".add-to-cart").click()

    def get_product_name(self, index: int = 0) -> str:
        return self.product_list.nth(index).locator("p").inner_text()

    def filter_by_category(self, category: str, subcategory: str) -> None:
        self.page.locator(f"a:has-text('{category}')").click()
        self.page.locator(f"a:has-text('{subcategory}')").click()
