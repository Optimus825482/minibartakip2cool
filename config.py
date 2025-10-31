import os
from datetime import timedelta

class Config:
    """Flask uygulama yapılandırması - GÜVENLİK İYİLEŞTİRMELERİ"""

    ENV = os.getenv('FLASK_ENV', os.getenv('ENV', 'production')).lower()
    IS_DEVELOPMENT = ENV in {'development', 'dev', 'local'}

    # Railway DATABASE_URL öncelikli (mysql:// -> mysql+pymysql://)
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Railway MySQL variables (fallback)
    MYSQLHOST = os.getenv('MYSQLHOST')
    MYSQLUSER = os.getenv('MYSQLUSER')
    MYSQLPASSWORD = os.getenv('MYSQLPASSWORD')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
    
    if DATABASE_URL and DATABASE_URL.startswith('mysql://'):
        # Railway DATABASE_URL kullan
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('mysql://', 'mysql+pymysql://')
    elif MYSQLHOST and MYSQLUSER:
        # Railway MySQL variables kullan (internal connection)
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQLUSER}:{MYSQLPASSWORD}@{MYSQLHOST}:3306/{MYSQL_DATABASE}?charset=utf8mb4'
    else:
        # Local development için .env dosyasından oku
        DB_HOST = os.getenv('DB_HOST', os.getenv('MYSQL_HOST', 'localhost'))
        DB_USER = os.getenv('DB_USER', os.getenv('MYSQL_USER', 'root'))
        DB_PASSWORD = os.getenv('DB_PASSWORD', os.getenv('MYSQL_PASSWORD', ''))
        DB_NAME = os.getenv('DB_NAME', os.getenv('MYSQL_DB', 'minibar_takip'))
        DB_PORT = os.getenv('DB_PORT', os.getenv('MYSQL_PORT', '3306'))
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20,
        'pool_timeout': 30  # GÜVENLİK: Connection timeout eklendi
    }
    
    # Flask ayarları - GÜVENLİK İYİLEŞTİRMELERİ
    SECRET_KEY = os.getenv('SECRET_KEY')

    if not SECRET_KEY:
        if IS_DEVELOPMENT:
            SECRET_KEY = 'development-secret-key-change-in-production'
        else:
            raise ValueError("SECRET_KEY environment variable is required. Set a strong secret key in production.")

    if not IS_DEVELOPMENT and len(SECRET_KEY) < 32:
        raise ValueError("SECRET_KEY must be at least 32 characters long for security.")
    
    # Oturum ayarları - GÜVENLİK: Session güvenliği artırıldı
    SESSION_COOKIE_SECURE = not IS_DEVELOPMENT  # Development'ta HTTP'ye izin ver, prod'da zorunlu kıl
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'  # 'Strict' önerilen ama 'Lax' uyumluluk için
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)  # 1 saatten 30 dakikaya düşürüldü
    
    # WTF Forms ayarları - GÜVENLİK
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 saat CSRF token timeout
    WTF_CSRF_HEADERS = ['X-CSRFToken', 'X-CSRF-Token']
    
    # Dosya yükleme ayarları - GÜVENLİK
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB - güvenlik için sınırlandırıldı
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'pdf'}  # Güvenli dosya türleri
    
    # GÜVENLİK HEADERS - Production için önerilen
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; img-src 'self' data: https:; connect-src 'self'",
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'  # HTTPS için
    }
