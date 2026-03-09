from pathlib import Path

from app.application_processing.domain.application_data import ApplicationData
from app.application_processing.domain.cv_payload import CvPayload

from app.application_processing.providers.jobs_cz.jobs_cz_applier import JobsCZApplier

def main():

    # ------------------------------------------------
    # test CV file (simulate DB content)
    # ------------------------------------------------

    cv_file = Path("/Users/tomaskucera/Projects/WorkSphereBE/app/application_processing/tests/test_data/john_testator_junior_php_developer_cv_C.pdf")

    cv_payload = CvPayload(
        filename=cv_file.name,
        mime_type="application/pdf",
        content=cv_file.read_bytes()
    )

    # ------------------------------------------------
    # application data
    # ------------------------------------------------

    data = ApplicationData(
        first_name="John",
        last_name="Testator",
        email="john.testator43@gmail.com",
        phone="+420725993100",
        message="V reakci na pozici zaměřenou na vývoj a údržbu e-shopového řešení nabízím své zkušenosti s prací s databázemi a integrací REST API, které jsou nezbytné pro správné fungování backendových služeb a propojení s dalšími systémy. Díky znalosti SQL dokáži efektivně navrhovat a optimalizovat databázové dotazy, což přispívá k plynulému chodu aplikace a rychlé odezvě uživatelského rozhraní. Orientace v práci s webovými službami mi umožňuje zajistit spolehlivou komunikaci mezi různými komponentami platformy. Jsem připraven přispět k dalšímu rozvoji e-commerce řešení v agilním prostředí s důrazem na kvalitu a stabilitu kódu.",
        cv=cv_payload
    )

    # ------------------------------------------------
    # provider
    # ------------------------------------------------

    job_id = "2001095186"

    applier = JobsCZApplier()

    result = applier.apply(job_id, data)

    # ------------------------------------------------
    # result
    # ------------------------------------------------

    print("Success:", result.success)
    print("Provider:", result.provider)
    print("Job URL:", result.job_url)

    if result.error_message:
        print("Error:", result.error_message)

    if result.screenshot_path:
        print("Screenshot:", result.screenshot_path)


if __name__ == "__main__":
    main()

