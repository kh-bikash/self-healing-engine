import asyncio
import json
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from shared.database import async_session_factory
from shared.models import Workflow, Task
from shared.event_bus import event_bus
from shared.logger import setup_logger

logger = setup_logger("workflow_orchestrator")

async def process_workflow_created(message):
    try:
        data = json.loads(message["data"])
        workflow_id = data["workflow_id"]
        logger.info(f"Processing new workflow: {workflow_id}")

        async with async_session_factory() as db:
            # Fetch workflow with tasks
            stmt = select(Workflow).options(selectinload(Workflow.tasks)).where(Workflow.id == workflow_id)
            result = await db.execute(stmt)
            workflow = result.scalar_one_or_none()

            if not workflow:
                logger.error(f"Workflow {workflow_id} not found")
                return

            # Find the first task (no dependencies or simplistically the first one if linear)
            # For this simplified engine, we assume the first task in the list is the start 
            # OR the one that is not a 'next_task' of any other task. 
            # But the prompt says "Tasks... next_task". 
            # Let's find the task that is NOT anyone's next_task, or just pick the first one blindly if simple.
            # A better approach for a linear chain: find task where name is not in [t.next_task for t in tasks]
            
            all_next_tasks = {t.next_task for t in workflow.tasks if t.next_task}
            start_tasks = [t for t in workflow.tasks if t.name not in all_next_tasks]
            
            if not start_tasks:
                 # Fallback: just pick the first one if circular or ambiguous
                 if workflow.tasks:
                     start_tasks = [workflow.tasks[0]]
                 else:
                     logger.warning(f"Workflow {workflow_id} has no tasks")
                     workflow.status = "COMPLETED"
                     await db.commit()
                     return

            for task in start_tasks:
                task.status = "QUEUED"
                await db.commit()
                # Publish task.queued to trigger execution
                await event_bus.publish("task.queued", {
                    "workflow_id": str(workflow.id),
                    "task_id": str(task.id),
                    "task_name": task.name,
                    "task_type": task.task_type,
                    "payload": task.payload
                })
                logger.info(f"Queued task {task.id} ({task.name})")

            workflow.status = "RUNNING"
            await db.commit()

    except Exception as e:
        logger.error(f"Error processing workflow_created: {e}")

async def main():
    logger.info("Starting Workflow Orchestrator...")
    pubsub = await event_bus.subscribe("workflow.created")
    
    async for message in pubsub.listen():
        if message["type"] == "message":
            await process_workflow_created(message)

if __name__ == "__main__":
    asyncio.run(main())
