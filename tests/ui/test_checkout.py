import re
from pathlib import Path
from typing import Callable

import allure
import pytest
from playwright.sync_api import Page, expect

from api.account_api import AccountApi
from pages.checkout_modal_page import CheckoutModalPage
from pages.checkout_page import CheckoutPage
from pages.login_page import LoginPage
from pages.payment_done_page import PaymentDonePage
from pages.payment_page import PaymentPage
from pages.register_page import RegisterPage

TEST_CARD = {
    "name_on_card": "Wiktor Tester",
    "card_number": "4242424242424242",
    "cvc": "123",
    "expiry_month": "12",
    "expiry_year": "2030",
}


@allure.feature("Checkout")
@allure.story("Guest checkout")
def test_guest_checkout_requires_login(page: Page, base_url: str) -> None:
    allure.dynamic.title("Niezalogowany użytkownik dostaje modal logowania przy Proceed To Checkout")

    checkout = CheckoutPage(page)
    modal = CheckoutModalPage(page)

    with allure.step("Jako gość dodaj produkt do koszyka"):
        checkout.add_first_product_to_cart()

    with allure.step("Kliknij Proceed To Checkout"):
        checkout.go_to_checkout()

    with allure.step("Zweryfikuj modal 'Checkout' z prośbą o zalogowanie"):
        expect(modal.modal).to_be_visible()
        expect(modal.title).to_have_text("Checkout")
        expect(modal.modal).to_contain_text("Register / Login account to proceed on checkout.")

    with allure.step("Zweryfikuj, że link Register / Login działa"):
        expect(modal.login_link).to_have_attribute("href", "/login")
        modal.click_login()
        expect(page).to_have_url(f"{base_url}login")


@allure.feature("Checkout")
@allure.story("Guest checkout")
def test_guest_checkout_modal_continue_on_cart_stays_on_cart(page: Page, base_url: str) -> None:
    allure.dynamic.title("Continue On Cart zamyka modal i zostawia na stronie koszyka")

    checkout = CheckoutPage(page)
    modal = CheckoutModalPage(page)

    with allure.step("Jako gość dodaj produkt do koszyka i kliknij Proceed To Checkout"):
        checkout.add_first_product_to_cart()
        checkout.go_to_checkout()
        expect(modal.modal).to_be_visible()

    with allure.step("Kliknij Continue On Cart"):
        modal.continue_on_cart()

    with allure.step("Zweryfikuj, że modal zniknął i nadal jesteśmy na /view_cart"):
        expect(modal.modal).to_be_hidden()
        expect(page).to_have_url(f"{base_url}view_cart")


@allure.feature("Checkout")
@allure.story("Zarejestrowany użytkownik")
def test_registered_user_checkout_shows_matching_address(
    page: Page,
    account_api: AccountApi,
    user_data: Callable[..., dict],
    ui_user_cleanup: list,
    base_url: str,
) -> None:
    allure.dynamic.title("Adres dostawy i rozliczeniowy na checkout zgadza się z danymi rejestracji")

    user = user_data()
    ui_user_cleanup.append({"email": user["email"], "password": user["password"]})

    login = LoginPage(page)
    register = RegisterPage(page)
    checkout = CheckoutPage(page)

    with allure.step("Zarejestruj nowego użytkownika przez UI"):
        login.goto("")
        login.go_to_login()
        login.start_registration(user["name"], user["email"])
        register.fill_account_form(user)
        register.submit()
        expect(page).to_have_url(f"{base_url}account_created")
        register.click_continue()
        expect(page).to_have_url(base_url)

    with allure.step("Dodaj produkt do koszyka i przejdź do checkout"):
        checkout.add_first_product_to_cart()
        checkout.go_to_checkout()
        expect(page).to_have_url(f"{base_url}checkout")

    with allure.step("Zweryfikuj adres dostawy"):
        delivery_text = checkout.delivery_address_text()
        for expected in [
            user["firstname"],
            user["lastname"],
            user["company"],
            user["address1"],
            user["address2"],
            user["city"],
            user["state"],
            user["zipcode"],
            user["country"],
            user["mobile_number"],
        ]:
            assert expected in delivery_text, f"'{expected}' nie znalezione w adresie dostawy"

    with allure.step("Zweryfikuj adres rozliczeniowy (ta sama zawartość)"):
        billing_text = checkout.billing_address_text()
        for expected in [
            user["firstname"],
            user["lastname"],
            user["address1"],
            user["country"],
        ]:
            assert expected in billing_text, f"'{expected}' nie znalezione w adresie rozliczeniowym"


