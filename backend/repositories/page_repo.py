"""
Page repository — CRUD for the `pages` table.
"""
from __future__ import annotations

import pathlib
from typing import Optional

from backend.db.schema import _DEFAULT_PATH, get_db


async def create(project_id: int, url: str = "", title: str = "",
                 db_path: pathlib.Path | None = None) -> dict:
    async with get_db(db_path or _DEFAULT_PATH) as db:
        cur = await db.execute(
            "INSERT INTO pages (project_id, url, title) VALUES (?, ?, ?)",
            (project_id, url, title),
        )
        await db.commit()
        row = await (await db.execute(
            "SELECT id, project_id, url, title, created_at FROM pages WHERE id = ?",
            (cur.lastrowid,),
        )).fetchone()
        return dict(row)


async def get(page_id: int, db_path: pathlib.Path | None = None) -> Optional[dict]:
    async with get_db(db_path or _DEFAULT_PATH) as db:
        row = await (await db.execute(
            "SELECT id, project_id, url, title, created_at FROM pages WHERE id = ?",
            (page_id,),
        )).fetchone()
        return dict(row) if row else None


async def list_for_project(project_id: int, db_path: pathlib.Path | None = None) -> list[dict]:
    async with get_db(db_path or _DEFAULT_PATH) as db:
        rows = await (await db.execute(
            "SELECT id, project_id, url, title, created_at FROM pages "
            "WHERE project_id = ? ORDER BY created_at DESC",
            (project_id,),
        )).fetchall()
        return [dict(r) for r in rows]


async def delete(page_id: int, db_path: pathlib.Path | None = None) -> bool:
    async with get_db(db_path or _DEFAULT_PATH) as db:
        cur = await db.execute("DELETE FROM pages WHERE id = ?", (page_id,))
        await db.commit()
        return cur.rowcount > 0
