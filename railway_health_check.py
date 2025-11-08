#!/usr/bin/env python3
"""
Railway Health Check Script
Database bağlantısını kontrol eder ve sorunları tespit eder
"""

import os
import sys
import time
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, TimeoutError

# Logging ayarla
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_database_url():
    """Database URL'ini environment variable'lardan al"""
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Heroku postgres:// -> postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://')
        return database_url
    
    # Railway internal variables
    pghost = os.getenv('PGHOST')
    pguser = os.getenv('PGUSER')
    pgpassword = os.getenv('PGPASSWORD')
    pgdatabase = os.getenv('PGDATABASE')
    pgport = os.getenv('PGPORT', '5432')
    
    if pghost and pguser:
        return f'postgresql+psycopg2://{pguser}:{pgpassword}@{pghost}:{pgport}/{pgdatabase}'
    
    logger.error("❌ Database URL bulunamadı!")
    return None

def test_connection(max_retries=7, retry_delay=5):
    """Database bağlantısını test et - v2 agresif retry"""
    database_url = get_database_url()
    
    if not database_url:
        return False
    
    logger.info(f"🔍 Database bağlantısı test ediliyor...")
    logger.info(f"📍 Host: {os.getenv('PGHOST', 'N/A')}")
    logger.info(f"📍 Port: {os.getenv('PGPORT', 'N/A')}")
    logger.info(f"📍 Database: {os.getenv('PGDATABASE', 'N/A')}")
    
    for attempt in range(max_retries):
        try:
            # Engine oluştur - Railway cold start için agresif ayarlar
            engine = create_engine(
                database_url,
                pool_size=1,
                max_overflow=2,
                pool_timeout=120,
                pool_recycle=1200,
                pool_pre_ping=True,
                connect_args={
                    'connect_timeout': 90,
                    'keepalives': 1,
                    'keepalives_idle': 120,
                    'keepalives_interval': 20,
                    'keepalives_count': 3,
                    'tcp_user_timeout': 90000,
                }
            )
            
            # Bağlantıyı test et
            logger.info(f"🔌 Bağlantı kuruluyor... (Deneme {attempt + 1}/{max_retries})")
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
                
            logger.info(f"✅ Database bağlantısı başarılı! (Deneme {attempt + 1}/{max_retries})")
            engine.dispose()
            return True
            
        except (OperationalError, TimeoutError) as e:
            error_msg = str(e)[:300]
            logger.warning(f"⚠️ Bağlantı hatası (Deneme {attempt + 1}/{max_retries}): {error_msg}")
            
            if attempt < max_retries - 1:
                # Exponential backoff: 5, 10, 20, 40, 80 saniye
                wait_time = retry_delay * (2 ** attempt)
                logger.info(f"🔄 {wait_time} saniye sonra tekrar denenecek...")
                time.sleep(wait_time)
            else:
                logger.error(f"❌ Database bağlantısı {max_retries} denemeden sonra başarısız!")
                logger.error(f"❌ Son hata: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Beklenmeyen hata: {str(e)}")
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                logger.info(f"🔄 {wait_time} saniye sonra tekrar denenecek...")
                time.sleep(wait_time)
            else:
                return False
    
    return False

def main():
    """Ana fonksiyon"""
    logger.info("=" * 60)
    logger.info("🚀 Railway Database Health Check")
    logger.info("=" * 60)
    
    success = test_connection()
    
    if success:
        logger.info("=" * 60)
        logger.info("✅ Health Check BAŞARILI!")
        logger.info("=" * 60)
        sys.exit(0)
    else:
        logger.error("=" * 60)
        logger.error("❌ Health Check BAŞARISIZ!")
        logger.error("=" * 60)
        sys.exit(1)

if __name__ == '__main__':
    main()
