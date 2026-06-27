from __future__ import annotations

from backend.analyzers import dashboard_analyzer, design_system_analyzer
from backend.models.analysis import AnalysisResult, CategoryScore, ParsedPage
from backend.models.issue import Category, Issue
from backend.rules import (
    button_rules,
    chart_rules,
    contrast_rules,
    dashboard_rules,
    form_rules,
    spacing_rules,
    table_rules,
    typography_rules,
)
from backend.utils.config_loader import load_scoring_config

_RULE_MODULES = [
    spacing_rules,
    typography_rules,
    contrast_rules,
    button_rules,
    table_rules,
    form_rules,
    chart_rules,
    dashboard_rules,
    design_system_analyzer,
    dashboard_analyzer,
]


def analyze(parsed_page: ParsedPage) -> AnalysisResult:
    config = load_scoring_config()
    weights: dict[str, float] = config["weights"]
    deductions: dict[str, float] = config["severity_deductions"]
    thresholds: dict = config["thresholds"]

    all_issues: list[Issue] = []
    for module in _RULE_MODULES:
        all_issues.extend(module.analyze(parsed_page, thresholds))

    category_scores: list[CategoryScore] = []
    for cat in Category:
        cat_issues = [i for i in all_issues if i.category == cat]
        total_deduction = sum(deductions.get(i.severity.value, 0) for i in cat_issues)
        score = max(0.0, 100.0 - total_deduction)
        weight = weights.get(cat.value, 0.0)

        for issue in cat_issues:
            issue.estimated_gain = round(deductions.get(issue.severity.value, 0) * weight, 1)

        category_scores.append(CategoryScore(
            category=cat,
            score=score,
            weight=weight,
            issues=cat_issues,
        ))

    overall = round(sum(cs.weighted_score for cs in category_scores), 1)
    sorted_issues = sorted(all_issues, key=lambda i: i.estimated_gain, reverse=True)

    return AnalysisResult(
        overall_score=overall,
        category_scores=category_scores,
        issues=sorted_issues,
    )
