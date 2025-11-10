# 🚀 Coolify Kurulum Rehberi - Minibar Takip Sistemi

## 📋 İçindekiler
1. [Ön Hazırlık](#ön-hazırlık)
2. [Coolify Kurulumu](#coolify-kurulumu)
3. [PostgreSQL Database Kurulumu](#postgresql-database-kurulumu)
4. [Uygulama Deployment](#uygulama-deployment)
5. [Environment Variables](#environment-variables)
6. [Domain ve SSL](#domain-ve-ssl)
7. [Backup Stratejisi](#backup-stratejisi)
8. [Sorun Giderme](#sorun-giderme)

---

## 🎯 Ön Hazırlık

### Gereksinimler
- **Sunucu**: Ubuntu 20.04+ / Debian 11+ (Minimum 2GB RAM, 2 CPU, 20GB Disk)
- **Domain**: Opsiyonel (IP ile de çalışır)
- **Git Repository**: GitHub/GitLab/Bitbucket hesabı

### Önerilen Sunucu Özellikleri
```
Minimum:  2GB RAM, 2 vCPU, 20GB SSD
Önerilen: 4GB RAM, 2 vCPU, 40GB SSD
Optimal:  8GB RAM, 4 vCPU, 80GB SSD
```

---

## 🔧 Coolify Kurulumu

### 1. Sunucuya Bağlan
```bash
ssh root@your-server-ip
```

### 2. Coolify'ı Kur (Tek Komut)
```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

### 3. Kurulum Kontrolü
```bash
# Coolify durumunu kontrol et
docker ps | grep coolify

# Coolify loglarını izle
docker logs -f coolify
```

### 4. Coolify Dashboard'a Eriş
```
http://your-server-ip:8000
```

**İlk Giriş:**
- Email ve şifre oluştur
- 2FA aktif et (önerilen)

---

## 🗄️ PostgreSQL Database Kurulumu

### Yöntem 1: Coolify Üzerinden (Önerilen)

1. **Dashboard → Resources → Add Resource**
2. **Database → PostgreSQL** seç
3. **Ayarlar:**
   ```
   Name: minibar-postgres
   Version: 15 (önerilen)
   Database Name: minibar_takip
   Username: minibar_user
   Password: [güçlü şifre oluştur]
   Port: 5432 (internal)
   ```

4. **Deploy** butonuna tıkla

5. **Connection String'i Kaydet:**
   ```
   postgresql://minibar_user:password@minibar-postgres:5432/minibar_takip
   ```

### Yöntem 2: External PostgreSQL (Supabase, Neon, vb.)

Eğer harici PostgreSQL kullanacaksan:
```
postgresql://user:pass@external-host:5432/dbname
```

---

## 🚀 Uygulama Deployment

### 1. Git Repository Bağla

**Dashboard → Projects → Add Project**

```
Source: GitHub/GitLab
Repository: your-username/minibar-takip
Branch: main
```

### 2. Build Pack Seçimi

**Dockerfile** kullanacağız (zaten mevcut):
```
Build Pack: Dockerfile
Dockerfile Location: ./Dockerfile
```

### 3. Port Ayarları

```
Port: 5000 (container içi)
Public Port: 80 veya 443 (SSL ile)
```

### 4. Health Check

```
Health Check Path: /health
Health Check Interval: 30s
Health Check Timeout: 10s
```

---

## 🔐 Environment Variables

### Coolify Dashboard'da Ayarla

**Project → Environment Variables → Add**

#### Zorunlu Variables:

```bash
# Database Configuration
DATABASE_URL=postgresql://minibar_user:password@minibar-postgres:5432/minibar_takip
DB_TYPE=postgresql

# Flask Configuration
SECRET_KEY=[32+ karakter güçlü key - aşağıda oluştur]
FLASK_ENV=production

# Port (Coolify otomatik ayarlar)
PORT=5000
```

#### Opsiyonel Variables:

```bash
# ML System
ML_ENABLED=true
ML_DATA_COLLECTION_INTERVAL=900
ML_ANOMALY_CHECK_INTERVAL=300
ML_TRAINING_SCHEDULE=0 0 * * *
ML_MIN_DATA_POINTS=100
ML_ACCURACY_THRESHOLD=0.85

# Backup
BACKUP_DIR=/app/backups
```

### SECRET_KEY Oluşturma

Sunucuda çalıştır:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Veya online:
```bash
openssl rand -base64 32
```

---

## 🌐 Domain ve SSL

### 1. Domain Bağlama

**Project → Domains → Add Domain**

```
Domain: minibar.yourdomain.com
```

### 2. DNS Ayarları

Domain sağlayıcında (GoDaddy, Cloudflare, vb.):

```
Type: A Record
Name: minibar (veya @)
Value: your-server-ip
TTL: 3600
```

### 3. SSL Sertifikası (Otomatik)

Coolify otomatik Let's Encrypt sertifikası oluşturur:
```
✅ SSL/TLS: Enabled
✅ Force HTTPS: Enabled
```

---

## 💾 Backup Stratejisi

### 1. Database Backup (Otomatik)

Coolify PostgreSQL için otomatik backup:

**Database → Backups → Configure**
```
Frequency: Daily
Retention: 7 days
Time: 03:00 AM
```

### 2. Manual Backup Script

Sunucuda çalıştır:
```bash
# PostgreSQL backup
docker exec minibar-postgres pg_dump -U minibar_user minibar_takip > backup_$(date +%Y%m%d).sql

# Uploads backup
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz /path/to/uploads
```

### 3. Cron Job Ekle

```bash
crontab -e
```

Ekle:
```bash
# Her gün saat 03:00'da backup al
0 3 * * * /root/backup_script.sh
```

---

## 🔍 Deployment Adımları (Özet)

### Hızlı Başlangıç

1. **Coolify Kur**
   ```bash
   curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
   ```

2. **PostgreSQL Oluştur**
   - Dashboard → Add Resource → PostgreSQL
   - Connection string'i kaydet

3. **Git Repository Bağla**
   - Dashboard → Add Project → GitHub
   - Repository seç

4. **Environment Variables Ekle**
   ```
   DATABASE_URL=postgresql://...
   SECRET_KEY=...
   FLASK_ENV=production
   ```

5. **Deploy**
   - Build & Deploy butonuna tıkla
   - Logları izle

6. **Domain Bağla (Opsiyonel)**
   - DNS ayarla
   - SSL otomatik aktif olur

---

## 🐛 Sorun Giderme

### 1. Build Hatası

**Log Kontrolü:**
```bash
# Coolify dashboard'dan Build Logs'a bak
# Veya sunucuda:
docker logs -f [container-name]
```

**Yaygın Sorunlar:**
- ❌ `requirements.txt` eksik → Dosya var mı kontrol et
- ❌ Port çakışması → Port 5000 kullanılıyor mu?
- ❌ Memory yetersiz → Sunucu RAM'ini artır

### 2. Database Bağlantı Hatası

**Kontrol:**
```bash
# PostgreSQL çalışıyor mu?
docker ps | grep postgres

# Connection test
docker exec -it minibar-postgres psql -U minibar_user -d minibar_takip
```

**Çözüm:**
- DATABASE_URL doğru mu?
- PostgreSQL container çalışıyor mu?
- Network ayarları doğru mu?

### 3. 502 Bad Gateway

**Sebep:** Uygulama başlamadı

**Kontrol:**
```bash
# Health check
curl http://localhost:5000/health

# Logs
docker logs -f [app-container]
```

**Çözüm:**
- Gunicorn timeout artır
- Worker sayısını azalt
- Memory kontrol et

### 4. Static Files Yüklenmiyor

**Nginx Ayarı:**
```nginx
location /static {
    alias /app/static;
    expires 30d;
}
```

### 5. Upload Klasörü Yazma Hatası

**Permission Fix:**
```bash
docker exec -it [container] chmod -R 755 /app/uploads
docker exec -it [container] chown -R appuser:appuser /app/uploads
```

---

## 📊 Monitoring ve Logs

### 1. Uygulama Logları

**Coolify Dashboard:**
```
Project → Logs → Real-time
```

**Sunucuda:**
```bash
docker logs -f [container-name]
docker logs --tail 100 [container-name]
```

### 2. Database Logları

```bash
docker logs -f minibar-postgres
```

### 3. Resource Monitoring

```bash
# CPU, Memory kullanımı
docker stats

# Disk kullanımı
df -h
```

---

## 🔒 Güvenlik Önerileri

### 1. Firewall Ayarları

```bash
# UFW aktif et
ufw enable

# Sadece gerekli portları aç
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 8000/tcp  # Coolify Dashboard
```

### 2. SSH Güvenliği

```bash
# SSH key-based auth kullan
# Password auth'u kapat
nano /etc/ssh/sshd_config

# Değiştir:
PasswordAuthentication no
PermitRootLogin prohibit-password

# Restart
systemctl restart sshd
```

### 3. Database Güvenliği

- ✅ Güçlü şifreler kullan (16+ karakter)
- ✅ Database'i external'a expose etme
- ✅ Regular backup al
- ✅ SSL/TLS kullan

### 4. Application Güvenliği

- ✅ SECRET_KEY'i güçlü tut
- ✅ HTTPS zorunlu kıl
- ✅ Rate limiting aktif
- ✅ CSRF protection aktif

---

## 📈 Performans Optimizasyonu

### 1. Gunicorn Ayarları

Coolify'da environment variable ekle:
```bash
GUNICORN_WORKERS=2
GUNICORN_THREADS=4
GUNICORN_TIMEOUT=120
```

### 2. PostgreSQL Tuning

```sql
-- Connection pool
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';

-- Restart gerekli
```

### 3. Nginx Caching

Coolify otomatik nginx kullanır, static cache için:
```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

---

## 🎉 Deployment Tamamlandı!

### Kontrol Listesi

- ✅ Coolify kuruldu
- ✅ PostgreSQL çalışıyor
- ✅ Uygulama deploy edildi
- ✅ Environment variables ayarlandı
- ✅ Health check başarılı
- ✅ Domain bağlandı (opsiyonel)
- ✅ SSL aktif (opsiyonel)
- ✅ Backup stratejisi kuruldu

### İlk Giriş

```
URL: https://minibar.yourdomain.com
veya
URL: http://your-server-ip

Superadmin oluştur:
python create_superadmin_only.py
```

---

## 📞 Destek ve Kaynaklar

- **Coolify Docs**: https://coolify.io/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Flask Docs**: https://flask.palletsprojects.com/

---

**Hazırlayan:** Erkan  
**Tarih:** 2025-11-10  
**Versiyon:** 1.0
