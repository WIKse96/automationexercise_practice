from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from pages.login_page import LoginPage
from pages.register_page import RegisterPage


class SignupPage(BasePage):
    """Orkiestruje pełny przepływ rejestracji: strona główna -> /login (start)
    -> /signup (Account + Address Information). Deleguje selektory do
    LoginPage/RegisterPage zamiast ich duplikować."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._login = LoginPage(page)
        self._register = RegisterPage(page)

    def open_from_home(self) -> None:
        self.goto("")
        self.nav_login.click()

    def start_signup(self, name: str, email: str) -> None:
        self._login.start_registration(name, email)

    def fill_account_form(self, user: dict) -> None:
        r = self._register

        if user.get("title") == "Mrs":
            r.title_mrs.check()
        elif user.get("title") == "Mr":
            r.title_mr.check()
        # brak "title" w danych -> celowo nie zaznaczamy żadnego radio
        # (pole opcjonalne, testy graniczne sprawdzają rejestrację bez title)

        r.password.fill(user["password"])

        if user.get("birth_date"):
            r.days_select.select_option(user["birth_date"])
        if user.get("birth_month"):
            r.months_select.select_option(user["birth_month"])
        if user.get("birth_year"):
            r.years_select.select_option(user["birth_year"])

        if user.get("newsletter"):
            r.newsletter_checkbox.check()
        if user.get("optin"):
            r.optin_checkbox.check()

        r.first_name.fill(user["firstname"])
        r.last_name.fill(user["lastname"])
        if user.get("company"):
            r.company.fill(user["company"])
        r.address1.fill(user["address1"])
        if user.get("address2"):
            r.address2.fill(user["address2"])
        r.country_select.select_option(user["country"])
        r.state.fill(user["state"])
        r.city.fill(user["city"])
        r.zipcode.fill(user["zipcode"])
        r.mobile_number.fill(user["mobile_number"])

    def submit(self) -> None:
        self._register.submit()

    @property
    def account_created_header(self) -> Locator:
        return self._register.account_created_header
