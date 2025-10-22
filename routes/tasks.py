from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Task
from schemas import TaskCreate, TaskResponse
from typing import List
from auth import verify_api_key

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(db: Session = Depends(get_db)):
    """Get all tasks"""
    tasks = db.query(Task).all()
    return tasks

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task: TaskCreate, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create a new task"""
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.put("/tasks/{task_id}")
async def update_task(
    task_id: int, 
    task: TaskCreate, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update a task"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    for key, value in task.dict().items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

@router.put("/tasks/{task_id}/status")
async def update_task_status(
    task_id: int, 
    status: str, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update task status"""
    if status not in ["todo", "inprogress", "completed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.status = status
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete a task"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}