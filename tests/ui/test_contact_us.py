import allure
import pytest
from playwright.sync_api import Page, expect

from pages.contact_us_page import ContactUsPage

DUMMY_PDF = "data/dummy.pdf"
SUCCESS_TEXT = "Success! Your details have been submitted successfully."

ALL_FIELDS = {
    "name": "Jan Testowy",
    "email": "jan@example.com",
    "subject": "Zapytanie testowe",
    "message": "Treść wiadomości testowej",
}


@allure.feature("Contact Us")
@allure.story("Submit form")
def test_contact_us_submit_with_file_shows_success_and_home_button(
    page: Page, base_url: str
) -> None:
    allure.dynamic.title("Wysłanie formularza z plikiem pokazuje komunikat sukcesu i przycisk Home")

    contact = ContactUsPage(page)

    with allure.step("Otwórz Contact Us, wypełnij formularz i załącz dummy.pdf"):
        contact.open()
        contact.fill_form(**ALL_FIELDS)
        contact.upload_file(DUMMY_PDF)

    with allure.step("Wyślij formularz"):
        contact.submit()

    with allure.step("Zweryfikuj komunikat sukcesu"):
        expect(contact.success_message).to_be_visible()
        expect(contact.success_message).to_have_text(SUCCESS_TEXT)

    with allure.step("Zweryfikuj przycisk Home (ikona + tekst)"):
        expect(contact.home_button).to_be_visible()
        expect(contact.home_button.locator("i.fa-angle-double-left")).to_be_visible()
        expect(contact.home_button).to_contain_text("Home")

    with allure.step("Kliknij Home i zweryfikuj przekierowanie na stronę główną"):
        contact.home_button.click()
        expect(page).to_have_url(base_url)


@allure.feature("Contact Us")
@allure.story("Walidacja pól")
def test_contact_us_empty_form_is_blocked(page: Page) -> None:
    allure.dynamic.title("Pusty formularz nie wysyła się")

    contact = ContactUsPage(page)

    with allure.step("Otwórz Contact Us i spróbuj wysłać bez wypełniania czegokolwiek"):
        contact.open()
        contact.submit()
        page.wait_for_timeout(1000)

    with allure.step("Zweryfikuj brak komunikatu sukcesu"):
        expect(contact.success_message).to_be_hidden()


@allure.feature("Contact Us")
@allure.story("Walidacja pól")
def test_contact_us_only_file_without_other_fields_is_blocked(page: Page) -> None:
    allure.dynamic.title("Sam załączony plik bez reszty pól nie wysyła formularza")

    contact = ContactUsPage(page)

    with allure.step("Otwórz Contact Us i załącz tylko plik"):
        contact.open()
        contact.upload_file(DUMMY_PDF)
        contact.submit()
        page.wait_for_timeout(1000)

    with allure.step("Zweryfikuj brak komunikatu sukcesu"):
        expect(contact.success_message).to_be_hidden()


@allure.feature("Contact Us")
@allure.story("Walidacja pól")
def test_contact_us_only_email_is_enough_to_submit(page: Page) -> None:
    allure.dynamic.title("Sam email (bez reszty pól) wystarcza do wysłania formularza")

    contact = ContactUsPage(page)

    with allure.step("Otwórz Contact Us i wypełnij tylko email"):
        contact.open()
        contact.email_input.fill(ALL_FIELDS["email"])
        contact.submit()

    with allure.step("Zweryfikuj komunikat sukcesu"):
        expect(contact.success_message).to_be_visible()


REQUIRED_FIELD_CASES = [
    pytest.param("email", id="missing_email"),
    pytest.param(
        "name",
        id="missing_name",
        marks=pytest.mark.xfail(
            reason="KNOWN BUG: pole Name nie jest wymagane mimo że powinno być — "
            "formularz wysyła się mimo braku imienia",
            strict=True,
        ),
    ),
    pytest.param(
        "subject",
        id="missing_subject",
        marks=pytest.mark.xfail(
            reason="KNOWN BUG: pole Subject nie jest wymagane mimo że powinno być — "
            "formularz wysyła się mimo braku tematu",
            strict=True,
        ),
    ),
    pytest.param(
        "message",
        id="missing_message",
        marks=pytest.mark.xfail(
            reason="KNOWN BUG: pole Message nie jest wymagane mimo że powinno być — "
            "formularz wysyła się mimo braku wiadomości",
            strict=True,
        ),
    ),
]


@allure.feature("Contact Us")
@allure.story("Walidacja pól")
@pytest.mark.parametrize("missing_field", REQUIRED_FIELD_CASES)
def test_contact_us_field_is_required(page: Page, missing_field: str) -> None:
    allure.dynamic.title(f"Pole '{missing_field}' powinno być wymagane do wysłania formularza")

    contact = ContactUsPage(page)
    # Kopiujemy wszystkie pola, potem usuwamy to jedno, które akurat testujemy —
    # zostaje puste, reszta ma wartości.
    fields = dict(ALL_FIELDS)
    del fields[missing_field]

    with allure.step(f"Wypełnij wszystko oprócz '{missing_field}' i spróbuj wysłać"):
        contact.open()
        if "name" in fields:
            contact.name_input.fill(fields["name"])
        if "email" in fields:
            contact.email_input.fill(fields["email"])
        if "subject" in fields:
            contact.subject_input.fill(fields["subject"])
        if "message" in fields:
            contact.message_input.fill(fields["message"])
        contact.submit()
        page.wait_for_timeout(1000)

    with allure.step(f"Zweryfikuj, że brak pola '{missing_field}' blokuje wysyłkę"):
        expect(contact.success_message).to_be_hidden()
