import pytest
from playwright.sync_api import Page
from pages.home_page import HomePage


@pytest.mark.ui
class TestHomePage:
    def test_home_page_title(self, page: Page, base_url: str) -> None:
        page.goto(base_url)
        home = HomePage(page)
        assert "Automation Exercise" in home.get_title()

    def test_home_page_loads_products(self, page: Page, base_url: str) -> None:
        page.goto(base_url)
        home = HomePage(page)
        assert home.get_featured_product_count() > 0

    def test_subscription_success(self, page: Page, base_url: str) -> None:
        page.goto(base_url)
        home = HomePage(page)
        home.subscribe("subscriber@test.com")
        home.wait_for(".alert-success")
        assert home.is_visible(".alert-success")

    def test_category_sidebar_visible(self, page: Page, base_url: str) -> None:
        page.goto(base_url)
        home = HomePage(page)
        assert home.category_sidebar.is_visible()

    @pytest.mark.smoke
    def test_navigation_links_visible(self, page: Page, base_url: str) -> None:
        page.goto(base_url)
        home = HomePage(page)
        assert home.nav_products.is_visible()
        assert home.nav_cart.is_visible()
        assert home.nav_login.is_visible()
