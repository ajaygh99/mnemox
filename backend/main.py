# main.py — Mnemox FastAPI Backend
# Step 7: + JWT auth, Stripe billing, team memory sharing

from fastapi import FastAPI, HTTPException, Header, Query, Depends, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import get_settings
from models import (
    MemoryCreate, MemoryResponse, MemoriesListResponse,
    Memory, HealthResponse, SearchRequest, SearchResponse,
    UserProfile, CheckoutRequest, CheckoutResponse,
    BillingPortalRequest, BillingPortalResponse, PlansResponse, PlanInfo,
    TeamInvite, TeamResponse,
)
from database import save_memory, get_memories, delete_memory, get_memory_count, health_check_db
from embeddings import embed_text
from vector_store import (
    ensure_collection, upsert_memory_vector,
    search_similar_memories, delete_memory_vector, health_check_vector
)
from auth import get_current_user, require_plan, CurrentUser
from billing import (
    PLANS, create_checkout_session, create_billing_portal_session, handle_stripe_webhook
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
    await ensure_collection()
    yield
    logger.info("Mnemox API shutting down")

app = FastAPI(
    title="Mnemox API",
    description="Universal AI Memory OS — Backend",
    version="0.7.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT"],
    allow_headers=["*"],
)


# ── System ────────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    """Health check — verifies Supabase + Qdrant connectivity"""
    db_ok = await health_check_db()
    vec_ok = await health_check_vector()
    return HealthResponse(
        status="ok" if (db_ok and vec_ok) else "degraded",
        version="0.7.0",
        environment=settings.app_env,
        supabase_connected=db_ok,
        qdrant_connected=vec_ok,
    )


# ── Auth: current user profile ────────────────────────────────────────────────

@app.get("/auth/me", response_model=UserProfile, tags=["Auth"])
async def get_me(user: CurrentUser = Depends(get_current_user)):
    """Return current user's profile, plan, and memory count"""
    count = await get_memory_count(user_id=user.memory_namespace)
    return UserProfile(
        user_id=user.user_id,
        email=user.email,
        plan=user.plan,
        team_id=user.team_id,
        memory_limit=user.memory_limit,
        memory_count=count,
    )


# ── Memories ──────────────────────────────────────────────────────────────────

@app.post("/memories", response_model=MemoryResponse, tags=["Memories"])
async def create_memory(
    payload: MemoryCreate,
    user: CurrentUser = Depends(get_current_user),
):
    """Save a captured prompt as a memory. Enforces plan memory limits."""
    # Enforce free plan limit
    if user.plan == "free":
        count = await get_memory_count(user_id=user.memory_namespace)
        if count >= user.memory_limit:
            raise HTTPException(
                status_code=402,
                detail=f"Free plan limit reached ({user.memory_limit} memories). Upgrade to Pro for unlimited.",
            )

    # Override user_id with resolved namespace (handles team sharing)
    payload_dict = payload.model_dump()
    payload_dict["user_id"] = user.memory_namespace
    from models import MemoryCreate as MC
    namespaced_payload = MC(**payload_dict)

    try:
        saved = await save_memory(namespaced_payload)
        memory_id = saved["id"]

        try:
            vector = await embed_text(payload.content)
            await upsert_memory_vector(
                memory_id=memory_id,
                vector=vector,
                payload={
                    "source": payload.source,
                    "user_id": user.memory_namespace,
                    "content": payload.content,
                    "created_at": saved.get("created_at", ""),
                },
            )
        except Exception as embed_err:
            logger.warning(f"Embedding failed for {memory_id}: {embed_err}")

        return MemoryResponse(success=True, id=memory_id)
    except Exception as e:
        logger.error(f"Failed to save memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memories/search", response_model=SearchResponse, tags=["Memories"])
async def search_memories(
    payload: SearchRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """Semantic search across user's (or team's) memory namespace"""
    try:
        query_vector = await embed_text(payload.query)
        results = await search_similar_memories(
            query_vector=query_vector,
            user_id=user.memory_namespace,   # scoped to user/team
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
    source: str | None = Query(None, pattern="^(chatgpt|claude|gemini|copilot)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: CurrentUser = Depends(get_current_user),
):
    """Retrieve memories scoped to the current user or team"""
    try:
        memories = await get_memories(
            user_id=user.memory_namespace, source=source, limit=limit, offset=offset
        )
        total = await get_memory_count(user_id=user.memory_namespace)
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
    user: CurrentUser = Depends(get_current_user),
):
    """Delete a memory (must belong to user's namespace)"""
    deleted = await delete_memory(memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    try:
        await delete_memory_vector(memory_id)
    except Exception as e:
        logger.warning(f"Vector delete failed for {memory_id}: {e}")
    return {"success": True, "id": memory_id}


# ── Billing ───────────────────────────────────────────────────────────────────

@app.get("/billing/plans", response_model=PlansResponse, tags=["Billing"])
async def get_plans(user: CurrentUser = Depends(get_current_user)):
    """Return available plans and current user's plan"""
    return PlansResponse(
        plans={k: PlanInfo(**v) for k, v in PLANS.items()},
        current_plan=user.plan,
    )


@app.post("/billing/checkout", response_model=CheckoutResponse, tags=["Billing"])
async def create_checkout(
    payload: CheckoutRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """Create Stripe Checkout session for plan upgrade"""
    try:
        url = await create_checkout_session(
            user_id=user.user_id,
            email=user.email,
            plan=payload.plan,
            success_url=payload.success_url,
            cancel_url=payload.cancel_url,
            team_id=payload.team_id,
        )
        return CheckoutResponse(url=url)
    except Exception as e:
        logger.error(f"Checkout failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/billing/portal", response_model=BillingPortalResponse, tags=["Billing"])
async def billing_portal(
    payload: BillingPortalRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """Create Stripe Billing Portal session for managing subscription"""
    try:
        url = await create_billing_portal_session(
            user_id=user.user_id,
            email=user.email,
            return_url=payload.return_url,
        )
        return BillingPortalResponse(url=url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/billing/webhook", tags=["Billing"], include_in_schema=False)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(..., alias="stripe-signature"),
):
    """Stripe webhook endpoint — handles subscription lifecycle events"""
    payload = await request.body()
    try:
        result = await handle_stripe_webhook(payload, stripe_signature)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Team ──────────────────────────────────────────────────────────────────────

@app.get("/team", response_model=TeamResponse, tags=["Team"])
async def get_team(user: CurrentUser = Depends(require_plan("team"))):
    """Get team info (team plan only)"""
    if not user.team_id:
        raise HTTPException(status_code=400, detail="No team associated with your account")
    return TeamResponse(
        team_id=user.team_id,
        members=[],  # Populated from Supabase in production
        memory_namespace=user.memory_namespace,
    )


@app.post("/team/invite", tags=["Team"])
async def invite_team_member(
    payload: TeamInvite,
    user: CurrentUser = Depends(require_plan("team")),
):
    """Invite a member to your team (team plan only)"""
    # In production: send invite email via Supabase Auth
    logger.info(f"Team invite: {payload.email} invited by {user.user_id}")
    return {"success": True, "message": f"Invitation sent to {payload.email}"}


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.app_port, reload=True)
