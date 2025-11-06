# Design Document

## Overview

Bu tasarım, Kat Sorumlusu panelini gelişmiş stok yönetimi özellikleriyle güçlendirir. Mevcut zimmet sistemi üzerine inşa edilerek, kritik stok takibi, otomatik sipariş hazırlama ve stokout uyarı mekanizmaları ekler. Sistem, Depo Sorumlusu panelindeki başarılı stok yönetimi yaklaşımını Kat Sorumlusu ihtiyaçlarına uyarlar.

## Architecture

### Mevcut Sistem Analizi

**Veritabanı Yapısı:**
- `PersonelZimmet`: Zimmet başlık tablosu (personel_id, zimmet_tarihi, durum)
- `PersonelZimmetDetay`: Zimmet detay tablosu (urun_id, miktar, kullanilan_miktar, kalan_miktar)
- `MinibarIslem`: Minibar işlem başlık (oda_id, personel_id, islem_tipi)
- `MinibarIslemDetay`: Minibar işlem detay (urun_id, baslangic_stok, bitis_stok, tuketim, zimmet_detay_id)

**Mevcut Helper Fonksiyonlar:**
- `get_stok_toplamlari()`: Depo stok hesaplama
- `get_kritik_stok_urunler()`: Kritik stok listesi
- `get_stok_durumu()`: Stok durum kategorileri
- `log_islem()`, `log_hata()`: Loglama sistemi

### Yeni Mimari Bileşenler

**1. Kat Sorumlusu Stok Modülü**
- Zimmet bazlı stok takibi
- Kritik seviye yönetimi
- Sipariş hazırlama motoru
- Stokout uyarı sistemi

**2. Veritabanı Genişletmeleri**
- `PersonelZimmetDetay` tablosuna yeni alan: `kritik_stok_seviyesi` (Integer, nullable)
- `SiparisIstek` yeni tablo (opsiyonel - sipariş takibi için)


## Components and Interfaces

### 1. Backend Components

#### Helper Functions (utils/helpers.py)

**get_kat_sorumlusu_zimmet_stoklari(personel_id)**
```python
"""
Kat sorumlusunun aktif zimmet stoklarını detaylı şekilde getirir

Args:
    personel_id (int): Kat sorumlusu kullanıcı ID

Returns:
    list: [
        {
            'zimmet_id': int,
            'zimmet_tarihi': datetime,
            'teslim_eden': str,
            'durum': str,
            'urunler': [
                {
                    'urun_id': int,
                    'urun_adi': str,
                    'grup_adi': str,
                    'birim': str,
                    'teslim_edilen': int,
                    'kullanilan': int,
                    'kalan': int,
                    'kritik_seviye': int or None,
                    'kullanim_yuzdesi': float,
                    'durum': 'kritik'|'dikkat'|'normal'|'stokout',
                    'badge_class': str,
                    'badge_text': str
                }
            ]
        }
    ]
"""
```

**get_kat_sorumlusu_kritik_stoklar(personel_id)**
```python
"""
Kat sorumlusunun kritik seviyedeki ürünlerini getirir

Args:
    personel_id (int): Kat sorumlusu kullanıcı ID

Returns:
    dict: {
        'stokout': [],      # Stok sıfır olan ürünler
        'kritik': [],       # Kritik seviyenin altındaki ürünler
        'dikkat': [],       # Kritik seviyenin %50-100 arasındaki ürünler
        'risk': [],         # Kritik seviyenin %100-150 arasındaki ürünler
        'istatistik': {
            'toplam_urun': int,
            'stokout_sayisi': int,
            'kritik_sayisi': int,
            'dikkat_sayisi': int
        }
    }
"""
```

**olustur_otomatik_siparis(personel_id, guvenlik_marji=1.5)**
```python
"""
Kritik seviyedeki ürünler için otomatik sipariş listesi oluşturur

Args:
    personel_id (int): Kat sorumlusu kullanıcı ID
    guvenlik_marji (float): Kritik seviyenin kaç katı sipariş edilsin (default: 1.5)

Returns:
    dict: {
        'siparis_listesi': [
            {
                'urun_id': int,
                'urun_adi': str,
                'mevcut_stok': int,
                'kritik_seviye': int,
                'onerilen_miktar': int,
                'aciliyet': 'acil'|'normal'
            }
        ],
        'toplam_urun_sayisi': int,
        'toplam_miktar': int
    }
"""
```

