# Design Document - Minibar QR Kod Sistemi

## Overview

Bu tasarım, mevcut minibar yönetim sistemine QR kod tabanlı oda tanıma ve işlem başlatma özelliğini entegre eder. Sistem, her oda için benzersiz QR kodlar oluşturacak ve bu kodlar hem kat sorumlusu hem de misafir tarafından farklı amaçlarla kullanılabilecek.

### Temel Özellikler

1. **Otomatik QR Kod Oluşturma**: Oda kaydı sırasında veya toplu işlemle
2. **Akıllı Yönlendirme**: Kat sorumlusu panelinden vs. dış kaynaklardan okutma
3. **Misafir Self-Servis**: QR kod ile dolum talebi
4. **Zaman Damgalı Takip**: QR okutma geçmişi
5. **Güvenlik**: Token tabanlı doğrulama ve rate limiting

## Architecture

### Sistem Bileşenleri

```
┌─────────────────────────────────────────────────────────────┐
│                     QR Kod Sistemi                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Admin      │  │ Kat Sorumlusu│  │   Misafir    │    │
│  │   Panel      │  │    Panel     │  │    Arayüz    │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                  │             │
│         └─────────────────┼──────────────────┘             │
│                           │                                │
│                  ┌────────▼────────┐                       │
│                  │  QR Kod Service │                       │
│                  └────────┬────────┘                       │
│                           │                                │
│         ┌─────────────────┼─────────────────┐             │
│         │                 │                 │             │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐      │
│  │ QR Generator│  │ QR Validator│  │  QR Logger  │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Veri Akışı

**1. QR Kod Oluşturma Akışı**
```
Admin → Oda Oluştur/Güncelle → QR Generator → Token Oluştur → 
QR Görsel Oluştur → Veritabanına Kaydet → Admin'e Göster
```

**2. Kat Sorumlusu QR Okutma Akışı**
```
Kat Sorumlusu → QR Okut (Panel İçi) → Parse URL → 
Validate Token → Form Doldur → İşlem Başlat → Log Kaydet
```

**3. Misafir QR Okutma Akışı**
```
Misafir → QR Okut (Dış Kaynak) → Validate Token → 
Dolum Talebi Sayfası → Talep Gönder → Bildirim Oluştur
```


## Components and Interfaces

### 1. Database Schema Changes

#### Oda Modeli Güncellemeleri

```python
class Oda(db.Model):
    # Mevcut alanlar...
    
    # YENİ ALANLAR
    qr_kod_token = db.Column(db.String(64), unique=True, nullable=True)
    qr_kod_gorsel = db.Column(db.Text, nullable=True)  # Base64 encoded PNG
    qr_kod_olusturma_tarihi = db.Column(db.DateTime, nullable=True)
    misafir_mesaji = db.Column(db.String(500), nullable=True)
```

#### Yeni Model: MinibarDolumTalebi

```python
class MinibarDolumTalebi(db.Model):
    """Misafir dolum talepleri"""
    __tablename__ = 'minibar_dolum_talepleri'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    oda_id = db.Column(db.Integer, db.ForeignKey('odalar.id'), nullable=False)
    talep_tarihi = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    durum = db.Column(db.Enum('beklemede', 'tamamlandi', 'iptal'), default='beklemede')
    tamamlanma_tarihi = db.Column(db.DateTime, nullable=True)
    notlar = db.Column(db.Text, nullable=True)
    
    # İlişkiler
    oda = db.relationship('Oda', backref='dolum_talepleri')
```

#### Yeni Model: QRKodOkutmaLog

```python
class QRKodOkutmaLog(db.Model):
    """QR kod okutma geçmişi"""
    __tablename__ = 'qr_kod_okutma_loglari'
    __table_args__ = (
        db.Index('idx_oda_tarih', 'oda_id', 'okutma_tarihi'),
        db.Index('idx_kullanici_tarih', 'kullanici_id', 'okutma_tarihi'),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    oda_id = db.Column(db.Integer, db.ForeignKey('odalar.id'), nullable=False)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=True)
    okutma_tarihi = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    okutma_tipi = db.Column(db.Enum('kat_sorumlusu', 'misafir'), nullable=False)
    ip_adresi = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    basarili = db.Column(db.Boolean, default=True)
    hata_mesaji = db.Column(db.Text, nullable=True)
    
    # İlişkiler
    oda = db.relationship('Oda', backref='qr_okutma_loglari')
    kullanici = db.relationship('Kullanici', backref='qr_okutma_loglari')
