import requests
from api.base_api import BaseApi


class UsersApi(BaseApi):
    CREATE_ENDPOINT = "createAccount"
    VERIFY_LOGIN_ENDPOINT = "verifyLogin"
    DELETE_ENDPOINT = "deleteAccount"
    UPDATE_ENDPOINT = "updateAccount"
    GET_USER_ENDPOINT = "getUserDetailByEmail"

    def create_account(self, payload: dict) -> requests.Response:
        return self.post(self.CREATE_ENDPOINT, data=payload)

    def verify_login(self, email: str, password: str) -> requests.Response:
        return self.post(self.VERIFY_LOGIN_ENDPOINT, data={"email": email, "password": password})

    def verify_login_without_password(self, email: str) -> requests.Response:
        return self.post(self.VERIFY_LOGIN_ENDPOINT, data={"email": email})

    def delete_account(self, email: str, password: str) -> requests.Response:
        return self.delete(self.DELETE_ENDPOINT, data={"email": email, "password": password})

    def update_account(self, payload: dict) -> requests.Response:
        return self.put(self.UPDATE_ENDPOINT, data=payload)

    def get_user_by_email(self, email: str) -> requests.Response:
        return self.get(self.GET_USER_ENDPOINT, params={"email": email})
