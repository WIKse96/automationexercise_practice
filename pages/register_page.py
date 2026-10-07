from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class RegisterPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # --- DOM selectors — headings ---
    @property
    def heading_account_info(self) -> Locator:
        return self.page.locator("h2:has-text('Enter Account Information')")

    @property
    def heading_address_info(self) -> Locator:
        return self.page.locator("h2:has-text('Address Information')")

    # --- DOM selectors — pre-filled fields ---
    @property
    def name_field(self) -> Locator:
        return self.page.locator("input[data-qa='name']")

    @property
    def email_field(self) -> Locator:
        return self.page.locator("input[data-qa='email']")

    # --- DOM selectors ---
    @property
    def title_mr(self) -> Locator:
        return self.page.locator("input#id_gender1")

    @property
    def title_mrs(self) -> Locator:
        return self.page.locator("input#id_gender2")

    @property
    def password(self) -> Locator:
        return self.page.locator("input[data-qa='password']")

    @property
    def days_select(self) -> Locator:
        return self.page.locator("select[data-qa='days']")

    @property
    def months_select(self) -> Locator:
        return self.page.locator("select[data-qa='months']")

    @property
    def years_select(self) -> Locator:
        return self.page.locator("select[data-qa='years']")

    @property
    def newsletter_checkbox(self) -> Locator:
        return self.page.locator("input#newsletter")

    @property
    def optin_checkbox(self) -> Locator:
        return self.page.locator("input#optin")

    @property
    def first_name(self) -> Locator:
        return self.page.locator("input[data-qa='first_name']")

    @property
    def last_name(self) -> Locator:
        return self.page.locator("input[data-qa='last_name']")

    @property
    def company(self) -> Locator:
        return self.page.locator("input[data-qa='company']")

    @property
    def address1(self) -> Locator:
        return self.page.locator("input[data-qa='address']")

    @property
    def address2(self) -> Locator:
        return self.page.locator("input[data-qa='address2']")

    @property
    def country_select(self) -> Locator:
        return self.page.locator("select[data-qa='country']")

    @property
    def state(self) -> Locator:
        return self.page.locator("input[data-qa='state']")

    @property
    def city(self) -> Locator:
        return self.page.locator("input[data-qa='city']")

    @property
    def zipcode(self) -> Locator:
        return self.page.locator("input[data-qa='zipcode']")

    @property
    def mobile_number(self) -> Locator:
        return self.page.locator("input[data-qa='mobile_number']")

    @property
    def create_account_button(self) -> Locator:
        return self.page.locator("button[data-qa='create-account']")

    @property
    def account_created_header(self) -> Locator:
        return self.page.locator("h2[data-qa='account-created']")

    # --- Actions ---
    def fill_account_form(self, user: dict) -> None:
        if user.get("title") == "Mrs":
            self.title_mrs.check()
        elif user.get("title") == "Mr":
            self.title_mr.check()
        # brak "title" w danych -> celowo nie zaznaczamy żadnego radio
        # (pole opcjonalne, testy graniczne sprawdzają rejestrację bez title)

        self.password.fill(user["password"])

        if user.get("birth_date"):
            self.days_select.select_option(user["birth_date"])
        if user.get("birth_month"):
            self.months_select.select_option(user["birth_month"])
        if user.get("birth_year"):
            self.years_select.select_option(user["birth_year"])

        if user.get("newsletter"):
            self.newsletter_checkbox.check()
        if user.get("optin"):
            self.optin_checkbox.check()

        self.first_name.fill(user["firstname"])
        self.last_name.fill(user["lastname"])
        if user.get("company"):
            self.company.fill(user["company"])
        self.address1.fill(user["address1"])
        if user.get("address2"):
            self.address2.fill(user["address2"])
        self.country_select.select_option(user["country"])
        self.state.fill(user["state"])
        self.city.fill(user["city"])
        self.zipcode.fill(user["zipcode"])
        self.mobile_number.fill(user["mobile_number"])

    def submit(self) -> None:
        self.create_account_button.click()

    def is_account_created(self) -> bool:
        return self.account_created_header.is_visible()
