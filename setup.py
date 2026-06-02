#!/usr/bin/env python3
"""
Product Lifecycle Automation CLI
==================================
Product-agnostic E2E automation. All product details come from product.config.json.
To use for a NEW project: copy setup.py + .env.template to your new project folder,
edit product.config.json with your new product details, and run python setup.py.

Usage:
  python setup.py              # Full setup wizard
  python setup.py --rotate     # Update/rotate one or more secrets
  python setup.py --deploy     # Deploy only (uses existing .env)
  python setup.py --package    # Package extension zip only
  python setup.py --ph-draft   # Generate ProductHunt draft only
  python setup.py --status     # Check status of all services
"""

import os
import sys
import json
import shutil
import zipfile
import subprocess
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# ── Load product config ──────────────────────────────────────────────────────
ROOT = Path(__file__).parent
CONFIG_FILE = ROOT / "product.config.json"

def load_config():
    if not CONFIG_FILE.exists():
        print(f"  ❌  product.config.json not found at {CONFIG_FILE}")
        print("  Create it first — see .env.template for reference.")
        sys.exit(1)
    return json.loads(CONFIG_FILE.read_text())

CFG = load_config()
PRODUCT_NAME = CFG["product"]["name"]
PRODUCT_WEBSITE = CFG["product"]["website"]

# ── Terminal colors ─────────────────────────────────────────────────────────
class C:
    PURPLE  = "\033[95m"
    BLUE    = "\033[94m"
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RESET   = "\033[0m"

def p(text, color=C.RESET, end="\n"):
    print(f"{color}{text}{C.RESET}", end=end)

def header(text):
    width = 60
    p("=" * width, C.PURPLE)
    p(f"  [{PRODUCT_NAME}] {text}", C.BOLD + C.PURPLE)
    p("=" * width, C.PURPLE)

def step(n, text):
    p(f"\n[{n}] {text}", C.BOLD + C.CYAN)
    p("─" * 50, C.DIM)

def ok(text):    p(f"  ✅  {text}", C.GREEN)
def warn(text):  p(f"  ⚠️   {text}", C.YELLOW)
def err(text):   p(f"  ❌  {text}", C.RED)
def info(text):  p(f"  ℹ️   {text}", C.BLUE)

def ask(prompt, secret=False, default=None):
    """Prompt user for input. If secret=True, show masked input."""
    display = f"  → {prompt}"
    if default:
        display += f" [{C.DIM}current: {default[:6]}...{C.RESET}]"
    display += ": "
    if secret:
        import getpass
        val = getpass.getpass(display)
    else:
        print(display, end="")
        val = input()
    return val.strip() or default or ""

def confirm(prompt):
    print(f"  → {prompt} [y/N]: ", end="")
    return input().strip().lower() == "y"

# ── Paths ────────────────────────────────────────────────────────────────────
ENV_FILE = ROOT / ".env"
ENV_TEMPLATE = ROOT / ".env.template"
BACKEND_DIR  = ROOT / CFG["deploy"]["backend_dir"]
WEBSITE_DIR  = ROOT / CFG["deploy"]["website_dir"]
EXTENSION_DIR = ROOT / CFG["deploy"]["extension_dir"]
OUTPUTS_DIR  = ROOT / "dist"

