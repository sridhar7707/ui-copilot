import asyncio
import pathlib

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from backend.api.routes.analyze import router as analyze_router
from backend.api.routes.projects import router as projects_router
from backend.api.routes.screenshot import router as screenshot_router
from backend.db.schema import init_db
from backend.services import benchmark_service

_FRONTEND = pathlib.Path(__file__).resolve().parents[2] / "frontend"
_DASHBOARD = _FRONTEND / "index.html"
_GALLERY = _FRONTEND / "gallery.html"

app = FastAPI(
    title="UICopilot",
    description="AI UI/UX Engineering Platform",
    version="0.1.0",
)

app.include_router(analyze_router, prefix="/api/v1")
app.include_router(screenshot_router, prefix="/api/v1")
app.include_router(projects_router, prefix="/api/v1")


@app.on_event("startup")
async def startup() -> None:
    await init_db()
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, benchmark_service.prewarm)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard() -> str:
    return _DASHBOARD.read_text(encoding="utf-8")


@app.get("/gallery", response_class=HTMLResponse, include_in_schema=False)
def gallery() -> str:
    return _GALLERY.read_text(encoding="utf-8")
