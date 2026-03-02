from app.db.models.work import Work

URL_BY_PROVIDER: dict[str, str] = {
    "StartupJobs": "https://www.startupjobs.cz",
    "CoolJobs": "https://www.cooljobs.eu/cz/",
    "JobStackIT": "https://www.jobstack.it",
    "Titans": "https://join.titans.eu/cs/",
    "JobsCZ": "https://www.jobs.cz/",
}


def get_work_full_url(work: Work) -> str | None:
    base = URL_BY_PROVIDER.get(work.Provider)

    if not base:
        return None

    if not work.Url:
        return None

    return f"{base}{work.Url}"