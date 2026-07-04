# models.py — Mnemox Pydantic Models (Step 7: + auth/billing models)

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ── Memory Models ─────────────────────────────────────────────────────────────

class MemoryCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    source: str = Field(..., pattern="^(chatgpt|claude|gemini|copilot|perplexity|grok|copilot_ms)$")
    user_id: Optional[str] = None
    trust_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class Memory(BaseModel):
    id: str
    content: str
    source: str
    user_id: Optional[str] = None
    created_at: datetime
    injected: bool = False
    trust_score: Optional[float] = None  # AI Response Quality Score (0.0-1.0). None = not yet scored.

    class Config:
        from_attributes = True


# ── Trace Models (MnemoxTrace -- AI Interaction Log) ──────────────────────────

class TraceCreate(BaseModel):
    tool_name: str = Field(..., pattern="^(chatgpt|claude|gemini|copilot|perplexity|grok)$")
    prompt_text: str = Field(..., min_length=1, max_length=10000)
    response_text: Optional[str] = Field(None, max_length=20000)
    prompt_score: Optional[int] = Field(None, ge=0, le=100)
    prompt_grade: Optional[str] = None
    trust_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    token_count: Optional[int] = None
    session_id: Optional[str] = None
    mnemox_uuid: Optional[str] = None


class TraceResponse(BaseModel):
    success: bool
    id: str
    message: str = "Interaction logged"


class TraceRecord(BaseModel):
    id: str
    user_id: Optional[str]
    tool_name: str
    prompt_text: str
    response_text: Optional[str]
    prompt_score: Optional[int]
    prompt_grade: Optional[str]
    trust_score: Optional[float]
    token_count: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class TracesListResponse(BaseModel):
    success: bool
    traces: List[TraceRecord]
    total: int


class MemoryResponse(BaseModel):
    success: bool
    id: str
    message: str = "Memory saved"


class MemoriesListResponse(BaseModel):
    success: bool
    memories: list[Memory]
    total: int


# ── Search Models ─────────────────────────────────────────────────────────────

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


# ── Auth Models (Step 7) ──────────────────────────────────────────────────────

class UserProfile(BaseModel):
    user_id: str
    email: str
    plan: str                       # "free" | "pro" | "team"
    team_id: Optional[str] = None
    memory_limit: int
    memory_count: int = 0


# ── Billing Models (Step 7) ───────────────────────────────────────────────────

class CheckoutRequest(BaseModel):
    plan: str = Field(..., pattern="^(pro|team)$")
    success_url: str
    cancel_url: str
    team_id: Optional[str] = None


class CheckoutResponse(BaseModel):
    url: str


class BillingPortalRequest(BaseModel):
    return_url: str


class BillingPortalResponse(BaseModel):
    url: str


class PlanInfo(BaseModel):
    name: str
    price_id: Optional[str]
    memory_limit: Optional[int]
    features: List[str]


class PlansResponse(BaseModel):
    plans: dict[str, PlanInfo]
    current_plan: str


# ── Team Models (Step 7) ──────────────────────────────────────────────────────

class TeamInvite(BaseModel):
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")


class TeamMember(BaseModel):
    user_id: str
    email: str
    joined_at: str


class TeamResponse(BaseModel):
    team_id: str
    members: List[TeamMember]
    memory_namespace: str


# ── Health Model ──────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    supabase_connected: bool
    qdrant_connected: bool = False
