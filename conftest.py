import os
import pytest
from dotenv import load_dotenv

load_dotenv()


# --- pytest-playwright config ---

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "headless": os.getenv("HEADLESS", "true").lower() == "true",
        "slow_mo": int(os.getenv("SLOW_MO", "0")),
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "locale": "en-US",
    }


# --- App fixtures ---

@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("BASE_URL", "https://automationexercise.com")


@pytest.fixture(scope="session")
def api_base_url() -> str:
    return os.getenv("API_BASE_URL", "https://automationexercise.com/api")


@pytest.fixture(scope="session")
def test_user() -> dict:
    return {
        "name": os.getenv("TEST_USER_NAME", "Test User"),
        "email": os.getenv("TEST_USER_EMAIL", "testuser@example.com"),
        "password": os.getenv("TEST_USER_PASSWORD", "TestPass123!"),
    }
