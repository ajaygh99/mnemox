"""
Step 8 Tests — End-to-End API Integration + Launch Readiness
Run: python -m pytest tests/step8/ -v

These tests exercise actual FastAPI routes via TestClient (real HTTP, in-process).
They use mocked external services (Supabase, Qdrant, OpenAI) via monkeypatching
so they run offline without any real credentials.
"""

import os
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

# Make sure backend is on path
BACKEND = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
sys.path.insert(0, BACKEND)


# ── Shared mock data ──────────────────────────────────────────────────────────

FAKE_MEMORY = {
    "id": "abc-123",
    "content": "I prefer concise Python code with type hints",
    "source": "claude",
    "user_id": "user-test-001",
    "created_at": datetime.utcnow(),
    "injected": False,
}

FAKE_SEARCH_RESULTS = [
    {
        "memory_id": "abc-123",
        "score": 0.89,
        "source": "claude",
        "content_preview": "I prefer concise Python code with type hints",
        "created_at": "2025-01-01T00:00:00",
    }
]


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_db(monkeypatch):
    """Patch all database calls"""
    monkeypatch.setattr("database.save_memory", AsyncMock(return_value=FAKE_MEMORY))
    monkeypatch.setattr("database.get_memories", AsyncMock(return_value=[FAKE_MEMORY]))
    monkeypatch.setattr("database.delete_memory", AsyncMock(return_value=True))
    monkeypatch.setattr("database.get_memory_count", AsyncMock(return_value=3))
    monkeypatch.setattr("database.health_check_db", AsyncMock(return_value=True))


@pytest.fixture
def mock_vectors(monkeypatch):
    """Patch vector store + embedding calls"""
    monkeypatch.setattr("embeddings.embed_text", AsyncMock(return_value=[0.1] * 1536))
    monkeypatch.setattr("vector_store.ensure_collection", AsyncMock())
    monkeypatch.setattr("vector_store.upsert_memory_vector", AsyncMock())
    monkeypatch.setattr("vector_store.search_similar_memories", AsyncMock(return_value=FAKE_SEARCH_RESULTS))
    monkeypatch.setattr("vector_store.delete_memory_vector", AsyncMock())
    monkeypatch.setattr("vector_store.health_check_vector", AsyncMock(return_value=True))


@pytest.fixture
def client(mock_db, mock_vectors):
    """FastAPI test client with all external services mocked"""
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)


DEV_HEADERS = {"X-API-Key": "dev-api-key-change-in-production"}

# JWT for a free-plan user (signed with dev secret)
import jwt as pyjwt
JWT_SECRET = "super-secret-jwt-key-for-dev-only-32chars!"

def make_jwt(user_id="u1", email="test@mnemox.app", plan="pro", team_id=None):
    app_meta = {"plan": plan}
    if team_id:
        app_meta["team_id"] = team_id
    return pyjwt.encode(
        {"sub": user_id, "email": email, "app_metadata": app_meta},
        JWT_SECRET, algorithm="HS256"
    )

def jwt_headers(plan="pro", team_id=None):
    token = make_jwt(plan=plan, team_id=team_id)
    return {"Authorization": f"Bearer {token}"}


# ── Health endpoint ───────────────────────────────────────────────────────────

def test_health_returns_200(client):
    r = client.get("/health")
    assert r.status_code == 200

def test_health_has_version(client):
    r = client.get("/health")
    assert r.json()["version"] == "0.7.0"

def test_health_reports_supabase_ok(client):
    r = client.get("/health")
    assert r.json()["supabase_connected"] is True

def test_health_reports_qdrant_ok(client):
    r = client.get("/health")
    assert r.json()["qdrant_connected"] is True

def test_health_status_ok_when_both_up(client):
    r = client.get("/health")
    assert r.json()["status"] == "ok"


# ── Auth: /auth/me ────────────────────────────────────────────────────────────

def test_auth_me_requires_auth(client):
    r = client.get("/auth/me")
    assert r.status_code == 401

def test_auth_me_with_jwt(client):
    r = client.get("/auth/me", headers=jwt_headers())
    assert r.status_code == 200

def test_auth_me_returns_user_fields(client):
    r = client.get("/auth/me", headers=jwt_headers())
    data = r.json()
    assert "user_id" in data
    assert "email" in data
    assert "plan" in data
    assert "memory_limit" in data

