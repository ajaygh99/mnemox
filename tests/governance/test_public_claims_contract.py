from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).parents[2]
WEBSITE_PATH = ROOT / "website" / "index.html"
MATRIX_PATH = ROOT / "docs" / "audits" / "onboarding" / "CLAIM-CAPABILITY-MATRIX.md"


def website() -> str:
    return WEBSITE_PATH.read_text(encoding="utf-8")


def public_copy_excluding_protected_policy() -> str:
    source = website()
    before_policy, policy_and_after = source.split('<div id="privacy-page">', 1)
    _, after_policy = policy_and_after.split('<div id="extension-page">', 1)
    return f"{before_policy}\n{after_policy}"


def public_copy_casefolded() -> str:
    return public_copy_excluding_protected_policy().casefold()


def test_public_html_is_statically_parseable():
    parser = HTMLParser()
    parser.feed(website())
    parser.close()


def test_unverified_guarantees_and_absolute_claims_are_absent():
    public = public_copy_casefolded()
    prohibited = (
        "free forever",
        "works in 60 seconds",
        "works in under a minute",
        "nothing leaves your browser",
        "we never train on your data",
        "encrypted & isolated",
        "silently captures",
        "automatically injects",
    )
    assert not any(phrase in public for phrase in prohibited)


def test_unavailable_features_are_not_active_purchase_benefits():
    public = public_copy_casefolded()
    assert "memory analytics" not in public
    assert "team memory is not currently available" in public
    assert "paid plans are not currently available" in public
    assert "shared team namespace" not in public
    assert "team invite management" not in public


def test_copy_states_consent_and_review_controls_precisely():
    public = public_copy_casefolded()
    for phrase in (
        "after informed consent",
        "capture and injection require consent",
        "edit, approve, reject, or return to your prompt",
        "injection remains off until you provide consent and enable it",
    ):
        assert phrase in public


def test_copy_distinguishes_local_and_connected_data_paths():
    public = public_copy_casefolded()
    for phrase in (
        "local unsigned use falls back to keyword matching",
        "unsigned use stores memories locally",
        "cloud sync and backend semantic search can send memory content beyond the browser",
    ):
        assert phrase in public


def test_site_support_is_qualified_and_not_guaranteed():
    public = public_copy_casefolded()
    assert "configured adapters for chatgpt, claude, gemini, and microsoft copilot" in public
    assert "live compatibility must be verified" in public
    assert "works with chatgpt" not in public


def test_claim_matrix_maps_corrections_to_source_and_production_boundaries():
    matrix = MATRIX_PATH.read_text(encoding="utf-8")
    for phrase in (
        "versioned consent receipt",
        "Public copy marks it not currently available",
        "Removed from active plan benefits",
        "Replaced with current, non-perpetual access wording",
        "Removed from public copy",
        "publication remains separately approval-gated",
    ):
        assert phrase in matrix

