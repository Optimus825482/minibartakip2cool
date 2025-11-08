# Railway Deployment Checklist

## Pre-Deployment

### 1. Environment Variables (Railway Dashboard)
- [ ] `SECRET_KEY` ayarlandı mı? (en az 32 karakter)
- [ ] `FLASK_ENV=production` ayarlandı mı?
- [ ] `ENV=production` ayarlandı mı?
- [ ] Database variables otomatik sağlanıyor mu? (PGHOST, PGUSER, etc.)

### 2. Local Test
```bash
# Config'i test et
python test_db_connection.py

# Health check'i test et (Railway variables ile)
python railway_health_check.py
```

### 3. Code Review
- [ ] `config.py` - timeout ayarları güncellendi
- [ ] `app.py` - retry mekanizması güncellendi
- [ ] `railway_start.sh` - gunicorn ayarları güncellendi
- [ ] `railway_health_check.py` - health check güncellendi

## Deployment

### 1. Git Push
```bash
git add .
git commit -m "fix: Railway PostgreSQL timeout v2 - agresif retry ve connection pool"
git push railway main
```

### 2. Railway Logs İzle
```bash
railway logs --follow
```

### 3. Beklenen Log Çıktısı
```
🔍 Database bağlantısı test ediliyor...
📍 Host: shinkansen.proxy.rlwy.net
📍 Port: 36747
📍 Database: railway
🔌 Bağlantı kuruluyor... (Deneme 1/7)
✅ Database bağlantısı başarılı! (Deneme 1/7)
✅ Health Check BAŞARILI!
📦 Database migration'ları uygulanıyor...
🚀 Uygulama başlatılıyor...
[INFO] Booting worker with pid: X
```

## Post-Deployment

### 1. Health Check
```bash
# Railway URL'ini test et
curl https://your-app.railway.app/health

# Beklenen response:
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "..."
}
```

### 2. Database Connection Test
- [ ] Login sayfası açılıyor mu?
- [ ] Database'e bağlanabiliyor mu?
- [ ] Query'ler çalışıyor mu?

### 3. Performance Monitoring
Railway Dashboard'dan kontrol et:
- [ ] CPU kullanımı normal mi? (<%50)
- [ ] Memory kullanımı normal mi? (<%80)
- [ ] Response time kabul edilebilir mi? (<2s)
- [ ] Error rate düşük mü? (<%1)

## Troubleshooting

### Timeout Devam Ederse

#### 1. Database Restart
```bash
railway service restart <database-service-id>
```

#### 2. Connection Pool Ayarları
`config.py` içinde:
- `pool_size`: 3 → 2
- `max_overflow`: 7 → 5
- `connect_timeout`: 90 → 120

#### 3. Gunicorn Ayarları
`railway_start.sh` içinde:
- `--timeout`: 180 → 240
- `--workers`: 1 (değiştirme)
- `--threads`: 2 → 1

#### 4. Railway Support
- Railway Discord'a sor
- Support ticket aç
- Status page kontrol et: https://status.railway.app

### Connection Limit Hatası

```bash
# Railway plan'ını kontrol et
railway status

# Connection limit'i artır (plan upgrade)
# veya pool_size'ı düşür
```

### Network Latency

```bash
# Database region'ı kontrol et
railway variables

# App ve DB aynı region'da mı?
# Farklıysa migrate et
```

## Rollback Plan

### Hızlı Rollback
```bash
# Önceki commit'e dön
git revert HEAD
git push railway main

# veya
railway rollback
```

### Manuel Rollback
1. Railway dashboard'a git
2. Deployments sekmesine tıkla
3. Önceki başarılı deployment'ı seç
4. "Redeploy" butonuna tıkla

## Success Criteria

- [ ] Uygulama 2 dakika içinde başladı
- [ ] Database bağlantısı başarılı
- [ ] Health check endpoint çalışıyor
- [ ] Login sayfası açılıyor
- [ ] Timeout hatası yok
- [ ] Error rate <%1

## Notes

- İlk deployment 2-3 dakika sürebilir (cold start)
- Database connection pool warm-up için 30 saniye bekle
- Traffic artarsa worker/thread sayısını artır
- Monitoring'i sürekli kontrol et
