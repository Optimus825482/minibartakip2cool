# ✅ Coolify Deployment Checklist

## 📋 Kurulum Öncesi

- [ ] Sunucu hazır (Ubuntu 20.04+, min 2GB RAM)
- [ ] Domain satın alındı (opsiyonel)
- [ ] SSH erişimi var
- [ ] Git repository hazır

## 🔧 Sunucu Kurulumu

### 1. Sunucuya Bağlan
```bash
ssh root@your-server-ip
```

### 2. Coolify Kur
```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

### 3. Firewall Ayarla
```bash
ufw enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
```

### 4. Coolify Dashboard'a Giriş
```
http://your-server-ip:8000
```

- [ ] İlk kullanıcı oluşturuldu
- [ ] 2FA aktif edildi
- [ ] Email ayarları yapıldı (opsiyonel)

## 🗄️ Database Kurulumu

### PostgreSQL Oluştur

**Dashboard → Resources → Add Resource → PostgreSQL**

```
Name: minibar-postgres
Version: 15
Database: minibar_takip
Username: minibar_user
Password: [güçlü şifre]
Port: 5432
```

- [ ] PostgreSQL oluşturuldu
- [ ] Connection string kaydedildi
- [ ] Health check başarılı

**Connection String:**
```
postgresql://minibar_user:password@minibar-postgres:5432/minibar_takip
```

## 🚀 Uygulama Deployment

### 1. Git Repository Bağla

**Dashboard → Projects → Add Project**

```
Source: GitHub
Repository: your-username/minibar-takip
Branch: main
Build Pack: Dockerfile
Dockerfile: ./Dockerfile.coolify
```

- [ ] Repository bağlandı
- [ ] Branch seçildi
- [ ] Dockerfile tanımlandı

### 2. Port Ayarları

```
Container Port: 5000
Public Port: 80 (veya 443 SSL ile)
```

- [ ] Port ayarları yapıldı

### 3. Health Check

```
Path: /health
Interval: 30s
Timeout: 10s
```

- [ ] Health check ayarlandı

## 🔐 Environment Variables

**Project → Environment Variables → Add**

### Zorunlu Variables:

```bash
DATABASE_URL=postgresql://minibar_user:password@minibar-postgres:5432/minibar_takip
DB_TYPE=postgresql
SECRET_KEY=[32+ karakter random string]
FLASK_ENV=production
PORT=5000
```

- [ ] DATABASE_URL eklendi
- [ ] SECRET_KEY oluşturuldu ve eklendi
- [ ] FLASK_ENV=production ayarlandı

### SECRET_KEY Oluştur:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Opsiyonel Variables:

```bash
ML_ENABLED=true
ML_DATA_COLLECTION_INTERVAL=900
ML_ANOMALY_CHECK_INTERVAL=300
BACKUP_DIR=/app/backups
TZ=Europe/Istanbul
```

- [ ] ML ayarları eklendi (opsiyonel)
- [ ] Timezone ayarlandı

## 🌐 Domain ve SSL (Opsiyonel)

### 1. Domain Ekle

**Project → Domains → Add Domain**

```
Domain: minibar.yourdomain.com
```

- [ ] Domain eklendi

### 2. DNS Ayarları

Domain sağlayıcıda:

```
Type: A Record
Name: minibar
Value: your-server-ip
TTL: 3600
```

- [ ] DNS ayarları yapıldı
- [ ] DNS propagation beklendi (5-30 dakika)

### 3. SSL Aktif Et

```
✅ SSL/TLS: Enabled
✅ Force HTTPS: Enabled
```

- [ ] SSL otomatik oluşturuldu
- [ ] HTTPS zorunlu kılındı

## 🚀 İlk Deploy

### Deploy Et

**Project → Deploy**

- [ ] Build başlatıldı
- [ ] Build başarılı
- [ ] Container çalışıyor
- [ ] Health check başarılı

### Logları Kontrol Et

```bash
# Coolify dashboard'dan
Project → Logs → Real-time

# Veya sunucuda
docker logs -f [container-name]
```

- [ ] Loglar kontrol edildi
- [ ] Hata yok

## 👤 Superadmin Oluştur

### Sunucuda Çalıştır:

```bash
# Container'a gir
docker exec -it [container-name] bash

