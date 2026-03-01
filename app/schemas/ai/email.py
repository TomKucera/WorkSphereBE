from pydantic import BaseModel


class GenerateEmailRequest(BaseModel):
    job_description: str
    cv_text: str


class GenerateEmailResponse(BaseModel):
    email: str