# ── Secret definitions ────────────────────────────────────────────────────────
SECRETS = [
    {
        "key": "SUPABASE_URL",
        "label": "Supabase Project URL",
        "hint": "https://xxxx.supabase.co  (Settings → API)",
        "secret": False,
        "group": "Supabase",
    },
    {
        "key": "SUPABASE_ANON_KEY",
        "label": "Supabase Anon Key",
        "hint": "Settings → API → anon public",
        "secret": True,
        "group": "Supabase",
    },
    {
        "key": "SUPABASE_SERVICE_KEY",
        "label": "Supabase Service Role Key",
        "hint": "Settings → API → service_role (keep secret!)",
        "secret": True,
        "group": "Supabase",
    },
    {
        "key": "SUPABASE_JWT_SECRET",
        "label": "Supabase JWT Secret",
        "hint": "Settings → API → JWT Secret",
        "secret": True,
        "group": "Supabase",
    },
    {
        "key": "OPENAI_API_KEY",
        "label": "OpenAI API Key",
        "hint": "platform.openai.com → API keys",
        "secret": True,
        "group": "AI",
    },
    {
        "key": "QDRANT_URL",
        "label": "Qdrant Cluster URL",
        "hint": "cloud.qdrant.io → your cluster URL",
        "secret": False,
        "group": "AI",
    },
    {
        "key": "QDRANT_API_KEY",
        "label": "Qdrant API Key",
        "hint": "cloud.qdrant.io → API Keys",
        "secret": True,
        "group": "AI",
    },
    {
        "key": "STRIPE_SECRET_KEY",
        "label": "Stripe Secret Key",
        "hint": "stripe.com → Developers → API keys → Secret key (sk_live_...)",
        "secret": True,
        "group": "Stripe",
    },
    {
        "key": "STRIPE_PUBLISHABLE_KEY",
        "label": "Stripe Publishable Key",
        "hint": "stripe.com → Developers → API keys → Publishable key (pk_live_...)",
        "secret": False,
        "group": "Stripe",
    },
    {
        "key": "STRIPE_WEBHOOK_SECRET",
        "label": "Stripe Webhook Signing Secret",
        "hint": "stripe.com → Developers → Webhooks → your endpoint → Signing secret (whsec_...)",
        "secret": True,
        "group": "Stripe",
    },
    {
        "key": "STRIPE_PRO_PRICE_ID",
        "label": "Stripe Pro Price ID",
        "hint": "price_1Td7kyRrGUb4Blx5LjQhP20n",
        "secret": False,
        "group": "Stripe",
    },
    {
        "key": "STRIPE_TEAM_PRICE_ID",
        "label": "Stripe Team Price ID",
        "hint": "price_1Td7liRrGUb4Blx5ayOaxqsT",
        "secret": False,
        "group": "Stripe",
    },
    {
        "key": "BACKEND_URL",
        "label": "Backend URL (Railway)",
        "hint": "https://mnemox-production.up.railway.app",
        "secret": False,
        "group": "Deploy",
    },
    {
        "key": "RAILWAY_TOKEN",
        "label": "Railway API Token",
        "hint": "railway.app → Account → Tokens → Create token",
        "secret": True,
        "group": "Deploy",
    },
]

# ── .env helpers ─────────────────────────────────────────────────────────────
def load_env():
    """Load existing .env into dict."""
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env

def save_env(env: dict):
    """Save dict to .env file."""
    lines = ["# Mnemox Environment Variables", f"# Updated: {datetime.now().isoformat()}", ""]
    groups = {}
    for s in SECRETS:
        groups.setdefault(s["group"], []).append(s["key"])

    for group, keys in groups.items():
        lines.append(f"# ── {group} ──")
        for key in keys:
            val = env.get(key, "")
            lines.append(f"{key}={val}")
        lines.append("")

    # Write any extra keys not in SECRETS
    known = {s["key"] for s in SECRETS}
    extras = {k: v for k, v in env.items() if k not in known}
    if extras:
        lines.append("# ── Other ──")
        for k, v in extras.items():
            lines.append(f"{k}={v}")

    ENV_FILE.write_text("\n".join(lines))
    ok(f"Secrets saved to {ENV_FILE}")

def write_template():
    """Write .env.template with placeholders."""
    lines = ["# Mnemox .env.template — copy to .env and fill in your values", ""]
    groups = {}
    for s in SECRETS:
        groups.setdefault(s["group"], []).append(s)

    for group, secrets in groups.items():
        lines.append(f"# ── {group} ──")
        for s in secrets:
            lines.append(f"# {s['hint']}")
            lines.append(f"{s['key']}=YOUR_{s['key']}_HERE")
        lines.append("")

    ENV_TEMPLATE.write_text("\n".join(lines))
    ok(f"Template written to {ENV_TEMPLATE}")

def mask(val):
    if not val or len(val) < 8:
        return "***"
    return val[:4] + "..." + val[-4:]

