from openai import OpenAI


# jednoduchý singleton klient (POC)
_client: OpenAI | None = None


DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


def _get_client() -> OpenAI:
    global _client

    if _client is None:
        _client = OpenAI()

    return _client


def get_embedding(text: str) -> list[float]:
    """
    Vrátí embedding vektor pro zadaný text.
    POC verze – synchronní, jeden text.
    """

    if not text.strip():
        raise ValueError("Text for embedding is empty")

    client = _get_client()

    response = client.embeddings.create(
        model=DEFAULT_EMBEDDING_MODEL,
        input=text,
    )

    return response.data[0].embedding