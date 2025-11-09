#!/bin/bash
set -e

echo "=========================================="
echo "DOCKER CONTAINER BAŞLATILIYOR"
echo "=========================================="

# Database bağlantısını bekle
echo "[1/1] Database bağlantısı kontrol ediliyor..."
python -c "
import time
import sys
from app import app, db

max_retries = 30
retry_count = 0

with app.app_context():
    while retry_count < max_retries:
        try:
            db.engine.connect()
            print('✅ Database bağlantısı başarılı!')
            sys.exit(0)
        except Exception as e:
            retry_count += 1
            print(f'⏳ Database bekleniyor... ({retry_count}/{max_retries})')
            time.sleep(2)
    
    print('❌ Database bağlantısı kurulamadı!')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Database bağlantısı başarısız!"
    exit 1
fi

echo ""
echo "[2/2] Veritabanı tabloları kontrol ediliyor..."
python -c "
from app import app, db
from models import *

with app.app_context():
    try:
        # Tabloları oluştur
        db.create_all()
        print('✅ Veritabanı tabloları hazır!')
    except Exception as e:
        print(f'⚠️  Tablo oluşturma uyarısı: {e}')
        print('ℹ️  Devam ediliyor...')
"

echo ""
echo "=========================================="
echo "✅ HAZIRLIK TAMAMLANDI - UYGULAMA BAŞLIYOR"
echo "=========================================="
echo ""

# Uygulamayı başlat
exec "$@"
