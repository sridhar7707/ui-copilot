"""
Module 14 — Dashboard Analyzer tests.

All tests are deterministic: no DB, no network, no file I/O beyond the
scoring config (loaded via config_loader).
"""
from __future__ import annotations

from backend.analyzers import dashboard_analyzer
from backend.utils.config_loader import load_scoring_config

_CFG = load_scoring_config()["thresholds"]


# ── helpers ───────────────────────────────────────────────────────────────────

def _page(**kwargs) -> dict:
    defaults = {
        "cards": [],
        "charts": [],
        "tables": [],
        "headings": [],
        "kpi_card_count": 0,
        "whitespace_ratio": 0.25,
        "spacing_values_px": [],
    }
    defaults.update(kwargs)
    return defaults


def _card() -> dict:
    return {"padding_px": 16}


def _table(cols: int = 4) -> dict:
    return {"column_count": cols, "row_count": 5, "has_header": True}


def _heading(level: int, size: float, text: str = "Title") -> dict:
    return {"level": level, "font_size_px": size, "text": text}


def _rule_ids(issues) -> set[str]:
    return {i.rule_id for i in issues}


# ── skip non-dashboard pages ──────────────────────────────────────────────────

class TestNotDashboard:
    def test_empty_page_returns_no_issues(self):
        issues = dashboard_analyzer.analyze(_page(), _CFG)
        assert issues == []

    def test_single_card_no_kpi_returns_no_issues(self):
        issues = dashboard_analyzer.analyze(_page(cards=[_card()], kpi_card_count=0), _CFG)
        assert issues == []

    def test_two_widgets_no_kpi_returns_no_issues(self):
        issues = dashboard_analyzer.analyze(
            _page(cards=[_card(), _card()], kpi_card_count=0), _CFG)
        assert issues == []


# ── DB1 — too many cards ──────────────────────────────────────────────────────

class TestDB1TooManyCards:
    def test_below_threshold_no_issue(self):
        page = _page(cards=[_card()] * 6, kpi_card_count=6,
                     headings=[_heading(1, 32)])
        ids = _rule_ids(dashboard_analyzer.analyze(page, _CFG))
        assert "DB1_too_many_cards" not in ids

    def test_at_threshold_no_issue(self):
        page = _page(cards=[_card()] * 8, kpi_card_count=8,
                     headings=[_heading(1, 32)])
        ids = _rule_ids(dashboard_analyzer.analyze(page, _CFG))
        assert "DB1_too_many_cards" not in ids

    def test_exceeds_threshold_fires(self):
        page = _page(cards=[_card()] * 9, kpi_card_count=9,
                     headings=[_heading(1, 32)])
        ids = _rule_ids(dashboard_analyzer.analyze(page, _CFG))
        assert "DB1_too_many_cards" in ids

    def test_issue_has_why_and_references(self):
        page = _page(kpi_card_count=10, headings=[_heading(1, 32)])
        issues = dashboard_analyzer.analyze(page, _CFG)
        issue = next(i for i in issues if i.rule_id == "DB1_too_many_cards")
        assert issue.why
        assert issue.references


# ── DB2 — poor hierarchy ─────────────────────────────────────────────────────

class TestDB2PoorHierarchy:
    def test_no_headings_fires(self):
        page = _page(kpi_card_count=4)
        ids = _rule_ids(dashboard_analyzer.analyze(page, _CFG))
        assert "DB2_poor_hierarchy" in ids

    def test_flat_hierarchy_fires(self):
        # h1=20px, h2=18px → ratio 1.11 < 1.3
        page = _page(kpi_card_count=4, headings=[
            _heading(1, 20), _heading(2, 18),
        ])
        ids = _rule_ids(dashboard_analyzer.analyze(page, _CFG))
        assert "DB2_poor_hierarchy" in ids

    def test_good_hierarchy_no_issue(self):
        # h1=32px, h2=20px → ratio 1.6 >= 1.3
        page = _page(kpi_card_count=4, headings=[
            _heading(1, 32), _heading(2, 20),
        ])
        ids = _rule_ids(dashboard_analyzer.analyze(page, _CFG))
        assert "DB2_poor_hierarchy" not in ids

    def test_h1_only_no_issue(self):
        page = _page(kpi_card_count=4, headings=[_heading(1, 28)])
        ids = _rule_ids(dashboard_analyzer.analyze(page, _CFG))
        assert "DB2_poor_hierarchy" not in ids


# ── DB3 — crowded layout ──────────────────────────────────────────────────────

