"""
SQLite schema definition and database lifecycle management.

Schema:
  projects   — one row per user project (name, description, created_at)
  pages      — one page per project (url, title, project_id, created_at)
  analyses   — one analysis run per page per submission
               stores the full JSON result so historic scores are preserved
"""
from __future__ import annotations

import os
import pathlib
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aiosqlite

_DEFAULT_PATH = pathlib.Path(os.environ.get("DB_PATH", "data/uicopilot.db"))

DDL = """
CREATE TABLE IF NOT EXISTS projects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    description TEXT    NOT NULL DEFAULT '',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS pages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    url         TEXT    NOT NULL DEFAULT '',
    title       TEXT    NOT NULL DEFAULT '',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS analyses (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id      INTEGER NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
    overall_score REAL   NOT NULL,
    result_json  TEXT   NOT NULL,
    source       TEXT   NOT NULL DEFAULT 'html',
    created_at   TEXT   NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_pages_project ON pages(project_id);
CREATE INDEX IF NOT EXISTS idx_analyses_page ON analyses(page_id);
"""


@asynccontextmanager
async def get_db(
    path: pathlib.Path = _DEFAULT_PATH,
) -> AsyncGenerator[aiosqlite.Connection, None]:
    """Open a configured aiosqlite connection, yield it, and close on exit."""
    path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(str(path)) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        yield db


async def init_db(path: pathlib.Path = _DEFAULT_PATH) -> None:
    """Create all tables and indexes if they don't exist."""
    async with get_db(path) as db:
        await db.executescript(DDL)
        await db.commit()
