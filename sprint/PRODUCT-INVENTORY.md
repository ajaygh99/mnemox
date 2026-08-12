# Mnemox canonical product and repository inventory

Status: Bootstrap B-01 evidence; external production state is not implied

Verified from: clean worktree of `origin/main`

Issue: `ajaygh99/mnemox#2`

## Canonical source

| Item | Value | Status | Repository evidence |
|---|---|---|---|
| Product | Mnemox - Universal AI Memory | Verified in source | `extension/manifest.json`
| Canonical repository | `https://github.com/ajaygh99/mnemox` | Verified by Git remote and GitHub repository metadata | `origin`; `product.config.json`
| Canonical local checkout | `C:\Users\ajjuk\Documents\Cowork\mnemox\Codex_Mnemox` | Owner-designated; verified as the checkout of the canonical remote | Git worktree metadata |
| Default branch | `main` | Verified through GitHub metadata | GitHub repository metadata |
| Bootstrap issue | `#2` - P0/B-01 | Verified on GitHub | `https://github.com/ajaygh99/mnemox/issues/2` |
| Isolated implementation branch | `agent/b01-canonical-inventory` | Verified locally | Git branch metadata |
| Baseline commit | `2b80eed0b984ccf7febc3ce806d871395c2f9263` | Verified; clean `origin/main` at worktree creation | Git metadata |

The checkout at `C:\Users\ajjuk\Documents\Cowork\mnemox\Mnemox_old` and the separate Prompt Coach checkout at `C:\Users\ajjuk\mnemox-extension` are outside this task. They were not read, changed, copied, or treated as release sources.

## Browser product identity

| Item | Value | Status | Evidence |
|---|---|---|---|
| Manifest version | Chrome Manifest V3 | Verified in source | `extension/manifest.json` |
| Extension version | `0.1.22` | Verified in source; store publication not independently verified by this task | `extension/manifest.json` |
| Chrome Store ID | `oningjpokiajciealpkkofdldcmnnfbf` | Verified as the ID used by repository website links; dashboard ownership/publication state unverified | `website/index.html` |
| Supported host declarations | ChatGPT, Claude, Gemini, Microsoft Copilot | Verified as manifest/content-script scope; live behavior unverified | `extension/manifest.json` |
| Permissions | `storage`, `activeTab` | Verified in source | `extension/manifest.json` |

Source declarations prove what the candidate is configured to do. They do not prove current Chrome Web Store contents, installation counts, production behavior, or policy approval.

## Product and service identifiers

| Item | Repository value | Verification status |
|---|---|---|
| Website | `https://mnemoxpro.com` | Configured in `product.config.json`; live route and deployment ownership require separate evidence |
| Support email | `hello@mnemoxpro.com` | Configured in `product.config.json` and website source; operational ownership unverified |
| Company | `SVK IT Services LLC` | Declared in `product.config.json`; legal ownership unverified |
| Source repository | `https://github.com/ajaygh99/mnemox` | Verified |
| Backend default | `https://mnemox-production.up.railway.app` | Hard-coded default in extension source; deployment health and ownership unverified |
| Backend directory | `backend/` | Verified in source |
| Website directory | `website/` | Verified in source; `website/vercel.json` indicates a Vercel-oriented static target |
| Extension directory | `extension/` | Verified in source |

## Claims requiring Phase 0 evidence

The following repository statements are configuration or marketing claims, not verified production facts:

- automatic capture and injection;
- cross-tool continuity across all declared sites;
- "Free forever";
- Pro and Team pricing or entitlement availability;
- backend, semantic-search, billing, and team readiness;
- live website, privacy-route, Railway, Vercel, and Chrome Store behavior.

They must be evaluated by the Phase 0 claim/capability matrix before publication or reuse. This inventory does not authorize copy, privacy, pricing, billing, deployment, or store changes.

## Ownership and approval

| Responsibility | Recorded owner | Status |
|---|---|---|
| Repository owner | GitHub account `ajaygh99` | Verified by repository namespace; human/legal identity not inferred |
| Product owner | Ajay (per repository instructions and issue approval) | Owner-designated; exact external-account authority still requires confirmation |
| Railway deployment owner | Not recorded in tracked source | Owner confirmation required |
| Vercel deployment owner | Not recorded in tracked source | Owner confirmation required |
| Chrome Web Store publisher | Not recorded in tracked source | Owner confirmation required |
| Supabase/Qdrant/Stripe owners | Not recorded in tracked source | Owner confirmation required; credentials must not be supplied in issue evidence |

## Test baseline

The original B-01 baseline had no executable Python runtime or dependency manifest. B-02 subsequently added an exact `requirements.txt`, explicit UTF-8 test reads, and a release guard matching manifest version `0.1.22`. B-04 added the supported command to GitHub Actions and contributor documentation.

Supported Windows command:

```powershell
$env:PYTHONUTF8 = "1"
python -m pytest -q
```

On the current B-01 candidate rebased through merged B-02 and B-04, the complete local suite passes with 391 tests, zero failures, and zero skips. The exact-head GitHub Actions workflow must also pass before merge.

## Six-gate status

| Gate | Result | Reason |
|---|---|---|
| Links | Blocked | Source URLs are inventoried, but live route/store validation is outside B-01 and lacks browser evidence |
| Claims | Fail | Multiple configured/public-facing claims lack production evidence |
| Functionality | Pass | Pinned clean-environment command runs 391 tests with zero failures or skips |
| Accessibility | Not applicable | Documentation-only inventory; no user interface changed |
| Security/privacy | Pass for this change | No secrets, content data, telemetry, permissions, or product behavior changed |
| Performance | Pass | The complete suite, including performance guards, passes; this inventory changes no runtime behavior |

## Rollback

This is documentation-only. Roll back by closing the draft pull request and deleting `agent/b01-canonical-inventory`; no production or user data is affected.
