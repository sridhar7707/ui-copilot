"""
Module 21 — Before/After Preview.

Pure function: takes a result_json dict (as stored by analysis_repo) and
returns a before/after breakdown showing the projected overall score after
applying all recommended fixes, ordered by estimated impact.

No DB access, no IO — call with pre-fetched data only.
"""
from __future__ import annotations


def generate(result_json: dict) -> dict:
    """
    Compute a before/after score preview from a stored analysis result.

    Args:
        result_json: dict with keys ``overall_score`` and ``issues`` (each
                     issue must have rule_id, category, severity, message,
                     estimated_gain).

    Returns::

        {
            "current_score": float,
            "projected_score": float,
            "score_delta": float,
            "category_gains": [
                {"category": str, "gain": float, "issue_count": int}
            ],
            "fix_chain": [
                {
                    "rule_id": str,
                    "category": str,
                    "severity": str,
                    "message": str,
                    "score_before": float,
                    "score_after": float,
                    "gain": float,
                }
            ],
        }
    """
    current = float(result_json.get("overall_score", 0))
    issues = result_json.get("issues", [])

    sorted_issues = sorted(
        issues,
        key=lambda i: float(i.get("estimated_gain", 0)),
        reverse=True,
    )

    running = current
    fix_chain: list[dict] = []
    for issue in sorted_issues:
        gain = float(issue.get("estimated_gain", 0))
        before = round(running, 1)
        running = min(100.0, running + gain)
        fix_chain.append({
            "rule_id": issue.get("rule_id", ""),
            "category": issue.get("category", ""),
            "severity": issue.get("severity", ""),
            "message": issue.get("message", ""),
            "score_before": before,
            "score_after": round(running, 1),
            "gain": round(gain, 1),
        })

    projected = round(running, 1)

    category_map: dict[str, dict] = {}
    for issue in issues:
        cat = issue.get("category", "unknown")
        gain = float(issue.get("estimated_gain", 0))
        if cat not in category_map:
            category_map[cat] = {"gain": 0.0, "issue_count": 0}
        category_map[cat]["gain"] += gain
        category_map[cat]["issue_count"] += 1

    category_gains = sorted(
        [
            {
                "category": cat,
                "gain": round(vals["gain"], 1),
                "issue_count": vals["issue_count"],
            }
            for cat, vals in category_map.items()
        ],
        key=lambda x: x["gain"],
        reverse=True,
    )

    return {
        "current_score": round(current, 1),
        "projected_score": projected,
        "score_delta": round(projected - current, 1),
        "category_gains": category_gains,
        "fix_chain": fix_chain,
    }
