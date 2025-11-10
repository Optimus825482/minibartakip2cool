#!/bin/bash
# Coolify Başlangıç Script'i
# Database bağlantısını kontrol eder ve uygulamayı başlatır

set -e  # Hata durumunda dur

echo "=========================================="
echo "🚀 Coolify Deployment Başlatılıyor..."
echo "=========================================="

# Environment variables kontrolü
echo "🔍 Environment variables kontrol ediliyor..."

if [ -z "$DATABASE_URL" ]; then
    echo "❌ HATA: DATABASE_URL tanımlı değil!"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    echo "❌ HATA: SECRET_KEY tanımlı değil!"
    exit 1
fi

echo "✅ Environment variables OK"

# Database bağlantı testi
echo ""
echo "🔍 Database bağlantısı test ediliyor..."

python3 << 'PYTHON_SCRIPT'
import os
import sys
from sqlalchemy import create_engine, text

try:
    database_url = os.getenv('DATABASE_URL')
    engine = create_engine(database_url, pool_pre_ping=True)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database bağlantısı başarılı!")
        sys.exit(0)
        
except Exception as e:
    print(f"❌ Database bağlantı hatası: {str(e)}")
    sys.exit(1)
PYTHON_SCRIPT

if [ $? -ne 0 ]; then
    echo ""
    echo "⏳ 10 saniye bekleniyor ve tekrar denenecek..."
    sleep 10
    
    # Tekrar dene
    python3 << 'PYTHON_SCRIPT'
import os
import sys
from sqlalchemy import create_engine, text

try:
    database_url = os.getenv('DATABASE_URL')
    engine = create_engine(database_url, pool_pre_ping=True)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database bağlantısı başarılı (2. deneme)!")
        sys.exit(0)
        
except Exception as e:
    print(f"❌ Database bağlantı hatası: {str(e)}")
    sys.exit(1)
PYTHON_SCRIPT
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ Database bağlantısı başarısız!"
        echo "🔧 Lütfen Coolify dashboard'dan database ayarlarını kontrol edin"
        exit 1
    fi
fi

# Database migration kontrolü
echo ""
echo "🔍 Database migration durumu kontrol ediliyor..."

if [ -d "migrations" ]; then
    echo "📦 Migration klasörü bulundu"
    
    # Alembic migration varsa çalıştır
    if command -v alembic &> /dev/null; then
        echo "🔄 Alembic migration çalıştırılıyor..."
        alembic upgrade head || echo "⚠️  Migration hatası (devam ediliyor)"
    fi
fi

# Gerekli dizinleri oluştur
echo ""
echo "📁 Gerekli dizinler oluşturuluyor..."
mkdir -p uploads xls backups static/uploads static/qr_codes
chmod -R 755 uploads xls backups static

echo "✅ Dizinler hazır"

# Uygulama başlatılıyor
echo ""
echo "=========================================="
echo "🚀 Uygulama Başlatılıyor..."
echo "=========================================="
echo ""
echo "📊 Konfigürasyon:"
echo "   - Workers: ${GUNICORN_WORKERS:-2}"
echo "   - Threads: ${GUNICORN_THREADS:-4}"
echo "   - Timeout: ${GUNICORN_TIMEOUT:-120}s"
echo "   - Port: ${PORT:-5000}"
echo ""

# Gunicorn ile başlat
exec gunicorn app:app \
    --bind 0.0.0.0:${PORT:-5000} \
    --workers ${GUNICORN_WORKERS:-2} \
    --threads ${GUNICORN_THREADS:-4} \
    --worker-class sync \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    --enable-stdio-inheritance
