"""
Module 18 — Achievements / Gamification tests.

All tests are deterministic: no DB, no network.
achievement_service.evaluate() is a pure function — tests supply
controlled inputs and assert badge earned/not-earned status.
"""
from __future__ import annotations

import json

import pytest

from backend.services import achievement_service


# ── helpers ───────────────────────────────────────────────────────────────────

def _rj(score: float, rule_ids: list[str], severities: list[str] | None = None,
        cat_scores: list[dict] | None = None) -> str:
    issues = [
        {"rule_id": r, "severity": (severities[i] if severities else "high")}
        for i, r in enumerate(rule_ids)
    ]
    blob: dict = {"overall_score": score, "issues": issues}
    if cat_scores:
        blob["category_scores"] = cat_scores
    return json.dumps(blob)


def _earned_ids(badges: list[dict]) -> set[str]:
    return {b["id"] for b in badges if b["earned"]}


# ── first_analysis ────────────────────────────────────────────────────────────

class TestFirstAnalysis:
    def test_no_analyses_not_earned(self):
        badges = achievement_service.evaluate(0, None, [])
        assert "first_analysis" not in _earned_ids(badges)

    def test_one_analysis_earned(self):
        badges = achievement_service.evaluate(1, _rj(75.0, []), [75.0])
        assert "first_analysis" in _earned_ids(badges)


# ── score_90_plus ─────────────────────────────────────────────────────────────

class TestScore90Plus:
    def test_score_89_not_earned(self):
        badges = achievement_service.evaluate(1, _rj(89.0, []), [89.0])
        assert "score_90_plus" not in _earned_ids(badges)

    def test_score_90_earned(self):
        badges = achievement_service.evaluate(1, _rj(90.0, []), [90.0])
        assert "score_90_plus" in _earned_ids(badges)

    def test_score_95_earned(self):
        badges = achievement_service.evaluate(1, _rj(95.0, []), [95.0])
        assert "score_90_plus" in _earned_ids(badges)

    def test_not_earned_has_progress_string(self):
        badges = achievement_service.evaluate(1, _rj(80.0, []), [80.0])
        badge = next(b for b in badges if b["id"] == "score_90_plus")
        assert badge["progress"] is not None
        assert "90" in badge["progress"]


# ── perfect_score ─────────────────────────────────────────────────────────────

class TestPerfectScore:
    def test_score_99_not_earned(self):
        badges = achievement_service.evaluate(1, _rj(99.0, []), [99.0])
        assert "perfect_score" not in _earned_ids(badges)

    def test_score_100_earned(self):
        badges = achievement_service.evaluate(1, _rj(100.0, []), [100.0])
        assert "perfect_score" in _earned_ids(badges)


# ── quick_improver ────────────────────────────────────────────────────────────

class TestQuickImprover:
    def test_single_analysis_not_earned(self):
        badges = achievement_service.evaluate(1, _rj(75.0, []), [75.0])
        assert "quick_improver" not in _earned_ids(badges)

    def test_improvement_of_9_not_earned(self):
        badges = achievement_service.evaluate(2, _rj(79.0, []), [70.0, 79.0])
        assert "quick_improver" not in _earned_ids(badges)

    def test_improvement_of_10_earned(self):
        badges = achievement_service.evaluate(2, _rj(80.0, []), [70.0, 80.0])
        assert "quick_improver" in _earned_ids(badges)

    def test_non_consecutive_improvement_counts(self):
        # 72 → 75 → 85 — the 75→85 jump is 10
        badges = achievement_service.evaluate(3, _rj(85.0, []), [72.0, 75.0, 85.0])
        assert "quick_improver" in _earned_ids(badges)


# ── typography_master ─────────────────────────────────────────────────────────

class TestTypographyMaster:
    def test_no_typo_issues_earned(self):
        badges = achievement_service.evaluate(1, _rj(80.0, ["S1_button_padding"]), [80.0])
        assert "typography_master" in _earned_ids(badges)

    def test_typo_issue_fires_not_earned(self):
        badges = achievement_service.evaluate(1, _rj(75.0, ["T1_body_font_size"]), [75.0])
        assert "typography_master" not in _earned_ids(badges)

    def test_no_analysis_not_earned(self):
        badges = achievement_service.evaluate(0, None, [])
        assert "typography_master" not in _earned_ids(badges)


# ── accessibility_champ ───────────────────────────────────────────────────────

