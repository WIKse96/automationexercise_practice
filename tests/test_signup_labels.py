import re
import time

import allure
import pytest
from playwright.sync_api import Page, expect


def _label_regex(label_text: str) -> "re.Pattern[str]":
    """Dopasowuje pełny tekst etykiety (z opcjonalną gwiazdką na końcu), żeby np.
    'Name' nie łapało 'First name', a 'Address 2' nie łapało 'Address'."""
    return re.compile(rf"^\s*{re.escape(label_text)}\s*\*?\s*$")


# Etykieta Address ma gwiazdkę PRZED dymkiem pomocniczym, nie na końcu —
# nie pasuje do ogólnego szablonu, więc ma własny, w pełni jawny regex.
_ADDRESS1_LABEL_REGEX = re.compile(
    r"^\s*Address\s*\*\s*\(Street address, P\.O\. Box, Company name, etc\.\)\s*$"
)

FIELDS = [
    pytest.param("id_gender1", "Mr.", "radio", id="id_gender1"),
    pytest.param("id_gender2", "Mrs.", "radio", id="id_gender2"),
    pytest.param("name", "Name", "text", id="name"),
    pytest.param("email", "Email", "disabled", id="email"),
    pytest.param("password", "Password", "text", id="password"),
    pytest.param("newsletter", "Sign up for our newsletter!", "checkbox", id="newsletter"),
    pytest.param(
        "optin", "Receive special offers from our partners!", "checkbox", id="optin"
    ),
    pytest.param("first_name", "First name", "text", id="first_name"),
    pytest.param("last_name", "Last name", "text", id="last_name"),
    pytest.param("company", "Company", "text", id="company"),
    pytest.param("address1", "Address", "text", id="address1"),
    pytest.param("address2", "Address 2", "text", id="address2"),
    pytest.param("country", "Country", "select", id="country"),
    pytest.param("state", "State", "text", id="state"),
    pytest.param("city", "City", "text", id="city"),
    pytest.param(
        "zipcode",
        "Zipcode",
        "text",
        id="zipcode",
        marks=pytest.mark.xfail(
            reason="KNOWN BUG: label 'Zipcode *' has for='city' instead of for='zipcode'",
            strict=True,
        ),
    ),
    pytest.param("mobile_number", "Mobile Number", "text", id="mobile_number"),
]


@pytest.fixture(scope="function")
def signup_page(page: Page) -> Page:
    page.goto("https://automationexercise.com/")

    try:
        page.locator(".fc-cta-do-not-consent").click(timeout=4000)
    except Exception:
        pass  # baner nie pojawił się lub nie ma opcji odrzucenia — kontynuujemy

    page.locator("xpath=//a[normalize-space()='Signup / Login']").click()
    expect(page).to_have_url("https://automationexercise.com/login")

    email = f"testwik+{int(time.time() * 1000)}@gmail.com"
    page.locator('[data-qa="signup-name"]').fill("wiktor")
    page.locator('[data-qa="signup-email"]').fill(email)
    page.locator('[data-qa="signup-button"]').click()

    expect(page).to_have_url("https://automationexercise.com/signup")

    return page


@allure.feature("Signup")
@allure.story("Label binding")
@pytest.mark.parametrize("field_id, label_text, field_type", FIELDS)
def test_signup_label_binding(
    signup_page: Page, field_id: str, label_text: str, field_type: str
) -> None:
    allure.dynamic.title(f"Label '{label_text}' wskazuje na pole #{field_id}")

    page = signup_page
    pattern = _ADDRESS1_LABEL_REGEX if field_id == "address1" else _label_regex(label_text)
    label = page.locator("label").filter(has_text=pattern)

    if field_id == "zipcode":
        allure.dynamic.tag("known-bug")
        allure.dynamic.severity(allure.severity_level.MINOR)
        allure.dynamic.issue(
            "BUG-ZIPCODE-LABEL", "Label Zipcode wskazuje na pole City"
        )
        allure.dynamic.description(
            "Etykieta 'Zipcode *' w HTML ma atrybut for=\"city\" zamiast for=\"zipcode\".\n\n"
            "Oczekiwane: for=\"zipcode\"\n"
            "Faktyczne: for=\"city\"\n\n"
            "Skutek: kliknięcie etykiety 'Zipcode *' ustawia focus w polu City zamiast "
            "Zipcode. page.get_by_label('Zipcode') zwraca pole City — to błąd dostępności "
            "(a11y), mylący dla użytkowników czytników ekranu i testów opartych o etykiety."
        )
        allure.attach(
            label.evaluate("el => el.outerHTML"),
            name="label-zipcode-outerHTML",
            attachment_type=allure.attachment_type.HTML,
        )
        # Klikamy i łapiemy zrzut PRZED asercją — ta i tak zaraz zawiedzie (celowy
        # xfail), więc inaczej załącznik pokazujący skutek buga nigdy by nie powstał.
        label.click()
        allure.attach(
            page.screenshot(),
            name="after-click-zipcode-label-cursor-in-city",
            attachment_type=allure.attachment_type.PNG,
        )
        expect(label).to_have_attribute("for", field_id)
        return

    # a) etykieta wskazuje właściwe pole
    expect(label).to_have_attribute("for", field_id)

    if field_type == "disabled":
        return

    # b) kliknięcie etykiety działa na właściwe pole
    label.click()
    field = page.locator(f"#{field_id}")
    if field_type in ("checkbox", "radio"):
        expect(field).to_be_checked()
    else:
        expect(field).to_be_focused()
