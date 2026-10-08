from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class ProductListingPage(BasePage):
    # Strony z siatką kafelków produktów (.features_items .product-image-wrapper) —
    # ten sam układ na stronie głównej, /brand_products/<marka> i /category_products/<id>.
    # Add to cart klika się z .product-overlay (widoczny po hover), nie z .productinfo —
    # oba mają ten sam data-product-id, więc selektor musi być zawężony do overlay.

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # --- DOM selectors ---
    @property
    def product_tiles(self) -> Locator:
        return self.page.locator(".features_items .product-image-wrapper")

    @property
    def first_product_hover_area(self) -> Locator:
        return self.product_tiles.first.locator(".single-products")

    @property
    def first_product_add_to_cart_overlay(self) -> Locator:
        return self.product_tiles.first.locator(".product-overlay a.add-to-cart")

    # --- Actions ---
    def open(self, path: str) -> None:
        self.goto(path)

    def add_first_product_to_cart(self) -> None:
        self.first_product_hover_area.hover()
        self.first_product_add_to_cart_overlay.click()