def test_auth_me_with_legacy_key(client):
    r = client.get("/auth/me", headers=DEV_HEADERS)
    assert r.status_code == 200
    assert r.json()["plan"] == "pro"

def test_auth_me_free_plan_limit_50(client):
    r = client.get("/auth/me", headers=jwt_headers(plan="free"))
    assert r.json()["memory_limit"] == 50

def test_auth_me_pro_plan_unlimited(client):
    r = client.get("/auth/me", headers=jwt_headers(plan="pro"))
    assert r.json()["memory_limit"] > 1000


# ── POST /memories ────────────────────────────────────────────────────────────

def test_create_memory_requires_auth(client):
    r = client.post("/memories", json={"content": "test", "source": "claude"})
    assert r.status_code == 401

def test_create_memory_success(client):
    r = client.post("/memories",
        headers=DEV_HEADERS,
        json={"content": "I prefer dark mode always", "source": "claude"})
    assert r.status_code == 200
    assert r.json()["success"] is True
    assert "id" in r.json()

def test_create_memory_rejects_invalid_source(client):
    r = client.post("/memories",
        headers=DEV_HEADERS,
        json={"content": "test prompt", "source": "twitter"})
    assert r.status_code == 422

def test_create_memory_rejects_empty_content(client):
    r = client.post("/memories",
        headers=DEV_HEADERS,
        json={"content": "", "source": "chatgpt"})
    assert r.status_code == 422

def test_create_memory_all_sources_accepted(client):
    for source in ("chatgpt", "claude", "gemini", "copilot"):
        r = client.post("/memories",
            headers=DEV_HEADERS,
            json={"content": f"test from {source}", "source": source})
        assert r.status_code == 200, f"Failed for source: {source}"

def test_free_plan_limit_returns_402(client, monkeypatch):
    monkeypatch.setattr("main.get_memory_count", AsyncMock(return_value=50))
    r = client.post("/memories",
        headers=jwt_headers(plan="free"),
        json={"content": "over limit", "source": "claude"})
    assert r.status_code == 402

def test_pro_plan_no_limit(client, monkeypatch):
    monkeypatch.setattr("main.get_memory_count", AsyncMock(return_value=50))
    r = client.post("/memories",
        headers=jwt_headers(plan="pro"),
        json={"content": "unlimited", "source": "claude"})
    assert r.status_code == 200


# ── GET /memories ─────────────────────────────────────────────────────────────

def test_list_memories_requires_auth(client):
    r = client.get("/memories")
    assert r.status_code == 401