class TestAccessibilityChamp:
    def test_no_a11y_issues_earned(self):
        badges = achievement_service.evaluate(1, _rj(80.0, ["T1_body_font_size"]), [80.0])
        assert "accessibility_champ" in _earned_ids(badges)

    def test_contrast_issue_not_earned(self):
        badges = achievement_service.evaluate(1, _rj(70.0, ["C1_wcag_aa_contrast"]), [70.0])
        assert "accessibility_champ" not in _earned_ids(badges)

    def test_missing_label_not_earned(self):
        badges = achievement_service.evaluate(1, _rj(75.0, ["F1_missing_label"]), [75.0])
        assert "accessibility_champ" not in _earned_ids(badges)


# ── design_system_clean ───────────────────────────────────────────────────────

class TestDesignSystemClean:
    def test_no_ds_issues_earned(self):
        badges = achievement_service.evaluate(1, _rj(80.0, ["T1_body_font_size"]), [80.0])
        assert "design_system_clean" in _earned_ids(badges)

    def test_ds1_fires_not_earned(self):
        badges = achievement_service.evaluate(1, _rj(70.0, ["DS1_button_color_variants"]), [70.0])
        assert "design_system_clean" not in _earned_ids(badges)


# ── consistency_high ──────────────────────────────────────────────────────────

class TestConsistencyHigh:
    def test_high_level_earned(self):
        badges = achievement_service.evaluate(1, _rj(80.0, []), [80.0], consistency_level="high")
        assert "consistency_high" in _earned_ids(badges)

    def test_medium_level_not_earned(self):
        badges = achievement_service.evaluate(1, _rj(80.0, []), [80.0], consistency_level="medium")
        assert "consistency_high" not in _earned_ids(badges)

    def test_no_level_not_earned(self):
        badges = achievement_service.evaluate(1, _rj(80.0, []), [80.0], consistency_level=None)
        assert "consistency_high" not in _earned_ids(badges)


# ── analysis count badges ─────────────────────────────────────────────────────

class TestAnalysisCountBadges:
    def test_five_analyses_not_earned_at_four(self):
        badges = achievement_service.evaluate(4, _rj(80.0, []), [80.0] * 4)
        assert "five_analyses" not in _earned_ids(badges)

    def test_five_analyses_earned_at_five(self):
        badges = achievement_service.evaluate(5, _rj(80.0, []), [80.0] * 5)
        assert "five_analyses" in _earned_ids(badges)

    def test_ten_analyses_earned_at_ten(self):
        badges = achievement_service.evaluate(10, _rj(80.0, []), [80.0] * 10)
        assert "ten_analyses" in _earned_ids(badges)


# ── no_critical ───────────────────────────────────────────────────────────────

class TestNoCritical:
    def test_no_critical_severities_earned(self):
        badges = achievement_service.evaluate(1, _rj(80.0, ["T1_body_font_size"], ["high"]), [80.0])
        assert "no_critical" in _earned_ids(badges)

    def test_critical_severity_not_earned(self):
        badges = achievement_service.evaluate(1, _rj(60.0, ["C1_wcag_aa_contrast"], ["critical"]), [60.0])
        assert "no_critical" not in _earned_ids(badges)


# ── improving_streak ──────────────────────────────────────────────────────────

class TestImprovingStreak:
    def test_three_consecutive_improvements_earned(self):
        badges = achievement_service.evaluate(3, _rj(80.0, []), [70.0, 75.0, 80.0])
        assert "improving_streak" in _earned_ids(badges)

    def test_two_improvements_not_enough(self):
        badges = achievement_service.evaluate(2, _rj(80.0, []), [70.0, 80.0])
        assert "improving_streak" not in _earned_ids(badges)

    def test_declining_then_improving_not_earned(self):
        badges = achievement_service.evaluate(3, _rj(80.0, []), [80.0, 70.0, 75.0])
        assert "improving_streak" not in _earned_ids(badges)


# ── badge structure ───────────────────────────────────────────────────────────

class TestBadgeStructure:
    def test_all_badges_have_required_fields(self):
        badges = achievement_service.evaluate(1, _rj(80.0, []), [80.0])
        for b in badges:
            assert "id" in b
            assert "name" in b
            assert "description" in b
            assert "icon" in b
            assert "earned" in b

    def test_14_badges_total(self):
        badges = achievement_service.evaluate(0, None, [])
        assert len(badges) == 14

    def test_earned_badges_helper(self):
        badges = achievement_service.evaluate(1, _rj(90.0, []), [90.0])
        earned = achievement_service.earned_badges(badges)
        assert all(b["earned"] for b in earned)
        assert len(earned) > 0
