from fastapi import Depends, FastAPI

from src.config import settings
from src.routes.task_routes import router as task_router
from src.utils.db import init_db
from src.utils.llm_client import LLMClient


app = FastAPI(title="AI-LLM Task Manager", version="0.1.0")


def get_llm_client() -> LLMClient:
    return LLMClient(provider=settings.llm_provider, api_key=settings.llm_api_key)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(task_router, prefix="/api")
