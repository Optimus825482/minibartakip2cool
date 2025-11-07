# Design Document

## Overview

Bu tasarım, kat sorumlusunun oda minibar kontrolü ve yeniden dolum işlemlerini optimize eder. Mevcut sistemde "İlk Dolum" işlemi "Oda Kontrol" menüsü içinde yer almaktadır. Bu değişiklikle:

1. **İlk Dolum** ayrı bir menü öğesi olacak (boş minibar'lara ilk ürün ekleme)
2. **Oda Kontrol** sadece mevcut minibar içeriğini görüntüleme ve yeniden dolum için kullanılacak

Yeniden dolum işlemi modal tabanlı, kullanıcı dostu bir arayüz ile gerçekleştirilecek ve tüm stok hareketleri otomatik olarak kaydedilecektir.

## Architecture

### Mevcut Sistem Analizi

**Mevcut Yapı:**
- `templates/kat_sorumlusu/minibar_kontrol.html` - Tek sayfa içinde tüm işlemler
- `routes/kat_sorumlusu_qr_routes.py` - QR kod işlemleri
- `models.py` - MinibarIslem, MinibarIslemDetay, PersonelZimmet, PersonelZimmetDetay

**Mevcut İşlem Akışı:**
1. Kat ve oda seçimi (manuel veya QR)
2. İşlem tipi seçimi (ilk_dolum, kontrol, doldurma)
3. İşlem tipine göre farklı form gösterimi

### Yeni Sistem Mimarisi

**Değişiklikler:**

1. **Menü Ayrımı:**
   - `/kat-sorumlusu/ilk-dolum` - İlk dolum sayfası (mevcut minibar_kontrol.html'den ayrılacak)
   - `/kat-sorumlusu/oda-kontrol` - Yeni oda kontrol sayfası (sadece görüntüleme + yeniden dolum)

2. **Yeni Route'lar:**
   - `GET /kat-sorumlusu/oda-kontrol` - Oda kontrol sayfası
   - `POST /api/kat-sorumlusu/minibar-urunler` - Oda ürünlerini getir
   - `POST /api/kat-sorumlusu/yeniden-dolum` - Yeniden dolum işlemi

3. **Frontend Akışı:**
   ```
   Oda Kontrol Sayfası
   ├── QR Kod Okutma / Manuel Seçim
   ├── Ürün Listesi Gösterimi
   │   ├── Ürün Adı
   │   ├── Mevcut Miktar
   │   └── Birim
   └── Ürüne Tıklama
       ├── Yeniden Dolum Modalı
       │   ├── Mevcut Miktar (readonly)
       │   ├── Eklenecek Miktar (input)
       │   └── Dolum Yap Butonu
       └── Onay Modalı
           ├── İşlem Özeti
           ├── Stok Düşüş Bilgisi
           └── Onayla / İptal
   ```

## Components and Interfaces

### 1. Backend Components

#### Route Handler: `kat_sorumlusu_routes.py`

```python
# Yeni route'lar eklenecek

@app.route('/kat-sorumlusu/oda-kontrol')
@login_required
@role_required('kat_sorumlusu')
def oda_kontrol():
    """Oda kontrol sayfası - sadece görüntüleme ve yeniden dolum"""
    pass

@app.route('/api/kat-sorumlusu/minibar-urunler', methods=['POST'])
@login_required
@role_required('kat_sorumlusu')
def api_minibar_urunler():
    """Seçilen odanın minibar ürünlerini getir"""
    pass

@app.route('/api/kat-sorumlusu/yeniden-dolum', methods=['POST'])
@login_required
@role_required('kat_sorumlusu')
def api_yeniden_dolum():
    """Yeniden dolum işlemi"""
    pass
```

#### API Endpoints

**1. GET /kat-sorumlusu/oda-kontrol**
- Oda kontrol sayfasını render eder
- Kat listesini template'e gönderir

**2. POST /api/kat-sorumlusu/minibar-urunler**

Request:
```json
{
  "oda_id": 123
}
```

Response (Success):
```json
{
  "success": true,
  "data": {
    "oda_no": "101",
    "kat_adi": "1. Kat",
    "urunler": [
      {
        "urun_id": 1,
        "urun_adi": "Coca Cola",
        "birim": "Adet",
        "mevcut_miktar": 5,
        "zimmet_detay_id": 45
      }
    ]
  }
}
```

Response (Empty):
```json
{
  "success": true,
  "data": {
    "oda_no": "101",
    "kat_adi": "1. Kat",
    "urunler": []
  },
  "message": "Bu minibar'da henüz ürün bulunmamaktadır"
}
```

**3. POST /api/kat-sorumlusu/yeniden-dolum**

Request:
```json
{
  "oda_id": 123,
  "urun_id": 1,
  "eklenecek_miktar": 3,
  "zimmet_detay_id": 45
}
```

Response (Success):
```json
{
  "success": true,
  "message": "Dolum işlemi başarıyla tamamlandı",
  "data": {
    "yeni_miktar": 8,
    "kalan_zimmet": 47
  }
}
```

Response (Error - Yetersiz Stok):
```json
{
  "success": false,
  "message": "Stoğunuzda yeterli Coca Cola bulunmamaktadır. Mevcut: 2, İstenen: 3"
}
```

### 2. Frontend Components

#### Template: `oda_kontrol.html`

**Bölümler:**

1. **Oda Seçim Bölümü**
   - QR Kod Okutma Butonu
   - Manuel Kat/Oda Seçimi

2. **Ürün Listesi Bölümü**
   - Responsive tablo
   - Tıklanabilir satırlar
   - Boş durum mesajı

3. **Yeniden Dolum Modalı**
   - Ürün bilgileri
   - Miktar input
   - İptal / Dolum Yap butonları

4. **Onay Modalı**
   - İşlem özeti
   - Bilgilendirme mesajı
   - İptal / Onayla butonları

#### JavaScript Modülü: `oda_kontrol.js`

**Fonksiyonlar:**

```javascript
// QR kod okutma
function qrIleBaslat() { }

// Oda seçildiğinde ürünleri getir
function odaSecildi(odaId) { }

// Ürün listesini render et
function urunListesiGoster(urunler) { }

// Ürüne tıklandığında modal aç
function uruneTiklandi(urun) { }

// Yeniden dolum modalını aç
function yenidenDolumModalAc(urun) { }

// Dolum yap butonuna tıklandığında
function dolumYap() { }

// Onay modalını aç
function onayModalAc(islemBilgileri) { }

// İşlemi onayla
function islemOnayla() { }

// Modalları kapat
function modallariKapat() { }
```

## Data Models

### Mevcut Modeller (Değişiklik Yok)

**MinibarIslem**
- İşlem başlık tablosu
- `islem_tipi`: 'ilk_dolum', 'kontrol', 'doldurma'

**MinibarIslemDetay**
- İşlem detay tablosu
- `baslangic_stok`: İşlem öncesi miktar
- `bitis_stok`: İşlem sonrası miktar
- `eklenen_miktar`: Eklenen miktar
- `zimmet_detay_id`: Hangi zimmetten kullanıldığı

**PersonelZimmetDetay**
- Kat sorumlusu stok tablosu
- `miktar`: Toplam zimmet miktarı
- `kullanilan_miktar`: Kullanılan miktar
- `kalan_miktar`: Kalan miktar

### Veri Akışı

**Yeniden Dolum İşlemi:**

1. **Mevcut Durum Sorgulama:**
   ```sql
   SELECT mid.urun_id, u.urun_adi, u.birim, 
          mid.bitis_stok as mevcut_miktar,
          mid.zimmet_detay_id
   FROM minibar_islem_detay mid
   JOIN minibar_islemleri mi ON mid.islem_id = mi.id
   JOIN urunler u ON mid.urun_id = u.urun_id
   WHERE mi.oda_id = ? 
   AND mid.islem_id = (
       SELECT MAX(id) FROM minibar_islemleri WHERE oda_id = ?
   )
   ```

2. **Zimmet Kontrolü:**
   ```sql
   SELECT kalan_miktar 
   FROM personel_zimmet_detay 
   WHERE id = ? AND kalan_miktar >= ?
   ```

3. **İşlem Kaydı:**
   - MinibarIslem oluştur (islem_tipi='doldurma')
   - MinibarIslemDetay oluştur
   - PersonelZimmetDetay güncelle (kalan_miktar düş, kullanilan_miktar artır)

## Error Handling

### Frontend Hata Yönetimi

**Validasyon Hataları:**
- Boş miktar girişi
- Negatif miktar
- Sayısal olmayan değer

**Kullanıcı Bildirimleri:**
```javascript
function hataGoster(mesaj) {
    // Toast notification
    Toastify({
        text: mesaj,
        duration: 3000,
        gravity: "top",
        position: "right",
        backgroundColor: "#ef4444"
    }).showToast();
}

function basariGoster(mesaj) {
    Toastify({
        text: mesaj,
        duration: 3000,
        gravity: "top",
        position: "right",
        backgroundColor: "#10b981"
    }).showToast();
}
```

### Backend Hata Yönetimi

**Hata Tipleri ve Yanıtları:**

1. **Validasyon Hataları (400)**
   - Eksik parametre
   - Geçersiz miktar
   - Geçersiz oda_id

2. **Yetkilendirme Hataları (403)**
   - Yetkisiz erişim

3. **Kaynak Bulunamadı (404)**
   - Oda bulunamadı
   - Ürün bulunamadı
   - Zimmet detay bulunamadı

4. **İş Mantığı Hataları (422)**
   - Yetersiz stok
   - Minibar'da ürün yok

5. **Sunucu Hataları (500)**
   - Veritabanı hatası
   - Beklenmeyen hata

**Hata Loglama:**
```python
try:
    # İşlem
    pass
except ValueError as e:
    log_hata(e, modul='yeniden_dolum', extra_info={'oda_id': oda_id})
    return jsonify({'success': False, 'message': str(e)}), 400
except Exception as e:
    log_hata(e, modul='yeniden_dolum')
    db.session.rollback()
    return jsonify({'success': False, 'message': 'İşlem sırasında bir hata oluştu'}), 500
```

**Transaction Yönetimi:**
```python
try:
    # Zimmet güncelle
    zimmet_detay.kalan_miktar -= eklenecek_miktar
    zimmet_detay.kullanilan_miktar += eklenecek_miktar
    
    # Minibar işlem oluştur
    minibar_islem = MinibarIslem(...)
    db.session.add(minibar_islem)
    
    # Detay oluştur
    minibar_detay = MinibarIslemDetay(...)
    db.session.add(minibar_detay)
    
    db.session.commit()
except Exception as e:
    db.session.rollback()
    raise
```

## Testing Strategy

### Unit Tests

**Backend Tests:**

1. **API Endpoint Tests**
   ```python
   def test_minibar_urunler_basarili():
       """Oda ürünlerini başarıyla getirme"""
       pass
   
   def test_minibar_urunler_bos():
       """Boş minibar durumu"""
       pass
   
   def test_yeniden_dolum_basarili():
       """Başarılı yeniden dolum"""
       pass
   
   def test_yeniden_dolum_yetersiz_stok():
       """Yetersiz stok hatası"""
       pass
   
   def test_yeniden_dolum_gecersiz_miktar():
       """Geçersiz miktar validasyonu"""
       pass
   ```

2. **Business Logic Tests**
   ```python
   def test_zimmet_dusus_hesaplama():
       """Zimmet düşüş hesaplaması"""
       pass
   
   def test_minibar_miktar_guncelleme():
       """Minibar miktar güncelleme"""
       pass
   ```

### Integration Tests

1. **End-to-End Flow**
   ```python
   def test_oda_kontrol_tam_akis():
       """Oda seçiminden dolum işlemine kadar tam akış"""
       # 1. Oda seç
       # 2. Ürünleri getir
       # 3. Yeniden dolum yap
       # 4. Stok kontrolü
       pass
   ```

2. **QR Kod Entegrasyonu**
   ```python
   def test_qr_ile_oda_secimi():
       """QR kod ile oda seçimi ve ürün listesi"""
       pass
   ```

### Manual Testing Checklist

**Fonksiyonel Testler:**
- [ ] Menüde "İlk Dolum" ve "Oda Kontrol" ayrı görünüyor
- [ ] QR kod ile oda seçimi çalışıyor
- [ ] Manuel oda seçimi çalışıyor
- [ ] Ürün listesi doğru gösteriliyor
- [ ] Boş minibar mesajı gösteriliyor
- [ ] Ürüne tıklayınca modal açılıyor
- [ ] Miktar girişi çalışıyor
- [ ] Onay modalı gösteriliyor
- [ ] Dolum işlemi başarılı
- [ ] Stok düşüşü doğru
- [ ] Hata mesajları gösteriliyor

**UI/UX Testler:**
- [ ] Responsive tasarım (mobil, tablet, desktop)
- [ ] Modal animasyonları
- [ ] Loading state'leri
- [ ] Toast bildirimleri
- [ ] Tema uyumu

**Performans Testler:**
- [ ] Ürün listesi hızlı yükleniyor
- [ ] Modal açılma hızı
- [ ] API yanıt süreleri

## Implementation Notes

### Mevcut Kod Değişiklikleri

**1. minibar_kontrol.html Ayrımı:**
- Mevcut dosya `ilk_dolum.html` olarak kopyalanacak
- İlk dolum dışındaki işlem tipleri kaldırılacak
- Yeni `oda_kontrol.html` oluşturulacak

**2. Route Organizasyonu:**
- Mevcut route'lar korunacak
- Yeni route'lar `kat_sorumlusu_routes.py` dosyasına eklenecek
- QR kod entegrasyonu mevcut `kat_sorumlusu_qr_routes.py` kullanılacak

**3. JavaScript Modülleri:**
- Ortak fonksiyonlar `static/js/kat_sorumlusu_common.js`
- Oda kontrol spesifik `static/js/oda_kontrol.js`

### Güvenlik Considerations

1. **CSRF Protection:** Tüm POST request'lerde CSRF token
2. **Authorization:** `@role_required('kat_sorumlusu')` decorator
3. **Input Validation:** Backend'de tüm inputlar validate edilecek
4. **SQL Injection:** SQLAlchemy ORM kullanımı
5. **XSS Protection:** Template'lerde auto-escape aktif

### Performans Optimizasyonları

1. **Database Queries:**
   - Join kullanımı ile N+1 problemi önleme
   - Index'ler mevcut (oda_id, islem_tarihi)

2. **Frontend:**
   - Debounce kullanımı (gerekirse)
   - Lazy loading (büyük listeler için)

3. **Caching:**
   - Kat/oda listesi session'da cache (gerekirse)

## Migration Plan

### Adım 1: Backend Hazırlık
1. Yeni route'ları ekle
2. API endpoint'leri oluştur
3. Unit testleri yaz

### Adım 2: Frontend Geliştirme
1. `oda_kontrol.html` template'i oluştur
2. JavaScript modülünü yaz
3. CSS stilleri ekle

### Adım 3: Menü Güncellemesi
1. Dashboard menüsünü güncelle
2. İlk Dolum ve Oda Kontrol ayrı linkler

### Adım 4: Test ve Deploy
1. Integration testleri çalıştır
2. Manual test
3. Production deploy

### Rollback Planı
- Mevcut `minibar_kontrol.html` korunacak
- Yeni özellik sorun çıkarırsa eski menü yapısına dönülebilir
- Database değişikliği olmadığı için rollback kolay
