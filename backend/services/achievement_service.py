"""
Module 18 — Achievements (Gamification).

Evaluates a project's analysis history and awards badges based on
criteria derived from scores, issue patterns, and improvement trajectory.

All public functions are pure: no DB access, no side effects.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Badge:
    id: str
    name: str
    description: str
    icon: str
    earned: bool
    progress: Optional[str] = None  # e.g. "72/90 points needed"


# ── badge definitions (id, name, description, icon, criterion) ────────────────

_BADGE_DEFS = [
    ("first_analysis",       "First Look",            "Completed your first UI analysis.",                                   "🔍"),
    ("score_90_plus",        "90+ Club",              "Achieved a UI score of 90 or above.",                                 "🌟"),
    ("perfect_score",        "Perfect Score",         "Achieved a flawless 100/100.",                                        "💎"),
    ("quick_improver",       "Quick Improver",        "Improved your score by 10+ points in one revision.",                  "📈"),
    ("typography_master",    "Typography Master",     "Zero typography issues in the latest analysis.",                      "🔤"),
    ("accessibility_champ",  "Accessibility Champion","Zero accessibility issues — WCAG AA compliant.",                      "♿"),
    ("design_system_clean",  "Design System Complete","No design-system inconsistencies detected.",                           "🎨"),
    ("consistency_high",     "Consistency Master",    "All pages in the project show high visual consistency.",              "📐"),
    ("dashboard_expert",     "Dashboard Expert",      "No dashboard-specific issues found.",                                  "📊"),
    ("five_analyses",        "Committed Reviewer",    "Ran 5 or more analyses on this project.",                             "🔁"),
    ("ten_analyses",         "Power User",            "Ran 10 or more analyses on this project.",                            "⚡"),
    ("no_critical",          "No Critical Issues",    "Latest analysis contains zero Critical-severity issues.",              "✅"),
    ("all_categories_pass",  "Full House",            "Every scoring category is 70 or above.",                              "🏆"),
    ("improving_streak",     "On a Roll",             "Score improved in three consecutive analyses.",                        "🔥"),
]


# ── public API ────────────────────────────────────────────────────────────────

def evaluate(
    total_analyses: int,
    latest_result_json: Optional[str],
    all_scores: list[float],
    consistency_level: Optional[str] = None,
) -> list[dict]:
    """
    Evaluate and return all badges for a project.

    Parameters
    ----------
    total_analyses     : total number of analyses stored for this project
    latest_result_json : JSON string from analysis_repo._serialise for the
                         latest analysis, or None if no analysis exists yet
    all_scores         : all overall_score values chronologically (oldest first)
    consistency_level  : "high" | "medium" | "low" | None

    Returns a list of badge dicts with earned/not-earned status.
    """
    latest = _parse(latest_result_json)
    badges = []
    for badge_id, name, desc, icon in _BADGE_DEFS:
        earned, progress = _check(
            badge_id, total_analyses, latest, all_scores, consistency_level
        )
        badges.append({
            "id": badge_id,
            "name": name,
            "description": desc,
            "icon": icon,
            "earned": earned,
            "progress": progress,
        })
    return badges


def earned_badges(badges: list[dict]) -> list[dict]:
    """Filter to only earned badges."""
    return [b for b in badges if b["earned"]]


# ── internal ──────────────────────────────────────────────────────────────────

def _parse(result_json: Optional[str]) -> dict:
    if not result_json:
        return {}
    try:
        return json.loads(result_json)
    except (json.JSONDecodeError, TypeError):
        return {}


def _check(
    badge_id: str,
    total_analyses: int,
    latest: dict,
    all_scores: list[float],
    consistency_level: Optional[str],
) -> tuple[bool, Optional[str]]:
    score = latest.get("overall_score", 0.0)
    issues = latest.get("issues", [])
    rule_ids = {i.get("rule_id", "") for i in issues}
    severities = {i.get("severity", "") for i in issues}
    category_scores = latest.get("category_scores", [])

    if badge_id == "first_analysis":
        return total_analyses >= 1, None

    if badge_id == "score_90_plus":
        if score >= 90:
            return True, None
        return False, f"{score:.0f}/90 points"

    if badge_id == "perfect_score":
        return score >= 100, None

    if badge_id == "quick_improver":
        if len(all_scores) >= 2:
            for i in range(1, len(all_scores)):
                if all_scores[i] - all_scores[i - 1] >= 10:
                    return True, None
        return False, None

    if badge_id == "typography_master":
        typo_rules = {"T1_body_font_size", "T2_font_family_count",
                      "T3_line_height", "T4_heading_hierarchy", "T5_heading_size"}
        fired = rule_ids & typo_rules
        if not fired and latest:
            return True, None
        return False, f"{len(fired)} typography issue(s) remaining" if fired else None

    if badge_id == "accessibility_champ":
        a11y_rules = {"C1_wcag_aa_contrast", "B3_focus_style", "B4_touch_target",
                      "F1_missing_label", "F2_placeholder_as_label",
                      "TBL1_missing_header", "CH2_similar_chart_colors"}
        fired = rule_ids & a11y_rules
        if not fired and latest:
            return True, None
        return False, f"{len(fired)} accessibility issue(s) remaining" if fired else None

    if badge_id == "design_system_clean":
        ds_rules = {"DS1_button_color_variants", "DS2_radius_variance",
                    "DS3_padding_combinations", "DS4_off_grid_elements",
                    "DS5_excessive_colours", "DS6_card_padding_range"}
        fired = rule_ids & ds_rules
        if not fired and latest:
            return True, None
        return False, f"{len(fired)} design-system issue(s) remaining" if fired else None

    if badge_id == "consistency_high":
        return consistency_level == "high", None

    if badge_id == "dashboard_expert":
        db_rules = {"DB1_too_many_cards", "DB2_poor_hierarchy",
                    "DB3_crowded_layout", "DB4_weak_kpi"}
        fired = rule_ids & db_rules
        if not fired and latest:
            return True, None
        return False, f"{len(fired)} dashboard issue(s) remaining" if fired else None

    if badge_id == "five_analyses":
        return total_analyses >= 5, f"{total_analyses}/5 analyses"

    if badge_id == "ten_analyses":
        return total_analyses >= 10, f"{total_analyses}/10 analyses"

    if badge_id == "no_critical":
        if latest and "critical" not in severities:
            return True, None
        return False, None

    if badge_id == "all_categories_pass":
        if not category_scores:
            return False, None
        below = [c for c in category_scores if c.get("score", 0) < 70]
        if not below:
            return True, None
        return False, f"{len(below)} categories below 70"

    if badge_id == "improving_streak":
        if len(all_scores) >= 3:
            for i in range(2, len(all_scores)):
                if all_scores[i] > all_scores[i - 1] > all_scores[i - 2]:
                    return True, None
        return False, None

    return False, None
