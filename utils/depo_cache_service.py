"""
Depo Sorumlusu Cache Service
Depo sorumlusu stok ve sipariş endpoint'leri için cache yönetimi
"""

import logging
from utils.cache_helper import cache_get, cache_set, cache_delete_pattern

logger = logging.getLogger(__name__)


class DepoCacheService:
    """Depo sorumlusu cache yönetimi"""
    
    CACHE_PREFIX = "depo_sorumlusu"
    
    # Cache süreleri (saniye)
    STOK_BILGILERI_TTL = 30  # 30 saniye
    SIPARIS_LISTESI_TTL = 45  # 45 saniye
    TEDARIK_LISTESI_TTL = 60  # 1 dakika
    
    @staticmethod
    def get_stok_bilgileri_cache_key(cache_key: str):
        """Stok bilgileri cache key"""
        return f"{DepoCacheService.CACHE_PREFIX}:stok:{cache_key}"
    
    @staticmethod
    def get_stok_bilgileri(cache_key: str):
        """Cache'den stok bilgileri al"""
        full_key = DepoCacheService.get_stok_bilgileri_cache_key(cache_key)
        return cache_get(full_key)
    
    @staticmethod
    def set_stok_bilgileri(cache_key: str, data: dict):
        """Stok bilgilerini cache'le"""
        full_key = DepoCacheService.get_stok_bilgileri_cache_key(cache_key)
        return cache_set(full_key, data, DepoCacheService.STOK_BILGILERI_TTL)
    
    @staticmethod
    def get_siparis_listesi_cache_key(otel_id: int = None):
        """Sipariş listesi cache key"""
        key = f"{DepoCacheService.CACHE_PREFIX}:siparis"
        if otel_id:
            key += f":{otel_id}"
        return key
    
    @staticmethod
    def get_siparis_listesi(otel_id: int = None):
        """Cache'den sipariş listesi al"""
        cache_key = DepoCacheService.get_siparis_listesi_cache_key(otel_id)
        return cache_get(cache_key)
    
    @staticmethod
    def set_siparis_listesi(data: list, otel_id: int = None):
        """Sipariş listesini cache'le"""
        cache_key = DepoCacheService.get_siparis_listesi_cache_key(otel_id)
        return cache_set(cache_key, data, DepoCacheService.SIPARIS_LISTESI_TTL)
    
    @staticmethod
    def get_tedarik_listesi_cache_key(otel_id: int):
        """Tedarik listesi cache key"""
        return f"{DepoCacheService.CACHE_PREFIX}:tedarik:{otel_id}"
    
    @staticmethod
    def get_tedarik_listesi(otel_id: int):
        """Cache'den tedarik listesi al"""
        cache_key = DepoCacheService.get_tedarik_listesi_cache_key(otel_id)
        return cache_get(cache_key)
    
    @staticmethod
    def set_tedarik_listesi(data: list, otel_id: int):
        """Tedarik listesini cache'le"""
        cache_key = DepoCacheService.get_tedarik_listesi_cache_key(otel_id)
        return cache_set(cache_key, data, DepoCacheService.TEDARIK_LISTESI_TTL)
    
    @staticmethod
    def invalidate_stok(otel_id: int = None):
        """Stok cache'ini temizle"""
        if otel_id:
            pattern = f"{DepoCacheService.CACHE_PREFIX}:stok:*{otel_id}*"
        else:
            pattern = f"{DepoCacheService.CACHE_PREFIX}:stok:*"
        deleted = cache_delete_pattern(pattern)
        logger.info(f"Depo stok cache temizlendi (otel={otel_id}): {deleted} key")
        return deleted
    
    @staticmethod
    def invalidate_siparis(otel_id: int = None):
        """Sipariş cache'ini temizle"""
        if otel_id:
            pattern = f"{DepoCacheService.CACHE_PREFIX}:siparis:{otel_id}*"
        else:
            pattern = f"{DepoCacheService.CACHE_PREFIX}:siparis*"
        deleted = cache_delete_pattern(pattern)
        logger.info(f"Depo sipariş cache temizlendi (otel={otel_id}): {deleted} key")
        return deleted
    
    @staticmethod
    def invalidate_tedarik(otel_id: int):
        """Tedarik cache'ini temizle"""
        pattern = f"{DepoCacheService.CACHE_PREFIX}:tedarik:{otel_id}*"
        deleted = cache_delete_pattern(pattern)
        logger.info(f"Depo tedarik cache temizlendi (otel={otel_id}): {deleted} key")
        return deleted
    
    @staticmethod
    def invalidate_otel(otel_id: int):
        """Otele ait tüm cache'i temizle"""
        pattern = f"{DepoCacheService.CACHE_PREFIX}:*:{otel_id}*"
        deleted = cache_delete_pattern(pattern)
        logger.info(f"Depo cache temizlendi (otel={otel_id}): {deleted} key")
        return deleted
