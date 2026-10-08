import pytest

from utils.price import parse_price


@pytest.mark.parametrize(
    "price_text, expected",
    [
        ("Rs. 3000", 3000),
        ("Rs. 0", 0),
        ("Rs. 2997000", 2997000),
        ("500", 500),
        ("Rs.999", 999),
    ],
)
def test_parse_price(price_text: str, expected: int) -> None:
    assert parse_price(price_text) == expected


def test_parse_price_ignores_decimal_separator():
    # regex wycina wszystkie znaki niebędące cyframi — kropka/przecinek też,
    # więc "1,250.50" zlewa się w jedną liczbę całkowitą. Udokumentowane
    # zachowanie, nie zaokrąglanie — cena na automationexercise.com zawsze
    # jest całkowita, więc w praktyce się nie zdarza.
    assert parse_price("Rs. 1,250.50") == 125050
