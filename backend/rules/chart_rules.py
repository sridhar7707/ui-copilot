from __future__ import annotations

from itertools import combinations

from backend.models.issue import Category, Issue, Severity
from backend.utils.color_utils import colour_distance


def analyze(parsed_page: dict, thresholds: dict) -> list[Issue]:
    issues: list[Issue] = []
    t = thresholds["charts"]
    charts = parsed_page.get("charts", [])

    for i, chart in enumerate(charts):
        label = f"Chart #{i + 1}"

        # CH1 — no axis labels
        if not chart.get("has_axis_labels", True):
            issues.append(Issue(
                rule_id="CH1_missing_axis_labels",
                category=Category.COMPONENT_QUALITY,
                severity=Severity.MEDIUM,
                confidence=0.8,
                message=f"{label} has no axis labels — users can't tell what the data represents.",
                recommendation="Add descriptive axis labels with units (e.g. 'Revenue ($)' on Y, 'Month' on X).",
                evidence="No axis labels detected.",
                estimated_time="10 minutes",
            ))

        # CH2 — chart colours too similar (hard to distinguish series)
        colors = chart.get("colors", [])
        if len(colors) >= 2:
            too_close = [
                (a, b)
                for a, b in combinations(colors, 2)
                if colour_distance(a, b) < t["min_color_distance"]
            ]
            if too_close:
                issues.append(Issue(
                    rule_id="CH2_similar_chart_colors",
                    category=Category.ACCESSIBILITY,
                    severity=Severity.MEDIUM,
                    confidence=0.85,
                    message=(
                        f"{label} has {len(too_close)} colour pair(s) that are too similar "
                        "to distinguish — problematic for colour-blind users."
                    ),
                    recommendation=(
                        "Use a perceptually distinct colour palette for chart series. "
                        "Test with a colour-blindness simulator."
                    ),
                    evidence=f"Similar pairs: {too_close[:3]}",
                    estimated_time="15 minutes",
                ))

    return issues
