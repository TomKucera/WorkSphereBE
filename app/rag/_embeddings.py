# from openai import OpenAI

# client = OpenAI()


# def embed_texts(texts: list[str]) -> list[list[float]]:
#     response = client.embeddings.create(
#         model="text-embedding-3-small",
#         input=texts,
#     )
#     return [e.embedding for e in response.data]


# def embed_query(text: str) -> list[float]:
#     return embed_texts([text])[0]