# ── Step 1: Secrets wizard ───────────────────────────────────────────────────
def run_secrets_wizard(rotate=False, env=None):
    if env is None:
        env = load_env()

    header("SECRETS CONFIGURATION")
    if rotate:
        p("\nRotate mode — press Enter to keep current value.\n", C.YELLOW)
    else:
        p("\nEnter your API keys. They will be saved to .env (gitignored).\n", C.CYAN)

    current_group = None
    for s in SECRETS:
        if s["group"] != current_group:
            current_group = s["group"]
            p(f"\n  ── {current_group} ──", C.BOLD + C.PURPLE)

        current = env.get(s["key"], "")
        if rotate and current:
            default_display = mask(current)
            label = f"{s['label']} (current: {default_display})"
        else:
            label = f"{s['label']}  [{s['hint']}]"

        val = ask(label, secret=s["secret"], default=current if rotate else None)
        if val:
            env[s["key"]] = val
        elif current:
            env[s["key"]] = current  # keep existing

    save_env(env)
    write_template()
    return env

# ── Step 2: Sync secrets to Railway ─────────────────────────────────────────
def deploy_backend(env):
    step(2, "Deploy Backend to Railway")

    token = env.get("RAILWAY_TOKEN")
    if not token:
        warn("No RAILWAY_TOKEN found — skipping Railway deploy.")
        info("Set RAILWAY_TOKEN in .env and re-run with --deploy")
        return False

    # Check railway CLI
    if not shutil.which("railway"):
        warn("Railway CLI not installed.")
        info("Install: npm install -g @railway/cli")
        info("Then run: railway login")
        info("Then re-run: python setup.py --deploy")
        return False

    p("  Pushing environment variables to Railway...", C.CYAN)

    # Keys to sync to Railway
    railway_keys = [
        "SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY",
        "SUPABASE_JWT_SECRET", "OPENAI_API_KEY", "QDRANT_URL", "QDRANT_API_KEY",
        "STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET",
        "STRIPE_PRO_PRICE_ID", "STRIPE_TEAM_PRICE_ID",
    ]

    for key in railway_keys:
        val = env.get(key)
        if val:
            result = subprocess.run(
                ["railway", "variables", "set", f"{key}={val}"],
                capture_output=True, text=True,
                env={**os.environ, "RAILWAY_TOKEN": token}
            )
            if result.returncode == 0:
                ok(f"Set {key}")
            else:
                warn(f"Failed to set {key}: {result.stderr.strip()}")

    # Deploy
    p("\n  Deploying backend...", C.CYAN)
    result = subprocess.run(
        ["railway", "up", "--detach"],
        capture_output=True, text=True, cwd=str(BACKEND_DIR),
        env={**os.environ, "RAILWAY_TOKEN": token}
    )
    if result.returncode == 0:
        ok("Backend deployed to Railway!")
    else:
        warn(f"Railway deploy output: {result.stdout}")
        err(f"Railway deploy error: {result.stderr}")

    # Health check
    backend_url = env.get("BACKEND_URL", "")
    if backend_url:
        p(f"\n  Checking {backend_url}/health ...", C.CYAN)
        try:
            import urllib.request
            with urllib.request.urlopen(f"{backend_url}/health", timeout=10) as r:
                data = json.loads(r.read())
                if data.get("status") == "ok":
                    ok(f"Backend healthy: {backend_url}")
                else:
                    warn(f"Unexpected response: {data}")
        except Exception as e:
            warn(f"Health check failed: {e}")

    return True

# ── Step 3: Deploy website to Vercel ─────────────────────────────────────────
def deploy_website(env):
    step(3, "Deploy Website to Vercel")

    if not shutil.which("vercel"):
        warn("Vercel CLI not installed.")
        info("Install: npm install -g vercel")
        info("Then run: vercel login")
        info("Re-run: python setup.py --deploy")
        return False

    p("  Deploying mnemoxpro.com to Vercel...", C.CYAN)
    result = subprocess.run(
        ["vercel", "--prod", "--yes"],
        capture_output=True, text=True, cwd=str(WEBSITE_DIR)
    )
    if result.returncode == 0:
        ok("Website deployed to Vercel!")
        # Extract URL from output
        for line in result.stdout.splitlines():
            if "https://" in line:
                info(f"URL: {line.strip()}")
    else:
        warn(f"Vercel output: {result.stdout}")
        err(f"Vercel error: {result.stderr}")
        return False

    return True

