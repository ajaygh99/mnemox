"""Non-destructive repository-state simulation for the B-08 dry run."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

# Fingerprints captured from merged B-10 baseline 4d448ac. A change to any
# protected runtime surface makes this documentation-only simulation fail.
PROTECTED_BASELINE = {
    "extension/manifest.json": "f9d8984b6c87bafed39dc34ecd642c02fefaf0cd6feb5d5289f05649908aadcf",
    "backend/main.py": "ac1e0d03ec532c687a5a5138edcd36b7e2a19ad5d205096593ac80256817b24f",
    "backend/database.py": "593f8da0f7143c45ce4a102878fe309c939a6fdc77fa8ace0ea51f4f4a1c9e1e",
    "backend/billing.py": "e36f33c5d4a0a5107324050a1a1bc8948440efde39ff768244ebc2fd36e72db7",
    "backend/requirements.txt": "a0830a53690a57bceeae241cb87c27b44afc0f7a61232036062bb65c50a633f4",
    "backend/supabase_schema.sql": "da632c122d568cc1970e555e2da37830c15c70da2b441bbe4e48cc21f286a952",
    "backend/supabase_schema_step7.sql": "9c858da2e870e6d72642e4dc0d9a7bffdb40ce9f3b6178558ea9981e092bc0ea",
    "product.config.json": "e1836d106382efef03fbd16e2ee6a1b591ad3a00ff2af9a58467f29896ea0b08",
    "railway.toml": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    ".github/workflows/autonomous-review.yml": "b6e0548f8eb8b57f54201e124055528120a0cedaf9f2a08190b7c8cc295039a6",
}


def sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def test_protected_product_and_operational_surfaces_match_b10_baseline():
    actual = {path: sha256(path) for path in PROTECTED_BASELINE}
    assert actual == PROTECTED_BASELINE


def test_extension_version_remains_0_1_22():
    manifest = json.loads((ROOT / "extension/manifest.json").read_text(encoding="utf-8"))
    assert manifest["version"] == "0.1.22"


def test_simulation_does_not_contain_live_side_effect_commands():
    source = Path(__file__).read_text(encoding="utf-8")
    prohibited = tuple(
        " ".join(parts)
        for parts in (
            ("railway", "up"),
            ("vercel", "deploy"),
            ("supabase", "db", "push"),
            ("chrome-webstore", "upload"),
            ("gh", "pr", "merge"),
        )
    )
    assert not any(command in source for command in prohibited)
    assert " ".join(("import", "subprocess")) not in source
    assert " ".join(("import", "requests")) not in source


def test_autonomous_workflow_does_not_execute_product_or_deployment_code():
    workflow = (ROOT / ".github/workflows/autonomous-review.yml").read_text(
        encoding="utf-8"
    )
    assert "actions/checkout" not in workflow
    assert "pytest" not in workflow
    assert "railway" not in workflow
    assert "vercel" not in workflow
    assert "supabase" not in workflow
    assert "stripe" not in workflow
    assert "npm publish" not in workflow


def test_phase1_remains_blocked_pending_separate_owner_decision():
    status = (ROOT / "governance/status/PHASE-0-STATUS.md").read_text(
        encoding="utf-8"
    )
    assert "Phase 0 exit is therefore **not approved**" in status
    assert "Phase 1" in status
    assert "remain disabled" in status
    assert "separately contracted and owner-authorized Phase 1 issue" in status


def test_dry_run_record_states_non_live_evidence_boundary():
    record = (ROOT / "governance/status/B-08-POST-MERGE-DRY-RUN.md").read_text(
        encoding="utf-8"
    )
    assert "deterministic repository-state simulation" in record
    assert "No production system was contacted" in record
    assert "does not authorize Phase 1" in record
