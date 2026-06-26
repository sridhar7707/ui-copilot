from __future__ import annotations

from backend.rules import button_rules
from backend.utils.config_loader import load_scoring_config
from tests.fixtures import bad_page, clean_page

THRESHOLDS = load_scoring_config()["thresholds"]


def rule_ids(issues) -> list[str]:
    return [i.rule_id for i in issues]


class TestCleanPage:
    def test_no_button_issues(self):
        issues = button_rules.analyze(clean_page(), THRESHOLDS)
        assert issues == []


class TestButtonStyleCount:
    def test_three_distinct_styles_flagged(self):
        page = clean_page()
        page["buttons"] = [
            {**page["buttons"][0], "background_color": "#ff0000"},
            {**page["buttons"][0], "background_color": "#00ff00"},
            {**page["buttons"][0], "background_color": "#0000ff"},
        ]
        issues = button_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "B1_button_style_count" for i in issues)

    def test_two_distinct_styles_allowed(self):
        issues = button_rules.analyze(clean_page(), THRESHOLDS)
        assert not any(i.rule_id == "B1_button_style_count" for i in issues)

    def test_bad_page_triggers_b1(self):
        issues = button_rules.analyze(bad_page(), THRESHOLDS)
        assert any(i.rule_id == "B1_button_style_count" for i in issues)


class TestBorderRadiusVariance:
    def test_large_variance_flagged(self):
        page = clean_page()
        page["buttons"][0]["border_radius_px"] = 2.0
        page["buttons"][1]["border_radius_px"] = 20.0
        issues = button_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "B2_border_radius_variance" for i in issues)

    def test_consistent_radius_passes(self):
        issues = button_rules.analyze(clean_page(), THRESHOLDS)
        assert not any(i.rule_id == "B2_border_radius_variance" for i in issues)


class TestFocusStyle:
    def test_missing_focus_flagged(self):
        page = clean_page()
        page["buttons"][0]["has_focus_style"] = False
        issues = button_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "B3_focus_style" for i in issues)

    def test_focus_present_passes(self):
        issues = button_rules.analyze(clean_page(), THRESHOLDS)
        assert not any(i.rule_id == "B3_focus_style" for i in issues)

    def test_bad_page_triggers_b3(self):
        issues = button_rules.analyze(bad_page(), THRESHOLDS)
        assert any(i.rule_id == "B3_focus_style" for i in issues)


class TestTouchTarget:
    def test_small_touch_target_flagged(self):
        page = clean_page()
        page["buttons"][0]["height_px"] = 28.0
        issues = button_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "B4_touch_target" for i in issues)

    def test_adequate_touch_target_passes(self):
        issues = button_rules.analyze(clean_page(), THRESHOLDS)
        assert not any(i.rule_id == "B4_touch_target" for i in issues)

    def test_no_buttons_returns_empty(self):
        page = clean_page()
        page["buttons"] = []
        issues = button_rules.analyze(page, THRESHOLDS)
        assert issues == []
