import numpy as np
import structlog

from app.config import settings
from app.services.embedding_service import embed_query, embed_texts

logger = structlog.get_logger()


def load_reranker_model() -> None:
    logger.info("reranker_service_ready", backend="embedding_similarity")


async def rerank(query: str, documents: list[dict], top_n: int | None = None) -> list[dict]:
    if not documents:
        return []

    top_n = top_n or settings.rerank_top_n

    query_emb = await embed_query(query)
    doc_texts = [doc["chunk_text"] for doc in documents]
    doc_embs = await embed_texts(doc_texts)

    scores = np.dot(doc_embs, query_emb)

    for i, doc in enumerate(documents):
        doc["reranker_score"] = float(scores[i])

    ranked = sorted(documents, key=lambda d: d["reranker_score"], reverse=True)

    seen_sections = {}
    diversified = []
    for doc in ranked:
        section = doc.get("section_path", "")
        if section in seen_sections and seen_sections[section] >= 2:
            continue
        seen_sections[section] = seen_sections.get(section, 0) + 1
        diversified.append(doc)
        if len(diversified) >= top_n:
            break

    return diversified
