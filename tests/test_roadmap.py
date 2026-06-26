"""
Module 7 — Improvement Roadmap: AnalysisResult.roadmap buckets.
"""
from __future__ import annotations

import pytest

from backend.models.issue import Category
from backend.services import scoring_engine
from tests.fixtures import bad_page, clean_page


@pytest.fixture
def bad_result():
    return scoring_engine.analyze(bad_page())


@pytest.fixture
def clean_result():
    return scoring_engine.analyze(clean_page())


# ── top_issues ────────────────────────────────────────────────────────────────

class TestTopIssues:
    def test_at_most_ten(self, bad_result):
        assert len(bad_result.top_issues) <= 10

    def test_sorted_by_gain_desc(self, bad_result):
        gains = [i.estimated_gain for i in bad_result.top_issues]
        assert gains == sorted(gains, reverse=True)

    def test_subset_of_all_issues(self, bad_result):
        for issue in bad_result.top_issues:
            assert issue in bad_result.issues

    def test_empty_when_no_issues(self, clean_result):
        assert len(clean_result.top_issues) <= 10


# ── quick_wins ────────────────────────────────────────────────────────────────

class TestQuickWins:
    def test_all_are_minutes(self, bad_result):
        for i in bad_result.quick_wins:
            assert "minute" in i.estimated_time

    def test_all_have_positive_gain(self, bad_result):
        for i in bad_result.quick_wins:
            assert i.estimated_gain >= 1.0

    def test_not_empty_on_bad_page(self, bad_result):
        assert bad_result.quick_wins, "bad_page should produce at least one quick win"


# ── high_impact ───────────────────────────────────────────────────────────────

class TestHighImpact:
    def test_at_most_five(self, bad_result):
        assert len(bad_result.high_impact) <= 5

    def test_all_above_threshold(self, bad_result):
        for i in bad_result.high_impact:
            assert i.estimated_gain >= 2.0

    def test_sorted_by_gain_desc(self, bad_result):
        gains = [i.estimated_gain for i in bad_result.high_impact]
        assert gains == sorted(gains, reverse=True)


# ── easy_fixes ────────────────────────────────────────────────────────────────

class TestEasyFixes:
    def test_all_are_minutes(self, bad_result):
        for i in bad_result.easy_fixes:
            assert "minute" in i.estimated_time

    def test_not_empty_on_bad_page(self, bad_result):
        assert bad_result.easy_fixes


# ── accessibility_fixes ───────────────────────────────────────────────────────

class TestAccessibilityFixes:
    def test_all_are_accessibility_category(self, bad_result):
        for i in bad_result.accessibility_fixes:
            assert i.category == Category.ACCESSIBILITY

    def test_not_empty_on_bad_page(self, bad_result):
        assert bad_result.accessibility_fixes


# ── visual_improvements ───────────────────────────────────────────────────────

class TestVisualImprovements:
    def test_all_are_visual_categories(self, bad_result):
        allowed = {Category.VISUAL_HIERARCHY, Category.TYPOGRAPHY}
        for i in bad_result.visual_improvements:
            assert i.category in allowed

    def test_not_empty_on_bad_page(self, bad_result):
        assert bad_result.visual_improvements


# ── consistency_improvements ──────────────────────────────────────────────────

class TestConsistencyImprovements:
    def test_all_are_consistency_category(self, bad_result):
        for i in bad_result.consistency_improvements:
            assert i.category == Category.CONSISTENCY

    def test_not_empty_on_bad_page(self, bad_result):
        assert bad_result.consistency_improvements


# ── roadmap dict ──────────────────────────────────────────────────────────────

class TestRoadmapDict:
    _EXPECTED_KEYS = {
        "top_issues", "quick_wins", "high_impact", "easy_fixes",
        "accessibility_fixes", "visual_improvements", "consistency_improvements",
    }

    def test_roadmap_has_all_keys(self, bad_result):
        assert set(bad_result.roadmap.keys()) == self._EXPECTED_KEYS

    def test_roadmap_values_are_lists(self, bad_result):
        for key, value in bad_result.roadmap.items():
            assert isinstance(value, list), f"{key} should be a list"

    def test_clean_page_roadmap_has_all_keys(self, clean_result):
        assert set(clean_result.roadmap.keys()) == self._EXPECTED_KEYS
