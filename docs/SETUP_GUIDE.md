# Setup Yönetim Sistemi

## Bölüm 1: Setup Yönetimi Kullanım Kılavuzu

### Genel Bakış

Setup yönetim sistemi, otel odalarına atanacak minibar içeriklerini tanımlamak ve yönetmek için kullanılır.

### Erişim

- **URL:** `/setup-yonetimi`
- **Menü:** Admin Sidebar > Otel & Yapı > Setup'lar (Odalar'ın altında)
- **Yetki:** Sistem Yöneticisi, Admin

### Özellikler

#### 1. Setup Listesi

- Tüm tanımlı setup'ları görüntüleme
- Her setup için:
  - Setup adı (MINI, MAXI vb.)
  - Açıklama
  - Ürün sayısı
  - Atanan oda tipleri

#### 2. Yeni Setup Ekleme

- **Buton:** Sağ üstte "Yeni Setup Ekle"
- **Alanlar:**
  - Setup Adı (zorunlu)
  - Açıklama (opsiyonel)

#### 3. Setup İçerik Düzenleme

- **Buton:** Her setup satırında "İçerik" butonu
- **İşlemler:**
  - Ürün listesinden ürün seçme
  - Adet belirleme
  - Ürün ekleme
  - Mevcut ürünleri silme

#### 4. Setup Atama

- **Buton:** Her setup satırında "Atama" butonu
- **İşlem:** Setup'ı oda tiplerine atama
- Bir oda tipi sadece bir setup kullanabilir

#### 5. Setup Silme

- **Buton:** Her setup satırında "Sil" butonu
- Soft delete (aktif = False)

### Veritabanı Yapısı

#### setuplar Tablosu

- `id`: Primary key
- `ad`: Setup adı (unique)
- `aciklama`: Açıklama
- `aktif`: Aktif/Pasif durumu
- `olusturma_tarihi`: Oluşturma zamanı

#### setup_icerik Tablosu

- `id`: Primary key
- `setup_id`: Setup referansı
- `urun_id`: Ürün referansı
- `adet`: Ürün adedi
- `olusturma_tarihi`: Oluşturma zamanı

### API Endpoint'leri

1. `GET /api/setuplar` - Setup listesi
2. `POST /api/setuplar` - Yeni setup ekle
3. `DELETE /api/setuplar/<id>` - Setup sil
4. `GET /api/setuplar/<id>/icerik` - Setup içeriği
5. `POST /api/setuplar/<id>/icerik` - İçeriğe ürün ekle
6. `DELETE /api/setup-icerik/<id>` - İçerikten ürün sil
7. `POST /api/setup-atama` - Setup'ı oda tiplerine ata
8. `GET /api/urunler-liste` - Ürün listesi

### Kullanım Senaryosu

#### Örnek: MINI Setup Oluşturma

1. **Setup Oluştur:**

   - "Yeni Setup Ekle" butonuna tıkla
   - Ad: "MINI"
   - Açıklama: "Standart oda minibar içeriği"
   - Kaydet

2. **İçerik Ekle:**

   - MINI setup'ın "İçerik" butonuna tıkla
   - Ürün seç: "Coca Cola"
   - Adet: 2
   - Ekle
   - Diğer ürünleri de ekle

3. **Oda Tiplerine Ata:**
   - MINI setup'ın "Atama" butonuna tıkla
   - "STANDARD" ve "JUNIOR SUITE" oda tiplerini seç
   - Kaydet

### Varsayılan Setup'lar

- **MINI:** Mini setup - Standart oda içeriği
- **MAXI:** Maxi setup - Geniş oda içeriği

### Notlar

- Her oda tipi sadece bir setup kullanabilir
- Setup silindiğinde içeriği de silinir (cascade)
- Oda tipine atanan setup, oda tanımlarında görünür

---

## Bölüm 2: Setup Bazlı Minibar Kontrol Sistemi

**Versiyon:** 1.0.0

### Genel Bakış

Setup bazlı minibar kontrol sistemi, oda tipine göre tanımlanan setup'lar üzerinden minibar kontrolü yapılmasını sağlar. Eski "İlk Dolum" ve "Ek Dolum" sisteminin yerine geçen modern bir yaklaşımdır.

