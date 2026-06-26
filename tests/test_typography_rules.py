from __future__ import annotations

import pytest
from backend.rules import typography_rules
from backend.utils.config_loader import load_scoring_config
from tests.fixtures import bad_page, clean_page

THRESHOLDS = load_scoring_config()["thresholds"]


def rule_ids(issues) -> list[str]:
    return [i.rule_id for i in issues]


class TestCleanPage:
    def test_no_typography_issues(self):
        issues = typography_rules.analyze(clean_page(), THRESHOLDS)
        assert issues == []


class TestBodyFontSize:
    def test_small_body_font_flagged(self):
        page = clean_page()
        page["body_font_size_px"] = 11.0
        issues = typography_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "T1_body_font_size" for i in issues)

    def test_exactly_minimum_not_flagged(self):
        page = clean_page()
        page["body_font_size_px"] = 14.0
        issues = typography_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "T1_body_font_size" for i in issues)

    def test_none_font_size_skipped(self):
        page = clean_page()
        page["body_font_size_px"] = None
        issues = typography_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "T1_body_font_size" for i in issues)

    def test_bad_page_triggers_t1(self):
        issues = typography_rules.analyze(bad_page(), THRESHOLDS)
        assert any(i.rule_id == "T1_body_font_size" for i in issues)


class TestFontFamilyCount:
    def test_too_many_fonts_flagged(self):
        page = clean_page()
        page["fonts"] = ["Arial", "Georgia", "Verdana"]
        issues = typography_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "T2_font_family_count" for i in issues)

    def test_two_fonts_allowed(self):
        page = clean_page()
        page["fonts"] = ["Inter", "JetBrains Mono"]
        issues = typography_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "T2_font_family_count" for i in issues)

    def test_bad_page_triggers_t2(self):
        issues = typography_rules.analyze(bad_page(), THRESHOLDS)
        assert any(i.rule_id == "T2_font_family_count" for i in issues)


class TestLineHeight:
    def test_tight_line_height_flagged(self):
        page = clean_page()
        page["line_height"] = 1.1
        issues = typography_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "T3_line_height" for i in issues)

    def test_good_line_height_passes(self):
        page = clean_page()
        page["line_height"] = 1.5
        issues = typography_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "T3_line_height" for i in issues)

    def test_none_line_height_skipped(self):
        page = clean_page()
        page["line_height"] = None
        issues = typography_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "T3_line_height" for i in issues)


class TestHeadingHierarchy:
    def test_weak_hierarchy_flagged(self):
        page = clean_page()
        page["headings"] = [
            {"level": 1, "font_size_px": 20.0, "text": "Title"},
            {"level": 2, "font_size_px": 18.0, "text": "Subtitle"},
        ]
        issues = typography_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "T4_heading_hierarchy" for i in issues)

    def test_strong_hierarchy_passes(self):
        issues = typography_rules.analyze(clean_page(), THRESHOLDS)
        assert not any(i.rule_id == "T4_heading_hierarchy" for i in issues)

    def test_no_h2_skips_hierarchy_check(self):
        page = clean_page()
        page["headings"] = [{"level": 1, "font_size_px": 32.0, "text": "Only H1"}]
        issues = typography_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "T4_heading_hierarchy" for i in issues)


class TestHeadingSize:
    def test_small_h1_flagged(self):
        page = clean_page()
        page["headings"] = [{"level": 1, "font_size_px": 14.0, "text": "Title"}]
        issues = typography_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "T5_heading_size" for i in issues)

    def test_adequate_h1_passes(self):
        issues = typography_rules.analyze(clean_page(), THRESHOLDS)
        assert not any(i.rule_id == "T5_heading_size" for i in issues)
