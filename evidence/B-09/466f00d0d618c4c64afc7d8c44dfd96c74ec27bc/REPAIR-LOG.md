# B-09 repair log

Validated candidate: `466f00d0d618c4c64afc7d8c44dfd96c74ec27bc`

Baseline: `origin/main` at `4087e046358eec22bc62e8bdf74fa11c575e6a9b`

## Removed unsafe or nonfunctional behavior

- Removed `gh pr review --approve`; the workflow never approves its own PR.
- Removed the `REVIEWER_TOKEN` secret dependency.
- Removed draft-only logic that attempted to merge an unmergeable draft.
- Removed checkout of the PR branch and all execution of PR-controlled code.
- Removed the phase-advance notification job, which relied on absent event data
  and was outside the merge gate.
- Removed swallowed merge failures (`|| echo ...`); an actual enablement failure
  now fails closed.

## Added protected native auto-merge behavior

- Uses the exact workflow name `Test Suite` in `workflow_run`.
- Resolves the open PR associated with the completed test head SHA.
- Uses `pull_request_target` only for `ready_for_review` and `labeled` events so
  the trusted default-branch workflow can re-evaluate a draft after independent
  review; it does not check out or execute PR content.
- Requires a same-repository PR targeting `main` with an `agent-ready` PR label.
- Treats a draft as an expected waiting state and does not mark it ready.
- Queries successful completed `Test Suite` runs for the PR's exact head SHA.
- Enables GitHub native squash auto-merge with `gh pr merge --auto` only after
  all eligibility checks pass.
- Leaves branch protection and required independent approval authoritative.

## Permissions

The workflow has `actions: read`, `contents: write`, and `pull-requests: write`.
Write permission is limited to enabling GitHub native auto-merge; it does not
approve reviews, push code, or bypass protection.

## Residual validation boundary

GitHub executes `pull_request_target` and `workflow_run` definitions from the
default branch. Therefore this draft PR can prove syntax, static invariants,
regressions, and exact-head CI, but it cannot safely prove the newly repaired
live auto-merge path before merge. B-10 must exercise refusal paths, and B-08
must provide a bounded post-merge dry run. No production merge is attempted by
B-09 itself.
