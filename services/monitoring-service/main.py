import asyncio
import json
from collections import defaultdict
from shared.event_bus import event_bus
from shared.logger import setup_logger

logger = setup_logger("monitoring_service")

metrics = defaultdict(int)

async def update_metrics(channel, message):
    metrics[channel] += 1
    # Periodically log stats or expose via an endpoint (skipping endpoint for simplicity)
    # logger.info(f"METRICS UPDATE: {dict(metrics)}")

async def print_stats():
    while True:
        await asyncio.sleep(10)
        logger.info(f"--- SYSTEM METRICS ---")
        for key, value in metrics.items():
            logger.info(f"{key}: {value}")
        logger.info("----------------------")

async def main():
    logger.info("Starting Monitoring Service...")
    channels = ["workflow.created", "task.queued", "task.completed", "task.failed", "task.retry"]
    
    ps = event_bus.redis.pubsub()
    await ps.subscribe(*channels)
    
    asyncio.create_task(print_stats())

    async for message in ps.listen():
        if message["type"] == "message":
            await update_metrics(message["channel"], message)

if __name__ == "__main__":
    asyncio.run(main())
