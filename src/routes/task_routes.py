from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.config import settings
from src.controllers import task_controller
from src.models.schemas import (
    NaturalLanguageTaskRequest,
    TagSuggestionRequest,
    TaskCreate,
    TaskQueryParams,
    TaskRead,
    TaskSearchRequest,
    TaskSummaryRequest,
    TaskUpdate,
)
from src.utils.db import get_db
from src.utils.llm_client import LLMClient


router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_llm_client() -> LLMClient:
    return LLMClient(provider=settings.llm_provider, api_key=settings.llm_api_key)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> TaskRead:
    return task_controller.create_task(db, payload)


@router.get("", response_model=list[TaskRead])
def list_tasks(params: TaskQueryParams = Depends(), db: Session = Depends(get_db)) -> list[TaskRead]:
    return task_controller.list_tasks(db, params)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)) -> TaskRead:
    task = task_controller.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)) -> TaskRead:
    task = task_controller.update_task(db, task_id, payload)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
    deleted = task_controller.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@router.post("/natural-language", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task_from_nl(
    req: NaturalLanguageTaskRequest,
    db: Session = Depends(get_db),
    client: LLMClient = Depends(get_llm_client),
) -> TaskRead:
    return task_controller.create_task_from_nl(db, req, client)


@router.post("/{task_id}/tags/suggestions")
def suggest_tags(
    task_id: int,
    req: TagSuggestionRequest,
    db: Session = Depends(get_db),
    client: LLMClient = Depends(get_llm_client),
) -> dict:
    return task_controller.suggest_tags(db, task_id, req, client)


@router.post("/summary")
def summarize_tasks(
    req: TaskSummaryRequest,
    db: Session = Depends(get_db),
    client: LLMClient = Depends(get_llm_client),
) -> dict:
    return task_controller.summarize_tasks(db, req, client)


@router.post("/search")
def semantic_search(
    req: TaskSearchRequest,
    db: Session = Depends(get_db),
    client: LLMClient = Depends(get_llm_client),
) -> dict:
    return task_controller.semantic_search(db, req, client)
