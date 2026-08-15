import re
from pathlib import Path


ROOT = Path(__file__).parents[2]
POPUP = (ROOT / "extension/popup/popup.html").read_text(encoding="utf-8")
LOGIN = (ROOT / "extension/popup/login.html").read_text(encoding="utf-8")
LOGIN_JS = (ROOT / "extension/popup/login.js").read_text(encoding="utf-8")
CONTENT = (ROOT / "extension/content/content.js").read_text(encoding="utf-8")
DASHBOARD = (ROOT / "extension/dashboard/index.html").read_text(encoding="utf-8")
DASHBOARD_JS = (ROOT / "extension/dashboard/dashboard.js").read_text(encoding="utf-8")


def test_popup_toggles_have_programmatic_names_and_descriptions():
    for prefix in ("capture", "inject"):
        assert f'id="{prefix}-label"' in POPUP
        assert f'id="{prefix}-description"' in POPUP
        assert f'aria-labelledby="{prefix}-label"' in POPUP
        assert f'aria-describedby="{prefix}-description"' in POPUP
    assert "width:0;height:0" not in POPUP.replace(" ", "")


def test_login_labels_are_associated_and_navigation_is_native():
    for field in ("signin-email", "signin-password", "signup-email", "signup-password"):
        assert f'for="{field}"' in LOGIN
        assert f'id="{field}"' in LOGIN
    for control in ("goto-signup", "goto-signin", "skip-login"):
        assert re.search(rf'<button[^>]+id="{control}"', LOGIN)
        assert f'<span id="{control}"' not in LOGIN


def test_errors_statuses_and_counts_are_live_regions():
    assert 'id="error-msg" role="alert" aria-live="assertive"' in LOGIN
    assert 'id="memory-count" role="status" aria-live="polite"' in POPUP
    assert 'id="site-badge" role="status" aria-live="polite"' in POPUP
    for status_id in ("conn-status", "clear-status"):
        assert re.search(rf'id="{status_id}"[^>]+role="status"[^>]+aria-live="polite"', DASHBOARD)
    assert "toast.setAttribute('role', 'status')" in CONTENT
    assert "toast.setAttribute('aria-live', 'polite')" in CONTENT


def test_injection_dialog_has_focus_trap_escape_and_restore():
    assert "aria-describedby" in CONTENT
    assert "e.key === 'Escape'" in CONTENT
    assert "e.key === 'Tab'" in CONTENT
    assert "e.shiftKey" in CONTENT
    assert "last.focus()" in CONTENT
    assert "first.focus()" in CONTENT
    assert "promptEl.focus()" in CONTENT


def test_visible_focus_indicators_exist():
    for source in (POPUP, LOGIN, CONTENT, DASHBOARD):
        assert ":focus-visible" in source
        assert "#fbbf24" in source


def test_dashboard_custom_toggles_are_keyboard_native_switches():
    for toggle_id in ("t-capture", "t-inject"):
        assert re.search(rf'<button[^>]+id="{toggle_id}"[^>]+role="switch"', DASHBOARD)
    assert "aria-checked" in DASHBOARD_JS
    assert "disabled = !hasConsent()" in DASHBOARD_JS


def test_dashboard_fields_and_search_have_accessible_names():
    assert 'aria-label="Filter memories"' in DASHBOARD
    assert 'aria-label="Search memories by meaning"' in DASHBOARD
    assert 'for="s-backend-url"' in DASHBOARD
    assert 'for="s-api-key"' in DASHBOARD


def _relative_luminance(hex_color):
    values = [int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in values]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(first, second):
    light, dark = sorted((_relative_luminance(first), _relative_luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def test_updated_secondary_text_and_focus_colors_meet_aa_targets():
    assert _contrast("#9ca3af", "#0d0d1a") >= 4.5
    assert _contrast("#fbbf24", "#0d0d1a") >= 3.0
