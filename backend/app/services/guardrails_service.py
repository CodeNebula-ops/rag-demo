import numpy as np
import structlog

logger = structlog.get_logger()


async def check_faithfulness(answer: str, chunks: list[dict]) -> dict:
    if not answer or not chunks:
        return {"faithful_ratio": 0.0, "unfaithful_sentences": []}

    from app.services.embedding_service import embed_texts

    sentences = _split_sentences(answer)
    if not sentences:
        return {"faithful_ratio": 0.0, "unfaithful_sentences": []}

    chunk_texts = [c["chunk_text"] for c in chunks]
    chunk_embeddings = await embed_texts(chunk_texts)
    sentence_embeddings = await embed_texts(sentences)

    faithful_count = 0
    unfaithful = []

    for i, sent_emb in enumerate(sentence_embeddings):
        similarities = np.dot(chunk_embeddings, sent_emb)
        max_sim = float(np.max(similarities)) if len(similarities) > 0 else 0.0

        if max_sim >= 0.5:
            faithful_count += 1
        else:
            unfaithful.append(sentences[i])

    ratio = faithful_count / len(sentences) if sentences else 0.0

    return {
        "faithful_ratio": ratio,
        "unfaithful_sentences": unfaithful,
    }


def compute_confidence(reranker_scores: list[float], faithful_ratio: float) -> dict:
    if not reranker_scores:
        avg_reranker = 0.0
    else:
        raw_avg = sum(reranker_scores) / len(reranker_scores)
        avg_reranker = min(max(raw_avg, 0.0), 1.0)

    score = (avg_reranker + faithful_ratio) / 2.0

    if score >= 0.85:
        level = "high"
    elif score >= 0.7:
        level = "medium"
    else:
        level = "low"

    return {
        "score": round(score, 3),
        "level": level,
        "retrieval_quality": round(avg_reranker, 3),
        "faithfulness": round(faithful_ratio, 3),
    }


def should_skip_llm(reranker_scores: list[float], threshold: float = 0.3) -> bool:
    if not reranker_scores:
        return True
    return all(s < threshold for s in reranker_scores)


def _split_sentences(text: str) -> list[str]:
    import nltk
    try:
        return [s.strip() for s in nltk.sent_tokenize(text) if len(s.strip()) > 5]
    except Exception:
        return [s.strip() for s in text.split(". ") if len(s.strip()) > 5]
