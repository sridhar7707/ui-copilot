"""
Analysis repository — stores and retrieves analysis runs for a page.
"""
from __future__ import annotations

import json
import pathlib
from typing import Optional

from backend.db.schema import _DEFAULT_PATH, get_db
from backend.models.analysis import AnalysisResult


async def save(page_id: int, result: AnalysisResult, source: str = "html",
               db_path: pathlib.Path | None = None) -> dict:
    """Persist an AnalysisResult and return the stored row."""
    result_json = _serialise(result)
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
    """Return the most recent analysis for a page."""
    async with get_db(db_path or _DEFAULT_PATH) as db:
        row = await (await db.execute(
            "SELECT id, page_id, overall_score, source, created_at "
            "FROM analyses WHERE page_id = ? ORDER BY created_at DESC LIMIT 1",
            (page_id,),
        )).fetchone()
        return dict(row) if row else None


def _serialise(result: AnalysisResult) -> str:
    return json.dumps({
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
    })
