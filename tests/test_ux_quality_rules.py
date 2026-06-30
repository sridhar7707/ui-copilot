"""Tests for backend/rules/ux_quality_rules.py"""
from __future__ import annotations

import pytest

from backend.rules.ux_quality_rules import analyze
from backend.models.issue import Category, Severity


def _run(page_overrides: dict) -> list:
    base = {
        "inputs": [],
        "buttons": [],
        "tables": [],
        "has_error_states": False,
        "has_empty_states": False,
        "has_skip_link": False,
    }
    base.update(page_overrides)
    return analyze(base, {})


def rule_ids(issues):
    return {i.rule_id for i in issues}


_MOCK_INPUT = {"has_label": True, "label_text": "Email", "placeholder": None,
               "padding_px": 10, "has_focus_style": True, "input_type": "email"}

_MOCK_BUTTON = {"text": "Submit", "height_px": 44, "background_color": "#007bff",
                "border_radius_px": 4, "has_focus_style": True,
                "padding_top_px": 8, "padding_right_px": 16,
                "padding_bottom_px": 8, "padding_left_px": 16, "color": "#fff"}


class TestUX1MissingErrorStates:
    def test_fires_when_form_present_no_error_states(self):
        issues = _run({"inputs": [_MOCK_INPUT], "has_error_states": False})
        assert "UX1_missing_error_states" in rule_ids(issues)

    def test_not_fires_when_has_error_states(self):
        issues = _run({"inputs": [_MOCK_INPUT], "has_error_states": True})
        assert "UX1_missing_error_states" not in rule_ids(issues)

    def test_not_fires_when_no_inputs(self):
        issues = _run({"inputs": [], "has_error_states": False})
        assert "UX1_missing_error_states" not in rule_ids(issues)

    def test_severity_is_medium(self):
        issues = _run({"inputs": [_MOCK_INPUT], "has_error_states": False})
        ux1 = next(i for i in issues if i.rule_id == "UX1_missing_error_states")
        assert ux1.severity == Severity.MEDIUM

    def test_category_is_ux_quality(self):
        issues = _run({"inputs": [_MOCK_INPUT], "has_error_states": False})
        ux1 = next(i for i in issues if i.rule_id == "UX1_missing_error_states")
        assert ux1.category == Category.UX_QUALITY

    def test_evidence_includes_input_count(self):
        issues = _run({"inputs": [_MOCK_INPUT, _MOCK_INPUT], "has_error_states": False})
        ux1 = next(i for i in issues if i.rule_id == "UX1_missing_error_states")
        assert "2" in ux1.evidence


class TestUX2MissingEmptyStates:
    def test_fires_when_tables_and_no_empty_state(self):
        mock_table = {"has_header": True, "has_zebra_striping": False,
                      "cell_padding_px": 10, "has_border": True}
        issues = _run({"tables": [mock_table], "has_empty_states": False})
        assert "UX2_missing_empty_states" in rule_ids(issues)

    def test_fires_when_inputs_and_no_empty_state(self):
        issues = _run({"inputs": [_MOCK_INPUT], "has_empty_states": False})
        assert "UX2_missing_empty_states" in rule_ids(issues)

    def test_not_fires_when_has_empty_state(self):
        mock_table = {"has_header": True, "has_zebra_striping": False,
                      "cell_padding_px": 10, "has_border": True}
        issues = _run({"tables": [mock_table], "has_empty_states": True})
        assert "UX2_missing_empty_states" not in rule_ids(issues)

    def test_not_fires_when_no_data_components(self):
        issues = _run({"inputs": [], "tables": [], "has_empty_states": False})
        assert "UX2_missing_empty_states" not in rule_ids(issues)

    def test_severity_is_low(self):
        issues = _run({"inputs": [_MOCK_INPUT], "has_empty_states": False})
        ux2 = next(i for i in issues if i.rule_id == "UX2_missing_empty_states")
        assert ux2.severity == Severity.LOW


class TestUX3GenericSubmitText:
    def test_fires_on_submit_button(self):
        btn = dict(_MOCK_BUTTON, text="Submit")
        issues = _run({"buttons": [btn], "inputs": [_MOCK_INPUT]})
        assert "UX3_generic_submit_text" in rule_ids(issues)

    def test_fires_on_ok_button(self):
        btn = dict(_MOCK_BUTTON, text="ok")
        issues = _run({"buttons": [btn], "inputs": [_MOCK_INPUT]})
        assert "UX3_generic_submit_text" in rule_ids(issues)

    def test_not_fires_on_descriptive_text(self):
        btn = dict(_MOCK_BUTTON, text="Create Account")
        issues = _run({"buttons": [btn], "inputs": [_MOCK_INPUT]})
        assert "UX3_generic_submit_text" not in rule_ids(issues)

    def test_not_fires_when_no_inputs(self):
        btn = dict(_MOCK_BUTTON, text="Submit")
        issues = _run({"buttons": [btn], "inputs": []})
        assert "UX3_generic_submit_text" not in rule_ids(issues)

    def test_severity_is_medium(self):
        btn = dict(_MOCK_BUTTON, text="Submit")
        issues = _run({"buttons": [btn], "inputs": [_MOCK_INPUT]})
        ux3 = next(i for i in issues if i.rule_id == "UX3_generic_submit_text")
        assert ux3.severity == Severity.MEDIUM

    def test_not_fires_on_save_changes(self):
        btn = dict(_MOCK_BUTTON, text="Save Changes")
        issues = _run({"buttons": [btn], "inputs": [_MOCK_INPUT]})
        assert "UX3_generic_submit_text" not in rule_ids(issues)


class TestUX4MissingSkipLink:
    def test_fires_when_many_interactive_and_no_skip(self):
        issues = _run({
            "inputs": [_MOCK_INPUT, _MOCK_INPUT],
            "buttons": [_MOCK_BUTTON],
            "has_skip_link": False,
        })
        assert "UX4_missing_skip_link" in rule_ids(issues)

    def test_not_fires_when_skip_link_present(self):
        issues = _run({
            "inputs": [_MOCK_INPUT, _MOCK_INPUT],
            "buttons": [_MOCK_BUTTON],
            "has_skip_link": True,
        })
        assert "UX4_missing_skip_link" not in rule_ids(issues)

    def test_not_fires_when_few_elements(self):
        # < 3 interactive elements
        issues = _run({
            "inputs": [_MOCK_INPUT],
            "buttons": [],
            "has_skip_link": False,
        })
        assert "UX4_missing_skip_link" not in rule_ids(issues)

    def test_severity_is_medium(self):
        issues = _run({
            "inputs": [_MOCK_INPUT, _MOCK_INPUT],
            "buttons": [_MOCK_BUTTON],
            "has_skip_link": False,
        })
        ux4 = next(i for i in issues if i.rule_id == "UX4_missing_skip_link")
        assert ux4.severity == Severity.MEDIUM
