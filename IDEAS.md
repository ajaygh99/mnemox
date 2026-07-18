# Mnemox — Parking Lot for Ideas

> Any new idea goes HERE first. Do NOT build it until it's planned into a step.
> Rule: Write it down, keep building the current step.

## Ideas Backlog

- [ ] Mobile app (iOS/Android) companion
- [ ] Firefox extension port
- [ ] Voice memo → memory capture
- [ ] Memory tagging / categories
- [ ] Memory export (JSON / CSV)
- [ ] Public memory sharing (opt-in)
- [ ] AI-summarized weekly digest of your memories
- [ ] Cosmetic: quiet the "No submit button matched" wire-time console
      warning in content.js (line ~436, all sites). Harmless — fires at
      page-load before the send button renders, capture/injection already
      have fallbacks — but noisy in chrome://extensions Errors panel.

## Planned — Pricing / Upgrade Flow (Step 11, not yet built)

Wire the popup's "Upgrade to Pro" to a real Stripe checkout. Backend
(`/billing/checkout`, `/billing/portal`, webhook) already works and is
tested — nothing calls it yet from the extension or website.

**Design decisions from 2026-07-12 analysis:**
- Button, not a toggle. Flipping a switch implies instant/free/reversible;
  paying does not. Show "Upgrade to Pro" → opens Stripe Checkout in a new
  tab. Only show "Pro ✓" after the webhook confirms payment.
- Sign-up stays optional for everyone except at the moment they click
  Upgrade — free/local mode must stay untouched (do not regress step10).
- Gotcha: the popup's cached JWT won't reflect a new plan until it's
  refreshed. Need a refresh-token exchange or re-prompt sign-in after
  checkout completes, or the popup will keep showing Free right after a
  successful upgrade.
- CWS risk: this project has been rejected twice for "described feature
  reviewer couldn't finish testing" (sign-up, then Dashboard). A paid flow
  that dead-ends at email confirmation risks the same pattern a third
  time. Test the full click-through in Stripe test mode before submitting.
- Must mark "contains purchases/subscriptions" in the store listing once
  this ships (currently undeclared).
- Ship as its own version (not bundled with a rejection-fix submission) so
  a new, riskier feature can't hold up an already-tested fix.
