import allure
import pytest
from playwright.sync_api import Page, expect

from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.products_page import ProductsPage

SUCCESS_TEXT = "You have been successfully subscribed!"

PAGES = [
    pytest.param(HomePage, id="home"),
    pytest.param(ProductsPage, id="products"),
    pytest.param(CartPage, id="cart"),
]


@allure.feature("Newsletter")
@allure.story("Subscription")
@pytest.mark.parametrize("page_class", PAGES)
def test_subscribe_with_valid_email_shows_success(
    page: Page, unique_email: str, page_class
) -> None:
    allure.dynamic.title(
        f"Subskrypcja z poprawnym e-mailem pokazuje komunikat sukcesu ({page_class.__name__})"
    )
    pom = page_class(page)
    pom.open()

    pom.subscribe(unique_email)

    expect(pom.subscription_success).to_be_visible()
    expect(pom.subscription_success).to_contain_text(SUCCESS_TEXT)


@allure.feature("Newsletter")
@allure.story("Subscription")
def test_subscribe_with_empty_email_is_blocked_by_browser_validation(
    page: Page,
) -> None:
    allure.dynamic.title("Pusty e-mail nie przechodzi walidacji HTML5 (required)")
    home = HomePage(page)
    home.open()

    home.subscription_button.click()

    expect(home.subscription_success).to_be_hidden()
    assert home.subscription_email.evaluate("el => el.validity.valid") is False


@allure.feature("Newsletter")
@allure.story("Subscription")
@pytest.mark.parametrize(
    "invalid_email",
    ["not-an-email", "missing-at-sign.com", "spaces in@email.com", "@no-local-part.com"],
)
def test_subscribe_with_invalid_email_format_is_blocked_by_browser_validation(
    page: Page, invalid_email: str
) -> None:
    allure.dynamic.title(f"Niepoprawny format e-maila '{invalid_email}' blokuje subskrypcję")
    home = HomePage(page)
    home.open()

    home.subscribe(invalid_email)

    expect(home.subscription_success).to_be_hidden()
    assert home.subscription_email.evaluate("el => el.validity.valid") is False


@allure.feature("Newsletter")
@allure.story("Subscription")
def test_success_message_disappears_and_field_clears_after_subscribe(
    page: Page, unique_email: str
) -> None:
    allure.dynamic.title("Komunikat sukcesu znika, a pole e-mail czyści się po subskrypcji")
    home = HomePage(page)
    home.open()

    home.subscribe(unique_email)
    expect(home.subscription_success).to_be_visible()

    expect(home.subscription_success).to_be_hidden(timeout=3000)
    expect(home.subscription_email).to_have_value("")