```

### 2. QR Kod Service (utils/qr_service.py)

```python
import qrcode
import secrets
import base64
from io import BytesIO
from flask import url_for, request

class QRKodService:
    """QR kod oluşturma ve doğrulama servisi"""
    
    @staticmethod
    def generate_token():
        """Güvenli token oluştur"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_qr_url(oda_id, token):
        """QR kod URL'i oluştur"""
        # Sistemin çalıştığı domain'i otomatik algıla
        base_url = request.url_root.rstrip('/')
        return f"{base_url}/qr/{token}"
    
    @staticmethod
    def generate_qr_image(url):
        """QR kod görseli oluştur (Base64)"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Base64'e çevir
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    def create_qr_for_oda(oda):
        """Oda için QR kod oluştur"""
        token = QRKodService.generate_token()
        url = QRKodService.generate_qr_url(oda.id, token)
        qr_image = QRKodService.generate_qr_image(url)
        
        oda.qr_kod_token = token
        oda.qr_kod_gorsel = qr_image
        oda.qr_kod_olusturma_tarihi = datetime.utcnow()
        
        return {
            'token': token,
            'url': url,
            'image': qr_image
        }
    
    @staticmethod
    def validate_token(token):
        """Token'ı doğrula ve oda bilgisini döndür"""
        oda = Oda.query.filter_by(qr_kod_token=token, aktif=True).first()
        return oda
    
    @staticmethod
    def log_qr_scan(oda_id, okutma_tipi, kullanici_id=None, basarili=True, hata_mesaji=None):
        """QR okutma logunu kaydet"""
        log = QRKodOkutmaLog(
            oda_id=oda_id,
            kullanici_id=kullanici_id,
            okutma_tipi=okutma_tipi,
            ip_adresi=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            basarili=basarili,
            hata_mesaji=hata_mesaji
        )
        db.session.add(log)
        db.session.commit()
```

### 3. Rate Limiting Service

```python
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    """QR kod okutma rate limiting"""
    
    # IP bazlı rate limit cache (production'da Redis kullanılmalı)
    _cache = defaultdict(list)
    
    @staticmethod
    def check_rate_limit(ip_address, max_attempts=10, window_minutes=1):
        """Rate limit kontrolü"""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=window_minutes)
        
        # Eski kayıtları temizle
        RateLimiter._cache[ip_address] = [
            timestamp for timestamp in RateLimiter._cache[ip_address]
            if timestamp > window_start
        ]
        
        # Limit kontrolü
        if len(RateLimiter._cache[ip_address]) >= max_attempts:
            return False
        
        # Yeni denemeyi kaydet
        RateLimiter._cache[ip_address].append(now)
        return True
