"""Tests for backend/rules/interactivity_rules.py"""
from __future__ import annotations

import pytest

from backend.rules.interactivity_rules import analyze
from backend.models.issue import Category, Severity


def _run(page_overrides: dict) -> list:
    base = {
        "buttons": [],
        "inputs": [],
        "cta_texts": [],
        "has_hover_styles": False,
        "has_transitions": False,
        "has_focus_outline_removed": False,
    }
    base.update(page_overrides)
    return analyze(base, {})


def rule_ids(issues):
    return {i.rule_id for i in issues}


_MOCK_BUTTON = {
    "text": "Buy Now", "height_px": 44, "background_color": "#007bff",
    "border_radius_px": 4, "has_focus_style": True,
    "padding_top_px": 8, "padding_right_px": 16,
    "padding_bottom_px": 8, "padding_left_px": 16,
    "color": "#fff",
}

_MOCK_INPUT = {
    "has_label": True, "label_text": "Email", "placeholder": None,
    "padding_px": 10, "has_focus_style": True, "input_type": "email",
}


class TestINT1MissingHoverStates:
    def test_fires_when_no_hover_on_interactive_page(self):
        issues = _run({
            "buttons": [_MOCK_BUTTON, _MOCK_BUTTON],
            "has_hover_styles": False,
        })
        assert "INT1_missing_hover_states" in rule_ids(issues)

    def test_not_fires_when_hover_styles_present(self):
        issues = _run({
            "buttons": [_MOCK_BUTTON, _MOCK_BUTTON],
            "has_hover_styles": True,
        })
        assert "INT1_missing_hover_states" not in rule_ids(issues)

    def test_not_fires_when_no_interactive_elements(self):
        issues = _run({"buttons": [], "inputs": [], "cta_texts": [], "has_hover_styles": False})
        assert "INT1_missing_hover_states" not in rule_ids(issues)

    def test_not_fires_when_only_one_element(self):
        issues = _run({"buttons": [_MOCK_BUTTON], "inputs": [], "cta_texts": [], "has_hover_styles": False})
        assert "INT1_missing_hover_states" not in rule_ids(issues)

    def test_severity_is_medium(self):
        issues = _run({"buttons": [_MOCK_BUTTON, _MOCK_BUTTON], "has_hover_styles": False})
        int1 = next(i for i in issues if i.rule_id == "INT1_missing_hover_states")
        assert int1.severity == Severity.MEDIUM

    def test_category_is_interactivity(self):
        issues = _run({"buttons": [_MOCK_BUTTON, _MOCK_BUTTON], "has_hover_styles": False})
        int1 = next(i for i in issues if i.rule_id == "INT1_missing_hover_states")
        assert int1.category == Category.INTERACTIVITY

    def test_counts_cta_texts_toward_interactive(self):
        issues = _run({
            "cta_texts": ["buy now", "learn more"],
            "has_hover_styles": False,
        })
        assert "INT1_missing_hover_states" in rule_ids(issues)


class TestINT2NoTransitions:
    def test_fires_when_no_transitions_on_interactive_page(self):
        issues = _run({
            "buttons": [_MOCK_BUTTON, _MOCK_BUTTON],
            "has_transitions": False,
        })
        assert "INT2_no_transitions" in rule_ids(issues)

    def test_not_fires_when_transitions_present(self):
        issues = _run({
            "buttons": [_MOCK_BUTTON, _MOCK_BUTTON],
            "has_transitions": True,
        })
        assert "INT2_no_transitions" not in rule_ids(issues)

    def test_not_fires_when_no_interactive_elements(self):
        issues = _run({"buttons": [], "inputs": [], "has_transitions": False})
        assert "INT2_no_transitions" not in rule_ids(issues)

    def test_severity_is_low(self):
        issues = _run({
            "inputs": [_MOCK_INPUT, _MOCK_INPUT],
            "has_transitions": False,
        })
        int2 = next(i for i in issues if i.rule_id == "INT2_no_transitions")
        assert int2.severity == Severity.LOW

    def test_category_is_interactivity(self):
        issues = _run({
            "buttons": [_MOCK_BUTTON, _MOCK_BUTTON],
            "has_transitions": False,
        })
        int2 = next(i for i in issues if i.rule_id == "INT2_no_transitions")
        assert int2.category == Category.INTERACTIVITY


class TestINT3FocusOutlineRemoved:
    def test_fires_when_outline_removed(self):
        issues = _run({"has_focus_outline_removed": True})
        assert "INT3_focus_outline_removed" in rule_ids(issues)

    def test_not_fires_when_outline_not_removed(self):
        issues = _run({"has_focus_outline_removed": False})
        assert "INT3_focus_outline_removed" not in rule_ids(issues)

    def test_severity_is_high(self):
        issues = _run({"has_focus_outline_removed": True})
        int3 = next(i for i in issues if i.rule_id == "INT3_focus_outline_removed")
        assert int3.severity == Severity.HIGH

    def test_category_is_accessibility(self):
        # This rule crosses into accessibility since it's a WCAG violation
        issues = _run({"has_focus_outline_removed": True})
        int3 = next(i for i in issues if i.rule_id == "INT3_focus_outline_removed")
        assert int3.category == Category.ACCESSIBILITY

    def test_evidence_is_descriptive(self):
        issues = _run({"has_focus_outline_removed": True})
        int3 = next(i for i in issues if i.rule_id == "INT3_focus_outline_removed")
        assert "outline" in int3.evidence.lower() or "True" in int3.evidence


class TestCssParserHelpers:
    """Integration: verify the CSS parser helpers that feed interactivity signals."""

    def test_has_hover_rules_detects_hover(self):
        from backend.analyzers.css_parser import has_hover_rules
        assert has_hover_rules("button:hover { background: blue; }")

    def test_has_hover_rules_false_without_hover(self):
        from backend.analyzers.css_parser import has_hover_rules
        assert not has_hover_rules("button { background: blue; }")

    def test_has_transition_rules_detects_transition(self):
        from backend.analyzers.css_parser import has_transition_rules
        assert has_transition_rules("button { transition: background 0.2s; }")

    def test_has_transition_rules_detects_keyframes(self):
        from backend.analyzers.css_parser import has_transition_rules
        assert has_transition_rules("@keyframes spin { from { } to { } }")

    def test_has_transition_rules_false_without(self):
        from backend.analyzers.css_parser import has_transition_rules
        assert not has_transition_rules("button { background: blue; }")

    def test_focus_outline_removed_detects_none(self):
        from backend.analyzers.css_parser import has_focus_outline_removed
        assert has_focus_outline_removed("* { outline: none; }")

    def test_focus_outline_removed_detects_zero(self):
        from backend.analyzers.css_parser import has_focus_outline_removed
        assert has_focus_outline_removed("button { outline: 0; }")

    def test_focus_outline_not_removed_when_present(self):
        from backend.analyzers.css_parser import has_focus_outline_removed
        assert not has_focus_outline_removed("button:focus { outline: 2px solid blue; }")
