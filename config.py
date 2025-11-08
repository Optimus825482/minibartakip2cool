import os
from datetime import timedelta

class Config:
    """Flask uygulama yapılandırması - GÜVENLİK İYİLEŞTİRMELERİ"""

    ENV = os.getenv('FLASK_ENV', os.getenv('ENV', 'production')).lower()
    IS_DEVELOPMENT = ENV in {'development', 'dev', 'local'}

    # Database Configuration - PostgreSQL & MySQL Support
    DATABASE_URL = os.getenv('DATABASE_URL')
    DB_TYPE = os.getenv('DB_TYPE', 'postgresql')  # 'postgresql' veya 'mysql'
    
    # PostgreSQL variables (Railway/Heroku)
    PGHOST = os.getenv('PGHOST')
    PGUSER = os.getenv('PGUSER')
    PGPASSWORD = os.getenv('PGPASSWORD')
    PGDATABASE = os.getenv('PGDATABASE')
    PGPORT = os.getenv('PGPORT', '5432')
    
    # MySQL variables (fallback - legacy support)
    MYSQLHOST = os.getenv('MYSQLHOST')
    MYSQLUSER = os.getenv('MYSQLUSER')
    MYSQLPASSWORD = os.getenv('MYSQLPASSWORD')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
    
    # Database URI Construction
    if DATABASE_URL:
        # Railway/Heroku DATABASE_URL kullan
        if DATABASE_URL.startswith('postgres://'):
            # Heroku postgres:// -> postgresql://
            SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('postgres://', 'postgresql://')
        elif DATABASE_URL.startswith('postgresql://'):
            SQLALCHEMY_DATABASE_URI = DATABASE_URL
        elif DATABASE_URL.startswith('mysql://'):
            SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('mysql://', 'mysql+pymysql://')
        else:
            SQLALCHEMY_DATABASE_URI = DATABASE_URL
    elif DB_TYPE == 'postgresql' and PGHOST and PGUSER:
        # PostgreSQL connection (Railway internal)
        SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}'
    elif DB_TYPE == 'mysql' and MYSQLHOST and MYSQLUSER:
        # MySQL connection (legacy)
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQLUSER}:{MYSQLPASSWORD}@{MYSQLHOST}:3306/{MYSQL_DATABASE}?charset=utf8mb4'
    else:
        # Local development için .env dosyasından oku
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_USER = os.getenv('DB_USER', 'postgres')
        DB_PASSWORD = os.getenv('DB_PASSWORD', '')
        DB_NAME = os.getenv('DB_NAME', 'minibar_takip')
        DB_PORT = os.getenv('DB_PORT', '5432')
        
        if DB_TYPE == 'postgresql':
            SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        else:
            # MySQL fallback
            SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}?charset=utf8mb4'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # PostgreSQL Optimized Engine Options - Railway Timeout Fix v2
    SQLALCHEMY_ENGINE_OPTIONS = {
        # Connection Pool Configuration - Railway cold start için agresif ayarlar
        'pool_size': 3,                     # Minimum connections (Railway için daha da düşürüldü)
        'max_overflow': 7,                  # Additional connections (total: 10)
        'pool_timeout': 120,                # Wait timeout 2 dakikaya çıkarıldı
        'pool_recycle': 1200,               # 20 dakikada bir recycle (Railway için)
        'pool_pre_ping': True,              # Health check before use (ZORUNLU)
        
        # PostgreSQL Specific Options
        'connect_args': {
            'connect_timeout': 90,          # Connection timeout 90 saniyeye çıkarıldı
            'options': '-c timezone=utc -c statement_timeout=60000',  # 60 saniye query timeout
            'application_name': 'minibar_takip',
            
            # Keep-alive settings - Railway için agresif
            'keepalives': 1,
            'keepalives_idle': 120,         # 120 saniye idle (2 dakika)
            'keepalives_interval': 20,      # 20 saniye interval
            'keepalives_count': 3,          # 3 deneme
            
            # TCP settings - timeout artırıldı
            'tcp_user_timeout': 90000,      # 90 saniye TCP timeout
        } if 'postgresql' in SQLALCHEMY_DATABASE_URI else {},
        
        # Execution Options
        'execution_options': {
            'isolation_level': 'READ COMMITTED'
        }
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
