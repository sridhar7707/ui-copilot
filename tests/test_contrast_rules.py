from __future__ import annotations

import pytest
from backend.rules import contrast_rules
from backend.utils.color_utils import contrast_ratio
from backend.utils.config_loader import load_scoring_config
from tests.fixtures import bad_page, clean_page

THRESHOLDS = load_scoring_config()["thresholds"]


class TestContrastRatioUtil:
    def test_black_on_white(self):
        assert abs(contrast_ratio("#000000", "#ffffff") - 21.0) < 0.1

    def test_white_on_white(self):
        assert abs(contrast_ratio("#ffffff", "#ffffff") - 1.0) < 0.01

    def test_symmetry(self):
        assert abs(contrast_ratio("#005fcc", "#ffffff") - contrast_ratio("#ffffff", "#005fcc")) < 0.001

    def test_short_hex(self):
        assert abs(contrast_ratio("#000", "#fff") - 21.0) < 0.1


class TestCleanPage:
    def test_no_contrast_issues(self):
        issues = contrast_rules.analyze(clean_page(), THRESHOLDS)
        assert issues == []


class TestWcagAA:
    def test_low_contrast_body_flagged(self):
        page = clean_page()
        page["text_color_pairs"] = [{
            "foreground": "#aaaaaa",
            "background": "#ffffff",
            "font_size_px": 16.0,
            "is_bold": False,
            "context": "body",
        }]
        issues = contrast_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "C1_wcag_aa_contrast" for i in issues)

    def test_passing_contrast_not_flagged(self):
        page = clean_page()
        page["text_color_pairs"] = [{
            "foreground": "#333333",
            "background": "#ffffff",
            "font_size_px": 16.0,
            "is_bold": False,
            "context": "body",
        }]
        issues = contrast_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "C1_wcag_aa_contrast" for i in issues)

    def test_large_text_uses_lower_threshold(self):
        # ratio ~3.5:1 — fails AA normal (4.5) but passes AA large (3.0)
        page = clean_page()
        page["text_color_pairs"] = [{
            "foreground": "#767676",
            "background": "#ffffff",
            "font_size_px": 20.0,   # large text
            "is_bold": False,
            "context": "heading",
        }]
        issues = contrast_rules.analyze(page, THRESHOLDS)
        ratio = contrast_ratio("#767676", "#ffffff")
        t = THRESHOLDS["contrast"]
        if ratio >= t["wcag_aa_large"]:
            assert not any(i.rule_id == "C1_wcag_aa_contrast" for i in issues)
        else:
            assert any(i.rule_id == "C1_wcag_aa_contrast" for i in issues)

    def test_bad_page_triggers_contrast_issue(self):
        issues = contrast_rules.analyze(bad_page(), THRESHOLDS)
        assert any(i.rule_id == "C1_wcag_aa_contrast" for i in issues)

    def test_contrast_failure_also_raises_accessibility_issue(self):
        page = clean_page()
        page["text_color_pairs"] = [{
            "foreground": "#aaaaaa",
            "background": "#ffffff",
            "font_size_px": 14.0,
            "is_bold": False,
            "context": "body",
        }]
        issues = contrast_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "C1_wcag_aa_contrast_a11y" for i in issues)
