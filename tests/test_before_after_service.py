"""
Module 21 — Before/After Preview tests.

All tests are deterministic: no DB, no network, pure dict input.
"""
from __future__ import annotations

from backend.services import before_after_service


# ── helpers ───────────────────────────────────────────────────────────────────

def _result(score: float, issues: list[dict]) -> dict:
    return {"overall_score": score, "issues": issues}


def _issue(rule_id: str, category: str, severity: str,
           gain: float, message: str = "msg") -> dict:
    return {
        "rule_id": rule_id,
        "category": category,
        "severity": severity,
        "message": message,
        "estimated_gain": gain,
    }


# ── empty result ──────────────────────────────────────────────────────────────

class TestEmptyResult:
    def test_no_issues_returns_same_score(self):
        out = before_after_service.generate(_result(72.0, []))
        assert out["current_score"] == 72.0
        assert out["projected_score"] == 72.0
        assert out["score_delta"] == 0.0

    def test_no_issues_empty_chain_and_gains(self):
        out = before_after_service.generate(_result(72.0, []))
        assert out["fix_chain"] == []
        assert out["category_gains"] == []

    def test_zero_score_no_issues(self):
        out = before_after_service.generate(_result(0.0, []))
        assert out["current_score"] == 0.0
        assert out["projected_score"] == 0.0


# ── single issue ──────────────────────────────────────────────────────────────

class TestSingleIssue:
    def test_projected_adds_gain(self):
        out = before_after_service.generate(
            _result(70.0, [_issue("T1", "typography", "high", 5.0)]))
        assert out["projected_score"] == 75.0
        assert out["score_delta"] == 5.0

    def test_fix_chain_has_one_entry(self):
        out = before_after_service.generate(
            _result(70.0, [_issue("T1", "typography", "high", 5.0)]))
        assert len(out["fix_chain"]) == 1
        step = out["fix_chain"][0]
        assert step["rule_id"] == "T1"
        assert step["score_before"] == 70.0
        assert step["score_after"] == 75.0
        assert step["gain"] == 5.0

    def test_category_gains_has_one_entry(self):
        out = before_after_service.generate(
            _result(70.0, [_issue("T1", "typography", "high", 5.0)]))
        assert len(out["category_gains"]) == 1
        assert out["category_gains"][0]["category"] == "typography"
        assert out["category_gains"][0]["gain"] == 5.0
        assert out["category_gains"][0]["issue_count"] == 1


# ── sort order ────────────────────────────────────────────────────────────────

class TestSortOrder:
    def test_fix_chain_sorted_by_gain_descending(self):
        issues = [
            _issue("S1", "spacing", "medium", 2.0),
            _issue("T1", "typography", "high", 8.0),
            _issue("C1", "contrast", "critical", 5.0),
        ]
        out = before_after_service.generate(_result(60.0, issues))
        gains = [step["gain"] for step in out["fix_chain"]]
        assert gains == sorted(gains, reverse=True)

    def test_fix_chain_first_step_is_highest_gain(self):
        issues = [
            _issue("S1", "spacing", "medium", 2.0),
            _issue("T1", "typography", "high", 8.0),
        ]
        out = before_after_service.generate(_result(60.0, issues))
        assert out["fix_chain"][0]["rule_id"] == "T1"

    def test_category_gains_sorted_descending(self):
        issues = [
            _issue("S1", "spacing", "medium", 2.0),
            _issue("T1", "typography", "high", 8.0),
            _issue("C1", "contrast", "critical", 5.0),
        ]
        out = before_after_service.generate(_result(60.0, issues))
        gains = [cg["gain"] for cg in out["category_gains"]]
        assert gains == sorted(gains, reverse=True)


# ── cumulative running score ──────────────────────────────────────────────────

class TestCumulativeScore:
    def test_running_score_chains_correctly(self):
        # start=50, gains: 10, 5, 3 → 60, 65, 68
        issues = [
            _issue("A", "spacing", "critical", 10.0),
            _issue("B", "typography", "high", 5.0),
            _issue("C", "contrast", "medium", 3.0),
        ]
        out = before_after_service.generate(_result(50.0, issues))
        chain = out["fix_chain"]
        assert chain[0]["score_before"] == 50.0
        assert chain[0]["score_after"] == 60.0
        assert chain[1]["score_before"] == 60.0
        assert chain[1]["score_after"] == 65.0
        assert chain[2]["score_before"] == 65.0
        assert chain[2]["score_after"] == 68.0

    def test_projected_score_equals_last_chain_step(self):
        issues = [
            _issue("A", "spacing", "high", 6.0),
            _issue("B", "typography", "medium", 4.0),
        ]
        out = before_after_service.generate(_result(60.0, issues))
        assert out["projected_score"] == out["fix_chain"][-1]["score_after"]


# ── cap at 100 ────────────────────────────────────────────────────────────────

class TestCapAt100:
    def test_projected_never_exceeds_100(self):
        issues = [_issue("A", "spacing", "critical", 50.0)]
        out = before_after_service.generate(_result(90.0, issues))
        assert out["projected_score"] == 100.0
        assert out["score_delta"] == 10.0

    def test_fix_chain_capped_at_100(self):
        issues = [_issue("A", "spacing", "critical", 50.0)]
        out = before_after_service.generate(_result(90.0, issues))
        assert out["fix_chain"][0]["score_after"] == 100.0

    def test_many_issues_caps_at_100(self):
        issues = [_issue(f"X{i}", "typography", "critical", 15.0) for i in range(10)]
        out = before_after_service.generate(_result(50.0, issues))
        assert out["projected_score"] == 100.0
        for step in out["fix_chain"]:
            assert step["score_after"] <= 100.0


# ── category grouping ─────────────────────────────────────────────────────────

class TestCategoryGrouping:
    def test_same_category_issues_summed(self):
        issues = [
            _issue("T1", "typography", "high", 4.0),
            _issue("T2", "typography", "medium", 3.0),
        ]
        out = before_after_service.generate(_result(60.0, issues))
        typo = next(cg for cg in out["category_gains"] if cg["category"] == "typography")
        assert typo["gain"] == 7.0
        assert typo["issue_count"] == 2

    def test_multiple_categories_all_present(self):
        issues = [
            _issue("T1", "typography", "high", 4.0),
            _issue("S1", "spacing", "medium", 2.0),
            _issue("C1", "contrast", "critical", 6.0),
        ]
        out = before_after_service.generate(_result(60.0, issues))
        cats = {cg["category"] for cg in out["category_gains"]}
        assert cats == {"typography", "spacing", "contrast"}

    def test_zero_gain_issue_still_counted(self):
        issues = [
            _issue("T1", "typography", "high", 4.0),
            _issue("T2", "typography", "low", 0.0),
        ]
        out = before_after_service.generate(_result(60.0, issues))
        typo = next(cg for cg in out["category_gains"] if cg["category"] == "typography")
        assert typo["issue_count"] == 2


# ── edge cases ────────────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_missing_fields_handled_gracefully(self):
        result = {"overall_score": 55.0, "issues": [{"estimated_gain": 5.0}]}
        out = before_after_service.generate(result)
        assert out["projected_score"] == 60.0

    def test_missing_overall_score_defaults_to_zero(self):
        out = before_after_service.generate({"issues": []})
        assert out["current_score"] == 0.0

    def test_score_delta_precision(self):
        issues = [_issue("A", "spacing", "high", 3.3)]
        out = before_after_service.generate(_result(60.0, issues))
        assert out["score_delta"] == round(out["projected_score"] - out["current_score"], 1)
