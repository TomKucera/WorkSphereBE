



from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.services.ai_service import AiService, SupportedLanguage
from app.services.scraping_service import ScrapingService
from app.db.repositories.work_repository import WorkRepository
from app.db.repositories.cv_repository import CvRepository

from app.schemas.ai.cover_letter_response import CoverLetterResponse

from app.db.deps import get_db
from app.core.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["AI"])

@router.get("/cover-letter", response_model=CoverLetterResponse)
def generate_cover_letter(
    work_id: int = Query(...),
    cv_id: int = Query(...),
    language: SupportedLanguage = SupportedLanguage.CZECH,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    """
    Generate cover letter body for given work and CV.
    """

    max_chars: int = 1000 # TODO: read from provider settings

    work_repo = WorkRepository(db)
    cv_repo = CvRepository(db)

    work = work_repo.get(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    cv = cv_repo.get(cv_id, user_id, active = None)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    ai_service = AiService()

    work_description = work.Description

    # TODO: convert html to plain text ?!
    # work_description = ScrapingService.html_to_text(work_description)

    work_description = ScrapingService.strip_html(work_description)


    
    # return CoverLetterResponse(
    #     job_description=work_description,
    #     cv_text=cv.ExtractedText,
    #     body="",
    #     usage_input_tokens=len(work.Description) - len(work_description),
    #     usage_output_tokens=0,
    # )

    
    result = ai_service.prepare_cover_letter(
        job_description=work_description,
        cv_text=cv.ExtractedText,
        language=language,
        max_chars=max_chars,
    )

    return CoverLetterResponse(
        job_description=work_description,
        cv_text=cv.ExtractedText,
        body=result.body,
        usage_input_tokens=result.usage_input_tokens,
        usage_output_tokens=result.usage_output_tokens,
    )


# from fastapi import APIRouter, UploadFile, HTTPException, status, File, Depends, Form, Query
# from openai import OpenAI

# from pypdf import PdfReader
# from io import BytesIO

# import httpx
# from bs4 import BeautifulSoup

# from app.rag.service import get_relevant_cv_parts

# from app.schemas.ai.email import (
#     GenerateEmailRequest,
#     GenerateEmailResponse,
# )

# def read_pdf_from_bytes(data: bytes) -> str:
#     reader = PdfReader(BytesIO(data))
#     text = []

#     for page in reader.pages:
#         extracted = page.extract_text()
#         if extracted:
#             text.append(extracted)

#     return "\n".join(text)

# def read_pdf_from_url(url: str) -> str:
#     response = httpx.get(url, timeout=20)
#     response.raise_for_status()
#     return read_pdf_from_bytes(response.content)



# client = OpenAI()


# def fetch_job_text(url: str) -> str:
#     response = httpx.get(url, timeout=10)
#     response.raise_for_status()

#     soup = BeautifulSoup(response.text, "html.parser")

#     # jednoduché odstranění script/style
#     for tag in soup(["script", "style"]):
#         tag.decompose()

#     text = soup.get_text(separator=" ")
#     return " ".join(text.split())




# @router.post("/generate-email", response_model=GenerateEmailResponse)
# def generate_email(data: GenerateEmailRequest):
#     """
#     Generate a job application email based on job description and CV.
#     """

#     prompt = f"""
# Napiš profesionální pracovní email jako reakci na pracovní nabídku.

# POŽADAVKY:
# - Buď stručný (max 150 slov)
# - Zachovej profesionální tón
# - Zdůrazni relevantní zkušenosti z CV

# JOB DESCRIPTION:
# {data.job_description}

# CV:
# {data.cv_text}
# """

#     response = client.responses.create(
#         model="gpt-4.1-mini",
#         input=prompt,
#     )

#     text = response.output[0].content[0].text

#     return GenerateEmailResponse(email=text)


# @router.post("/generate-email-from-url")
# def generate_email_from_url(url: str, cv_text: str):
#     job_text = fetch_job_text(url)

#     prompt = f"""
# Napiš profesionální pracovní email jako reakci na pracovní nabídku.

# JOB:
# {job_text}

# CV:
# {cv_text}
# """

#     response = client.responses.create(
#         model="gpt-4.1-mini",
#         input=prompt,
#     )

#     return {"email": response.output[0].content[0].text}




# @router.post("/generate-email-rag")
# def generate_email_rag(job_url: str, cv_pdf_url: str):

#     job_text = fetch_job_text(job_url)
#     cv_text = read_pdf_from_url(cv_pdf_url)

#     relevant_cv = get_relevant_cv_parts(cv_text, job_text)

#     prompt = f"""
# Napiš profesionální pracovní email jako reakci na pracovní nabídku.

# Použij pouze relevantní informace z CV.

# JOB:
# {job_text}

# RELEVANT CV PARTS:
# {relevant_cv}
# """

#     response = client.responses.create(
#         model="gpt-4.1-mini",
#         input=prompt,
#     )

#     return {"email": response.output[0].content[0].text}

