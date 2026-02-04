from typing import Optional

from sqlalchemy.orm import Session

from src.models.schemas import TaskCreate, TaskQueryParams, TaskRead, TaskUpdate
from src.services import task_service


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
