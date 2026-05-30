# vector_store.py — Mnemox Qdrant Vector Store
# Step 4: Store, search, and delete memory embeddings
# Free tier: Qdrant Cloud — 1GB, no credit card needed

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

# ── Client (singleton) ────────────────────────────────────────────────────────
_client: AsyncQdrantClient | None = None


def get_qdrant_client() -> AsyncQdrantClient:
    global _client
    if _client is None:
        settings = get_settings()
        if settings.qdrant_url:
            # Qdrant Cloud
            _client = AsyncQdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key or None,
            )
            logger.info(f"Qdrant connected: {settings.qdrant_url}")
        else:
            # Local in-memory (dev/test — no persistence)
            _client = AsyncQdrantClient(":memory:")
            logger.warning("Qdrant running in-memory (dev mode — data not persisted)")
    return _client


# ── Collection setup ──────────────────────────────────────────────────────────

async def ensure_collection() -> None:
    """Create the Qdrant collection if it doesn't exist. Safe to call on every startup."""
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
        logger.info(f"Qdrant collection '{COLLECTION_NAME}' created")
    else:
        logger.info(f"Qdrant collection '{COLLECTION_NAME}' already exists")


# ── Vector operations ─────────────────────────────────────────────────────────

async def upsert_memory_vector(
    memory_id: str,
    vector: list[float],
    payload: dict,
) -> None:
    """Store a memory embedding in Qdrant with metadata payload."""
    client = get_qdrant_client()

    # Qdrant requires integer IDs — we hash the UUID to an int
    point_id = _uuid_to_int(memory_id)

    await client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "memory_id": memory_id,   # original UUID string
                    "source": payload.get("source", ""),
                    "user_id": payload.get("user_id", ""),
                    "content_preview": payload.get("content", "")[:200],
                    "created_at": payload.get("created_at", ""),
                },
            )
        ],
    )
    logger.info(f"Vector upserted for memory {memory_id}")


async def search_similar_memories(
    query_vector: list[float],
    user_id: str | None = None,
    source: str | None = None,
    limit: int = 10,
    score_threshold: float = 0.65,
) -> list[dict]:
    """
    Find the top-N most semantically similar memories.
    Returns list of dicts with memory_id + similarity score.
    """
    client = get_qdrant_client()

    # Build optional filters
    conditions = []
    if user_id:
        conditions.append(FieldCondition(key="user_id", match=MatchValue(value=user_id)))
    if source:
        conditions.append(FieldCondition(key="source", match=MatchValue(value=source)))

    query_filter = Filter(must=conditions) if conditions else None

    results: list[ScoredPoint] = await client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        query_filter=query_filter,
        limit=limit,
        score_threshold=score_threshold,
        with_payload=True,
    )

    return [
        {
            "memory_id": r.payload.get("memory_id"),
            "score": round(r.score, 4),
            "source": r.payload.get("source"),
            "content_preview": r.payload.get("content_preview"),
            "created_at": r.payload.get("created_at"),
        }
        for r in results
    ]


async def delete_memory_vector(memory_id: str) -> None:
    """Remove a memory's vector from Qdrant."""
    client = get_qdrant_client()
    point_id = _uuid_to_int(memory_id)
    await client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=[point_id],
    )
    logger.info(f"Vector deleted for memory {memory_id}")


async def health_check_vector() -> bool:
    """Verify Qdrant is reachable."""
    try:
        client = get_qdrant_client()
        await client.get_collections()
        return True
    except Exception as e:
        logger.warning(f"Qdrant health check failed: {e}")
        return False


# ── Helpers ───────────────────────────────────────────────────────────────────

def _uuid_to_int(uuid_str: str) -> int:
    """Convert UUID string to a positive 64-bit integer for Qdrant point ID."""
    import uuid
    return uuid.UUID(uuid_str).int % (2**63)
