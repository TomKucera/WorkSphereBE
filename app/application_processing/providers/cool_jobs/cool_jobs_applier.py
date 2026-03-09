import requests

from app.application_processing.providers.base_provider import BaseProvider

from app.application_processing.domain.application_data import ApplicationData
from app.application_processing.domain.application_result import ApplicationResult


class CoolJobsApplier(BaseProvider):

    provider_name = "CoolJobs"

    BASE_URL = "https://www.cooljobs.eu"

    def apply(self, job_id: str, job_url: str, data: ApplicationData) -> ApplicationResult:

        try:

            url = f"{self.BASE_URL}/cz/pos/1001.html?action=SubmitApplication"

            form_data = {
                "jmeno": f"{data.first_name} {data.last_name}",
                "email": data.email,
                "telefon": data.phone,
                "poznamka": data.message,
                "souhlas": "on",
                "requestid": job_id,
            }

            files = {
                "cv": (
                    data.cv.filename,
                    data.cv.content,
                    data.cv.mime_type,
                )
            }

            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json",
                # "Referer": f"{self.BASE_URL}/cz/pos/{job_id}.html"
            }

            response = requests.post(
                url,
                data=form_data,
                files=files,
                headers=headers,
            )

            response.raise_for_status()

            result = response.json()

            success = False

            for action in result.get("actions", []):
                if action.get("icon") == "success":
                    success = True
                    break

            return ApplicationResult(
                success=success,
                provider=self.provider_name,
                job_url=f"{self.BASE_URL}/cz/pos/{job_id}.html",
                raw_debug=result,
                error_message=None if success else "Application not confirmed",
            )

        except Exception as e:

            return ApplicationResult(
                success=False,
                provider=self.provider_name,
                job_url=f"{self.BASE_URL}/cz/pos/{job_id}.html",
                error_message=str(e),
            )