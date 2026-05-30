# main.py — Mnemox FastAPI Backend
# Step 4: + Vector embeddings, semantic search, Qdrant integration

from fastapi import FastAPI, HTTPException, Header, Query, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import get_settings
from models import (
    MemoryCreate, MemoryResponse, MemoriesListResponse,
    Memory, HealthResponse, SearchRequest, SearchResponse
)
from database import save_memory, get_memories, delete_memory, get_memory_count, health_check_db
from embeddings import embed_text
from vector_store import (
    ensure_collection, upsert_memory_vector,
    search_similar_memories, delete_memory_vector, health_check_vector
)

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("mnemox")

# ── App setup ─────────────────────────────────────────────────────────────────
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Mnemox API starting — env: {settings.app_env}")
    await ensure_collection()   # create Qdrant collection if not exists
    yield
    logger.info("Mnemox API shutting down")

app = FastAPI(
    title="Mnemox API",
    description="Universal AI Memory Layer — Backend",
    version="0.3.0",
    lifespan=lifespan,
)

# ── CORS — allow Chrome extension + dashboard ─────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# ── Auth dependency (simple API key for now — replaced with JWT in Step 7) ────
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_secret_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    """Health check — verifies Supabase + Qdrant connectivity"""
    db_ok = await health_check_db()
    vec_ok = await health_check_vector()
    return HealthResponse(
        status="ok" if (db_ok and vec_ok) else "degraded",
        version="0.4.0",
        environment=settings.app_env,
        supabase_connected=db_ok,
        qdrant_connected=vec_ok,
    )


@app.post("/memories", response_model=MemoryResponse, tags=["Memories"])
async def create_memory(
    payload: MemoryCreate,
    _: str = Depends(verify_api_key),
):
    """
    Save a captured prompt as a memory.
    Stores in Supabase (full text) AND Qdrant (vector embedding).
    """
    try:
        # 1. Save text to Supabase
        saved = await save_memory(payload)
        memory_id = saved["id"]

        # 2. Generate embedding + store in Qdrant
        try:
            vector = await embed_text(payload.content)
            await upsert_memory_vector(
                memory_id=memory_id,
                vector=vector,
                payload={
                    "source": payload.source,
                    "user_id": payload.user_id or "",
                    "content": payload.content,
                    "created_at": saved.get("created_at", ""),
                },
            )
        except Exception as embed_err:
            # Embedding failure is non-fatal — memory still saved in Supabase
            logger.warning(f"Embedding failed for {memory_id}: {embed_err}")

        return MemoryResponse(success=True, id=memory_id)
    except Exception as e:
        logger.error(f"Failed to save memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memories/search", response_model=SearchResponse, tags=["Memories"])
async def search_memories(
    payload: SearchRequest,
    _: str = Depends(verify_api_key),
):
    """
    Semantic search — find memories similar to a query.
    Used by Step 5 (injection) to find relevant context for a prompt.
    """
    try:
        query_vector = await embed_text(payload.query)
        results = await search_similar_memories(
            query_vector=query_vector,
            user_id=payload.user_id,
            source=payload.source,
            limit=payload.limit,
            score_threshold=payload.score_threshold,
        )
        return SearchResponse(success=True, results=results, query=payload.query)
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memories", response_model=MemoriesListResponse, tags=["Memories"])
async def list_memories(
    user_id: str | None = Query(None),
    source: str | None = Query(None, pattern="^(chatgpt|claude|gemini|copilot)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: str = Depends(verify_api_key),
):
    """
    Retrieve memories with optional filters.
    Called by the dashboard (Step 6).
    """
    try:
        memories = await get_memories(user_id=user_id, source=source, limit=limit, offset=offset)
        total = await get_memory_count(user_id=user_id)
        return MemoriesListResponse(
            success=True,
            memories=[Memory(**m) for m in memories],
            total=total,
        )
    except Exception as e:
        logger.error(f"Failed to list memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/memories/{memory_id}", tags=["Memories"])
async def remove_memory(
    memory_id: str,
    _: str = Depends(verify_api_key),
):
    """Delete a memory from both Supabase and Qdrant"""
    deleted = await delete_memory(memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    # Also remove vector (non-fatal if it fails)
    try:
        await delete_memory_vector(memory_id)
    except Exception as e:
        logger.warning(f"Vector delete failed for {memory_id}: {e}")
    return {"success": True, "id": memory_id}


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.app_port, reload=True)
