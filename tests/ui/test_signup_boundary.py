import allure
import pytest
from playwright.sync_api import Page, expect

from api.account_api import AccountApi, REQUEST_TO_RESPONSE_FIELD_MAP
from pages.checkout_page import CheckoutPage
from pages.login_page import LoginPage
from pages.register_page import RegisterPage


@allure.epic("Automation Exercise")
@allure.feature("Rejestracja użytkownika")
@allure.story("Walidacja — puste wymagane pole")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Pusty formularz /signup blokuje wysłanie (natywna walidacja HTML5)")
@allure.description(
    "Sprawdza, że próba wysłania formularza Account Information bez wypełnienia "
    "żadnego pola nie przechodzi — przeglądarka blokuje submit przez natywną "
    "walidację HTML5 (atrybut required). Weryfikacja przez pseudo-klasę CSS "
    "':invalid' na polu password (pierwsze realnie puste wymagane pole — "
    "name/email są już wypełnione z kroku startu rejestracji), nie przez tekst "
    "komunikatu walidacji, bo ten zależy od języka przeglądarki."
)
def test_signup_empty_form_shows_validation_errors(
    page: Page,
    user_data,
    base_url: str,
) -> None:
    user = user_data()
    login = LoginPage(page)
    register = RegisterPage(page)

    with allure.step("Rozpocznij rejestrację — dotrzyj do /signup"):
        login.goto("")
        login.nav_login.click()
        login.start_registration(user["name"], user["email"])

    with allure.step("Wyślij pusty formularz Account Information"):
        register.submit()

    with allure.step("Zweryfikuj, że submit nie przeszedł i pole jest :invalid"):
        expect(page).to_have_url(f"{base_url}signup")
        is_invalid = register.password.evaluate("el => el.matches(':invalid')")
        assert is_invalid is True


@allure.epic("Automation Exercise")
@allure.feature("Rejestracja użytkownika")
@allure.story("Walidacja — puste wymagane pole")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Wypełnienie TYLKO pól opcjonalnych nie przechodzi — błąd nadal na password")
@allure.description(
    "Pola opcjonalne (title, data urodzenia, newsletter, optin, company, "
    "address2) wypełnione poprawnymi wartościami nie mogą zastąpić pól "
    "wymaganych. Formularz nadal blokuje submit na pierwszym pustym "
    "wymaganym polu (password)."
)
def test_signup_only_optional_fields_filled_still_blocks_on_required(
    page: Page, user_data, base_url: str
) -> None:
    user = user_data(newsletter=True, optin=True)
    login = LoginPage(page)
    register = RegisterPage(page)

    with allure.step("Dotrzyj do /signup"):
        login.goto("")
        login.nav_login.click()
        login.start_registration(user["name"], user["email"])

    with allure.step("Wypełnij TYLKO pola opcjonalne, zostaw wymagane puste"):
        register.title_mrs.check()
        register.days_select.select_option(user["birth_date"])
        register.months_select.select_option(user["birth_month"])
        register.years_select.select_option(user["birth_year"])
        register.newsletter_checkbox.check()
        register.optin_checkbox.check()
        register.company.fill(user["company"])
        register.address2.fill(user["address2"])
        register.submit()

    with allure.step("Formularz nie przechodzi — password nadal :invalid"):
        expect(page).to_have_url(f"{base_url}signup")
        assert register.password.evaluate("el => el.matches(':invalid')") is True


SHORT_VALUES = ["a", "aa", "2", "22", "a22", "a2@", " "]

# DOM id (property w RegisterPage) -> required pola na /signup, które realnie
# da się przetestować (email jest disabled, country/title/dob nie są text inputami).
REQUIRED_FIELD_PROPERTIES = {
    "name": "name_field",
    "password": "password",
    "first_name": "first_name",
    "last_name": "last_name",
    "address1": "address1",
    "state": "state",
    "city": "city",
    "zipcode": "zipcode",
    "mobile_number": "mobile_number",
}


