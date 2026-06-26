from __future__ import annotations

from backend.rules import dashboard_rules
from backend.utils.config_loader import load_scoring_config
from tests.fixtures import bad_page, clean_page

THRESHOLDS = load_scoring_config()["thresholds"]
MAX_KPI   = THRESHOLDS["dashboard"]["max_kpi_cards"]
MIN_WS    = THRESHOLDS["dashboard"]["min_whitespace_ratio"]


def rule_ids(issues) -> list[str]:
    return [i.rule_id for i in issues]


class TestCleanPage:
    def test_no_dashboard_issues(self):
        issues = dashboard_rules.analyze(clean_page(), THRESHOLDS)
        assert issues == [], f"Unexpected issues: {rule_ids(issues)}"


class TestKpiCardOverload:
    def test_above_max_kpi_flagged(self):
        page = clean_page()
        page["kpi_card_count"] = MAX_KPI + 1
        issues = dashboard_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "D1_kpi_card_overload" for i in issues)

    def test_at_max_kpi_not_flagged(self):
        page = clean_page()
        page["kpi_card_count"] = MAX_KPI
        issues = dashboard_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "D1_kpi_card_overload" for i in issues)

    def test_below_max_kpi_not_flagged(self):
        page = clean_page()
        page["kpi_card_count"] = MAX_KPI - 1
        issues = dashboard_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "D1_kpi_card_overload" for i in issues)

    def test_zero_kpi_cards_not_flagged(self):
        page = clean_page()
        page["kpi_card_count"] = 0
        issues = dashboard_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "D1_kpi_card_overload" for i in issues)

    def test_count_appears_in_message(self):
        page = clean_page()
        page["kpi_card_count"] = 12
        issues = dashboard_rules.analyze(page, THRESHOLDS)
        d1 = next(i for i in issues if i.rule_id == "D1_kpi_card_overload")
        assert "12" in d1.message

    def test_severity_is_medium(self):
        from backend.models.issue import Severity
        page = clean_page()
        page["kpi_card_count"] = MAX_KPI + 1
        issues = dashboard_rules.analyze(page, THRESHOLDS)
        d1 = next(i for i in issues if i.rule_id == "D1_kpi_card_overload")
        assert d1.severity == Severity.MEDIUM

    def test_bad_page_triggers_d1(self):
        issues = dashboard_rules.analyze(bad_page(), THRESHOLDS)
        assert any(i.rule_id == "D1_kpi_card_overload" for i in issues)


class TestLowWhitespace:
    def test_below_min_whitespace_flagged(self):
        page = clean_page()
        page["whitespace_ratio"] = MIN_WS - 0.01
        issues = dashboard_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "D2_low_whitespace" for i in issues)

    def test_at_min_whitespace_not_flagged(self):
        page = clean_page()
        page["whitespace_ratio"] = MIN_WS
        issues = dashboard_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "D2_low_whitespace" for i in issues)

    def test_above_min_whitespace_not_flagged(self):
        page = clean_page()
        page["whitespace_ratio"] = MIN_WS + 0.10
        issues = dashboard_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "D2_low_whitespace" for i in issues)

    def test_zero_whitespace_flagged(self):
        page = clean_page()
        page["whitespace_ratio"] = 0.0
        issues = dashboard_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "D2_low_whitespace" for i in issues)

    def test_ratio_appears_in_evidence(self):
        page = clean_page()
        page["whitespace_ratio"] = 0.08
        issues = dashboard_rules.analyze(page, THRESHOLDS)
        d2 = next(i for i in issues if i.rule_id == "D2_low_whitespace")
        assert "0.08" in d2.evidence

    def test_severity_is_high(self):
        from backend.models.issue import Severity
        page = clean_page()
        page["whitespace_ratio"] = 0.05
        issues = dashboard_rules.analyze(page, THRESHOLDS)
        d2 = next(i for i in issues if i.rule_id == "D2_low_whitespace")
        assert d2.severity == Severity.HIGH

    def test_bad_page_triggers_d2(self):
        issues = dashboard_rules.analyze(bad_page(), THRESHOLDS)
        assert any(i.rule_id == "D2_low_whitespace" for i in issues)


class TestBothRulesFire:
    def test_dense_dashboard_with_many_kpis_triggers_both(self):
        page = clean_page()
        page["kpi_card_count"] = MAX_KPI + 5
        page["whitespace_ratio"] = 0.05
        issues = dashboard_rules.analyze(page, THRESHOLDS)
        fired = rule_ids(issues)
        assert "D1_kpi_card_overload" in fired
        assert "D2_low_whitespace" in fired
