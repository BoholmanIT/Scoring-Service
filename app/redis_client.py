import redis
import json
from typing import Optional
from config import settings

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True
        )
    
    def get_cached_result(self, key: str) -> Optional[float]:
        """Получить закешированный результат"""
        cached = self.client.get(key)
        if cached:
            return float(cached)
        return None
    
    def cache_result(self, key: str, result: float, ttl: int = 3600):
        """Сохранить результат в кэш"""
        self.client.setex(key, ttl, str(result))
    
    def generate_cache_key(self, request_data: dict) -> str:
        """Генерация ключа кэша на основе входных данных"""
        import hashlib
        data_str = json.dumps(request_data, sort_keys=True)
        return f"scoring:{hashlib.md5(data_str.encode()).hexdigest()}"

redis_client = RedisClient()