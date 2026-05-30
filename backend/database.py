# database.py — Supabase client + memory operations
# Step 3: CRUD for memories table

from supabase import create_client, Client
from config import get_settings
from models import MemoryCreate, Memory
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)

# ── Supabase client (singleton) ───────────────────────────────────────────────
_client: Client | None = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        settings = get_settings()
        if not settings.supabase_url or not settings.supabase_service_key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env"
            )
        _client = create_client(settings.supabase_url, settings.supabase_service_key)
    return _client


async def health_check_db() -> bool:
    """Ping Supabase to verify connection"""
    try:
        client = get_supabase()
        client.table("memories").select("id").limit(1).execute()
        return True
    except Exception as e:
        logger.warning(f"Supabase health check failed: {e}")
        return False


# ── Memory CRUD ───────────────────────────────────────────────────────────────

async def save_memory(payload: MemoryCreate) -> dict:
    """Insert a new memory into Supabase"""
    client = get_supabase()

    record = {
        "id": str(uuid.uuid4()),
        "content": payload.content,
        "source": payload.source,
        "user_id": payload.user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "injected": False,
    }

    response = client.table("memories").insert(record).execute()

    if not response.data:
        raise RuntimeError("Failed to insert memory into Supabase")

    saved = response.data[0]
    logger.info(f"Memory saved: {saved['id']} from {saved['source']}")
    return saved


async def get_memories(
    user_id: str | None = None,
    source: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Retrieve memories with optional filters"""
    client = get_supabase()

    query = client.table("memories").select("*")

    if user_id:
        query = query.eq("user_id", user_id)
    if source:
        query = query.eq("source", source)

    query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
    response = query.execute()

    return response.data or []


async def delete_memory(memory_id: str) -> bool:
    """Delete a memory by ID"""
    client = get_supabase()
    response = client.table("memories").delete().eq("id", memory_id).execute()
    return bool(response.data)


async def get_memory_count(user_id: str | None = None) -> int:
    """Count memories for a user"""
    client = get_supabase()
    query = client.table("memories").select("id", count="exact")
    if user_id:
        query = query.eq("user_id", user_id)
    response = query.execute()
    return response.count or 0
