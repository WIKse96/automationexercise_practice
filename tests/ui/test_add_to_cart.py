import re

import allure
import pytest
from playwright.sync_api import Page, expect

from pages.add_to_cart_modal_page import AddToCartModalPage
from pages.cart_page import CartPage
from pages.product_card_page import ProductCardPage
from pages.product_listing_page import ProductListingPage

PRODUCT_ID = 39


def _parse_price(price_text: str) -> int:
    return int(re.sub(r"[^\d]", "", price_text))


@allure.feature("Product card")
@allure.story("Add to cart")
def test_add_to_cart_from_product_card_shows_modal(page: Page) -> None:
    allure.dynamic.title("Dodanie produktu z karty produktu pokazuje modal 'Added!'")

    product_card = ProductCardPage(page)
    modal = AddToCartModalPage(page)

    with allure.step(f"Otwórz kartę produktu {PRODUCT_ID}"):
        product_card.open(PRODUCT_ID)

    with allure.step("Kliknij Add to cart"):
        product_card.add_to_cart_button.click()

    with allure.step("Zweryfikuj, że modal 'Added!' się pojawił"):
        expect(modal.modal).to_be_visible()
        expect(modal.title).to_have_text("Added!")
        expect(modal.body_text).to_contain_text("Your product has been added to cart")


@allure.feature("Product card")
@allure.story("Add to cart")
@pytest.mark.parametrize("quantity", [2, 99, 999])
def test_view_cart_link_in_modal_shows_added_product(
    page: Page, base_url: str, quantity: int
) -> None:
    allure.dynamic.title(
        f"Klik 'View Cart' w modalu przenosi do koszyka z dodanym produktem (qty={quantity})"
    )

    product_card = ProductCardPage(page)
    modal = AddToCartModalPage(page)
    cart = CartPage(page)

    with allure.step(f"Otwórz kartę produktu {PRODUCT_ID}, ustaw ilość {quantity} i dodaj do koszyka"):
        product_card.open(PRODUCT_ID)
        product_name = product_card.product_name.inner_text()
        unit_price = _parse_price(product_card.product_price.inner_text())
        product_card.quantity_input.fill(str(quantity))
        product_card.add_to_cart_button.click()
        expect(modal.modal).to_be_visible()

    with allure.step("Kliknij View Cart"):
        modal.click_view_cart()

    with allure.step("Zweryfikuj, że jesteśmy na stronie koszyka"):
        expect(page).to_have_url(f"{base_url}view_cart")

    with allure.step("Zweryfikuj, że dodany produkt jest widoczny w koszyku"):
        expect(cart.cart_rows).to_have_count(1)
        # normalizacja whitespace — nazwa w h2 bywa z \xa0, w koszyku ze spacją
        assert " ".join(cart.get_product_name(0).split()) == " ".join(product_name.split())

    with allure.step("Zweryfikuj ilość i poprawnie wyliczoną sumę za produkt"):
        assert cart.get_product_quantity(0) == str(quantity)
        assert _parse_price(cart.get_product_total(0)) == unit_price * quantity


@allure.feature("Product card")
@allure.story("Add to cart")
def test_continue_shopping_button_does_not_redirect(page: Page, base_url: str) -> None:
    allure.dynamic.title("Continue Shopping nie przekierowuje poza kartę produktu")

    product_card = ProductCardPage(page)
    modal = AddToCartModalPage(page)
    product_url = f"{base_url}product_details/{PRODUCT_ID}"

    with allure.step(f"Otwórz kartę produktu {PRODUCT_ID} i dodaj do koszyka"):
        product_card.open(PRODUCT_ID)
        product_card.add_to_cart_button.click()
        expect(modal.modal).to_be_visible()

    with allure.step("Kliknij Continue Shopping"):
        modal.continue_shopping()

    with allure.step("Poczekaj 1s i zweryfikuj brak przekierowania"):
        page.wait_for_timeout(1_000)
        expect(page).to_have_url(product_url)


@allure.feature("Product listing")
@allure.story("Add to cart")
@pytest.mark.parametrize(
    "path",
    ["", "brand_products/Polo", "category_products/6"],
    ids=["home", "brand_products", "category_products"],
)
def test_add_to_cart_from_listing_shows_modal(page: Page, path: str) -> None:
    allure.dynamic.title(f"Add to cart z listingu (hover) pokazuje modal 'Added!' [{path or 'home'}]")

    listing = ProductListingPage(page)
    modal = AddToCartModalPage(page)

    with allure.step(f"Otwórz /{path} i dodaj pierwszy produkt przez hover + overlay"):
        listing.open(path)
        listing.add_first_product_to_cart()

    with allure.step("Zweryfikuj, że modal 'Added!' się pojawił"):
        expect(modal.modal).to_be_visible()
        expect(modal.title).to_have_text("Added!")
        expect(modal.body_text).to_contain_text("Your product has been added to cart")
