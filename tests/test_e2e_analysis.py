"""
End-to-end tests: HTML file → parse → score engine → verify results.
No mocking — this exercises the full pipeline.
"""
from __future__ import annotations

from pathlib import Path

from backend.analyzers.html_analyzer import parse
from backend.models.issue import Severity
from backend.services import scoring_engine

_SAMPLES = Path(__file__).parent.parent / "samples"
BAD_HTML = (_SAMPLES / "bad_ui.html").read_text(encoding="utf-8")
GOOD_HTML = (_SAMPLES / "good_ui.html").read_text(encoding="utf-8")


class TestBadUiScore:
    def test_score_is_low(self):
        result = scoring_engine.analyze(parse(BAD_HTML))
        assert result.overall_score < 70, f"Expected score < 70, got {result.overall_score}"

    def test_many_issues_found(self):
        result = scoring_engine.analyze(parse(BAD_HTML))
        assert len(result.issues) >= 6, f"Expected ≥6 issues, got {len(result.issues)}"

    def test_critical_issues_present(self):
        result = scoring_engine.analyze(parse(BAD_HTML))
        critical = [i for i in result.issues if i.severity == Severity.CRITICAL]
        assert len(critical) >= 1, "Expected at least one CRITICAL issue (missing labels)"

    def test_specific_rules_fire(self):
        result = scoring_engine.analyze(parse(BAD_HTML))
        fired = {i.rule_id for i in result.issues}
        expected = {
            "T1_body_font_size",     # 11px body
            "T2_font_family_count",  # 4 fonts
            "T3_line_height",        # 1.1 line-height
            "T4_heading_hierarchy",  # h1/h2 ratio < 1.2
            "B1_button_style_count", # 3 distinct styles
            "B3_focus_style",        # no :focus rules
            "B4_touch_target",       # buttons 28px high
            "F1_missing_label",      # inputs without labels
            "TBL1_missing_header",   # table has no <thead>
            "TBL3_cell_padding",     # 3px cell padding
            "S1_button_padding",     # 3px button padding
            "S2_card_padding",       # 6px card padding
            "S3_off_grid_spacing",   # 3/6/7px values
            "D1_kpi_card_overload",  # 12 cards
            "D2_low_whitespace",     # dense layout
        }
        missing = expected - fired
        assert not missing, f"Expected rules did not fire: {sorted(missing)}"


class TestGoodUiScore:
    def test_score_is_high(self):
        result = scoring_engine.analyze(parse(GOOD_HTML))
        assert result.overall_score >= 80, f"Expected score ≥80, got {result.overall_score}"

    def test_no_critical_issues(self):
        result = scoring_engine.analyze(parse(GOOD_HTML))
        critical = [i for i in result.issues if i.severity == Severity.CRITICAL]
        assert critical == [], f"Unexpected CRITICAL issues: {[i.rule_id for i in critical]}"

    def test_key_rules_do_not_fire(self):
        result = scoring_engine.analyze(parse(GOOD_HTML))
        fired = {i.rule_id for i in result.issues}
        should_not_fire = {
            "T1_body_font_size",
            "T4_heading_hierarchy",
            "B1_button_style_count",
            "B3_focus_style",
            "B4_touch_target",
            "F1_missing_label",
            "TBL1_missing_header",
            "S2_card_padding",
            "D1_kpi_card_overload",
            "D2_low_whitespace",
        }
        unexpected = should_not_fire & fired
        assert not unexpected, f"Rules fired unexpectedly on good UI: {sorted(unexpected)}"


class TestComparison:
    def test_good_scores_higher_than_bad(self):
        good_score = scoring_engine.analyze(parse(GOOD_HTML)).overall_score
        bad_score = scoring_engine.analyze(parse(BAD_HTML)).overall_score
        assert good_score > bad_score, f"Good: {good_score}, Bad: {bad_score}"

    def test_good_has_fewer_issues(self):
        good_count = len(scoring_engine.analyze(parse(GOOD_HTML)).issues)
        bad_count = len(scoring_engine.analyze(parse(BAD_HTML)).issues)
        assert good_count < bad_count, f"Good: {good_count}, Bad: {bad_count}"

    def test_issues_sorted_by_gain(self):
        result = scoring_engine.analyze(parse(BAD_HTML))
        gains = [i.estimated_gain for i in result.issues]
        assert gains == sorted(gains, reverse=True)
