# Railway Migration Uygulama - Hızlı Kılavuz

## 🎯 Ne Yapılacak?

Railway PostgreSQL veritabanınıza şu migration'lar uygulanacak:

1. **Otel Logo** - `oteller` tablosuna `logo` kolonu eklenir
2. **ML Tabloları** - Machine Learning sistemi için 4 tablo oluşturulur:
   - `ml_metrics` - Metrik verileri
   - `ml_models` - Model bilgileri
   - `ml_alerts` - Uyarılar
   - `ml_training_logs` - Eğitim logları

---

## 🚀 Kullanım

### Yöntem 1: Batch Dosyası (Windows)

```cmd
apply_migrations.bat
```

### Yöntem 2: Python Script

```bash
python apply_migrations_railway.py
```

---

## 📝 Adımlar

1. **Script'i çalıştırın**
2. **Railway bağlantı bilgilerini girin:**
   - Host (örn: `autorack.proxy.rlwy.net`)
   - Port (örn: `12345`)
   - User (`postgres`)
   - Password (Railway'den alın)
   - Database (`railway`)

3. **İşlemin tamamlanmasını bekleyin**

---

## ✅ Kontrol

Migration sonrası kontrol komutları:

```sql
-- Oteller tablosunda logo kolonunu kontrol et
\d oteller

-- ML tablolarını listele
\dt ml_*

-- ML tablolarını kontrol et
SELECT COUNT(*) FROM ml_metrics;
SELECT COUNT(*) FROM ml_models;
SELECT COUNT(*) FROM ml_alerts;
SELECT COUNT(*) FROM ml_training_logs;
```

---

## 🔒 Güvenlik

- Mevcut verileriniz **etkilenmez**
- Sadece yeni kolonlar ve tablolar eklenir
- Eğer kolon/tablo zaten varsa **atlanır**

---

## 📌 Özellikler

✅ **Güvenli** - Mevcut yapıyı kontrol eder
✅ **Akıllı** - Var olan migration'ları atlar
✅ **Detaylı** - Her adımı raporlar
✅ **Hata toleranslı** - Sorunları yakalar ve raporlar

---

## ⚠️ Not

Migration'ları uygulamadan **önce**:
1. Backup aldığınızdan emin olun
2. Railway veritabanının çalıştığını kontrol edin
3. Doğru bağlantı bilgilerine sahip olduğunuzdan emin olun

---

## 🆘 Sorun mu var?

**Bağlantı hatası:**
- Railway bağlantı bilgilerini kontrol edin
- Public networking URL kullandığınızdan emin olun

**Tablo zaten var hatası:**
- Normal - Migration atlanacak
- Devam edebilirsiniz

**Yetki hatası:**
- Railway kullanıcısının yeterli yetkisi olmalı
- Genelde sorun olmaz

---

**Hazır mısınız?** `apply_migrations.bat` dosyasını çalıştırın! 🚀