@allure.feature("Checkout")
@allure.story("Zarejestrowany użytkownik")
def test_order_comment_is_optional_for_placing_order(
    page: Page,
    account_api: AccountApi,
    user_data: Callable[..., dict],
    ui_user_cleanup: list,
    base_url: str,
) -> None:
    allure.dynamic.title("Puste pole komentarza do zamówienia nie blokuje Place Order")

    user = user_data()
    ui_user_cleanup.append({"email": user["email"], "password": user["password"]})

    login = LoginPage(page)
    register = RegisterPage(page)
    checkout = CheckoutPage(page)

    with allure.step("Zarejestruj użytkownika i przejdź do checkout"):
        login.goto("")
        login.go_to_login()
        login.start_registration(user["name"], user["email"])
        register.fill_account_form(user)
        register.submit()
        register.click_continue()
        checkout.add_first_product_to_cart()
        checkout.go_to_checkout()

    with allure.step("NIE wypełniaj komentarza i kliknij Place Order"):
        expect(checkout.order_comment_textarea).to_have_value("")
        checkout.place_order()

    with allure.step("Zweryfikuj, że mimo pustego komentarza przechodzimy do /payment"):
        expect(page).to_have_url(f"{base_url}payment")


@allure.feature("Checkout")
@allure.story("Płatność")
def test_full_order_placement_and_invoice_download(
    page: Page,
    account_api: AccountApi,
    user_data: Callable[..., dict],
    ui_user_cleanup: list,
    base_url: str,
    tmp_path: Path,
) -> None:
    allure.dynamic.title("Pełna ścieżka: rejestracja -> zamówienie -> pobranie faktury")

    user = user_data()
    ui_user_cleanup.append({"email": user["email"], "password": user["password"]})

    login = LoginPage(page)
    register = RegisterPage(page)
    checkout = CheckoutPage(page)
    payment = PaymentPage(page)
    done = PaymentDonePage(page)

    with allure.step("Zarejestruj użytkownika przez UI"):
        login.goto("")
        login.go_to_login()
        login.start_registration(user["name"], user["email"])
        register.fill_account_form(user)
        register.submit()
        register.click_continue()

    with allure.step("Dodaj produkt do koszyka i zapamiętaj sumę zamówienia"):
        checkout.add_first_product_to_cart()
        cart_total_text = page.locator(".cart_total_price").inner_text()
        expected_amount = re.sub(r"[^\d]", "", cart_total_text)

    with allure.step("Przejdź do checkout i kliknij Place Order"):
        checkout.go_to_checkout()
        checkout.place_order()
        expect(page).to_have_url(f"{base_url}payment")

    with allure.step("Wypełnij dane karty testowej i zapłać"):
        payment.fill_card_details(**TEST_CARD)
        # #success_message na formularzu płatności nigdy nie staje się widoczny —
        # to realny POST z przekierowaniem serwera, nie AJAX, więc stary DOM
        # znika razem z nawigacją. Pomijamy tę asercję świadomie.
        payment.pay()

    with allure.step("Zweryfikuj przekierowanie na /payment_done/<kwota>"):
        expect(page).to_have_url(re.compile(re.escape(f"{base_url}payment_done/") + r"\d+"))
        assert expected_amount in page.url

    with allure.step("Zweryfikuj elementy strony potwierdzenia zamówienia"):
        expect(done.order_placed_heading).to_have_text("Order Placed!")
        expect(done.confirmation_text).to_be_visible()
        expect(done.download_invoice_link).to_be_visible()
        expect(done.continue_button).to_be_visible()
        expect(done.download_invoice_link).to_have_attribute(
            "href", re.compile(r"/download_invoice/\d+")
        )

    with allure.step("Pobierz fakturę i zweryfikuj jej zawartość"):
        with page.expect_download() as download_info:
            done.download_invoice_link.click()
        download = download_info.value

        assert download.suggested_filename == "invoice.txt"
        assert download.failure() is None

        saved_path = tmp_path / "invoice.txt"
        download.save_as(saved_path)
        content = saved_path.read_text()

        assert content.strip() != ""
        assert f"{user['firstname']} {user['lastname']}" in content
        assert expected_amount in content

    with allure.step("Kliknij Continue i zweryfikuj powrót na stronę główną, dalej zalogowany"):
        done.click_continue()
        expect(page).to_have_url(base_url)
        expect(page.locator("a:has-text('Logged in as')")).to_be_visible()
