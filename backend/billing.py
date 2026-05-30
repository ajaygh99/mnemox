# billing.py — Mnemox Stripe Billing Integration
# Step 7: Plans, checkout, webhook handler, customer management

import logging
import stripe
from typing import Optional

from config import get_settings

logger = logging.getLogger("mnemox.billing")
settings = get_settings()

stripe.api_key = settings.stripe_secret_key

# ── Plan definitions ─────────────────────────────────────────────────────────

PLANS = {
    "free": {
        "name": "Free",
        "price_id": None,
        "memory_limit": 50,
        "features": ["50 memories", "Single user", "All AI platforms"],
    },
    "pro": {
        "name": "Pro",
        "price_id": settings.stripe_pro_price_id,
        "memory_limit": None,   # unlimited
        "features": ["Unlimited memories", "Semantic search", "Priority support"],
    },
    "team": {
        "name": "Team",
        "price_id": settings.stripe_team_price_id,
        "memory_limit": None,   # unlimited
        "features": ["Everything in Pro", "Shared team vault", "Up to 10 members", "Admin controls"],
    },
}


# ── Customer management ──────────────────────────────────────────────────────

async def get_or_create_customer(user_id: str, email: str) -> str:
    """Find existing Stripe customer by metadata or create new"""
    existing = stripe.Customer.search(
        query=f'metadata["user_id"]:"{user_id}"',
        limit=1,
    )
    if existing.data:
        return existing.data[0].id

    customer = stripe.Customer.create(
        email=email,
        metadata={"user_id": user_id},
    )
    logger.info(f"Created Stripe customer {customer.id} for user {user_id}")
    return customer.id


async def create_checkout_session(
    user_id: str,
    email: str,
    plan: str,
    success_url: str,
    cancel_url: str,
    team_id: Optional[str] = None,
) -> str:
    """Create a Stripe Checkout Session and return the URL"""
    price_id = PLANS[plan]["price_id"]
    if not price_id:
        raise ValueError(f"Plan '{plan}' has no price ID (it's free)")

    customer_id = await get_or_create_customer(user_id, email)

    metadata = {"user_id": user_id, "plan": plan}
    if team_id:
        metadata["team_id"] = team_id

    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata,
        subscription_data={"metadata": metadata},
    )
    return session.url


async def create_billing_portal_session(user_id: str, email: str, return_url: str) -> str:
    """Create a Stripe Billing Portal session for managing subscription"""
    customer_id = await get_or_create_customer(user_id, email)
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session.url


# ── Webhook handler ──────────────────────────────────────────────────────────

async def handle_stripe_webhook(payload: bytes, sig_header: str) -> dict:
    """
    Verify and process Stripe webhook events.
    Updates Supabase user metadata to reflect new plan.
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Stripe webhook signature invalid: {e}")
        raise ValueError("Invalid signature")

    event_type = event["type"]
    logger.info(f"Stripe event: {event_type}")

    if event_type in ("customer.subscription.created", "customer.subscription.updated"):
        sub = event["data"]["object"]
        plan = sub.get("metadata", {}).get("plan", "pro")
        team_id = sub.get("metadata", {}).get("team_id")
        user_id = sub.get("metadata", {}).get("user_id")
        status = sub.get("status")

        if user_id and status in ("active", "trialing"):
            await _update_user_plan(user_id, plan, team_id)

    elif event_type == "customer.subscription.deleted":
        sub = event["data"]["object"]
        user_id = sub.get("metadata", {}).get("user_id")
        if user_id:
            await _update_user_plan(user_id, "free", None)

    return {"received": True, "type": event_type}


async def _update_user_plan(user_id: str, plan: str, team_id: Optional[str]):
    """Update user's plan in Supabase via admin API"""
    from database import get_supabase
    client = get_supabase()

    app_metadata = {"plan": plan}
    if team_id:
        app_metadata["team_id"] = team_id
    elif plan != "team":
        app_metadata["team_id"] = None

    try:
        # Update via Supabase admin API
        client.auth.admin.update_user_by_id(
            user_id,
            {"app_metadata": app_metadata},
        )
        logger.info(f"Updated user {user_id} → plan={plan}, team={team_id}")
    except Exception as e:
        logger.error(f"Failed to update user plan: {e}")
