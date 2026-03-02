import re
from typing import List, Iterable
from .ai_client import AiResult

MODEL_PRICING = {
    "gpt-4.1-mini": {
        "input_per_1k": 0.0005,
        "output_per_1k": 0.0015,
    },
    "gpt-4.1": {
        "input_per_1k": 0.005,
        "output_per_1k": 0.015,
    },
    "gpt-4o-mini": {
        "input_per_1k": 0.0003,
        "output_per_1k": 0.0006,
    },
}


KNOWN_SKILLS = [
    "Python", "REST API", "SQL", "PostgreSQL",
    "MS SQL", "Kafka", "ETL", "Airflow",
    "OAuth2", "JWT", "Azure", "CI/CD",
    "Node.js", "C#", "FastAPI"
]


def sanitize_text(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"\+?\d[\d\s]{7,}", "", text)  # phone
    text = re.sub(r"\S+@\S+", "", text)          # email
    return text.strip()


def extract_skills(text: str) -> List[str]:
    found = []
    lower = text.lower()

    for skill in KNOWN_SKILLS:
        if skill.lower() in lower:
            found.append(skill)

    return found


def calculate_match_score(job_skills: List[str], cv_skills: List[str]) -> float:
    if not job_skills:
        return 0.0

    intersection = set(job_skills).intersection(set(cv_skills))
    return len(intersection) / len(job_skills)


# def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
#     pricing = MODEL_PRICING.get(model)

#     if not pricing:
#         raise ValueError(f"No pricing configured for model {model}")

#     input_cost = (input_tokens / 1000) * pricing["input_per_1k"]
#     output_cost = (output_tokens / 1000) * pricing["output_per_1k"]

#     return round(input_cost + output_cost, 6)

def estimate_cost(model: str, results: Iterable[AiResult]) -> dict:

    pricing = MODEL_PRICING.get(model)
    if not pricing:
        raise ValueError(f"No pricing configured for model '{model}'")

    total_input_tokens = sum(r.input_tokens for r in results)
    total_output_tokens = sum(r.output_tokens for r in results)

    input_cost = (total_input_tokens / 1000) * pricing["input_per_1k"]
    output_cost = (total_output_tokens / 1000) * pricing["output_per_1k"]

    total_cost = round(input_cost + output_cost, 6)

    return {
        "model": model,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "estimated_cost_usd": total_cost,
    }