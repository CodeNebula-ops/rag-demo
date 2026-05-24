import numpy as np
import structlog

from app.config import settings

logger = structlog.get_logger()

_model = None


def _get_model():
    global _model
    if _model is None:
        from fastembed import TextEmbedding
        _model = TextEmbedding(model_name=settings.embedding_model_name)
        logger.info("embedding_model_loaded", model=settings.embedding_model_name)
    return _model


def _normalize(arr: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1
    return arr / norms


async def embed_texts(texts: list[str], batch_size: int = 32) -> np.ndarray:
    model = _get_model()
    embeddings = list(model.embed(texts, batch_size=batch_size))
    arr = np.array(embeddings, dtype=np.float32)
    return _normalize(arr)


async def embed_query(query: str) -> np.ndarray:
    model = _get_model()
    embeddings = list(model.embed([query]))
    arr = np.array(embeddings, dtype=np.float32)
    return _normalize(arr)[0]


def load_embedding_model() -> None:
    _get_model()
