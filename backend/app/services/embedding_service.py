import numpy as np
import httpx
import structlog

from app.config import settings

logger = structlog.get_logger()

HF_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction"


async def _call_hf_api(texts: list[str]) -> list[list[float]]:
    url = f"{HF_API_URL}/{settings.embedding_model_name}"
    headers = {}
    if settings.hf_api_token:
        headers["Authorization"] = f"Bearer {settings.hf_api_token}"

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            resp = await client.post(url, json={"inputs": texts, "options": {"wait_for_model": True}}, headers=headers)
            if resp.status_code != 200:
                raise RuntimeError(f"HuggingFace API error {resp.status_code}: {resp.text[:200]}")
            return resp.json()
    except httpx.ConnectError as e:
        raise RuntimeError(f"Cannot connect to HuggingFace API ({url}): {e}") from e
    except httpx.TimeoutException:
        raise RuntimeError(f"HuggingFace API request timed out ({url})") from None


def _normalize(vectors: list[list[float]]) -> np.ndarray:
    arr = np.array(vectors, dtype=np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1
    return arr / norms


async def embed_texts(texts: list[str], batch_size: int = 32) -> np.ndarray:
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        raw = await _call_hf_api(batch)
        all_embeddings.extend(raw)
    return _normalize(all_embeddings)


async def embed_query(query: str) -> np.ndarray:
    raw = await _call_hf_api([query])
    return _normalize(raw)[0]


def load_embedding_model() -> None:
    logger.info("embedding_service_ready", model=settings.embedding_model_name, backend="huggingface_api")
