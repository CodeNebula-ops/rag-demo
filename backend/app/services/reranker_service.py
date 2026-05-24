import structlog
from sentence_transformers import CrossEncoder

from app.config import settings

logger = structlog.get_logger()

_reranker: CrossEncoder | None = None


def load_reranker_model() -> None:
    global _reranker
    logger.info("loading_reranker_model", model=settings.reranker_model_name)
    _reranker = CrossEncoder(settings.reranker_model_name)
    logger.info("reranker_model_loaded")


def get_reranker() -> CrossEncoder:
    if _reranker is None:
        load_reranker_model()
    return _reranker


def rerank(query: str, documents: list[dict], top_n: int | None = None) -> list[dict]:
    if not documents:
        return []

    top_n = top_n or settings.rerank_top_n
    reranker = get_reranker()

    pairs = [(query, doc["chunk_text"]) for doc in documents]
    scores = reranker.predict(pairs)

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
