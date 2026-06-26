"""
Module 13 — Accessibility Review.
"""
from __future__ import annotations

import pytest

from backend.services import accessibility_service, scoring_engine
from tests.fixtures import bad_page, clean_page


@pytest.fixture
def bad_result():
    return scoring_engine.analyze(bad_page())


@pytest.fixture
def clean_result():
    return scoring_engine.analyze(clean_page())


@pytest.fixture
def bad_report(bad_result):
    return accessibility_service.build_report(bad_result, bad_page())


@pytest.fixture
def clean_report(clean_result):
    return accessibility_service.build_report(clean_result, clean_page())


# ── report shape ──────────────────────────────────────────────────────────────

class TestReportShape:
    def test_has_wcag_aa_pass_field(self, bad_report):
        assert hasattr(bad_report, "wcag_aa_pass")

    def test_has_wcag_a_pass_field(self, bad_report):
        assert hasattr(bad_report, "wcag_a_pass")

    def test_score_in_range(self, bad_report):
        assert 0.0 <= bad_report.score <= 100.0

    def test_issues_is_list(self, bad_report):
        assert isinstance(bad_report.issues, list)

    def test_keyboard_hints_is_list(self, bad_report):
        assert isinstance(bad_report.keyboard_hints, list)

    def test_aria_hints_is_list(self, bad_report):
        assert isinstance(bad_report.aria_hints, list)

    def test_summary_is_non_empty_string(self, bad_report):
        assert isinstance(bad_report.summary, str)
        assert len(bad_report.summary) > 10


# ── bad page accessibility ────────────────────────────────────────────────────

class TestBadPageAccessibility:
    def test_fails_wcag_aa(self, bad_report):
        assert bad_report.wcag_aa_pass is False

    def test_fails_wcag_a(self, bad_report):
        assert bad_report.wcag_a_pass is False

    def test_score_below_50(self, bad_report):
        assert bad_report.score < 50

    def test_has_issues(self, bad_report):
        assert len(bad_report.issues) > 0

    def test_has_keyboard_hints(self, bad_report):
        assert len(bad_report.keyboard_hints) > 0

    def test_summary_mentions_failures(self, bad_report):
        assert "failure" in bad_report.summary.lower() or "fail" in bad_report.summary.lower()


# ── clean page accessibility ──────────────────────────────────────────────────

class TestCleanPageAccessibility:
    def test_passes_wcag_aa(self, clean_report):
        assert clean_report.wcag_aa_pass is True

    def test_passes_wcag_a(self, clean_report):
        assert clean_report.wcag_a_pass is True

    def test_score_high(self, clean_report):
        assert clean_report.score >= 80

    def test_no_issues(self, clean_report):
        assert len(clean_report.issues) == 0


# ── wcag issue fields ─────────────────────────────────────────────────────────

class TestWcagIssueFields:
    def test_all_issues_have_criterion(self, bad_report):
        for w in bad_report.issues:
            assert w.criterion, f"{w.rule_id} missing criterion"

    def test_all_issues_have_level(self, bad_report):
        for w in bad_report.issues:
            assert w.level in ("A", "AA", "AAA"), f"{w.rule_id} has bad level"

    def test_all_issues_have_why(self, bad_report):
        for w in bad_report.issues:
            assert w.why, f"{w.rule_id} missing why"

    def test_all_issues_have_severity(self, bad_report):
        for w in bad_report.issues:
            assert w.severity in ("critical", "high", "medium", "low", "suggestion")


# ── contrast issues mapped to criteria ───────────────────────────────────────

class TestWcagCriteriaMapping:
    def test_contrast_mapped_to_1_4_3(self, bad_report):
        contrast_issues = [w for w in bad_report.issues if "C1_wcag_aa" in w.rule_id]
        assert contrast_issues
        for w in contrast_issues:
            assert "1.4.3" in w.criterion

    def test_focus_style_mapped_to_2_4_7(self, bad_report):
        focus_issues = [w for w in bad_report.issues if w.rule_id == "B3_focus_style"]
        assert focus_issues
        assert "2.4.7" in focus_issues[0].criterion

    def test_missing_label_mapped_to_1_3_1(self, bad_report):
        label_issues = [w for w in bad_report.issues if w.rule_id == "F1_missing_label"]
        assert label_issues
        assert "1.3.1" in label_issues[0].criterion


# ── report_to_dict ────────────────────────────────────────────────────────────

class TestReportToDict:
    _EXPECTED_KEYS = {
        "wcag_aa_pass", "wcag_a_pass", "score", "issue_count",
        "issues", "keyboard_hints", "aria_hints", "summary",
    }

    def test_has_all_keys(self, bad_report):
        d = accessibility_service.report_to_dict(bad_report)
        assert set(d.keys()) == self._EXPECTED_KEYS

    def test_issue_count_matches_issues(self, bad_report):
        d = accessibility_service.report_to_dict(bad_report)
        assert d["issue_count"] == len(d["issues"])

    def test_issue_dicts_have_required_fields(self, bad_report):
        d = accessibility_service.report_to_dict(bad_report)
        for issue in d["issues"]:
            for key in ("rule_id", "criterion", "level", "severity",
                        "message", "recommendation", "why"):
                assert key in issue, f"missing {key} in serialised issue"
