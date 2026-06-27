"""
Project repository — CRUD for the `projects` table.
"""
from __future__ import annotations

import pathlib
from typing import Optional

from backend.db.schema import get_db


async def create(name: str, description: str = "",
                 db_path: pathlib.Path | None = None) -> dict:
    async with get_db(db_path or _default()) as db:
        cur = await db.execute(
            "INSERT INTO projects (name, description) VALUES (?, ?)",
            (name, description),
        )
        await db.commit()
        row = await (await db.execute(
            "SELECT id, name, description, created_at FROM projects WHERE id = ?",
            (cur.lastrowid,),
        )).fetchone()
        return dict(row)


async def get(project_id: int, db_path: pathlib.Path | None = None) -> Optional[dict]:
    async with get_db(db_path or _default()) as db:
        row = await (await db.execute(
            "SELECT id, name, description, created_at FROM projects WHERE id = ?",
            (project_id,),
        )).fetchone()
        return dict(row) if row else None


async def list_all(db_path: pathlib.Path | None = None) -> list[dict]:
    async with get_db(db_path or _default()) as db:
        rows = await (await db.execute(
            "SELECT id, name, description, created_at FROM projects ORDER BY created_at DESC",
        )).fetchall()
        return [dict(r) for r in rows]


async def delete(project_id: int, db_path: pathlib.Path | None = None) -> bool:
    async with get_db(db_path or _default()) as db:
        cur = await db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        await db.commit()
        return cur.rowcount > 0


def _default() -> pathlib.Path:
    from backend.db.schema import _DEFAULT_PATH
    return _DEFAULT_PATH
