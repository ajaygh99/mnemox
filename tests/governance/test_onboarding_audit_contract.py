from pathlib import Path


ROOT = Path(__file__).parents[2]
AUDIT = ROOT / "docs" / "audits" / "onboarding"


def read(name):
    return (AUDIT / name).read_text(encoding="utf-8")


def test_required_audit_artifacts_exist():
    assert {"AUDIT.md", "CLAIM-CAPABILITY-MATRIX.md", "FRICTION-REGISTER.md"} <= {
        path.name for path in AUDIT.iterdir()
    }


def test_audit_marks_live_evidence_boundary():
    audit = read("AUDIT.md")
    assert "source audit only" in audit
    assert "Static source evidence proves configuration" in audit
    assert "Live evidence" in audit
    assert "Blocked" in audit


def test_audit_covers_required_first_use_topics():
    audit = read("AUDIT.md").casefold()
    for topic in (
        "permission", "supported-site", "capture", "injection", "local/cloud",
        "consent", "preview", "approve", "reject", "edit", "forget", "pause",
        "undo", "diagnostic", "unsupported-site", "recovery", "accessibility",
        "screenshot",
    ):
        assert topic in audit


def test_accessibility_results_are_explicit():
    audit = read("AUDIT.md")
    for check in (
        "Form label association", "Toggle accessible names", "Keyboard reachability",
        "Focus indication", "Dynamic status announcement", "Screen reader operation",
        "Color contrast", "Focus order/return",
    ):
        assert check in audit
    for result in ("Pass", "Fail", "Partial", "Blocked"):
        assert result in audit


def test_claim_matrix_uses_required_statuses_and_high_risk_claims():
    matrix = read("CLAIM-CAPABILITY-MATRIX.md")
    for status in ("verified-source", "conditional", "unverified-production", "absent", "contradicted"):
        assert f"`{status}`" in matrix
    for claim in ("silently captures", "Semantic search", "Team Memory", "Memory analytics", "Free forever", "Works in 60 seconds"):
        assert claim in matrix


def test_friction_register_has_severity_ranked_actionable_findings():
    register = read("FRICTION-REGISTER.md")
    assert register.count("| ONB-") >= 15
    for severity in ("| 1 |", "| 2 |", "| 3 |", "| 4 |"):
        assert severity in register
    for heading in ("User impact", "Recommended next issue", "Approval boundary"):
        assert heading in register
    assert "before Phase 0 exit" in register


def test_audit_does_not_claim_product_fixes_or_live_proof():
    combined = "\n".join(read(name) for name in ("AUDIT.md", "CLAIM-CAPABILITY-MATRIX.md", "FRICTION-REGISTER.md"))
    prohibited_completion_claims = (
        "onboarding is complete", "all claims are verified", "accessibility passes live",
        "store listing verified", "phase 0 exit passed",
    )
    assert not any(claim in combined.casefold() for claim in prohibited_completion_claims)


def test_reproducible_static_audit_command_is_documented():
    audit = read("AUDIT.md")
    assert "python -m pytest tests/governance/test_onboarding_audit_contract.py -q" in audit
    assert "python -m pytest -q" in audit
