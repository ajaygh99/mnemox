"""Fail-closed validator for the content-free Mnemox event contract.

This module validates event-shaped dictionaries only. It does not collect, persist,
transmit, hash, or otherwise process a user identifier or user content.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


SCHEMA_PATH = Path(__file__).parents[1] / "contracts" / "events" / "event.schema.json"

PROHIBITED_KEY_FRAGMENTS = {
    "prompt", "response", "memory_id", "memory_text", "memory_content",
    "email", "username", "user_id", "session_id", "anonymous_session_hash", "installation_id",
    "device_id", "project_id", "api_key", "token", "credential", "secret",
    "source_code", "file_content", "stack", "traceback", "url", "history",
    "ip_address", "locale", "timezone",
}

PROHIBITED_VALUE_PATTERNS = (
    re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE),
    re.compile(r"\b(?:gho_|github_pat_|sk_(?:live|test)_|whsec_)[A-Za-z0-9_-]+"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
)


class EventValidationError(ValueError):
    """Raised when an event violates the approved content-free contract."""


def load_contract(path: Path = SCHEMA_PATH) -> dict[str, Any]:
    with path.open(encoding="utf-8") as contract_file:
        return json.load(contract_file)


def _event_schemas(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    schemas: dict[str, dict[str, Any]] = {}
    for candidate in contract.get("oneOf", []):
        name = candidate.get("properties", {}).get("event_name", {}).get("const")
        if isinstance(name, str):
            schemas[name] = candidate
    if not schemas:
        raise EventValidationError("Contract contains no event definitions")
    return schemas


def _reject_prohibited_data(event: dict[str, Any]) -> None:
    for key, value in event.items():
        normalized = key.casefold()
        if any(fragment in normalized for fragment in PROHIBITED_KEY_FRAGMENTS):
            raise EventValidationError(f"Prohibited field: {key}")
        if isinstance(value, str):
            for pattern in PROHIBITED_VALUE_PATTERNS:
                if pattern.search(value):
                    raise EventValidationError(f"Prohibited value pattern in field: {key}")


def _validate_value(field: str, value: Any, rules: dict[str, Any]) -> None:
    if "const" in rules and value != rules["const"]:
        raise EventValidationError(f"Invalid constant for {field}")
    if "enum" in rules and value not in rules["enum"]:
        raise EventValidationError(f"Invalid enum value for {field}")

    expected = rules.get("type")
    if expected == "string" and not isinstance(value, str):
        raise EventValidationError(f"{field} must be a string")
    if expected == "boolean" and not isinstance(value, bool):
        raise EventValidationError(f"{field} must be a boolean")
    if expected == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
        raise EventValidationError(f"{field} must be an integer")

    if isinstance(value, str) and "pattern" in rules:
        if re.fullmatch(rules["pattern"], value) is None:
            raise EventValidationError(f"Invalid format for {field}")
    if isinstance(value, int) and not isinstance(value, bool):
        if "minimum" in rules and value < rules["minimum"]:
            raise EventValidationError(f"{field} is below its minimum")
        if "maximum" in rules and value > rules["maximum"]:
            raise EventValidationError(f"{field} exceeds its maximum")


def validate_event(event: Any, contract: dict[str, Any] | None = None) -> None:
    """Validate one event or raise ``EventValidationError``.

    Unknown fields and event types fail closed. Successful validation returns None.
    """
    if not isinstance(event, dict):
        raise EventValidationError("Event must be an object")
    if not all(isinstance(key, str) for key in event):
        raise EventValidationError("Event field names must be strings")

    _reject_prohibited_data(event)
    schemas = _event_schemas(contract or load_contract())
    event_name = event.get("event_name")
    if event_name not in schemas:
        raise EventValidationError("Unknown event name")

    schema = schemas[event_name]
    required = set(schema.get("required", []))
    missing = required - event.keys()
    if missing:
        raise EventValidationError(f"Missing required fields: {', '.join(sorted(missing))}")

    properties = schema.get("properties", {})
    unknown = event.keys() - properties.keys()
    if unknown:
        raise EventValidationError(f"Unknown fields: {', '.join(sorted(unknown))}")

    for field, value in event.items():
        _validate_value(field, value, properties[field])
