from __future__ import annotations

from backend.rules import table_rules
from backend.utils.config_loader import load_scoring_config
from tests.fixtures import bad_page, clean_page

THRESHOLDS = load_scoring_config()["thresholds"]


def rule_ids(issues) -> list[str]:
    return [i.rule_id for i in issues]


class TestCleanPage:
    def test_no_table_issues(self):
        issues = table_rules.analyze(clean_page(), THRESHOLDS)
        assert issues == [], f"Unexpected issues: {rule_ids(issues)}"

    def test_no_tables_yields_no_issues(self):
        page = clean_page()
        page["tables"] = []
        assert table_rules.analyze(page, THRESHOLDS) == []


class TestMissingHeader:
    def test_table_without_thead_flagged(self):
        page = clean_page()
        page["tables"][0]["has_header"] = False
        issues = table_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "TBL1_missing_header" for i in issues)

    def test_table_with_header_not_flagged(self):
        page = clean_page()
        page["tables"][0]["has_header"] = True
        issues = table_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "TBL1_missing_header" for i in issues)

    def test_severity_is_high(self):
        from backend.models.issue import Severity
        page = clean_page()
        page["tables"][0]["has_header"] = False
        issues = table_rules.analyze(page, THRESHOLDS)
        tbl1 = next(i for i in issues if i.rule_id == "TBL1_missing_header")
        assert tbl1.severity == Severity.HIGH

    def test_bad_page_triggers_tbl1(self):
        issues = table_rules.analyze(bad_page(), THRESHOLDS)
        assert any(i.rule_id == "TBL1_missing_header" for i in issues)


class TestNoZebraStriping:
    def test_table_without_zebra_flagged(self):
        page = clean_page()
        page["tables"][0]["has_zebra_striping"] = False
        issues = table_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "TBL2_no_zebra" for i in issues)

    def test_table_with_zebra_not_flagged(self):
        page = clean_page()
        page["tables"][0]["has_zebra_striping"] = True
        issues = table_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "TBL2_no_zebra" for i in issues)

    def test_severity_is_low(self):
        from backend.models.issue import Severity
        page = clean_page()
        page["tables"][0]["has_zebra_striping"] = False
        issues = table_rules.analyze(page, THRESHOLDS)
        tbl2 = next(i for i in issues if i.rule_id == "TBL2_no_zebra")
        assert tbl2.severity == Severity.LOW

    def test_bad_page_triggers_tbl2(self):
        issues = table_rules.analyze(bad_page(), THRESHOLDS)
        assert any(i.rule_id == "TBL2_no_zebra" for i in issues)


class TestCellPadding:
    def test_low_cell_padding_flagged(self):
        page = clean_page()
        page["tables"][0]["cell_padding_px"] = 3.0
        issues = table_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "TBL3_cell_padding" for i in issues)

    def test_exact_threshold_not_flagged(self):
        page = clean_page()
        page["tables"][0]["cell_padding_px"] = float(
            THRESHOLDS["tables"]["min_cell_padding_px"]
        )
        issues = table_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "TBL3_cell_padding" for i in issues)

    def test_above_threshold_not_flagged(self):
        page = clean_page()
        page["tables"][0]["cell_padding_px"] = 16.0
        issues = table_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "TBL3_cell_padding" for i in issues)

    def test_zero_padding_flagged(self):
        page = clean_page()
        page["tables"][0]["cell_padding_px"] = 0.0
        issues = table_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "TBL3_cell_padding" for i in issues)

    def test_bad_page_triggers_tbl3(self):
        issues = table_rules.analyze(bad_page(), THRESHOLDS)
        assert any(i.rule_id == "TBL3_cell_padding" for i in issues)


class TestMultipleTables:
    def test_each_table_evaluated_independently(self):
        page = clean_page()
        page["tables"] = [
            {"has_header": True, "has_zebra_striping": True, "cell_padding_px": 12.0, "has_border": True},
            {"has_header": False, "has_zebra_striping": False, "cell_padding_px": 3.0, "has_border": False},
        ]
        issues = table_rules.analyze(page, THRESHOLDS)
        fired = rule_ids(issues)
        assert "TBL1_missing_header" in fired
        assert "TBL2_no_zebra" in fired
        assert "TBL3_cell_padding" in fired

    def test_label_includes_table_number(self):
        page = clean_page()
        page["tables"] = [
            {"has_header": False, "has_zebra_striping": True, "cell_padding_px": 12.0},
            {"has_header": False, "has_zebra_striping": True, "cell_padding_px": 12.0},
        ]
        issues = table_rules.analyze(page, THRESHOLDS)
        messages = [i.message for i in issues if i.rule_id == "TBL1_missing_header"]
        assert any("Table #1" in m for m in messages)
        assert any("Table #2" in m for m in messages)
