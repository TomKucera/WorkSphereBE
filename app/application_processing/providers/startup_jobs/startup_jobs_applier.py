import requests
from datetime import datetime, timezone

from app.application_processing.providers.base_provider import BaseProvider

from app.application_processing.domain.application_data import ApplicationData
from app.application_processing.domain.application_result import ApplicationResult


class StartupJobsApplier(BaseProvider):

    provider_name = "StartupJobs"

    BASE_URL = "https://www.startupjobs.cz"

    def apply(self, job_id: str, job_url: str, data: ApplicationData) -> ApplicationResult:

        session = requests.Session()

        try:

            attachment_name = self._upload_file(session, data)

            phonePrefix, phoneNumber = self._split_phone(data.phone)

            payload = {
                "payload": {
                    "email": data.email,
                    "name": f"{data.first_name} {data.last_name}",
                    "phone": phoneNumber,
                    "phonePrefix": phonePrefix,
                    "registerAccount": False,
                    "userFiles": [],
                    "why": f"<p>{data.message}</p>",
                    "attachments": [attachment_name],
                    "formOpenedAt": datetime.now(timezone.utc).isoformat(),
                    "device": "desktop",
                }
            }

            url = f"{self.BASE_URL}/offer/{job_id}/application/create"

            response = session.post(url, json=payload)

            response.raise_for_status()

            result = response.json()

            return ApplicationResult(
                success=True,
                provider=self.provider_name,
                job_url=f"{self.BASE_URL}/offer/{job_id}",
                external_application_id=str(result.get("application_id")),
                raw_debug=result,
            )

        except Exception as e:

            return ApplicationResult(
                success=False,
                provider=self.provider_name,
                job_url=f"{self.BASE_URL}/offer/{job_id}",
                error_message=str(e),
            )

    # ------------------------------------------------

    def _upload_file(self, session: requests.Session, data: ApplicationData) -> str:

        url = f"{self.BASE_URL}/admin-api/file"

        files = {
            "file": (
                data.cv.filename,
                data.cv.content,
                data.cv.mime_type,
            )
        }

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = session.post(url, files=files, headers=headers)

        response.raise_for_status()

        result = response.json()

        return result["name"]
    

    def _split_phone(self, phone: str) -> tuple[str, str]:

        phone = phone.replace(" ", "")

        if phone.startswith("+"):
            phone = phone[1:]

        # CZ default prefix
        if len(phone) == 9:
            return "420", phone

        # prefix + number
        if len(phone) > 9:
            prefix = phone[:-9]
            number = phone[-9:]
            return prefix, number

        raise ValueError(f"Invalid phone format: {phone}")