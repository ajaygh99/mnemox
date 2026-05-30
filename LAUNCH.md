# Mnemox — Launch Playbook

## ProductHunt Launch

### Tagline (60 chars max)
> Your AI memory, everywhere — ChatGPT, Claude, Gemini, Copilot

### Short description (260 chars)
> Mnemox is a Chrome extension that gives all your AI tools a shared long-term memory. It silently captures your prompts, embeds them as vectors, and automatically injects the most relevant context before you hit send — on any AI platform.

### Full description

**Stop repeating yourself to every AI.**

You've already told ChatGPT your tech stack. You've explained your writing style to Claude. You've described your project to Gemini. Tomorrow you'll do it all again.

**Mnemox fixes this.**

Install the extension once. It works silently across ChatGPT, Claude, Gemini, and Microsoft Copilot. Every prompt you send becomes a memory. The next time you open any of these tools, Mnemox finds your most relevant past context and prepends it — automatically, before you hit Send.

**The result:** AI tools that feel like they've known you for months, from the first message.

---

**How it works:**
1. 🔵 **Capture** — Your prompts are saved as memories in your private vault
2. 🟣 **Search** — OpenAI vector embeddings find semantically similar past context
3. 🟢 **Inject** — Relevant memories are prepended to your next prompt silently

**Key features:**
- Works on ChatGPT, Claude, Gemini, and Microsoft Copilot
- Semantic vector search (not just keyword matching)
- Zero-friction injection — no extra clicks
- Memory dashboard to browse, search, and delete memories
- Team plan with shared memory vault for whole teams
- Free tier with 50 memories to get started

**Built with:** Chrome MV3, FastAPI, Supabase, OpenAI embeddings, Qdrant vector DB, Stripe

---

**Maker comment (post on launch day):**

Hey PH! 👋 I'm Ajay, maker of Mnemox.

The idea hit me when I realised I'd explained my tech stack to Claude for the 12th time in a month. Every AI tool is brilliant — but they're all amnesiac by default.

Mnemox is the memory layer they're all missing.

I built this in 6 weeks: Chrome extension → FastAPI backend → vector embeddings → auto-injection → dashboard → auth + billing. Every step is fully tested (303 tests).

The free tier is genuinely free. 50 memories, all 4 platforms, no credit card.

Would love your feedback — especially on the injection UX. What gets injected, when, and how visible it is are the hardest design problems here.

AMA! 🧠

---

### Maker questions to ask community
1. Which AI tool do you use most? (ChatGPT / Claude / Gemini / Copilot)
2. What context do you find yourself re-explaining most to AI?
3. Would a shared team memory vault change how your team uses AI?

---

## Chrome Web Store Listing

### Name
Mnemox — AI Memory Layer

### Short description (132 chars)
Universal memory for AI tools. Remembers your context across ChatGPT, Claude, Gemini & Copilot — automatically.

### Detailed description

**Mnemox gives every AI tool a long-term memory.**

Install once. It works on ChatGPT, Claude, Gemini, and Microsoft Copilot — silently capturing your prompts and automatically injecting the most relevant past context before you send each new message.

**WHAT IT DOES**

Every time you type a prompt, Mnemox:
• Saves it as a searchable memory (your private vault)
• Before your next prompt: finds semantically similar memories using AI vector search
• Prepends the top matches as context — so the AI already "knows" your background

**KEY FEATURES**

✓ Works across ChatGPT, Claude, Gemini, and Copilot
✓ Semantic vector search — finds relevant context even with different wording
✓ Auto-injection — zero extra clicks, zero workflow change
✓ Memory dashboard — browse, search, and delete memories
✓ Team plan — share one memory vault across your whole team
✓ Privacy-first — you own your data (self-hostable backend)

**PLANS**

Free: 50 memories · All platforms · Dashboard
Pro ($9/mo): Unlimited memories · Semantic search
Team ($29/mo): Shared vault · Up to 10 members · Admin controls

**PERMISSIONS EXPLAINED**

• Access to chat.openai.com, claude.ai, gemini.google.com, copilot.microsoft.com — to inject and capture prompts on those pages only
• Storage — to save your memories locally as backup
• No access to any other sites

**PRIVACY**

Your memories are stored in your own Supabase database. Mnemox never reads your browser history, never tracks pages outside AI tool domains, and never sells your data.

---

## Social Media Launch Copy

### Twitter/X thread

**Tweet 1 (hook):**
I explained my tech stack to Claude for the 12th time last month.

So I built Mnemox: a Chrome extension that gives ALL your AI tools a shared memory.

Install once → ChatGPT, Claude, Gemini, Copilot all start remembering who you are. 🧠

**Tweet 2 (how it works):**
Here's how it works:

1/ You send a prompt to Claude → Mnemox saves it as a memory