#### Temel Özellikler

- Oda tipine göre otomatik setup yükleme
- Setup bazlı ürün kontrolü
- Eksik ürün tamamlama
- Setup üstü ekstra ürün ekleme
- Ekstra ürün tüketim takibi
- Zimmet stok kontrolü
- Otomatik tüketim hesaplama
- Audit trail kayıtları
- Responsive mobil tasarım

### Mimari

#### Veritabanı Değişiklikleri

**1. Yeni Enum Değerleri**

```sql
ALTER TYPE minibar_islem_tipi ADD VALUE 'setup_kontrol';
ALTER TYPE minibar_islem_tipi ADD VALUE 'ekstra_ekleme';
ALTER TYPE minibar_islem_tipi ADD VALUE 'ekstra_tuketim';
```

**2. Yeni Kolon**

```sql
ALTER TABLE minibar_islem_detay
ADD COLUMN ekstra_miktar INTEGER DEFAULT 0;
```

**3. Performans Index'leri**

```sql
CREATE INDEX idx_minibar_islem_oda_tarih ON minibar_islemleri(oda_id, islem_tarihi);
CREATE INDEX idx_minibar_islem_personel_tarih ON minibar_islemleri(personel_id, islem_tarihi);
CREATE INDEX idx_minibar_detay_urun ON minibar_islem_detay(urun_id);
CREATE INDEX idx_setup_icerik_setup ON setup_icerik(setup_id);
CREATE INDEX idx_oda_tipi_setup_oda_tipi ON oda_tipi_setup(oda_tipi_id);
CREATE INDEX idx_oda_tipi_setup_setup ON oda_tipi_setup(setup_id);
```

#### Backend Bileşenleri

**1. Servis Katmanı (`utils/minibar_servisleri.py`)**

Custom Exception'lar:
- `ZimmetStokYetersizError` - Zimmet stoğu yetersiz
- `OdaTipiNotFoundError` - Oda tipi bulunamadı
- `SetupNotFoundError` - Setup bulunamadı

Servis Fonksiyonları:
- `oda_setup_durumu_getir(oda_id)` - Oda setup durumunu getirir
- `tuketim_hesapla(...)` - Tüketim miktarını hesaplar
- `zimmet_stok_kontrol(...)` - Zimmet stok kontrolü
- `zimmet_stok_dusu(...)` - Zimmet stoğundan düşüş
- `minibar_stok_guncelle(...)` - Minibar stok güncelleme
- `tuketim_kaydet(...)` - Tüketim kaydı oluşturma

**2. API Endpoint'leri (`routes/kat_sorumlusu_routes.py`)**

GET Endpoint'leri:
- `GET /api/kat-sorumlusu/oda-setup/<oda_id>` - Oda setup durumu

POST Endpoint'leri:
- `POST /api/kat-sorumlusu/urun-ekle` - Eksik ürün ekleme
- `POST /api/kat-sorumlusu/ekstra-ekle` - Ekstra ürün ekleme
- `POST /api/kat-sorumlusu/ekstra-sifirla` - Ekstra ürün sıfırlama

Sayfa Route'u:
- `GET /minibar-kontrol-setup` - Ana sayfa

#### Frontend Bileşenleri

**1. Template (`templates/kat_sorumlusu/minibar_kontrol_setup.html`)**
- Responsive tasarım
- Accordion yapısı
- Modal dialog'lar
- Toast mesajları
- Loading state'leri
- Durum renklendirmesi

**2. JavaScript (`static/js/minibar_kontrol_setup.js`)**
- Kat/Oda seçimi
- Setup listesi yükleme
- Accordion yönetimi
- Modal yönetimi
- API çağrıları
- Toast mesajları

### Kullanım Kılavuzu

#### 1. Oda Seçimi

**Manuel Seçim:**
1. Kat dropdown'ından kat seçin
2. Oda dropdown'ından oda seçin
3. Setup listesi otomatik yüklenir

**QR Kod ile:**
1. "QR Kod ile Başla" butonuna tıklayın
2. Oda QR kodunu tarayın
3. Setup listesi otomatik yüklenir

