
from abc import ABC, abstractmethod

from app.application_processing.domain.application_data import ApplicationData
from app.application_processing.domain.application_result import ApplicationResult

class BaseProvider(ABC):

    provider_name: str

    @abstractmethod
    def apply(self, job_id: str, job_url: str, data: ApplicationData) -> ApplicationResult:
        """
        Apply to a job.

        Parameters
        ----------
        job_id : str
            External job identifier from provider.

        data : ApplicationData
            Candidate data used for the application.

        Returns
        -------
        ApplicationResult
        """
        pass