2/ Next time you open ChatGPT → Mnemox finds the 5 most relevant memories using vector search

3/ It quietly prepends them to your prompt BEFORE you hit send

The AI responds like it's known you for months.

**Tweet 3 (team angle):**
The team plan is wild.

One shared memory vault across your whole team.

New hire joins → they start with ALL the context your team has built up over months.

No more "explain our stack to every new AI conversation."

**Tweet 4 (CTA):**
Mnemox is free to start (50 memories, all 4 AI tools, no CC).

Built with: Chrome MV3 · FastAPI · Supabase · OpenAI embeddings · Qdrant

🔗 [Chrome Web Store link]
🔗 [ProductHunt link]

---

### LinkedIn post

**Stop repeating yourself to every AI tool.**

I built something that's been quietly changing how I use AI every day.

**Mnemox** is a Chrome extension that gives ChatGPT, Claude, Gemini, and Copilot a shared long-term memory.

It works like this:
→ You explain your tech stack to Claude on Monday
→ On Tuesday you open ChatGPT
→ Mnemox has already read your relevant memories and prepended them to your prompt — automatically

The AI responds like it's already been briefed. Because it has.

6 weeks to build. 303 tests. Launching today on ProductHunt.

Free tier: 50 memories, all 4 platforms, no credit card.

🔗 [link]

#AI #ProductLaunch #ChromeExtension #BuildInPublic

---

## Launch Day Checklist

### Week before launch
- [ ] Submit to Chrome Web Store (5-7 day review)
- [ ] Create ProductHunt account + set up product page with all assets
- [ ] Record 60-second demo video (show capture → inject in action on Claude)
- [ ] Take 5 screenshots: popup, dashboard, injection toast, search, settings
- [ ] Set up mnemox.app domain + deploy landing page
- [ ] Deploy backend to Railway / Render / Fly.io
- [ ] Set up Stripe products (Pro $9, Team $29) + get real price IDs
- [ ] Configure Supabase production project + run schema SQL
- [ ] Set up Qdrant Cloud cluster (free tier available)
- [ ] Test full flow end-to-end in production

### 48 hours before
- [ ] Schedule ProductHunt for 12:01am PST Tuesday (best launch day)
- [ ] Prepare list of 50+ people to message on launch day
- [ ] Write maker comment (already drafted above)
- [ ] Set up Discord/Slack community for early users
- [ ] Email waitlist (if any)

### Launch day (12:01am PST)
- [ ] Post ProductHunt listing live
- [ ] Post Twitter/X thread
- [ ] Post LinkedIn
- [ ] Message personal network individually asking for upvotes
- [ ] Post in relevant Slack communities (Indie Hackers, etc.)
- [ ] Reply to every ProductHunt comment within 30 minutes
- [ ] Monitor Stripe for first paying customers

### Week after launch
- [ ] Email all sign-ups personally
- [ ] Ship any bugs reported on launch day
- [ ] Post "Day 1 results" thread on Twitter
- [ ] Write dev blog post on building Mnemox in 6 weeks
- [ ] Submit to: Hacker News (Show HN), BetaList, SaaS Hub, Launching Next

---

## Backend Deployment Guide

### Environment variables to set in production

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_KEY=...
SUPABASE_JWT_SECRET=...          # from Supabase project settings → API → JWT Secret
OPENAI_API_KEY=sk-...
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRO_PRICE_ID=price_...
STRIPE_TEAM_PRICE_ID=price_...
API_SECRET_KEY=generate-with-openssl-rand-hex-32
APP_ENV=production
CORS_ORIGINS=chrome-extension://YOUR_EXTENSION_ID,https://mnemox.app
```

### Supabase setup
1. Create project at supabase.com
2. Run `supabase_schema.sql` in SQL editor
3. Run `supabase_schema_step7.sql` in SQL editor
4. Enable email auth in Authentication settings
5. Set JWT expiry to 3600s (1 hour)

### Stripe setup
1. Create products: "Mnemox Pro" ($9/mo) and "Mnemox Team" ($29/mo)
2. Copy price IDs to env
3. Add webhook endpoint: `https://your-api.com/billing/webhook`
4. Subscribe to: `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`

### Extension
1. Replace `supabaseUrl` and `supabaseAnonKey` defaults in extension settings
2. Update `backendUrl` default to your production API URL
3. Package extension → submit to Chrome Web Store

---

## Key metrics to track

| Metric | Target (Day 30) |
|--------|-----------------|
| Chrome installs | 500 |
| Daily active users | 150 |
| Memories captured/day | 2,000 |
| Pro conversions | 25 (5% of actives) |
| Team conversions | 5 |
| MRR | $320 |

---

*Built by Ajay — ajjukak123@gmail.com*
*Mnemox v0.8.0 — 303 tests passing*
