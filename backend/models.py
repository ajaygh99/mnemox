# models.py — Mnemox Pydantic Models (request/response schemas)

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Memory Models ─────────────────────────────────────────────────────────────

class MemoryCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    source: str = Field(..., pattern="^(chatgpt|claude|gemini|copilot)$")
    user_id: Optional[str] = None


class Memory(BaseModel):
    id: str
    content: str
    source: str
    user_id: Optional[str] = None
    created_at: datetime
    injected: bool = False

    class Config:
        from_attributes = True


class MemoryResponse(BaseModel):
    success: bool
    id: str
    message: str = "Memory saved"


class MemoriesListResponse(BaseModel):
    success: bool
    memories: list[Memory]
    total: int


# ── Search Models (Step 4) ────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    user_id: Optional[str] = None
    source: Optional[str] = None
    limit: int = Field(10, ge=1, le=50)
    score_threshold: float = Field(0.65, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    memory_id: str
    score: float
    source: str
    content_preview: str
    created_at: str


class SearchResponse(BaseModel):
    success: bool
    query: str
    results: list[SearchResult]


# ── Health Model ──────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    supabase_connected: bool
    qdrant_connected: bool = False
