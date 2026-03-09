from pathlib import Path

from app.application_processing.domain.application_data import ApplicationData
from app.application_processing.domain.cv_payload import CvPayload

from app.application_processing.providers.startup_jobs.startup_jobs_applier import StartupJobsApplier

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
        message="V reakci na pozici vývojáře backendu zaměřeného na PHP a Symfony nabízím své zkušenosti s vývojem robustních backendových řešení a integrací API, které přispějí k efektivnímu propojení e-shopových šablon s platformou Shoptet. Mám zkušenosti s návrhem architektury a refaktorováním kódu, což umožňuje zlepšit udržovatelnost a rozšiřitelnost aplikací. Práce v týmu, zahrnující spolupráci s frontend developery, produktovými manažery a UX designéry, je mi dobře známá a umím díky ní dosahovat optimálních výsledků. Díky orientaci na moderní technologie a metodiky vývoje přispěji k tvorbě nové generace šablon, které budou flexibilní a přizpůsobitelné potřebám uživatelů.",
        cv=cv_payload
    )

    # ------------------------------------------------
    # provider
    # ------------------------------------------------

    job_id = "101207"

    applier = StartupJobsApplier()

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

