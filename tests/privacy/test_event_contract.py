import copy
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_event_contract import (  # noqa: E402
    EventValidationError,
    SCHEMA_PATH,
    load_contract,
    validate_event,
)


TIMESTAMP = "2026-08-12T17:30:00Z"
VALID_EVENTS = [
    {"schema_version": 1, "event_name": "install", "timestamp": TIMESTAMP,
     "extension_version": "0.1.22", "os": "windows", "browser": "chrome"},
    {"schema_version": 1, "event_name": "onboarding_started", "timestamp": TIMESTAMP,
     "step": "welcome"},
    {"schema_version": 1, "event_name": "onboarding_completed", "timestamp": TIMESTAMP,
     "duration_seconds": 45, "step_completed": "first_memory"},
    {"schema_version": 1, "event_name": "capture_result", "timestamp": TIMESTAMP,
     "source": "claude", "success": False, "error_code": "dom_timeout"},
    {"schema_version": 1, "event_name": "preview_decision", "timestamp": TIMESTAMP,
     "memories_shown": 2, "user_action": "approved"},
    {"schema_version": 1, "event_name": "injection_result", "timestamp": TIMESTAMP,
     "memories_injected": 1, "success": True, "error_code": None},
    {"schema_version": 1, "event_name": "feedback", "timestamp": TIMESTAMP,
     "type": "useful", "context": "after_injection"},
    {"schema_version": 1, "event_name": "error_event", "timestamp": TIMESTAMP,
     "error_code": "api_timeout", "source_component": "backend", "severity": "error"},
]


@pytest.mark.parametrize("event", VALID_EVENTS)
def test_all_approved_events_validate(event):
    assert validate_event(event) is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prompt_text", "Summarize my private plan"),
        ("response_text", "Here is the private response"),
        ("memory_id", "mem-123"),
        ("memory_content", "The user's home address"),
        ("email", "person@example.com"),
        ("api_key", "sk_test_not-a-real-key"),
        ("access_token", "secret-token"),
        ("source_code", "print('private')"),
        ("url", "https://example.com/private"),
        ("session_id", "deadbeef"),
        ("anonymous_session_hash", "deadbeef"),
        ("stack_trace", "private stack details"),
    ],
)
def test_prohibited_fields_are_rejected(field, value):
    event = copy.deepcopy(VALID_EVENTS[3])
    event[field] = value
    with pytest.raises(EventValidationError, match="Prohibited field"):
        validate_event(event)


@pytest.mark.parametrize(
    "value",
    [
        "person" + "@example.com",
        "gho_" + "not-a-real-token",
        "-----BEGIN " + "PRIVATE KEY-----",
    ],
)
def test_sensitive_patterns_are_rejected_even_under_unknown_key(value):
    event = copy.deepcopy(VALID_EVENTS[6])
    event["note"] = value
    with pytest.raises(EventValidationError, match="Prohibited value pattern"):
        validate_event(event)


def test_unknown_benign_field_is_rejected():
    event = copy.deepcopy(VALID_EVENTS[4])
    event["relevance_score"] = 0.9
    with pytest.raises(EventValidationError, match="Unknown fields"):
        validate_event(event)


@pytest.mark.parametrize("event_name", ["page_view", "raw_trace", ""])
def test_unknown_event_names_are_rejected(event_name):
    event = {"schema_version": 1, "event_name": event_name, "timestamp": TIMESTAMP}
    with pytest.raises(EventValidationError, match="Unknown event name"):
        validate_event(event)


@pytest.mark.parametrize("timestamp", ["2026-08-12", "2026-08-12T17:30:00", "not-a-date"])
def test_timestamp_requires_utc_z_format(timestamp):
    event = copy.deepcopy(VALID_EVENTS[0])
    event["timestamp"] = timestamp
    with pytest.raises(EventValidationError, match="Invalid format"):
        validate_event(event)


def test_boolean_is_not_accepted_as_integer_count():
    event = copy.deepcopy(VALID_EVENTS[4])
    event["memories_shown"] = True
    with pytest.raises(EventValidationError, match="must be an integer"):
        validate_event(event)


def test_contract_is_valid_json_and_defines_all_events():
    contract = load_contract()
    names = {
        item["properties"]["event_name"]["const"]
        for item in contract["oneOf"]
    }
    assert names == {event["event_name"] for event in VALID_EVENTS}
    assert json.loads(SCHEMA_PATH.read_text(encoding="utf-8")) == contract


def test_each_event_disallows_additional_properties():
    contract = load_contract()
    assert all(item.get("additionalProperties") is False for item in contract["oneOf"])
