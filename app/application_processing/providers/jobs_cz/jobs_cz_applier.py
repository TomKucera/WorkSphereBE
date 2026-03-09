from pathlib import Path
from playwright.sync_api import TimeoutError

from app.application_processing.providers.base_provider import BaseProvider
from app.application_processing.runtime.playwright_session import PlaywrightSession

from app.application_processing.domain.application_data import ApplicationData
from app.application_processing.domain.application_result import ApplicationResult


class JobsCZApplier(BaseProvider):

    provider_name = "JobsCZ"

    BASE_URL = "https://www.jobs.cz/rpd"

    def apply(self, job_id: str, job_url: str, data: ApplicationData) -> ApplicationResult:

        url = f"{self.BASE_URL}/{job_id}/"
        session = PlaywrightSession(headless=True)

        try:
            session.start()
            page = session.page

            page.goto(url)

            self._open_form(page)
            self._fill_contact(page, data)
            self._fill_message(page, data)
            self._upload_cv(page, data)

            success = self._submit(page)

            if success:
                return ApplicationResult(
                    success=True,
                    provider=self.provider_name,
                    job_url=url
                )

            screenshot = self._take_screenshot(page)

            return ApplicationResult(
                success=False,
                provider=self.provider_name,
                job_url=url,
                screenshot_path=screenshot,
                error_message="Application confirmation not detected"
            )

        except Exception as e:

            screenshot = None
            try:
                screenshot = self._take_screenshot(page)
            except:
                pass

            return ApplicationResult(
                success=False,
                provider=self.provider_name,
                job_url=url,
                screenshot_path=screenshot,
                error_message=str(e)
            )

        finally:
            session.stop()

    # ------------------------------------------------

    def _open_form(self, page):

        page.wait_for_load_state("networkidle")

        btn = page.locator("[data-test='jd-reply-button-top']")
        btn.wait_for(timeout=10000)
        btn.click()

    # ------------------------------------------------

    def _fill_contact(self, page, data: ApplicationData):

        page.fill("#jobad_application_firstName", data.first_name)
        page.fill("#jobad_application_surname", data.last_name)
        page.fill("#jobad_application_email", data.email)
        page.fill("#jobad_application_phone", data.phone)

    # ------------------------------------------------

    def _fill_message(self, page, data: ApplicationData):

        page.fill("#jobad_application_coverLetter", data.message)

    # ------------------------------------------------

    def _upload_cv(self, page, data: ApplicationData):

        page.set_input_files(
            "#customCvs",
            {
                "name": data.cv.filename,
                "mimeType": data.cv.mime_type,
                "buffer": data.cv.content,
            }
        )

    # ------------------------------------------------

    def _submit(self, page) -> bool:

        page.click("[data-test='application-send']")

        try:
            page.get_by_role(
                "heading",
                name="Skvělé! Máte odesláno"
            ).wait_for(timeout=10000)

            return True

        except TimeoutError:
            return False

    # ------------------------------------------------

    def _take_screenshot(self, page) -> str:

        path = Path("screenshots")
        path.mkdir(exist_ok=True)

        file = path / "jobs_cz_error.png"

        page.screenshot(path=str(file))

        return str(file)
