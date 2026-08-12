# Mnemox event privacy contract

Status: design and validation contract only. Event collection is not activated by this document or its validator.

## Boundary

Mnemox events may describe only a predefined product action using enums, bounded counts or durations, a UTC timestamp, and a version number. They must not contain user content or a stable identifier. Unknown event names, fields, values, and types fail closed.

The canonical machine-readable contract is `contracts/events/event.schema.json`. `scripts/validate_event_contract.py` validates the supported schema subset without collecting, storing, hashing, or transmitting anything.

## Approved events

| Event | Approved information |
|---|---|
| `install` | Extension version, operating-system enum, browser enum |
| `onboarding_started` | Current approved step enum |
| `onboarding_completed` | Bounded duration and completed-step enum |
| `capture_result` | Supported-source enum, success boolean, safe error-code enum |
| `preview_decision` | Bounded count shown and approved/rejected/edited enum |
| `injection_result` | Bounded count injected, success boolean, safe error-code enum |
| `feedback` | Useful/not-useful/error enum and interaction-context enum |
| `error_event` | Safe error-code, component, and severity enums |

Every event also contains `schema_version: 1`, an exact approved `event_name`, and an ISO 8601 UTC timestamp ending in `Z`. There is no timezone, locale, URL, or location property.

## Prohibited data

No event may include:

- prompt or response text, including excerpts;
- memory content, memory IDs, provenance text, or relevance scores;
- names, email addresses, usernames, account IDs, or other personal data;
- user, session, installation, device, project, or anonymous correlation IDs;
- API keys, tokens, credentials, secrets, or private keys;
- source code, file content, terminal content, or repository content;
- browser history, page URLs, IP addresses, locale, or timezone;
- stack traces, exception messages, or other free-form diagnostics;
- unapproved fields hidden under generic names such as `metadata`, `note`, or `properties`.

An eight-character hash is not anonymous enough to include by default: it is still a stable correlation identifier and may collide. It remains deferred until an approved design defines necessity, consent, salt lifecycle, retention, deletion, and isolation.

## Validation behavior

The validator rejects:

- unknown event names or schema versions;
- missing or additional fields;
- malformed timestamps;
- values outside approved enums;
- booleans used as integer counts;
- negative or unbounded counts and durations;
- prohibited field names; and
- recognizable email, credential, token, or private-key patterns.

Key filtering is defense in depth. The primary privacy control is the per-event allowlist with `additionalProperties: false`.

## Developer use

Validate an in-memory event before any future approved transport boundary:

```python
from scripts.validate_event_contract import EventValidationError, validate_event

try:
    validate_event(candidate)
except EventValidationError:
    # Drop the event and increment no content-bearing diagnostic.
    pass
```

Do not log the rejected event or exception alongside user data. Tests belong in `tests/privacy/` and must include negative cases for every proposed field expansion.

## Change and approval policy

Adding an event, field, enum value, identifier, retention rule, transport, vendor, endpoint, or persistence layer requires a new reviewed issue and privacy/security evidence. Activating telemetry, changing consent, or publishing privacy text requires exact owner approval. A schema merge alone never authorizes collection.
