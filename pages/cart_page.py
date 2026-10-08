from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class CartPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # --- DOM selectors — strona ---
    @property
    def cart_section(self) -> Locator:
        return self.page.locator("#cart_items")

    @property
    def breadcrumb_active(self) -> Locator:
        return self.page.locator(".breadcrumbs li.active")

    @property
    def cart_table(self) -> Locator:
        return self.page.locator("#cart_info_table")

    @property
    def cart_rows(self) -> Locator:
        return self.page.locator('#cart_info_table tbody tr[id^="product-"]')

    @property
    def proceed_to_checkout_button(self) -> Locator:
        return self.page.locator("#do_action a.check_out")

    @property
    def empty_cart_message(self) -> Locator:
        return self.page.locator("#empty_cart")

    @property
    def empty_cart_continue_link(self) -> Locator:
        return self.page.locator('#empty_cart a[href="/products"]')

    # --- Kolumny w obrębie wierszy (indeksowane przez .nth(index)) ---
    @property
    def row_images(self) -> Locator:
        return self.cart_rows.locator("td.cart_product img.product_image")

    @property
    def row_names(self) -> Locator:
        return self.cart_rows.locator("td.cart_description h4 a")

    @property
    def row_categories(self) -> Locator:
        return self.cart_rows.locator("td.cart_description p")

    @property
    def row_prices(self) -> Locator:
        return self.cart_rows.locator("td.cart_price p")

    @property
    def row_quantities(self) -> Locator:
        return self.cart_rows.locator("td.cart_quantity button")

    @property
    def row_totals(self) -> Locator:
        return self.cart_rows.locator("td.cart_total p.cart_total_price")

    @property
    def row_delete_buttons(self) -> Locator:
        return self.cart_rows.locator("td.cart_delete a.cart_quantity_delete")

    # --- Actions ---
    def open(self) -> None:
        self.goto("view_cart")

    def get_cart_item_count(self) -> int:
        return self.cart_rows.count()

    def remove_product(self, index: int = 0) -> None:
        self.row_delete_buttons.nth(index).click()

    def remove_product_by_id(self, product_id: int) -> None:
        self.page.locator(f'a.cart_quantity_delete[data-product-id="{product_id}"]').click()

    def get_product_name(self, index: int = 0) -> str:
        return self.row_names.nth(index).inner_text()

    def get_product_category(self, index: int = 0) -> str:
        return self.row_categories.nth(index).inner_text()

    def get_product_price(self, index: int = 0) -> str:
        return self.row_prices.nth(index).inner_text()

    def get_product_quantity(self, index: int = 0) -> str:
        return self.row_quantities.nth(index).inner_text()

    def get_product_total(self, index: int = 0) -> str:
        return self.row_totals.nth(index).inner_text()

    def proceed_to_checkout(self) -> None:
        self.proceed_to_checkout_button.click()

    def is_empty(self) -> bool:
        return self.empty_cart_message.is_visible()
