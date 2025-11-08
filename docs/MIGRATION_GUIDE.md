# MySQL to PostgreSQL Migration Guide

## 🎯 Adım Adım Migration Rehberi

### 1️⃣ Docker Ortamını Hazırla

```bash
# MySQL ve PostgreSQL'i birlikte başlat (migration profili ile)
docker-compose --profile migration up -d

# Servislerin durumunu kontrol et
docker-compose ps

# Logları izle
docker-compose logs -f
```

**Beklenen Çıktı:**
- ✅ minibar_mysql (healthy)
- ✅ minibar_postgres (healthy)
- ✅ minibar_phpmyadmin (running)

### 2️⃣ MySQL Veritabanını Kontrol Et

```bash
# MySQL'e bağlan
docker exec -it minibar_mysql mysql -u minibar_user -pminibar123 minibar_takip

# Tabloları listele
SHOW TABLES;

# Örnek veri kontrolü
SELECT COUNT(*) FROM oteller;
SELECT COUNT(*) FROM kullanicilar;
SELECT COUNT(*) FROM urunler;

# Çıkış
exit
```

**Alternatif:** phpMyAdmin'den kontrol et
- URL: http://localhost:8081
- User: minibar_user
- Pass: minibar123

### 3️⃣ PostgreSQL Veritabanını Hazırla

```bash
# PostgreSQL'e bağlan
docker exec -it minibar_postgres psql -U minibar_user -d minibar_takip

# Mevcut tabloları kontrol et
\dt

# Çıkış
\q
```

**Eğer tablolar yoksa, Alembic migration çalıştır:**

```bash
# Alembic migration'ı çalıştır (schema oluştur)
alembic upgrade head
```

### 4️⃣ Migration Script'ini Çalıştır

```bash
# Python bağımlılıklarını kontrol et
pip install -r requirements.txt

# Migration script'ini çalıştır
python run_migration.py
```

**Script şunları yapacak:**
1. MySQL'den tüm tabloları okur
2. Verileri batch'ler halinde PostgreSQL'e aktarır
3. JSON → JSONB dönüşümü yapar
4. Timezone-aware datetime'lara çevirir
5. Sequence'leri günceller
6. Her tablo için checkpoint oluşturur
7. Veri doğrulama yapar

### 5️⃣ Migration Sonrası Kontroller

```bash
# PostgreSQL'de veri kontrolü
docker exec -it minibar_postgres psql -U minibar_user -d minibar_takip

# Row count karşılaştırması
SELECT 'oteller' as tablo, COUNT(*) FROM oteller
UNION ALL
SELECT 'kullanicilar', COUNT(*) FROM kullanicilar
UNION ALL
SELECT 'urunler', COUNT(*) FROM urunler
UNION ALL
SELECT 'stok_hareketleri', COUNT(*) FROM stok_hareketleri;

# JSONB kolonlarını kontrol et
SELECT id, islem_detay FROM sistem_loglari LIMIT 5;
SELECT id, eski_deger, yeni_deger FROM audit_logs LIMIT 5;

# Index'leri kontrol et
\di

# Çıkış
\q
```

### 6️⃣ Uygulama Konfigürasyonunu Güncelle

```bash
# .env dosyasını güncelle
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5433
DB_USER=minibar_user
DB_PASSWORD=minibar123
DB_NAME=minibar_takip
```

### 7️⃣ Flask Uygulamasını Test Et

```bash
# Uygulamayı başlat
python app.py

# Veya Docker ile
docker-compose up web
```

**Test endpoint'leri:**
- Health Check: http://localhost:5001/health
- Performance: http://localhost:5001/admin/performance

### 8️⃣ MySQL'i Durdur (Opsiyonel)

Migration başarılı olduktan sonra:

```bash
# MySQL container'ını durdur
docker-compose stop mysql

# Veya tamamen kaldır
docker-compose --profile migration down mysql
```

---

## 🔧 Troubleshooting

### Problem: MySQL bağlantı hatası

```bash
# MySQL container'ının çalıştığını kontrol et
docker-compose ps mysql

# MySQL loglarını kontrol et
docker-compose logs mysql

# MySQL'i yeniden başlat
docker-compose restart mysql
```

### Problem: PostgreSQL bağlantı hatası

```bash
# PostgreSQL container'ının çalıştığını kontrol et
docker-compose ps postgres

# PostgreSQL loglarını kontrol et
docker-compose logs postgres

# PostgreSQL'i yeniden başlat
docker-compose restart postgres
```

### Problem: Alembic migration hatası

```bash
# Alembic geçmişini kontrol et
alembic current

# Migration'ı sıfırla
alembic downgrade base

# Yeniden çalıştır
alembic upgrade head
```

### Problem: Port çakışması

```bash
# Kullanılan portları kontrol et
netstat -ano | findstr "3306"
netstat -ano | findstr "5433"

# docker-compose.yml'de portları değiştir
# Örnek: "3307:3306" veya "5434:5432"
```

---

## 📊 Migration Checkpoint Sistemi

Migration sırasında her tablo için checkpoint oluşturulur:

```json
// migration_checkpoint.json
[
  {
    "table": "oteller",
    "rows": 5,
    "timestamp": "2024-01-15T10:30:00Z"
  },
  {
    "table": "kullanicilar",
    "rows": 12,
    "timestamp": "2024-01-15T10:30:15Z"
  }
]
```

**Checkpoint'ten devam etmek için:**
- Script otomatik olarak checkpoint dosyasını okur
- Başarısız olan tablodan devam eder

---

## 🎯 Başarı Kriterleri

✅ Tüm tablolar migrate edildi
✅ Row count'lar eşleşiyor
✅ Foreign key ilişkileri korundu
✅ JSON → JSONB dönüşümü başarılı
✅ Timezone-aware datetime'lar
✅ Sequence'ler güncellendi
✅ Index'ler oluşturuldu
✅ Uygulama çalışıyor

---

## 📝 Notlar

- Migration sırasında MySQL read-only modda kalır
- PostgreSQL'e yazma işlemleri transaction içinde yapılır
- Hata durumunda otomatik rollback
- Checkpoint sistemi ile kaldığı yerden devam
- Validation otomatik olarak çalışır

