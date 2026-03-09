from pathlib import Path

from app.application_processing.domain.application_data import ApplicationData
from app.application_processing.domain.cv_payload import CvPayload

from app.application_processing.providers.cool_jobs.cool_jobs_applier import CoolJobsApplier


def main():

    # ------------------------------------------------
    # test CV file (simulate DB content)
    # ------------------------------------------------

    cv_file = Path(
        "/Users/tomaskucera/Projects/WorkSphereBE/app/application_processing/tests/test_data/john_testator_junior_php_developer_cv_C.pdf"
    )

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
        message="""V reakci na pozici PHP Developera nabízím své zkušenosti s vývojem a modernizací backendových systémů, které jsou založené na objektově orientovaném programování a principu Domain-Driven Design. Mám praxi v práci s PHP 8.2 a PHPUnit, což mi umožňuje psát testovatelný a udržitelný kód, který odpovídá vysokým standardům kvality. Zkušenosti s agilním vývojem v prostředí Scrum mi dávají schopnost efektivně spolupracovat v týmu a flexibilně reagovat na změny během vývojového cyklu. Jsem připraven přispět k rozkladu monolitické architektury a optimalizaci CI/CD pipeline, což povede k lepší škálovatelnosti a rychlejší dodávce nových funkcionalit. Díky svému zaměření na kvalitu a čitelnost kódu mohu podpořit kontinuální zlepšování vývojového procesu a rozvoj DevOps kultury v týmu. Věřím, že mé zkušenosti a přístup pomohou posunout projekt směrem k udržitelnému a efektivnímu vývoji SaaS řešení.""",
        cv=cv_payload
    )

    # ------------------------------------------------
    # provider
    # ------------------------------------------------

    job_id = "41925"   # requestid = job_id

    applier = CoolJobsApplier()

    result = applier.apply(job_id, data)

    # ------------------------------------------------
    # result
    # ------------------------------------------------

    print("Success:", result.success)
    print("Provider:", result.provider)
    print("Job URL:", result.job_url)

    if result.external_application_id:
        print("External application id:", result.external_application_id)

    if result.error_message:
        print("Error:", result.error_message)

    if result.screenshot_path:
        print("Screenshot:", result.screenshot_path)


if __name__ == "__main__":
    main()