**kaydet_siparis_talebi(personel_id, siparis_listesi, aciklama=None)**
```python
"""
Sipariş talebini kaydeder ve depo sorumlusuna bildirim gönderir

Args:
    personel_id (int): Kat sorumlusu kullanıcı ID
    siparis_listesi (list): Sipariş edilecek ürünler
    aciklama (str, optional): Ek açıklama

Returns:
    dict: {
        'success': bool,
        'siparis_id': int,
        'message': str
    }
"""
```

**get_zimmet_urun_gecmisi(personel_id, urun_id, gun_sayisi=30)**
```python
"""
Belirli bir ürünün kullanım geçmişini getirir

Args:
    personel_id (int): Kat sorumlusu kullanıcı ID
    urun_id (int): Ürün ID
    gun_sayisi (int): Kaç günlük geçmiş (default: 30)

Returns:
    dict: {
        'urun': Urun object,
        'hareketler': [
            {
                'tarih': datetime,
                'islem_tipi': str,
                'oda_no': str,
                'miktar': int,
                'aciklama': str
            }
        ],
        'istatistik': {
            'toplam_kullanim': int,
            'gunluk_ortalama': float,
            'en_cok_kullanilan_gun': datetime,
            'en_az_kullanilan_gun': datetime
        }
    }
"""
```

**guncelle_kritik_seviye(zimmet_detay_id, kritik_seviye)**
```python
"""
Zimmet detayındaki ürün için kritik stok seviyesi günceller

Args:
    zimmet_detay_id (int): PersonelZimmetDetay ID
    kritik_seviye (int): Yeni kritik seviye

Returns:
    dict: {
        'success': bool,
        'message': str
    }
"""
```

**export_zimmet_stok_excel(personel_id)**
```python
"""
Kat sorumlusunun zimmet stoklarını Excel'e export eder

Args:
    personel_id (int): Kat sorumlusu kullanıcı ID

Returns:
    BytesIO: Excel dosyası buffer
"""
```

#### Route Handlers (app.py)

**Yeni Route'lar:**
- `/kat-sorumlusu/zimmet-stoklarim` - Zimmet stok listesi
- `/kat-sorumlusu/kritik-stoklar` - Kritik stok sayfası
- `/kat-sorumlusu/siparis-hazirla` - Sipariş hazırlama
- `/kat-sorumlusu/urun-gecmisi/<urun_id>` - Ürün kullanım geçmişi
- `/api/kat-sorumlusu/kritik-seviye-guncelle` - AJAX kritik seviye güncelleme
- `/api/kat-sorumlusu/siparis-kaydet` - AJAX sipariş kaydetme
- `/kat-sorumlusu/zimmet-export` - Excel export

### 2. Frontend Components

#### Dashboard Kartları
- **Toplam Zimmet Ürün Sayısı**: Aktif zimmetteki toplam ürün adedi
- **Kritik Stok Sayısı**: Kritik seviyenin altındaki ürün sayısı (kırmızı vurgu)
- **Stokout Ürün Sayısı**: Stok sıfır olan ürün sayısı (kırmızı vurgu)
- **Bugünkü Kullanım**: Bugün kullanılan toplam ürün adedi

#### Grafikler
- **En Çok Kullanılan Ürünler**: Bar chart (Chart.js)
- **Zimmet Kullanım Durumu**: Doughnut chart (kullanılan vs kalan)
- **Günlük Tüketim Trendi**: Line chart (son 7 gün)

#### Tablolar
- **Zimmet Stok Listesi**: Tüm aktif zimmetler ve detayları
- **Kritik Stok Listesi**: Kritik seviyedeki ürünler
- **Sipariş Listesi**: Hazırlanan sipariş önerileri

#### Modal/Dialog
- **Kritik Seviye Belirleme**: Input modal
- **Sipariş Onaylama**: Confirmation modal
- **Ürün Geçmişi**: Detail modal


## Data Models

### Mevcut Modeller (Değişiklik Yok)

**PersonelZimmet**
```python
id: Integer (PK)
personel_id: Integer (FK -> Kullanici)
zimmet_tarihi: DateTime
teslim_eden_id: Integer (FK -> Kullanici)
durum: Enum('aktif', 'tamamlandi', 'iptal')
aciklama: Text
```

**PersonelZimmetDetay**
```python
id: Integer (PK)
zimmet_id: Integer (FK -> PersonelZimmet)
urun_id: Integer (FK -> Urun)
miktar: Integer
kullanilan_miktar: Integer
kalan_miktar: Integer
iade_edilen_miktar: Integer
```

