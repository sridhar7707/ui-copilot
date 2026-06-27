"""
Module 17 — UI Trend Analysis.

Pure functions that compute trend metrics from pre-fetched analysis rows.
No DB access here — repositories supply the data, routes call these functions.
"""
from __future__ import annotations

from typing import Optional


def page_trend(analyses: list[dict]) -> dict:
    """
    Compute score-over-time for a single page.

    ``analyses`` is a list of dicts from analysis_repo (any order accepted).
    Returns a chronological scores list plus summary stats.
    """
    if not analyses:
        return {
            "scores": [],
            "count": 0,
            "latest": None,
            "best": None,
            "worst": None,
            "delta": None,
            "improving": None,
        }

    ordered = sorted(analyses, key=lambda a: a["created_at"])
    scores = [
        {"date": a["created_at"], "score": round(a["overall_score"], 1)}
        for a in ordered
    ]
    values = [s["score"] for s in scores]

    delta: Optional[float] = None
    improving: Optional[bool] = None
    if len(values) > 1:
        delta = round(values[-1] - values[0], 1)
        improving = delta > 0

    return {
        "scores": scores,
        "count": len(scores),
        "latest": values[-1],
        "best": max(values),
        "worst": min(values),
        "delta": delta,
        "improving": improving,
    }


def project_trend(page_trends: list[dict]) -> dict:
    """
    Aggregate trend data across all pages in a project.

    ``page_trends`` is a list of dicts returned by ``page_trend()``.
    """
    active = [pt for pt in page_trends if pt["count"] > 0]

    if not active:
        return {
            "page_count": len(page_trends),
            "avg_latest_score": None,
            "best_score": None,
            "worst_score": None,
            "total_analyses": 0,
            "pages_improving": 0,
            "pages_declining": 0,
        }

    latest_scores = [pt["latest"] for pt in active if pt["latest"] is not None]
    all_scores = [s["score"] for pt in active for s in pt["scores"]]

    avg_latest = round(sum(latest_scores) / len(latest_scores), 1) if latest_scores else None
    pages_improving = sum(1 for pt in active if pt.get("improving") is True)
    pages_declining = sum(1 for pt in active if pt.get("improving") is False)

    return {
        "page_count": len(page_trends),
        "avg_latest_score": avg_latest,
        "best_score": max(all_scores) if all_scores else None,
        "worst_score": min(all_scores) if all_scores else None,
        "total_analyses": sum(pt["count"] for pt in active),
        "pages_improving": pages_improving,
        "pages_declining": pages_declining,
    }
