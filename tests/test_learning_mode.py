"""
Module 8 — Learning Mode: every issue must carry a non-empty `why` and at least
one `references` entry.  Tests run each rule file individually against a synthetic
bad_page so we know exactly which rule_id produced each issue.
"""
from __future__ import annotations

import pytest

from backend.models.issue import Issue
from backend.rules import (
    button_rules,
    chart_rules,
    contrast_rules,
    dashboard_rules,
    form_rules,
    spacing_rules,
    table_rules,
    typography_rules,
)
from tests.fixtures import bad_page


# ── helpers ───────────────────────────────────────────────────────────────────

@pytest.fixture
def bad() -> dict:
    return bad_page()


@pytest.fixture
def thresholds() -> dict:
    import json
    import pathlib
    cfg = pathlib.Path("config/scoring.json").read_text()
    return json.loads(cfg)["thresholds"]


def _assert_has_learning(issue: Issue) -> None:
    assert issue.why, f"{issue.rule_id} has empty 'why'"
    assert issue.references, f"{issue.rule_id} has empty 'references'"


# ── spacing ───────────────────────────────────────────────────────────────────

class TestSpacingLearning:
    def test_s1_has_why_and_refs(self, bad, thresholds):
        issues = spacing_rules.analyze(bad, thresholds)
        s1 = [i for i in issues if i.rule_id == "S1_button_padding"]
        assert s1, "S1 should fire on bad_page"
        for i in s1:
            _assert_has_learning(i)

    def test_s2_has_why_and_refs(self, bad, thresholds):
        issues = spacing_rules.analyze(bad, thresholds)
        s2 = [i for i in issues if i.rule_id == "S2_card_padding"]
        assert s2, "S2 should fire on bad_page"
        _assert_has_learning(s2[0])

    def test_s3_has_why_and_refs(self, bad, thresholds):
        issues = spacing_rules.analyze(bad, thresholds)
        s3 = [i for i in issues if i.rule_id == "S3_off_grid_spacing"]
        assert s3, "S3 should fire on bad_page"
        _assert_has_learning(s3[0])


# ── typography ────────────────────────────────────────────────────────────────

class TestTypographyLearning:
    def test_t1_has_why_and_refs(self, bad, thresholds):
        issues = typography_rules.analyze(bad, thresholds)
        t1 = [i for i in issues if i.rule_id == "T1_body_font_size"]
        assert t1
        _assert_has_learning(t1[0])

    def test_t2_has_why_and_refs(self, bad, thresholds):
        issues = typography_rules.analyze(bad, thresholds)
        t2 = [i for i in issues if i.rule_id == "T2_font_family_count"]
        assert t2
        _assert_has_learning(t2[0])

    def test_t3_has_why_and_refs(self, bad, thresholds):
        issues = typography_rules.analyze(bad, thresholds)
        t3 = [i for i in issues if i.rule_id == "T3_line_height"]
        assert t3
        _assert_has_learning(t3[0])

    def test_t4_has_why_and_refs(self, bad, thresholds):
        issues = typography_rules.analyze(bad, thresholds)
        t4 = [i for i in issues if i.rule_id == "T4_heading_hierarchy"]
        assert t4
        _assert_has_learning(t4[0])

    def test_t5_has_why_and_refs(self, thresholds):
        page = {"fonts": [], "headings": [{"level": 1, "font_size_px": 14.0, "text": "Title"}],
                "body_font_size_px": None, "line_height": None}
        issues = typography_rules.analyze(page, thresholds)
        t5 = [i for i in issues if i.rule_id == "T5_heading_size"]
        assert t5, "T5 should fire when H1 is below min_heading_size_px"
        _assert_has_learning(t5[0])


# ── contrast ──────────────────────────────────────────────────────────────────

class TestContrastLearning:
    def test_c1_contrast_has_why_and_refs(self, bad, thresholds):
        issues = contrast_rules.analyze(bad, thresholds)
        c1 = [i for i in issues if i.rule_id == "C1_wcag_aa_contrast"]
        assert c1
        _assert_has_learning(c1[0])

    def test_c1_a11y_has_why_and_refs(self, bad, thresholds):
        issues = contrast_rules.analyze(bad, thresholds)
        c1a = [i for i in issues if i.rule_id == "C1_wcag_aa_contrast_a11y"]
        assert c1a
        _assert_has_learning(c1a[0])


# ── buttons ───────────────────────────────────────────────────────────────────

