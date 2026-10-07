from typing import Callable

import allure
import pytest
from playwright.sync_api import Page, expect

from api.account_api import AccountApi, REQUEST_TO_RESPONSE_FIELD_MAP
from pages.checkout_page import CheckoutPage
from pages.login_page import LoginPage
from pages.register_page import RegisterPage

# ============================================================================
# GRUPA A — wartości graniczne POPRAWNE. Każda zweryfikowana na żywo przed
# napisaniem testu: rejestracja przechodzi i dane zapisują się dokładnie
# tak, jak wpisano (API nie ma żadnych ograniczeń długości/formatu — brak
# atrybutów maxlength/pattern na polach tekstowych, potwierdzone w DOM).
# ============================================================================
GROUP_A_CASES = [
    ("name_1char", {"name": "A"}),
    ("name_50char", {"name": "A" * 50}),
    ("name_polish_chars", {"name": "Wiktor Żółćęś"}),
    ("name_hyphen_apostrophe", {"name": "Anna-Maria O'Neil"}),
    ("password_1char", {"password": "x"}),
    ("password_100char", {"password": "P" * 100}),
    ("password_special_chars", {"password": "!@#$%^&*()_+-=[]{}|;:,.<>?"}),
    ("first_name_1char", {"firstname": "A"}),
    ("first_name_100char", {"firstname": "A" * 100}),
    ("last_name_1char", {"lastname": "A"}),
    ("last_name_100char", {"lastname": "A" * 100}),
    ("city_1char", {"city": "A"}),
    ("city_100char", {"city": "A" * 100}),
    ("state_1char", {"state": "A"}),
    ("state_100char", {"state": "A" * 100}),
    ("address1_255char", {"address1": "A" * 255}),
    ("address2_255char", {"address2": "A" * 255}),
    ("company_255char", {"company": "A" * 255}),
    ("mobile_plus_country_code", {"mobile_number": "+48123456789"}),
    ("mobile_digits_only", {"mobile_number": "123456789"}),
    ("zipcode_dash_format", {"zipcode": "00-001"}),
    ("zipcode_plain_digits", {"zipcode": "12345"}),
    ("zipcode_uk_format", {"zipcode": "SW1A 1AA"}),
    ("dob_oldest_1900", {"birth_date": "1", "birth_month": "1", "birth_year": "1900"}),
    ("dob_youngest_2021", {"birth_date": "31", "birth_month": "12", "birth_year": "2021"}),
    ("dob_leap_year_2020", {"birth_date": "29", "birth_month": "2", "birth_year": "2020"}),
    ("title_mrs", {"title": "Mrs"}),
    ("no_optional_fields", {"birth_date": "", "birth_month": "", "birth_year": "", "title": None}),
]


@allure.feature("Signup")
@allure.story("Boundary — poprawne wartości graniczne (grupa A)")
@pytest.mark.parametrize("case_id, overrides", GROUP_A_CASES, ids=[c[0] for c in GROUP_A_CASES])
def test_signup_boundary_valid(
    page: Page,
    account_api: AccountApi,
    user_data: Callable[..., dict],
    ui_user_cleanup: list,
    case_id: str,
    overrides: dict,
) -> None:
    user = user_data(**overrides)
    allure.dynamic.title(f"Graniczna wartość poprawna: {case_id}")
    ui_user_cleanup.append({"email": user["email"], "password": user["password"]})

    login = LoginPage(page)
    register = RegisterPage(page)
    with allure.step("Rejestracja przez UI"):
        login.goto("")
        login.nav_login.click()
        login.start_registration(user["name"], user["email"])
        register.fill_account_form(user)
        register.submit()
        expect(page).to_have_url("https://automationexercise.com/account_created")
        register.click_continue()

    if "password" in overrides:
        with allure.step("Weryfikacja hasła przez verifyLogin (password nie jest w GET)"):
            result = account_api.verify_login(user["email"], user["password"])
            assert result.get("responseCode") == 200, result
        return

    with allure.step("Weryfikacja zapisanych danych przez API GET"):
        result = account_api.get_by_email(user["email"])
        assert result.get("responseCode") == 200, result
        api_user = result["user"]
        for req_field, value in overrides.items():
            response_field = REQUEST_TO_RESPONSE_FIELD_MAP.get(req_field)
            if response_field is None:
                continue  # np. mobile_number — weryfikowane w UI poniżej
            expected = "" if value is None else value
            assert str(api_user[response_field]) == str(expected), (
                f"{req_field}: oczekiwano {expected!r}, API zwróciło {api_user[response_field]!r}"
            )

    if "mobile_number" in overrides:
        with allure.step("Weryfikacja mobile_number w adresie dostawy na checkout"):
            checkout = CheckoutPage(page)
            checkout.add_first_product_to_cart()
            checkout.go_to_checkout()
            assert overrides["mobile_number"] in checkout.delivery_address_text()


