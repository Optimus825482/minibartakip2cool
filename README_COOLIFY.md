# 🚀 Minibar Takip Sistemi - Coolify Deployment

Bu repo, Coolify platformunda deploy edilmek üzere optimize edilmiştir.

## 📦 Hızlı Başlangıç

### 1. Coolify'da Yeni Proje Oluştur

**Dashboard → Projects → Add Project**

```
Source: GitHub
Repository: Optimus825482/minibartakip2cool
Branch: main
Build Pack: Dockerfile
Dockerfile: ./Dockerfile.coolify
```

### 2. PostgreSQL Database Oluştur

**Dashboard → Resources → Add Resource → PostgreSQL**

```
Name: minibar-postgres
Version: 15
Database: minibar_takip
Username: minibar_user
Password: [güçlü şifre oluştur]
```

### 3. Environment Variables Ayarla

**Project → Environment Variables**

Aşağıdaki değişkenleri `.env.coolify` dosyasından kopyala:

```bash
# ZORUNLU
DATABASE_URL=postgresql://minibar_user:PASSWORD@minibar-postgres:5432/minibar_takip
DB_TYPE=postgresql
SECRET_KEY=[python3 -c "import secrets; print(secrets.token_urlsafe(32))"]
FLASK_ENV=production
PORT=5000

# OPSIYONEL
ML_ENABLED=true
TZ=Asia/Nicosia
```

### 4. Deploy Et

**Project → Deploy** butonuna tıkla ve logları izle.

### 5. Superadmin Oluştur

Deploy başarılı olduktan sonra:

```bash
docker exec -it [container-name] python create_superadmin_only.py
```

## 📚 Detaylı Dokümantasyon

- **[COOLIFY_KURULUM_REHBERI.md](COOLIFY_KURULUM_REHBERI.md)** - Adım adım kurulum rehberi
- **[COOLIFY_CHECKLIST.md](COOLIFY_CHECKLIST.md)** - Deployment checklist
- **[COOLIFY_COMMANDS.md](COOLIFY_COMMANDS.md)** - Hızlı komutlar ve cheat sheet

## 🔧 Özel Dosyalar

- `Dockerfile.coolify` - Coolify için optimize edilmiş Dockerfile
- `docker-compose.coolify.yml` - Referans docker-compose
- `.env.coolify` - Environment variables template
- `coolify_start.sh` - Başlangıç scripti
- `coolify_backup.sh` - Backup scripti
- `coolify_restore.sh` - Restore scripti
- `coolify_setup.sh` - Sunucu kurulum scripti

## 🌐 Erişim

Deploy sonrası:

```
URL: https://your-domain.com
veya
URL: http://your-server-ip:5000
```

## 💾 Backup

Otomatik backup için:

```bash
# Sunucuda çalıştır
chmod +x coolify_backup.sh
./coolify_backup.sh

# Cron job ekle
crontab -e
0 3 * * * /root/coolify_backup.sh >> /var/log/minibar_backup.log 2>&1
```

## 🔒 Güvenlik

- ✅ SECRET_KEY 32+ karakter olmalı
- ✅ Database şifresi güçlü olmalı
- ✅ HTTPS kullan (Coolify otomatik SSL)
- ✅ Firewall ayarlarını yap

## 📞 Destek

Sorun yaşarsan:

1. Logları kontrol et: `docker logs -f [container]`
2. Health check: `curl http://localhost:5000/health`
3. Database bağlantısı test et
4. [COOLIFY_COMMANDS.md](COOLIFY_COMMANDS.md) dosyasına bak

---

**Hazırlayan:** Erkan  
**Platform:** Coolify  
**Timezone:** Asia/Nicosia (Kıbrıs)  
**Versiyon:** 1.0