#### 2. Setup Kontrolü

**Setup Görüntüleme:**
- Her setup accordion olarak gösterilir
- Dolap içi setup'lar mor renkte
- Dolap dışı setup'lar pembe renkte
- Accordion'a tıklayarak ürünleri görüntüleyin

**Ürün Durumları:**
- 🟢 **Tam** - Setup miktarı tam
- 🔴 **Eksik** - Setup miktarından az
- 🟠 **Ekstra** - Setup üstü ürün var

#### 3. Eksik Ürün Ekleme

1. Eksik durumundaki ürünün yanındaki "Ekle" butonuna tıklayın
2. Modal açılır, ürün bilgileri gösterilir
3. Eklenecek miktarı girin (varsayılan: eksik miktar)
4. Zimmet stoğunuzu kontrol edin
5. "Kaydet" butonuna tıklayın

**İşlem Sonucu:**
- Tüketim otomatik hesaplanır
- Zimmet stoğundan düşüş yapılır
- Minibar stok güncellenir
- Setup listesi yenilenir

#### 4. Ekstra Ürün Ekleme

1. Tam veya Ekstra durumundaki ürünün yanındaki "Ekstra" butonuna tıklayın
2. Modal açılır, ürün bilgileri gösterilir
3. Ekstra miktarı girin
4. Zimmet stoğunuzu kontrol edin
5. "Kaydet" butonuna tıklayın

**İşlem Sonucu:**
- Zimmet stoğundan düşüş yapılır
- Ekstra miktar kaydedilir
- Tüketim kaydedilmez (henüz tüketilmedi)
- Setup listesi yenilenir

#### 5. Ekstra Ürün Sıfırlama

1. Ekstra miktarı olan ürünün yanındaki "Sıfırla" butonuna tıklayın
2. Onay modalı açılır
3. Ekstra miktar gösterilir
4. "Sıfırla" butonuna tıklayın

**İşlem Sonucu:**
- Ekstra miktar tüketim olarak kaydedilir
- Ekstra miktar sıfırlanır
- Setup listesi yenilenir

### Güvenlik

#### Yetkilendirme
- Tüm endpoint'ler `@login_required` decorator'ü ile korunur
- Tüm endpoint'ler `@role_required('kat_sorumlusu')` ile kısıtlanır
- Oda erişim kontrolü yapılır (kat sorumlusunun oteline ait mi?)

#### Input Validasyonu
- Tüm API endpoint'lerinde input validasyonu yapılır
- Miktar değerleri pozitif olmalıdır
- Zimmet stok kontrolü yapılır
- Oda tipi ve setup kontrolü yapılır

#### Audit Trail
- Her işlem audit log'a kaydedilir
- Kullanıcı, tarih, işlem tipi bilgileri saklanır
- İşlem detayları JSONB formatında kaydedilir

### Veri Akışı

#### Eksik Ürün Ekleme Akışı

```
1. Kullanıcı "Ekle" butonuna tıklar
2. Modal açılır, ürün bilgileri gösterilir
3. Kullanıcı miktarı girer ve "Kaydet" tıklar
4. Frontend: POST /api/kat-sorumlusu/urun-ekle
5. Backend: Input validasyonu
6. Backend: Zimmet stok kontrolü
7. Backend: Transaction başlat
   a. Tüketim hesapla
   b. Zimmet stoğundan düş
   c. MinibarIslem kaydı oluştur
   d. MinibarIslemDetay kaydı oluştur
   e. Audit log kaydet
8. Backend: Transaction commit
9. Frontend: Success mesajı göster
10. Frontend: Setup listesini yenile
```

#### Ekstra Ürün Ekleme Akışı

```
1. Kullanıcı "Ekstra" butonuna tıklar
2. Modal açılır, ürün bilgileri gösterilir
3. Kullanıcı ekstra miktarı girer ve "Kaydet" tıklar
4. Frontend: POST /api/kat-sorumlusu/ekstra-ekle
5. Backend: Input validasyonu
6. Backend: Zimmet stok kontrolü
7. Backend: Transaction başlat
   a. Zimmet stoğundan düş
   b. MinibarIslem kaydı oluştur (tuketim=0)
   c. MinibarIslemDetay kaydı oluştur (ekstra_miktar set)
   d. Audit log kaydet
8. Backend: Transaction commit
9. Frontend: Success mesajı göster
10. Frontend: Setup listesini yenile
```

