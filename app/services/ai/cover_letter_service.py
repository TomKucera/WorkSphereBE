# app/services/ai/cover_letter_service.py

from .ai_client import AiClient, AiResult
from .ai_utils import (
    sanitize_text,
    extract_skills,
    calculate_match_score,
    estimate_cost,
)

LANGUAGE_PROMPTS = {
    "cs": "Piš v češtině.",
    "en": "Write in English.",
    "de": "Schreibe auf Deutsch.",
}


class CoverLetterService:

    def __init__(self):
        self.ai_client = AiClient()
    
    def generate(
        self,
        job_description: str,
        cv_text: str,
        max_chars: int = 1000,
        language: str = "cs",
        language_level: str | None = None,
    ) -> dict:

        # 1️⃣ Sanitizace CV (odstranění kontaktů)
        clean_cv = sanitize_text(cv_text)

        # 2️⃣ Shrnutí pozice (AI krok – komprese kontextu)
        job_summary_result = self._summarize_job(job_description)
        job_summary = job_summary_result.text

        # 3️⃣ Skill extraction
        job_skills = extract_skills(job_description)
        cv_skills = extract_skills(clean_cv)

        overlap = list(set(job_skills).intersection(set(cv_skills)))

        # 4️⃣ Match score
        score = calculate_match_score(job_skills, cv_skills)

        language_note = self._build_language_note(language, language_level)

        # 5️⃣ Kontext pro generování (bez mechanického výčtu)
        context = f"""
    Shrnutí pozice:
    {job_summary}

    Relevantní dovednosti kandidáta:
    {', '.join(overlap)}

    {language_note}
    """

        system_prompt = f"""
    Jsi senior HR specialista.
    {LANGUAGE_PROMPTS.get(language)}

    Instrukce:
    - Nevytvářej oslovení ani podpis.
    - Nezmiňuj chybějící dovednosti.
    - Nevypisuj seznam technologií mechanicky.
    - Piš profesionálně, konkrétně a přirozeně.
    - Zaměř se na hodnotu, kterou kandidát přinese.
    - Neuváděj kontaktní údaje.
    - Nepřeháněj rozsah zkušeností.
    - Používej pouze informace, které jsou podloženy uvedenými dovednostmi.
    - Nepoužívej marketingové fráze typu "S potěšením".
    - Nepoužívej obecné hodnotící formulace (např. "klíčové", "zásadní", "významné").
    """

        user_prompt = f"""
    Vytvoř profesionální motivační dopis.

    {context}
    """

        # 6️⃣ Generování dopisu
        generation_result = self.ai_client.generate(system_prompt, user_prompt)
        body = generation_result.text

        # # 7️⃣ Odstranění případného AI oslovení
        # body = self._remove_ai_greeting(body)

        # # 8️⃣ Přidání deterministického pozdravu
        # body = f"Dobrý den,\n\n{body.strip()}"

        # 9️⃣ Hard trim safeguard
        if len(body) > max_chars:
            body = body[:max_chars].rsplit(".", 1)[0] + "."

        # 🔟 Post-sanitization safeguard
        body = sanitize_text(body)

        cost_info = estimate_cost(self.ai_client._model, [job_summary_result, generation_result])
        cost_info["language"] = language
        cost_info["language_level"] = language_level

        return {
            "body": body.strip(),
            "match_score": score,
            "job_skills": job_skills,
            "cv_skills": cv_skills,
            "generation_info": cost_info,
        }

    def _summarize_job(self, job_description: str) -> AiResult:

        system_prompt = """
        Shrň pracovní pozici do maximálně 4 vět.
        Zaměř se na:
        - hlavní odpovědnost
        - typ projektu
        - klíčové technologie
        Neuváděj benefity ani obecné fráze.
        """

        summary = self.ai_client.generate(system_prompt, job_description)

        return summary
    
    def _build_language_note(self, language: str, level: str | None) -> str:

        if not level:
            return ""

        if language == "en":
            return f"Candidate communicates in English at {level} level."

        if language == "de":
            return f"Der Kandidat verfügt über Deutschkenntnisse auf {level} Niveau."

        return ""