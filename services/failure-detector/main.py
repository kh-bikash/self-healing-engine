import asyncio
from datetime import datetime, timedelta
from sqlalchemy.future import select
from shared.database import async_session_factory
from shared.models import Task
from shared.event_bus import event_bus
from shared.logger import setup_logger

logger = setup_logger("failure_detector")

STALE_TASK_TIMEOUT_SECONDS = 30 

async def check_stale_tasks():
    logger.info("Checking for stale tasks...")
    try:
        async with async_session_factory() as db:
            # Find tasks that are RUNNING for more than X seconds
            cutoff = datetime.utcnow() - timedelta(seconds=STALE_TASK_TIMEOUT_SECONDS)
            stmt = select(Task).where(Task.status == "RUNNING", Task.updated_at < cutoff)
            result = await db.execute(stmt)
            stale_tasks = result.scalars().all()

            for task in stale_tasks:
                logger.warning(f"Detected stale task {task.id} ({task.name}). Marking as FAILED.")
                task.status = "FAILED"
                task.error = "Task execution timed out (Stale)"
                await db.commit()
                
                # Publish event
                await event_bus.publish("task.failed", {
                    "workflow_id": str(task.workflow_id),
                    "task_id": str(task.id),
                    "error": task.error
                })

    except Exception as e:
        logger.error(f"Error checking stale tasks: {e}")

async def main():
    logger.info("Starting Failure Detector...")
    while True:
        await check_stale_tasks()
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