# ── Step 4: Package Chrome Extension ─────────────────────────────────────────
def package_extension(env):
    step(4, "Package Chrome Extension")

    OUTPUTS_DIR.mkdir(exist_ok=True)
    version = "0.1.0"

    # Try to read version from manifest
    manifest_path = EXTENSION_DIR / "manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
            version = manifest.get("version", version)
            # Inject backend URL into manifest description or update service worker
            ok(f"Read manifest version: {version}")
        except:
            pass

    # Patch service_worker.js with correct backend URL
    sw_path = EXTENSION_DIR / "background" / "service_worker.js"
    backend_url = env.get("BACKEND_URL", "https://mnemox-production.up.railway.app")
    if sw_path.exists():
        content = sw_path.read_text()
        # Update backendUrl default value
        import re
        patched = re.sub(
            r"backendUrl:\s*'[^']*'",
            f"backendUrl: '{backend_url}'",
            content
        )
        sw_path.write_text(patched)
        ok(f"Patched service_worker.js → backendUrl: {backend_url}")

    # Create zip
    zip_name = f"mnemox-extension-v{version}.zip"
    zip_path = OUTPUTS_DIR / zip_name

    # Exclude files that shouldn't be in the extension
    EXCLUDE = {".DS_Store", "Thumbs.db", "__pycache__", ".git"}
    EXCLUDE_EXT = {".py", ".md", ".log"}

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in EXTENSION_DIR.rglob("*"):
            if file.is_file():
                if any(ex in file.parts for ex in EXCLUDE):
                    continue
                if file.suffix in EXCLUDE_EXT:
                    continue
                arcname = file.relative_to(EXTENSION_DIR)
                zf.write(file, arcname)
                info(f"  + {arcname}")

    size_kb = zip_path.stat().st_size // 1024
    ok(f"Extension packaged: {zip_path} ({size_kb} KB)")
    ok(f"Upload this ZIP to: chrome.google.com/webstore/devconsole")

    # Also copy to root for easy access
    shutil.copy(zip_path, ROOT / zip_name)
    ok(f"Also copied to: {ROOT / zip_name}")

    return str(zip_path)

