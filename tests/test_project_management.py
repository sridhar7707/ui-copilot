"""
Module 1 — Project Management: repository-level tests using isolated per-test
SQLite files.  Runs as native async tests via pytest-asyncio (auto mode).
"""
from __future__ import annotations

import pathlib

import pytest

from backend.db.schema import init_db
from backend.repositories import analysis_repo, page_repo, project_repo
from backend.services import scoring_engine
from tests.fixtures import bad_page


@pytest.fixture
async def db_path(tmp_path: pathlib.Path) -> pathlib.Path:
    p = tmp_path / "test.db"
    await init_db(p)
    return p


# ── project CRUD ──────────────────────────────────────────────────────────────

class TestProjectRepo:
    async def test_create_returns_dict_with_id(self, db_path):
        proj = await project_repo.create("My App", "A test project", db_path)
        assert proj["id"] == 1
        assert proj["name"] == "My App"
        assert proj["description"] == "A test project"
        assert "created_at" in proj

    async def test_get_returns_project(self, db_path):
        await project_repo.create("Alpha", db_path=db_path)
        proj = await project_repo.get(1, db_path)
        assert proj["name"] == "Alpha"

    async def test_get_missing_returns_none(self, db_path):
        assert await project_repo.get(999, db_path) is None

    async def test_list_all_empty_initially(self, db_path):
        assert await project_repo.list_all(db_path) == []

    async def test_list_all_returns_all_projects(self, db_path):
        await project_repo.create("A", db_path=db_path)
        await project_repo.create("B", db_path=db_path)
        projects = await project_repo.list_all(db_path)
        assert len(projects) == 2

    async def test_delete_removes_project(self, db_path):
        await project_repo.create("To delete", db_path=db_path)
        deleted = await project_repo.delete(1, db_path)
        assert deleted is True
        assert await project_repo.get(1, db_path) is None

    async def test_delete_missing_returns_false(self, db_path):
        assert await project_repo.delete(999, db_path) is False


# ── page CRUD ─────────────────────────────────────────────────────────────────

class TestPageRepo:
    async def test_create_page_linked_to_project(self, db_path):
        await project_repo.create("Proj", db_path=db_path)
        page = await page_repo.create(1, "https://example.com", "Home", db_path)
        assert page["project_id"] == 1
        assert page["url"] == "https://example.com"
        assert page["title"] == "Home"

    async def test_list_for_project_returns_pages(self, db_path):
        await project_repo.create("Proj", db_path=db_path)
        await page_repo.create(1, "https://a.com", "A", db_path)
        await page_repo.create(1, "https://b.com", "B", db_path)
        pages = await page_repo.list_for_project(1, db_path)
        assert len(pages) == 2

    async def test_list_for_project_empty_when_none(self, db_path):
        await project_repo.create("Proj", db_path=db_path)
        assert await page_repo.list_for_project(1, db_path) == []

    async def test_get_page_by_id(self, db_path):
        await project_repo.create("Proj", db_path=db_path)
        await page_repo.create(1, "https://x.com", "X", db_path)
        page = await page_repo.get(1, db_path)
        assert page["url"] == "https://x.com"

    async def test_get_missing_page_returns_none(self, db_path):
        assert await page_repo.get(999, db_path) is None

    async def test_delete_page(self, db_path):
        await project_repo.create("Proj", db_path=db_path)
        await page_repo.create(1, db_path=db_path)
        assert await page_repo.delete(1, db_path) is True
        assert await page_repo.get(1, db_path) is None


# ── analysis storage ──────────────────────────────────────────────────────────

class TestAnalysisRepo:
    async def test_save_returns_row_with_id(self, db_path):
        await project_repo.create("Proj", db_path=db_path)
        await page_repo.create(1, db_path=db_path)
        result = scoring_engine.analyze(bad_page())
        row = await analysis_repo.save(1, result, db_path=db_path)
        assert row["id"] == 1
        assert row["page_id"] == 1
        assert abs(row["overall_score"] - result.overall_score) < 0.01

    async def test_list_for_page_returns_history(self, db_path):
        await project_repo.create("Proj", db_path=db_path)
        await page_repo.create(1, db_path=db_path)
        result = scoring_engine.analyze(bad_page())
        await analysis_repo.save(1, result, db_path=db_path)
        await analysis_repo.save(1, result, db_path=db_path)
        history = await analysis_repo.list_for_page(1, db_path)
        assert len(history) == 2

    async def test_latest_for_page(self, db_path):
        await project_repo.create("Proj", db_path=db_path)
        await page_repo.create(1, db_path=db_path)
        result = scoring_engine.analyze(bad_page())
        await analysis_repo.save(1, result, db_path=db_path)
        latest = await analysis_repo.latest_for_page(1, db_path)
        assert latest is not None
        assert latest["page_id"] == 1

    async def test_latest_returns_none_when_no_analyses(self, db_path):
        await project_repo.create("Proj", db_path=db_path)
        await page_repo.create(1, db_path=db_path)
        assert await analysis_repo.latest_for_page(1, db_path) is None

    async def test_get_full_analysis(self, db_path):
        await project_repo.create("Proj", db_path=db_path)
        await page_repo.create(1, db_path=db_path)
        result = scoring_engine.analyze(bad_page())
        await analysis_repo.save(1, result, db_path=db_path)
        row = await analysis_repo.get(1, db_path)
        assert row is not None
        assert "result_json" in row

    async def test_source_field_stored(self, db_path):
        await project_repo.create("Proj", db_path=db_path)
        await page_repo.create(1, db_path=db_path)
        result = scoring_engine.analyze(bad_page())
        await analysis_repo.save(1, result, source="screenshot", db_path=db_path)
        row = await analysis_repo.get(1, db_path)
        assert row["source"] == "screenshot"
