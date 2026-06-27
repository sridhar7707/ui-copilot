"""
Analysis repository — stores and retrieves analysis runs for a page.
"""
from __future__ import annotations

import json
import pathlib
from typing import Optional

from backend.db.schema import _DEFAULT_PATH, get_db
from backend.models.analysis import AnalysisResult


async def save(
    page_id: int,
    result: AnalysisResult,
    source: str = "html",
    parsed_page: Optional[dict] = None,
    db_path: pathlib.Path | None = None,
) -> dict:
    """Persist an AnalysisResult and return the stored row.

    Pass ``parsed_page`` to include a component snapshot in the stored JSON
    (required by Module 20 — Component Library).
    """
    result_json = _serialise(result, parsed_page)
    async with get_db(db_path or _DEFAULT_PATH) as db:
        cur = await db.execute(
            "INSERT INTO analyses (page_id, overall_score, result_json, source) "
            "VALUES (?, ?, ?, ?)",
            (page_id, result.overall_score, result_json, source),
        )
        await db.commit()
        row = await (await db.execute(
            "SELECT id, page_id, overall_score, source, created_at "
            "FROM analyses WHERE id = ?",
            (cur.lastrowid,),
        )).fetchone()
        return dict(row)


async def get(analysis_id: int, db_path: pathlib.Path | None = None) -> Optional[dict]:
    async with get_db(db_path or _DEFAULT_PATH) as db:
        row = await (await db.execute(
            "SELECT id, page_id, overall_score, result_json, source, created_at "
            "FROM analyses WHERE id = ?",
            (analysis_id,),
        )).fetchone()
        return dict(row) if row else None


async def list_for_page(page_id: int, db_path: pathlib.Path | None = None) -> list[dict]:
    """Return all analysis runs for a page, newest first (history view)."""
    async with get_db(db_path or _DEFAULT_PATH) as db:
        rows = await (await db.execute(
            "SELECT id, page_id, overall_score, source, created_at "
            "FROM analyses WHERE page_id = ? ORDER BY created_at DESC",
            (page_id,),
        )).fetchall()
        return [dict(r) for r in rows]


async def latest_for_page(page_id: int, db_path: pathlib.Path | None = None) -> Optional[dict]:
    """Return the most recent analysis for a page, including result_json."""
    async with get_db(db_path or _DEFAULT_PATH) as db:
        row = await (await db.execute(
            "SELECT id, page_id, overall_score, result_json, source, created_at "
            "FROM analyses WHERE page_id = ? ORDER BY created_at DESC LIMIT 1",
            (page_id,),
        )).fetchone()
        return dict(row) if row else None


# ── serialisation ─────────────────────────────────────────────────────────────

def _serialise(result: AnalysisResult, parsed_page: Optional[dict] = None) -> str:
    data: dict = {
        "overall_score": result.overall_score,
        "issues": [
            {
                "rule_id": i.rule_id,
                "category": i.category.value,
                "severity": i.severity.value,
                "message": i.message,
                "estimated_gain": i.estimated_gain,
            }
            for i in result.issues
        ],
    }
    if parsed_page is not None:
        data["components"] = _component_snapshot(parsed_page)
    return json.dumps(data)


def _component_snapshot(parsed_page: dict) -> dict:
    """Compact component data from a parsed page, capped to avoid bloat."""
    _btn_keys = {
        "background_color", "text_color", "border_radius_px",
        "padding_top_px", "padding_bottom_px", "font_size_px", "height_px",
    }
    _card_keys = {"padding_px", "border_radius_px", "background_color", "width_px"}
    _input_keys = {"border_radius_px", "padding_px", "background_color"}

    return {
        "buttons": [
            {k: v for k, v in b.items() if k in _btn_keys}
            for b in parsed_page.get("buttons", [])[:20]
        ],
        "cards": [
            {k: v for k, v in c.items() if k in _card_keys}
            for c in parsed_page.get("cards", [])[:20]
        ],
        "inputs": [
            {k: v for k, v in inp.items() if k in _input_keys}
            for inp in parsed_page.get("inputs", [])[:20]
        ],
        "tables": [
            {
                "column_count": t.get("column_count"),
                "row_count": t.get("row_count"),
                "has_header": t.get("has_header"),
            }
            for t in parsed_page.get("tables", [])[:10]
        ],
        "fonts": parsed_page.get("fonts", [])[:10],
        "text_color_pairs": parsed_page.get("text_color_pairs", [])[:20],
        "spacing_values_px": parsed_page.get("spacing_values_px", [])[:30],
        "body_font_size_px": parsed_page.get("body_font_size_px"),
    }
