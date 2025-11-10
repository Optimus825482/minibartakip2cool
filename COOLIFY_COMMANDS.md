# 🚀 Coolify Hızlı Komutlar - Cheat Sheet

## 📦 Coolify Yönetimi

### Kurulum
```bash
# Coolify kur
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash

# Kurulum kontrolü
docker ps | grep coolify
```

### Coolify Servisi
```bash
# Durumu kontrol et
systemctl status coolify

# Başlat
systemctl start coolify

# Durdur
systemctl stop coolify

# Restart
systemctl restart coolify

# Logları izle
docker logs -f coolify
```

### Coolify Güncelleme
```bash
# Güncelleme kontrolü
cd /data/coolify/source
git pull

# Güncelle
docker compose up -d --force-recreate
```

---

## 🗄️ PostgreSQL Yönetimi

### Container Yönetimi
```bash
# Container'ı bul
docker ps | grep postgres

# Container'a gir
docker exec -it minibar-postgres bash

# PostgreSQL'e bağlan
docker exec -it minibar-postgres psql -U minibar_user -d minibar_takip
```

### Database İşlemleri
```bash
# Database listesi
docker exec -it minibar-postgres psql -U minibar_user -c "\l"

# Tablo listesi
docker exec -it minibar-postgres psql -U minibar_user -d minibar_takip -c "\dt"

# Database boyutu
docker exec -it minibar-postgres psql -U minibar_user -d minibar_takip -c "SELECT pg_size_pretty(pg_database_size('minibar_takip'));"

# Aktif bağlantılar
docker exec -it minibar-postgres psql -U minibar_user -d minibar_takip -c "SELECT * FROM pg_stat_activity;"
```

### Backup & Restore
```bash
# Manuel backup
docker exec minibar-postgres pg_dump -U minibar_user minibar_takip > backup_$(date +%Y%m%d).sql

# Backup'ı compress et
gzip backup_$(date +%Y%m%d).sql

# Restore
gunzip -c backup_20251110.sql.gz | docker exec -i minibar-postgres psql -U minibar_user -d minibar_takip

# Script ile backup
./coolify_backup.sh

# Script ile restore
./coolify_restore.sh
```

---

## 🐳 Uygulama Container Yönetimi

### Container İşlemleri
```bash
# Container'ı bul
docker ps | grep minibar

# Logları izle (real-time)
docker logs -f minibar-app

# Son 100 satır log
docker logs --tail 100 minibar-app

# Container'a gir
docker exec -it minibar-app bash

# Container restart
docker restart minibar-app

# Container durdur
docker stop minibar-app

# Container başlat
docker start minibar-app
```

### Resource Monitoring
```bash
# Tüm container'ların resource kullanımı
docker stats

# Belirli container
docker stats minibar-app

# Disk kullanımı
docker system df

# Container detayları
docker inspect minibar-app
```

### Health Check
```bash
# Health endpoint test
curl http://localhost:5000/health

# Detaylı health check
curl -v http://localhost:5000/health

# Response time ölç
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5000/health
```

---

## 🔧 Deployment İşlemleri

### Manuel Deploy
```bash
# Git pull ve rebuild
cd /path/to/app
git pull origin main
docker compose -f docker-compose.coolify.yml up -d --build

# Sadece restart (kod değişikliği yoksa)
docker compose -f docker-compose.coolify.yml restart web
```

### Environment Variables
```bash
# Container'daki env variables'ı gör
docker exec minibar-app env

# Belirli bir variable
docker exec minibar-app printenv DATABASE_URL

# .env dosyasını düzenle (Coolify dashboard'dan önerilir)
nano .env
```

### Migration İşlemleri
```bash
# Container içinde migration çalıştır
docker exec -it minibar-app alembic upgrade head

# Migration geçmişi
docker exec -it minibar-app alembic history

# Migration oluştur
docker exec -it minibar-app alembic revision --autogenerate -m "description"
```

---

## 🔍 Debugging ve Sorun Giderme

### Log Analizi
```bash
# Error logları filtrele
docker logs minibar-app 2>&1 | grep -i error

# Warning logları
docker logs minibar-app 2>&1 | grep -i warning

# Son 1 saatin logları
docker logs --since 1h minibar-app

# Belirli tarih aralığı
docker logs --since "2025-11-10T00:00:00" --until "2025-11-10T23:59:59" minibar-app
```

### Network Debugging
```bash
# Container network bilgisi
docker network inspect bridge

# Container IP adresi
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' minibar-app

# Port mapping
docker port minibar-app

# Network connectivity test
docker exec minibar-app ping -c 3 minibar-postgres
```

### Database Connection Test
```bash
# Python ile test
docker exec -it minibar-app python3 << 'EOF'
from sqlalchemy import create_engine
import os
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    result = conn.execute("SELECT 1")
    print("✅ Database bağlantısı başarılı!")
EOF

# psql ile test
docker exec -it minibar-app psql $DATABASE_URL -c "SELECT 1"
```

---

## 📊 Monitoring ve Performans

### System Resources
```bash
# CPU kullanımı
top -bn1 | grep "Cpu(s)"

# Memory kullanımı
free -h

# Disk kullanımı
df -h

# Disk I/O
iostat -x 1 5

# Network kullanımı
iftop -i eth0
```

