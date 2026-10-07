import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Callable

import allure
import pytest
from dotenv import load_dotenv

from api.account_api import AccountApi

load_dotenv()

_CONSENT_STATE = Path("tests/fixtures/consent_state.json")


# --- pytest-playwright config ---

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, pytestconfig):
    args = {**browser_type_launch_args, "slow_mo": int(os.getenv("SLOW_MO", "0"))}
    # Flaga --headed ma pierwszeństwo przed HEADLESS z .env — inaczej .env
    # zawsze wymuszał headless=True i --headed nic nie zmieniał.
    if not pytestconfig.getoption("--headed"):
        args["headless"] = os.getenv("HEADLESS", "true").lower() == "true"
    return args


@pytest.fixture(scope="session")
def _fc_consent(playwright):
    """Jednorazowo generuje plik ze stanem zgody FC cookie (działa w CI bez pliku)."""
    if _CONSENT_STATE.exists():
        return
    _CONSENT_STATE.parent.mkdir(parents=True, exist_ok=True)
    browser = playwright.chromium.launch(headless=True)
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto("https://automationexercise.com")
    try:
        page.locator(".fc-cta-consent").click(timeout=8000)
        page.wait_for_timeout(500)
    except Exception:
        pass
    ctx.storage_state(path=str(_CONSENT_STATE))
    browser.close()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, _fc_consent):
    args = {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "locale": "en-US",
    }
    if _CONSENT_STATE.exists():
        args["storage_state"] = str(_CONSENT_STATE)
    return args


# --- App fixtures ---

@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("BASE_URL", "https://automationexercise.com")


@pytest.fixture(scope="session")
def api_base_url() -> str:
    return os.getenv("API_BASE_URL", "https://automationexercise.com/api")


@pytest.fixture(scope="session")
def test_user() -> dict:
    """Dane istniejącego, już zarejestrowanego użytkownika (np. testy logowania)."""
    return {
        "name": os.getenv("TEST_USER_NAME", "Test User"),
        "email": os.getenv("TEST_USER_EMAIL", "testuser@example.com"),
        "password": os.getenv("TEST_USER_PASSWORD", "TestPass123!"),
    }


@pytest.fixture()
def register_user_name() -> str:
    """Imię używane w testach rejestracji nowego konta."""
    return os.getenv("REGISTER_USER_NAME", "wiktor")


@pytest.fixture()
def email_factory() -> Callable[[], str]:
    """
    Fabryka unikalnych adresów e-mail do testów rejestracji.

    Każde wywołanie zwraca nowy adres <base>+<timestamp>@<domain>, dzięki
    czemu test rejestracji można uruchamiać wielokrotnie bez błędu
    "Email Address already exist!".
    """
    base = os.getenv("REGISTER_EMAIL_BASE", "testwik5")
    domain = os.getenv("REGISTER_EMAIL_DOMAIN", "gmail.com")

    def _make() -> str:
        return f"{base}+{int(time.time() * 1000)}@{domain}"

    return _make


# --- API client ---

@pytest.fixture(scope="session")
def api_request_context(playwright, base_url):
    context = playwright.request.new_context(base_url=base_url)
    yield context
    context.dispose()


@pytest.fixture()
def account_api(api_request_context) -> AccountApi:
    return AccountApi(api_request_context)


# --- Dane testowe rejestracji/API ---

@pytest.fixture()
def unique_email() -> str:
    """Unikalny e-mail bezpieczny dla uruchomień równoległych (pytest-xdist)."""
    base = os.getenv("REGISTER_EMAIL_BASE", "testwik")
    domain = os.getenv("REGISTER_EMAIL_DOMAIN", "gmail.com")
    return f"{base}+{int(time.time())}{uuid.uuid4().hex[:6]}@{domain}"


@pytest.fixture()
def user_data(unique_email: str) -> Callable[..., dict]:
    """Fabryka kompletnych, poprawnych danych użytkownika. `overrides` nadpisuje
    pojedyncze pola (np. country=..., title=...) bez przepisywania reszty."""

    def _make(**overrides) -> dict:
        base = {
            "name": "wiktor",
            "email": unique_email,
            "password": "TestPass123!",
            "title": "Mr",
            "birth_date": "10",
            "birth_month": "5",
            "birth_year": "1990",
            "firstname": "Wiktor",
            "lastname": "Tester",
            "company": "TestCo",
            "address1": "123 Test Street",
            "address2": "Suite 1",
            "country": "India",
            "zipcode": "12345",
            "state": "TestState",
            "city": "TestCity",
            "mobile_number": "1234567890",
        }
        base.update(overrides)
        return base

    return _make


@pytest.fixture()
def ui_user_cleanup(account_api: AccountApi):
    """Rejestr e-maili/haseł kont założonych przez UI w teście — każdy wpis
    zostaje usunięty przez API po teście, niezależnie od jego wyniku."""
    pending: list[dict] = []
    yield pending
    for cred in pending:
        try:
            account_api.delete(cred["email"], cred["password"])
        except Exception:
            pass


# --- Allure: godzina testu + zrzut ekranu przy niepowodzeniu ---

@pytest.fixture(autouse=True)
def _allure_test_timing():
    started_at = datetime.now()
    allure.dynamic.label("start_time", started_at.strftime("%Y-%m-%d %H:%M:%S"))
    allure.attach(
        f"Start: {started_at.strftime('%Y-%m-%d %H:%M:%S')}",
        name="Godzina rozpoczęcia testu",
        attachment_type=allure.attachment_type.TEXT,
    )
    yield
    finished_at = datetime.now()
    allure.attach(
        f"Koniec: {finished_at.strftime('%Y-%m-%d %H:%M:%S')} "
        f"(czas trwania: {finished_at - started_at})",
        name="Godzina zakończenia testu",
        attachment_type=allure.attachment_type.TEXT,
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page is not None:
            allure.attach(
                page.screenshot(full_page=True),
                name="screenshot-on-failure",
                attachment_type=allure.attachment_type.PNG,
            )
