# 🚀 Railway Hızlı Kurulum (5 Dakika)

## 1️⃣ Railway'de Proje Oluştur
1. https://railway.app → GitHub ile giriş
2. **New Project** → **Deploy from GitHub repo**
3. `Optimus825482/minibartakip2` seç

## 2️⃣ PostgreSQL Ekle
1. Proje içinde **New** → **Database** → **PostgreSQL**
2. Otomatik bağlanır ✅

## 3️⃣ Environment Variables Ayarla

### Yöntem 1: Otomatik (Önerilen)
```bash
python railway_setup.py
```

### Yöntem 2: Manuel
**Variables** sekmesine git ve ekle:

```bash
DATABASE_URL=postgresql://postgres:NEOcbkYOOSzROELtJEuVZxdPphGLIXnx@shinkansen.proxy.rlwy.net:36747/railway
SECRET_KEY=8f3a9b2c7d1e6f4a5b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a
FLASK_ENV=production
ENV=production
DB_TYPE=postgresql
```

⚠️ **NOT:** SECRET_KEY'i production'da mutlaka değiştir!

## 4️⃣ Deploy Et
**Deploy** butonuna tıkla → Bekle (2-3 dakika)

## 5️⃣ İlk Superadmin Oluştur

Railway Dashboard → Service → **Shell** sekmesi:

```bash
python add_superadmin_railway.py
```

Kullanıcı adı: `superadmin`
Şifre: `Admin123!`

## ✅ Bitti!

URL'ni al: **Settings** → **Domains** → **Generate Domain**

Örnek: `https://minibartakip2-production.up.railway.app`

---

## 🔧 Sorun mu var?

### Database bağlanamıyor:
```bash
railway variables  # Değişkenleri kontrol et
railway restart    # Servisi yeniden başlat
```

### Migration hatası:
```bash
railway run python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Logs:
```bash
railway logs
```

---

## 📚 Detaylı Rehber
Daha fazla bilgi için: `RAILWAY_DEPLOYMENT.md`
