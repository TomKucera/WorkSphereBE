from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class ApplicationResult:
    success: bool
    provider: str
    job_url: str

    external_application_id: Optional[str] = None

    error_code: Optional[str] = None
    error_message: Optional[str] = None

    screenshot_path: Optional[str] = None
    raw_debug: Optional[dict[str, Any]] = None