# ============================================================================
# GRUPA B — wartości NIEPOPRAWNE.
# Zweryfikowane na żywo: formularz ma TYLKO natywną walidację HTML5
# `required` (brak pustego pola). Brak jakiegokolwiek ograniczenia
# maxlength/pattern — stąd prawie wszystkie "niepoprawne" dane są w
# rzeczywistości AKCEPTOWANE przez stronę = potwierdzony bug, oznaczony
# strict xfail z pełnym opisem w Allure (tak jak bug Zipcode w
# test_signup_labels.py).
# ============================================================================

# Pola, które da się realnie wyczyścić przez UI (email jest disabled,
# country to <select> bez pustej opcji — zawsze ma wybraną wartość domyślną,
# więc obu nie da się sprawdzić jako "puste" przez normalną interakcję usera).
REQUIRED_TEXT_FIELD_IDS = [
    "name", "password", "first_name", "last_name",
    "address1", "state", "city", "zipcode", "mobile_number",
]


@allure.feature("Signup")
@allure.story("Boundary — niepoprawne wartości odrzucone (grupa B)")
@pytest.mark.parametrize("field_id", REQUIRED_TEXT_FIELD_IDS, ids=REQUIRED_TEXT_FIELD_IDS)
def test_signup_boundary_required_field_empty(
    page: Page, user_data: Callable[..., dict], field_id: str
) -> None:
    allure.dynamic.title(f"Puste wymagane pole '{field_id}' blokuje wysłanie formularza")
    user = user_data()

    login = LoginPage(page)
    register = RegisterPage(page)
    login.goto("")
    login.nav_login.click()
    login.start_registration(user["name"], user["email"])
    register.fill_account_form(user)
    page.locator(f"#{field_id}").fill("")

    with allure.step(f"Próba wysłania formularza z pustym polem '{field_id}'"):
        register.submit()
        expect(page).to_have_url("https://automationexercise.com/signup")
        validation_message = page.locator(f"#{field_id}").evaluate("el => el.validationMessage")
        assert validation_message != "", "Oczekiwano natywnego komunikatu walidacji HTML5"


def _known_bug_whitespace(field_id: str) -> pytest.MarkDecorator:
    return pytest.mark.xfail(
        reason=(
            f"KNOWN BUG: wymagane pole '{field_id}' wypełnione samymi spacjami "
            "przechodzi natywną walidację HTML5 required (spacje liczą się jako "
            "'niepuste') i serwer NIE przycina/odrzuca takiej wartości — konto "
            "rejestruje się z polem zawierającym same spacje."
        ),
        strict=True,
    )


@allure.feature("Signup")
@allure.story("Boundary — niepoprawne wartości odrzucone (grupa B)")
@pytest.mark.parametrize(
    "field_id",
    [pytest.param(f, id=f, marks=_known_bug_whitespace(f)) for f in REQUIRED_TEXT_FIELD_IDS],
)
def test_signup_boundary_required_field_whitespace_only(
    page: Page,
    account_api: AccountApi,
    user_data: Callable[..., dict],
    ui_user_cleanup: list,
    field_id: str,
) -> None:
    allure.dynamic.tag("known-bug")
    allure.dynamic.severity(allure.severity_level.MINOR)
    allure.dynamic.issue(
        "BUG-WHITESPACE-REQUIRED", f"Pole '{field_id}' akceptuje same spacje"
    )
    allure.dynamic.title(f"Wymagane pole '{field_id}' wypełnione samymi spacjami")
    allure.dynamic.description(
        f"Oczekiwane: formularz odrzuca pole '{field_id}' zawierające tylko spacje "
        "(dane bez realnej treści).\n"
        "Faktyczne: konto rejestruje się poprawnie, pole zapisane jako '   '."
    )

    user = user_data()
    ui_user_cleanup.append({"email": user["email"], "password": user["password"]})

    login = LoginPage(page)
    register = RegisterPage(page)
    login.goto("")
    login.nav_login.click()
    login.start_registration(user["name"], user["email"])
    register.fill_account_form(user)
    page.locator(f"#{field_id}").fill("   ")

    allure.attach(
        page.locator(f"#{field_id}").evaluate("el => el.outerHTML"),
        name=f"field-{field_id}-outerHTML",
        attachment_type=allure.attachment_type.HTML,
    )
    register.submit()
    allure.attach(
        page.screenshot(full_page=True),
        name="after-submit-screenshot",
        attachment_type=allure.attachment_type.PNG,
    )
    # Celowy xfail: oczekujemy, że formularz NIE przejdzie (zostaniemy na /signup).
    expect(page).not_to_have_url("https://automationexercise.com/account_created")


