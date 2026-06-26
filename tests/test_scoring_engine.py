from __future__ import annotations

from backend.models.issue import Category
from backend.services import scoring_engine
from tests.fixtures import bad_page, clean_page


class TestCleanPage:
    def test_score_near_100(self):
        result = scoring_engine.analyze(clean_page())
        assert result.overall_score >= 95.0, f"Expected near-100, got {result.overall_score}"

    def test_no_critical_issues(self):
        from backend.models.issue import Severity
        result = scoring_engine.analyze(clean_page())
        critical = [i for i in result.issues if i.severity == Severity.CRITICAL]
        assert critical == []

    def test_all_categories_present(self):
        result = scoring_engine.analyze(clean_page())
        categories = {cs.category for cs in result.category_scores}
        assert categories == set(Category)

    def test_weights_sum_to_one(self):
        result = scoring_engine.analyze(clean_page())
        total_weight = sum(cs.weight for cs in result.category_scores)
        assert abs(total_weight - 1.0) < 0.001


class TestBadPage:
    def test_score_well_below_100(self):
        result = scoring_engine.analyze(bad_page())
        assert result.overall_score < 70.0, f"Expected low score, got {result.overall_score}"

    def test_issues_found(self):
        result = scoring_engine.analyze(bad_page())
        assert len(result.issues) > 0

    def test_issues_sorted_by_gain_descending(self):
        result = scoring_engine.analyze(bad_page())
        gains = [i.estimated_gain for i in result.issues]
        assert gains == sorted(gains, reverse=True)

    def test_estimated_gain_positive(self):
        result = scoring_engine.analyze(bad_page())
        for issue in result.issues:
            assert issue.estimated_gain >= 0.0


class TestScoreBounds:
    def test_score_never_exceeds_100(self):
        result = scoring_engine.analyze(clean_page())
        assert result.overall_score <= 100.0
        for cs in result.category_scores:
            assert cs.score <= 100.0

    def test_score_never_below_zero(self):
        result = scoring_engine.analyze(bad_page())
        assert result.overall_score >= 0.0
        for cs in result.category_scores:
            assert cs.score >= 0.0

    def test_overall_is_weighted_sum(self):
        result = scoring_engine.analyze(bad_page())
        expected = sum(cs.weighted_score for cs in result.category_scores)
        assert abs(result.overall_score - round(expected, 1)) < 0.01


class TestAnalysisResultHelpers:
    def test_top_issues_returns_at_most_10(self):
        result = scoring_engine.analyze(bad_page())
        assert len(result.top_issues) <= 10

    def test_quick_wins_have_gain_and_time(self):
        result = scoring_engine.analyze(bad_page())
        for issue in result.quick_wins:
            assert issue.estimated_gain >= 1.0
            assert "minute" in issue.estimated_time
