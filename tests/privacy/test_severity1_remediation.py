from pathlib import Path


ROOT = Path(__file__).parents[2]
SERVICE_WORKER = (ROOT / "extension/background/service_worker.js").read_text(encoding="utf-8")
CONTENT = (ROOT / "extension/content/content.js").read_text(encoding="utf-8")
POPUP_JS = (ROOT / "extension/popup/popup.js").read_text(encoding="utf-8")
POPUP_HTML = (ROOT / "extension/popup/popup.html").read_text(encoding="utf-8")


def test_fresh_install_defaults_sensitive_features_off():
    defaults = SERVICE_WORKER.split("const defaults = {", 1)[1].split("};", 1)[0]
    assert "captureEnabled: false" in defaults
    assert "injectEnabled: false" in defaults
    assert "consentReceipt: null" in defaults


def test_versioned_timestamped_consent_receipt_is_required():
    for source in (SERVICE_WORKER, CONTENT, POPUP_JS):
        assert "consentReceipt" in source
    assert "receipt.version === 1" in SERVICE_WORKER
    assert "acceptedAt" in SERVICE_WORKER
    assert "new Date().toISOString()" in POPUP_JS
    assert "Informed consent is required" in SERVICE_WORKER
    assert "sender.url !== popupUrl" in SERVICE_WORKER


def test_popup_explains_consent_and_supports_withdrawal():
    assert "Both remain off until you agree" in POPUP_HTML
    assert 'id="consent-checkbox"' in POPUP_HTML
    assert 'id="consent-btn"' in POPUP_HTML
    assert 'id="withdraw-consent-btn"' in POPUP_HTML
    assert "consentReceipt: null, captureEnabled: false, injectEnabled: false" in POPUP_JS
    assert "notifyActiveTab(patch)" in POPUP_JS


def test_content_script_fail_closed_without_consent():
    assert "!hasValidConsent() || !settings.captureEnabled" in CONTENT
    assert "!hasValidConsent() || !settings.injectEnabled" in CONTENT


def test_preview_offers_approve_reject_edit_and_cancel_before_mutation():
    assert "showInjectionPreview(memories" in CONTENT
    assert "Review memories before sending" in CONTENT
    assert "Proposed memory context" in CONTENT
    assert "Approve and send" in CONTENT
    assert "Send without memories" in CONTENT
    assert ">Return</button>" in CONTENT
    preview_index = CONTENT.index("showInjectionPreview(memories")
    mutation_index = CONTENT.index("config.setPromptText(promptEl, enriched)", preview_index)
    assert preview_index < mutation_index


def test_keyboard_and_button_submission_both_use_preview_gate():
    assert CONTENT.count("injectMemoriesIntoPrompt(promptEl, text") >= 2
    assert "if (cancelled) return" in CONTENT


def test_prompt_content_is_not_exposed_in_diagnostics_or_toasts():
    prohibited = [
        "stored.slice(0, 60)",
        "text.slice(0, 60)",
        "text.slice(0, 45)",
        "JSON.stringify(text",
        "JSON.stringify(original)",
        "payload && (payload.content",
        "outerHTML.slice",
    ]
    combined = CONTENT + SERVICE_WORKER
    for expression in prohibited:
        assert expression not in combined
    assert "Prompt content is hidden from diagnostics" in CONTENT


def test_existing_storage_is_preserved():
    assert "if (!(key in existing)) patch[key] = defaults[key]" in SERVICE_WORKER
