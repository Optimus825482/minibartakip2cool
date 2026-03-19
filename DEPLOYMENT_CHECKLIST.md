# Deployment Checklist - Performans ve Hata Düzeltmeleri

## Tarih: 19 Mart 2026

### ✅ Tamamlanan Düzeltmeler

#### 1. KRİTİK HATA: SQLAlchemy Import

- **Dosya**: `utils/executive_dashboard_service.py`
- **Değişiklik**: `from sqlalchemy.sql import text as sql_text` eklendi
- **Etki**: `get_hotel_comparison()` ve `get_task_completion_by_hotel()` fonksiyonları düzeltildi
- **Test**: `getDiagnostics` ile syntax kontrolü yapıldı ✅

#### 2. Redis Cache Sistemi

- **Yeni Dosyalar**:
  - `utils/cache_helper.py` - Genel cache fonksiyonları
  - `utils/executive_cache_service.py` - Executive dashboard cache
  - `utils/rapor_cache_service.py` - Rapor cache
- **Test**: Import ve syntax kontrolü yapıldı ✅

#### 3. Cache Entegrasyonu

- **Executive Dashboard Service**:
  - `get_kpi_summary()` - Cache eklendi (60s TTL)
  - `get_hotel_comparison()` - Cache eklendi (60s TTL)
- **Backward Compatible**: `use_cache=True` parametresi ile eski kod çalışmaya devam eder

### 🔄 Deployment Adımları

#### Ön Kontroller

1. ✅ Redis bağlantısı çalışıyor mu?

   ```bash
   redis-cli -u $REDIS_URL ping
   ```

2. ✅ Environment variables set mi?

   ```bash
   echo $REDIS_URL
   echo $CACHE_ENABLED  # true olmalı
   ```

3. ✅ Python dependencies yüklü mü?
   ```bash
   pip list | grep redis
   ```

#### Deployment Sırası

1. **Kod Deploy**:

   ```bash
   git add utils/cache_helper.py utils/executive_cache_service.py utils/rapor_cache_service.py
   git add utils/executive_dashboard_service.py
   git add PERFORMANCE_FIX_SUMMARY.md DEPLOYMENT_CHECKLIST.md
   git commit -m "fix: SQLAlchemy import hatası + Redis cache optimizasyonu"
   git push
   ```

2. **Application Restart**:

   ```bash
   # Coolify/Docker ortamında
   # Otomatik restart olacak veya manuel:
   docker-compose restart app
   ```

3. **Cache Warm-up** (opsiyonel):
   ```bash
   # İlk isteklerde cache miss olacak, bu normal
   # 1-2 dakika içinde cache dolacak
   ```

#### Post-Deployment Kontroller

1. **Hata Logları Kontrolü**:

   ```bash
   # Executive dashboard hatası olmamalı
   grep "name 'text' is not defined" logs/app.log
   # Sonuç: boş olmalı

   # Cache bağlantı hatası olmamalı
   grep "Redis cache kullanılamıyor" logs/app.log
   # İlk başta 1 kez görebilirsin (startup), sonra olmamalı
   ```

2. **Endpoint Response Time**:
   - Executive dashboard: <500ms (ilk istek), <100ms (cache hit)
   - Gün sonu raporu: <1000ms (ilk istek), <100ms (cache hit)

3. **Cache Hit Rate Monitoring**:

   ```bash
   # Redis'te key sayısını kontrol et
   redis-cli -u $REDIS_URL DBSIZE
   # executive:*, rapor:* key'leri olmalı

   redis-cli -u $REDIS_URL KEYS "executive:*"
   redis-cli -u $REDIS_URL KEYS "rapor:*"
   ```

### 🚨 Rollback Planı

Eğer bir sorun olursa:

1. **Cache'i Devre Dışı Bırak**:

   ```bash
   # .env dosyasında
   CACHE_ENABLED=false
   ```

   Restart gerekli.

2. **Eski Commit'e Dön**:

   ```bash
   git revert HEAD
   git push
   ```

3. **Manuel Cache Temizleme**:
   ```bash
   redis-cli -u $REDIS_URL FLUSHDB
   ```

### 📊 Monitoring Metrikleri

#### İzlenecek Metrikler (İlk 24 Saat)

- [ ] Executive dashboard response time < 500ms (P95)
- [ ] Gün sonu raporu response time < 1000ms (P95)
- [ ] Cache hit rate > 60% (hedef: 80%)
- [ ] Redis memory usage < 100MB
- [ ] Hata log'larında "text is not defined" yok

#### Alarm Eşikleri

- Response time > 1000ms (P95) → Cache TTL review
- Cache hit rate < 50% → Cache stratejisi review
- Redis memory > 200MB → Cache eviction policy review

### 📝 Notlar

- Cache invalidation otomatik değil, manuel temizleme gerekebilir
- İlk deployment'ta cache boş olacak, 1-2 dakika içinde dolacak
- Eski `cache_manager` kullanımı hala var, yavaş yavaş migrate edilecek
- Rate limiting eklenmedi (kullanıcı isteği üzerine)

### ✅ Sign-off

- [ ] Kod review yapıldı
- [ ] Syntax hataları kontrol edildi
- [ ] Redis bağlantısı test edildi
- [ ] Deployment planı onaylandı
- [ ] Rollback planı hazır

**Deployment Onayı**: ******\_\_\_****** (Tarih: **\_\_\_**)
