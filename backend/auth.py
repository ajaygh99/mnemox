# auth.py — Mnemox JWT Authentication
# Step 7: Verifies Supabase JWTs + legacy API key for backwards compatibility

import logging
from typing import Optional
from fastapi import HTTPException, Header, Depends
import jwt
from jwt.exceptions import InvalidTokenError

from config import get_settings

logger = logging.getLogger("mnemox.auth")
settings = get_settings()

# ── JWT Verification ─────────────────────────────────────────────────────────

def decode_supabase_jwt(token: str) -> dict:
    """
    Decode and verify a Supabase JWT.
    Supabase uses HS256 with the JWT secret from project settings.
    """
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},  # Supabase doesn't set standard aud
        )
        return payload
    except InvalidTokenError as e:
        logger.warning(f"JWT decode failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ── Current User Dependency ──────────────────────────────────────────────────

class CurrentUser:
    def __init__(self, user_id: str, email: str, plan: str = "free", team_id: Optional[str] = None):
        self.user_id = user_id
        self.email = email
        self.plan = plan           # "free" | "pro" | "team"
        self.team_id = team_id     # set for team plan members

    @property
    def memory_namespace(self) -> str:
        """Returns the effective user_id for memory storage.
        Team members share a namespace: team:{team_id}"""
        if self.plan == "team" and self.team_id:
            return f"team:{self.team_id}"
        return self.user_id

    @property
    def memory_limit(self) -> int:
        """Memory limit by plan"""
        if self.plan == "free":
            return 50
        return 999_999  # Pro + Team: unlimited


async def get_current_user(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None),
) -> CurrentUser:
    """
    FastAPI dependency — resolves the current user from:
    1. Bearer JWT (Supabase auth)
    2. Legacy X-API-Key (for backwards compat / dev)
    """
    # ── Bearer token (primary) ─────────────────────────────────────────────
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        payload = decode_supabase_jwt(token)

        user_id = payload.get("sub")
        email = payload.get("email", "")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token missing user ID")

        # Read plan + team from app_metadata (set by Stripe webhook)
        app_meta = payload.get("app_metadata", {})
        plan = app_meta.get("plan", "free")
        team_id = app_meta.get("team_id")

        return CurrentUser(user_id=user_id, email=email, plan=plan, team_id=team_id)

    # ── Legacy API key (dev / backwards compat) ────────────────────────────
    if x_api_key and x_api_key == settings.api_secret_key:
        return CurrentUser(
            user_id="dev",
            email="dev@mnemox.local",
            plan="pro",  # legacy key gets pro access
        )

    raise HTTPException(
        status_code=401,
        detail="Authentication required — provide Bearer token or X-API-Key",
    )


# ── Plan enforcement ─────────────────────────────────────────────────────────

def require_plan(min_plan: str):
    """Dependency factory — enforces minimum plan level"""
    plan_order = {"free": 0, "pro": 1, "team": 2}

    async def check(user: CurrentUser = Depends(get_current_user)):
        if plan_order.get(user.plan, 0) < plan_order.get(min_plan, 0):
            raise HTTPException(
                status_code=403,
                detail=f"This feature requires {min_plan} plan. Current: {user.plan}",
            )
        return user

    return check
