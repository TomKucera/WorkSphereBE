from io import BytesIO

import pdfplumber
from docx import Document


def extract_text(file_bytes: bytes, content_type: str | None) -> str:
    """
    Vrátí čistý text ze souboru.
    Podporuje PDF, DOCX, TXT.
    """

    if content_type == "application/pdf":
        return _extract_pdf(file_bytes)

    if content_type in (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    ):
        return _extract_docx(file_bytes)

    if content_type == "text/plain":
        return file_bytes.decode("utf-8", errors="ignore")

    raise ValueError("Unsupported file type")


def _extract_pdf(file_bytes: bytes) -> str:
    text_parts: list[str] = []

    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)

    return "\n".join(text_parts).strip()


def _extract_docx(file_bytes: bytes) -> str:
    doc = Document(BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs).strip()