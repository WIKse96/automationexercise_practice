from typing import Callable

import allure
import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.register_page import RegisterPage


@allure.epic("Automation Exercise")
@allure.feature("Rejestracja użytkownika")
@allure.story("E2E – start rejestracji")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Pełna ścieżka rejestracji nowego użytkownika")
@allure.description(
    "Sprawdza, że strona /login wyświetla poprawnie formularze logowania i rejestracji "
    "(URL, nagłówki, 6 pól), że wypełnienie formularza startowego (imię + e-mail) i kliknięcie "
    "Signup przenosi na /signup, oraz że formularz Account Information i Address Information "
    "zawiera wszystkie wymagane pola, wartości przeniesione z poprzedniego kroku (imię, "
    "zablokowany e-mail) i pełną listę krajów w selekcie."
)
def test_register_e2e(
    page: Page, register_user_name: str, email_factory: Callable[[], str]
) -> None:
    email = email_factory()
    login = LoginPage(page)

    with allure.step("Otwórz stronę główną i przejdź do Signup / Login"):
        login.goto("")
        login.go_to_login()
        expect(page).to_have_url("https://automationexercise.com/login")

    with allure.step("Zweryfikuj elementy formularzy na /login"):
        expect(login.heading_login).to_be_visible()
        expect(login.heading_signup).to_be_visible()

        for locator in [
            login.login_email,
            login.login_password,
            login.login_button,
            login.register_name,
            login.register_email,
            login.register_button,
        ]:
            expect(locator).to_be_visible()

        expect(login.login_button).to_have_text("Login")
        expect(login.register_button).to_have_text("Signup")

    with allure.step("Wypełnij formularz startowy rejestracji (imię + e-mail) i wyślij"):
        login.start_registration(register_user_name, email)
        expect(page).to_have_url("https://automationexercise.com/signup")

    register = RegisterPage(page)

    with allure.step("Zweryfikuj nagłówki i pola Account Information / Address Information"):
        expect(register.heading_account_info).to_be_visible()
        expect(register.heading_address_info).to_be_visible()

        expect(register.title_mr).to_be_visible()
        expect(register.title_mrs).to_be_visible()

        expect(register.name_field).to_have_value(register_user_name)
        expect(register.email_field).to_have_value(email)
        expect(register.email_field).to_be_disabled()

        expect(register.password).to_be_visible()

        for locator in [register.days_select, register.months_select, register.years_select]:
            expect(locator).to_be_visible()

        expect(register.newsletter_checkbox).to_be_visible()
        expect(register.optin_checkbox).to_be_visible()

        for locator in [
            register.first_name,
            register.last_name,
            register.company,
            register.address1,
            register.address2,
            register.state,
            register.city,
            register.zipcode,
            register.mobile_number,
        ]:
            expect(locator).to_be_visible()

    with allure.step("Zweryfikuj listę dostępnych krajów w selekcie"):
        expected_countries = [
            "India", "United States", "Canada", "Australia",
            "Israel", "New Zealand", "Singapore",
        ]
        for country in expected_countries:
            expect(register.country_select.locator(f"option:has-text('{country}')")).to_be_attached()

    with allure.step("Zweryfikuj przycisk Create Account"):
        expect(register.create_account_button).to_be_visible()
        expect(register.create_account_button).to_have_text("Create Account")
