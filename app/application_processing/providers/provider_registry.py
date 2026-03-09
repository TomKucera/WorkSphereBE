from app.application_processing.providers.jobs_cz.jobs_cz_applier import JobsCZApplier
from app.application_processing.providers.startup_jobs.startup_jobs_applier import StartupJobsApplier
from app.application_processing.providers.cool_jobs.cool_jobs_applier import CoolJobsApplier
# from app.application_processing.providers.jobstack_it.jobstack_it_applier import JobStackITApplier
from app.application_processing.providers.titans.titans_applier import TitansApplier

from app.application_processing.providers.base_provider import BaseProvider


class ProviderRegistry:

    _providers: dict[str, type[BaseProvider]] = {
        "JobsCZ": JobsCZApplier,
        "StartupJobs": StartupJobsApplier,
        "CoolJobs": CoolJobsApplier,
        # "JobStackIT": JobStackITApplier,
        "Titans": TitansApplier,
    }

    @classmethod
    def get(cls, provider: str) -> BaseProvider:

        provider_cls = cls._providers.get(provider)

        if not provider_cls:
            raise ValueError(f"Unknown provider: {provider}")

        return provider_cls()
