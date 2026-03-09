from dataclasses import dataclass

from .cv_payload import CvPayload 

@dataclass(frozen=True)
class ApplicationData:
    first_name: str
    last_name: str
    email: str
    phone: str
    message: str
    cv: CvPayload
