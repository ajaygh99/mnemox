-- ============================================================
-- MNEMOX — Supabase Schema
-- Run this in Supabase > SQL Editor > New Query
-- ============================================================

-- Memories table
CREATE TABLE IF NOT EXISTS memories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content     TEXT NOT NULL,
    source      TEXT NOT NULL CHECK (source IN ('chatgpt', 'claude', 'gemini', 'copilot')),
    user_id     UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    injected    BOOLEAN DEFAULT FALSE
);

-- Index for fast user queries
CREATE INDEX IF NOT EXISTS idx_memories_user_id ON memories(user_id);
CREATE INDEX IF NOT EXISTS idx_memories_source  ON memories(source);
CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at DESC);

-- Row Level Security (RLS) — each user sees only their own memories
ALTER TABLE memories ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users see own memories" ON memories
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users insert own memories" ON memories
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users delete own memories" ON memories
    FOR DELETE USING (auth.uid() = user_id);

-- Service role bypass (backend uses service key — bypasses RLS)
-- No extra policy needed; service key bypasses RLS by default.

-- Verify setup
SELECT 'Schema created successfully' AS status;
