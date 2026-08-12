import json
from pathlib import Path


ROOT = Path(__file__).parents[2]
STUDY = ROOT / "docs" / "research" / "first-use"


def read(name):
    return (STUDY / name).read_text(encoding="utf-8")


def test_required_study_artifacts_exist():
    required = {
        "PROTOCOL.md", "CONSENT.md", "DATA-POLICY.md", "RESULTS-TEMPLATE.md",
        "participant-observation.template.json",
    }
    assert required <= {path.name for path in STUDY.iterdir()}


def test_protocol_targets_exactly_five_and_defines_non_coaching():
    protocol = read("PROTOCOL.md")
    assert "exactly five consenting participants" in protocol
    assert "P01" in protocol and "P05" in protocol
    assert "No pointing, feature naming, navigation hint" in protocol
    assert "120 seconds" in protocol


def test_protocol_has_required_tasks_and_severity_one_blocker():
    protocol = read("PROTOCOL.md")
    for code in ("T1_TRUST", "T2_SUPPORT", "T3_FIRST_VALUE", "T4_DECISION", "T5_RECOVERY", "T6_COMPREHENSION"):
        assert code in protocol
    assert "severity-1 data/control failure" in protocol
    assert "Phase 0 exit blocked" in protocol


def test_consent_covers_voluntary_withdrawal_no_recording_and_deletion():
    consent = read("CONSENT.md")
    for phrase in ("Participation is voluntary", "stop at any time", "will not record audio, video, or your screen", "deleted within two business days", "30 days"):
        assert phrase in consent


def test_data_policy_defines_access_retention_and_incident_stop():
    policy = read("DATA-POLICY.md")
    for phrase in ("study owner and independent reviewer", "30 calendar days", "two business days", "stop the session", "PROHIBITED_DATA_CAPTURED", "confirm deletion"):
        assert phrase in policy


def test_results_separate_observations_hypotheses_and_decisions():
    results = read("RESULTS-TEMPLATE.md")
    for heading in ("## Observations", "## Hypotheses", "## Decisions and approvals", "## Privacy and deletion attestation"):
        assert heading in results


def test_observation_template_is_structured_and_content_free():
    template = json.loads(read("participant-observation.template.json"))
    assert template["participant_code"] == "P01"
    assert template["consent"]["status"] == "accepted"
    assert isinstance(template["tasks"], list)

    prohibited_fragments = {
        "name", "email", "username", "prompt", "response", "memory_id",
        "memory_text", "content", "credential", "token", "api_key", "url",
        "ip", "device_id", "session_id", "recording", "screenshot", "transcript",
        "free_text", "notes",
    }

    def keys(value):
        if isinstance(value, dict):
            for key, child in value.items():
                yield key.casefold()
                yield from keys(child)
        elif isinstance(value, list):
            for child in value:
                yield from keys(child)

    template_keys = set(keys(template))
    assert not {
        key for key in template_keys
        if any(fragment == key or key.startswith(fragment + "_") for fragment in prohibited_fragments)
    }


def test_template_contains_only_approved_top_level_fields():
    template = json.loads(read("participant-observation.template.json"))
    assert set(template) == {
        "schema_version", "participant_code", "consent", "approved_build_sha",
        "product_version", "session_status", "tasks", "protocol_deviation_codes",
        "prohibited_data_incident", "deletion_deadline_utc_date", "review_status",
    }
