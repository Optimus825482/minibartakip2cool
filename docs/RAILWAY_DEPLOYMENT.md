# Railway Deployment Rehberi

## 🚀 Hızlı Başlangıç

### 1. Railway Hesabı Oluştur
- https://railway.app adresine git
- GitHub ile giriş yap

### 2. Yeni Proje Oluştur
```bash
# Railway CLI kur (opsiyonel)
npm i -g @railway/cli

# Login
railway login

# Proje oluştur
railway init
```

### 3. PostgreSQL Ekle
Railway Dashboard'da:
1. **"New"** → **"Database"** → **"PostgreSQL"**
2. Otomatik olarak şu değişkenler oluşur:
   - `DATABASE_URL`
   - `PGHOST`
   - `PGUSER`
   - `PGPASSWORD`
   - `PGDATABASE`
   - `PGPORT`

### 4. Environment Variables Ayarla

Railway Dashboard → **Variables** sekmesine git:

#### ✅ ZORUNLU:
```bash
SECRET_KEY=BURAYA_GUCLU_BIR_SECRET_KEY_YAZ
FLASK_ENV=production
ENV=production
DB_TYPE=postgresql
```

#### 🔐 SECRET_KEY Oluştur:
```bash
# Python ile güçlü secret key oluştur
python -c "import secrets; print(secrets.token_hex(32))"
```

#### ⚠️ OTOMATIK SAĞLANAN (Ayarlamana gerek YOK):
- `DATABASE_URL` - PostgreSQL bağlantı URL'i
- `PORT` - Uygulama portu
- `PGHOST`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`, `PGPORT`

### 5. GitHub'dan Deploy Et

#### A. Railway Dashboard'dan:
1. **"New"** → **"GitHub Repo"**
2. Repository seç: `Optimus825482/minibartakip2`
3. Branch seç: `main`
4. **Deploy** butonuna tıkla

#### B. Railway CLI ile:
```bash
# Repo'yu bağla
railway link

# Deploy et
railway up
```

### 6. Database Migration

Deploy sonrası otomatik migration çalışır. Manuel çalıştırmak için:

```bash
# Railway CLI ile
railway run python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Veya Railway Dashboard → Service → Shell
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 7. İlk Superadmin Oluştur

```bash
# Railway CLI ile
railway run python add_superadmin_railway.py

# Veya Railway Dashboard → Service → Shell
python add_superadmin_railway.py
```

## 📋 Deployment Checklist

- [ ] PostgreSQL database eklendi
- [ ] `SECRET_KEY` ayarlandı (en az 32 karakter)
- [ ] `FLASK_ENV=production` ayarlandı
- [ ] GitHub repo bağlandı
- [ ] Deploy başarılı
- [ ] Database migration çalıştı
- [ ] Superadmin oluşturuldu
- [ ] Domain ayarlandı (opsiyonel)
- [ ] HTTPS aktif (otomatik)

## 🔧 Önemli Dosyalar

### `Procfile`
```
web: gunicorn app:app
```

### `runtime.txt`
```
python-3.11.9
```

### `requirements.txt`
Tüm bağımlılıklar otomatik yüklenir.

## 🌐 Domain Ayarlama (Opsiyonel)

1. Railway Dashboard → **Settings** → **Domains**
2. **Generate Domain** veya **Custom Domain** ekle
3. DNS ayarlarını yap (custom domain için)

## 📊 Monitoring

### Logs Görüntüleme:
```bash
# Railway CLI
railway logs

# Veya Dashboard → Service → Logs
```

### Database Bağlantısı:
```bash
# Railway CLI ile PostgreSQL'e bağlan
railway connect postgres

# Veya connection string al
railway variables
```

## 🔄 Güncelleme

```bash
# Kod değişikliklerini push et
git add .
git commit -m "Update"
git push origin main

# Railway otomatik deploy eder
```

## 🐛 Sorun Giderme

### 1. Database Bağlantı Hatası
```bash
# Database değişkenlerini kontrol et
railway variables

# Database'i yeniden başlat
railway restart
```

### 2. Migration Hatası
```bash
# Manuel migration
railway run alembic upgrade head
```

### 3. Secret Key Hatası
```bash
# Yeni secret key oluştur ve ayarla
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Port Hatası
Railway otomatik `PORT` değişkeni sağlar. Manuel ayarlamana gerek yok!

## 📞 Destek

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: https://github.com/Optimus825482/minibartakip2/issues

## 🎯 Production Best Practices

1. ✅ **SECRET_KEY** her zaman güçlü ve benzersiz olmalı
2. ✅ **HTTPS** otomatik aktif (Railway sağlar)
3. ✅ **Database backups** düzenli al
4. ✅ **Environment variables** güvenli tut
5. ✅ **Logs** düzenli kontrol et
6. ✅ **Updates** düzenli yap

## 🔐 Güvenlik

- SECRET_KEY asla GitHub'a commit etme
- .env dosyaları .gitignore'da
- Production'da DEBUG=False
- HTTPS zorunlu (Railway otomatik)
- CSRF protection aktif
- Session güvenliği aktif

## 💰 Maliyet

Railway ücretsiz plan:
- $5 kredi/ay
- 500 saat çalışma
- PostgreSQL dahil

Daha fazla bilgi: https://railway.app/pricing
