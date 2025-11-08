# 🚀 Docker Hızlı Başlangıç

## 5 Dakikada Çalıştır!

### Windows

```cmd
REM 1. Environment dosyasını hazırla
copy .env.docker .env

REM 2. .env dosyasını düzenle (Notepad ile)
notepad .env
REM SECRET_KEY ve DB_PASSWORD değiştir!

REM 3. Tek komutla başlat
docker.bat setup

REM 4. Tarayıcıda aç
start http://localhost:5000
```

### Linux/Mac

```bash
# 1. Environment dosyasını hazırla
cp .env.docker .env

# 2. .env dosyasını düzenle
nano .env  # veya vim .env
# SECRET_KEY ve DB_PASSWORD değiştir!

# 3. Tek komutla başlat
make setup

# 4. Tarayıcıda aç
open http://localhost:5000  # Mac
xdg-open http://localhost:5000  # Linux
```

## 🔑 İlk Giriş

- **Kullanıcı**: admin
- **Şifre**: admin123
- ⚠️ İlk girişte şifreyi değiştir!

## 📊 Yönetim Araçları

- **Ana Uygulama**: http://localhost:5000
- **phpMyAdmin**: http://localhost:8080
  - Kullanıcı: minibar_user
  - Şifre: .env dosyasındaki DB_PASSWORD

## 🛠️ Temel Komutlar

### Windows
```cmd
docker.bat start      REM Başlat
docker.bat stop       REM Durdur
docker.bat restart    REM Yeniden başlat
docker.bat logs       REM Logları göster
docker.bat status     REM Durum kontrol
docker.bat health     REM Health check
```

### Linux/Mac
```bash
make start      # Başlat
make stop       # Durdur
make restart    # Yeniden başlat
make logs       # Logları göster
make status     # Durum kontrol
make health     # Health check
```

## 🔧 Sorun mu Var?

```bash
# Logları kontrol et
docker-compose logs -f web

# Health check yap
curl http://localhost:5000/health

# Yeniden başlat
docker-compose restart
```

## 📚 Detaylı Dokümantasyon

- **Docker Kullanım Kılavuzu**: [DOCKER_KULLANIM.md](DOCKER_KULLANIM.md)
- **Genel Dokümantasyon**: [README.md](README.md)
- **Kullanım Kılavuzu**: [docs/](docs/)

## 💡 İpuçları

1. **Güvenlik**: .env dosyasındaki SECRET_KEY ve DB_PASSWORD'ü mutlaka değiştir
2. **Backup**: Düzenli backup al: `docker.bat backup` veya `make backup`
3. **Güncelleme**: Kod güncellemesi sonrası: `docker-compose up -d --build`
4. **Temizlik**: Disk doluysa: `docker system prune -a`

## ⚠️ Önemli Notlar

- İlk başlatmada MySQL'in hazır olması 30 saniye sürer
- Port 5000 ve 3306 kullanımda olmamalı
- Windows'ta Docker Desktop çalışıyor olmalı
- Linux'ta docker grubuna kullanıcı eklenmiş olmalı

---

**Hızlı Destek**: Sorun yaşıyorsan [DOCKER_KULLANIM.md](DOCKER_KULLANIM.md) dosyasındaki "Sorun Giderme" bölümüne bak!