### Application Metrics
```bash
# Gunicorn worker'ları
docker exec minibar-app ps aux | grep gunicorn

# Python process'leri
docker exec minibar-app ps aux | grep python

# Open files
docker exec minibar-app lsof | wc -l

# Database connections
docker exec minibar-postgres psql -U minibar_user -d minibar_takip -c "SELECT count(*) FROM pg_stat_activity;"
```

### Performance Testing
```bash
# Apache Bench (basit load test)
ab -n 1000 -c 10 http://localhost:5000/

# Response time test
time curl -s http://localhost:5000/ > /dev/null

# Concurrent requests
for i in {1..10}; do curl -s http://localhost:5000/ & done; wait
```

---

## 🔒 Güvenlik İşlemleri

### Firewall (UFW)
```bash
# Durum kontrol
ufw status

# Port aç
ufw allow 80/tcp
ufw allow 443/tcp

# Port kapat
ufw deny 8080/tcp

# Belirli IP'ye izin
ufw allow from 192.168.1.100

# Kuralları listele
ufw status numbered

# Kural sil
ufw delete [number]
```

### SSL/TLS
```bash
# Sertifika kontrolü
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Sertifika detayları
echo | openssl s_client -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates

# Let's Encrypt sertifika yenileme (Coolify otomatik yapar)
certbot renew --dry-run
```

### Security Scan
```bash
# Port scan
nmap -sV localhost

# Docker security scan
docker scan minibar-app

# Vulnerability check
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image minibar-app
```

---

## 💾 Backup ve Maintenance

### Otomatik Backup
```bash
# Cron job ekle
crontab -e

# Her gün 03:00'da backup
0 3 * * * /root/coolify_backup.sh >> /var/log/minibar_backup.log 2>&1

# Cron job'ları listele
crontab -l

# Backup loglarını kontrol et
tail -f /var/log/minibar_backup.log
```

### Cleanup İşlemleri
```bash
# Kullanılmayan Docker image'ları sil
docker image prune -a

# Kullanılmayan volume'ları sil
docker volume prune

# Kullanılmayan network'leri sil
docker network prune

# Tüm kullanılmayanları sil
docker system prune -a --volumes

# Eski logları temizle
truncate -s 0 /var/log/minibar_backup.log
```

### Database Maintenance
```bash
# Vacuum (optimize)
docker exec minibar-postgres psql -U minibar_user -d minibar_takip -c "VACUUM ANALYZE;"

# Reindex
docker exec minibar-postgres psql -U minibar_user -d minibar_takip -c "REINDEX DATABASE minibar_takip;"

# Database statistics
docker exec minibar-postgres psql -U minibar_user -d minibar_takip -c "SELECT schemaname, tablename, n_live_tup, n_dead_tup FROM pg_stat_user_tables;"
```

---

## 🚨 Acil Durum Komutları

### Hızlı Restart
```bash
# Sadece app restart
docker restart minibar-app

# Tüm servisler restart
docker compose -f docker-compose.coolify.yml restart

# Hard restart (stop + start)
docker compose -f docker-compose.coolify.yml down
docker compose -f docker-compose.coolify.yml up -d
```

### Acil Backup
```bash
# Hızlı database backup
docker exec minibar-postgres pg_dump -U minibar_user minibar_takip | gzip > emergency_backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Uploads backup
tar -czf emergency_uploads_$(date +%Y%m%d_%H%M%S).tar.gz /path/to/uploads
```

### Rollback
```bash
# Önceki image'a dön
docker tag minibar-app:latest minibar-app:backup
docker pull minibar-app:previous
docker compose -f docker-compose.coolify.yml up -d

# Git'te önceki commit'e dön
git log --oneline
git checkout [commit-hash]
docker compose -f docker-compose.coolify.yml up -d --build
```

---

## 📱 Hızlı Erişim URL'leri

```bash
# Coolify Dashboard
http://your-server-ip:8000

# Uygulama
http://your-server-ip:5000
https://minibar.yourdomain.com

# Health Check
curl http://localhost:5000/health

# Database (internal)
postgresql://minibar_user:password@minibar-postgres:5432/minibar_takip
```

---

## 🎯 Sık Kullanılan Kombinasyonlar

### Deploy ve Test
```bash
# Pull, build, restart, test
git pull && \
docker compose -f docker-compose.coolify.yml up -d --build && \
sleep 10 && \
curl http://localhost:5000/health
```

### Backup ve Cleanup
```bash
# Backup al, eski backupları temizle
./coolify_backup.sh && \
find /root/minibar_backups -name "*.gz" -mtime +7 -delete
```

### Log Monitoring
```bash
# Tüm container loglarını izle
docker compose -f docker-compose.coolify.yml logs -f
```

### Full System Check
```bash
# Sistem durumu özeti
echo "=== Docker Containers ===" && \
docker ps && \
echo -e "\n=== Disk Usage ===" && \
df -h && \
echo -e "\n=== Memory Usage ===" && \
free -h && \
echo -e "\n=== Health Check ===" && \
curl -s http://localhost:5000/health
```

---

**Hazırlayan:** Erkan  
**Tarih:** 2025-11-10  
**Versiyon:** 1.0

**Not:** Bu komutları kullanmadan önce production ortamında test etmeyi unutma!