class TestButtonLearning:
    def test_b1_has_why_and_refs(self, bad, thresholds):
        issues = button_rules.analyze(bad, thresholds)
        b1 = [i for i in issues if i.rule_id == "B1_button_style_count"]
        assert b1
        _assert_has_learning(b1[0])

    def test_b2_has_why_and_refs(self, bad, thresholds):
        issues = button_rules.analyze(bad, thresholds)
        b2 = [i for i in issues if i.rule_id == "B2_border_radius_variance"]
        assert b2
        _assert_has_learning(b2[0])

    def test_b3_has_why_and_refs(self, bad, thresholds):
        issues = button_rules.analyze(bad, thresholds)
        b3 = [i for i in issues if i.rule_id == "B3_focus_style"]
        assert b3
        _assert_has_learning(b3[0])

    def test_b4_has_why_and_refs(self, bad, thresholds):
        issues = button_rules.analyze(bad, thresholds)
        b4 = [i for i in issues if i.rule_id == "B4_touch_target"]
        assert b4
        _assert_has_learning(b4[0])


# ── tables ────────────────────────────────────────────────────────────────────

class TestTableLearning:
    def test_tbl1_has_why_and_refs(self, bad, thresholds):
        issues = table_rules.analyze(bad, thresholds)
        tbl1 = [i for i in issues if i.rule_id == "TBL1_missing_header"]
        assert tbl1
        _assert_has_learning(tbl1[0])

    def test_tbl2_has_why_and_refs(self, bad, thresholds):
        issues = table_rules.analyze(bad, thresholds)
        tbl2 = [i for i in issues if i.rule_id == "TBL2_no_zebra"]
        assert tbl2
        _assert_has_learning(tbl2[0])

    def test_tbl3_has_why_and_refs(self, bad, thresholds):
        issues = table_rules.analyze(bad, thresholds)
        tbl3 = [i for i in issues if i.rule_id == "TBL3_cell_padding"]
        assert tbl3
        _assert_has_learning(tbl3[0])


# ── forms ─────────────────────────────────────────────────────────────────────

class TestFormLearning:
    def test_f1_has_why_and_refs(self, bad, thresholds):
        issues = form_rules.analyze(bad, thresholds)
        f1 = [i for i in issues if i.rule_id == "F1_missing_label"]
        assert f1
        _assert_has_learning(f1[0])

    def test_f2_has_why_and_refs(self, bad, thresholds):
        issues = form_rules.analyze(bad, thresholds)
        f2 = [i for i in issues if i.rule_id == "F2_placeholder_as_label"]
        assert f2
        _assert_has_learning(f2[0])

    def test_f3_has_why_and_refs(self, bad, thresholds):
        issues = form_rules.analyze(bad, thresholds)
        f3 = [i for i in issues if i.rule_id == "F3_input_padding"]
        assert f3
        _assert_has_learning(f3[0])


# ── charts ────────────────────────────────────────────────────────────────────

class TestChartLearning:
    def test_ch1_has_why_and_refs(self, bad, thresholds):
        issues = chart_rules.analyze(bad, thresholds)
        ch1 = [i for i in issues if i.rule_id == "CH1_missing_axis_labels"]
        assert ch1
        _assert_has_learning(ch1[0])

    def test_ch2_has_why_and_refs(self, bad, thresholds):
        issues = chart_rules.analyze(bad, thresholds)
        ch2 = [i for i in issues if i.rule_id == "CH2_similar_chart_colors"]
        assert ch2
        _assert_has_learning(ch2[0])


# ── dashboard ─────────────────────────────────────────────────────────────────

class TestDashboardLearning:
    def test_d1_has_why_and_refs(self, bad, thresholds):
        issues = dashboard_rules.analyze(bad, thresholds)
        d1 = [i for i in issues if i.rule_id == "D1_kpi_card_overload"]
        assert d1
        _assert_has_learning(d1[0])

    def test_d2_has_why_and_refs(self, bad, thresholds):
        issues = dashboard_rules.analyze(bad, thresholds)
        d2 = [i for i in issues if i.rule_id == "D2_low_whitespace"]
        assert d2
        _assert_has_learning(d2[0])


# ── model defaults ────────────────────────────────────────────────────────────

class TestIssueModelDefaults:
    def test_why_defaults_to_empty_string(self):
        from backend.models.issue import Category, Severity
        i = Issue(
            rule_id="X1_test",
            category=Category.SPACING,
            severity=Severity.LOW,
            confidence=1.0,
            message="test",
            recommendation="test",
            evidence="test",
            estimated_time="1 minute",
        )
        assert i.why == ""
        assert i.references == []

    def test_why_and_references_set_correctly(self):
        from backend.models.issue import Category, Severity
        i = Issue(
            rule_id="X2_test",
            category=Category.SPACING,
            severity=Severity.LOW,
            confidence=1.0,
            message="test",
            recommendation="test",
            evidence="test",
            estimated_time="1 minute",
            why="Because it matters.",
            references=["Stripe", "Linear"],
        )
        assert i.why == "Because it matters."
        assert i.references == ["Stripe", "Linear"]