### Veritabanı Değişiklikleri

**PersonelZimmetDetay - Yeni Alan**
```python
kritik_stok_seviyesi: Integer (nullable=True, default=None)
# Kat sorumlusu her zimmet detayı için kendi kritik seviyesini belirleyebilir
# NULL ise, ürünün genel kritik_stok_seviyesi kullanılır
```

**Migration Script:**
```python
# Migration: add_kritik_seviye_to_zimmet_detay
def upgrade():
    op.add_column('personel_zimmet_detay', 
        sa.Column('kritik_stok_seviyesi', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('personel_zimmet_detay', 'kritik_stok_seviyesi')
```

### Yeni Model (Opsiyonel - Sipariş Takibi İçin)

**SiparisIstek**
```python
__tablename__ = 'siparis_istekleri'

id: Integer (PK)
personel_id: Integer (FK -> Kullanici)
olusturma_tarihi: DateTime (default=now)
durum: Enum('beklemede', 'onaylandi', 'tamamlandi', 'iptal')
aciklama: Text
onaylayan_id: Integer (FK -> Kullanici, nullable)
onay_tarihi: DateTime (nullable)
tamamlanma_tarihi: DateTime (nullable)

# İlişkiler
detaylar: relationship('SiparisIstekDetay')
```

**SiparisIstekDetay**
```python
__tablename__ = 'siparis_istek_detay'

id: Integer (PK)
siparis_id: Integer (FK -> SiparisIstek)
urun_id: Integer (FK -> Urun)
talep_edilen_miktar: Integer
onaylanan_miktar: Integer (nullable)
aciliyet: Enum('normal', 'acil')
```

## Error Handling

### Hata Kategorileri

**1. Veri Doğrulama Hataları**
- Kritik seviye negatif veya sıfır
- Sipariş miktarı geçersiz
- Zimmet bulunamadı

**Yaklaşım:**
```python
try:
    if kritik_seviye <= 0:
        return {
            'success': False,
            'message': 'Kritik seviye pozitif bir sayı olmalıdır'
        }
except ValueError:
    flash('Geçersiz değer girdiniz', 'danger')
    log_hata(e, modul='kat_sorumlusu_stok')
```

**2. Veritabanı Hataları**
- Kayıt bulunamadı
- Foreign key constraint
- Transaction rollback

**Yaklaşım:**
```python
try:
    db.session.commit()
except IntegrityError as e:
    db.session.rollback()
    log_hata(e, modul='kat_sorumlusu_stok')
    flash('Veritabanı hatası oluştu', 'danger')
```

**3. İş Mantığı Hataları**
- Aktif zimmet yok
- Sipariş listesi boş
- Yetki hatası

**Yaklaşım:**
```python
if not aktif_zimmetler:
    flash('Aktif zimmetiniz bulunmamaktadır', 'warning')
    return redirect(url_for('kat_sorumlusu_dashboard'))
```

### Loglama Stratejisi

**Başarılı İşlemler:**
```python
log_islem('guncelleme', 'kritik_seviye', {
    'zimmet_detay_id': detay_id,
    'eski_seviye': eski_seviye,
    'yeni_seviye': yeni_seviye
})
```

**Hatalar:**
```python
log_hata(exception, 
    modul='kat_sorumlusu_stok',
    extra_info={
        'function': 'olustur_otomatik_siparis',
        'personel_id': personel_id
    }
)
```

**Audit Trail:**
```python
from utils.audit import audit_update

audit_update(
    tablo_adi='personel_zimmet_detay',
    kayit_id=detay.id,
    eski_deger=serialize_model(detay),
    yeni_deger=detay,
    aciklama='Kritik stok seviyesi güncellendi'
)
```


## Testing Strategy

### Unit Tests

**Test Edilecek Fonksiyonlar:**

1. **get_kat_sorumlusu_zimmet_stoklari()**
   - Aktif zimmetleri doğru getiriyor mu?
   - Kullanım yüzdesi doğru hesaplanıyor mu?
   - Stok durumu kategorileri doğru mu?

2. **get_kat_sorumlusu_kritik_stoklar()**
   - Kritik seviye karşılaştırması doğru mu?
   - Stokout ürünler doğru tespit ediliyor mu?
   - İstatistikler doğru hesaplanıyor mu?

3. **olustur_otomatik_siparis()**
   - Sipariş miktarı doğru hesaplanıyor mu?
   - Güvenlik marjı uygulanıyor mu?
   - Aciliyet seviyeleri doğru belirleniyor mu?

