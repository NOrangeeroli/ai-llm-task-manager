from fastapi import FastAPI

from src.routes.task_routes import router as task_router
from src.utils.db import init_db


app = FastAPI(title="AI-LLM Task Manager", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(task_router, prefix="/api")
