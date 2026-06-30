"""Tests for backend/rules/performance_rules.py"""
from __future__ import annotations

import pytest

from backend.rules.performance_rules import analyze
from backend.models.issue import Category, Severity


def _run(page_overrides: dict, threshold_overrides: dict | None = None) -> list:
    base = {
        "web_fonts": [],
        "has_font_display": False,
        "images": [],
        "media_query_breakpoints": [],
    }
    base.update(page_overrides)
    t = {"performance": {"required_breakpoints": [768]}}
    if threshold_overrides:
        t["performance"].update(threshold_overrides)
    return analyze(base, t)


def rule_ids(issues):
    return {i.rule_id for i in issues}


def _img(has_alt=True, has_srcset=True, has_width=True, has_height=True):
    return {
        "src": "img.png", "has_alt": has_alt, "alt_text": "desc",
        "has_srcset": has_srcset, "has_width": has_width, "has_height": has_height,
    }


class TestP1MissingFontDisplay:
    def test_fires_when_web_font_no_display(self):
        issues = _run({"web_fonts": ["Inter"], "has_font_display": False})
        assert "P1_missing_font_display" in rule_ids(issues)

    def test_not_fires_when_font_display_set(self):
        issues = _run({"web_fonts": ["Inter"], "has_font_display": True})
        assert "P1_missing_font_display" not in rule_ids(issues)

    def test_not_fires_when_no_web_fonts(self):
        issues = _run({"web_fonts": [], "has_font_display": False})
        assert "P1_missing_font_display" not in rule_ids(issues)

    def test_severity_is_medium(self):
        issues = _run({"web_fonts": ["Roboto"], "has_font_display": False})
        p1 = next(i for i in issues if i.rule_id == "P1_missing_font_display")
        assert p1.severity == Severity.MEDIUM

    def test_category_is_performance(self):
        issues = _run({"web_fonts": ["Roboto"], "has_font_display": False})
        p1 = next(i for i in issues if i.rule_id == "P1_missing_font_display")
        assert p1.category == Category.PERFORMANCE

    def test_evidence_contains_font_name(self):
        issues = _run({"web_fonts": ["Poppins"], "has_font_display": False})
        p1 = next(i for i in issues if i.rule_id == "P1_missing_font_display")
        assert "Poppins" in p1.evidence


class TestP2MissingImageAlt:
    def test_fires_when_images_missing_alt(self):
        issues = _run({"images": [_img(has_alt=False)]})
        assert "P2_missing_image_alt" in rule_ids(issues)

    def test_not_fires_when_all_have_alt(self):
        issues = _run({"images": [_img(has_alt=True), _img(has_alt=True)]})
        assert "P2_missing_image_alt" not in rule_ids(issues)

    def test_not_fires_when_no_images(self):
        issues = _run({"images": []})
        assert "P2_missing_image_alt" not in rule_ids(issues)

    def test_fires_accessibility_category(self):
        issues = _run({"images": [_img(has_alt=False)]})
        p2 = next(i for i in issues if i.rule_id == "P2_missing_image_alt")
        assert p2.category == Category.ACCESSIBILITY

    def test_severity_is_high(self):
        issues = _run({"images": [_img(has_alt=False)]})
        p2 = next(i for i in issues if i.rule_id == "P2_missing_image_alt")
        assert p2.severity == Severity.HIGH

    def test_evidence_includes_count(self):
        issues = _run({"images": [_img(has_alt=False), _img(has_alt=False)]})
        p2 = next(i for i in issues if i.rule_id == "P2_missing_image_alt")
        assert "2" in p2.evidence


class TestP3LayoutShiftImages:
    def test_fires_when_images_missing_dimensions(self):
        issues = _run({"images": [_img(has_width=False, has_height=False)]})
        assert "P3_layout_shift_images" in rule_ids(issues)

    def test_fires_when_only_width_missing(self):
        issues = _run({"images": [_img(has_width=False, has_height=True)]})
        assert "P3_layout_shift_images" in rule_ids(issues)

    def test_not_fires_when_all_have_dimensions(self):
        issues = _run({"images": [_img(has_width=True, has_height=True)]})
        assert "P3_layout_shift_images" not in rule_ids(issues)

    def test_not_fires_when_no_images(self):
        issues = _run({"images": []})
        assert "P3_layout_shift_images" not in rule_ids(issues)

    def test_severity_is_medium(self):
        issues = _run({"images": [_img(has_width=False)]})
        p3 = next(i for i in issues if i.rule_id == "P3_layout_shift_images")
        assert p3.severity == Severity.MEDIUM

    def test_category_is_performance(self):
        issues = _run({"images": [_img(has_width=False)]})
        p3 = next(i for i in issues if i.rule_id == "P3_layout_shift_images")
        assert p3.category == Category.PERFORMANCE


class TestP4MissingSrcset:
    def test_fires_when_multiple_images_no_srcset(self):
        issues = _run({"images": [_img(has_srcset=False), _img(has_srcset=False)]})
        assert "P4_missing_srcset" in rule_ids(issues)

    def test_not_fires_when_only_one_image(self):
        # Threshold: >= 2 images without srcset
        issues = _run({"images": [_img(has_srcset=False)]})
        assert "P4_missing_srcset" not in rule_ids(issues)

    def test_not_fires_when_images_have_srcset(self):
        issues = _run({"images": [_img(has_srcset=True), _img(has_srcset=True)]})
        assert "P4_missing_srcset" not in rule_ids(issues)

    def test_severity_is_low(self):
        issues = _run({"images": [_img(has_srcset=False), _img(has_srcset=False)]})
        p4 = next(i for i in issues if i.rule_id == "P4_missing_srcset")
        assert p4.severity == Severity.LOW


class TestP5MissingBreakpoints:
    def test_fires_when_no_media_queries(self):
        issues = _run({"media_query_breakpoints": []})
        assert "P5_missing_breakpoints" in rule_ids(issues)

    def test_not_fires_when_768_breakpoint_present(self):
        issues = _run({"media_query_breakpoints": [768]})
        assert "P5_missing_breakpoints" not in rule_ids(issues)

    def test_allows_breakpoints_within_64px(self):
        # 800px is within 64px of 768px
        issues = _run({"media_query_breakpoints": [800]})
        assert "P5_missing_breakpoints" not in rule_ids(issues)

    def test_fires_on_only_tiny_breakpoints(self):
        issues = _run({"media_query_breakpoints": [320]})
        assert "P5_missing_breakpoints" in rule_ids(issues)

    def test_severity_is_high(self):
        issues = _run({"media_query_breakpoints": []})
        p5 = next(i for i in issues if i.rule_id == "P5_missing_breakpoints")
        assert p5.severity == Severity.HIGH

    def test_custom_required_breakpoint(self):
        issues = _run({"media_query_breakpoints": []}, {"required_breakpoints": [1024]})
        p5 = next((i for i in issues if i.rule_id == "P5_missing_breakpoints"), None)
        assert p5 is not None
        assert "1024" in p5.evidence