@allure.epic("Automation Exercise")
@allure.feature("Rejestracja użytkownika")
@allure.story("Walidacja — wymagane pola")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize(
    "field_id", list(REQUIRED_FIELD_PROPERTIES), ids=list(REQUIRED_FIELD_PROPERTIES)
)
@pytest.mark.parametrize("value", SHORT_VALUES, ids=[repr(v) for v in SHORT_VALUES])
def test_signup_required_field_any_short_value_satisfies_required(
    page: Page, user_data, base_url: str, field_id: str, value: str
) -> None:
    allure.dynamic.title(f"{field_id}={value!r} wystarcza by przejść required")
    user = user_data()
    login = LoginPage(page)
    register = RegisterPage(page)

    with allure.step("Dotrzyj do /signup"):
        login.goto("")
        login.nav_login.click()
        login.start_registration(user["name"], user["email"])

    with allure.step(f"Wypełnij {field_id}={value!r}"):
        field = getattr(register, REQUIRED_FIELD_PROPERTIES[field_id])
        field.fill(value)

    with allure.step(f"{field_id} przestaje być :invalid"):
        assert field.evaluate("el => el.matches(':invalid')") is False


# Jak wyżej + pola opcjonalne (company, address2) — tu testujemy nie "required",
# tylko brak limitu długości, więc opcjonalność pola nie ma znaczenia.
ALL_TEXT_FIELD_TO_REQUEST_KEY = {
    "name": "name",
    "password": "password",
    "first_name": "firstname",
    "last_name": "lastname",
    "company": "company",
    "address1": "address1",
    "address2": "address2",
    "state": "state",
    "city": "city",
    "zipcode": "zipcode",
    "mobile_number": "mobile_number",
}


@allure.epic("Automation Exercise")
@allure.feature("Rejestracja użytkownika")
@allure.story("Walidacja — wymagane pola")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize(
    "field_id", list(ALL_TEXT_FIELD_TO_REQUEST_KEY), ids=list(ALL_TEXT_FIELD_TO_REQUEST_KEY)
)
@pytest.mark.parametrize("length", [255, 256], ids=["255_znakow", "256_znakow"])
def test_signup_field_long_value_accepted(
    page: Page,
    account_api: AccountApi,
    user_data,
    ui_user_cleanup: list,
    base_url: str,
    field_id: str,
    length: int,
) -> None:
    request_key = ALL_TEXT_FIELD_TO_REQUEST_KEY[field_id]
    value = "a" * length
    allure.dynamic.title(f"{field_id} o długości {length} znaków — zapisuje się poprawnie")

    user = user_data(**{request_key: value})
    ui_user_cleanup.append({"email": user["email"], "password": user["password"]})

    login = LoginPage(page)
    register = RegisterPage(page)
    with allure.step(f"Pełna rejestracja z {field_id}={length} znaków"):
        login.goto("")
        login.nav_login.click()
        login.start_registration(user["name"], user["email"])
        register.fill_account_form(user)
        register.submit()
        expect(page).to_have_url(f"{base_url}account_created")
        register.click_continue()

    if request_key == "password":
        with allure.step("Weryfikacja hasła przez verifyLogin (password nie jest w GET)"):
            result = account_api.verify_login(user["email"], value)
            assert result.get("responseCode") == 200, result
        return

    if request_key == "mobile_number":
        with allure.step("Weryfikacja mobile_number w adresie dostawy na checkout"):
            checkout = CheckoutPage(page)
            checkout.add_first_product_to_cart()
            checkout.go_to_checkout()
            assert value in checkout.delivery_address_text()
        return

    with allure.step("Weryfikacja zapisanej wartości przez API GET"):
        result = account_api.get_by_email(user["email"])
        assert result.get("responseCode") == 200, result
        response_field = REQUEST_TO_RESPONSE_FIELD_MAP[request_key]
        assert result["user"][response_field] == value
