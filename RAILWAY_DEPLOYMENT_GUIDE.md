# Railway Deployment Rehberi

## ✅ Yapılan Değişiklikler

### 1. Template Düzeltmeleri
- ✅ `_form_helpers.html` - Jinja2 syntax hataları düzeltildi
- ✅ `personel_zimmet.html` - Eksik endblock eklendi
- ✅ Tüm template'ler güncellendi ve iyileştirildi

### 2. Yeni Özellikler
- ✅ Audit Trail (Denetim İzi) sistemi eklendi
- ✅ WTForms ile form validasyonu
- ✅ CSRF koruması
- ✅ PWA desteği (Progressive Web App)
- ✅ Toplu oda doldurma özelliği
- ✅ Kat bazlı raporlama
- ✅ Rate limiting (429 hata sayfası)

### 3. Database Güncellemeleri
- ✅ `audit_log` tablosu eklendi
- ✅ Audit trail fonksiyonları

### 4. Yeni Dosyalar
- ✅ `forms.py` - Form tanımlamaları
- ✅ `utils/audit.py` - Audit trail yardımcı fonksiyonlar
- ✅ `static/` klasörü - JS, CSS, PWA dosyaları
- ✅ Yeni template'ler

## 🚀 Railway Deployment Adımları

### Adım 1: Railway Dashboard Kontrolü
1. Railway.app'e giriş yapın
2. `minibartakip` projenizi açın
3. Deployment'ın otomatik olarak başladığını göreceksiniz

### Adım 2: Veritabanı Güncellemelerini Uygulama

Railway'de PostgreSQL veritabanına bağlanmak için:

#### Yöntem 1: Railway CLI ile (Önerilen)
```bash
# Railway CLI kurulumu (eğer kurulu değilse)
npm install -g @railway/cli

# Railway'e login
railway login

# Projeye bağlan
railway link

# Database shell'e gir
railway connect postgres

# Audit log tablosunu oluştur
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    kullanici_id INTEGER REFERENCES kullanicilar(id),
    kullanici_adi VARCHAR(100),
    islem_tipi VARCHAR(50) NOT NULL,
    tablo_adi VARCHAR(100),
    kayit_id INTEGER,
    eski_deger TEXT,
    yeni_deger TEXT,
    ip_adresi VARCHAR(45),
    user_agent TEXT,
    islem_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aciklama TEXT
);

CREATE INDEX idx_audit_kullanici ON audit_log(kullanici_id);
CREATE INDEX idx_audit_islem_tipi ON audit_log(islem_tipi);
CREATE INDEX idx_audit_tablo ON audit_log(tablo_adi);
CREATE INDEX idx_audit_zaman ON audit_log(islem_zamani);

# Çıkış
\q
```

#### Yöntem 2: Python Script ile
Railway projesinde Variables bölümünden `DATABASE_URL` bilgisini alın ve:

```bash
# Local'de çalıştırın (Railway DATABASE_URL ile)
DATABASE_URL="your-railway-db-url" python create_audit_table.py
```

### Adım 3: Environment Variables Kontrolü

Railway Dashboard → Variables bölümünde şunları kontrol edin:

```
DATABASE_URL=postgresql://... (Otomatik oluşturulmuş olmalı)
SECRET_KEY=your-secret-key (Güvenli bir key)
FLASK_ENV=production
```

Eğer `SECRET_KEY` yoksa ekleyin:
```bash
railway variables set SECRET_KEY=$(openssl rand -hex 32)
```

### Adım 4: Deployment'ı İzleme

1. Railway Dashboard'da Deployments sekmesine gidin
2. Logs'u açın ve hata kontrolü yapın
3. Build başarılı olduktan sonra uygulamanızı test edin

### Adım 5: İlk Kurulum (Eğer yeni deployment ise)

Uygulama URL'sine gidin:
```
https://your-app-name.up.railway.app/setup
```

Sistem yöneticisi hesabını oluşturun.

## 🔍 Deployment Sonrası Kontroller

### 1. Uygulama Çalışıyor mu?
- [ ] Ana sayfa açılıyor
- [ ] Login sayfası çalışıyor
- [ ] Setup sayfası (ilk kurulum için) erişilebilir

### 2. Veritabanı Bağlantısı
- [ ] Login yapılabiliyor
- [ ] Veriler listeleniyor
- [ ] Yeni kayıt ekleniyor

### 3. Yeni Özellikler
- [ ] Audit Trail çalışıyor (`/audit-trail`)
- [ ] Formlar CSRF korumalı
- [ ] PWA manifest erişilebilir (`/static/manifest.json`)

### 4. Hata Sayfaları
- [ ] 404 sayfası çalışıyor
- [ ] 500 sayfası çalışıyor
- [ ] 429 rate limit sayfası çalışıyor

## 🐛 Sorun Giderme

### Build Hatası
```bash
# Railway logs'u kontrol et
railway logs

# Eğer dependency hatası varsa requirements.txt kontrol et
```

### Database Bağlantı Hatası
```bash
# DATABASE_URL doğru mu kontrol et
railway variables

# Database servisinin çalıştığından emin ol
railway status
```

### Static Files Yüklenmiyor
- Railway `static/` klasörünün doğru serve edildiğinden emin olun
- `app.py`'de static folder ayarı doğru: `static_folder='static'`

## 📝 Önemli Notlar

1. **Audit Log**: Her önemli işlem artık audit_log tablosuna kaydediliyor
2. **CSRF Koruması**: Tüm formlar CSRF token gerektiriyor
3. **Rate Limiting**: Brute force koruması aktif
4. **PWA**: Uygulama mobil cihazlara yüklenebilir
5. **Session Güvenliği**: Cookie güvenliği artırıldı

## 🎉 Deploy Tamamlandı!

Tüm adımları tamamladıysanız, uygulamanız artık Railway'de çalışıyor olmalı.

Test etmek için:
1. Uygulamanızı açın
2. Login yapın
3. Audit Trail'i kontrol edin: `/audit-trail`
4. Yeni özellikleri test edin

**Deployment URL**: https://minibartakip-production.up.railway.app (veya kendi URL'iniz)

---
*Son güncelleme: 31 Ekim 2025*
