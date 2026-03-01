# from app.rag.chunking import split_text
# from app.rag.embeddings import embed_texts, embed_query
# from app.rag.search import top_k_chunks


# def get_relevant_cv_parts(cv_text: str, job_text: str) -> str:
#     chunks = split_text(cv_text)

#     chunk_embeddings = embed_texts(chunks)
#     query_embedding = embed_query(job_text)

#     best_chunks = top_k_chunks(query_embedding, chunk_embeddings, chunks, k=5)

#     return "\n\n".join(best_chunks)
