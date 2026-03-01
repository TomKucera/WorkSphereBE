from playwright.sync_api import sync_playwright
from pathlib import Path


class WebUserSimulatorForJobsCZ:
    def __init__(self, job_id: str, first_name: str, last_name:str, email: str, phone: str, message: str, cv_path: str, headless: bool = False):

        job_url=f"https://www.jobs.cz/rpd/{job_id}/"

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
        self._click_reply()

        # fill form
        self._fill_contact_form()
        self._fill_contact_message()
        self._upload_cv()

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

    def _click_reply(self):
        self._page.wait_for_load_state("networkidle")

        btn = self._page.locator("[data-test='jd-reply-button-top']")
        btn.wait_for(timeout=10000)
        btn.click()

    def _fill_contact_form(self):
        self._page.fill("#jobad_application_firstName", self._first_name)
        self._page.fill("#jobad_application_surname", self._last_name)
        self._page.fill("#jobad_application_email", self._email)
        self._page.fill("#jobad_application_phone", self._phone)

    def _fill_contact_message(self):
        self._page.fill("#jobad_application_coverLetter", self._message)

    def _upload_cv(self):
        self._page.set_input_files("#customCvs", self._cv_path)

    def _submit(self) -> bool:
        self._page.click("[data-test='application-send']")

        try:
            self._page.get_by_role("heading", name="Skvělé! Máte odesláno").wait_for(timeout=10000)
            return True
        except:
            return False

if __name__ == "__main__":

    job_id="_2000983843"
    cv_path = Path(__file__).parent / "CVs" / "picture_ehub.png"

    web_user_simulator = WebUserSimulatorForJobsCZ(
        job_id=job_id,
        first_name="Jan",
        last_name="Novák",
        email="jan.novak@email.cz",
        phone="777123456",
        message="I am interested in this position.",
        cv_path=cv_path
        )

    applied = web_user_simulator.apply()
