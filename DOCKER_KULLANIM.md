# 🐳 Docker Kullanım Kılavuzu - Minibar Takip Sistemi

## 📋 İçindekiler
1. [Gereksinimler](#gereksinimler)
2. [Hızlı Başlangıç](#hızlı-başlangıç)
3. [Detaylı Kurulum](#detaylı-kurulum)
4. [Kullanım](#kullanım)
5. [Yönetim Komutları](#yönetim-komutları)
6. [Sorun Giderme](#sorun-giderme)

---

## 🔧 Gereksinimler

### Sistem Gereksinimleri
- **Docker**: 20.10 veya üzeri
- **Docker Compose**: 2.0 veya üzeri
- **RAM**: Minimum 2GB (Önerilen 4GB)
- **Disk**: Minimum 5GB boş alan

### Docker Kurulumu

#### Windows
```bash
# Docker Desktop indir ve kur
https://www.docker.com/products/docker-desktop/

# Kurulum sonrası kontrol
docker --version
docker-compose --version
```

#### Linux (Ubuntu/Debian)
```bash
# Docker kurulumu
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose kurulumu
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Kullanıcıyı docker grubuna ekle
sudo usermod -aG docker $USER
newgrp docker

# Kontrol
docker --version
docker compose version
```

#### macOS
```bash
# Docker Desktop indir ve kur
https://www.docker.com/products/docker-desktop/

# Homebrew ile alternatif
brew install --cask docker
```

---

## 🚀 Hızlı Başlangıç

### 1. Environment Dosyasını Hazırla
```bash
# .env.docker dosyasını .env olarak kopyala
cp .env.docker .env

# .env dosyasını düzenle (ÖNEMLİ!)
# - SECRET_KEY değiştir (minimum 32 karakter)
# - DB_PASSWORD değiştir
# - Diğer ayarları ihtiyaca göre düzenle
```

### 2. Uygulamayı Başlat
```bash
# Tüm servisleri başlat (MySQL + Flask + phpMyAdmin)
docker-compose up -d

# Sadece MySQL ve Flask (phpMyAdmin olmadan)
docker-compose up -d web
```

### 3. Database'i Başlat
```bash
# İlk kurulumda database'i oluştur
docker-compose exec web python init_db.py

# Superadmin kullanıcısı oluştur
docker-compose exec web python add_local_superadmin.py
```

### 4. Uygulamaya Eriş
- **Ana Uygulama**: http://localhost:5000
- **phpMyAdmin**: http://localhost:8080 (opsiyonel)

---

## 📦 Detaylı Kurulum

### Adım 1: Projeyi Hazırla
```bash
# Proje dizinine git
cd /path/to/minibar-takip

# Gerekli dizinleri oluştur
mkdir -p uploads xls static
```

### Adım 2: Environment Yapılandırması
```bash
# .env dosyasını oluştur
cp .env.docker .env

# Güvenli SECRET_KEY oluştur (Python ile)
python -c "import secrets; print(secrets.token_hex(32))"

# .env dosyasını düzenle
nano .env  # veya notepad .env (Windows)
```

**Önemli .env Ayarları:**
```env
# GÜVENLİK: Bu değerleri mutlaka değiştir!
SECRET_KEY=buraya-python-ile-olusturdugun-64-karakterlik-key-yaz
DB_PASSWORD=guclu-bir-sifre-123456

# Opsiyonel ayarlar
FLASK_ENV=production
DB_NAME=minibar_takip
DB_USER=minibar_user
PORT=5000
```

### Adım 3: Docker Image'ları İndir ve Başlat
```bash
# Image'ları indir (ilk seferde biraz zaman alır)
docker-compose pull

# Container'ları oluştur ve başlat
docker-compose up -d

# Logları takip et (sorun varsa)
docker-compose logs -f
```

### Adım 4: Database Kurulumu
```bash
# MySQL'in hazır olmasını bekle (30 saniye)
sleep 30

# Database tablolarını oluştur
docker-compose exec web python init_db.py

# Superadmin kullanıcısı ekle
docker-compose exec web python add_local_superadmin.py
# Kullanıcı adı: admin
# Şifre: admin123 (ilk girişte değiştir!)
```

### Adım 5: Kontrol
```bash
# Container'ların durumunu kontrol et
docker-compose ps

# Health check
curl http://localhost:5000/health

# Logları kontrol et
docker-compose logs web
docker-compose logs db
```

---

## 💻 Kullanım

### Container Yönetimi

#### Başlatma
```bash
# Tüm servisleri başlat
docker-compose up -d

# Sadece belirli servisi başlat
docker-compose up -d web
docker-compose up -d db

# Logları görerek başlat (debug için)
docker-compose up
```

#### Durdurma
```bash
# Tüm servisleri durdur
docker-compose stop

# Belirli servisi durdur
docker-compose stop web
docker-compose stop db
```

#### Yeniden Başlatma
```bash
# Tüm servisleri yeniden başlat
docker-compose restart

# Belirli servisi yeniden başlat
docker-compose restart web
```

#### Kapatma (Container'ları sil)
```bash
# Container'ları durdur ve sil
docker-compose down

# Container'ları + Volume'ları sil (DİKKAT: Tüm data silinir!)
docker-compose down -v

# Container'ları + Image'ları sil
docker-compose down --rmi all
```

### Log Yönetimi

```bash
# Tüm logları göster
docker-compose logs

# Belirli servisin loglarını göster
docker-compose logs web
docker-compose logs db

# Canlı log takibi (tail -f gibi)
docker-compose logs -f web

# Son 100 satır
docker-compose logs --tail=100 web

# Zaman damgalı loglar
docker-compose logs -t web
```

### Container İçinde Komut Çalıştırma

```bash
# Python shell
docker-compose exec web python

# Flask shell
docker-compose exec web flask shell

# Bash shell
docker-compose exec web bash

# MySQL shell
docker-compose exec db mysql -u root -p

# Database backup
docker-compose exec db mysqldump -u root -p minibar_takip > backup.sql

# Database restore
docker-compose exec -T db mysql -u root -p minibar_takip < backup.sql
```

### Güncelleme ve Yeniden Build

```bash
# Kod değişikliği sonrası yeniden build
docker-compose build web

# Build ve başlat
docker-compose up -d --build

# Cache kullanmadan build (temiz build)
docker-compose build --no-cache web
```

---

## 🛠️ Yönetim Komutları

### Database Yönetimi

```bash
# Database tablolarını oluştur
docker-compose exec web python init_db.py

# Superadmin ekle
docker-compose exec web python add_local_superadmin.py

# Database şemasını kontrol et
docker-compose exec web python check_db_schema.py

# Tabloları listele
docker-compose exec web python list_tables.py

# MySQL backup
docker-compose exec db mysqldump -u root -p${DB_PASSWORD} minibar_takip > backup_$(date +%Y%m%d_%H%M%S).sql

# MySQL restore
docker-compose exec -T db mysql -u root -p${DB_PASSWORD} minibar_takip < backup.sql
```

### phpMyAdmin Kullanımı

```bash
# phpMyAdmin'i başlat
docker-compose --profile tools up -d phpmyadmin

# Erişim
# URL: http://localhost:8080
# Sunucu: db
# Kullanıcı: minibar_user (veya .env'deki DB_USER)
# Şifre: .env'deki DB_PASSWORD

# phpMyAdmin'i durdur
docker-compose stop phpmyadmin
```

### Sistem Bilgileri

```bash
# Container durumları
docker-compose ps

# Container kaynak kullanımı
docker stats

# Disk kullanımı
docker system df

# Network bilgileri
docker network ls
docker network inspect minibar_network

# Volume bilgileri
docker volume ls
docker volume inspect minibar_takip_mysql_data
```

### Temizlik İşlemleri

```bash
# Kullanılmayan container'ları temizle
docker container prune

# Kullanılmayan image'ları temizle
docker image prune

# Kullanılmayan volume'ları temizle (DİKKAT!)
docker volume prune

# Tüm kullanılmayan kaynakları temizle
docker system prune -a
```

---

## 🔍 Sorun Giderme

### Container Başlamıyor

```bash
# Logları kontrol et
docker-compose logs web
docker-compose logs db

# Container durumunu kontrol et
docker-compose ps

# Port çakışması kontrolü
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Linux/Mac

# Yeniden başlat
docker-compose down
docker-compose up -d
```

### Database Bağlantı Hatası

```bash
# MySQL'in hazır olup olmadığını kontrol et
docker-compose exec db mysqladmin ping -h localhost -u root -p

# MySQL loglarını kontrol et
docker-compose logs db

# Database'e manuel bağlan
docker-compose exec db mysql -u root -p

# Health check
curl http://localhost:5000/health
```

### Port Zaten Kullanımda

```bash
# .env dosyasında portu değiştir
PORT=5001
PHPMYADMIN_PORT=8081

# Yeniden başlat
docker-compose down
docker-compose up -d
```

### Yavaş Çalışma

```bash
# Kaynak kullanımını kontrol et
docker stats

# Container'ları yeniden başlat
docker-compose restart

# Docker Desktop ayarlarından RAM/CPU artır
# Settings > Resources > Advanced
```

### Volume Sorunları

```bash
# Volume'ları listele
docker volume ls

# Volume'u incele
docker volume inspect minibar_takip_mysql_data

# Volume'u sil ve yeniden oluştur (DİKKAT: Tüm data silinir!)
docker-compose down -v
docker-compose up -d
```

### Build Hataları

```bash
# Cache'siz build
docker-compose build --no-cache

# Detaylı build log
docker-compose build --progress=plain

# Dockerfile syntax kontrolü
docker build --check .
```

### Genel Sorunlar

#### "Permission Denied" Hatası (Linux)
```bash
# Docker grubuna kullanıcı ekle
sudo usermod -aG docker $USER
newgrp docker
```

#### "Cannot connect to Docker daemon"
```bash
# Docker servisini başlat
sudo systemctl start docker  # Linux
# Docker Desktop'ı başlat     # Windows/Mac
```

#### "No space left on device"
```bash
# Disk kullanımını kontrol et
docker system df

# Temizlik yap
docker system prune -a
```

---

## 📊 Production Deployment

### Güvenlik Kontrol Listesi

- [ ] SECRET_KEY değiştirildi (minimum 32 karakter)
- [ ] DB_PASSWORD güçlü bir şifre
- [ ] FLASK_ENV=production
- [ ] phpMyAdmin production'da kapalı
- [ ] Firewall kuralları ayarlandı
- [ ] SSL/TLS sertifikası eklendi (Nginx/Traefik ile)
- [ ] Backup stratejisi oluşturuldu
- [ ] Log rotation ayarlandı

### Nginx Reverse Proxy (Opsiyonel)

```nginx
# /etc/nginx/sites-available/minibar
server {
    listen 80;
    server_name minibar.example.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Otomatik Backup Script

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

docker-compose exec -T db mysqldump -u root -p${DB_PASSWORD} minibar_takip > ${BACKUP_DIR}/minibar_${DATE}.sql

# 7 günden eski backupları sil
find ${BACKUP_DIR} -name "minibar_*.sql" -mtime +7 -delete
```

---

## 📞 Destek

Sorun yaşıyorsan:
1. Logları kontrol et: `docker-compose logs -f`
2. Health check yap: `curl http://localhost:5000/health`
3. Container durumunu kontrol et: `docker-compose ps`
4. Bu dokümandaki sorun giderme bölümüne bak

---

**Not**: Bu kılavuz Docker ile local development ve production deployment için hazırlanmıştır. Railway deployment için `RAILWAY_DEPLOYMENT_GUIDE.md` dosyasına bakın.
