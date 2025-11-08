# Railway PostgreSQL Timeout Fix v2

## Sorun
Railway'de PostgreSQL bağlantısı timeout veriyor:
- Connection timeout (66+ saniye)
- Cold start sorunları
- Network latency

## Uygulanan Çözümler

### 1. Config.py - Database Engine Ayarları

**Değişiklikler:**
- `pool_size`: 5 → 3 (daha az connection)
- `max_overflow`: 10 → 7 (total: 10 connection)
- `pool_timeout`: 60 → 120 saniye (2 dakika)
- `pool_recycle`: 1800 → 1200 saniye (20 dakika)
- `connect_timeout`: 30 → 90 saniye
- `keepalives_idle`: 60 → 120 saniye
- `keepalives_interval`: 10 → 20 saniye
- `keepalives_count`: 5 → 3
- `tcp_user_timeout`: 30000 → 90000 ms (90 saniye)
- `statement_timeout`: 30000 → 60000 ms (60 saniye)

**Mantık:**
- Daha az connection = daha az overhead
- Daha uzun timeout = cold start'a izin ver
- Agresif keep-alive = connection'ı canlı tut

### 2. App.py - Retry Mekanizması

**Değişiklikler:**
- `max_retries`: 3 → 5 deneme
- `retry_delay`: 2 → 5 saniye başlangıç
- Exponential backoff: 5, 10, 20, 40 saniye
- Connection'ı açıp kapatma (test için)
- Hata durumunda uygulama çalışmaya devam eder

### 3. Railway_start.sh - Gunicorn Ayarları

**Değişiklikler:**
- `workers`: 2 → 1 (tek worker)
- `threads`: 4 → 2 (daha az thread)
- `timeout`: 120 → 180 saniye
- `graceful-timeout`: 180 saniye eklendi
- `keep-alive`: 5 → 10 saniye
- `max-requests`: 1000 → 500
- `--preload` eklendi (app'i önceden yükle)

**Mantık:**
- Tek worker = daha az DB connection
- Uzun timeout = cold start'a izin ver
- Preload = startup'ta hazır ol

### 4. Railway_health_check.py - Health Check

**Değişiklikler:**
- `max_retries`: 5 → 7 deneme
- `retry_delay`: 2 → 5 saniye başlangıç
- Exponential backoff: 5, 10, 20, 40, 80, 160 saniye
- Daha detaylı logging
- Connection ayarları config.py ile uyumlu

## Test Etme

1. **Railway'e Deploy Et:**
```bash
git add .
git commit -m "fix: Railway PostgreSQL timeout v2"
git push railway main
```

2. **Logları İzle:**
```bash
railway logs
```

3. **Beklenen Çıktı:**
```
🔍 Database bağlantısı test ediliyor...
🔌 Bağlantı kuruluyor... (Deneme 1/7)
✅ Database bağlantısı başarılı! (Deneme 1/7)
```

## Sorun Devam Ederse

### Senaryo 1: Hala Timeout
- Railway dashboard'dan database'i restart et
- `PGHOST` değişkenini kontrol et (internal mi external mi?)
- Railway'in private networking'ini kullan

### Senaryo 2: Connection Limit
- Railway plan'ını kontrol et (connection limit?)
- `pool_size` ve `max_overflow`'u daha da düşür

### Senaryo 3: Network Problemi
- Railway status page'i kontrol et
- Database region'ı kontrol et
- Farklı region'a migrate et

## Monitoring

Railway dashboard'dan kontrol et:
- Database CPU kullanımı
- Connection sayısı
- Query performance
- Network latency

## Notlar

- Bu ayarlar **cold start** için optimize edildi
- Production'da traffic artarsa worker/thread sayısını artır
- Database connection pool'u ihtiyaca göre ayarla
- Keep-alive ayarları Railway network'üne göre optimize edildi
