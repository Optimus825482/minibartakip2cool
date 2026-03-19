"""
Kat Sorumlusu Cache Service
Kat sorumlusu dashboard ve işlem endpoint'leri için cache yönetimi
"""

import logging
from utils.cache_helper import cache_get, cache_set, cache_delete_pattern

logger = logging.getLogger(__name__)


class KatSorumlusuCacheService:
    """Kat sorumlusu cache yönetimi"""
    
    CACHE_PREFIX = "kat_sorumlusu"
    
    # Cache süreleri (saniye)
    DASHBOARD_TTL = 30  # 30 saniye - sık güncellenen veriler
    MINIBAR_ISLEMLER_TTL = 60  # 1 dakika
    MINIBAR_URUNLER_TTL = 60  # 1 dakika
    DND_LISTE_TTL = 45  # 45 saniye
    ODA_SETUP_TTL = 300  # 5 dakika - nadiren değişir
    ZIMMET_URUNLER_TTL = 120  # 2 dakika
    ZIMMET_OZET_TTL = 120  # 2 dakika
    KRITIK_STOKLAR_TTL = 60  # 1 dakika
    
    # ✅ YENİ EKLENEN CACHE METODLARI
    @staticmethod
    def get_minibar_urunler_cache_key(kullanici_id: int):
        """Minibar ürünler cache key"""
        return f"{KatSorumlusuCacheService.CACHE_PREFIX}:minibar_urunler:{kullanici_id}"
    
    @staticmethod
    def get_minibar_urunler(kullanici_id: int):
        """Cache'den minibar ürünler al"""
        cache_key = KatSorumlusuCacheService.get_minibar_urunler_cache_key(kullanici_id)
        return cache_get(cache_key)
    
    @staticmethod
    def set_minibar_urunler(data: list, kullanici_id: int):
        """Minibar ürünleri cache'le"""
        cache_key = KatSorumlusuCacheService.get_minibar_urunler_cache_key(kullanici_id)
        return cache_set(cache_key, data, KatSorumlusuCacheService.MINIBAR_URUNLER_TTL)
    
    @staticmethod
    def get_zimmet_ozet_cache_key(kullanici_id: int):
        """Zimmet özet cache key"""
        return f"{KatSorumlusuCacheService.CACHE_PREFIX}:zimmet_ozet:{kullanici_id}"
    
    @staticmethod
    def get_zimmet_ozet(kullanici_id: int):
        """Cache'den zimmet özet al"""
        cache_key = KatSorumlusuCacheService.get_zimmet_ozet_cache_key(kullanici_id)
        return cache_get(cache_key)
    
    @staticmethod
    def set_zimmet_ozet(data: dict, kullanici_id: int):
        """Zimmet özetini cache'le"""
        cache_key = KatSorumlusuCacheService.get_zimmet_ozet_cache_key(kullanici_id)
        return cache_set(cache_key, data, KatSorumlusuCacheService.ZIMMET_OZET_TTL)
    
    @staticmethod
    def invalidate_minibar_urunler(kullanici_id: int):
        """Minibar ürünler cache'ini temizle"""
        pattern = f"{KatSorumlusuCacheService.CACHE_PREFIX}:minibar_urunler:{kullanici_id}"
        deleted = cache_delete_pattern(pattern)
        logger.info(f"Minibar ürünler cache temizlendi (kullanici={kullanici_id}): {deleted} key")
        return deleted
    
    @staticmethod
    def invalidate_zimmet_ozet(kullanici_id: int):
        """Zimmet özet cache'ini temizle"""
        pattern = f"{KatSorumlusuCacheService.CACHE_PREFIX}:zimmet_ozet:{kullanici_id}"
        deleted = cache_delete_pattern(pattern)
        logger.info(f"Zimmet özet cache temizlendi (kullanici={kullanici_id}): {deleted} key")
        return deleted
    
    @staticmethod
    def get_dashboard_cache_key(kullanici_id: int, tarih: str = None):
        """Dashboard cache key"""
        key = f"{KatSorumlusuCacheService.CACHE_PREFIX}:dashboard:{kullanici_id}"
        if tarih:
            key += f":{tarih}"
        return key
    
    @staticmethod
    def get_dashboard(kullanici_id: int, tarih: str = None):
        """Cache'den dashboard verisi al"""
        cache_key = KatSorumlusuCacheService.get_dashboard_cache_key(kullanici_id, tarih)
        return cache_get(cache_key)
    
    @staticmethod
    def set_dashboard(data: dict, kullanici_id: int, tarih: str = None):
        """Dashboard verisini cache'le"""
        cache_key = KatSorumlusuCacheService.get_dashboard_cache_key(kullanici_id, tarih)
        return cache_set(cache_key, data, KatSorumlusuCacheService.DASHBOARD_TTL)
    
    @staticmethod
    def get_minibar_islemler_cache_key(kullanici_id: int, tarih: str = None, 
                                        oda_no: str = None, islem_tipi: str = None):
        """Minibar işlemler cache key"""
        key = f"{KatSorumlusuCacheService.CACHE_PREFIX}:minibar:{kullanici_id}"
        if tarih:
            key += f":{tarih}"
        if oda_no:
            key += f":{oda_no}"
        if islem_tipi:
            key += f":{islem_tipi}"
        return key
    
    @staticmethod
    def get_minibar_islemler(kullanici_id: int, tarih: str = None, 
                             oda_no: str = None, islem_tipi: str = None):
        """Cache'den minibar işlemler al"""
        cache_key = KatSorumlusuCacheService.get_minibar_islemler_cache_key(
            kullanici_id, tarih, oda_no, islem_tipi
        )
        return cache_get(cache_key)
    
    @staticmethod
    def set_minibar_islemler(data: list, kullanici_id: int, tarih: str = None,
                             oda_no: str = None, islem_tipi: str = None):
        """Minibar işlemleri cache'le"""
        cache_key = KatSorumlusuCacheService.get_minibar_islemler_cache_key(
            kullanici_id, tarih, oda_no, islem_tipi
        )
        return cache_set(cache_key, data, KatSorumlusuCacheService.MINIBAR_ISLEMLER_TTL)
    
    @staticmethod
    def get_dnd_liste_cache_key(otel_id: int, tarih: str = None, sadece_aktif: bool = False):
        """DND liste cache key"""
        key = f"{KatSorumlusuCacheService.CACHE_PREFIX}:dnd:{otel_id}"
        if tarih:
            key += f":{tarih}"
        if sadece_aktif:
            key += ":aktif"
        return key
    
    @staticmethod
    def get_dnd_liste(otel_id: int, tarih: str = None, sadece_aktif: bool = False):
        """Cache'den DND liste al"""
        cache_key = KatSorumlusuCacheService.get_dnd_liste_cache_key(otel_id, tarih, sadece_aktif)
        return cache_get(cache_key)
    
    @staticmethod
    def set_dnd_liste(data: list, otel_id: int, tarih: str = None, sadece_aktif: bool = False):
        """DND listesini cache'le"""
        cache_key = KatSorumlusuCacheService.get_dnd_liste_cache_key(otel_id, tarih, sadece_aktif)
        return cache_set(cache_key, data, KatSorumlusuCacheService.DND_LISTE_TTL)
    
    @staticmethod
    def get_oda_setup_cache_key(oda_id: int):
        """Oda setup cache key"""
        return f"{KatSorumlusuCacheService.CACHE_PREFIX}:oda_setup:{oda_id}"
    
    @staticmethod
    def get_oda_setup(oda_id: int):
        """Cache'den oda setup al"""
        cache_key = KatSorumlusuCacheService.get_oda_setup_cache_key(oda_id)
        return cache_get(cache_key)
    
    @staticmethod
    def set_oda_setup(data: dict, oda_id: int):
        """Oda setup'ı cache'le"""
        cache_key = KatSorumlusuCacheService.get_oda_setup_cache_key(oda_id)
        return cache_set(cache_key, data, KatSorumlusuCacheService.ODA_SETUP_TTL)
    
    @staticmethod
    def get_zimmet_urunler_cache_key(kullanici_id: int):
        """Zimmet ürünler cache key"""
        return f"{KatSorumlusuCacheService.CACHE_PREFIX}:zimmet:{kullanici_id}"
    
    @staticmethod
    def get_zimmet_urunler(kullanici_id: int):
        """Cache'den zimmet ürünler al"""
        cache_key = KatSorumlusuCacheService.get_zimmet_urunler_cache_key(kullanici_id)
        return cache_get(cache_key)
    
    @staticmethod
    def set_zimmet_urunler(data: list, kullanici_id: int):
        """Zimmet ürünleri cache'le"""
        cache_key = KatSorumlusuCacheService.get_zimmet_urunler_cache_key(kullanici_id)
        return cache_set(cache_key, data, KatSorumlusuCacheService.ZIMMET_URUNLER_TTL)
    
    @staticmethod
    def get_kritik_stoklar_cache_key(kullanici_id: int):
        """Kritik stoklar cache key"""
        return f"{KatSorumlusuCacheService.CACHE_PREFIX}:kritik_stok:{kullanici_id}"
    
    @staticmethod
    def get_kritik_stoklar(kullanici_id: int):
        """Cache'den kritik stoklar al"""
        cache_key = KatSorumlusuCacheService.get_kritik_stoklar_cache_key(kullanici_id)
        return cache_get(cache_key)
    
    @staticmethod
    def set_kritik_stoklar(data: dict, kullanici_id: int):
        """Kritik stokları cache'le"""
        cache_key = KatSorumlusuCacheService.get_kritik_stoklar_cache_key(kullanici_id)
        return cache_set(cache_key, data, KatSorumlusuCacheService.KRITIK_STOKLAR_TTL)
    
    @staticmethod
    def invalidate_kullanici(kullanici_id: int):
        """Kullanıcıya ait tüm cache'i temizle"""
        pattern = f"{KatSorumlusuCacheService.CACHE_PREFIX}:*:{kullanici_id}*"
        deleted = cache_delete_pattern(pattern)
        logger.info(f"Kat sorumlusu cache temizlendi (kullanici={kullanici_id}): {deleted} key")
        return deleted
    
    @staticmethod
    def invalidate_otel(otel_id: int):
        """Otele ait tüm cache'i temizle"""
        pattern = f"{KatSorumlusuCacheService.CACHE_PREFIX}:*:{otel_id}*"
        deleted = cache_delete_pattern(pattern)
        logger.info(f"Kat sorumlusu cache temizlendi (otel={otel_id}): {deleted} key")
        return deleted
    
    @staticmethod
    def invalidate_minibar(kullanici_id: int):
        """Minibar işlem cache'ini temizle"""
        pattern = f"{KatSorumlusuCacheService.CACHE_PREFIX}:minibar:{kullanici_id}*"
        deleted = cache_delete_pattern(pattern)
        logger.info(f"Minibar cache temizlendi (kullanici={kullanici_id}): {deleted} key")
        return deleted
    
    @staticmethod
    def invalidate_dnd(otel_id: int):
        """DND cache'ini temizle"""
        pattern = f"{KatSorumlusuCacheService.CACHE_PREFIX}:dnd:{otel_id}*"
        deleted = cache_delete_pattern(pattern)
        logger.info(f"DND cache temizlendi (otel={otel_id}): {deleted} key")
        return deleted
    
    @staticmethod
    def invalidate_oda_setup(oda_id: int):
        """Oda setup cache'ini temizle"""
        pattern = f"{KatSorumlusuCacheService.CACHE_PREFIX}:oda_setup:{oda_id}"
        deleted = cache_delete_pattern(pattern)
        logger.info(f"Oda setup cache temizlendi (oda={oda_id}): {deleted} key")
        return deleted