4. **guncelle_kritik_seviye()**
   - Kritik seviye güncellemesi başarılı mı?
   - Geçersiz değerler reddediliyor mu?
   - Audit log kaydı oluşuyor mu?

**Test Örneği:**
```python
def test_get_kritik_stoklar():
    # Arrange
    personel = create_test_personel()
    zimmet = create_test_zimmet(personel.id)
    detay = create_test_zimmet_detay(
        zimmet.id, 
        kalan_miktar=5, 
        kritik_seviye=10
    )
    
    # Act
    sonuc = get_kat_sorumlusu_kritik_stoklar(personel.id)
    
    # Assert
    assert len(sonuc['kritik']) == 1
    assert sonuc['istatistik']['kritik_sayisi'] == 1
    assert sonuc['kritik'][0]['urun_id'] == detay.urun_id
```

### Integration Tests

**Test Senaryoları:**

1. **Zimmet Stok Görüntüleme Flow**
   - Login → Dashboard → Zimmet Stoklarım
   - Tüm veriler doğru görüntüleniyor mu?

2. **Kritik Seviye Belirleme Flow**
   - Zimmet detay → Kritik seviye modal → Kaydet
   - Güncelleme başarılı mı?
   - Flash mesaj gösteriliyor mu?

3. **Sipariş Hazırlama Flow**
   - Kritik stoklar → Sipariş hazırla → Düzenle → Kaydet
   - Sipariş kaydı oluşuyor mu?
   - Bildirim gönderiliyor mu?

### Manual Testing Checklist

**Dashboard:**
- [ ] Kartlar doğru sayıları gösteriyor
- [ ] Grafikler yükleniyor
- [ ] Kritik stok kartı kırmızı vurgulu
- [ ] Yenile butonu çalışıyor

**Zimmet Stoklarım:**
- [ ] Tüm aktif zimmetler listeleniyor
- [ ] Progress bar'lar doğru
- [ ] Kritik ürünler vurgulu
- [ ] Detay sayfası açılıyor

**Kritik Stoklar:**
- [ ] Stokout ürünler en üstte
- [ ] Renk kodlaması doğru
- [ ] Eksik miktar hesaplaması doğru
- [ ] Filtreleme çalışıyor

**Sipariş Hazırlama:**
- [ ] Otomatik liste oluşuyor
- [ ] Manuel düzenleme yapılabiliyor
- [ ] Onay modalı çalışıyor
- [ ] Sipariş kaydediliyor

**Ürün Geçmişi:**
- [ ] Hareketler listeleniyor
- [ ] Grafik görünümü çalışıyor
- [ ] Tarih filtresi çalışıyor
- [ ] Excel export çalışıyor

### Performance Testing

**Hedefler:**
- Dashboard yükleme: < 2 saniye
- Zimmet listesi: < 1 saniye
- Kritik stok hesaplama: < 500ms
- Excel export: < 3 saniye

**Optimizasyon Stratejileri:**
- Eager loading (joinedload) kullan
- Stok hesaplamalarını cache'le
- Pagination uygula (sayfa başı 50 kayıt)
- Index'leri optimize et

## UI/UX Design Patterns

### Renk Kodlaması

**Stok Durumları:**
- 🔴 Stokout: `bg-red-100 text-red-800 border-red-300`
- 🔴 Kritik: `bg-red-100 text-red-800 border-red-300`
- 🟡 Dikkat: `bg-yellow-100 text-yellow-800 border-yellow-300`
- 🟢 Normal: `bg-green-100 text-green-800 border-green-300`

**Aciliyet Seviyeleri:**
- 🔴 Acil: `bg-red-600 text-white`
- 🔵 Normal: `bg-blue-600 text-white`

### Progress Bar Gösterimi

```html
<!-- Kullanım Yüzdesi -->
<div class="w-full bg-gray-200 rounded-full h-2.5">
    <div class="bg-blue-600 h-2.5 rounded-full" 
         style="width: {{ kullanim_yuzdesi }}%"></div>
</div>
<span class="text-sm text-gray-600">
    {{ kullanilan }} / {{ toplam }} ({{ kullanim_yuzdesi }}%)
</span>
```

### Badge Gösterimi

```html
<!-- Stok Durumu Badge -->
<span class="{{ badge_class }} px-2 py-1 rounded-full text-xs font-medium">
    {{ badge_text }}
</span>
```

### Modal Yapısı

