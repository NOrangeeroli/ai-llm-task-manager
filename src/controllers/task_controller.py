from typing import Optional

from sqlalchemy.orm import Session

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
from src.services import ai_service, task_service
from src.utils.llm_client import LLMClient


def create_task(db: Session, payload: TaskCreate) -> TaskRead:
    task = task_service.create_task(db, payload)
    return TaskRead.model_validate(task)


def list_tasks(db: Session, params: TaskQueryParams) -> list[TaskRead]:
    tasks = task_service.list_tasks(db, params)
    return [TaskRead.model_validate(t) for t in tasks]


def get_task(db: Session, task_id: int) -> Optional[TaskRead]:
    task = task_service.get_task(db, task_id)
    return TaskRead.model_validate(task) if task else None


def update_task(db: Session, task_id: int, payload: TaskUpdate) -> Optional[TaskRead]:
    task = task_service.update_task(db, task_id, payload)
    return TaskRead.model_validate(task) if task else None


def delete_task(db: Session, task_id: int) -> bool:
    return task_service.delete_task(db, task_id)


def create_task_from_nl(db: Session, req: NaturalLanguageTaskRequest, client: LLMClient) -> TaskRead:
    parsed = ai_service.parse_natural_language_task(req.text, client)
    task = task_service.create_task(db, TaskCreate(**parsed))
    return TaskRead.model_validate(task)


def suggest_tags(db: Session, task_id: int, req: TagSuggestionRequest, client: LLMClient) -> dict:
    task = task_service.get_task(db, task_id)
    return ai_service.suggest_tags_and_priority(task, req, client)


def summarize_tasks(db: Session, req: TaskSummaryRequest, client: LLMClient) -> dict:
    if req.task_ids:
        tasks = [task_service.get_task(db, tid) for tid in req.task_ids]
        tasks = [t for t in tasks if t is not None]
    else:
        tasks = task_service.list_tasks(db, TaskQueryParams(limit=100))
    return ai_service.summarize_tasks(tasks, client)


def semantic_search(db: Session, req: TaskSearchRequest, client: LLMClient) -> dict:
    tasks = task_service.list_tasks(db, TaskQueryParams(limit=req.limit))
    return ai_service.semantic_search(req.query, tasks, client, limit=req.limit)
