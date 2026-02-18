from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from shared.database import get_db, init_db
from shared.models import Workflow, Task
from shared.schemas import WorkflowCreate, WorkflowResponse
from shared.event_bus import event_bus
from shared.logger import setup_logger
from contextlib import asynccontextmanager

logger = setup_logger("api_gateway")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API Gateway...")
    await init_db()
    yield
    logger.info("Stopping API Gateway...")

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Self-Healing Workflow Engine", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(workflow: WorkflowCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"Creating workflow: {workflow.name}")
    
    # Create workflow record
    db_workflow = Workflow(name=workflow.name, status="PENDING")
    
    # Create task records
    for task_data in workflow.tasks:
        db_task = Task(
            name=task_data.name,
            task_type=task_data.task_type,
            payload=task_data.payload,
            next_task=task_data.next_task,
            max_retries=task_data.max_retries,
            workflow=db_workflow
        )
        db_workflow.tasks.append(db_task)
    
    db.add(db_workflow)
    await db.commit()
    await db.refresh(db_workflow) # This might not load relationships immediately

    # Re-fetch with relationship to ensure selectinload
    stmt = select(Workflow).options(selectinload(Workflow.tasks)).where(Workflow.id == db_workflow.id)
    result = await db.execute(stmt)
    db_workflow_loaded = result.scalar_one()

    # Publish event
    await event_bus.publish("workflow.created", {"workflow_id": str(db_workflow_loaded.id)})
    
    return db_workflow_loaded

@app.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Workflow).options(selectinload(Workflow.tasks)).where(Workflow.id == workflow_id)
    result = await db.execute(stmt)
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    return workflow

@app.get("/workflows", response_model=list[WorkflowResponse])
async def list_workflows(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    stmt = select(Workflow).options(selectinload(Workflow.tasks)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    workflows = result.scalars().all()
    return workflows
