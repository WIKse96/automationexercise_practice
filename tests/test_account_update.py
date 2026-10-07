import allure
import pytest
from playwright.sync_api import Page, expect

from api.account_api import AccountApi, REQUEST_TO_RESPONSE_FIELD_MAP
from pages.checkout_page import CheckoutPage
from pages.login_page import LoginPage

# Pola widoczne w adresie dostawy na /checkout (#address_delivery) — dla nich
# dodatkowo weryfikujemy UI, nie tylko API.
CHECKOUT_VISIBLE_FIELDS = {
    "firstname", "lastname", "company", "address1", "address2",
    "city", "state", "zipcode", "country", "mobile_number",
}

NEW_VALUES = {
    "name": "WiktorUpdated",
    "password": "NewPass456!",
    "title": "Mrs",
    "birth_date": "15",
    "birth_month": "8",
    "birth_year": "1995",
    "firstname": "UpdatedFirst",
    "lastname": "UpdatedLast",
    "company": "UpdatedCo",
    "address1": "456 Updated Ave",
    "address2": "Floor 2",
    "country": "Canada",
    "zipcode": "54321",
    "state": "UpdatedState",
    "city": "UpdatedCity",
    "mobile_number": "9998887777",
}

# "password" jest wyjątkiem — patrz known-bug niżej.
FIELD_PARAMS = [
    pytest.param(field, id=field)
    if field != "password"
    else pytest.param(
        field,
        id=field,
        marks=pytest.mark.xfail(
            reason=(
                "KNOWN BUG: PUT /api/updateAccount używa pola 'password' "
                "JEDNOCZEŚNIE jako klucza uwierzytelniającego (email+password "
                "muszą pasować do ISTNIEJĄCEGO konta) i jako nowej wartości do "
                "zapisania. Wysłanie innego hasła niż aktualne powoduje 404 "
                "'Account not found!' — hasła nie da się zmienić tym endpointem."
            ),
            strict=True,
        ),
    )
    for field in NEW_VALUES
]


@allure.feature("Account")
@allure.story("Update")
@allure.severity(allure.severity_level.CRITICAL)
def test_update_title(page: Page, account_api: AccountApi, api_user: dict) -> None:
    allure.dynamic.title("Zmiana title: Mr -> Mrs -> Mr (API + UI checkout)")
    user = api_user

    with allure.step("PUT title=Mrs"):
        payload = dict(user)
        payload["title"] = "Mrs"
        result = account_api.update(payload)
        assert result.get("message") == "User updated!", result

    with allure.step("GET: title == Mrs"):
        got = account_api.get_by_email(user["email"])["user"]
        assert got["title"] == "Mrs"

    with allure.step("UI: zaloguj -> checkout -> adres dostawy zaczyna się od 'Mrs.'"):
        login = LoginPage(page)
        login.open()
        login.login(user["email"], user["password"])
        checkout = CheckoutPage(page)
        checkout.add_first_product_to_cart()
        checkout.go_to_checkout()
        lines = [l.strip() for l in checkout.delivery_address_text().splitlines() if l.strip()]
        assert lines[1].startswith("Mrs."), lines

    with allure.step("PUT title=Mr (powrót) -> GET potwierdza zmianę w obie strony"):
        payload2 = dict(user)
        payload2["title"] = "Mr"
        result2 = account_api.update(payload2)
        assert result2.get("message") == "User updated!", result2
        got2 = account_api.get_by_email(user["email"])["user"]
        assert got2["title"] == "Mr"


@allure.feature("Account")
@allure.story("Update")
@pytest.mark.parametrize("field", FIELD_PARAMS)
def test_update_single_field(
    page: Page, account_api: AccountApi, api_user: dict, field: str
) -> None:
    allure.dynamic.title(f"Edycja pojedynczego pola: {field}")
    user = api_user
    new_value = NEW_VALUES[field]

    if field == "password":
        allure.dynamic.tag("known-bug")
        allure.dynamic.severity(allure.severity_level.NORMAL)
        allure.dynamic.issue(
            "BUG-UPDATE-PASSWORD", "updateAccount nie pozwala zmienić hasła"
        )
        allure.dynamic.description(
            "Pole 'password' w PUT /api/updateAccount jest używane JEDNOCZEŚNIE "
            "jako klucz uwierzytelniający (email+password muszą pasować do "
            "istniejącego konta) i jako nowa wartość do zapisania.\n\n"
            "Oczekiwane: wysłanie nowego hasła w polu 'password' zmienia hasło "
            "konta.\n"
            "Faktyczne: {'responseCode': 404, 'message': 'Account not found!'} — "
            "endpoint szuka konta po parze email+NOWE_hasło (które jeszcze nie "
            "istnieje w bazie), więc nigdy nie znajduje konta i hasła nie da "
            "się zmienić przez ten endpoint."
        )

    with allure.step(f"Snapshot GET przed zmianą pola '{field}'"):
        snapshot = account_api.get_by_email(user["email"])["user"]

    with allure.step(f"PUT z nową wartością pola '{field}'"):
        payload = dict(user)
        payload[field] = new_value
        result = account_api.update(payload)

    if field == "password":
        allure.attach(
            str(result),
            name="updateAccount-response",
            attachment_type=allure.attachment_type.TEXT,
        )
        assert result.get("message") == "User updated!", result  # celowy xfail
        return

    with allure.step("Weryfikacja: message == 'User updated!'"):
        assert result.get("message") == "User updated!", result

    with allure.step("GET po zmianie: zmienione pole == nowa wartość, reszta bez zmian"):
        updated = account_api.get_by_email(user["email"])["user"]
        response_field = REQUEST_TO_RESPONSE_FIELD_MAP.get(field)
        if response_field:
            assert str(updated[response_field]) == str(new_value)
            for req_f, resp_f in REQUEST_TO_RESPONSE_FIELD_MAP.items():
                if req_f == field:
                    continue
                assert updated[resp_f] == snapshot[resp_f], (
                    f"Pole '{req_f}' zmieniło się niespodziewanie: "
                    f"{snapshot[resp_f]!r} -> {updated[resp_f]!r}"
                )

    needs_ui = field == "name" or field in CHECKOUT_VISIBLE_FIELDS
    if needs_ui:
        with allure.step("Zaloguj się przez UI"):
            login = LoginPage(page)
            login.open()
            login.login(user["email"], user["password"])

    if field == "name":
        with allure.step(f"UI: widoczne 'Logged in as {new_value}'"):
            expect(page.locator(f"text=Logged in as {new_value}")).to_be_visible()

    if field in CHECKOUT_VISIBLE_FIELDS:
        with allure.step(f"UI checkout: pole '{field}' widoczne w adresie dostawy"):
            checkout = CheckoutPage(page)
            checkout.add_first_product_to_cart()
            checkout.go_to_checkout()
            assert str(new_value) in checkout.delivery_address_text()