# ── Step 5: Generate ProductHunt Draft ───────────────────────────────────────
def generate_ph_draft(env):
    step(5, "Generate ProductHunt Launch Draft")

    OUTPUTS_DIR.mkdir(exist_ok=True)
    backend_url = env.get("BACKEND_URL", "https://mnemox-production.up.railway.app")
    launch_date = (datetime.now() + timedelta(days=7)).strftime("%A, %B %d, %Y")
    # Find next Tuesday
    today = datetime.now()
    days_ahead = 1 - today.weekday()  # Tuesday = 1
    if days_ahead <= 0:
        days_ahead += 7
    next_tuesday = today + timedelta(days=days_ahead)
    launch_date = next_tuesday.strftime("%A, %B %d, %Y")

    p = CFG["product"]
    pr = CFG["pricing"]
    ph = CFG["producthunt"]
    plans_text = "\n".join(f"  - {pl['name']}: {pl['price']}" for pl in pr["plans"])
    tags_text = ", ".join(ph["tags"])

    draft = f"""# {p['name']} — ProductHunt Launch Draft
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
Recommended Launch Date: {launch_date} at {ph['launch_time']}

---

## LISTING DETAILS

**Product Name:** {p['name']}

**Tagline (60 chars max):**
{p['tagline']}

**Description:**
{p['description']}

**Website:** {p['website']}
**Category:** {ph['category']}
**Tags:** {tags_text}
**Pricing:** Paid (with a free plan)
{plans_text}

**Promo Code:** {pr['promo_code']} ({pr['promo_description']}, max 100 redemptions)

---

## MAKER COMMENT (pin this as your first comment)

Hey Product Hunt! 👋

I built Mnemox because I was frustrated switching between ChatGPT and Claude and having to
re-explain my entire context every time — my stack, my project name, my preferences.

So I built a Chrome extension that silently watches your AI conversations, captures the important
stuff, and injects it as context before your next message — on any AI platform.

Took me about 6 weeks solo. 303 tests, 8 build steps, deployed to production.

Would love brutal honest feedback:
→ What's missing?
→ What would make you actually install this?

Use code PHUNT50 for 50% off Pro — just for the PH community 🙏

---

## TWITTER THREAD (post launch morning)

Tweet 1:
I got tired of re-explaining myself to every AI chatbot.
So I built Mnemox — one memory layer across ChatGPT, Claude, Gemini & Copilot.
Install once. Never repeat yourself again.
🔗 mnemoxpro.com
[attach: screenshot of memory injection in action]

Tweet 2:
How it works:
→ Mnemox watches your AI conversations
→ Captures key context automatically
→ Injects it before your next prompt
→ Works across ALL AI platforms
No API keys. No setup. Just install and go.

Tweet 3:
Built this solo in 6 weeks:
✅ Chrome MV3 extension
✅ FastAPI backend on Railway
✅ Vector search (OpenAI + Qdrant)
✅ Supabase auth + Stripe billing
✅ 303 tests passing
Shipping solo is hard. Worth it.

Tweet 4:
Free forever for up to 50 memories.
Pro is $9/month for unlimited.
PH community gets 50% off with code PHUNT50.
👉 We're live on Product Hunt today — upvote if this solves a real problem for you!
[link to PH listing]

---

## REDDIT POST (r/SideProject)

**Title:** I built Mnemox — a Chrome extension that gives you one memory layer across ChatGPT, Claude, Gemini, and Copilot

**Body:**
Hey r/SideProject,

I've been switching between ChatGPT and Claude constantly for work, and every session starts from zero.
No memory. No context. I re-explain my stack, my project, my preferences dozens of times per week.

So I built Mnemox.

It's a Chrome extension that:
- Silently captures important context from your AI conversations
- Stores it as searchable memories
- Injects the most relevant ones before each new prompt — across any AI platform

Free to install, no credit card, works in 60 seconds.
Chrome extension is under review — website + waitlist is live at mnemoxpro.com

Honest feedback welcome. What am I missing?

---

## REDDIT POST (r/ChatGPT)

**Title:** Tired of re-explaining yourself every new ChatGPT session? Built a fix.

**Body:**
Every session with ChatGPT starts from zero.
"I'm a Python developer working on..."
"My project is called..."
"I prefer..."

I built a Chrome extension called Mnemox that captures your context from AI conversations
and automatically injects it before your next prompt — so ChatGPT already knows who you are.

Works on Claude, Gemini, Copilot too.

Free: mnemoxpro.com

---

## CHECKLIST BEFORE LAUNCH

- [ ] Chrome extension approved by Chrome Web Store
- [ ] mnemoxpro.com is live and all sections loading
- [ ] Backend health check passing: {backend_url}/health
- [ ] PHUNT50 Stripe coupon active and tested
- [ ] ProductHunt listing scheduled for {launch_date} 12:01 AM PST
- [ ] Maker comment written and ready to post
- [ ] Twitter thread drafted and scheduled
- [ ] Reddit posts ready to paste
- [ ] Personal outreach list of 30-50 people prepared
- [ ] Commit to replying to every PH comment within 20 minutes all day

---

## TARGET METRICS (Day 30)

- 500+ active Chrome extension installs
- 50+ Product Hunt upvotes
- 10+ Pro plan conversions
- 100+ Reddit/Twitter mentions
- 5+ press/blog mentions
"""

    draft_path = OUTPUTS_DIR / f"{p['name'].upper()}_PRODUCTHUNT_DRAFT.md"
    draft_path.write_text(draft)

    root_copy = ROOT / f"{p['name'].upper()}_PRODUCTHUNT_DRAFT.md"
    shutil.copy(draft_path, root_copy)

    ok(f"ProductHunt draft saved: {draft_path}")
    ok(f"Also saved to: {root_copy}")
    return str(draft_path)

