from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class RegisterPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

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
    def fill_account_info(self, password: str, day: str, month: str, year: str) -> None:
        self.title_mr.check()
        self.password.fill(password)
        self.days_select.select_option(day)
        self.months_select.select_option(month)
        self.years_select.select_option(year)

    def fill_address_info(
        self,
        first_name: str,
        last_name: str,
        address: str,
        country: str,
        state: str,
        city: str,
        zipcode: str,
        mobile: str,
    ) -> None:
        self.first_name.fill(first_name)
        self.last_name.fill(last_name)
        self.address1.fill(address)
        self.country_select.select_option(country)
        self.state.fill(state)
        self.city.fill(city)
        self.zipcode.fill(zipcode)
        self.mobile_number.fill(mobile)

    def submit(self) -> None:
        self.create_account_button.click()

    def is_account_created(self) -> bool:
        return self.account_created_header.is_visible()
