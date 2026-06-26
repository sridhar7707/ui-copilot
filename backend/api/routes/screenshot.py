from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.analyzers import screenshot_analyzer
from backend.services import scoring_engine

router = APIRouter()


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

    return {
        "overall_score": result.overall_score,
        "category_scores": [
            {
                "category": cs.category.value,
                "score": cs.score,
                "weight": cs.weight,
                "issue_count": len(cs.issues),
            }
            for cs in result.category_scores
        ],
        "issues": [
            {
                "rule_id": i.rule_id,
                "category": i.category.value,
                "severity": i.severity.value,
                "confidence": i.confidence,
                "message": i.message,
                "recommendation": i.recommendation,
                "estimated_time": i.estimated_time,
                "estimated_gain": i.estimated_gain,
            }
            for i in result.issues
        ],
        "issue_count": len(result.issues),
        "quick_wins": [
            {
                "rule_id": i.rule_id,
                "message": i.message,
                "estimated_gain": i.estimated_gain,
                "estimated_time": i.estimated_time,
            }
            for i in result.quick_wins
        ],
        "analyzed_by": "screenshot",
    }