# ── Step 6: Status check ──────────────────────────────────────────────────────
def check_status(env):
    header("SERVICE STATUS CHECK")

    import urllib.request
    services = [
        ("Backend API", env.get("BACKEND_URL", "") + "/health"),
        (f"{PRODUCT_NAME} Website", CFG["product"]["website"]),
    ]

    for name, url in services:
        if not url or url == "/health":
            warn(f"{name}: URL not configured")
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MnemoxSetup/1.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                ok(f"{name}: {r.status} {url}")
        except Exception as e:
            err(f"{name}: {e}")

    p("\n  Secrets configured:", C.BOLD)
    env_data = load_env()
    for s in SECRETS:
        val = env_data.get(s["key"], "")
        if val and val != f"YOUR_{s['key']}_HERE":
            ok(f"{s['key']}: {mask(val)}")
        else:
            warn(f"{s['key']}: NOT SET")

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Mnemox Lifecycle Automation CLI")
    parser.add_argument("--rotate",   action="store_true", help="Rotate/update secrets only")
    parser.add_argument("--deploy",   action="store_true", help="Deploy backend + website")
    parser.add_argument("--package",  action="store_true", help="Package extension zip")
    parser.add_argument("--ph-draft", action="store_true", help="Generate ProductHunt draft")
    parser.add_argument("--status",   action="store_true", help="Check service status")
    args = parser.parse_args()

    p(r"""
  __  __
 |  \/  |_ __   ___ _ __ ___   _____  __
 | |\/| | '_ \ / _ \ '_ ` _ \ / _ \ \/ /
 | |  | | | | |  __/ | | | | | (_) >  <
 |_|  |_|_| |_|\___|_| |_| |_|\___/_/\_\

  Lifecycle Automation CLI
""", C.PURPLE + C.BOLD)

    if args.status:
        env = load_env()
        check_status(env)
        return

    if args.rotate:
        env = load_env()
        env = run_secrets_wizard(rotate=True, env=env)
        if confirm("Deploy backend with updated secrets?"):
            deploy_backend(env)
        return

    if args.deploy:
        env = load_env()
        deploy_backend(env)
        deploy_website(env)
        return

    if args.package:
        env = load_env()
        package_extension(env)
        return

    if args.ph_draft:
        env = load_env()
        generate_ph_draft(env)
        return

    # ── Full wizard ──
    header("FULL LIFECYCLE SETUP")
    p("This will configure secrets, deploy everything, and generate launch assets.\n", C.CYAN)

    # Step 1: Secrets
    env = run_secrets_wizard(rotate=False, env=load_env())

    # Step 2: Backend
    step(2, "Deploy Backend")
    if confirm("Deploy backend to Railway now?"):
        deploy_backend(env)
    else:
        info("Skipped. Run later: python setup.py --deploy")

    # Step 3: Website
    step(3, "Deploy Website")
    if confirm("Deploy website to Vercel now?"):
        deploy_website(env)
    else:
        info("Skipped. Run later: python setup.py --deploy")

    # Step 4: Package extension
    step(4, "Package Extension")
    if confirm("Package Chrome extension ZIP now?"):
        package_extension(env)
    else:
        info("Skipped. Run later: python setup.py --package")

    # Step 5: PH draft
    step(5, "ProductHunt Draft")
    if confirm("Generate ProductHunt launch draft?"):
        generate_ph_draft(env)
    else:
        info("Skipped. Run later: python setup.py --ph-draft")

    # Done
    p("\n" + "=" * 60, C.GREEN)
    p("  🚀  MNEMOX SETUP COMPLETE!", C.BOLD + C.GREEN)
    p("=" * 60, C.GREEN)
    p("""
  Next steps:
  1. Wait for Chrome Web Store approval
  2. Run: python setup.py --status   (check everything is live)
  3. Schedule your ProductHunt listing for Tuesday 12:01 AM PST
  4. Post on Reddit + Twitter on launch day
  5. Reply to every comment within 20 minutes all day
    """, C.CYAN)

if __name__ == "__main__":
    main()
