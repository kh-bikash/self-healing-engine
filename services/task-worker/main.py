import asyncio
import json
import random
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from shared.database import async_session_factory
from shared.models import Workflow, Task
from shared.event_bus import event_bus
from shared.logger import setup_logger

logger = setup_logger("task_worker")

async def process_task(message):
    try:
        data = json.loads(message["data"])
        task_id = data.get("task_id")
        
        async with async_session_factory() as db:
            result = await db.execute(select(Task).where(Task.id == task_id))
            task = result.scalar_one_or_none()

            if not task:
                logger.error(f"Task {task_id} not found")
                return

            if task.status not in ["QUEUED", "PENDING"]:
                logger.warning(f"Task {task_id} is {task.status}, skipping")
                return

            task.status = "RUNNING"
            await db.commit()
            
            logger.info(f"Executing task: {task.name} ({task.id})")
            
            # Simulate work
            await asyncio.sleep(1) # mock processing time

            # Check for simulated failure
            payload = task.payload or {}
            if payload.get("simulate_failure", False):
                # Only fail if we haven't maxed out retries? 
                # actually failure detector/retry engine handles the retry logic.
                # Here we just fail.
                raise Exception("Simulated Failure")

            task.status = "COMPLETED"
            task.result = {"status": "success", "processed": True}
            await db.commit()

            await event_bus.publish("task.completed", {
                "workflow_id": str(task.workflow_id),
                "task_id": str(task.id),
                "task_name": task.name
            })
            logger.info(f"Task {task.id} completed")

            # Trigger next task if exists
            if task.next_task:
                # Find the next task by name in the same workflow
                # We need to query the workflow's tasks
                # Using a fresh query to avoid stale relation issues
                # Note: This is an async query inside the session
                stmt = select(Task).where(Task.workflow_id == task.workflow_id, Task.name == task.next_task)
                next_task_result = await db.execute(stmt)
                next_task_obj = next_task_result.scalar_one_or_none()
                
                if next_task_obj:
                    next_task_obj.status = "QUEUED"
                    await db.commit()
                    await event_bus.publish("task.queued", {
                        "workflow_id": str(next_task_obj.workflow_id),
                        "task_id": str(next_task_obj.id),
                        "task_name": next_task_obj.name,
                        "task_type": next_task_obj.task_type,
                        "payload": next_task_obj.payload
                    })
                    logger.info(f"Triggered next task: {next_task_obj.name}")
                else:
                    logger.error(f"Next task {task.next_task} not found for workflow {task.workflow_id}")
            else:
                 # Check if workflow is complete (no running tasks)
                 # This is a bit simplistic, but valid for a chain.
                 # Updated workflow status
                 wf_stmt = select(Workflow).where(Workflow.id == task.workflow_id)
                 wf_result = await db.execute(wf_stmt)
                 wf = wf_result.scalar_one()
                 wf.status = "COMPLETED"
                 await db.commit()
                 logger.info(f"Workflow {wf.id} completed")

    except Exception as e:
        logger.error(f"Task failed: {e}")
        # Re-fetch task to update status safely
        try:
             async with async_session_factory() as error_db:
                task_res = await error_db.execute(select(Task).where(Task.id == task_id))
                failed_task = task_res.scalar_one_or_none()
                if failed_task:
                    failed_task.status = "FAILED"
                    failed_task.error = str(e)
                    await error_db.commit()
                    
                    await event_bus.publish("task.failed", {
                        "workflow_id": str(failed_task.workflow_id),
                        "task_id": str(failed_task.id),
                        "error": str(e)
                    })
        except Exception as db_e:
            logger.critical(f"Failed to update task status to FAILED: {db_e}")

async def main():
    logger.info("Starting Task Worker...")
    pubsub = await event_bus.subscribe("task.queued")
    
    async for message in pubsub.listen():
        if message["type"] == "message":
            # Process in background task to not block the listener?
            # For simplicity/safety in this demo, await it.
            # In high perf, create_task.
            await process_task(message)

if __name__ == "__main__":
    asyncio.run(main())
