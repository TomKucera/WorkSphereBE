import math
from typing import List, Tuple


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot / (norm1 * norm2)


def score_cv(
    job_embedding: List[float],
    cv_chunks: list,
    cv_language: str,
    job_language: str,
    top_k: int = 3,
) -> Tuple[float, float, float]:
    """
    Returns:
        (similarity, language_bonus, final_score)
    """

    chunk_scores = []

    for chunk in cv_chunks:
        embedding = chunk.get("embedding")
        if not embedding:
            continue

        score = cosine_similarity(job_embedding, embedding)
        chunk_scores.append(score)

    if not chunk_scores:
        return 0.0, 0.0, 0.0

    chunk_scores.sort(reverse=True)
    top_scores = chunk_scores[:top_k]

    similarity = sum(top_scores) / len(top_scores)

    language_bonus = 0.03 if cv_language == job_language else 0.0

    final_score = similarity + language_bonus

    return similarity, language_bonus, final_score
