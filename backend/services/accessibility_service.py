"""
Module 13 — Accessibility Review.

Produces a WCAG conformance summary from an AnalysisResult.  Aggregates
accessibility issues from all rule modules and adds heuristic keyboard-
navigation and ARIA checks based on the ParsedPage data.

No API calls, no DB, no CV.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from backend.models.analysis import AnalysisResult
from backend.models.issue import Category, Issue, Severity


_WCAG_CRITERION: dict[str, str] = {
    "C1_wcag_aa_contrast":           "1.4.3 Contrast (Minimum)",
    "C1_wcag_aa_contrast_a11y":      "1.4.3 Contrast (Minimum)",
    "B3_focus_style":                 "2.4.7 Focus Visible",
    "B4_touch_target":                "2.5.8 Target Size (Minimum)",
    "TBL1_missing_header":            "1.3.1 Info and Relationships",
    "F1_missing_label":               "1.3.1 Info and Relationships / 3.3.2 Labels or Instructions",
    "F2_placeholder_as_label":        "3.3.2 Labels or Instructions",
    "CH2_similar_chart_colors":       "1.4.1 Use of Color",
    "T1_body_font_size":              "1.4.4 Resize Text",
    "T3_line_height":                 "1.4.8 Visual Presentation",
}

_CONFORMANCE_LEVELS = {
    Severity.CRITICAL: "A",
    Severity.HIGH: "AA",
    Severity.MEDIUM: "AA",
    Severity.LOW: "AAA",
    Severity.SUGGESTION: "AAA",
}


@dataclass
class WcagIssue:
    rule_id: str
    criterion: str
    level: str           # "A", "AA", or "AAA"
    severity: str
    message: str
    recommendation: str
    why: str
    references: list[str] = field(default_factory=list)


@dataclass
class AccessibilityReport:
    wcag_aa_pass: bool
    wcag_a_pass: bool
    score: float          # 0–100; 100 = zero accessibility issues
    issues: list[WcagIssue]
    keyboard_hints: list[str]
    aria_hints: list[str]
    summary: str


def build_report(result: AnalysisResult, parsed_page: dict) -> AccessibilityReport:
    """Summarise accessibility conformance from an AnalysisResult + ParsedPage."""
    a11y_issues = _extract_a11y_issues(result)
    keyboard_hints = _keyboard_hints(parsed_page)
    aria_hints = _aria_hints(parsed_page)

    wcag_issues = [_to_wcag_issue(i) for i in a11y_issues]

    level_a_fails = [w for w in wcag_issues if w.level == "A"]
    level_aa_fails = [w for w in wcag_issues if w.level in ("A", "AA")]

    deduction = sum(
        25 if i.severity == Severity.CRITICAL else
        15 if i.severity == Severity.HIGH else
        8 if i.severity == Severity.MEDIUM else 3
        for i in a11y_issues
    )
    score = round(max(0.0, 100.0 - deduction), 1)

    return AccessibilityReport(
        wcag_aa_pass=len(level_aa_fails) == 0,
        wcag_a_pass=len(level_a_fails) == 0,
        score=score,
        issues=wcag_issues,
        keyboard_hints=keyboard_hints,
        aria_hints=aria_hints,
        summary=_build_summary(score, level_a_fails, level_aa_fails,
                               keyboard_hints, aria_hints),
    )


def report_to_dict(report: AccessibilityReport) -> dict:
    return {
        "wcag_aa_pass": report.wcag_aa_pass,
        "wcag_a_pass": report.wcag_a_pass,
        "score": report.score,
        "issue_count": len(report.issues),
        "issues": [
            {
                "rule_id": w.rule_id,
                "criterion": w.criterion,
                "level": w.level,
                "severity": w.severity,
                "message": w.message,
                "recommendation": w.recommendation,
                "why": w.why,
                "references": w.references,
            }
            for w in report.issues
        ],
        "keyboard_hints": report.keyboard_hints,
        "aria_hints": report.aria_hints,
        "summary": report.summary,
    }


# ── internal helpers ──────────────────────────────────────────────────────────

def _extract_a11y_issues(result: AnalysisResult) -> list[Issue]:
    return [
        i for i in result.issues
        if i.category == Category.ACCESSIBILITY
        or i.rule_id in _WCAG_CRITERION
    ]


def _to_wcag_issue(issue: Issue) -> WcagIssue:
    criterion = _WCAG_CRITERION.get(issue.rule_id, "General Accessibility")
    level = _CONFORMANCE_LEVELS.get(issue.severity, "AA")
    return WcagIssue(
        rule_id=issue.rule_id,
        criterion=criterion,
        level=level,
        severity=issue.severity.value,
        message=issue.message,
        recommendation=issue.recommendation,
        why=issue.why,
        references=issue.references,
    )


def _keyboard_hints(parsed_page: dict) -> list[str]:
    hints: list[str] = []
    buttons = parsed_page.get("buttons", [])
    no_focus = [b for b in buttons if not b.get("has_focus_style", True)]
    if no_focus:
        hints.append(
            f"{len(no_focus)} button(s) lack a visible :focus-visible style. "
            "Keyboard users cannot tell which element has focus."
        )
    inputs = parsed_page.get("inputs", [])
    no_label = [i for i in inputs if not i.get("has_label", True)]
    if no_label:
        hints.append(
            f"{len(no_label)} input(s) have no label. Tab order reaches them but "
            "screen readers cannot announce the field purpose."
        )
    tables = parsed_page.get("tables", [])
    no_header = [t for t in tables if not t.get("has_header", True)]
    if no_header:
        hints.append(
            f"{len(no_header)} table(s) have no <th> headers. Screen readers will "
            "read each cell without column context."
        )
    return hints


def _aria_hints(parsed_page: dict) -> list[str]:
    hints: list[str] = []
    charts = parsed_page.get("charts", [])
    if charts:
        hints.append(
            f"{len(charts)} chart(s) detected. Add role='img' and aria-label "
            "describing the chart's key finding for screen readers."
        )
    tables = parsed_page.get("tables", [])
    for t in tables:
        if not t.get("has_header", True):
            hints.append(
                "Table without headers: add scope='col' to each <th> so screen readers "
                "announce the column name before each cell."
            )
            break
    inputs = parsed_page.get("inputs", [])
    ph_only = [i for i in inputs
               if not i.get("has_label") and i.get("placeholder") and not i.get("label_text")]
    if ph_only:
        hints.append(
            f"{len(ph_only)} input(s) use placeholder as the only label. "
            "Add aria-label or a persistent <label> element."
        )
    return hints


def _build_summary(
    score: float,
    level_a_fails: list,
    level_aa_fails: list,
    keyboard_hints: list[str],
    aria_hints: list[str],
) -> str:
    parts: list[str] = []
    if not level_a_fails and not level_aa_fails:
        parts.append(f"✓ No WCAG A/AA failures detected (accessibility score: {score}/100).")
    else:
        if level_a_fails:
            parts.append(
                f"✗ {len(level_a_fails)} WCAG Level A failure(s) — "
                "these prevent basic accessibility and must be fixed immediately."
            )
        aa_only = [f for f in level_aa_fails if f not in level_a_fails]
        if aa_only:
            parts.append(
                f"⚠ {len(aa_only)} WCAG Level AA failure(s) — "
                "required for legal compliance in most jurisdictions."
            )
        parts.append(f"Accessibility score: {score}/100.")
    if keyboard_hints:
        parts.append(f"{len(keyboard_hints)} keyboard navigation issue(s) found.")
    if aria_hints:
        parts.append(f"{len(aria_hints)} ARIA improvement(s) recommended.")
    return " ".join(parts)
