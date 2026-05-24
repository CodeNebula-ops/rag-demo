import numpy as np
import structlog
from sentence_transformers import SentenceTransformer

from app.config import settings

logger = structlog.get_logger()

_model: SentenceTransformer | None = None


def load_embedding_model() -> None:
    global _model
    logger.info("loading_embedding_model", model=settings.embedding_model_name)
    _model = SentenceTransformer(settings.embedding_model_name)
    logger.info("embedding_model_loaded")


def get_embedding_model() -> SentenceTransformer:
    if _model is None:
        load_embedding_model()
    return _model


def embed_texts(texts: list[str], batch_size: int = 32) -> np.ndarray:
    model = get_embedding_model()
    embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=False, normalize_embeddings=True)
    return np.array(embeddings)


def embed_query(query: str) -> np.ndarray:
    model = get_embedding_model()
    embedding = model.encode(query, normalize_embeddings=True)
    return np.array(embedding)
