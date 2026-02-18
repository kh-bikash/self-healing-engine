import json
import redis.asyncio as redis
from shared.settings import settings
from shared.logger import setup_logger

logger = setup_logger("event_bus")

class EventBus:
    def __init__(self):
        self.redis = redis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf-8", decode_responses=True)

    async def publish(self, channel: str, message: dict):
        try:
            await self.redis.publish(channel, json.dumps(message, default=str))
            logger.info(f"Published to {channel}: {message}")
        except Exception as e:
            logger.error(f"Failed to publish to {channel}: {e}")

    async def subscribe(self, channel: str):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

    async def close(self):
        await self.redis.close()

event_bus = EventBus()
