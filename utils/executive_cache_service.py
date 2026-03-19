"""
Executive Dashboard Cache Service
Executive dashboard endpoint'leri için cache yönetimi
"""

import logging
from utils.cache_helper import cache_get, cache_set, cache_delete_pattern

logger = logging.getLogger(__name__)


class ExecutiveCacheService:
    """Executive dashboard cache yönetimi"""
    
    CACHE_PREFIX = "executive"
    
    # Cache süreleri (saniye)
    KPI_SUMMARY_TTL = 60  # 1 dakika
    HOTEL_COMPARISON_TTL = 60  # 1 dakika
    CONSUMPTION_TRENDS_TTL = 120  # 2 dakika
    ROOM_CONTROL_STATS_TTL = 90  # 1.5 dakika
    TASK_COMPLETION_TTL = 60  # 1 dakika
    ACTIVITY_FEED_TTL = 30  # 30 saniye
    
    @staticmethod
    def get_kpi_cache_key(period: str = 'today'):
        """KPI summary cache key"""
        return f"{ExecutiveCacheService.CACHE_PREFIX}:kpi:{period}"
    
    @staticmethod
    def get_kpi_summary(period: str = 'today'):
        """Cache'den KPI summary al"""
        cache_key = ExecutiveCacheService.get_kpi_cache_key(period)
        return cache_get(cache_key)
    
    @staticmethod
    def set_kpi_summary(data: dict, period: str = 'today'):
        """KPI summary'yi cache'le"""
        cache_key = ExecutiveCacheService.get_kpi_cache_key(period)
        return cache_set(cache_key, data, ExecutiveCacheService.KPI_SUMMARY_TTL)
    
    @staticmethod
    def get_hotel_comparison_cache_key(period: str = 'today'):
        """Hotel comparison cache key"""
        return f"{ExecutiveCacheService.CACHE_PREFIX}:hotel_comparison:{period}"
    
    @staticmethod
    def get_hotel_comparison(period: str = 'today'):
        """Cache'den hotel comparison al"""
        cache_key = ExecutiveCacheService.get_hotel_comparison_cache_key(period)
        return cache_get(cache_key)
    
    @staticmethod
    def set_hotel_comparison(data: list, period: str = 'today'):
        """Hotel comparison'ı cache'le"""
        cache_key = ExecutiveCacheService.get_hotel_comparison_cache_key(period)
        return cache_set(cache_key, data, ExecutiveCacheService.HOTEL_COMPARISON_TTL)
    
    @staticmethod
    def get_consumption_trends_cache_key(period: str = 'today', days: int = None):
        """Consumption trends cache key"""
        key = f"{ExecutiveCacheService.CACHE_PREFIX}:consumption:{period}"
        if days:
            key += f":{days}"
        return key
    
    @staticmethod
    def get_consumption_trends(period: str = 'today', days: int = None):
        """Cache'den consumption trends al"""
        cache_key = ExecutiveCacheService.get_consumption_trends_cache_key(period, days)
        return cache_get(cache_key)
    
    @staticmethod
    def set_consumption_trends(data: dict, period: str = 'today', days: int = None):
        """Consumption trends'i cache'le"""
        cache_key = ExecutiveCacheService.get_consumption_trends_cache_key(period, days)
        return cache_set(cache_key, data, ExecutiveCacheService.CONSUMPTION_TRENDS_TTL)
    
    @staticmethod
    def get_room_control_stats_cache_key(period: str = 'today', days: int = None):
        """Room control stats cache key"""
        key = f"{ExecutiveCacheService.CACHE_PREFIX}:room_control:{period}"
        if days:
            key += f":{days}"
        return key
    
    @staticmethod
    def get_room_control_stats(period: str = 'today', days: int = None):
        """Cache'den room control stats al"""
        cache_key = ExecutiveCacheService.get_room_control_stats_cache_key(period, days)
        return cache_get(cache_key)
    
    @staticmethod
    def set_room_control_stats(data: dict, period: str = 'today', days: int = None):
        """Room control stats'i cache'le"""
        cache_key = ExecutiveCacheService.get_room_control_stats_cache_key(period, days)
        return cache_set(cache_key, data, ExecutiveCacheService.ROOM_CONTROL_STATS_TTL)
    
    @staticmethod
    def get_task_completion_cache_key(period: str = 'today'):
        """Task completion cache key"""
        return f"{ExecutiveCacheService.CACHE_PREFIX}:task_completion:{period}"
    
    @staticmethod
    def get_task_completion(period: str = 'today'):
        """Cache'den task completion al"""
        cache_key = ExecutiveCacheService.get_task_completion_cache_key(period)
        return cache_get(cache_key)
    
    @staticmethod
    def set_task_completion(data: list, period: str = 'today'):
        """Task completion'ı cache'le"""
        cache_key = ExecutiveCacheService.get_task_completion_cache_key(period)
        return cache_set(cache_key, data, ExecutiveCacheService.TASK_COMPLETION_TTL)
    
    @staticmethod
    def get_activity_feed_cache_key(limit: int = 50):
        """Activity feed cache key"""
        return f"{ExecutiveCacheService.CACHE_PREFIX}:activity:{limit}"
    
    @staticmethod
    def get_activity_feed(limit: int = 50):
        """Cache'den activity feed al"""
        cache_key = ExecutiveCacheService.get_activity_feed_cache_key(limit)
        return cache_get(cache_key)
    
    @staticmethod
    def set_activity_feed(data: list, limit: int = 50):
        """Activity feed'i cache'le"""
        cache_key = ExecutiveCacheService.get_activity_feed_cache_key(limit)
        return cache_set(cache_key, data, ExecutiveCacheService.ACTIVITY_FEED_TTL)
    
    @staticmethod
    def invalidate_all():
        """Tüm executive dashboard cache'ini temizle"""
        pattern = f"{ExecutiveCacheService.CACHE_PREFIX}:*"
        deleted = cache_delete_pattern(pattern)
        logger.info(f"Executive dashboard cache temizlendi: {deleted} key")
        return deleted
    
    @staticmethod
    def invalidate_period(period: str):
        """Belirli bir period için cache'i temizle"""
        pattern = f"{ExecutiveCacheService.CACHE_PREFIX}:*:{period}*"
        deleted = cache_delete_pattern(pattern)
        logger.info(f"Executive dashboard cache temizlendi (period={period}): {deleted} key")
        return deleted
