import re


def parse_price(price_text: str) -> int:
    return int(re.sub(r"[^\d]", "", price_text))
