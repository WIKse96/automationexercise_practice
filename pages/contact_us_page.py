from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class ContactUsPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # --- DOM selectors — nagłówki / kontener ---
    @property
    def page_heading(self) -> Locator:
        return self.page.get_by_role("heading", name="Contact Us")

    @property
    def form_heading(self) -> Locator:
        return self.page.get_by_role("heading", name="Get In Touch")

    @property
    def form(self) -> Locator:
        return self.page.locator("#contact-us-form")

    # --- DOM selectors — pola formularza ---
    @property
    def name_input(self) -> Locator:
        return self.page.locator("[data-qa='name']")

    @property
    def email_input(self) -> Locator:
        return self.page.locator("[data-qa='email']")

    @property
    def subject_input(self) -> Locator:
        return self.page.locator("[data-qa='subject']")

    @property
    def message_input(self) -> Locator:
        return self.page.locator("[data-qa='message']")

    @property
    def file_input(self) -> Locator:
        return self.page.locator("input[name='upload_file']")

    @property
    def submit_button(self) -> Locator:
        return self.page.locator("[data-qa='submit-button']")

    # --- DOM selectors — po wysłaniu ---
    @property
    def success_message(self) -> Locator:
        return self.page.locator("#contact-page .status.alert-success")

    @property
    def home_button(self) -> Locator:
        return self.page.locator("#form-section a.btn-success")

    # --- Actions ---
    def open(self) -> None:
        self.goto("contact_us")

    def fill_form(self, name: str, email: str, subject: str, message: str) -> None:
        self.name_input.fill(name)
        self.email_input.fill(email)
        self.subject_input.fill(subject)
        self.message_input.fill(message)

    def upload_file(self, file_path: str) -> None:
        self.file_input.set_input_files(file_path)

    def submit(self) -> None:
        # Formularz pokazuje natywny confirm() przed wysyłką — handler trzeba
        # zarejestrować PRZED kliknięciem, inaczej dialog zablokuje wykonanie.
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.submit_button.click()
