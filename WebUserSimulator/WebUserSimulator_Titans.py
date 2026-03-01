from playwright.sync_api import sync_playwright
from pathlib import Path


class WebUserSimulatorForTitans:
    def __init__(self, job_url_route: str, first_name: str, last_name:str, email: str, phone: str, message: str, cv_path: str, headless: bool = False):

        job_url=f"https://join.titans.eu/cs/{job_url_route}/"

        self._job_url = job_url
        self._first_name = first_name
        self._last_name = last_name
        self._email = email
        self._phone = phone
        self._message = message
        self._cv_path = cv_path

        self._headless = headless

        self._playwright = None
        self._browser = None
        self._page = None


    def apply(self)-> bool:
        
        # open browser
        self._start()
        
        # open form
        self._open_job_page(self._job_url)
        self._accept_cookies()
        self._click_reply()
        
        # fill form
        self._fill_contact_form()
        self._upload_cv()
        self._accept_terms()

        # submit form
        submited = self._submit()

        # close browser
        self._stop()

        return submited

    # --- lifecycle ---
    def _start(self):
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self._headless)
        self._page = self._browser.new_page()

    def _stop(self):
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    # --- main actions ---
    def _open_job_page(self, url: str):
        self._page.goto(url)

    def _accept_cookies(self, accept: bool = True):
        try:
            self._page.locator("#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click(timeout=3000)
        except Exception as e:
            print(f"Cookie bar not found or already handled: {e}")
    
    def _click_reply(self):
        self._page.click("[data-cy='react-btn']")

    def _fill_contact_form(self):
        name: str = f"{self._first_name} {self._last_name}"
        self._page.locator("[data-cy='name-input']:visible").fill(name)
        self._page.locator("[data-cy='email-input']:visible").fill(self._email)
        self._page.locator("[data-cy='phone-input']:visible").fill(self._phone)

    def _upload_cv(self):
        self._page.set_input_files("[data-cy='cv-input-file']", self._cv_path)

    def _accept_terms(self):
        self._page.locator("[data-cy='gdpr-checkbox']:visible").check()

    def _submit(self) -> bool:
        submit = self._page.locator("[data-cy='modal-form-send-btn']:visible")

        submit.wait_for(state="visible")

        with self._page.expect_response("**/api/registration") as resp:
            submit.click()

        return resp.value.status == 200

if __name__ == "__main__":

    url_route="salesforce-developer-260130ACZ"
    cv_path = Path(__file__).parent / "CVs" / "picture_ehub.png"

    web_user_simulator = WebUserSimulatorForTitans(
        job_url_route=url_route,
        first_name="Jan",
        last_name="Novák",
        email="jan.novak@email.cz",
        phone="+420777123456",
        message="I am interested in this position.",
        cv_path=cv_path
        )

    applied = web_user_simulator.apply()

    
