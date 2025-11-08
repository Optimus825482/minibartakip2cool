#!/bin/bash
# Railway Başlangıç Script'i
# Database bağlantısını kontrol eder ve uygulamayı başlatır

echo "=========================================="
echo "🚀 Railway Deployment Başlatılıyor..."
echo "=========================================="

# Health check çalıştır
echo "🔍 Database bağlantısı kontrol ediliyor..."
python railway_health_check.py

if [ $? -eq 0 ]; then
    echo "✅ Database bağlantısı başarılı!"
    
    # Migration'ları uygula
    echo ""
    echo "📦 Database migration'ları uygulanıyor..."
    python apply_multi_hotel_migration.py
    
    if [ $? -ne 0 ]; then
        echo "⚠️  Migration hatası! Devam ediliyor..."
    fi
    
    # Veri migrasyonunu uygula
    echo ""
    echo "📊 Veri migrasyonu uygulanıyor..."
    python migrate_to_multi_hotel.py
    
    if [ $? -ne 0 ]; then
        echo "⚠️  Veri migrasyonu hatası! Devam ediliyor..."
    fi
    
    echo ""
    echo "🚀 Uygulama başlatılıyor..."
    
    # Gunicorn ile uygulamayı başlat
    # Railway için optimize edilmiş ayarlar - v3 (ultra agresif)
    exec gunicorn app:app \
        --bind 0.0.0.0:$PORT \
        --workers 1 \
        --threads 1 \
        --worker-class sync \
        --timeout 300 \
        --graceful-timeout 300 \
        --keep-alive 5 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --worker-tmp-dir /dev/shm \
        --access-logfile - \
        --error-logfile - \
        --log-level info
else
    echo "❌ Database bağlantısı başarısız!"
    echo "⏳ 10 saniye bekleniyor ve tekrar denenecek..."
    sleep 10
    
    # Tekrar dene
    python railway_health_check.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Database bağlantısı başarılı (2. deneme)!"
        
        # Migration'ları uygula
        echo ""
        echo "📦 Database migration'ları uygulanıyor..."
        python apply_multi_hotel_migration.py
        
        if [ $? -ne 0 ]; then
            echo "⚠️  Migration hatası! Devam ediliyor..."
        fi
        
        # Veri migrasyonunu uygula
        echo ""
        echo "📊 Veri migrasyonu uygulanıyor..."
        python migrate_to_multi_hotel.py
        
        if [ $? -ne 0 ]; then
            echo "⚠️  Veri migrasyonu hatası! Devam ediliyor..."
        fi
        
        echo ""
        echo "🚀 Uygulama başlatılıyor..."
        
        exec gunicorn app:app \
            --bind 0.0.0.0:$PORT \
            --workers 1 \
            --threads 1 \
            --worker-class sync \
            --timeout 300 \
            --graceful-timeout 300 \
            --keep-alive 5 \
            --max-requests 1000 \
            --max-requests-jitter 100 \
            --worker-tmp-dir /dev/shm \
            --access-logfile - \
            --error-logfile - \
            --log-level info
    else
        echo "❌ Database bağlantısı hala başarısız!"
        echo "🔧 Lütfen Railway dashboard'dan database ayarlarını kontrol edin"
        exit 1
    fi
fi
