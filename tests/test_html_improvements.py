"""
Module 11 — HTML Improvements tests.

All tests are deterministic: no API calls, no disk access.
html_improvements.generate() is a pure function tested with controlled
AnalysisResult fixtures.
"""
from __future__ import annotations

import pytest

from backend.models.analysis import AnalysisResult, CategoryScore
from backend.models.issue import Category, Issue, Severity
from backend.services import html_improvements


# ── helpers ───────────────────────────────────────────────────────────────────

def _result(issues: list[Issue]) -> AnalysisResult:
    return AnalysisResult(overall_score=70.0, category_scores=[], issues=issues)


def _issue(rule_id: str, cat: Category = Category.ACCESSIBILITY) -> Issue:
    return Issue(
        rule_id=rule_id,
        category=cat,
        severity=Severity.HIGH,
        confidence=0.9,
        message="test",
        recommendation="fix it",
        evidence="none",
        estimated_time="5 minutes",
        estimated_gain=2.0,
    )


def _clean() -> AnalysisResult:
    return _result([])


# ── always-present elements ───────────────────────────────────────────────────

class TestAlwaysPresent:
    def test_output_is_string(self):
        assert isinstance(html_improvements.generate(_clean()), str)

    def test_doctype_always_included(self):
        assert "<!DOCTYPE html>" in html_improvements.generate(_clean())

    def test_lang_attribute_always_included(self):
        assert 'lang="en"' in html_improvements.generate(_clean())

    def test_viewport_meta_always_included(self):
        assert 'name="viewport"' in html_improvements.generate(_clean())

    def test_charset_meta_always_included(self):
        assert 'charset="UTF-8"' in html_improvements.generate(_clean())

    def test_landmark_roles_always_included(self):
        out = html_improvements.generate(_clean())
        assert 'role="banner"' in out
        assert 'role="contentinfo"' in out

    def test_main_id_always_included(self):
        assert 'id="main-content"' in html_improvements.generate(_clean())

    def test_score_appears_in_header(self):
        assert "70.0/100" in html_improvements.generate(_clean())


# ── skip link ─────────────────────────────────────────────────────────────────

class TestSkipLink:
    def test_skip_link_present_when_a11y_issue_exists(self):
        result = _result([_issue("F1_missing_label")])
        assert "skip-link" in html_improvements.generate(result)

    def test_skip_link_present_when_focus_issue(self):
        result = _result([_issue("B3_focus_style")])
        assert "skip-link" in html_improvements.generate(result)

    def test_skip_link_present_when_touch_target_issue(self):
        result = _result([_issue("B4_touch_target")])
        assert "skip-link" in html_improvements.generate(result)


# ── form patterns ─────────────────────────────────────────────────────────────

class TestFormPatterns:
    def test_label_pattern_when_f1_fires(self):
        result = _result([_issue("F1_missing_label")])
        out = html_improvements.generate(result)
        assert '<label for="email">' in out

    def test_f2_pattern_when_placeholder_as_label(self):
        result = _result([_issue("F2_placeholder_as_label")])
        out = html_improvements.generate(result)
        assert "placeholder" in out
        assert "label" in out.lower()

    def test_no_form_section_when_clean(self):
        out = html_improvements.generate(_clean())
        assert 'for="email"' not in out

    def test_error_message_pattern_always_in_form_section(self):
        result = _result([_issue("F1_missing_label")])
        out = html_improvements.generate(result)
        assert 'role="alert"' in out


# ── table pattern ─────────────────────────────────────────────────────────────

class TestTablePattern:
    def test_table_pattern_when_tbl1_fires(self):
        result = _result([_issue("TBL1_missing_header")])
        out = html_improvements.generate(result)
        assert 'scope="col"' in out

    def test_caption_element_included(self):
        result = _result([_issue("TBL1_missing_header")])
        assert "<caption>" in html_improvements.generate(result)

    def test_no_table_section_when_clean(self):
        assert 'scope="col"' not in html_improvements.generate(_clean())


# ── button patterns ───────────────────────────────────────────────────────────

class TestButtonPattern:
    def test_touch_target_comment_when_b4_fires(self):
        result = _result([_issue("B4_touch_target")])
        out = html_improvements.generate(result)
        assert "44" in out  # 44×44px touch target

    def test_consolidated_variants_when_b1_fires(self):
        result = _result([_issue("B1_button_style_count", Category.CONSISTENCY)])
        out = html_improvements.generate(result)
        assert "btn-primary" in out
        assert "btn-secondary" in out

    def test_aria_label_on_icon_button_always_present(self):
        result = _result([_issue("B4_touch_target")])
        assert "aria-label" in html_improvements.generate(result)


# ── typography pattern ────────────────────────────────────────────────────────

class TestTypographyPattern:
    def test_heading_hierarchy_when_t4_fires(self):
        result = _result([_issue("T4_heading_hierarchy", Category.VISUAL_HIERARCHY)])
        out = html_improvements.generate(result)
        assert "<h1>" in out
        assert "<h2" in out

    def test_one_h1_comment_present(self):
        result = _result([_issue("T1_body_font_size", Category.TYPOGRAPHY)])
        assert "one per page" in html_improvements.generate(result)

    def test_no_heading_section_when_clean(self):
        out = html_improvements.generate(_clean())
        assert "one per page" not in out


# ── idempotency ───────────────────────────────────────────────────────────────

class TestIdempotency:
    def test_same_result_produces_same_output(self):
        result = _result([_issue("F1_missing_label"), _issue("TBL1_missing_header")])
        assert html_improvements.generate(result) == html_improvements.generate(result)
