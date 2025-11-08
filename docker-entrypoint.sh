#!/bin/bash
set -e

echo "=========================================="
echo "DOCKER CONTAINER BAŞLATILIYOR"
echo "=========================================="

# Database bağlantısını bekle
echo "[1/3] Database bağlantısı kontrol ediliyor..."
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

# Migration'ları uygula
echo ""
echo "[2/3] Database migration'ları uygulanıyor..."
python apply_multi_hotel_migration.py

if [ $? -ne 0 ]; then
    echo "⚠️  Migration hatası! Devam ediliyor..."
fi

# Veri migrasyonunu uygula
echo ""
echo "[3/3] Veri migrasyonu uygulanıyor..."
python migrate_to_multi_hotel.py

if [ $? -ne 0 ]; then
    echo "⚠️  Veri migrasyonu hatası! Devam ediliyor..."
fi

echo ""
echo "=========================================="
echo "✅ HAZIRLIK TAMAMLANDI - UYGULAMA BAŞLIYOR"
echo "=========================================="
echo ""

# Uygulamayı başlat
exec "$@"
