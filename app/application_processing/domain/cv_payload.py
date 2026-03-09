from dataclasses import dataclass

@dataclass(frozen=True)
class CvPayload:
    filename: str
    mime_type: str
    content: bytes  # DB -> bytes