# from openai import OpenAI


# class AiClient:

#     def __init__(self, model: str = "gpt-4.1-mini"):
#         self._client = OpenAI()
#         self._model = model

#     def generate(self, system_prompt: str, user_prompt: str) -> str:
#         response = self._client.responses.create(
#             model=self._model,
#             temperature=0.4,
#             input=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_prompt},
#             ],
#         )

#         return response.output_text.strip()
    

from openai import OpenAI
from dataclasses import dataclass


@dataclass
class AiResult:
    text: str
    input_tokens: int
    output_tokens: int


class AiClient:

    def __init__(self, model: str = "gpt-4.1-mini"):
        self._client = OpenAI()
        self._model = model

    def generate(self, system_prompt: str, user_prompt: str) -> AiResult:

        response = self._client.responses.create(
            model=self._model,
            temperature=0.4,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        return AiResult(
            text=response.output_text.strip(),
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )