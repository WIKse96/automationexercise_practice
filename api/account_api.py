import json
from typing import Any

from playwright.sync_api import APIRequestContext

# Mapowanie: klucz w payloadzie create/updateAccount -> klucz w odpowiedzi
# GET getUserDetailByEmail (zweryfikowane na żywo wobec API):
#   - "password" nie jest zwracane wcale — weryfikacja przez verify_login().
#   - "mobile_number" też nie jest zwracane przez GET, ALE jest widoczne w
#     adresie dostawy na /checkout (#address_delivery) — tam weryfikować w UI.
REQUEST_TO_RESPONSE_FIELD_MAP = {
    "name": "name",
    "email": "email",
    "title": "title",
    "birth_date": "birth_day",
    "birth_month": "birth_month",
    "birth_year": "birth_year",
    "firstname": "first_name",
    "lastname": "last_name",
    "company": "company",
    "address1": "address1",
    "address2": "address2",
    "country": "country",
    "zipcode": "zipcode",
    "state": "state",
    "city": "city",
}
FIELDS_NOT_IN_GET_RESPONSE = {"password", "mobile_number"}


class AccountApi:
    """
    Klient /api/* na automationexercise.com.

    API zawsze odpowiada HTTP 200 (content-type text/html) — prawdziwy status
    operacji jest zapakowany w JSON w polu "responseCode" treści odpowiedzi,
    np. {"responseCode": 201, "message": "User created!"}. Wyjątek: zupełnie
    zła metoda HTTP (np. GET na /createAccount) daje realny HTTP 405.
    """

    def __init__(self, request_context: APIRequestContext) -> None:
        self._request = request_context

    @staticmethod
    def _parse(response) -> dict[str, Any]:
        return json.loads(response.text())

    def create(self, user: dict) -> dict:
        response = self._request.post("/api/createAccount", form=user)
        return self._parse(response)

    def update(self, user: dict) -> dict:
        response = self._request.put("/api/updateAccount", form=user)
        return self._parse(response)

    def delete(self, email: str, password: str) -> dict:
        response = self._request.delete(
            "/api/deleteAccount", form={"email": email, "password": password}
        )
        return self._parse(response)

    def get_by_email(self, email: str) -> dict:
        response = self._request.get(
            "/api/getUserDetailByEmail", params={"email": email}
        )
        return self._parse(response)

    def verify_login(self, email: str, password: str) -> dict:
        response = self._request.post(
            "/api/verifyLogin", form={"email": email, "password": password}
        )
        return self._parse(response)
