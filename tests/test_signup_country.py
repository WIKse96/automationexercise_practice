from typing import Callable

import allure
import pytest
from playwright.sync_api import Page, expect

from api.account_api import AccountApi
from pages.checkout_page import CheckoutPage
from pages.signup_page import SignupPage

COUNTRIES = [
    "India", "United States", "Canada", "Australia",
    "Israel", "New Zealand", "Singapore",
]


@allure.feature("Signup")
@allure.story("Country")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize("country", COUNTRIES, ids=COUNTRIES)
def test_signup_country_selection(
    page: Page,
    account_api: AccountApi,
    user_data: Callable[..., dict],
    ui_user_cleanup: list,
    country: str,
) -> None:
    user = user_data(country=country)
    allure.dynamic.title(f"Rejestracja z krajem: {country}")
    ui_user_cleanup.append({"email": user["email"], "password": user["password"]})

    signup = SignupPage(page)
    country_select = page.locator("select[data-qa='country']")

    with allure.step(f"Rejestracja przez UI z krajem {country}"):
        signup.open_from_home()
        signup.start_signup(user["name"], user["email"])
        signup.fill_account_form(user)
        expect(country_select).to_have_value(country)
        signup.submit()
        expect(page).to_have_url("https://automationexercise.com/account_created")
        signup.click_continue()

    with allure.step("Weryfikacja kraju przez API"):
        result = account_api.get_by_email(user["email"])
        assert result["responseCode"] == 200, result
        assert result["user"]["country"] == country

    with allure.step("Weryfikacja kraju w adresie dostawy na checkout"):
        checkout = CheckoutPage(page)
        checkout.add_first_product_to_cart()
        checkout.go_to_checkout()
        assert country in checkout.delivery_address_text()


@allure.feature("Signup")
@allure.story("Country")
def test_signup_country_default_and_options(
    page: Page, user_data: Callable[..., dict]
) -> None:
    allure.dynamic.title("Domyślny kraj = India, lista zawiera dokładnie 7 opcji w kolejności")
    user = user_data()

    with allure.step("Otwórz formularz /signup"):
        signup = SignupPage(page)
        signup.open_from_home()
        signup.start_signup(user["name"], user["email"])

    with allure.step("Zweryfikuj domyślną wartość i pełną listę opcji"):
        country_select = page.locator("select[data-qa='country']")
        expect(country_select).to_have_value("India")

        options = country_select.locator("option").all_inner_texts()
        assert options == COUNTRIES, f"Kolejność/zawartość opcji: {options}"