_INVALID_FORMAT_BUG_CASES = [
    (
        "mobile_letters",
        {"mobile_number": "abcdef"},
        "mobile_number",
        "pole mobile_number akceptuje litery zamiast cyfr",
    ),
    (
        "mobile_too_short",
        {"mobile_number": "12"},
        "mobile_number",
        "pole mobile_number akceptuje 2-cyfrowy numer",
    ),
    (
        "zipcode_symbols",
        {"zipcode": "abc!@#"},
        "zipcode",
        "pole zipcode akceptuje dowolne znaki specjalne",
    ),
    (
        "name_1000_chars",
        {"name": "A" * 1000},
        "name",
        "pole name akceptuje 1000 znaków bez ograniczenia",
    ),
]


@allure.feature("Signup")
@allure.story("Boundary — niepoprawne wartości odrzucone (grupa B)")
@pytest.mark.parametrize(
    "case_id, overrides, field_id, bug_desc",
    [
        pytest.param(
            cid, ov, fid, desc, id=cid,
            marks=pytest.mark.xfail(
                reason=f"KNOWN BUG: {desc} — brak walidacji formatu/długości na serwerze.",
                strict=True,
            ),
        )
        for cid, ov, fid, desc in _INVALID_FORMAT_BUG_CASES
    ],
)
def test_signup_boundary_invalid_format(
    page: Page,
    account_api: AccountApi,
    user_data: Callable[..., dict],
    ui_user_cleanup: list,
    case_id: str,
    overrides: dict,
    field_id: str,
    bug_desc: str,
) -> None:
    allure.dynamic.tag("known-bug")
    allure.dynamic.severity(allure.severity_level.MINOR)
    allure.dynamic.issue(f"BUG-{case_id.upper()}", bug_desc)
    allure.dynamic.title(f"Niepoprawny format: {case_id}")
    allure.dynamic.description(
        f"Oczekiwane: formularz odrzuca niepoprawną wartość pola '{field_id}'.\n"
        f"Faktyczne: {bug_desc} — rejestracja przechodzi, wartość zapisana 1:1."
    )

    user = user_data(**overrides)
    ui_user_cleanup.append({"email": user["email"], "password": user["password"]})

    login = LoginPage(page)
    register = RegisterPage(page)
    login.goto("")
    login.nav_login.click()
    login.start_registration(user["name"], user["email"])
    register.fill_account_form(user)

    allure.attach(
        page.locator(f"#{field_id}").evaluate("el => el.outerHTML"),
        name=f"field-{field_id}-outerHTML",
        attachment_type=allure.attachment_type.HTML,
    )
    register.submit()
    allure.attach(
        page.screenshot(full_page=True),
        name="after-submit-screenshot",
        attachment_type=allure.attachment_type.PNG,
    )
    expect(page).not_to_have_url("https://automationexercise.com/account_created")


_INVALID_DATE_BUG_CASES = [
    (
        "dob_31_february",
        {"birth_date": "31", "birth_month": "2", "birth_year": "2021"},
        "31 lutego nie istnieje w żadnym roku",
    ),
    (
        "dob_29_february_nonleap",
        {"birth_date": "29", "birth_month": "2", "birth_year": "2021"},
        "2021 nie jest rokiem przestępnym — 29 lutego nie istnieje",
    ),
    (
        "dob_31_april",
        {"birth_date": "31", "birth_month": "4", "birth_year": "2000"},
        "kwiecień ma 30 dni — 31 kwietnia nie istnieje",
    ),
    (
        "dob_incomplete_day_only",
        {"birth_date": "15", "birth_month": "", "birth_year": ""},
        "wybrano tylko dzień, bez miesiąca i roku",
    ),
]