```html
<!-- Kritik Seviye Modal -->
<div id="kritikSeviyeModal" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50">
    <div class="bg-white rounded-lg p-6 max-w-md mx-auto mt-20">
        <h3 class="text-lg font-semibold mb-4">Kritik Stok Seviyesi Belirle</h3>
        <form id="kritikSeviyeForm">
            <input type="number" name="kritik_seviye" 
                   class="w-full border rounded px-3 py-2" 
                   min="1" required>
            <div class="mt-4 flex gap-2">
                <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded">
                    Kaydet
                </button>
                <button type="button" class="bg-gray-300 px-4 py-2 rounded">
                    İptal
                </button>
            </div>
        </form>
    </div>
</div>
```

### Responsive Design

**Breakpoints:**
- Mobile: < 640px (tek sütun)
- Tablet: 640px - 1024px (2 sütun)
- Desktop: > 1024px (3-4 sütun)

**Grid Layout:**
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Kartlar -->
</div>
```

## Security Considerations

### Yetkilendirme

**Route Koruma:**
```python
@app.route('/kat-sorumlusu/zimmet-stoklarim')
@login_required
@role_required('kat_sorumlusu')
def zimmet_stoklarim():
    # Sadece kat sorumlusu erişebilir
```

**Veri İzolasyonu:**
```python
# Kullanıcı sadece kendi zimmetlerini görebilir
zimmetler = PersonelZimmet.query.filter_by(
    personel_id=session['kullanici_id'],
    durum='aktif'
).all()
```

### Input Validation

**Backend Validation:**
```python
if not isinstance(kritik_seviye, int) or kritik_seviye <= 0:
    return jsonify({
        'success': False,
        'message': 'Kritik seviye pozitif bir tam sayı olmalıdır'
    }), 400
```

**Frontend Validation:**
```html
<input type="number" min="1" max="9999" required>
```

### CSRF Protection

**Form Token:**
```html
<form method="POST">
    {{ form.csrf_token }}
    <!-- Form fields -->
</form>
```

**AJAX Request:**
```javascript
fetch('/api/kat-sorumlusu/kritik-seviye-guncelle', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
    },
    body: JSON.stringify(data)
})
```

### SQL Injection Prevention

**ORM Kullanımı:**
```python
# ✅ Güvenli - ORM kullanımı
PersonelZimmet.query.filter_by(personel_id=personel_id).all()

# ❌ Güvensiz - Raw SQL
db.session.execute(f"SELECT * FROM personel_zimmet WHERE personel_id = {personel_id}")
```

## Implementation Notes

### Aşamalı Geliştirme

**Faz 1: Temel Görüntüleme**
- Zimmet stok listesi
- Dashboard kartları
- Kritik stok listesi

**Faz 2: Kritik Seviye Yönetimi**
- Kritik seviye belirleme
- Stok durumu hesaplama
- Uyarı sistemi

**Faz 3: Sipariş Sistemi**
- Otomatik sipariş hazırlama
- Sipariş kaydetme
- Bildirim sistemi

**Faz 4: Raporlama**
- Ürün geçmişi
- Grafikler
- Excel export

### Mevcut Kod ile Entegrasyon

**Kullanılacak Mevcut Fonksiyonlar:**
- `get_current_user()`: Kullanıcı bilgisi
- `log_islem()`, `log_hata()`: Loglama
- `format_tarih()`: Tarih formatlama
- `audit_create()`, `audit_update()`: Audit trail

**Kullanılacak Mevcut Template'ler:**
- `base.html`: Ana layout
- `_form_helpers.html`: Form makroları
- Tailwind CSS sınıfları

### Veritabanı Migration

```python
# migrations/versions/xxx_add_kritik_seviye.py
"""Add kritik_stok_seviyesi to PersonelZimmetDetay

Revision ID: xxx
Revises: yyy
Create Date: 2025-xx-xx
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('personel_zimmet_detay', 
        sa.Column('kritik_stok_seviyesi', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('personel_zimmet_detay', 'kritik_stok_seviyesi')
```

### Backward Compatibility

**Kritik Seviye Fallback:**
```python
# Zimmet detayında kritik seviye yoksa, ürünün genel seviyesini kullan
kritik_seviye = detay.kritik_stok_seviyesi or detay.urun.kritik_stok_seviyesi
```

**Mevcut Dashboard Koruması:**
```python
# Mevcut dashboard fonksiyonalitesi korunur
# Yeni özellikler ek route'lar olarak eklenir
```
