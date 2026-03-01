# import numpy as np


# def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
#     return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# def top_k_chunks(
#     query_embedding: list[float],
#     chunk_embeddings: list[list[float]],
#     chunks: list[str],
#     k: int = 5,
# ) -> list[str]:

#     q = np.array(query_embedding)

#     scored = []
#     for emb, chunk in zip(chunk_embeddings, chunks):
#         score = cosine_similarity(q, np.array(emb))
#         scored.append((score, chunk))

#     scored.sort(reverse=True, key=lambda x: x[0])

#     return [chunk for _, chunk in scored[:k]]