# Superadmin oluştur
python create_superadmin_only.py
```

- [ ] Superadmin oluşturuldu
- [ ] Giriş test edildi

## 💾 Backup Kurulumu

### 1. Database Backup (Otomatik)

**Database → Backups → Configure**

```
Frequency: Daily
Retention: 7 days
Time: 03:00 AM
```

- [ ] Otomatik backup ayarlandı

### 2. Manual Backup Script

Sunucuya `coolify_backup.sh` yükle:

```bash
# Script'i çalıştırılabilir yap
chmod +x coolify_backup.sh

# Test et
./coolify_backup.sh
```

- [ ] Backup script yüklendi
- [ ] Test edildi

### 3. Cron Job Ekle

```bash
crontab -e
```

Ekle:
```bash
# Her gün saat 03:00'da backup al
0 3 * * * /root/coolify_backup.sh >> /var/log/minibar_backup.log 2>&1
```

- [ ] Cron job eklendi
- [ ] Log dosyası oluşturuldu

## 🔒 Güvenlik Kontrolleri

### SSH Güvenliği

```bash
# SSH config düzenle
nano /etc/ssh/sshd_config

# Değiştir:
PasswordAuthentication no
PermitRootLogin prohibit-password

# Restart
systemctl restart sshd
```

- [ ] SSH key-based auth aktif
- [ ] Password auth kapalı
- [ ] Root login kısıtlı

### Database Güvenliği

- [ ] Güçlü şifre kullanıldı (16+ karakter)
- [ ] Database external'a expose edilmedi
- [ ] Backup stratejisi kuruldu

### Application Güvenliği

- [ ] SECRET_KEY güçlü (32+ karakter)
- [ ] HTTPS aktif (production için)
- [ ] CSRF protection aktif
- [ ] Rate limiting aktif

## 📊 Monitoring

### 1. Uygulama Logları

```bash
# Real-time logs
docker logs -f [container-name]

# Son 100 satır
docker logs --tail 100 [container-name]
```

- [ ] Log monitoring kuruldu

### 2. Resource Monitoring

```bash
# Container stats
docker stats

# Disk kullanımı
df -h

# Memory kullanımı
free -h
```

- [ ] Resource monitoring kuruldu

### 3. Uptime Monitoring (Opsiyonel)

Harici servisler:
- UptimeRobot
- Pingdom
- StatusCake

- [ ] Uptime monitoring kuruldu (opsiyonel)

## ✅ Final Kontroller

### Uygulama Testi

- [ ] Ana sayfa açılıyor
- [ ] Login çalışıyor
- [ ] Database bağlantısı OK
- [ ] File upload çalışıyor
- [ ] QR kod oluşturma çalışıyor
- [ ] ML sistem çalışıyor (varsa)

### Performance Testi

```bash
# Response time test
curl -w "@curl-format.txt" -o /dev/null -s https://your-domain.com

# Load test (opsiyonel)
ab -n 1000 -c 10 https://your-domain.com/
```

- [ ] Response time < 2s
- [ ] Load test başarılı

### Backup Testi

```bash
# Backup al
./coolify_backup.sh

# Restore test et (test ortamında)
./coolify_restore.sh
```

- [ ] Backup başarılı
- [ ] Restore test edildi

## 🎉 Deployment Tamamlandı!

### Erişim Bilgileri

```
URL: https://minibar.yourdomain.com
veya
URL: http://your-server-ip

Superadmin:
Email: [email]
Password: [password]
```

### Dokümantasyon

- [ ] Erişim bilgileri kaydedildi
- [ ] Backup prosedürü dokümante edildi
- [ ] Sorun giderme notları alındı

### Takım Bilgilendirmesi

- [ ] Takıma deployment bilgisi verildi
- [ ] Kullanıcı hesapları oluşturuldu
- [ ] Eğitim verildi (gerekirse)

---

## 📞 Destek

**Sorun mu yaşıyorsun?**

1. Logları kontrol et: `docker logs -f [container]`
2. Health check: `curl http://localhost:5000/health`
3. Database bağlantısı: `docker exec -it postgres psql -U minibar_user`
4. Coolify docs: https://coolify.io/docs

---

**Hazırlayan:** Erkan  
**Tarih:** 2025-11-10  
**Versiyon:** 1.0
