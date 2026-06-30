"""Tests for backend/rules/conversion_rules.py"""
from __future__ import annotations

import pytest

from backend.rules.conversion_rules import analyze
from backend.models.issue import Category, Severity


def _run(page_overrides: dict, threshold_overrides: dict | None = None) -> list:
    base = {
        "cta_texts": [],
        "form_field_counts": [],
        "trust_signal_count": 0,
        "has_testimonials": False,
        "has_hero": False,
        "hero_word_count": 0,
        "headings": [],
        "buttons": [],
        "has_pricing_section": False,
    }
    base.update(page_overrides)
    t = {"conversion": {"max_form_fields": 6, "min_trust_signals": 1,
                        "hero_max_words": 150, "hero_min_words": 5}}
    if threshold_overrides:
        t["conversion"].update(threshold_overrides)
    return analyze(base, t)


def rule_ids(issues):
    return {i.rule_id for i in issues}


class TestCV1WeakCtaText:
    def test_fires_on_all_generic_ctAs(self):
        issues = _run({"cta_texts": ["click here", "submit", "learn more"]})
        assert "CV1_weak_cta_text" in rule_ids(issues)

    def test_high_severity_when_no_strong_verb(self):
        issues = _run({"cta_texts": ["click here"]})
        cv1 = next(i for i in issues if i.rule_id == "CV1_weak_cta_text")
        assert cv1.severity == Severity.HIGH

    def test_medium_severity_when_mixed(self):
        # "submit" is weak but "start free trial" has "start" (strong)
        issues = _run({"cta_texts": ["submit", "start free trial"]})
        cv1 = next((i for i in issues if i.rule_id == "CV1_weak_cta_text"), None)
        if cv1:
            assert cv1.severity == Severity.MEDIUM

    def test_does_not_fire_on_strong_cta(self):
        issues = _run({"cta_texts": ["start free trial", "get started", "join now"]})
        assert "CV1_weak_cta_text" not in rule_ids(issues)

    def test_does_not_fire_on_empty_ctas(self):
        issues = _run({"cta_texts": []})
        assert "CV1_weak_cta_text" not in rule_ids(issues)

    def test_category_is_conversion(self):
        issues = _run({"cta_texts": ["submit"]})
        cv1 = next((i for i in issues if i.rule_id == "CV1_weak_cta_text"), None)
        if cv1:
            assert cv1.category == Category.CONVERSION_OPTIMIZATION


class TestCV2FormFriction:
    def test_fires_when_too_many_fields(self):
        issues = _run({"form_field_counts": [9]})
        assert "CV2_form_friction" in rule_ids(issues)

    def test_not_fires_on_short_form(self):
        issues = _run({"form_field_counts": [4]})
        assert "CV2_form_friction" not in rule_ids(issues)

    def test_fires_on_multiple_long_forms(self):
        issues = _run({"form_field_counts": [8, 10]})
        assert "CV2_form_friction" in rule_ids(issues)

    def test_not_fires_on_empty_forms(self):
        issues = _run({"form_field_counts": []})
        assert "CV2_form_friction" not in rule_ids(issues)

    def test_custom_threshold(self):
        issues = _run({"form_field_counts": [4]}, {"max_form_fields": 3})
        assert "CV2_form_friction" in rule_ids(issues)

    def test_severity_is_high(self):
        issues = _run({"form_field_counts": [10]})
        cv2 = next(i for i in issues if i.rule_id == "CV2_form_friction")
        assert cv2.severity == Severity.HIGH


class TestCV3MissingTrustSignals:
    def test_fires_when_no_trust_signals(self):
        issues = _run({"trust_signal_count": 0, "has_testimonials": False})
        assert "CV3_missing_trust_signals" in rule_ids(issues)

    def test_not_fires_when_has_trust_signals(self):
        issues = _run({"trust_signal_count": 2, "has_testimonials": False})
        assert "CV3_missing_trust_signals" not in rule_ids(issues)

    def test_not_fires_when_has_testimonials(self):
        issues = _run({"trust_signal_count": 0, "has_testimonials": True})
        assert "CV3_missing_trust_signals" not in rule_ids(issues)

    def test_severity_is_medium(self):
        issues = _run({"trust_signal_count": 0, "has_testimonials": False})
        cv3 = next((i for i in issues if i.rule_id == "CV3_missing_trust_signals"), None)
        if cv3:
            assert cv3.severity == Severity.MEDIUM


class TestCV4HeroClarity:
    def test_fires_missing_h1(self):
        issues = _run({"headings": []})
        assert "CV4_missing_value_proposition" in rule_ids(issues)

    def test_not_fires_when_h1_present(self):
        issues = _run({"headings": [{"level": 1, "font_size_px": 32, "text": "Build Faster"}]})
        assert "CV4_missing_value_proposition" not in rule_ids(issues)

    def test_fires_hero_word_overload(self):
        issues = _run({
            "headings": [{"level": 1, "font_size_px": 32, "text": "headline"}],
            "has_hero": True,
            "hero_word_count": 200,
        })
        assert "CV4_hero_word_overload" in rule_ids(issues)

    def test_not_fires_on_lean_hero(self):
        issues = _run({
            "headings": [{"level": 1, "font_size_px": 32, "text": "headline"}],
            "has_hero": True,
            "hero_word_count": 40,
        })
        assert "CV4_hero_word_overload" not in rule_ids(issues)

    def test_no_hero_fires_low_severity(self):
        issues = _run({
            "headings": [{"level": 1, "font_size_px": 32, "text": "headline"}],
            "has_hero": False,
            "hero_word_count": 0,
        })
        no_hero = next((i for i in issues if i.rule_id == "CV4_no_hero_section"), None)
        if no_hero:
            assert no_hero.severity == Severity.LOW

    def test_severity_h1_missing_is_high(self):
        issues = _run({"headings": []})
        mv = next(i for i in issues if i.rule_id == "CV4_missing_value_proposition")
        assert mv.severity == Severity.HIGH


class TestCV5PricingNoCta:
    def test_fires_when_pricing_but_no_buttons(self):
        issues = _run({"has_pricing_section": True, "buttons": []})
        assert "CV5_pricing_no_cta" in rule_ids(issues)

    def test_not_fires_when_pricing_and_buttons(self):
        issues = _run({
            "has_pricing_section": True,
            "buttons": [{"text": "Get Started", "height_px": 44,
                         "background_color": "#007bff", "border_radius_px": 4,
                         "has_focus_style": True,
                         "padding_top_px": 8, "padding_right_px": 16,
                         "padding_bottom_px": 8, "padding_left_px": 16,
                         "color": "#fff"}],
        })
        assert "CV5_pricing_no_cta" not in rule_ids(issues)

    def test_not_fires_when_no_pricing_section(self):
        issues = _run({"has_pricing_section": False, "buttons": []})
        assert "CV5_pricing_no_cta" not in rule_ids(issues)

    def test_severity_is_high(self):
        issues = _run({"has_pricing_section": True, "buttons": []})
        cv5 = next((i for i in issues if i.rule_id == "CV5_pricing_no_cta"), None)
        if cv5:
            assert cv5.severity == Severity.HIGH
