import asyncio
import json
from shared.event_bus import event_bus
from shared.logger import setup_logger

logger = setup_logger("notification_service")

async def log_event(channel, message):
    data = json.loads(message["data"])
    logger.info(f"NOTIFICATION [{channel}]: {json.dumps(data, indent=2)}")

async def main():
    logger.info("Starting Notification Service...")
    channels = ["workflow.created", "task.created", "task.queued", "task.completed", "task.failed", "task.retry"]
    
    ps = event_bus.redis.pubsub()
    await ps.subscribe(*channels)
    
    async for message in ps.listen():
        if message["type"] == "message":
            await log_event(message["channel"], message)

if __name__ == "__main__":
    asyncio.run(main())
