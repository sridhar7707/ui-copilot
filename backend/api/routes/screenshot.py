from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.analyzers import screenshot_analyzer
from backend.models.issue import Issue
from backend.services import (
    accessibility_service,
    css_generator,
    html_improvements,
    prompt_generator,
    scoring_engine,
)

router = APIRouter()


def _full(i: Issue) -> dict:
    return {
        "rule_id": i.rule_id,
        "category": i.category.value,
        "severity": i.severity.value,
        "confidence": i.confidence,
        "message": i.message,
        "recommendation": i.recommendation,
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


@router.post("/analyze/screenshot")
async def analyze_screenshot(screenshot: UploadFile = File(...)):
    """
    POST /api/v1/analyze/screenshot

    Upload a screenshot (PNG, JPEG, WebP, …) and receive a scored analysis.
    Analysis is entirely local — no vision-model API calls are made.

    Returns the same JSON shape as POST /api/v1/analyze.
    Fields that require HTML/CSS (fonts, headings, inputs) will be absent
    from issues since no text is read from the image.
    """
    content_type = screenshot.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image (image/*).")

    image_bytes = await screenshot.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        parsed = screenshot_analyzer.analyze(image_bytes)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not process image: {exc}") from exc

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
        "html_improvements": html_improvements.generate(result),
        "analyzed_by": "screenshot",
    }
