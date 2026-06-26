from __future__ import annotations

from backend.rules import chart_rules
from backend.utils.config_loader import load_scoring_config
from tests.fixtures import bad_page, clean_page

THRESHOLDS = load_scoring_config()["thresholds"]
MIN_DIST = THRESHOLDS["charts"]["min_color_distance"]

# Color pairs with known distances for deterministic assertions
_SIMILAR   = ["#aaaaaa", "#b4b4b4"]   # delta=10 per channel → distance ≈ 17.3 < 30
_DISTINCT  = ["#005fcc", "#e65c00"]   # delta ~230 per channel → distance ≈ 307 >> 30


def rule_ids(issues) -> list[str]:
    return [i.rule_id for i in issues]


class TestCleanPage:
    def test_no_chart_issues(self):
        issues = chart_rules.analyze(clean_page(), THRESHOLDS)
        assert issues == [], f"Unexpected issues: {rule_ids(issues)}"

    def test_no_charts_yields_no_issues(self):
        page = clean_page()
        page["charts"] = []
        assert chart_rules.analyze(page, THRESHOLDS) == []


class TestMissingAxisLabels:
    def test_chart_without_axis_labels_flagged(self):
        page = clean_page()
        page["charts"][0]["has_axis_labels"] = False
        issues = chart_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "CH1_missing_axis_labels" for i in issues)

    def test_chart_with_axis_labels_not_flagged(self):
        page = clean_page()
        page["charts"][0]["has_axis_labels"] = True
        issues = chart_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "CH1_missing_axis_labels" for i in issues)

    def test_severity_is_medium(self):
        from backend.models.issue import Severity
        page = clean_page()
        page["charts"][0]["has_axis_labels"] = False
        issues = chart_rules.analyze(page, THRESHOLDS)
        ch1 = next(i for i in issues if i.rule_id == "CH1_missing_axis_labels")
        assert ch1.severity == Severity.MEDIUM

    def test_bad_page_triggers_ch1(self):
        issues = chart_rules.analyze(bad_page(), THRESHOLDS)
        assert any(i.rule_id == "CH1_missing_axis_labels" for i in issues)


class TestSimilarChartColors:
    def test_similar_colors_flagged(self):
        page = clean_page()
        page["charts"][0]["colors"] = _SIMILAR
        issues = chart_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "CH2_similar_chart_colors" for i in issues)

    def test_distinct_colors_not_flagged(self):
        page = clean_page()
        page["charts"][0]["colors"] = _DISTINCT
        issues = chart_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "CH2_similar_chart_colors" for i in issues)

    def test_single_color_not_flagged(self):
        page = clean_page()
        page["charts"][0]["colors"] = ["#005fcc"]
        issues = chart_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "CH2_similar_chart_colors" for i in issues)

    def test_empty_colors_not_flagged(self):
        page = clean_page()
        page["charts"][0]["colors"] = []
        issues = chart_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "CH2_similar_chart_colors" for i in issues)

    def test_three_similar_grays_flagged(self):
        page = clean_page()
        page["charts"][0]["colors"] = ["#cccccc", "#d5d5d5", "#bbbbbb"]
        issues = chart_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "CH2_similar_chart_colors" for i in issues)

    def test_mixed_colors_one_similar_pair_flagged(self):
        page = clean_page()
        # #005fcc and #e65c00 are distinct; #aaaaaa and #b4b4b4 are similar
        page["charts"][0]["colors"] = ["#005fcc", "#aaaaaa", "#b4b4b4"]
        issues = chart_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "CH2_similar_chart_colors" for i in issues)

    def test_severity_is_medium(self):
        from backend.models.issue import Severity
        page = clean_page()
        page["charts"][0]["colors"] = _SIMILAR
        issues = chart_rules.analyze(page, THRESHOLDS)
        ch2 = next(i for i in issues if i.rule_id == "CH2_similar_chart_colors")
        assert ch2.severity == Severity.MEDIUM

    def test_bad_page_triggers_ch2(self):
        issues = chart_rules.analyze(bad_page(), THRESHOLDS)
        assert any(i.rule_id == "CH2_similar_chart_colors" for i in issues)


class TestMultipleCharts:
    def test_each_chart_evaluated_independently(self):
        page = clean_page()
        page["charts"] = [
            {"has_axis_labels": True,  "colors": _DISTINCT},
            {"has_axis_labels": False, "colors": _SIMILAR},
        ]
        issues = chart_rules.analyze(page, THRESHOLDS)
        fired = rule_ids(issues)
        assert "CH1_missing_axis_labels" in fired
        assert "CH2_similar_chart_colors" in fired

    def test_label_includes_chart_number(self):
        page = clean_page()
        page["charts"] = [
            {"has_axis_labels": False, "colors": _DISTINCT},
            {"has_axis_labels": False, "colors": _DISTINCT},
        ]
        issues = chart_rules.analyze(page, THRESHOLDS)
        messages = [i.message for i in issues if i.rule_id == "CH1_missing_axis_labels"]
        assert any("Chart #1" in m for m in messages)
        assert any("Chart #2" in m for m in messages)
