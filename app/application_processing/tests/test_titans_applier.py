from pathlib import Path

from app.application_processing.domain.application_data import ApplicationData
from app.application_processing.domain.cv_payload import CvPayload

from app.application_processing.providers.titans.titans_applier import TitansApplier


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
        message="""V rámci pozice vývojáře Smart Industry platformy mohu nabídnout zkušenosti s databázovými systémy, zejména s PostgreSQL a SQL, které jsou nezbytné pro správu a optimalizaci datových toků v logistických procesech. Díky znalostem databázového modelování a dotazování dokážu efektivně podporovat backendové systémy a přispívat k jejich stabilitě a výkonnosti. Jsem připraven úzce spolupracovat s týmem vývojářů, ICT specialistů a business analytiků, abych zajistil, že implementace databázových řešení bude odpovídat požadavkům projektu a podpoří plánování projektových dodávek. Věřím, že mé schopnosti v oblasti databází přispějí k hladkému průběhu vývoje a nasazení platformy.""",
        cv=cv_payload
    )

    # ------------------------------------------------
    # provider
    # ------------------------------------------------

    job_id = "java-smart-industry-programmer-251003FSK"

    applier = TitansApplier()

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
