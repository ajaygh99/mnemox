-- ─────────────────────────────────────────────────────────────────────────────
-- Mnemox Step 7 — Auth + Billing schema additions
-- Run in Supabase SQL editor AFTER supabase_schema.sql
-- ─────────────────────────────────────────────────────────────────────────────

-- ── Teams table ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS teams (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    owner_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ── Team members ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS team_members (
    team_id    UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    joined_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (team_id, user_id)
);

-- ── Billing subscriptions ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS subscriptions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    stripe_customer_id  TEXT,
    stripe_sub_id       TEXT,
    plan                TEXT NOT NULL DEFAULT 'free'
                            CHECK (plan IN ('free', 'pro', 'team')),
    status              TEXT NOT NULL DEFAULT 'active',
    team_id             UUID REFERENCES teams(id),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS subscriptions_user_id_idx ON subscriptions(user_id);

-- ── Update memories table: support team namespace ─────────────────────────────
-- user_id column already exists; team namespace stored as 'team:{uuid}' string
-- No schema change needed — user_id is TEXT so it handles 'team:uuid' values

-- ── RLS for teams ─────────────────────────────────────────────────────────────
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Team owners can manage" ON teams
    FOR ALL USING (auth.uid() = owner_id);

ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Members can view their team" ON team_members
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Owners can manage members" ON team_members
    FOR ALL USING (
        EXISTS (SELECT 1 FROM teams WHERE id = team_id AND owner_id = auth.uid())
    );

ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own subscription" ON subscriptions
    FOR SELECT USING (auth.uid() = user_id);

-- ── Indexes ───────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS team_members_user_idx ON team_members(user_id);
CREATE INDEX IF NOT EXISTS subscriptions_stripe_idx ON subscriptions(stripe_customer_id);
