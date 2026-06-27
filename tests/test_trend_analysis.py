"""
Module 17 — UI Trend Analysis tests.

All tests are deterministic: no DB, no network. trend_service is a pure function
module — tests feed it pre-built lists and assert the output.
"""
from __future__ import annotations


from backend.services import trend_service


# ── helpers ───────────────────────────────────────────────────────────────────

def _a(score: float, date: str = "2026-01-01T00:00:00") -> dict:
    return {"overall_score": score, "created_at": date}


# ── page_trend — empty input ──────────────────────────────────────────────────

class TestPageTrendEmpty:
    def test_returns_empty_scores_list(self):
        result = trend_service.page_trend([])
        assert result["scores"] == []

    def test_count_is_zero(self):
        assert trend_service.page_trend([])["count"] == 0

    def test_latest_is_none(self):
        assert trend_service.page_trend([])["latest"] is None

    def test_delta_is_none(self):
        assert trend_service.page_trend([])["delta"] is None

    def test_improving_is_none(self):
        assert trend_service.page_trend([])["improving"] is None


# ── page_trend — single analysis ──────────────────────────────────────────────

class TestPageTrendSingle:
    def setup_method(self):
        self.result = trend_service.page_trend([_a(72.5, "2026-01-15T10:00:00")])

    def test_count_is_one(self):
        assert self.result["count"] == 1

    def test_latest_equals_only_score(self):
        assert self.result["latest"] == 72.5

    def test_best_equals_only_score(self):
        assert self.result["best"] == 72.5

    def test_worst_equals_only_score(self):
        assert self.result["worst"] == 72.5

    def test_delta_is_none_for_single(self):
        assert self.result["delta"] is None

    def test_improving_is_none_for_single(self):
        assert self.result["improving"] is None

    def test_scores_list_has_one_entry(self):
        assert len(self.result["scores"]) == 1

    def test_scores_entry_has_date_and_score(self):
        entry = self.result["scores"][0]
        assert "date" in entry and "score" in entry


# ── page_trend — improving series ────────────────────────────────────────────

class TestPageTrendImproving:
    def setup_method(self):
        self.analyses = [
            _a(72.0, "2026-01-01T00:00:00"),
            _a(80.0, "2026-02-01T00:00:00"),
            _a(84.0, "2026-03-01T00:00:00"),
            _a(91.0, "2026-04-01T00:00:00"),
        ]
        self.result = trend_service.page_trend(self.analyses)

    def test_count(self):
        assert self.result["count"] == 4

    def test_latest_is_last_chronological(self):
        assert self.result["latest"] == 91.0

    def test_best(self):
        assert self.result["best"] == 91.0

    def test_worst(self):
        assert self.result["worst"] == 72.0

    def test_delta_positive(self):
        assert self.result["delta"] == 19.0

    def test_improving_true(self):
        assert self.result["improving"] is True

    def test_scores_chronological_order(self):
        scores_list = [s["score"] for s in self.result["scores"]]
        assert scores_list == sorted(scores_list)


# ── page_trend — declining series ────────────────────────────────────────────

class TestPageTrendDeclining:
    def setup_method(self):
        self.result = trend_service.page_trend([
            _a(90.0, "2026-01-01T00:00:00"),
            _a(75.0, "2026-02-01T00:00:00"),
        ])

    def test_delta_negative(self):
        assert self.result["delta"] == -15.0

    def test_improving_false(self):
        assert self.result["improving"] is False


# ── page_trend — unordered input is sorted ───────────────────────────────────

class TestPageTrendOrdering:
    def test_unordered_input_produces_chronological_output(self):
        analyses = [
            _a(84.0, "2026-03-01T00:00:00"),
            _a(72.0, "2026-01-01T00:00:00"),
            _a(80.0, "2026-02-01T00:00:00"),
        ]
        result = trend_service.page_trend(analyses)
        dates = [s["date"] for s in result["scores"]]
        assert dates == sorted(dates)

    def test_latest_is_most_recent_regardless_of_input_order(self):
        analyses = [
            _a(91.0, "2026-04-01T00:00:00"),
            _a(72.0, "2026-01-01T00:00:00"),
        ]
        result = trend_service.page_trend(analyses)
        assert result["latest"] == 91.0


# ── project_trend — empty ─────────────────────────────────────────────────────

class TestProjectTrendEmpty:
    def test_no_pages(self):
        result = trend_service.project_trend([])
        assert result["page_count"] == 0
        assert result["avg_latest_score"] is None
        assert result["total_analyses"] == 0

    def test_pages_with_no_analyses(self):
        empty = trend_service.page_trend([])
        result = trend_service.project_trend([empty, empty])
        assert result["page_count"] == 2
        assert result["avg_latest_score"] is None
        assert result["total_analyses"] == 0


# ── project_trend — aggregation ───────────────────────────────────────────────

class TestProjectTrendAggregation:
    def setup_method(self):
        pt1 = trend_service.page_trend([
            _a(72.0, "2026-01-01T00:00:00"),
            _a(80.0, "2026-02-01T00:00:00"),
        ])
        pt2 = trend_service.page_trend([
            _a(60.0, "2026-01-01T00:00:00"),
            _a(90.0, "2026-02-01T00:00:00"),
        ])
        self.result = trend_service.project_trend([pt1, pt2])

    def test_page_count(self):
        assert self.result["page_count"] == 2

    def test_total_analyses(self):
        assert self.result["total_analyses"] == 4

    def test_avg_latest_score(self):
        # latest scores: 80 and 90 → average 85
        assert self.result["avg_latest_score"] == 85.0

    def test_best_score(self):
        assert self.result["best_score"] == 90.0

    def test_worst_score(self):
        assert self.result["worst_score"] == 60.0

    def test_pages_improving(self):
        assert self.result["pages_improving"] == 2

    def test_pages_declining(self):
        assert self.result["pages_declining"] == 0
