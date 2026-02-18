import asyncio
import json
from sqlalchemy.future import select
from shared.database import async_session_factory
from shared.models import Task
from shared.event_bus import event_bus
from shared.logger import setup_logger

logger = setup_logger("retry_engine")

async def process_task_failed(message):
    try:
        data = json.loads(message["data"])
        task_id = data.get("task_id")
        
        async with async_session_factory() as db:
            result = await db.execute(select(Task).where(Task.id == task_id))
            task = result.scalar_one_or_none()
            
            if not task:
                logger.error(f"Task {task_id} not found")
                return
            
            if task.retry_count < task.max_retries:
                # Exponential backoff (simulated with sleep? Or just schedule?)
                # For demo, just immediate or short delay
                wait_time = 2 ** task.retry_count
                logger.info(f"Retrying task {task.id} in {wait_time}s (Attempt {task.retry_count + 1}/{task.max_retries})")
                
                await asyncio.sleep(wait_time)
                
                task.retry_count += 1
                task.status = "QUEUED"
                task.error = None # Clear error
                await db.commit()
                
                await event_bus.publish("task.queued", {
                    "workflow_id": str(task.workflow_id),
                    "task_id": str(task.id),
                    "task_name": task.name,
                    "task_type": task.task_type,
                    "payload": task.payload
                })
                await event_bus.publish("task.retry", {
                    "workflow_id": str(task.workflow_id),
                    "task_id": str(task.id),
                     "retry_count": task.retry_count
                })
            else:
                logger.error(f"Task {task.id} exceeded max retries. Workflow failed.")
                # Mark workflow as failed?
                # Ideally we should traverse up to workflow and mark it.
                # But let's keep it simple.
                pass

    except Exception as e:
        logger.error(f"Error processing task failure: {e}")

async def main():
    logger.info("Starting Retry Engine...")
    pubsub = await event_bus.subscribe("task.failed")
    
    async for message in pubsub.listen():
        if message["type"] == "message":
            # Fire and forget / background task for retry logic to avoid blocking listener?
            # Creating task is safer if we sleep.
            asyncio.create_task(process_task_failed(message))

if __name__ == "__main__":
    asyncio.run(main())
