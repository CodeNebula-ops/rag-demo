import uuid

import structlog
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PayloadSchemaType,
    PointStruct,
    VectorParams,
)

from app.config import settings

logger = structlog.get_logger()

_client: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    global _client
    if _client is None:
        if settings.qdrant_api_key:
            host = settings.qdrant_host.strip()
            if host.startswith("https://") or host.startswith("http://"):
                url = host
            else:
                url = f"https://{host}"
            url = url.rstrip("/")
            logger.info("qdrant_connecting", url=url)
            _client = QdrantClient(
                url=url,
                api_key=settings.qdrant_api_key,
                port=None,
            )
        else:
            _client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
    return _client


async def init_collection() -> None:
    client = get_qdrant_client()
    collections = client.get_collections().collections
    exists = any(c.name == settings.qdrant_collection_name for c in collections)

    if not exists:
        logger.info("creating_qdrant_collection", name=settings.qdrant_collection_name)
        client.create_collection(
            collection_name=settings.qdrant_collection_name,
            vectors_config=VectorParams(
                size=settings.qdrant_embedding_dim,
                distance=Distance.COSINE,
            ),
        )
        client.create_payload_index(
            collection_name=settings.qdrant_collection_name,
            field_name="document_id",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        client.create_payload_index(
            collection_name=settings.qdrant_collection_name,
            field_name="is_active",
            field_schema=PayloadSchemaType.BOOL,
        )
        logger.info("qdrant_collection_created")
    else:
        logger.info("qdrant_collection_exists", name=settings.qdrant_collection_name)


def upsert_vectors(
    vectors: list[list[float]],
    payloads: list[dict],
) -> list[str]:
    client = get_qdrant_client()
    point_ids = [str(uuid.uuid4()) for _ in vectors]

    points = [
        PointStruct(id=pid, vector=vec, payload=payload)
        for pid, vec, payload in zip(point_ids, vectors, payloads)
    ]

    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        client.upsert(collection_name=settings.qdrant_collection_name, points=batch)

    return point_ids


def search_vectors(
    query_vector: list[float],
    top_k: int = 20,
    document_filter: str | None = None,
) -> list[dict]:
    client = get_qdrant_client()

    must_conditions = [FieldCondition(key="is_active", match=MatchValue(value=True))]
    if document_filter:
        must_conditions.append(
            FieldCondition(key="document_id", match=MatchValue(value=document_filter))
        )

    try:
        results = client.search(
            collection_name=settings.qdrant_collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=Filter(must=must_conditions),
            with_payload=True,
        )
    except Exception as e:
        raise RuntimeError(f"Qdrant search failed (host={settings.qdrant_host}): {e}") from e

    return [
        {
            "point_id": str(hit.id),
            "score": hit.score,
            **hit.payload,
        }
        for hit in results
    ]


def deactivate_document_vectors(document_id: str) -> None:
    client = get_qdrant_client()

    results = client.scroll(
        collection_name=settings.qdrant_collection_name,
        scroll_filter=Filter(
            must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
        ),
        limit=10000,
        with_payload=False,
    )

    point_ids = [p.id for p in results[0]]
    if point_ids:
        client.set_payload(
            collection_name=settings.qdrant_collection_name,
            payload={"is_active": False},
            points=point_ids,
        )
        logger.info("deactivated_vectors", document_id=document_id, count=len(point_ids))
