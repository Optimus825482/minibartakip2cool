"""
Redis Cache Helper
Performans optimizasyonu için cache yardımcı fonksiyonları
"""

import redis
import json
import logging
from functools import wraps
from config import Config

logger = logging.getLogger(__name__)

# Redis bağlantısı
try:
    redis_client = redis.from_url(
        Config.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )
    # Bağlantı testi
    redis_client.ping()
    CACHE_AVAILABLE = True
    logger.info("✅ Redis cache bağlantısı başarılı")
except Exception as e:
    logger.warning(f"⚠️ Redis cache kullanılamıyor: {e}")
    redis_client = None
    CACHE_AVAILABLE = False


def cache_get(key: str):
    """Cache'den veri al"""
    if not CACHE_AVAILABLE or not Config.CACHE_ENABLED:
        return None
    
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        logger.warning(f"Cache get hatası ({key}): {e}")
        return None


def cache_set(key: str, value, ttl: int = 60):
    """Cache'e veri kaydet"""
    if not CACHE_AVAILABLE or not Config.CACHE_ENABLED:
        return False
    
    try:
        redis_client.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )
        return True
    except Exception as e:
        logger.warning(f"Cache set hatası ({key}): {e}")
        return False


def cache_delete(key: str):
    """Cache'den veri sil"""
    if not CACHE_AVAILABLE or not Config.CACHE_ENABLED:
        return False
    
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Cache delete hatası ({key}): {e}")
        return False


def cache_delete_pattern(pattern: str):
    """Pattern'e uyan tüm cache'leri sil"""
    if not CACHE_AVAILABLE or not Config.CACHE_ENABLED:
        return 0
    
    try:
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
        return 0
    except Exception as e:
        logger.warning(f"Cache delete pattern hatası ({pattern}): {e}")
        return 0


def cached(ttl: int = 60, key_prefix: str = ""):
    """
    Decorator: Fonksiyon sonucunu cache'le
    
    Args:
        ttl: Cache süresi (saniye)
        key_prefix: Cache key prefix'i
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Cache key oluştur
            cache_key = f"{key_prefix}:{func.__name__}"
            if args:
                cache_key += f":{':'.join(str(a) for a in args)}"
            if kwargs:
                cache_key += f":{':'.join(f'{k}={v}' for k, v in sorted(kwargs.items()))}"
            
            # Cache'den dene
            cached_data = cache_get(cache_key)
            if cached_data is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached_data
            
            # Cache miss - fonksiyonu çalıştır
            logger.debug(f"Cache MISS: {cache_key}")
            result = func(*args, **kwargs)
            
            # Sonucu cache'le
            cache_set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator
