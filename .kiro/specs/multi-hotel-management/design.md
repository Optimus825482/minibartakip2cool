# Çoklu Otel Yönetim Sistemi - Tasarım Dokümanı

## Genel Bakış

Bu doküman, mevcut tek otel sisteminin çoklu otel desteğine dönüştürülmesi için teknik tasarımı içerir. Sistem, veritabanı şeması değişiklikleri, yeni ara tablolar, route güncellemeleri ve kullanıcı arayüzü değişikliklerini kapsar.

## Mimari

### Katmanlı Yapı

```
┌─────────────────────────────────────┐
│   Presentation Layer (Templates)    │
│  - Otel seçim dropdown'ları         │
│  - Hiyerarşik form yapıları         │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│   Application Layer (Routes)        │
│  - admin_routes.py (Otel CRUD)      │
│  - admin_user_routes.py (Atamalar)  │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│   Business Logic Layer              │
│  - Yetkilendirme kontrolleri        │
│  - Otel bazlı filtreleme            │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│   Data Layer (Models)               │
│  - KullaniciOtel (Many-to-Many)     │
│  - Otel, Kat, Oda ilişkileri        │
└─────────────────────────────────────┘
```

## Veri Modeli Değişiklikleri

### 1. Yeni Ara Tablo: KullaniciOtel

Depo sorumlularının birden fazla otele atanması için many-to-many ilişki tablosu:

```python
class KullaniciOtel(db.Model):
    """Kullanıcı-Otel ilişki tablosu (Many-to-Many)"""
    __tablename__ = 'kullanici_otel'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=False)
    otel_id = db.Column(db.Integer, db.ForeignKey('oteller.id'), nullable=False)
    olusturma_tarihi = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Unique constraint - Aynı kullanıcı aynı otele birden fazla kez atanamaz
    __table_args__ = (
        db.UniqueConstraint('kullanici_id', 'otel_id', name='uq_kullanici_otel'),
        db.Index('idx_kullanici_otel', 'kullanici_id', 'otel_id'),
    )
```

### 2. Kullanici Model Güncellemesi

```python
class Kullanici(db.Model):
    # ... mevcut alanlar ...
    
    # YENİ: Kat sorumlusu için tek otel ilişkisi
    otel_id = db.Column(db.Integer, db.ForeignKey('oteller.id'), nullable=True)
    
    # YENİ: İlişkiler
    otel = db.relationship('Otel', foreign_keys=[otel_id], backref='kat_sorumlu_kullanicilar')
    atanan_oteller = db.relationship('KullaniciOtel', backref='kullanici', lazy=True, cascade='all, delete-orphan')
```


### 3. Otel Model Güncellemesi

```python
class Otel(db.Model):
    # ... mevcut alanlar ...
    
    # YENİ: İlişkiler
    kullanici_atamalari = db.relationship('KullaniciOtel', backref='otel', lazy=True, cascade='all, delete-orphan')
    
    def get_depo_sorumlu_sayisi(self):
        """Bu otele atanan depo sorumlusu sayısı"""
        return KullaniciOtel.query.join(Kullanici).filter(
            KullaniciOtel.otel_id == self.id,
            Kullanici.rol == 'depo_sorumlusu'
        ).count()
    
    def get_kat_sorumlu_sayisi(self):
        """Bu otele atanan kat sorumlusu sayısı"""
        return Kullanici.query.filter(
            Kullanici.otel_id == self.id,
            Kullanici.rol == 'kat_sorumlusu'
        ).count()
```

## Bileşenler ve Arayüzler

### 1. Otel Yönetimi Sayfaları

#### a) Otel Listesi (`/admin/oteller`)
- Tüm otellerin listesi
- Sütunlar: ID, Otel Adı, Telefon, Email, Kat Sayısı, Oda Sayısı, Personel Sayısı, Durum
- Aksiyonlar: Düzenle, Aktif/Pasif Yap

#### b) Otel Ekleme/Düzenleme Formu
```python
class OtelForm(FlaskForm):
    ad = StringField('Otel Adı', validators=[DataRequired(), Length(max=200)])
    adres = TextAreaField('Adres')
    telefon = StringField('Telefon', validators=[Length(max=20)])
    email = StringField('Email', validators=[Email(), Length(max=100)])
    vergi_no = StringField('Vergi No', validators=[Length(max=50)])
    aktif = BooleanField('Aktif', default=True)
```

### 2. Kat Yönetimi Güncellemeleri

#### Kat Formu Güncelleme
```python
class KatForm(FlaskForm):
    otel_id = SelectField('Otel', coerce=int, validators=[DataRequired()])
    kat_adi = StringField('Kat Adı', validators=[DataRequired()])
    kat_no = IntegerField('Kat No', validators=[DataRequired()])
    aciklama = TextAreaField('Açıklama')
    aktif = BooleanField('Aktif', default=True)
```

### 3. Oda Yönetimi Güncellemeleri

#### Oda Formu Güncelleme
```python
class OdaForm(FlaskForm):
    otel_id = SelectField('Otel', coerce=int, validators=[DataRequired()])
    kat_id = SelectField('Kat', coerce=int, validators=[DataRequired()])
    oda_no = StringField('Oda No', validators=[DataRequired()])
    oda_tipi = StringField('Oda Tipi')
    kapasite = IntegerField('Kapasite')
    aktif = BooleanField('Aktif', default=True)
```

#### JavaScript Dinamik Kat Yükleme
```javascript
// Otel seçildiğinde katları yükle
$('#otel_id').change(function() {
    var otel_id = $(this).val();
    $.ajax({
        url: '/api/oteller/' + otel_id + '/katlar',
        success: function(data) {
            $('#kat_id').empty();
            $('#kat_id').append('<option value="">Kat Seçin</option>');
            data.forEach(function(kat) {
                $('#kat_id').append('<option value="' + kat.id + '">' + kat.kat_adi + '</option>');
            });
        }
    });
});
```


### 4. Kullanıcı Atama Güncellemeleri

#### Depo Sorumlusu Formu (Çoklu Otel)
```python
class DepoSorumlusuForm(FlaskForm):
    kullanici_adi = StringField('Kullanıcı Adı', validators=[DataRequired()])
    ad = StringField('Ad', validators=[DataRequired()])
    soyad = StringField('Soyad', validators=[DataRequired()])
    email = StringField('Email', validators=[Email()])
    telefon = StringField('Telefon')
    sifre = PasswordField('Şifre', validators=[DataRequired()])
    otel_ids = SelectMultipleField('Oteller', coerce=int, validators=[DataRequired()])
    aktif = BooleanField('Aktif', default=True)
```

#### Kat Sorumlusu Formu (Tekli Otel)
```python
class KatSorumlusuForm(FlaskForm):
    kullanici_adi = StringField('Kullanıcı Adı', validators=[DataRequired()])
    ad = StringField('Ad', validators=[DataRequired()])
    soyad = StringField('Soyad', validators=[DataRequired()])
    email = StringField('Email', validators=[Email()])
    telefon = StringField('Telefon')
    sifre = PasswordField('Şifre', validators=[DataRequired()])
    otel_id = SelectField('Otel', coerce=int, validators=[DataRequired()])
    aktif = BooleanField('Aktif', default=True)
```

## API Endpoints

### Yeni Endpoint'ler

```python
# Otel CRUD
GET    /admin/oteller                    # Otel listesi
GET    /admin/oteller/ekle               # Otel ekleme formu
POST   /admin/oteller/ekle               # Otel kaydet
GET    /admin/oteller/<id>/duzenle       # Otel düzenleme formu
POST   /admin/oteller/<id>/duzenle       # Otel güncelle
POST   /admin/oteller/<id>/aktif-pasif   # Otel aktif/pasif yap

# API - Dinamik veri yükleme
GET    /api/oteller/<id>/katlar          # Otele ait katları getir
GET    /api/oteller/<id>/odalar          # Otele ait odaları getir
GET    /api/katlar/<id>/odalar           # Kata ait odaları getir
```

### Güncellenecek Endpoint'ler

```python
# Kat yönetimi
GET    /admin/katlar                     # Otel bilgisi eklenecek
POST   /admin/katlar/ekle                # Otel seçimi eklenecek
POST   /admin/katlar/<id>/duzenle        # Otel değiştirme eklenecek

# Oda yönetimi
GET    /admin/odalar                     # Otel bilgisi eklenecek
POST   /admin/odalar/ekle                # Otel+Kat seçimi eklenecek
POST   /admin/odalar/<id>/duzenle        # Otel+Kat değiştirme eklenecek

# Kullanıcı yönetimi
POST   /admin/kullanicilar/depo-sorumlusu/ekle      # Çoklu otel seçimi
POST   /admin/kullanicilar/kat-sorumlusu/ekle       # Tekli otel seçimi
```

## Yetkilendirme ve Filtreleme

### 1. Depo Sorumlusu Yetkilendirmesi

```python
def get_depo_sorumlusu_oteller(kullanici_id):
    """Depo sorumlusunun erişebileceği oteller"""
    return db.session.query(Otel).join(KullaniciOtel).filter(
        KullaniciOtel.kullanici_id == kullanici_id
    ).all()

def depo_sorumlusu_otel_erisimi(kullanici_id, otel_id):
    """Depo sorumlusunun belirli bir otele erişimi var mı?"""
    return KullaniciOtel.query.filter_by(
        kullanici_id=kullanici_id,
        otel_id=otel_id
    ).first() is not None
```

### 2. Kat Sorumlusu Yetkilendirmesi

```python
def get_kat_sorumlusu_otel(kullanici_id):
    """Kat sorumlusunun atandığı otel"""
    kullanici = Kullanici.query.get(kullanici_id)
    return kullanici.otel if kullanici else None

def kat_sorumlusu_otel_erisimi(kullanici_id, otel_id):
    """Kat sorumlusunun belirli bir otele erişimi var mı?"""
    kullanici = Kullanici.query.get(kullanici_id)
    return kullanici and kullanici.otel_id == otel_id
```


### 3. Decorator'lar

```python
from functools import wraps
from flask import abort, session

def otel_erisim_gerekli(f):
    """Kullanıcının otele erişimi olup olmadığını kontrol eder"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        otel_id = kwargs.get('otel_id') or request.args.get('otel_id')
        kullanici_id = session.get('kullanici_id')
        kullanici = Kullanici.query.get(kullanici_id)
        
        if not kullanici:
            abort(401)
        
        # Sistem yöneticisi ve admin tüm otellere erişebilir
        if kullanici.rol in ['sistem_yoneticisi', 'admin']:
            return f(*args, **kwargs)
        
        # Depo sorumlusu - atandığı otellere erişebilir
        if kullanici.rol == 'depo_sorumlusu':
            if not depo_sorumlusu_otel_erisimi(kullanici_id, otel_id):
                abort(403)
        
        # Kat sorumlusu - sadece kendi oteline erişebilir
        elif kullanici.rol == 'kat_sorumlusu':
            if not kat_sorumlusu_otel_erisimi(kullanici_id, otel_id):
                abort(403)
        
        return f(*args, **kwargs)
    return decorated_function
```

## Veri Migrasyonu

### Migration Script

```python
"""
Mevcut verileri çoklu otel sistemine taşıma
"""

def migrate_to_multi_hotel():
    try:
        # 1. Merit Royal Diamond oteli oluştur
        merit_otel = Otel.query.filter_by(ad='Merit Royal Diamond').first()
        if not merit_otel:
            merit_otel = Otel(
                ad='Merit Royal Diamond',
                adres='',
                telefon='',
                email='',
                vergi_no='',
                aktif=True
            )
            db.session.add(merit_otel)
            db.session.flush()
        
        # 2. Tüm katları Merit Royal Diamond'a ata
        katlar = Kat.query.filter(Kat.otel_id.is_(None)).all()
        for kat in katlar:
            kat.otel_id = merit_otel.id
        
        # 3. Tüm kat sorumlularını Merit Royal Diamond'a ata
        kat_sorumlu_list = Kullanici.query.filter_by(rol='kat_sorumlusu').all()
        for kat_sorumlu in kat_sorumlu_list:
            if not kat_sorumlu.otel_id:
                kat_sorumlu.otel_id = merit_otel.id
        
        # 4. Tüm depo sorumlularını Merit Royal Diamond'a ata
        depo_sorumlu_list = Kullanici.query.filter_by(rol='depo_sorumlusu').all()
        for depo_sorumlu in depo_sorumlu_list:
            # Zaten atama var mı kontrol et
            existing = KullaniciOtel.query.filter_by(
                kullanici_id=depo_sorumlu.id,
                otel_id=merit_otel.id
            ).first()
            
            if not existing:
                atama = KullaniciOtel(
                    kullanici_id=depo_sorumlu.id,
                    otel_id=merit_otel.id
                )
                db.session.add(atama)
        
        db.session.commit()
        print("✅ Migrasyon başarılı!")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Migrasyon hatası: {str(e)}")
        raise
```

## Hata Yönetimi

### 1. Validasyon Hataları

```python
# Otel seçimi zorunlu
if not form.otel_id.data:
    flash('Lütfen bir otel seçin!', 'error')
    return redirect(url_for('admin.kat_ekle'))

# Kat sorumlusu zaten başka otele atanmış
if kullanici.otel_id and kullanici.otel_id != form.otel_id.data:
    flash('Bu kat sorumlusu zaten başka bir otele atanmış!', 'error')
    return redirect(url_for('admin.kullanici_listesi'))
```

### 2. Silme Korumaları

```python
@admin_bp.route('/oteller/<int:id>/sil', methods=['POST'])
def otel_sil(id):
    otel = Otel.query.get_or_404(id)
    
    # Otele ait kat var mı?
    if otel.katlar:
        flash('Bu otele ait katlar bulunuyor. Önce katları silin veya başka otele taşıyın!', 'error')
        return redirect(url_for('admin.otel_listesi'))
    
    # Otele atanmış personel var mı?
    if otel.get_depo_sorumlu_sayisi() > 0 or otel.get_kat_sorumlu_sayisi() > 0:
        flash('Bu otele atanmış personel bulunuyor. Önce personel atamalarını kaldırın!', 'error')
        return redirect(url_for('admin.otel_listesi'))
    
    # Güvenli silme
    db.session.delete(otel)
    db.session.commit()
    flash('Otel başarıyla silindi!', 'success')
    return redirect(url_for('admin.otel_listesi'))
```


## Test Stratejisi

### 1. Unit Tests

```python
# test_otel_model.py
def test_otel_olusturma():
    """Otel oluşturma testi"""
    otel = Otel(ad='Test Otel', aktif=True)
    db.session.add(otel)
    db.session.commit()
    assert otel.id is not None

def test_depo_sorumlusu_coklu_otel():
    """Depo sorumlusu çoklu otel ataması testi"""
    kullanici = Kullanici(kullanici_adi='depo1', rol='depo_sorumlusu')
    otel1 = Otel(ad='Otel 1')
    otel2 = Otel(ad='Otel 2')
    
    db.session.add_all([kullanici, otel1, otel2])
    db.session.commit()
    
    atama1 = KullaniciOtel(kullanici_id=kullanici.id, otel_id=otel1.id)
    atama2 = KullaniciOtel(kullanici_id=kullanici.id, otel_id=otel2.id)
    
    db.session.add_all([atama1, atama2])
    db.session.commit()
    
    assert len(kullanici.atanan_oteller) == 2

def test_kat_sorumlusu_tekli_otel():
    """Kat sorumlusu tekli otel ataması testi"""
    kullanici = Kullanici(kullanici_adi='kat1', rol='kat_sorumlusu')
    otel = Otel(ad='Otel 1')
    
    db.session.add_all([kullanici, otel])
    db.session.commit()
    
    kullanici.otel_id = otel.id
    db.session.commit()
    
    assert kullanici.otel_id == otel.id
    assert kullanici.otel.ad == 'Otel 1'
```

### 2. Integration Tests

```python
# test_otel_routes.py
def test_otel_listesi_erisim(client, auth):
    """Otel listesi sayfası erişim testi"""
    auth.login('admin', 'admin123')
    response = client.get('/admin/oteller')
    assert response.status_code == 200
    assert b'Otel Listesi' in response.data

def test_otel_ekleme(client, auth):
    """Otel ekleme testi"""
    auth.login('admin', 'admin123')
    response = client.post('/admin/oteller/ekle', data={
        'ad': 'Yeni Otel',
        'telefon': '1234567890',
        'email': 'info@yenotel.com',
        'aktif': True
    })
    assert response.status_code == 302  # Redirect
    
    otel = Otel.query.filter_by(ad='Yeni Otel').first()
    assert otel is not None

def test_kat_otel_secimi(client, auth):
    """Kat eklerken otel seçimi testi"""
    auth.login('admin', 'admin123')
    otel = Otel(ad='Test Otel')
    db.session.add(otel)
    db.session.commit()
    
    response = client.post('/admin/katlar/ekle', data={
        'otel_id': otel.id,
        'kat_adi': 'Zemin Kat',
        'kat_no': 0,
        'aktif': True
    })
    assert response.status_code == 302
    
    kat = Kat.query.filter_by(kat_adi='Zemin Kat').first()
    assert kat.otel_id == otel.id
```

### 3. Yetkilendirme Tests

```python
# test_authorization.py
def test_depo_sorumlusu_otel_erisimi(client, auth):
    """Depo sorumlusu sadece atandığı otellere erişebilir"""
    # Setup
    otel1 = Otel(ad='Otel 1')
    otel2 = Otel(ad='Otel 2')
    kullanici = Kullanici(kullanici_adi='depo1', rol='depo_sorumlusu')
    db.session.add_all([otel1, otel2, kullanici])
    db.session.commit()
    
    # Sadece otel1'e ata
    atama = KullaniciOtel(kullanici_id=kullanici.id, otel_id=otel1.id)
    db.session.add(atama)
    db.session.commit()
    
    auth.login('depo1', 'password')
    
    # Otel1'e erişebilir
    response = client.get(f'/depo/stok?otel_id={otel1.id}')
    assert response.status_code == 200
    
    # Otel2'ye erişemez
    response = client.get(f'/depo/stok?otel_id={otel2.id}')
    assert response.status_code == 403

def test_kat_sorumlusu_otel_erisimi(client, auth):
    """Kat sorumlusu sadece kendi oteline erişebilir"""
    otel1 = Otel(ad='Otel 1')
    otel2 = Otel(ad='Otel 2')
    kullanici = Kullanici(kullanici_adi='kat1', rol='kat_sorumlusu', otel_id=otel1.id)
    db.session.add_all([otel1, otel2, kullanici])
    db.session.commit()
    
    auth.login('kat1', 'password')
    
    # Kendi oteline erişebilir
    response = client.get(f'/kat-sorumlusu/odalar?otel_id={otel1.id}')
    assert response.status_code == 200
    
    # Başka otele erişemez
    response = client.get(f'/kat-sorumlusu/odalar?otel_id={otel2.id}')
    assert response.status_code == 403
```

## UI/UX Tasarım Notları

### 1. Otel Seçim Dropdown'ları

- **Stil**: Bootstrap Select2 kullanılacak (arama özelliği için)
- **Placeholder**: "Otel Seçin..."
- **Sıralama**: Alfabetik
- **Aktif/Pasif**: Sadece aktif oteller gösterilecek

### 2. Hiyerarşik Form Yapısı

```
┌─────────────────────────────┐
│  Otel Seçin ▼              │
└─────────────────────────────┘
         ↓ (seçim yapılınca)
┌─────────────────────────────┐
│  Kat Seçin ▼               │
└─────────────────────────────┘
         ↓ (seçim yapılınca)
┌─────────────────────────────┐
│  Oda Bilgileri             │
│  [Oda No]                  │
│  [Oda Tipi]                │
└─────────────────────────────┘
```

### 3. Tablo Görünümleri

**Otel Listesi:**
| ID | Otel Adı | Telefon | Kat Sayısı | Oda Sayısı | Personel | Durum | İşlemler |
|----|----------|---------|------------|------------|----------|-------|----------|

**Kat Listesi (Güncellenmiş):**
| ID | Otel | Kat Adı | Kat No | Oda Sayısı | Durum | İşlemler |
|----|------|---------|--------|------------|-------|----------|

**Oda Listesi (Güncellenmiş):**
| ID | Otel | Kat | Oda No | Oda Tipi | Durum | İşlemler |
|----|------|-----|--------|----------|-------|----------|

### 4. Sidebar Menü Yapısı

```
📊 Dashboard
👥 Kullanıcı Yönetimi
🏢 Sistem Yönetimi
   ├── 🏨 Otel Yönetimi        [YENİ]
   ├── 🏗️ Kat Yönetimi
   ├── 🚪 Oda Yönetimi
   └── ⚙️ Sistem Ayarları
📦 Stok Yönetimi
...
```

## Performans Optimizasyonları

### 1. Database Indexler

```python
# Yeni indexler
db.Index('idx_kullanici_otel', 'otel_id')  # Kullanici tablosuna
db.Index('idx_kullanici_otel_kullanici', 'kullanici_id', 'otel_id')  # KullaniciOtel tablosuna
```

### 2. Query Optimizasyonları

```python
# Eager loading kullan
oteller = Otel.query.options(
    db.joinedload(Otel.katlar),
    db.joinedload(Otel.kullanici_atamalari)
).all()

# Pagination kullan
oteller = Otel.query.paginate(page=page, per_page=20)
```

### 3. Caching

```python
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=300, key_prefix='otel_listesi')
def get_aktif_oteller():
    return Otel.query.filter_by(aktif=True).all()
```

## Güvenlik Önlemleri

1. **CSRF Protection**: Tüm formlarda CSRF token kullanımı
2. **SQL Injection**: SQLAlchemy ORM kullanımı
3. **XSS Protection**: Template'lerde otomatik escaping
4. **Yetkilendirme**: Her endpoint'te rol ve otel erişim kontrolü
5. **Audit Log**: Tüm otel, kat, oda ve atama işlemlerinin loglanması

## Deployment Notları

1. **Migration Sırası**:
   - Yeni tabloları oluştur (KullaniciOtel)
   - Kullanici tablosuna otel_id ekle
   - Mevcut verileri migrate et
   - Constraint'leri ekle

2. **Rollback Planı**:
   - Migration script'i geri alınabilir olmalı
   - Backup alınmalı
   - Test ortamında önce denenme li

3. **Monitoring**:
   - Otel bazlı performans metrikleri
   - Kullanıcı erişim logları
   - Hata oranları takibi
