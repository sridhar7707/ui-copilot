"""
Module 14 — Dashboard Analyzer.

Special-cased rules for dashboard-style pages: too many cards, poor hierarchy,
crowded layouts, weak KPI presentation, oversized tables, and missing sections.

Only fires when a page looks like a dashboard (kpi_card_count > 0 or
card + chart count suggests a dashboard layout).
"""
from __future__ import annotations

from backend.models.issue import Category, Issue, Severity


def analyze(parsed_page: dict, thresholds: dict) -> list[Issue]:
    t = thresholds["dashboard"]
    issues: list[Issue] = []

    cards = parsed_page.get("cards", [])
    charts = parsed_page.get("charts", [])
    tables = parsed_page.get("tables", [])
    headings = parsed_page.get("headings", [])
    kpi_count = parsed_page.get("kpi_card_count", 0)

    total_widgets = len(cards) + len(charts) + len(tables)
    looks_like_dashboard = kpi_count > 0 or total_widgets >= 3

    if not looks_like_dashboard:
        return []

    _check_too_many_cards(cards, kpi_count, t, issues)
    _check_crowded_layout(total_widgets, t, issues)
    _check_poor_hierarchy(headings, t, issues)
    _check_weak_kpi(headings, kpi_count, t, issues)
    _check_dense_tables(tables, t, issues)
    _check_no_section_headings(headings, total_widgets, issues)

    return issues


# ── rule implementations ──────────────────────────────────────────────────────

def _check_too_many_cards(cards: list, kpi_count: int,
                           t: dict, issues: list[Issue]) -> None:
    card_count = max(len(cards), kpi_count)
    if card_count > t["max_kpi_cards"]:
        issues.append(Issue(
            rule_id="DB1_too_many_cards",
            category=Category.VISUAL_HIERARCHY,
            severity=Severity.MEDIUM,
            confidence=0.85,
            message=(
                f"{card_count} cards detected — more than {t['max_kpi_cards']} "
                "dilutes focus and overwhelms users."
            ),
            recommendation=(
                f"Limit the primary dashboard to {t['max_kpi_cards']} cards maximum. "
                "Move lower-priority cards behind a 'View More' toggle or a secondary tab."
            ),
            evidence=f"card_count={card_count}, threshold={t['max_kpi_cards']}",
            estimated_time="2 hours",
            why=(
                "Miller's Law limits working memory to ~7±2 items. Dashboards with "
                "more than 8 visible cards cause users to scan without absorbing — "
                "the most important metrics get lost in the noise. Stripe, Linear, "
                "and Notion all default to ≤6 primary metrics above the fold."
            ),
            references=["Stripe Dashboard", "Linear", "Nielsen Norman Group"],
        ))


def _check_crowded_layout(total_widgets: int, t: dict,
                           issues: list[Issue]) -> None:
    if total_widgets > t["max_total_widgets"]:
        issues.append(Issue(
            rule_id="DB3_crowded_layout",
            category=Category.SPACING,
            severity=Severity.HIGH,
            confidence=0.80,
            message=(
                f"{total_widgets} widgets (cards + charts + tables) detected — "
                f"more than {t['max_total_widgets']} creates a crowded, hard-to-scan layout."
            ),
            recommendation=(
                "Split the dashboard into focused sub-views or tabs. "
                "Each view should answer one question — not every question at once."
            ),
            evidence=f"total_widgets={total_widgets}, threshold={t['max_total_widgets']}",
            estimated_time="4 hours",
            why=(
                "Crowded dashboards increase time-to-insight: users must work harder "
                "to find the signal in the noise. Every additional widget reduces the "
                "cognitive budget available for the most important ones. "
                "High-performing analytics dashboards (Looker, Metabase) enforce a "
                "'one story per screen' heuristic."
            ),
            references=["Looker", "Metabase", "Gestalt Principles"],
        ))


def _check_poor_hierarchy(headings: list, t: dict,
                           issues: list[Issue]) -> None:
    if not headings:
        issues.append(Issue(
            rule_id="DB2_poor_hierarchy",
            category=Category.VISUAL_HIERARCHY,
            severity=Severity.HIGH,
            confidence=0.90,
            message="No headings detected — the dashboard has no visual hierarchy to guide the eye.",
            recommendation=(
                "Add an h1 as the page title, h2 for each major section "
                "(Overview, Performance, Recent Activity), and h3 for sub-sections."
            ),
            evidence="heading_count=0",
            estimated_time="30 minutes",
            why=(
                "Without headings, every element competes equally for attention. "
                "Screen readers also rely on headings for navigation. "
                "A clear heading hierarchy is the single fastest win for scannability."
            ),
            references=["WCAG 2.4.6", "Nielsen Norman Group", "GOV.UK Design System"],
        ))
        return

    h1s = [h for h in headings if h["level"] == 1]
    h2s = [h for h in headings if h["level"] == 2]

    if h1s and h2s:
        h1_size = max(h["font_size_px"] for h in h1s)
        h2_size = max(h["font_size_px"] for h in h2s)
        ratio = h1_size / h2_size if h2_size > 0 else 0
        if ratio < t.get("min_h1_h2_ratio", 1.3):
            issues.append(Issue(
                rule_id="DB2_poor_hierarchy",
                category=Category.VISUAL_HIERARCHY,
                severity=Severity.MEDIUM,
                confidence=0.75,
                message=(
                    f"H1 ({h1_size:.0f}px) is only {ratio:.1f}× the size of H2 ({h2_size:.0f}px) "
                    f"— the hierarchy is too flat to guide the eye."
                ),
                recommendation=(
                    f"Make H1 at least {t.get('min_h1_h2_ratio', 1.3):.1f}× larger than H2. "
                    "A strong visual hierarchy is the backbone of any effective dashboard."
                ),
                evidence=f"h1={h1_size:.0f}px, h2={h2_size:.0f}px, ratio={ratio:.2f}",
                estimated_time="20 minutes",
                why=(
                    "Insufficient size contrast between heading levels collapses the "
                    "visual hierarchy — users can't distinguish what's a section title "
                    "from what's a data label. Effective dashboards use a minimum 1.3× "
                    "step between heading levels to create clear scanning landmarks."
                ),
                references=["Material Design Type System", "Apple HIG"],
            ))


