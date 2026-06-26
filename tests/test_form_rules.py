from __future__ import annotations

from backend.rules import form_rules
from backend.utils.config_loader import load_scoring_config
from tests.fixtures import bad_page, clean_page

THRESHOLDS = load_scoring_config()["thresholds"]


def rule_ids(issues) -> list[str]:
    return [i.rule_id for i in issues]


class TestCleanPage:
    def test_no_form_issues(self):
        issues = form_rules.analyze(clean_page(), THRESHOLDS)
        assert issues == [], f"Unexpected issues: {rule_ids(issues)}"

    def test_no_inputs_yields_no_issues(self):
        page = clean_page()
        page["inputs"] = []
        assert form_rules.analyze(page, THRESHOLDS) == []


class TestMissingLabel:
    def test_input_without_label_flagged(self):
        page = clean_page()
        page["inputs"][0]["has_label"] = False
        page["inputs"][0]["label_text"] = None
        page["inputs"][0]["placeholder"] = None
        issues = form_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "F1_missing_label" for i in issues)

    def test_input_with_label_not_flagged(self):
        page = clean_page()
        page["inputs"][0]["has_label"] = True
        issues = form_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "F1_missing_label" for i in issues)

    def test_severity_is_critical(self):
        from backend.models.issue import Severity
        page = clean_page()
        page["inputs"][0]["has_label"] = False
        page["inputs"][0]["label_text"] = None
        page["inputs"][0]["placeholder"] = None
        issues = form_rules.analyze(page, THRESHOLDS)
        f1 = next(i for i in issues if i.rule_id == "F1_missing_label")
        assert f1.severity == Severity.CRITICAL

    def test_bad_page_triggers_f1(self):
        issues = form_rules.analyze(bad_page(), THRESHOLDS)
        assert any(i.rule_id == "F1_missing_label" for i in issues)

    def test_all_unlabelled_inputs_flagged(self):
        page = clean_page()
        page["inputs"] = [
            {"has_label": False, "label_text": None, "placeholder": None,
             "padding_px": 10.0, "has_focus_style": True, "input_type": "text"},
            {"has_label": False, "label_text": None, "placeholder": None,
             "padding_px": 10.0, "has_focus_style": True, "input_type": "email"},
        ]
        issues = form_rules.analyze(page, THRESHOLDS)
        f1_issues = [i for i in issues if i.rule_id == "F1_missing_label"]
        assert len(f1_issues) == 2


class TestPlaceholderAsLabel:
    def test_placeholder_without_label_flagged(self):
        page = clean_page()
        page["inputs"][0]["has_label"] = False
        page["inputs"][0]["label_text"] = None
        page["inputs"][0]["placeholder"] = "Enter your email"
        issues = form_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "F2_placeholder_as_label" for i in issues)

    def test_placeholder_with_label_not_flagged(self):
        page = clean_page()
        page["inputs"][0]["has_label"] = True
        page["inputs"][0]["label_text"] = "Email"
        page["inputs"][0]["placeholder"] = "you@example.com"
        issues = form_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "F2_placeholder_as_label" for i in issues)

    def test_no_label_no_placeholder_not_flagged(self):
        page = clean_page()
        page["inputs"][0]["has_label"] = False
        page["inputs"][0]["label_text"] = None
        page["inputs"][0]["placeholder"] = None
        issues = form_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "F2_placeholder_as_label" for i in issues)

    def test_severity_is_high(self):
        from backend.models.issue import Severity
        page = clean_page()
        page["inputs"][0]["has_label"] = False
        page["inputs"][0]["label_text"] = None
        page["inputs"][0]["placeholder"] = "Enter name"
        issues = form_rules.analyze(page, THRESHOLDS)
        f2 = next(i for i in issues if i.rule_id == "F2_placeholder_as_label")
        assert f2.severity == Severity.HIGH

    def test_placeholder_text_appears_in_evidence(self):
        page = clean_page()
        page["inputs"][0]["has_label"] = False
        page["inputs"][0]["label_text"] = None
        page["inputs"][0]["placeholder"] = "Search here"
        issues = form_rules.analyze(page, THRESHOLDS)
        f2 = next(i for i in issues if i.rule_id == "F2_placeholder_as_label")
        assert "Search here" in f2.evidence

    def test_bad_page_triggers_f2(self):
        issues = form_rules.analyze(bad_page(), THRESHOLDS)
        assert any(i.rule_id == "F2_placeholder_as_label" for i in issues)


class TestInputPadding:
    def test_low_padding_flagged(self):
        page = clean_page()
        page["inputs"][0]["padding_px"] = 4.0
        issues = form_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "F3_input_padding" for i in issues)

    def test_exact_threshold_not_flagged(self):
        page = clean_page()
        page["inputs"][0]["padding_px"] = float(
            THRESHOLDS["forms"]["min_input_padding_px"]
        )
        issues = form_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "F3_input_padding" for i in issues)

    def test_above_threshold_not_flagged(self):
        page = clean_page()
        page["inputs"][0]["padding_px"] = 12.0
        issues = form_rules.analyze(page, THRESHOLDS)
        assert not any(i.rule_id == "F3_input_padding" for i in issues)

    def test_zero_padding_flagged(self):
        page = clean_page()
        page["inputs"][0]["padding_px"] = 0.0
        issues = form_rules.analyze(page, THRESHOLDS)
        assert any(i.rule_id == "F3_input_padding" for i in issues)

    def test_severity_is_low(self):
        from backend.models.issue import Severity
        page = clean_page()
        page["inputs"][0]["padding_px"] = 2.0
        issues = form_rules.analyze(page, THRESHOLDS)
        f3 = next(i for i in issues if i.rule_id == "F3_input_padding")
        assert f3.severity == Severity.LOW

    def test_bad_page_triggers_f3(self):
        issues = form_rules.analyze(bad_page(), THRESHOLDS)
        assert any(i.rule_id == "F3_input_padding" for i in issues)


class TestMultipleInputs:
    def test_label_includes_input_type(self):
        page = clean_page()
        page["inputs"] = [
            {"has_label": False, "label_text": None, "placeholder": None,
             "padding_px": 10.0, "has_focus_style": True, "input_type": "email"},
        ]
        issues = form_rules.analyze(page, THRESHOLDS)
        f1 = next(i for i in issues if i.rule_id == "F1_missing_label")
        assert "email" in f1.message

    def test_each_input_evaluated_independently(self):
        page = clean_page()
        page["inputs"] = [
            {"has_label": True, "label_text": "Name", "placeholder": "Jane",
             "padding_px": 10.0, "has_focus_style": True, "input_type": "text"},
            {"has_label": False, "label_text": None, "placeholder": "Enter email",
             "padding_px": 4.0, "has_focus_style": False, "input_type": "email"},
        ]
        issues = form_rules.analyze(page, THRESHOLDS)
        fired = rule_ids(issues)
        assert "F1_missing_label" in fired
        assert "F2_placeholder_as_label" in fired
        assert "F3_input_padding" in fired
        assert fired.count("F1_missing_label") == 1
