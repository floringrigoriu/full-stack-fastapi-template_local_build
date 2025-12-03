import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Task, TaskCreate, TaskPublic, TasksPublic, TaskUpdate, Message

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=TasksPublic)
def read_tasks(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve tasks.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Task)
        count = session.exec(count_statement).one()
        statement = select(Task).offset(skip).limit(limit)
        tasks = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Task)
            .where(Task.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Task)
            .where(Task.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        tasks = session.exec(statement).all()
    return TasksPublic(data=tasks, count=count)

@router.get("/{id}", response_model=TaskPublic)
def read_task(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get task by ID.
    """
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not current_user.is_superuser and task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return task

@router.post("/", response_model=TaskPublic)
def create_task(
    session: SessionDep, current_user: CurrentUser, task_in: TaskCreate
) -> Any:
    """
    Create new task.
    """
    db_task = Task.model_validate(task_in, update={"owner_id": current_user.id})
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.put("/{id}", response_model=TaskPublic)
def update_task(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID, task_in: TaskUpdate
) -> Any:
    """
    Update a task.
    """
    db_task = session.get(Task, id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not current_user.is_superuser and db_task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_task.sqlmodel_update(task_in.model_dump(exclude_unset=True))
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.delete("/{id}", response_model=Message)
def delete_task(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Delete a task.
    """
    db_task = session.get(Task, id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not current_user.is_superuser and db_task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(db_task)
    session.commit()
    return Message(message="Task deleted successfully")
