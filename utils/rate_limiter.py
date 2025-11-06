"""
Rate Limiter Servisi
QR kod okutma ve diğer işlemler için rate limiting
"""

from datetime import datetime, timedelta
from collections import defaultdict
from threading import Lock


class RateLimiter:
    """
    IP bazlı rate limiting servisi
    Production ortamında Redis kullanılması önerilir
    """
    
    # IP bazlı rate limit cache
    _cache = defaultdict(list)
    _lock = Lock()  # Thread-safe işlemler için
    
    @staticmethod
    def check_rate_limit(ip_address, max_attempts=10, window_minutes=1):
        """
        Rate limit kontrolü yap
        
        Args:
            ip_address (str): Kontrol edilecek IP adresi
            max_attempts (int): İzin verilen maksimum deneme sayısı
            window_minutes (int): Zaman penceresi (dakika)
            
        Returns:
            bool: True ise izin ver, False ise reddet
        """
        with RateLimiter._lock:
            now = datetime.utcnow()
            window_start = now - timedelta(minutes=window_minutes)
            
            # Eski kayıtları temizle
            RateLimiter._cache[ip_address] = [
                timestamp for timestamp in RateLimiter._cache[ip_address]
                if timestamp > window_start
            ]
            
            # Limit kontrolü
            if len(RateLimiter._cache[ip_address]) >= max_attempts:
                return False
            
            # Yeni denemeyi kaydet
            RateLimiter._cache[ip_address].append(now)
            return True
    
    @staticmethod
    def get_remaining_attempts(ip_address, max_attempts=10, window_minutes=1):
        """
        Kalan deneme hakkını getir
        
        Args:
            ip_address (str): IP adresi
            max_attempts (int): Maksimum deneme sayısı
            window_minutes (int): Zaman penceresi (dakika)
            
        Returns:
            int: Kalan deneme hakkı
        """
        with RateLimiter._lock:
            now = datetime.utcnow()
            window_start = now - timedelta(minutes=window_minutes)
            
            # Eski kayıtları temizle
            RateLimiter._cache[ip_address] = [
                timestamp for timestamp in RateLimiter._cache[ip_address]
                if timestamp > window_start
            ]
            
            current_attempts = len(RateLimiter._cache[ip_address])
            remaining = max(0, max_attempts - current_attempts)
            
            return remaining
    
    @staticmethod
    def reset_limit(ip_address):
        """
        Belirli bir IP için rate limit'i sıfırla
        
        Args:
            ip_address (str): Sıfırlanacak IP adresi
        """
        with RateLimiter._lock:
            if ip_address in RateLimiter._cache:
                del RateLimiter._cache[ip_address]
    
    @staticmethod
    def clear_all():
        """
        Tüm rate limit cache'ini temizle
        Test ve bakım amaçlı
        """
        with RateLimiter._lock:
            RateLimiter._cache.clear()
    
    @staticmethod
    def get_cache_stats():
        """
        Cache istatistiklerini getir
        
        Returns:
            dict: İstatistik bilgileri
        """
        with RateLimiter._lock:
            total_ips = len(RateLimiter._cache)
            total_attempts = sum(len(attempts) for attempts in RateLimiter._cache.values())
            
            return {
                'total_ips': total_ips,
                'total_attempts': total_attempts,
                'cache_size': len(RateLimiter._cache)
            }


class QRRateLimiter:
    """
    QR kod işlemleri için özelleştirilmiş rate limiter
    """
    
    # QR işlemleri için varsayılan limitler
    QR_SCAN_LIMIT = 10  # Dakikada 10 okutma
    QR_SCAN_WINDOW = 1  # 1 dakika
    
    QR_GENERATE_LIMIT = 50  # Dakikada 50 oluşturma
    QR_GENERATE_WINDOW = 1  # 1 dakika
    
    @staticmethod
    def check_qr_scan_limit(ip_address):
        """
        QR okutma rate limit kontrolü
        
        Args:
            ip_address (str): IP adresi
            
        Returns:
            bool: True ise izin ver, False ise reddet
        """
        return RateLimiter.check_rate_limit(
            ip_address,
            max_attempts=QRRateLimiter.QR_SCAN_LIMIT,
            window_minutes=QRRateLimiter.QR_SCAN_WINDOW
        )
    
    @staticmethod
    def check_qr_generate_limit(ip_address):
        """
        QR oluşturma rate limit kontrolü
        
        Args:
            ip_address (str): IP adresi
            
        Returns:
            bool: True ise izin ver, False ise reddet
        """
        return RateLimiter.check_rate_limit(
            ip_address,
            max_attempts=QRRateLimiter.QR_GENERATE_LIMIT,
            window_minutes=QRRateLimiter.QR_GENERATE_WINDOW
        )
    
    @staticmethod
    def get_qr_scan_remaining(ip_address):
        """
        QR okutma için kalan deneme hakkı
        
        Args:
            ip_address (str): IP adresi
            
        Returns:
            int: Kalan deneme hakkı
        """
        return RateLimiter.get_remaining_attempts(
            ip_address,
            max_attempts=QRRateLimiter.QR_SCAN_LIMIT,
            window_minutes=QRRateLimiter.QR_SCAN_WINDOW
        )
