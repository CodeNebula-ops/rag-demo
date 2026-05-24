import pickle
from pathlib import Path

import numpy as np
import structlog
from rank_bm25 import BM25Okapi
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.text_preprocessor import normalize_text
from app.models.document import DocumentChunk
from app.services.embedding_service import embed_query
from app.services.reranker_service import rerank
from app.services.vector_store_service import search_vectors

logger = structlog.get_logger()

_bm25_index: BM25Okapi | None = None
_bm25_corpus: list[str] = []
_bm25_point_ids: list[str] = []

BM25_CACHE_PATH = Path("/tmp/bm25_index.pkl")


def add_to_bm25_index(texts: list[str], point_ids: list[str]) -> None:
    global _bm25_index, _bm25_corpus, _bm25_point_ids

    _bm25_corpus.extend(texts)
    _bm25_point_ids.extend(point_ids)

    tokenized = [doc.lower().split() for doc in _bm25_corpus]
    _bm25_index = BM25Okapi(tokenized)

    _save_bm25_cache()


async def rebuild_bm25_index(session: AsyncSession) -> None:
    global _bm25_index, _bm25_corpus, _bm25_point_ids

    result = await session.execute(
        select(DocumentChunk.chunk_text, DocumentChunk.qdrant_point_id).where(
            DocumentChunk.qdrant_point_id.is_not(None)
        )
    )
    rows = result.all()

    if not rows:
        logger.info("bm25_index_empty")
        _bm25_index = None
        _bm25_corpus = []
        _bm25_point_ids = []
        return

    _bm25_corpus = [row[0] for row in rows]
    _bm25_point_ids = [row[1] for row in rows]

    tokenized = [doc.lower().split() for doc in _bm25_corpus]
    _bm25_index = BM25Okapi(tokenized)

    _save_bm25_cache()
    logger.info("bm25_index_rebuilt", documents=len(_bm25_corpus))


def _save_bm25_cache() -> None:
    try:
        with open(BM25_CACHE_PATH, "wb") as f:
            pickle.dump(
                {"corpus": _bm25_corpus, "point_ids": _bm25_point_ids},
                f,
            )
    except Exception as e:
        logger.warning("bm25_cache_save_failed", error=str(e))


def _bm25_search(query: str, top_k: int = 20) -> list[dict]:
    if _bm25_index is None or not _bm25_corpus:
        return []

    tokenized_query = query.lower().split()
    scores = _bm25_index.get_scores(tokenized_query)

    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        if scores[idx] > 0:
            results.append({
                "point_id": _bm25_point_ids[idx],
                "bm25_score": float(scores[idx]),
                "chunk_text": _bm25_corpus[idx],
            })

    return results


def _reciprocal_rank_fusion(
    dense_results: list[dict],
    sparse_results: list[dict],
    k: int = 60,
) -> list[dict]:
    rrf_scores: dict[str, float] = {}
    all_docs: dict[str, dict] = {}

    for rank, doc in enumerate(dense_results):
        pid = doc["point_id"]
        rrf_scores[pid] = rrf_scores.get(pid, 0) + 1.0 / (k + rank + 1)
        all_docs[pid] = doc

    for rank, doc in enumerate(sparse_results):
        pid = doc["point_id"]
        rrf_scores[pid] = rrf_scores.get(pid, 0) + 1.0 / (k + rank + 1)
        if pid not in all_docs:
            all_docs[pid] = doc

    sorted_ids = sorted(rrf_scores, key=rrf_scores.get, reverse=True)

    fused = []
    for pid in sorted_ids[:20]:
        doc = all_docs[pid]
        doc["rrf_score"] = rrf_scores[pid]
        fused.append(doc)

    return fused


async def retrieve(query: str, top_n: int | None = None) -> list[dict]:
    top_n = top_n or settings.rerank_top_n
    normalized_query = normalize_text(query)

    query_embedding = embed_query(normalized_query)
    dense_results = search_vectors(query_embedding.tolist(), top_k=settings.retrieval_top_k)

    sparse_results = _bm25_search(normalized_query, top_k=settings.retrieval_top_k)

    fused = _reciprocal_rank_fusion(dense_results, sparse_results)

    if not fused:
        return []

    reranked = rerank(normalized_query, fused, top_n=top_n)

    logger.info(
        "retrieval_complete",
        query_length=len(query),
        dense=len(dense_results),
        sparse=len(sparse_results),
        fused=len(fused),
        reranked=len(reranked),
    )

    return reranked
