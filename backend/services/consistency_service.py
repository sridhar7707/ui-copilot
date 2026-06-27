"""
Module 16 — Consistency Checker.

Compares the latest analysis across all pages in a project and flags
divergences in rule firing, score spread, and common vs. unique issues.

All public functions are pure: they accept pre-fetched dicts and return
plain dicts — no DB access, no side effects.
"""
from __future__ import annotations

import json
from typing import Optional


# ── public API ────────────────────────────────────────────────────────────────

def build_report(
    pages: list[dict],
    analyses: list[Optional[dict]],
) -> dict:
    """
    Build a cross-page consistency report.

    Parameters
    ----------
    pages      : list of page rows (id, url, title)
    analyses   : latest analysis row per page, same index order as ``pages``.
                 Elements are None when a page has no stored analysis yet.

    The analysis row must include ``result_json`` (a JSON string with
    ``overall_score`` and ``issues`` list from analysis_repo._serialise).
    """
    active_pairs = [
        (p, a) for p, a in zip(pages, analyses)
        if a is not None and a.get("result_json")
    ]

    if len(active_pairs) < 2:
        return _empty_report(len(pages), len(active_pairs))

    page_data = [_parse(p, a) for p, a in active_pairs]
    return _compute(page_data)


# ── internal helpers ──────────────────────────────────────────────────────────

def _parse(page: dict, analysis: dict) -> dict:
    try:
        blob = json.loads(analysis["result_json"])
    except (json.JSONDecodeError, KeyError):
        blob = {}
    rule_ids = {i["rule_id"] for i in blob.get("issues", [])}
    return {
        "page_id": page["id"],
        "url": page.get("url", ""),
        "title": page.get("title", ""),
        "score": blob.get("overall_score", 0.0),
        "rule_ids": rule_ids,
    }


def _compute(page_data: list[dict]) -> dict:
    all_sets = [p["rule_ids"] for p in page_data]
    scores = [p["score"] for p in page_data]
    n = len(page_data)

    common_rules = set.intersection(*all_sets) if all_sets else set()

    # Rules that fire on some pages but not all (divergent)
    all_rules = set.union(*all_sets) if all_sets else set()
    divergent_rules: dict[str, list] = {}
    for rule in sorted(all_rules - common_rules):
        pages_with_rule = [
            {"page_id": p["page_id"], "url": p["url"]}
            for p in page_data
            if rule in p["rule_ids"]
        ]
        divergent_rules[rule] = pages_with_rule

    avg_score = round(sum(scores) / n, 1)
    score_range = round(max(scores) - min(scores), 1)
    consistency_level = _level(score_range, len(divergent_rules))

    return {
        "pages_analyzed": n,
        "avg_score": avg_score,
        "min_score": round(min(scores), 1),
        "max_score": round(max(scores), 1),
        "score_range": score_range,
        "consistency_level": consistency_level,
        "common_issues": sorted(common_rules),
        "divergent_issues": divergent_rules,
        "divergent_count": len(divergent_rules),
        "pages": [
            {
                "page_id": p["page_id"],
                "url": p["url"],
                "title": p["title"],
                "score": p["score"],
                "unique_issues": sorted(p["rule_ids"] - common_rules),
            }
            for p in page_data
        ],
    }


def _level(score_range: float, divergent_count: int) -> str:
    if score_range <= 5 and divergent_count <= 2:
        return "high"
    if score_range <= 15 and divergent_count <= 6:
        return "medium"
    return "low"


def _empty_report(total_pages: int, active: int) -> dict:
    return {
        "pages_analyzed": active,
        "total_pages": total_pages,
        "avg_score": None,
        "min_score": None,
        "max_score": None,
        "score_range": None,
        "consistency_level": None,
        "common_issues": [],
        "divergent_issues": {},
        "divergent_count": 0,
        "pages": [],
        "note": "At least 2 pages with analyses are required for a consistency report.",
    }