def _check_weak_kpi(headings: list, kpi_count: int,
                    t: dict, issues: list[Issue]) -> None:
    if kpi_count == 0:
        return
    min_kpi_px = t.get("min_kpi_heading_size_px", 24)
    large_headings = [h for h in headings if h["font_size_px"] >= min_kpi_px]
    if not large_headings:
        issues.append(Issue(
            rule_id="DB4_weak_kpi",
            category=Category.VISUAL_HIERARCHY,
            severity=Severity.HIGH,
            confidence=0.80,
            message=(
                f"{kpi_count} KPI card(s) detected but no heading is ≥{min_kpi_px}px "
                "— KPI numbers lack the visual weight to register at a glance."
            ),
            recommendation=(
                f"KPI numbers should be at least {min_kpi_px}px (preferably 28–40px) "
                "with semibold or bold weight. The number is the hero — make it obvious."
            ),
            evidence=f"kpi_count={kpi_count}, max_heading_px={max((h['font_size_px'] for h in headings), default=0):.0f}",
            estimated_time="30 minutes",
            why=(
                "KPI cards exist to let executives and operators glean the headline "
                "number in under a second. If the number is the same size as body text, "
                "it fails its core purpose. Products like Stripe, Baremetrics, and "
                "ChartMogul all use 28px+ numbers for primary KPIs."
            ),
            references=["Stripe Dashboard", "Baremetrics", "ChartMogul"],
        ))


def _check_dense_tables(tables: list, t: dict, issues: list[Issue]) -> None:
    max_cols = t.get("max_table_columns", 8)
    wide_tables = [tbl for tbl in tables if tbl.get("column_count", 0) > max_cols]
    if wide_tables:
        issues.append(Issue(
            rule_id="DB5_dense_tables",
            category=Category.COMPONENT_QUALITY,
            severity=Severity.MEDIUM,
            confidence=0.85,
            message=(
                f"{len(wide_tables)} table(s) have more than {max_cols} columns — "
                "wide tables are hard to scan and break on smaller screens."
            ),
            recommendation=(
                f"Limit tables to {max_cols} columns maximum. "
                "Move secondary columns into an expandable row detail or export. "
                "Consider showing only the 5–6 most actionable columns by default."
            ),
            evidence=f"wide_tables={len(wide_tables)}, max_cols={max_cols}",
            estimated_time="1 hour",
            why=(
                "Wide tables force users to scroll horizontally — a pattern that "
                "consistently scores poorly in usability testing. Tables with 5–6 "
                "focused columns are faster to scan and more actionable than 12-column "
                "spreadsheet dumps. GitHub, Linear, and Jira all default to ≤7 visible columns."
            ),
            references=["GitHub Issues", "Linear", "Jira"],
        ))


def _check_no_section_headings(headings: list, total_widgets: int,
                                issues: list[Issue]) -> None:
    h2_count = sum(1 for h in headings if h["level"] == 2)
    if total_widgets >= 4 and h2_count == 0:
        issues.append(Issue(
            rule_id="DB6_no_section_headings",
            category=Category.VISUAL_HIERARCHY,
            severity=Severity.MEDIUM,
            confidence=0.75,
            message=(
                f"{total_widgets} widgets with no H2 section headings — "
                "content areas are visually undifferentiated."
            ),
            recommendation=(
                "Add H2 headings to separate logical sections: "
                "'Overview', 'Performance', 'Recent Activity', 'Alerts'. "
                "Section headings let users jump directly to what they need."
            ),
            evidence=f"total_widgets={total_widgets}, h2_count=0",
            estimated_time="15 minutes",
            why=(
                "Without section headings, a dashboard is just a grid of widgets "
                "with no mental model for the user to hang them on. Section headings "
                "reduce orientation time and help users decide which parts to engage with "
                "and which to skip — critical for dashboards visited multiple times per day."
            ),
            references=["Nielsen Norman Group", "GOV.UK Design System"],
        ))
