"""
Module 1 — Project Management API routes.

POST /api/v1/projects           — create project
GET  /api/v1/projects           — list all projects
GET  /api/v1/projects/{id}      — get project
DELETE /api/v1/projects/{id}    — delete project

POST /api/v1/projects/{id}/pages        — add page to project
GET  /api/v1/projects/{id}/pages        — list pages in project

GET  /api/v1/pages/{id}/analyses        — list analyses for a page
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.repositories import analysis_repo, page_repo, project_repo

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
