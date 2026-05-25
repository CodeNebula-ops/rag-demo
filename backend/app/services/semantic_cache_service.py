import time
from collections import OrderedDict

import numpy as np
import structlog

from app.services.embedding_service import embed_query

logger = structlog.get_logger()

CACHE_SIMILARITY_THRESHOLD = 0.95
CACHE_TTL_SECONDS = 600
MAX_CACHE_SIZE = 50


class SemanticCache:
    def __init__(self):
        self._cache: OrderedDict[str, dict] = OrderedDict()
        self._embeddings: dict[str, np.ndarray] = {}

    async def get(self, query: str) -> dict | None:
        if not self._cache:
            return None

        query_emb = await embed_query(query)
        now = time.time()

        best_key = None
        best_sim = 0.0

        expired = []
        for key, entry in self._cache.items():
            if now - entry["timestamp"] > CACHE_TTL_SECONDS:
                expired.append(key)
                continue

            sim = float(np.dot(query_emb, self._embeddings[key]))
            if sim > best_sim:
                best_sim = sim
                best_key = key

        for key in expired:
            self._cache.pop(key, None)
            self._embeddings.pop(key, None)

        if best_key and best_sim >= CACHE_SIMILARITY_THRESHOLD:
            logger.info("semantic_cache_hit", similarity=round(best_sim, 3))
            self._cache.move_to_end(best_key)
            return self._cache[best_key]["data"]

        return None

    async def put(self, query: str, data: dict) -> None:
        query_emb = await embed_query(query)
        key = query

        if len(self._cache) >= MAX_CACHE_SIZE:
            oldest = next(iter(self._cache))
            self._cache.pop(oldest)
            self._embeddings.pop(oldest, None)

        self._cache[key] = {
            "data": data,
            "timestamp": time.time(),
        }
        self._embeddings[key] = query_emb
        self._cache.move_to_end(key)


cache = SemanticCache()
