from typing import Dict, Any, Optional
from redis import Redis
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    """Redis cache implementation"""
    def __init__(self, host: str, port: int):
        self.client = Redis(host=host, port=port)
        
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from cache"""
        try:
            value = self.client.get(key)
            if value:
                return value
            return None
            
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None
            
    async def set(
        self,
        key: str,
        value: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        try:
            return self.client.set(
                key,
                value,
                ex=ttl
            )
            
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False
            
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            return bool(self.client.delete(key))
            
        except Exception as e:
            logger.error(f"Redis delete error: {str(e)}")
            return False
            
    async def clear(self) -> bool:
        """Clear all values from cache"""
        try:
            return self.client.flushall()
            
        except Exception as e:
            logger.error(f"Redis clear error: {str(e)}")
            return False
            
    async def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        try:
            info = self.client.info()
            return {
                'hits': int(info['keyspace_hits']),
                'misses': int(info['keyspace_misses']),
                'memory': int(info['used_memory']),
                'keys': len(self.client.keys('*'))
            }
            
        except Exception as e:
            logger.error(f"Redis stats error: {str(e)}")
            return {
                'hits': 0,
                'misses': 0,
                'memory': 0,
                'keys': 0
            }

class CacheService:
    """Abstract cache service interface"""
    async def get(
        self,
        key: str
    ) -> Optional[Dict[str, Any]]:
        raise NotImplementedError
        
    async def set(
        self,
        key: str,
        value: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        raise NotImplementedError
        
    async def delete(self, key: str) -> bool:
        raise NotImplementedError
        
    async def clear(self) -> bool:
        raise NotImplementedError
        
    async def get_stats(self) -> Dict[str, int]:
        raise NotImplementedError