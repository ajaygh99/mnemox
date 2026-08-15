"""Fail-closed regression contract for the autonomous merge workflow."""

from dataclasses import dataclass
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = (ROOT / ".github/workflows/autonomous-review.yml").read_text(
    encoding="utf-8"
)
PHASE_STATUS = (ROOT / "governance/status/PHASE-0-STATUS.md").read_text(
    encoding="utf-8"
)


@dataclass(frozen=True)
class PullRequestState:
    same_repository: bool = True
    base_ref: str = "main"
    labels: tuple[str, ...] = ("agent-ready",)
    draft: bool = False
    head_sha: str = "candidate-sha"
    successful_test_sha: str | None = "candidate-sha"


def eligible_for_native_auto_merge(state: PullRequestState) -> bool:
    """Executable model of every eligibility gate in the trusted workflow."""

    return (
        state.same_repository
        and state.base_ref == "main"
        and "agent-ready" in state.labels
        and not state.draft
        and state.successful_test_sha == state.head_sha
    )


@pytest.mark.parametrize(
    ("state", "reason"),
    [
        (PullRequestState(draft=True), "draft"),
        (PullRequestState(labels=()), "missing agent-ready label"),
        (PullRequestState(base_ref="release"), "non-main base"),
        (PullRequestState(same_repository=False), "fork head"),
        (PullRequestState(successful_test_sha=None), "missing or failed tests"),
        (
            PullRequestState(successful_test_sha="stale-sha"),
            "successful test belongs to stale head",
        ),
    ],
)
def test_prohibited_state_is_ineligible(state: PullRequestState, reason: str):
    assert not eligible_for_native_auto_merge(state), reason


def test_only_complete_exact_head_state_is_eligible():
    assert eligible_for_native_auto_merge(PullRequestState())


def test_workflow_rejects_forks_and_non_main_bases():
    assert 'if [ "$HEAD_REPO" != "$GH_REPO" ] || [ "$BASE_REF" != "main" ]' in WORKFLOW
    assert 'echo "eligible=false"' in WORKFLOW


def test_workflow_requires_agent_ready_label():
    assert "grep -Fxq 'agent-ready'" in WORKFLOW
    assert "PR does not have the agent-ready label." in WORKFLOW


def test_workflow_refuses_drafts():
    assert 'if [ "$IS_DRAFT" = "true" ]' in WORKFLOW
    assert "PR remains draft; independent review must mark it ready." in WORKFLOW


def test_workflow_requires_success_for_exact_pull_request_head():
    assert (
        'HEAD_SHA=$(gh api "repos/$GH_REPO/pulls/$PR_NUMBER" --jq \'.head.sha\')'
        in WORKFLOW
    )
    assert "head_sha=$HEAD_SHA&status=completed" in WORKFLOW
    assert 'select(.conclusion == "success")' in WORKFLOW
    assert 'if [ "$SUCCESS_COUNT" -lt 1 ]' in WORKFLOW


def test_failed_cancelled_pending_or_missing_runs_cannot_count_as_success():
    assert '--jq \'[.workflow_runs[] | select(.conclusion == "success") ] | length\'' in WORKFLOW
    for disallowed in ("failure", "cancelled", "timed_out", "pending", "in_progress"):
        assert f'select(.conclusion == "{disallowed}")' not in WORKFLOW


def test_workflow_does_not_self_approve_or_use_reviewer_secret():
    assert "gh pr review" not in WORKFLOW
    assert "REVIEWER_TOKEN" not in WORKFLOW
    assert "--approve" not in WORKFLOW


def test_workflow_has_no_actor_specific_exception():
    assert "github.actor" not in WORKFLOW
    assert "codex-mnemox" not in WORKFLOW


def test_workflow_cannot_bypass_branch_protection_or_directly_merge():
    assert "--admin" not in WORKFLOW
    assert "--auto" in WORKFLOW
    assert "--squash --auto" in WORKFLOW
    assert "|| echo" not in WORKFLOW


def test_workflow_does_not_execute_pull_request_code():
    assert "actions/checkout" not in WORKFLOW
    assert "github.event.pull_request.head" not in WORKFLOW


def test_phase_order_keeps_b08_and_phase1_blocked_until_b10_finishes():
    required_order = (
        "1. B-09 (#16)",
        "2. B-10 (#20)",
        "3. B-08 (#19)",
        "4. reviewed Phase 0 exit decision",
        "5. separately contracted and owner-authorized Phase 1 issue",
    )
    positions = [PHASE_STATUS.index(item) for item in required_order]
    assert positions == sorted(positions)
