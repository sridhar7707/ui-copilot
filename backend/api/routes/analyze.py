from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.analyzers.html_analyzer import parse
from backend.models.issue import Issue
from backend.services import (
    accessibility_service,
    css_generator,
    prompt_generator,
    scoring_engine,
)

router = APIRouter(tags=["analysis"])


def _full(i: Issue) -> dict:
    return {
        "rule_id": i.rule_id,
        "category": i.category.value,
        "severity": i.severity.value,
        "confidence": i.confidence,
        "message": i.message,
        "recommendation": i.recommendation,
        "evidence": i.evidence,
        "estimated_time": i.estimated_time,
        "estimated_gain": i.estimated_gain,
        "why": i.why,
        "references": i.references,
    }


def _summary(i: Issue) -> dict:
    return {
        "rule_id": i.rule_id,
        "severity": i.severity.value,
        "message": i.message,
        "estimated_gain": i.estimated_gain,
        "estimated_time": i.estimated_time,
    }


@router.post("/analyze")
async def analyze_page(
    html_file: UploadFile = File(..., description="HTML file to analyze"),
    css_file: Optional[UploadFile] = File(None, description="External CSS file (optional)"),
) -> dict:
    """
    Parse the uploaded HTML (and optional CSS) and return a full UI quality report.
    Inline <style> blocks are always parsed; use css_file for linked stylesheets.
    """
    try:
        html = (await html_file.read()).decode("utf-8", errors="replace")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read HTML file: {exc}")

    css = ""
    if css_file:
        try:
            css = (await css_file.read()).decode("utf-8", errors="replace")
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Could not read CSS file: {exc}")

    parsed = parse(html, css)
    result = scoring_engine.analyze(parsed)
    a11y_report = accessibility_service.build_report(result, parsed)

    return {
        "overall_score": result.overall_score,
        "category_scores": [
            {
                "category": cs.category.value,
                "score": round(cs.score, 1),
                "weight": cs.weight,
                "issue_count": len(cs.issues),
            }
            for cs in result.category_scores
        ],
        "issues": [_full(i) for i in result.issues],
        "issue_count": len(result.issues),
        "roadmap": {
            "top_issues": [_summary(i) for i in result.top_issues],
            "quick_wins": [_summary(i) for i in result.quick_wins],
            "high_impact": [_summary(i) for i in result.high_impact],
            "easy_fixes": [_summary(i) for i in result.easy_fixes],
            "accessibility_fixes": [_summary(i) for i in result.accessibility_fixes],
            "visual_improvements": [_summary(i) for i in result.visual_improvements],
            "consistency_improvements": [_summary(i) for i in result.consistency_improvements],
        },
        "accessibility": accessibility_service.report_to_dict(a11y_report),
        "claude_prompt": prompt_generator.generate(result),
        "css_snippet": css_generator.generate(result),
    }