class TestDB3CrowdedLayout:
    def test_below_widget_threshold_no_issue(self):
        page = _page(
            cards=[_card()] * 4,
            charts=[{"type": "bar"}] * 4,
            tables=[_table()] * 3,
            kpi_card_count=1,
            headings=[_heading(1, 32)],
        )
        ids = _rule_ids(dashboard_analyzer.analyze(page, _CFG))
        assert "DB3_crowded_layout" not in ids

    def test_exceeds_widget_threshold_fires(self):
        page = _page(
            cards=[_card()] * 6,
            charts=[{"type": "bar"}] * 4,
            tables=[_table()] * 3,
            kpi_card_count=1,
            headings=[_heading(1, 32)],
        )
        ids = _rule_ids(dashboard_analyzer.analyze(page, _CFG))
        assert "DB3_crowded_layout" in ids


# ── DB4 — weak KPI ───────────────────────────────────────────────────────────

class TestDB4WeakKPI:
    def test_no_kpi_cards_no_issue(self):
        page = _page(kpi_card_count=0, cards=[_card()] * 3)
        ids = _rule_ids(dashboard_analyzer.analyze(page, _CFG))
        assert "DB4_weak_kpi" not in ids

    def test_kpi_with_small_headings_fires(self):
        # kpi present but all headings < 24px
        page = _page(kpi_card_count=4, headings=[_heading(1, 18), _heading(2, 16)])
        ids = _rule_ids(dashboard_analyzer.analyze(page, _CFG))
        assert "DB4_weak_kpi" in ids

    def test_kpi_with_large_heading_no_issue(self):
        page = _page(kpi_card_count=4, headings=[_heading(1, 32)])
        ids = _rule_ids(dashboard_analyzer.analyze(page, _CFG))
        assert "DB4_weak_kpi" not in ids


# ── DB5 — dense tables ────────────────────────────────────────────────────────

class TestDB5DenseTables:
    def test_narrow_table_no_issue(self):
        page = _page(tables=[_table(6)], kpi_card_count=1,
                     headings=[_heading(1, 32)])
        ids = _rule_ids(dashboard_analyzer.analyze(page, _CFG))
        assert "DB5_dense_tables" not in ids

    def test_wide_table_fires(self):
        page = _page(tables=[_table(10)], kpi_card_count=1,
                     headings=[_heading(1, 32)])
        ids = _rule_ids(dashboard_analyzer.analyze(page, _CFG))
        assert "DB5_dense_tables" in ids

    def test_mixed_tables_fires_if_any_wide(self):
        page = _page(tables=[_table(4), _table(9)], kpi_card_count=1,
                     headings=[_heading(1, 32)])
        ids = _rule_ids(dashboard_analyzer.analyze(page, _CFG))
        assert "DB5_dense_tables" in ids


# ── DB6 — no section headings ─────────────────────────────────────────────────

class TestDB6NoSectionHeadings:
    def test_4_widgets_no_h2_fires(self):
        page = _page(
            cards=[_card()] * 2, charts=[{}] * 2, kpi_card_count=1,
            headings=[_heading(1, 32)],
        )
        ids = _rule_ids(dashboard_analyzer.analyze(page, _CFG))
        assert "DB6_no_section_headings" in ids

    def test_4_widgets_with_h2_no_issue(self):
        page = _page(
            cards=[_card()] * 2, charts=[{}] * 2, kpi_card_count=1,
            headings=[_heading(1, 32), _heading(2, 22, "Overview")],
        )
        ids = _rule_ids(dashboard_analyzer.analyze(page, _CFG))
        assert "DB6_no_section_headings" not in ids

    def test_3_widgets_no_h2_no_issue(self):
        # threshold is 4+
        page = _page(
            cards=[_card()] * 2, charts=[{}], kpi_card_count=1,
            headings=[_heading(1, 32)],
        )
        ids = _rule_ids(dashboard_analyzer.analyze(page, _CFG))
        assert "DB6_no_section_headings" not in ids


# ── issue shape ───────────────────────────────────────────────────────────────

class TestIssueShape:
    def test_all_issues_have_why_and_references(self):
        page = _page(
            kpi_card_count=10,
            cards=[_card()] * 15,
            charts=[{}] * 5,
            tables=[_table(12)],
            headings=[_heading(1, 16), _heading(2, 15)],
        )
        issues = dashboard_analyzer.analyze(page, _CFG)
        assert issues
        for issue in issues:
            assert issue.why, f"{issue.rule_id} missing why"
            assert issue.references, f"{issue.rule_id} missing references"
