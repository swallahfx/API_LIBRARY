import redis.asyncio as redis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.redis: redis.Redis = None
    
    async def connect(self):
        """Connect to Redis"""
        logger.info("Connecting to Redis...")
        self.redis = redis.from_url(settings.REDIS_URL)
        await self.redis.ping()
        logger.info("Connected to Redis")
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")
    
    async def get(self, key: str):
        """Get value from Redis"""
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, expire: int = None):
        """Set value in Redis"""
        return await self.redis.set(key, value, ex=expire)
    
    async def delete(self, key: str):
        """Delete key from Redis"""
        return await self.redis.delete(key)

redis_client = RedisClient()
