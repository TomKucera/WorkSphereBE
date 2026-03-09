from pathlib import Path

from app.application_processing.providers.base_provider import BaseProvider
from app.application_processing.runtime.playwright_session import PlaywrightSession

from app.application_processing.domain.application_data import ApplicationData
from app.application_processing.domain.application_result import ApplicationResult


class TitansApplier(BaseProvider):

    provider_name = "Titans"

    BASE_URL = "https://join.titans.eu/cs"

    def apply(self, job_id: str, job_url: str, data: ApplicationData) -> ApplicationResult:

        url = f"{self.BASE_URL}/{job_url}/"
        session = PlaywrightSession(headless=True)

        try:

            session.start()
            page = session.page

            page.goto(url)

            self._accept_cookies(page)
            self._click_reply(page)

            self._fill_contact(page, data)
            self._upload_cv(page, data)
            self._accept_terms(page)

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
                error_message="Application API returned non-200 status"
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

    def _accept_cookies(self, page):

        try:
            page.locator(
                "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"
            ).click(timeout=3000)

        except Exception:
            pass

    # ------------------------------------------------

    def _click_reply(self, page):

        page.locator("[data-cy='react-btn']").first.click()

    # ------------------------------------------------

    def _fill_contact(self, page, data: ApplicationData):

        name = f"{data.first_name} {data.last_name}"

        page.locator("[data-cy='name-input']:visible").fill(name)
        page.locator("[data-cy='email-input']:visible").fill(data.email)
        page.locator("[data-cy='phone-input']:visible").fill(data.phone)

    # ------------------------------------------------

    def _upload_cv(self, page, data: ApplicationData):

        page.set_input_files(
            "[data-cy='cv-input-file']",
            {
                "name": data.cv.filename,
                "mimeType": data.cv.mime_type,
                "buffer": data.cv.content
            }
        )

    # ------------------------------------------------

    def _accept_terms(self, page):

        page.locator("[data-cy='gdpr-checkbox']:visible").check()

    # ------------------------------------------------

    def _submit(self, page) -> bool:

        submit = page.locator("[data-cy='modal-form-send-btn']:visible")

        submit.wait_for(state="visible")

        with page.expect_response("**/api/registration") as resp:
            submit.click()

        return resp.value.status == 200

    # ------------------------------------------------

    def _take_screenshot(self, page) -> str:

        path = Path("screenshots")
        path.mkdir(exist_ok=True)

        file = path / "titans_error.png"

        page.screenshot(path=str(file))

        return str(file)
