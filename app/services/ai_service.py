# from openai import OpenAI
# from dataclasses import dataclass
# from enum import Enum


# class SupportedLanguage(str, Enum):
#     CZECH = "čeština"
#     ENGLISH = "angličtina"
#     GERMAN = "němčina"


# @dataclass
# class CoverLetterResult:
#     body: str
#     usage_input_tokens: int
#     usage_output_tokens: int


# class AiService:

#     def __init__(
#         self,
#         model: str = "gpt-4.1-mini",
#         temperature: float = 0.4,
#     ):
#         self._client = OpenAI()
#         self._model = model
#         self._temperature = temperature

#     # ==========================
#     # PUBLIC API
#     # ==========================

#     def prepare_cover_letter(
#         self,
#         job_description: str,
#         cv_text: str,
#         language: SupportedLanguage = SupportedLanguage.CZECH,
#         max_chars: int = 1200,
#     ) -> CoverLetterResult:

#         self._validate_input(job_description, cv_text)

#         body, usage1 = self._generate_full_version(
#             job_description,
#             cv_text,
#             language.value,
#         )

#         total_input = usage1.input_tokens
#         total_output = usage1.output_tokens

#         if len(body) > max_chars:
#             body, usage2 = self._compress_to_limit(
#                 body,
#                 language.value,
#                 max_chars,
#             )
#             total_input += usage2.input_tokens
#             total_output += usage2.output_tokens

#         body = self._hard_trim(body, max_chars)

#         return CoverLetterResult(
#             body=body.strip(),
#             usage_input_tokens=total_input,
#             usage_output_tokens=total_output,
#         )

#     # ==========================
#     # INTERNAL METHODS
#     # ==========================

#     def _validate_input(self, job_description: str, cv_text: str):
#         if not job_description or not cv_text:
#             raise ValueError("job_description and cv_text must not be empty")

#     def _generate_full_version(
#         self,
#         job_description: str,
#         cv_text: str,
#         language: str,
#     ):

#         system_prompt = (
#             "Jsi senior HR specialista a copywriter. "
#             "Vytváříš profesionální, konkrétní a přesvědčivé motivační dopisy."
#         )

#         user_prompt = f"""
#         Vytvoř profesionální motivační dopis.

#         Požadavky:
#         - Jazyk: {language}
#         - Profesionální tón
#         - Konkrétní a bez obecných frází
#         - Zaměř se pouze na relevantní zkušenosti

#         === POPIS POZICE ===
#         {job_description}

#         === CV ===
#         {cv_text}
#         """

#         response = self._client.responses.create(
#             model=self._model,
#             temperature=self._temperature,
#             input=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_prompt},
#             ],
#         )

#         return response.output_text.strip(), response.usage

#     def _compress_to_limit(
#         self,
#         body: str,
#         language: str,
#         max_chars: int,
#     ):

#         system_prompt = (
#             "Jsi expert na zkracování textů. "
#             "Zachovej význam, profesionalitu a klíčové informace."
#         )

#         user_prompt = f"""
#         Zkrať následující text na maximálně {max_chars} znaků včetně mezer.
#         Neztrácej klíčové informace.
#         Zachovej profesionální tón.
#         Jazyk: {language}

#         TEXT:
#         {body}
#         """

#         response = self._client.responses.create(
#             model=self._model,
#             temperature=0.2,
#             input=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_prompt},
#             ],
#         )

#         return response.output_text.strip(), response.usage

#     def _hard_trim(self, text: str, max_chars: int) -> str:
#         if len(text) <= max_chars:
#             return text

#         trimmed = text[:max_chars]
#         last_dot = trimmed.rfind(".")
#         if last_dot > 0:
#             return trimmed[: last_dot + 1]
#         return trimmed


from openai import OpenAI
from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class SupportedLanguage(str, Enum):
    CZECH = "čeština"
    ENGLISH = "angličtina"
    GERMAN = "němčina"


@dataclass
class TokenUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class CoverLetterResult:
    body: str
    usage_input_tokens: int
    usage_output_tokens: int


class AiService:

    def __init__(
        self,
        model: str = "gpt-4.1-mini",
        temperature: float = 0.4,
    ):
        self._client = OpenAI()
        self._model = model
        self._temperature = temperature

    # ==========================
    # PUBLIC API
    # ==========================

    def prepare_cover_letter(
        self,
        job_description: str,
        cv_text: str,
        language: SupportedLanguage = SupportedLanguage.CZECH,
        max_chars: int = 1200,
    ) -> CoverLetterResult:

        self._validate_input(job_description, cv_text)

        body, usage1 = self._generate_full_version(
            job_description,
            cv_text,
            language.value,
        )

        total_input = usage1.input_tokens
        total_output = usage1.output_tokens

        if len(body) > max_chars:
            body, usage2 = self._compress_to_limit(
                body,
                language.value,
                max_chars,
            )
            total_input += usage2.input_tokens
            total_output += usage2.output_tokens

        body = self._hard_trim(body, max_chars)

        return CoverLetterResult(
            body=body.strip(),
            usage_input_tokens=total_input,
            usage_output_tokens=total_output,
        )

    # ==========================
    # INTERNAL METHODS
    # ==========================

    def _validate_input(self, job_description: str, cv_text: str) -> None:
        if not job_description or not cv_text:
            raise ValueError("job_description and cv_text must not be empty")

    def _generate_full_version(
        self,
        job_description: str,
        cv_text: str,
        language: str,
    ) -> Tuple[str, TokenUsage]:

        system_prompt = (
            "Jsi senior HR specialista a copywriter. "
            "Vytváříš profesionální, konkrétní a přesvědčivé motivační dopisy."
        )

        user_prompt = f"""
        Vytvoř profesionální motivační dopis.

        Požadavky:
        - Jazyk: {language}
        - Profesionální tón
        - Konkrétní a bez obecných frází
        - Zaměř se pouze na relevantní zkušenosti

        === POPIS POZICE ===
        {job_description}

        === CV ===
        {cv_text}
        """

        response = self._client.responses.create(
            model=self._model,
            temperature=self._temperature,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        body = response.output_text.strip()

        usage = TokenUsage(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

        return body, usage

    def _compress_to_limit(
        self,
        body: str,
        language: str,
        max_chars: int,
    ) -> Tuple[str, TokenUsage]:

        system_prompt = (
            "Jsi expert na zkracování textů. "
            "Zachovej význam, profesionalitu a klíčové informace."
        )

        user_prompt = f"""
        Zkrať následující text na maximálně {max_chars} znaků včetně mezer.
        Neztrácej klíčové informace.
        Zachovej profesionální tón.
        Jazyk: {language}

        TEXT:
        {body}
        """

        response = self._client.responses.create(
            model=self._model,
            temperature=0.2,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        compressed_body = response.output_text.strip()

        usage = TokenUsage(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

        return compressed_body, usage

    def _hard_trim(self, text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text

        trimmed = text[:max_chars]
        last_dot = trimmed.rfind(".")
        if last_dot > 0:
            return trimmed[: last_dot + 1]

        return trimmed