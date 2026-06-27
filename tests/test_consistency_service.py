"""
Module 16 — Consistency Checker tests.

All tests are deterministic: no DB, no network.
consistency_service.build_report() is a pure function — tests supply
controlled page/analysis dicts and assert on the output.
"""
from __future__ import annotations

import json


from backend.services import consistency_service


# ── helpers ───────────────────────────────────────────────────────────────────

def _page(page_id: int, url: str = "") -> dict:
    return {"id": page_id, "url": url or f"/page-{page_id}", "title": f"Page {page_id}"}


def _analysis(score: float, rule_ids: list[str]) -> dict:
    result_json = json.dumps({
        "overall_score": score,
        "issues": [{"rule_id": r} for r in rule_ids],
    })
    return {"id": 1, "overall_score": score, "result_json": result_json, "source": "html"}


# ── empty / insufficient data ─────────────────────────────────────────────────

class TestInsufficientData:
    def test_no_pages_returns_empty(self):
        result = consistency_service.build_report([], [])
        assert result["pages_analyzed"] == 0
        assert result["common_issues"] == []

    def test_one_page_returns_empty_note(self):
        pages = [_page(1)]
        analyses = [_analysis(80.0, ["T1_body_font_size"])]
        result = consistency_service.build_report(pages, analyses)
        assert "note" in result
        assert result["pages_analyzed"] == 1

    def test_one_page_with_none_analysis(self):
        result = consistency_service.build_report([_page(1)], [None])
        assert result["pages_analyzed"] == 0

    def test_two_pages_both_no_analysis(self):
        result = consistency_service.build_report([_page(1), _page(2)], [None, None])
        assert result["pages_analyzed"] == 0
        assert "note" in result


# ── common issues ─────────────────────────────────────────────────────────────

class TestCommonIssues:
    def test_rules_on_all_pages_are_common(self):
        pages = [_page(1), _page(2)]
        analyses = [
            _analysis(75.0, ["T1_body_font_size", "S1_button_padding"]),
            _analysis(80.0, ["T1_body_font_size", "B3_focus_style"]),
        ]
        result = consistency_service.build_report(pages, analyses)
        assert "T1_body_font_size" in result["common_issues"]

    def test_rule_on_one_page_not_in_common(self):
        pages = [_page(1), _page(2)]
        analyses = [
            _analysis(75.0, ["T1_body_font_size", "S1_button_padding"]),
            _analysis(80.0, ["T1_body_font_size"]),
        ]
        result = consistency_service.build_report(pages, analyses)
        assert "S1_button_padding" not in result["common_issues"]

    def test_no_shared_rules_means_empty_common(self):
        pages = [_page(1), _page(2)]
        analyses = [
            _analysis(75.0, ["T1_body_font_size"]),
            _analysis(80.0, ["B3_focus_style"]),
        ]
        result = consistency_service.build_report(pages, analyses)
        assert result["common_issues"] == []

    def test_three_pages_all_share_one_rule(self):
        pages = [_page(i) for i in range(1, 4)]
        analyses = [
            _analysis(70.0, ["S1_button_padding", "T1_body_font_size"]),
            _analysis(75.0, ["S1_button_padding", "B3_focus_style"]),
            _analysis(80.0, ["S1_button_padding"]),
        ]
        result = consistency_service.build_report(pages, analyses)
        assert "S1_button_padding" in result["common_issues"]
        assert "T1_body_font_size" not in result["common_issues"]


# ── divergent issues ──────────────────────────────────────────────────────────

class TestDivergentIssues:
    def test_rule_only_on_one_page_is_divergent(self):
        pages = [_page(1), _page(2)]
        analyses = [
            _analysis(75.0, ["T1_body_font_size", "TBL1_missing_header"]),
            _analysis(80.0, ["T1_body_font_size"]),
        ]
        result = consistency_service.build_report(pages, analyses)
        assert "TBL1_missing_header" in result["divergent_issues"]

    def test_divergent_issue_lists_which_pages(self):
        pages = [_page(1), _page(2)]
        analyses = [
            _analysis(75.0, ["TBL1_missing_header"]),
            _analysis(80.0, []),
        ]
        result = consistency_service.build_report(pages, analyses)
        pages_with_issue = result["divergent_issues"]["TBL1_missing_header"]
        assert len(pages_with_issue) == 1
        assert pages_with_issue[0]["page_id"] == 1

    def test_divergent_count(self):
        pages = [_page(1), _page(2)]
        analyses = [
            _analysis(75.0, ["A", "B", "C"]),
            _analysis(80.0, ["A"]),
        ]
        result = consistency_service.build_report(pages, analyses)
        assert result["divergent_count"] == 2  # B and C are divergent


# ── score stats ───────────────────────────────────────────────────────────────

class TestScoreStats:
    def test_avg_score(self):
        pages = [_page(1), _page(2)]
        analyses = [_analysis(70.0, []), _analysis(90.0, [])]
        result = consistency_service.build_report(pages, analyses)
        assert result["avg_score"] == 80.0

    def test_min_max_score(self):
        pages = [_page(1), _page(2), _page(3)]
        analyses = [_analysis(60.0, []), _analysis(80.0, []), _analysis(100.0, [])]
        result = consistency_service.build_report(pages, analyses)
        assert result["min_score"] == 60.0
        assert result["max_score"] == 100.0

    def test_score_range(self):
        pages = [_page(1), _page(2)]
        analyses = [_analysis(72.0, []), _analysis(84.0, [])]
        result = consistency_service.build_report(pages, analyses)
        assert result["score_range"] == 12.0


# ── consistency level ─────────────────────────────────────────────────────────

class TestConsistencyLevel:
    def test_high_consistency_small_range_few_divergent(self):
        pages = [_page(1), _page(2)]
        analyses = [_analysis(80.0, ["T1_body_font_size"]), _analysis(82.0, ["T1_body_font_size"])]
        result = consistency_service.build_report(pages, analyses)
        assert result["consistency_level"] == "high"

    def test_low_consistency_large_range(self):
        pages = [_page(1), _page(2)]
        analyses = [
            _analysis(50.0, ["A", "B", "C", "D", "E", "F", "G"]),
            _analysis(90.0, ["X", "Y", "Z"]),
        ]
        result = consistency_service.build_report(pages, analyses)
        assert result["consistency_level"] == "low"


# ── per-page unique issues ────────────────────────────────────────────────────

class TestPerPageUnique:
    def test_per_page_report_has_unique_issues(self):
        pages = [_page(1), _page(2)]
        analyses = [
            _analysis(75.0, ["T1_body_font_size", "TBL1_missing_header"]),
            _analysis(80.0, ["T1_body_font_size"]),
        ]
        result = consistency_service.build_report(pages, analyses)
        page1_entry = next(p for p in result["pages"] if p["page_id"] == 1)
        assert "TBL1_missing_header" in page1_entry["unique_issues"]

    def test_page_with_no_unique_issues_has_empty_list(self):
        pages = [_page(1), _page(2)]
        analyses = [
            _analysis(75.0, ["T1_body_font_size"]),
            _analysis(80.0, ["T1_body_font_size"]),
        ]
        result = consistency_service.build_report(pages, analyses)
        for page_entry in result["pages"]:
            assert page_entry["unique_issues"] == []
