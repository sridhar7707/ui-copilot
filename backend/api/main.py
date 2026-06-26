from fastapi import FastAPI

from backend.api.routes.analyze import router as analyze_router

app = FastAPI(
    title="UICopilot",
    description="AI UI/UX Engineering Platform",
    version="0.1.0",
)

app.include_router(analyze_router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