#### Ekstra Sıfırlama Akışı

```
1. Kullanıcı "Sıfırla" butonuna tıklar
2. Onay modalı açılır
3. Kullanıcı "Sıfırla" tıklar
4. Frontend: POST /api/kat-sorumlusu/ekstra-sifirla
5. Backend: Son ekstra miktarı bul
6. Backend: Transaction başlat
   a. MinibarIslem kaydı oluştur (tuketim=ekstra_miktar)
   b. MinibarIslemDetay kaydı oluştur (ekstra_miktar=0)
   c. Audit log kaydet
7. Backend: Transaction commit
8. Frontend: Success mesajı göster
9. Frontend: Setup listesini yenile
```

### Hata Yönetimi

#### Frontend Hataları

Toast Mesajları:
- Success (Yeşil) - İşlem başarılı
- Error (Kırmızı) - Hata oluştu
- Warning (Turuncu) - Uyarı
- Info (Mavi) - Bilgilendirme

Hata Senaryoları:
- Oda tipi bulunamadı
- Setup bulunamadı
- Zimmet stoğu yetersiz
- Network hatası
- Validation hatası

#### Backend Hataları

```python
try:
    # İşlem
except ZimmetStokYetersizError as e:
    return jsonify({'success': False, 'error': str(e)}), 400
except OdaTipiNotFoundError as e:
    return jsonify({'success': False, 'error': str(e)}), 404
except SetupNotFoundError as e:
    return jsonify({'success': False, 'error': str(e)}), 404
except Exception as e:
    log_hata(...)
    return jsonify({'success': False, 'error': 'İşlem sırasında hata oluştu'}), 500
```

### Performans

#### Optimizasyonlar
- Database index'leri eklendi
- Eager loading kullanıldı
- Query optimizasyonu yapıldı
- Frontend caching (zimmet stokları)
- Lazy loading (accordion'lar)

#### Beklenen Performans
- Setup listeleme: < 2 saniye
- Ürün ekleme: < 1 saniye
- Ekstra ekleme: < 1 saniye
- Ekstra sıfırlama: < 1 saniye

### Mobil Uyumluluk

- Tablet desteği (768px+)
- Telefon desteği (< 768px)
- Touch-friendly butonlar
- Responsive grid layout
- Mobile-first yaklaşım

### Sık Sorulan Sorular

**S: Eski "İlk Dolum" sistemi ne olacak?**
C: Eski sistem kaldırılacak. Tüm işlemler setup bazlı sistem üzerinden yapılacak.

**S: Ekstra ürün nedir?**
C: Setup'ta tanımlı miktarın üzerinde eklenen ürünlerdir. Örneğin setup'ta 2 adet varsa ve siz 4 adet eklerseniz, 2 adeti ekstra olarak kaydedilir.

**S: Ekstra ürün neden sıfırlanır?**
C: Ekstra ürünler tüketildiğinde "Sıfırla" butonu ile tüketim olarak kaydedilir. Bu sayede ekstra ürün takibi yapılır.

**S: Zimmet stoğum yetersizse ne olur?**
C: İşlem yapılamaz ve hata mesajı gösterilir. Depo sorumlusundan zimmet almanız gerekir.

**S: QR kod ile nasıl başlarım?**
C: "QR Kod ile Başla" butonuna tıklayın ve oda QR kodunu tarayın. Sistem otomatik olarak o odanın setup'larını yükler.

### İlgili Dosyalar

#### Backend
- `utils/minibar_servisleri.py` - Servis katmanı
- `routes/kat_sorumlusu_routes.py` - API endpoint'leri
- `models.py` - Veri modelleri

#### Frontend
- `templates/kat_sorumlusu/minibar_kontrol_setup.html` - Template
- `static/js/minibar_kontrol_setup.js` - JavaScript
