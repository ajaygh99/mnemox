# vector_store.py — Mnemox Qdrant Vector Store
# Step 4: Store, search, and delete memory embeddings

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue,
    ScoredPoint,
)
from config import get_settings
from embeddings import EMBEDDING_DIMENSIONS
import logging

logger = logging.getLogger(__name__)

COLLECTION_NAME = "mnemox_memories"

_client: AsyncQdrantClient | None = None


def get_qdrant_client() -> AsyncQdrantClient:
    global _client
    if _client is None:
        settings = get_settings()
        url = settings.qdrant_url.strip() if settings.qdrant_url else ""

        # Use in-memory only if explicitly set to :memory: or empty
        if not url or url == ":memory:":
            _client = AsyncQdrantClient(location=":memory:")
            logger.warning("Qdrant running in-memory (dev mode)")
        else:
            _client = AsyncQdrantClient(
                url=url,
                api_key=settings.qdrant_api_key or None,
            )
            logger.info(f"Qdrant connected: {url}")
    return _client


async def ensure_collection():
    try:
        client = get_qdrant_client()
        collections = await client.get_collections()
        names = [c.name for c in collections.collections]
        if COLLECTION_NAME not in names:
            await client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIMENSIONS,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Created Qdrant collection: {COLLECTION_NAME}")
        else:
            logger.info(f"Qdrant collection exists: {COLLECTION_NAME}")
    except Exception as e:
        logger.error(f"Qdrant ensure_collection failed: {e}")
        # Non-fatal — app still starts, search/store will fail gracefully


def _uuid_to_int(uuid_str: str) -> int:
    import uuid
    return uuid.UUID(uuid_str).int % (2**63)


async def upsert_memory_vector(memory_id: str, vector: list, payload: dict):
    try:
        client = get_qdrant_client()
        await client.upsert(
            collection_name=COLLECTION_NAME,
            points=[PointStruct(
                id=_uuid_to_int(memory_id),
                vector=vector,
                payload={"memory_id": memory_id, **payload},
            )],
        )
    except Exception as e:
        logger.error(f"Qdrant upsert failed: {e}")
        raise


async def search_similar_memories(
    query_vector: list,
    user_id: str | None = None,
    source: str | None = None,
    limit: int = 5,
    score_threshold: float = 0.65,
) -> list:
    try:
        client = get_qdrant_client()
        filters = []
        if user_id:
            filters.append(FieldCondition(key="user_id", match=MatchValue(value=user_id)))
        if source:
            filters.append(FieldCondition(key="source", match=MatchValue(value=source)))

        query_filter = Filter(must=filters) if filters else None

        results = await client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=limit,
            score_threshold=score_threshold,
        )

        return [
            {
                "memory_id": r.payload.get("memory_id", str(r.id)),
                "score": r.score,
                "source": r.payload.get("source", ""),
                "content_preview": r.payload.get("content", "")[:200],
                "created_at": r.payload.get("created_at", ""),
            }
            for r in results
        ]
    except Exception as e:
        logger.error(f"Qdrant search failed: {e}")
        return []


async def delete_memory_vector(memory_id: str):
    try:
        client = get_qdrant_client()
        await client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=[_uuid_to_int(memory_id)],
        )
    except Exception as e:
        logger.error(f"Qdrant delete failed: {e}")
        raise


async def health_check_vector() -> bool:
    try:
        client = get_qdrant_client()
        await client.get_collections()
        return True
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        return False
