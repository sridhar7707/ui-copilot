from __future__ import annotations

from backend.rules import spacing_rules
from backend.utils.config_loader import load_scoring_config
from tests.fixtures import bad_page, clean_page

THRESHOLDS = load_scoring_config()["thresholds"]


def rule_ids(issues) -> list[str]:
    return [i.rule_id for i in issues]


class TestCleanPage:
    def test_no_spacing_issues(self):
        issues = spacing_rules.analyze(clean_page(), THRESHOLDS)
        spacing_ids = [i for i in rule_ids(issues) if i.startswith("S")]
        assert spacing_ids == [], f"Unexpected issues: {spacing_ids}"


class TestButtonPadding:
    def test_small_button_padding_flagged(self):
        page = clean_page()
        page["buttons"][0]["padding_top_px"] = 3.0
        page["buttons"][0]["padding_left_px"] = 5.0
        issues = spacing_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "S1_button_padding" for i in issues)

    def test_adequate_padding_not_flagged(self):
        page = clean_page()
        # padding_top=8, padding_left=16 — both meet thresholds
        issues = spacing_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "S1_button_padding" for i in issues)

    def test_bad_page_triggers_s1(self):
        issues = spacing_rules.analyze(bad_page(), THRESHOLDS)
        assert any(i.rule_id == "S1_button_padding" for i in issues)


class TestCardPadding:
    def test_small_card_padding_flagged(self):
        page = clean_page()
        page["cards"][0]["padding_top_px"] = 6.0
        page["cards"][0]["padding_left_px"] = 6.0
        page["cards"][0]["padding_right_px"] = 6.0
        page["cards"][0]["padding_bottom_px"] = 6.0
        issues = spacing_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "S2_card_padding" for i in issues)

    def test_adequate_card_padding_not_flagged(self):
        issues = spacing_rules.analyze(clean_page(), THRESHOLDS)
        assert not any(i.rule_id == "S2_card_padding" for i in issues)

    def test_bad_page_triggers_s2(self):
        issues = spacing_rules.analyze(bad_page(), THRESHOLDS)
        assert any(i.rule_id == "S2_card_padding" for i in issues)


class TestOffGridSpacing:
    def test_many_off_grid_values_flagged(self):
        page = clean_page()
        page["spacing_values_px"] = [7.0, 13.0, 11.0, 22.0, 5.0]
        issues = spacing_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "S3_off_grid_spacing" for i in issues)

    def test_on_grid_values_not_flagged(self):
        page = clean_page()
        page["spacing_values_px"] = [8.0, 16.0, 24.0, 32.0, 48.0]
        issues = spacing_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "S3_off_grid_spacing" for i in issues)

    def test_two_off_grid_values_tolerated(self):
        page = clean_page()
        page["spacing_values_px"] = [8.0, 16.0, 7.0, 13.0]  # only 2 off-grid
        issues = spacing_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "S3_off_grid_spacing" for i in issues)

    def test_zero_spacing_ignored(self):
        page = clean_page()
        page["spacing_values_px"] = [0.0, 0.0, 0.0]
        issues = spacing_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "S3_off_grid_spacing" for i in issues)
