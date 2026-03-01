from app.schemas.base.base_model import ApiBaseModel
from .scan_output_provider import ScanOutputProvider

class ScanOutput(ApiBaseModel):
    StartupJobs: ScanOutputProvider
    CoolJobs: ScanOutputProvider
    JobStackIT: ScanOutputProvider
    Titans: ScanOutputProvider
    JobsCZ: ScanOutputProvider