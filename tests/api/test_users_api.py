import pytest
import uuid
from api.users_api import UsersApi


@pytest.fixture(scope="module")
def users_api(api_base_url: str) -> UsersApi:
    return UsersApi(api_base_url)


@pytest.fixture
def unique_user() -> dict:
    uid = uuid.uuid4().hex[:8]
    return {
        "name": f"Test User {uid}",
        "email": f"testuser_{uid}@test.com",
        "password": "TestPass123!",
        "title": "Mr",
        "birth_date": "1",
        "birth_month": "January",
        "birth_year": "1990",
        "firstname": "Test",
        "lastname": "User",
        "company": "TestCo",
        "address1": "123 Test St",
        "address2": "",
        "country": "United States",
        "zipcode": "12345",
        "state": "NY",
        "city": "New York",
        "mobile_number": "5551234567",
    }


@pytest.mark.api
class TestUsersApi:
    @pytest.mark.smoke
    def test_create_account_returns_201(self, users_api: UsersApi, unique_user: dict) -> None:
        data = users_api.create_account(unique_user).json()
        assert data["responseCode"] == 201

    def test_verify_login_valid_credentials(self, users_api: UsersApi, unique_user: dict) -> None:
        users_api.create_account(unique_user)
        data = users_api.verify_login(unique_user["email"], unique_user["password"]).json()
        assert data["responseCode"] == 200

    def test_verify_login_invalid_credentials(self, users_api: UsersApi) -> None:
        data = users_api.verify_login("nobody@nowhere.com", "wrongpass").json()
        assert data["responseCode"] == 404

    def test_verify_login_without_password_returns_400(self, users_api: UsersApi) -> None:
        data = users_api.verify_login_without_password("test@test.com").json()
        assert data["responseCode"] == 400

    def test_get_user_by_email(self, users_api: UsersApi, unique_user: dict) -> None:
        users_api.create_account(unique_user)
        data = users_api.get_user_by_email(unique_user["email"]).json()
        assert data["responseCode"] == 200
        assert "user" in data

    def test_delete_account(self, users_api: UsersApi, unique_user: dict) -> None:
        users_api.create_account(unique_user)
        data = users_api.delete_account(unique_user["email"], unique_user["password"]).json()
        assert data["responseCode"] == 200

    def test_update_account(self, users_api: UsersApi, unique_user: dict) -> None:
        users_api.create_account(unique_user)
        updated = {**unique_user, "name": "Updated Name"}
        data = users_api.update_account(updated).json()
        assert data["responseCode"] == 200
