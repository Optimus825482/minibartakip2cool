"""
Rapor Cache Service
Yavaş rapor endpoint'leri için cache yönetimi
"""

import logging
from utils.cache_helper import cache_get, cache_set, cache_delete_pattern

logger = logging.getLogger(__name__)


class RaporCacheService:
    """Rapor cache yönetimi"""
    
    CACHE_PREFIX = "rapor"
    
    # Cache süreleri (saniye)
    GUN_SONU_RAPORU_TTL = 300  # 5 dakika
    ZIMMET_STOK_RAPORU_TTL = 180  # 3 dakika
    KULLANIM_RAPORU_TTL = 240  # 4 dakika
    
    @staticmethod
    def get_gun_sonu_raporu_cache_key(otel_id: int, personel_ids: list = None, 
                                       baslangic_tarihi=None, bitis_tarihi=None):
        """Gün sonu raporu cache key'i oluştur"""
        key = f"{RaporCacheService.CACHE_PREFIX}:gun_sonu:{otel_id}"
        if personel_ids:
            key += f":{'_'.join(str(p) for p in sorted(personel_ids))}"
        if baslangic_tarihi and bitis_tarihi:
            key += f":{baslangic_tarihi}:{bitis_tarihi}"
        return key
    
    @staticmethod
    def get_gun_sonu_raporu(otel_id: int, personel_ids: list = None,
                            baslangic_tarihi=None, bitis_tarihi=None):
        """Cache'den gün sonu raporu al"""
        cache_key = RaporCacheService.get_gun_sonu_raporu_cache_key(
            otel_id, personel_ids, baslangic_tarihi, bitis_tarihi
        )
        return cache_get(cache_key)
    
    @staticmethod
    def set_gun_sonu_raporu(otel_id: int, data: dict, personel_ids: list = None,
                            baslangic_tarihi=None, bitis_tarihi=None):
        """Gün sonu raporunu cache'le"""
        cache_key = RaporCacheService.get_gun_sonu_raporu_cache_key(
            otel_id, personel_ids, baslangic_tarihi, bitis_tarihi
        )
        return cache_set(cache_key, data, RaporCacheService.GUN_SONU_RAPORU_TTL)
    
    @staticmethod
    def invalidate_gun_sonu_raporu(otel_id: int = None):
        """Gün sonu raporu cache'ini temizle"""
        if otel_id:
            pattern = f"{RaporCacheService.CACHE_PREFIX}:gun_sonu:{otel_id}:*"
        else:
            pattern = f"{RaporCacheService.CACHE_PREFIX}:gun_sonu:*"
        
        deleted = cache_delete_pattern(pattern)
        logger.info(f"Gün sonu raporu cache temizlendi: {deleted} key")
        return deleted
    
    @staticmethod
    def get_zimmet_stok_raporu_cache_key(otel_id: int = None):
        """Zimmet stok raporu cache key'i"""
        if otel_id:
            return f"{RaporCacheService.CACHE_PREFIX}:zimmet_stok:{otel_id}"
        return f"{RaporCacheService.CACHE_PREFIX}:zimmet_stok:all"
    
    @staticmethod
    def get_zimmet_stok_raporu(otel_id: int = None):
        """Cache'den zimmet stok raporu al"""
        cache_key = RaporCacheService.get_zimmet_stok_raporu_cache_key(otel_id)
        return cache_get(cache_key)
    
    @staticmethod
    def set_zimmet_stok_raporu(data: dict, otel_id: int = None):
        """Zimmet stok raporunu cache'le"""
        cache_key = RaporCacheService.get_zimmet_stok_raporu_cache_key(otel_id)
        return cache_set(cache_key, data, RaporCacheService.ZIMMET_STOK_RAPORU_TTL)
    
    @staticmethod
    def invalidate_zimmet_stok_raporu(otel_id: int = None):
        """Zimmet stok raporu cache'ini temizle"""
        if otel_id:
            pattern = f"{RaporCacheService.CACHE_PREFIX}:zimmet_stok:{otel_id}"
        else:
            pattern = f"{RaporCacheService.CACHE_PREFIX}:zimmet_stok:*"
        
        deleted = cache_delete_pattern(pattern)
        logger.info(f"Zimmet stok raporu cache temizlendi: {deleted} key")
        return deleted