@allure.feature("Signup")
@allure.story("Boundary — niepoprawne wartości odrzucone (grupa B)")
@pytest.mark.parametrize(
    "case_id, overrides, bug_desc",
    [
        pytest.param(
            cid, ov, desc, id=cid,
            marks=pytest.mark.xfail(
                reason=(
                    f"KNOWN BUG: data urodzenia nieprawidłowa kalendarzowo ({desc}) "
                    "jest akceptowana — selecty dni/miesięcy/lat są niezależne "
                    "(dzień zawsze 1-31 niezależnie od miesiąca), serwer nie "
                    "waliduje spójności kalendarzowej."
                ),
                strict=True,
            ),
        )
        for cid, ov, desc in _INVALID_DATE_BUG_CASES
    ],
)
def test_signup_boundary_invalid_date(
    page: Page,
    account_api: AccountApi,
    user_data: Callable[..., dict],
    ui_user_cleanup: list,
    case_id: str,
    overrides: dict,
    bug_desc: str,
) -> None:
    allure.dynamic.tag("known-bug")
    allure.dynamic.severity(allure.severity_level.MINOR)
    allure.dynamic.issue(f"BUG-{case_id.upper()}", f"Niepoprawna data akceptowana: {bug_desc}")
    allure.dynamic.title(f"Niepoprawna data urodzenia: {case_id}")
    allure.dynamic.description(
        f"Oczekiwane: formularz odrzuca niepoprawną kalendarzowo datę ({bug_desc}).\n"
        "Faktyczne: rejestracja przechodzi, data zapisana dokładnie tak, jak wybrana "
        "w selectach (dzień/miesiąc/rok są od siebie niezależne)."
    )

    user = user_data(**overrides)
    ui_user_cleanup.append({"email": user["email"], "password": user["password"]})

    login = LoginPage(page)
    register = RegisterPage(page)
    login.goto("")
    login.nav_login.click()
    login.start_registration(user["name"], user["email"])
    register.fill_account_form(user)
    register.submit()
    allure.attach(
        page.screenshot(full_page=True),
        name="after-submit-screenshot",
        attachment_type=allure.attachment_type.PNG,
    )
    expect(page).not_to_have_url("https://automationexercise.com/account_created")


# ============================================================================
# GRUPA C — bezpieczeństwo. Oba przypadki zweryfikowane na żywo jako
# BEZPIECZNE (strona poprawnie escapuje HTML przy renderowaniu) — to są
# zwykłe PASS, nie xfail.
# ============================================================================

@allure.feature("Signup")
@allure.story("Boundary — bezpieczeństwo (grupa C)")
@allure.severity(allure.severity_level.CRITICAL)
def test_signup_xss_name_is_escaped_not_executed(
    page: Page,
    account_api: AccountApi,
    user_data: Callable[..., dict],
    ui_user_cleanup: list,
) -> None:
    allure.dynamic.title("name='<script>alert(1)</script>' — renderowane jako tekst, bez wykonania")
    payload = "<script>alert(1)</script>"
    user = user_data(name=payload)
    ui_user_cleanup.append({"email": user["email"], "password": user["password"]})

    dialogs: list[str] = []
    page.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))

    login = LoginPage(page)
    register = RegisterPage(page)
    with allure.step("Rejestracja z payloadem XSS w polu name"):
        login.goto("")
        login.nav_login.click()
        login.start_registration(user["name"], user["email"])
        register.fill_account_form(user)
        register.submit()
        expect(page).to_have_url("https://automationexercise.com/account_created")
        register.click_continue()

    with allure.step("Weryfikacja: tekst wyświetlony dosłownie, żaden dialog się nie otworzył"):
        logged_in = page.locator("text=Logged in as")
        expect(logged_in).to_be_visible()
        assert dialogs == [], f"Wykonał się dialog — XSS zadziałał: {dialogs}"
        script_elements = page.locator(f"script:has-text('alert(1)')")
        assert script_elements.count() == 0, "Znaleziono wykonywalny <script> w DOM"


@allure.feature("Signup")
@allure.story("Boundary — bezpieczeństwo (grupa C)")
def test_signup_sqli_like_name_saved_literally(
    page: Page,
    account_api: AccountApi,
    user_data: Callable[..., dict],
    ui_user_cleanup: list,
) -> None:
    allure.dynamic.title("name=\"' OR '1'='1\" — rejestracja normalna, wartość 1:1")
    payload = "' OR '1'='1"
    user = user_data(name=payload)
    ui_user_cleanup.append({"email": user["email"], "password": user["password"]})

    login = LoginPage(page)
    register = RegisterPage(page)
    with allure.step("Rejestracja z payloadem SQLi-podobnym w polu name"):
        login.goto("")
        login.nav_login.click()
        login.start_registration(user["name"], user["email"])
        register.fill_account_form(user)
        register.submit()
        expect(page).to_have_url("https://automationexercise.com/account_created")

    with allure.step("Weryfikacja: wartość zapisana dosłownie przez API"):
        result = account_api.get_by_email(user["email"])
        assert result.get("responseCode") == 200, result
        assert result["user"]["name"] == payload
