from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.models.schemas import TaskCreate, TaskQueryParams, TaskUpdate
from src.models.task import Task


def create_task(db: Session, payload: TaskCreate) -> Task:
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(db: Session, params: TaskQueryParams) -> list[Task]:
    stmt = select(Task)

    if params.status:
        stmt = stmt.where(Task.status == params.status)
    if params.priority:
        stmt = stmt.where(Task.priority == params.priority)
    if params.tag:
        stmt = stmt.where(Task.tags.contains([params.tag]))
    if params.search:
        pattern = f"%{params.search}%"
        stmt = stmt.where(or_(Task.title.ilike(pattern), Task.description.ilike(pattern)))

    stmt = stmt.offset(params.offset).limit(params.limit)
    return list(db.execute(stmt).scalars().all())


def get_task(db: Session, task_id: int) -> Optional[Task]:
    return db.get(Task, task_id)


def update_task(db: Session, task_id: int, payload: TaskUpdate) -> Optional[Task]:
    task = get_task(db, task_id)
    if not task:
        return None

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int) -> bool:
    task = get_task(db, task_id)
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True
