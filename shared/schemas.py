from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

# --- API Models ---

class TaskBase(BaseModel):
    name: str
    task_type: str
    payload: Dict[str, Any] = {}
    next_task: Optional[str] = None
    max_retries: int = 3

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: UUID
    workflow_id: UUID
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WorkflowBase(BaseModel):
    name: str

class WorkflowCreate(WorkflowBase):
    tasks: List[TaskCreate]

class WorkflowResponse(WorkflowBase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    tasks: List[TaskResponse]

    class Config:
        from_attributes = True

# --- Event Models ---

class EventPayload(BaseModel):
    workflow_id: UUID
    task_id: Optional[UUID] = None
    task_name: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