```


### 4. Flask Routes

#### Admin Routes (app.py)

```python
# QR Kod Yönetimi
@app.route('/admin/oda-qr-olustur/<int:oda_id>', methods=['POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def admin_oda_qr_olustur(oda_id):
    """Tek oda için QR kod oluştur"""
    pass

@app.route('/admin/toplu-qr-olustur', methods=['POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def admin_toplu_qr_olustur():
    """Tüm odalar veya QR'sız odalar için toplu QR oluştur"""
    pass

@app.route('/admin/oda-qr-goruntule/<int:oda_id>')
@login_required
@role_required('sistem_yoneticisi', 'admin')
def admin_oda_qr_goruntule(oda_id):
    """QR kodu görüntüle"""
    pass

@app.route('/admin/oda-qr-indir/<int:oda_id>')
@login_required
@role_required('sistem_yoneticisi', 'admin')
def admin_oda_qr_indir(oda_id):
    """QR kodu PNG olarak indir"""
    pass

@app.route('/admin/toplu-qr-indir')
@login_required
@role_required('sistem_yoneticisi', 'admin')
def admin_toplu_qr_indir():
    """Tüm QR kodları ZIP olarak indir"""
    pass

@app.route('/admin/oda-misafir-mesaji/<int:oda_id>', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def admin_oda_misafir_mesaji(oda_id):
    """Oda misafir mesajını düzenle"""
    pass
```

#### Kat Sorumlusu Routes

```python
# QR Kod ile İşlem Başlatma
@app.route('/kat-sorumlusu/qr-okut')
@login_required
@role_required('kat_sorumlusu')
def kat_sorumlusu_qr_okut():
    """QR okuyucu sayfası"""
    pass

@app.route('/api/kat-sorumlusu/qr-parse', methods=['POST'])
@login_required
@role_required('kat_sorumlusu')
def api_kat_sorumlusu_qr_parse():
    """QR koddan oda bilgilerini parse et"""
    pass
```

#### Misafir Routes (Public)

```python
# Misafir Dolum Talebi
@app.route('/qr/<token>')
def qr_redirect(token):
    """QR kod yönlendirme - Akıllı routing"""
    pass

@app.route('/misafir/dolum-talebi/<token>', methods=['GET', 'POST'])
def misafir_dolum_talebi(token):
    """Misafir dolum talebi sayfası"""
    pass

@app.route('/api/dolum-talepleri')
@login_required
@role_required('kat_sorumlusu')
def api_dolum_talepleri():
    """Bekleyen dolum taleplerini listele"""
    pass

@app.route('/api/dolum-talebi-tamamla/<int:talep_id>', methods=['POST'])
@login_required
@role_required('kat_sorumlusu')
def api_dolum_talebi_tamamla(talep_id):
    """Dolum talebini tamamla"""
    pass
```

### 5. Frontend Components

#### Admin Panel - QR Yönetimi

**Oda Listesi Güncellemeleri (templates/sistem_yoneticisi/odalar.html)**
```html
<!-- Her oda satırına QR butonları ekle -->
<td>
    <button class="btn btn-sm btn-info" onclick="qrGoruntule({{ oda.id }})">
        <i class="fas fa-qrcode"></i> QR Görüntüle
    </button>
    <button class="btn btn-sm btn-success" onclick="qrIndir({{ oda.id }})">
        <i class="fas fa-download"></i> İndir
    </button>
    <button class="btn btn-sm btn-warning" onclick="misafirMesajiDuzenle({{ oda.id }})">
        <i class="fas fa-comment"></i> Mesaj
    </button>
</td>

<!-- Toplu işlemler -->
<div class="mb-3">
    <button class="btn btn-primary" onclick="topluQrOlustur('tumu')">
        <i class="fas fa-qrcode"></i> Tüm Odalar İçin QR Oluştur
    </button>
    <button class="btn btn-secondary" onclick="topluQrOlustur('qrsiz')">
        <i class="fas fa-qrcode"></i> QR'sız Odalar İçin Oluştur
    </button>
    <button class="btn btn-success" onclick="topluQrIndir()">
        <i class="fas fa-download"></i> Tüm QR'ları İndir (ZIP)
    </button>
</div>
```

**QR Görüntüleme Modal**
```html
<div class="modal fade" id="qrModal">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">QR Kod - Oda <span id="qrOdaNo"></span></h5>
                <button type="button" class="close" data-dismiss="modal">&times;</button>
            </div>
            <div class="modal-body text-center">
                <img id="qrImage" src="" alt="QR Kod" class="img-fluid mb-3">
                <p class="text-muted">
                    <strong>Kat:</strong> <span id="qrKat"></span><br>
                    <strong>Oda No:</strong> <span id="qrOdaNoDetay"></span>
                </p>
            </div>
            <div class="modal-footer">
                <button class="btn btn-success" onclick="qrYazdir()">
                    <i class="fas fa-print"></i> Yazdır
                </button>
                <button class="btn btn-primary" onclick="qrIndir()">
                    <i class="fas fa-download"></i> İndir
                </button>
            </div>
        </div>
    </div>
</div>
```

#### Kat Sorumlusu Panel - QR Okuyucu

**Minibar İşlemleri Sayfası (templates/kat_sorumlusu/minibar_islemleri.html)**
```html
<!-- QR ile başlat butonu -->
<div class="card mb-4">
    <div class="card-body">
        <h5 class="card-title">Minibar İşlemi Başlat</h5>
        <div class="btn-group" role="group">
            <button class="btn btn-primary" onclick="qrIleBaslat()">
                <i class="fas fa-qrcode"></i> QR Kod ile Başla
            </button>
            <button class="btn btn-secondary" onclick="manuelBaslat()">
                <i class="fas fa-keyboard"></i> Manuel Seçim
            </button>
        </div>
    </div>
</div>

<!-- QR Okuyucu Modal -->
<div class="modal fade" id="qrScannerModal">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">QR Kod Okut</h5>
                <button type="button" class="close" data-dismiss="modal">&times;</button>
            </div>
            <div class="modal-body">
                <div id="qrReader" style="width: 100%;"></div>
                <div id="qrResult" class="alert alert-info mt-3" style="display:none;"></div>
            </div>
        </div>
    </div>
</div>
```

**QR Scanner JavaScript (static/js/qr_scanner.js)**
```javascript
// html5-qrcode kütüphanesi kullanılacak
function qrIleBaslat() {
    $('#qrScannerModal').modal('show');
    
    const html5QrCode = new Html5Qrcode("qrReader");
    
    html5QrCode.start(
        { facingMode: "environment" },
        { fps: 10, qrbox: 250 },
        (decodedText, decodedResult) => {
            // QR kod okundu
            parseQRCode(decodedText);
            html5QrCode.stop();
            $('#qrScannerModal').modal('hide');
        },
        (errorMessage) => {
            // Hata (sessizce yoksay)
        }
    );
}

function parseQRCode(qrUrl) {
    // URL'den token'ı çıkar
    const token = qrUrl.split('/').pop();
    
    // API'ye gönder
    $.ajax({
        url: '/api/kat-sorumlusu/qr-parse',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ token: token }),
        success: function(response) {
            if (response.success) {
                // Form alanlarını doldur
                $('#kat_id').val(response.kat_id).trigger('change');
                $('#oda_id').val(response.oda_id).trigger('change');
                
                // Başarı mesajı
                toastr.success('Oda bilgileri otomatik dolduruldu!');
            } else {
                toastr.error(response.message);
            }
        },
        error: function() {
            toastr.error('QR kod okunamadı!');
        }
    });
}
```


#### Misafir Arayüzü - Dolum Talebi

**Dolum Talebi Sayfası (templates/misafir_dolum_talebi.html)**
```html
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minibar Dolum Talebi</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .card {
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body p-5">
                        <div class="text-center mb-4">
                            <i class="fas fa-wine-bottle fa-3x text-primary mb-3"></i>
                            <h3>Minibar Dolum Talebi</h3>
                            <p class="text-muted">Oda {{ oda.oda_no }}</p>
                        </div>
                        
                        <div class="alert alert-info">
                            {{ oda.misafir_mesaji or 'Minibar dolum talebiniz en kısa sürede yerine getirilecektir.' }}
                        </div>
                        
                        <form method="POST" id="dolumTalebiForm">
                            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                            
                            <div class="form-group">
                                <label>Ek Not (Opsiyonel)</label>
                                <textarea name="notlar" class="form-control" rows="3" 
                                          placeholder="Özel bir talebiniz varsa buraya yazabilirsiniz..."></textarea>
                            </div>
                            
                            <button type="submit" class="btn btn-primary btn-block btn-lg">
                                <i class="fas fa-paper-plane"></i> Dolum Talebi Gönder
                            </button>
                        </form>
                        
                        <div id="successMessage" class="alert alert-success mt-3" style="display:none;">
                            <i class="fas fa-check-circle"></i> Talebiniz başarıyla gönderildi!
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        $('#dolumTalebiForm').on('submit', function(e) {
            e.preventDefault();
            
            $.ajax({
                url: window.location.href,
                method: 'POST',
                data: $(this).serialize(),
                success: function(response) {
                    $('#dolumTalebiForm').hide();
                    $('#successMessage').show();
                },
                error: function() {
                    alert('Bir hata oluştu. Lütfen tekrar deneyin.');
                }
            });
        });
    </script>
</body>
</html>
```

## Data Models

### Oda Model Güncellemesi

```python
# Migration dosyası: migrations/add_qr_kod_to_oda.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('odalar', sa.Column('qr_kod_token', sa.String(64), nullable=True))
    op.add_column('odalar', sa.Column('qr_kod_gorsel', sa.Text(), nullable=True))
    op.add_column('odalar', sa.Column('qr_kod_olusturma_tarihi', sa.DateTime(), nullable=True))
    op.add_column('odalar', sa.Column('misafir_mesaji', sa.String(500), nullable=True))
    op.create_unique_constraint('uq_oda_qr_token', 'odalar', ['qr_kod_token'])

def downgrade():
    op.drop_constraint('uq_oda_qr_token', 'odalar', type_='unique')
    op.drop_column('odalar', 'misafir_mesaji')
    op.drop_column('odalar', 'qr_kod_olusturma_tarihi')
    op.drop_column('odalar', 'qr_kod_gorsel')
    op.drop_column('odalar', 'qr_kod_token')
```

### Yeni Tablolar

**minibar_dolum_talepleri**
- id (PK)
- oda_id (FK → odalar.id)
- talep_tarihi (DateTime)
- durum (Enum: beklemede, tamamlandi, iptal)
- tamamlanma_tarihi (DateTime, nullable)
- notlar (Text, nullable)

**qr_kod_okutma_loglari**
- id (PK)
- oda_id (FK → odalar.id)
- kullanici_id (FK → kullanicilar.id, nullable)
- okutma_tarihi (DateTime)
- okutma_tipi (Enum: kat_sorumlusu, misafir)
- ip_adresi (String)
- user_agent (String)
- basarili (Boolean)
- hata_mesaji (Text, nullable)

## Error Handling

### Hata Senaryoları ve Çözümleri

1. **QR Kod Oluşturma Hatası**
   - Hata: Token oluşturulamadı veya görsel oluşturulamadı
   - Çözüm: Try-catch ile yakala, log kaydet, kullanıcıya bildir
   - Rollback: Veritabanı transaction'ı geri al

2. **Geçersiz Token**
   - Hata: Token bulunamadı veya oda aktif değil
   - Çözüm: 404 sayfası göster, güvenlik logu kaydet
   - Rate Limit: Aynı IP'den çok fazla geçersiz deneme

3. **Rate Limit Aşımı**
   - Hata: Dakikada 10'dan fazla QR okutma denemesi
   - Çözüm: 429 Too Many Requests döndür
   - Mesaj: "Çok fazla deneme yaptınız. Lütfen 1 dakika bekleyin."

4. **QR Okuyucu Kamera Erişimi**
   - Hata: Tarayıcı kamera iznini reddetti
   - Çözüm: Kullanıcıya manuel seçim seçeneği sun
   - Mesaj: "Kamera erişimi reddedildi. Manuel seçim yapabilirsiniz."

5. **Ağ Bağlantı Hatası**
   - Hata: QR parse API'sine ulaşılamadı
   - Çözüm: Retry mekanizması (max 3 deneme)
   - Fallback: Manuel seçim öner

### Hata Loglama

```python
def handle_qr_error(error_type, oda_id=None, token=None, extra_info=None):
    """QR kod hatalarını logla"""
    log_hata(
        Exception(error_type),
        modul='qr_kod_sistemi',
        extra_info={
            'oda_id': oda_id,
            'token': token[:10] + '...' if token else None,  # Güvenlik için kısalt
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            **extra_info
        }
    )
```

## Testing Strategy

### Unit Tests

1. **QR Kod Oluşturma**
   ```python
   def test_generate_token():
       token = QRKodService.generate_token()
       assert len(token) > 0
       assert token.isalnum() or '-' in token or '_' in token
   
   def test_generate_qr_image():
       url = "http://test.com/qr/test123"
       image = QRKodService.generate_qr_image(url)
       assert image.startswith('data:image/png;base64,')
   ```

2. **Token Doğrulama**
   ```python
   def test_validate_token_valid():
       oda = create_test_oda()
       qr_data = QRKodService.create_qr_for_oda(oda)
       validated_oda = QRKodService.validate_token(qr_data['token'])
       assert validated_oda.id == oda.id
   
   def test_validate_token_invalid():
       validated_oda = QRKodService.validate_token('invalid_token_123')
       assert validated_oda is None
   ```

3. **Rate Limiting**
   ```python
   def test_rate_limit_allows_under_limit():
       ip = '192.168.1.1'
       for i in range(9):
           assert RateLimiter.check_rate_limit(ip) == True
   
   def test_rate_limit_blocks_over_limit():
       ip = '192.168.1.2'
       for i in range(10):
           RateLimiter.check_rate_limit(ip)
       assert RateLimiter.check_rate_limit(ip) == False
   ```

### Integration Tests

1. **Admin QR Oluşturma Akışı**
   - Oda oluştur
   - QR kod oluştur
   - Veritabanında token ve görsel kontrolü
   - QR görüntüleme sayfası testi

2. **Kat Sorumlusu QR Okutma Akışı**
   - Login yap (kat sorumlusu)
   - QR okuyucu sayfasını aç
   - Mock QR kod gönder
   - Form doldurma kontrolü

3. **Misafir Dolum Talebi Akışı**
   - QR URL'e git
   - Dolum talebi formu doldur
   - Veritabanında talep kontrolü
   - Bildirim oluşturma kontrolü

### Manual Testing Checklist

- [ ] Admin panelinde tek oda için QR oluşturma
- [ ] Toplu QR oluşturma (tüm odalar)
- [ ] Toplu QR oluşturma (sadece QR'sız odalar)
- [ ] QR kod görüntüleme modal
- [ ] QR kod indirme (PNG)
- [ ] Toplu QR indirme (ZIP)
- [ ] Misafir mesajı düzenleme
- [ ] Kat sorumlusu QR okuyucu (mobil cihaz)
- [ ] Kat sorumlusu QR okuyucu (desktop kamera)
- [ ] Form otomatik doldurma
- [ ] Misafir QR okutma (mobil)
- [ ] Misafir dolum talebi gönderme
- [ ] Dolum talebi bildirimi
- [ ] Geçersiz token testi
- [ ] Rate limit testi
- [ ] Kamera izni reddi senaryosu


## Security Considerations

### 1. Token Güvenliği

**Token Özellikleri:**
- 32 byte (256 bit) rastgele token
- URL-safe base64 encoding
- Benzersizlik garantisi (database unique constraint)
- Tahmin edilemez (cryptographically secure random)

**Token Yaşam Döngüsü:**
- Token süresiz (oda silinene kadar geçerli)
- Oda silindiğinde otomatik geçersiz
- Yeniden oluşturma seçeneği (eski token geçersiz olur)

### 2. Rate Limiting

**Koruma Mekanizmaları:**
- IP bazlı rate limiting (dakikada max 10 deneme)
- Başarısız token doğrulama sayacı
- Güvenlik logu (şüpheli aktivite tespiti)

**Implementation:**
```python
@app.before_request
def check_qr_rate_limit():
    if request.endpoint and 'qr' in request.endpoint:
        ip = request.remote_addr
        if not RateLimiter.check_rate_limit(ip):
            abort(429)  # Too Many Requests
```

### 3. Input Validation

**Misafir Mesajı:**
- Maksimum 500 karakter
- HTML injection koruması (escape)
- XSS koruması (bleach kütüphanesi)

```python
import bleach

def sanitize_misafir_mesaji(mesaj):
    """Misafir mesajını temizle"""
    if not mesaj:
        return None
    
    # HTML taglerini temizle
    clean_mesaj = bleach.clean(mesaj, tags=[], strip=True)
    
    # Maksimum uzunluk kontrolü
    if len(clean_mesaj) > 500:
        clean_mesaj = clean_mesaj[:500]
    
    return clean_mesaj
```

### 4. CSRF Koruması

Tüm POST endpoint'leri CSRF token gerektirmeli:
```python
@app.route('/admin/oda-qr-olustur/<int:oda_id>', methods=['POST'])
@csrf.exempt  # Sadece API endpoint'leri için
@login_required
def admin_oda_qr_olustur(oda_id):
    # CSRF token otomatik kontrol edilir
    pass
```

### 5. Audit Trail

Tüm QR kod işlemleri audit log'a kaydedilmeli:
```python
# QR oluşturma
audit_create(
    tablo_adi='odalar',
    kayit_id=oda.id,
    yeni_deger={'qr_kod_token': token[:10] + '...'},  # Güvenlik için kısalt
    aciklama='QR kod oluşturuldu'
)

# QR okutma
audit_create(
    tablo_adi='qr_kod_okutma_loglari',
    kayit_id=log.id,
    yeni_deger=serialize_model(log),
    aciklama=f'QR kod okutuldu - {okutma_tipi}'
)
```

## Performance Optimization

### 1. Database Indexing

```python
# Oda modeli
__table_args__ = (
    db.Index('idx_qr_token', 'qr_kod_token'),
)

# QR okutma log
__table_args__ = (
    db.Index('idx_oda_tarih', 'oda_id', 'okutma_tarihi'),
    db.Index('idx_kullanici_tarih', 'kullanici_id', 'okutma_tarihi'),
)
```

### 2. Caching

**QR Görsel Cache:**
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.memoize(timeout=3600)  # 1 saat cache
def get_qr_image(oda_id):
    oda = Oda.query.get(oda_id)
    return oda.qr_kod_gorsel if oda else None
```

### 3. Lazy Loading

QR görsel sadece gerektiğinde yüklensin:
```python
# Oda listesinde QR görsel yükleme
odalar = Oda.query.options(
    db.defer('qr_kod_gorsel')  # Görsel yükleme
).all()
```

### 4. Batch Operations

Toplu QR oluşturma optimize edilmeli:
```python
def toplu_qr_olustur(oda_listesi):
    """Toplu QR oluşturma - batch insert"""
    for oda in oda_listesi:
        qr_data = QRKodService.create_qr_for_oda(oda)
        # Commit her 100 odada bir
        if oda_listesi.index(oda) % 100 == 0:
            db.session.commit()
    
    db.session.commit()  # Final commit
```

## Deployment Considerations

### 1. Dependencies

**requirements.txt güncellemeleri:**
```
qrcode[pil]==7.4.2
Pillow==10.0.0
bleach==6.0.0
```

### 2. Environment Variables

**.env dosyası:**
```
# QR Kod Ayarları
QR_RATE_LIMIT_MAX=10
QR_RATE_LIMIT_WINDOW=1  # dakika
QR_DEFAULT_MISAFIR_MESAJI="Minibar dolum talebiniz en kısa sürede yerine getirilecektir."
```

### 3. Migration Script

```bash
# Migration çalıştır
python -c "from app import app, db; from models import *; \
    with app.app_context(): db.create_all()"

# Veya Alembic ile
alembic upgrade head
```

### 4. Initial Data Setup

Mevcut odalar için QR oluşturma scripti:
```python
# scripts/generate_qr_for_existing_odalar.py
from app import app, db
from models import Oda
from utils.qr_service import QRKodService

with app.app_context():
    odalar = Oda.query.filter_by(aktif=True).all()
    
    for oda in odalar:
        if not oda.qr_kod_token:
            QRKodService.create_qr_for_oda(oda)
            print(f"QR oluşturuldu: Oda {oda.oda_no}")
    
    db.session.commit()
    print(f"Toplam {len(odalar)} oda için QR oluşturuldu.")
```

## Future Enhancements

### Faz 2 Özellikler

1. **QR Kod Analitikleri**
   - En çok okutulan odalar
   - Okutma zamanı analizi
   - Misafir vs kat sorumlusu okutma oranları

2. **Dinamik QR Kodlar**
   - Zaman bazlı geçerlilik
   - Tek kullanımlık QR kodlar
   - Şifreli QR kodlar

3. **Mobil Uygulama**
   - Native QR okuyucu
   - Offline QR okuma
   - Push notification

4. **Gelişmiş Bildirimler**
   - SMS bildirimi
   - Email bildirimi
   - WhatsApp entegrasyonu

5. **QR Kod Tasarım Özelleştirme**
   - Logo ekleme
   - Renk özelleştirme
   - Çerçeve seçenekleri

## Documentation

### Admin Kullanım Kılavuzu

**QR Kod Oluşturma:**
1. Admin paneline giriş yap
2. "Oda Tanımları" menüsüne git
3. Yeni oda eklerken QR otomatik oluşturulur
4. Mevcut odalar için "QR Oluştur" butonuna tıkla

**Toplu QR Oluşturma:**
1. "Oda Tanımları" sayfasında "Toplu İşlemler" bölümüne git
2. "Tüm Odalar İçin QR Oluştur" veya "QR'sız Odalar İçin Oluştur" seç
3. İşlem tamamlanınca bildirim gelir

**QR Kod İndirme:**
1. Tek oda: Oda satırında "İndir" butonuna tıkla
2. Toplu: "Tüm QR'ları İndir" butonuna tıkla (ZIP dosyası)

### Kat Sorumlusu Kullanım Kılavuzu

**QR Kod ile İşlem Başlatma:**
1. "Minibar İşlemleri" sayfasına git
2. "QR Kod ile Başla" butonuna tıkla
3. Kamera izni ver
4. Odadaki QR kodu okut
5. Form otomatik doldurulur
6. İşleme devam et

### Misafir Kullanım Kılavuzu

**Minibar Dolum Talebi:**
1. Odadaki QR kodu telefonla okut
2. Açılan sayfada "Dolum Talebi Gönder" butonuna tıkla
3. Opsiyonel not ekle
4. Talebi gönder
5. Onay mesajı gelir

