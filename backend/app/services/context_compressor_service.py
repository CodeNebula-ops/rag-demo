import numpy as np
import structlog

from app.services.embedding_service import embed_texts

logger = structlog.get_logger()

SIMILARITY_DEDUP_THRESHOLD = 0.92


async def compress_and_order(chunks: list[dict], query_intent: str = "factual") -> list[dict]:
    if not chunks:
        return []

    deduped = await _deduplicate(chunks)
    ordered = _order_by_intent(deduped, query_intent)
    compressed = _compress_chunks(ordered)

    logger.info(
        "context_compressed",
        input_chunks=len(chunks),
        after_dedup=len(deduped),
        output_chunks=len(compressed),
    )
    return compressed


async def _deduplicate(chunks: list[dict]) -> list[dict]:
    if len(chunks) <= 1:
        return chunks

    texts = [c["chunk_text"] for c in chunks]

    try:
        embeddings = await embed_texts(texts)
    except Exception:
        return chunks

    keep = [True] * len(chunks)
    for i in range(len(chunks)):
        if not keep[i]:
            continue
        for j in range(i + 1, len(chunks)):
            if not keep[j]:
                continue
            sim = float(np.dot(embeddings[i], embeddings[j]))
            if sim >= SIMILARITY_DEDUP_THRESHOLD:
                if chunks[j].get("reranker_score", 0) <= chunks[i].get("reranker_score", 0):
                    keep[j] = False
                else:
                    keep[i] = False
                    break

    return [c for c, k in zip(chunks, keep) if k]


def _order_by_intent(chunks: list[dict], intent: str) -> list[dict]:
    if intent == "procedural":
        return sorted(chunks, key=lambda c: c.get("chunk_index", 0))

    if intent == "comparative":
        by_doc: dict[str, list[dict]] = {}
        for c in chunks:
            doc = c.get("document_title", "")
            by_doc.setdefault(doc, []).append(c)
        ordered = []
        for doc_chunks in by_doc.values():
            ordered.extend(sorted(doc_chunks, key=lambda c: c.get("chunk_index", 0)))
        return ordered

    return chunks


def _compress_chunks(chunks: list[dict], max_tokens: int = 300) -> list[dict]:
    compressed = []
    for chunk in chunks:
        text = chunk.get("chunk_text", "")
        words = text.split()
        if len(words) > max_tokens:
            text = " ".join(words[:max_tokens]) + "..."
            chunk = {**chunk, "chunk_text": text}
        compressed.append(chunk)
    return compressed