def test_list_memories_success(client):
    r = client.get("/memories", headers=DEV_HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert isinstance(data["memories"], list)
    assert "total" in data

def test_list_memories_source_filter_validates(client):
    r = client.get("/memories?source=invalid", headers=DEV_HEADERS)
    assert r.status_code == 422

def test_list_memories_valid_source_filter(client):
    r = client.get("/memories?source=claude", headers=DEV_HEADERS)
    assert r.status_code == 200

def test_list_memories_pagination(client):
    r = client.get("/memories?limit=10&offset=0", headers=DEV_HEADERS)
    assert r.status_code == 200


# ── POST /memories/search ─────────────────────────────────────────────────────

def test_search_requires_auth(client):
    r = client.post("/memories/search", json={"query": "python"})
    assert r.status_code == 401

def test_search_returns_results(client):
    r = client.post("/memories/search",
        headers=DEV_HEADERS,
        json={"query": "python code style"})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert isinstance(data["results"], list)
    assert data["query"] == "python code style"

def test_search_result_has_required_fields(client):
    r = client.post("/memories/search",
        headers=DEV_HEADERS,
        json={"query": "test"})
    result = r.json()["results"][0]
    assert "memory_id" in result
    assert "score" in result
    assert "content_preview" in result
    assert "source" in result

def test_search_score_threshold_respected(client):
    r = client.post("/memories/search",
        headers=DEV_HEADERS,
        json={"query": "test", "score_threshold": 0.9, "limit": 5})
    assert r.status_code == 200

def test_search_empty_query_rejected(client):
    r = client.post("/memories/search",
        headers=DEV_HEADERS,
        json={"query": ""})
    assert r.status_code == 422


# ── DELETE /memories/{id} ─────────────────────────────────────────────────────

def test_delete_memory_requires_auth(client):
    r = client.delete("/memories/abc-123")
    assert r.status_code == 401

def test_delete_memory_success(client):
    r = client.delete("/memories/abc-123", headers=DEV_HEADERS)
    assert r.status_code == 200
    assert r.json()["success"] is True

def test_delete_nonexistent_returns_404(client, monkeypatch):
    monkeypatch.setattr("main.delete_memory", AsyncMock(return_value=False))
    r = client.delete("/memories/ghost-id", headers=DEV_HEADERS)
    assert r.status_code == 404


# ── Billing endpoints ─────────────────────────────────────────────────────────

def test_billing_plans_requires_auth(client):
    r = client.get("/billing/plans")
    assert r.status_code == 401

def test_billing_plans_returns_three_plans(client):
    r = client.get("/billing/plans", headers=DEV_HEADERS)
    assert r.status_code == 200
    plans = r.json()["plans"]
    assert "free" in plans
    assert "pro" in plans
    assert "team" in plans

def test_billing_plans_shows_current(client):
    r = client.get("/billing/plans", headers=DEV_HEADERS)
    assert "current_plan" in r.json()

def test_billing_checkout_rejects_free_plan(client):
    r = client.post("/billing/checkout",
        headers=DEV_HEADERS,
        json={"plan": "free", "success_url": "http://x.com", "cancel_url": "http://x.com"})
    assert r.status_code == 422  # free not in pattern ^(pro|team)$

def test_billing_checkout_valid_plan(client, monkeypatch):
    monkeypatch.setattr("main.create_checkout_session",
        AsyncMock(return_value="https://checkout.stripe.com/test"))
    r = client.post("/billing/checkout",
        headers=DEV_HEADERS,
        json={"plan": "pro", "success_url": "http://x.com/ok", "cancel_url": "http://x.com/cancel"})
    assert r.status_code == 200
    assert r.json()["url"].startswith("https://")


# ── Team endpoints ────────────────────────────────────────────────────────────

def test_team_requires_team_plan(client):
    r = client.get("/team", headers=jwt_headers(plan="free"))
    assert r.status_code == 403

def test_team_pro_plan_forbidden(client):
    r = client.get("/team", headers=jwt_headers(plan="pro"))
    assert r.status_code == 403

def test_team_invite_requires_team_plan(client):
    r = client.post("/team/invite",
        headers=jwt_headers(plan="pro"),
        json={"email": "friend@example.com"})
    assert r.status_code == 403

def test_team_invite_valid_email(client):
    r = client.post("/team/invite",
        headers=jwt_headers(plan="team", team_id="team-001"),
        json={"email": "friend@example.com"})
    assert r.status_code == 200

def test_team_invite_invalid_email(client):
    r = client.post("/team/invite",
        headers=jwt_headers(plan="team", team_id="team-001"),
        json={"email": "not-an-email"})
    assert r.status_code == 422


# ── Team memory namespace ─────────────────────────────────────────────────────

def test_team_members_share_namespace(client):
    """Two team members with same team_id should query same namespace"""
    from auth import CurrentUser
    u1 = CurrentUser("user-1", "a@x.com", plan="team", team_id="team-abc")
    u2 = CurrentUser("user-2", "b@x.com", plan="team", team_id="team-abc")
    assert u1.memory_namespace == u2.memory_namespace == "team:team-abc"

def test_solo_user_namespace_is_user_id():
    from auth import CurrentUser
    u = CurrentUser("user-solo", "c@x.com", plan="pro")
    assert u.memory_namespace == "user-solo"

def test_free_user_namespace_is_user_id():
    from auth import CurrentUser
    u = CurrentUser("user-free", "d@x.com", plan="free")
    assert u.memory_namespace == "user-free"


# ── Auth edge cases ───────────────────────────────────────────────────────────

def test_expired_jwt_rejected(client):
    import time
    token = pyjwt.encode(
        {"sub": "u1", "email": "x@x.com", "app_metadata": {"plan": "pro"},
         "exp": int(time.time()) - 3600},  # expired 1 hour ago
        JWT_SECRET, algorithm="HS256"
    )
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401

def test_wrong_secret_jwt_rejected(client):
    token = pyjwt.encode(
        {"sub": "u1", "email": "x@x.com", "app_metadata": {"plan": "pro"}},
        "wrong-secret", algorithm="HS256"
    )
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401

def test_no_auth_header_rejected(client):
    r = client.get("/auth/me")
    assert r.status_code == 401

def test_wrong_api_key_rejected(client):
    r = client.get("/auth/me", headers={"X-API-Key": "wrong-key"})
    assert r.status_code == 401
