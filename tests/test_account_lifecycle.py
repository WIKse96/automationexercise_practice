from typing import Callable

import allure
import pytest
from playwright.sync_api import Page, expect

from api.account_api import AccountApi, REQUEST_TO_RESPONSE_FIELD_MAP
from pages.login_page import LoginPage
from pages.register_page import RegisterPage


@allure.feature("Account")
@allure.story("Lifecycle")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_and_delete_user_ui(
    page: Page,
    account_api: AccountApi,
    user_data: Callable[..., dict],
    ui_user_cleanup: list,
) -> None:
    user = user_data(newsletter=True, optin=True)
    allure.dynamic.title(f"Pełny cykl życia konta UI: {user['email']}")

    # Rejestrujemy e-mail do sprzątania PRZED akcjami — gdyby test padł przed
    # krokiem usuwania, konto i tak zostanie skasowane w teardownie.
    ui_user_cleanup.append({"email": user["email"], "password": user["password"]})

    login = LoginPage(page)
    register = RegisterPage(page)

    with allure.step("Rejestracja przez UI z kompletem danych"):
        login.goto("")
        login.nav_login.click()
        login.start_registration(user["name"], user["email"])
        register.fill_account_form(user)
        register.submit()

    with allure.step("Weryfikacja strony /account_created"):
        expect(page).to_have_url("https://automationexercise.com/account_created")
        # DOM ma "Account Created!" — "ACCOUNT CREATED!" to tylko CSS text-transform,
        # to_have_text() porównuje surowy textContent, nie tekst po renderowaniu.
        expect(register.account_created_header).to_have_text("Account Created!")
        register.click_continue()

    with allure.step("Weryfikacja zalogowania jako wiktor"):
        expect(page.locator("text=Logged in as wiktor")).to_be_visible()

    with allure.step("Weryfikacja danych konta przez API (GET po e-mailu)"):
        result = account_api.get_by_email(user["email"])
        assert result["responseCode"] == 200, result
        api_user = result["user"]
        for request_field, response_field in REQUEST_TO_RESPONSE_FIELD_MAP.items():
            if request_field == "email":
                continue
            assert str(api_user[response_field]) == str(user[request_field]), (
                f"Pole '{request_field}': API zwróciło {api_user[response_field]!r}, "
                f"oczekiwano {user[request_field]!r}"
            )

    with allure.step("Usunięcie konta przez UI"):
        page.goto("https://automationexercise.com/delete_account")
        expect(page.locator("h2:has-text('ACCOUNT DELETED!')")).to_be_visible()
        register.click_continue()

    with allure.step("Weryfikacja przez API, że konto nie istnieje"):
        result_after = account_api.get_by_email(user["email"])
        assert result_after["responseCode"] == 404, result_after

    with allure.step("Próba logowania usuniętymi danymi -> komunikat błędu"):
        login.open()
        login.login(user["email"], user["password"])
        expect(login.login_error).to_be_visible()
        expect(login.login_error).to_have_text("Your email or password is incorrect!")
