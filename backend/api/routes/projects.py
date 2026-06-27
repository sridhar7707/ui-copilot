"""
Module 1 — Project Management API routes.
Module 17 — UI Trend Analysis routes.

POST /api/v1/projects           — create project
GET  /api/v1/projects           — list all projects
GET  /api/v1/projects/{id}      — get project
DELETE /api/v1/projects/{id}    — delete project

POST /api/v1/projects/{id}/pages        — add page to project
GET  /api/v1/projects/{id}/pages        — list pages in project
GET  /api/v1/projects/{id}/trend        — score-over-time across all pages

GET  /api/v1/pages/{id}                 — get page
GET  /api/v1/pages/{id}/analyses        — list analyses for a page
GET  /api/v1/pages/{id}/trend           — score-over-time for one page
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.repositories import analysis_repo, page_repo, project_repo
from backend.services import consistency_service, trend_service

router = APIRouter(tags=["projects"])


# ── request models ────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str
    description: str = ""


class PageCreate(BaseModel):
    url: str = ""
    title: str = ""


# ── projects ──────────────────────────────────────────────────────────────────

@router.post("/projects", status_code=201)
async def create_project(body: ProjectCreate) -> dict:
    if not body.name.strip():
        raise HTTPException(status_code=422, detail="Project name cannot be empty.")
    return await project_repo.create(body.name.strip(), body.description)


@router.get("/projects")
async def list_projects() -> list[dict]:
    return await project_repo.list_all()


@router.get("/projects/{project_id}")
async def get_project(project_id: int) -> dict:
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: int) -> None:
    deleted = await project_repo.delete(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found.")


# ── pages ─────────────────────────────────────────────────────────────────────

@router.post("/projects/{project_id}/pages", status_code=201)
async def create_page(project_id: int, body: PageCreate) -> dict:
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return await page_repo.create(project_id, body.url, body.title)


@router.get("/projects/{project_id}/pages")
async def list_pages(project_id: int) -> list[dict]:
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return await page_repo.list_for_project(project_id)


@router.get("/pages/{page_id}")
async def get_page(page_id: int) -> dict:
    page = await page_repo.get(page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found.")
    return page


# ── analyses (read-only; writing is done via /analyze endpoints) ─────────────

@router.get("/pages/{page_id}/analyses")
async def list_analyses(page_id: int) -> list[dict]:
    page = await page_repo.get(page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found.")
    return await analysis_repo.list_for_page(page_id)


# ── trend (Module 17) ─────────────────────────────────────────────────────────

@router.get("/pages/{page_id}/trend")
async def page_trend(page_id: int) -> dict:
    """Score-over-time for a single page."""
    page = await page_repo.get(page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found.")
    analyses = await analysis_repo.list_for_page(page_id)
    return trend_service.page_trend(analyses)


@router.get("/projects/{project_id}/trend")
async def project_trend(project_id: int) -> dict:
    """Aggregated score-over-time across all pages in a project."""
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    pages = await page_repo.list_for_project(project_id)
    page_trends = []
    for p in pages:
        analyses = await analysis_repo.list_for_page(p["id"])
        page_trends.append(trend_service.page_trend(analyses))
    return {
        "project": project,
        **trend_service.project_trend(page_trends),
        "pages": [
            {"page_id": pages[i]["id"], "url": pages[i]["url"], **page_trends[i]}
            for i in range(len(pages))
        ],
    }


# ── consistency (Module 16) ───────────────────────────────────────────────────

@router.get("/projects/{project_id}/consistency")
async def project_consistency(project_id: int) -> dict:
    """Cross-page consistency report for a project."""
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    pages = await page_repo.list_for_project(project_id)
    latest_analyses = [await analysis_repo.latest_for_page(p["id"]) for p in pages]
    return {
        "project_id": project_id,
        **consistency_service.build_report(pages, latest_analyses),
    }
