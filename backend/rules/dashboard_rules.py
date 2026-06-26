from __future__ import annotations

from backend.models.issue import Category, Issue, Severity


def analyze(parsed_page: dict, thresholds: dict) -> list[Issue]:
    issues: list[Issue] = []
    t = thresholds["dashboard"]

    # D1 — too many KPI cards
    kpi_count = parsed_page.get("kpi_card_count", 0)
    if kpi_count > t["max_kpi_cards"]:
        issues.append(Issue(
            rule_id="D1_kpi_card_overload",
            category=Category.VISUAL_HIERARCHY,
            severity=Severity.MEDIUM,
            confidence=0.8,
            message=(
                f"{kpi_count} KPI cards on screen at once — "
                f"more than {t['max_kpi_cards']} dilutes focus and overwhelms the user."
            ),
            recommendation=(
                "Limit the primary view to the 6–8 most important metrics. "
                "Move secondary metrics to a collapsed section or a detail page."
            ),
            evidence=f"kpi_card_count: {kpi_count}",
            estimated_time="2 hours",
            why=(
                "More than 8 KPI cards overwhelm working memory (Miller's Law: 7±2 items). "
                "When everything is highlighted, nothing is — users end up ignoring all the "
                "metrics rather than acting on the most important ones. Leading analytics "
                "products show 4–6 primary metrics with secondary stats hidden by default."
            ),
            references=["Stripe", "Linear", "Google Analytics"],
        ))

    # D2 — insufficient whitespace
    whitespace = parsed_page.get("whitespace_ratio", 1.0)
    if whitespace < t["min_whitespace_ratio"]:
        issues.append(Issue(
            rule_id="D2_low_whitespace",
            category=Category.SPACING,
            severity=Severity.HIGH,
            confidence=0.75,
            message=(
                f"Estimated whitespace ratio ({whitespace:.0%}) is below the "
                f"recommended minimum ({t['min_whitespace_ratio']:.0%}). "
                "The layout feels dense and cluttered."
            ),
            recommendation=(
                "Increase section gaps, card margins, and padding. "
                "A well-designed dashboard dedicates 20–30% of its area to whitespace."
            ),
            evidence=f"whitespace_ratio: {whitespace:.2f}",
            estimated_time="1 hour",
            why=(
                "Dense dashboards induce decision fatigue within seconds of viewing. "
                "White space is not wasted space — it directs the eye to what matters, "
                "separates concepts, and signals quality. Sparse, high-signal dashboards "
                "are consistently rated as more trustworthy and easier to act on."
            ),
            references=["Notion", "Linear", "Apple Human Interface Guidelines"],
        ))

    return issues
