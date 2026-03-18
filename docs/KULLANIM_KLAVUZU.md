# 🏨 OTEL MİNİBAR TAKİP SİSTEMİ - KULLANIM KILAVUZU

**Versiyon:** 1.0  
**Tarih:** 31 Ekim 2025  
**Hazırlayan:** Sistem Dokümantasyon Ekibi

---

## 📑 İÇİNDEKİLER

### Bölüm 1: Sistem Genel Bakış ve Kurulum
- Sistem Hakkında
- Teknik Özellikler
- Kurulum Adımları
- İlk Yapılandırma

### Bölüm 2: Rol Tabanlı Kullanım Kılavuzları
- Sistem Yöneticisi
- Admin Kullanıcı
- Depo Sorumlusu
- Kat Sorumlusu

### Bölüm 3: Özellik Detayları ve İş Akışları
- Stok Yönetimi
- Zimmet Sistemi
- Minibar İşlemleri
- Raporlama

### Bölüm 4: Teknik Dokümantasyon
- API Endpoints
- Veritabanı Yapısı
- Güvenlik Özellikleri
- Sorun Giderme

---

# BÖLÜM 1: SİSTEM GENEL BAKIŞ VE KURULUM

## 1. SİSTEM HAKKINDA

### 1.1 Genel Tanım

Otel Minibar Takip Sistemi, otel işletmelerinde minibar stok yönetimini, personel zimmet takibini ve tüketim analizlerini dijital ortamda yönetmek için geliştirilmiş profesyonel bir web uygulamasıdır.

### 1.2 Temel Özellikler

#### ✅ Stok Yönetimi
- Gerçek zamanlı stok takibi
- Kritik stok uyarıları
- Otomatik stok hesaplama
- Giriş/Çıkış kayıtları
- Depo envanteri

#### 📦 Zimmet Sistemi
- Personel zimmet atama
- Zimmet kullanım takibi
- İade işlemleri
- Zimmet geçmişi
- Otomatik stok düşümü

#### 🛏️ Minibar Yönetimi
- Oda bazlı minibar takibi
- İlk dolum işlemleri
- Kontrol ve doldurma
- Tüketim analizi
- Toplu işlem desteği

#### 📊 Raporlama ve Analiz
- Detaylı stok raporları
- Tüketim analizleri
- Zimmet raporları
- Excel/PDF export
- Grafik ve görselleştirme

#### 🔒 Güvenlik
- Rol tabanlı erişim kontrolü
- CSRF koruması
- Rate limiting (DDoS koruması)
- Audit trail (denetim izi)
- Oturum güvenliği
- Şifreleme

### 1.3 Kullanıcı Rolleri

#### 🔐 Sistem Yöneticisi
- Tam sistem yetkisi
- Otel tanımlama
- Kat/Oda yönetimi
- Admin atama
- Sistem logları

#### 👔 Admin
- Ürün yönetimi
- Personel tanımlama
- Stok işlemleri
- Tüm raporlar
- Sistem ayarları

#### 📦 Depo Sorumlusu
- Stok giriş/çıkış
- Personel zimmet atama
- Minibar durum görüntüleme
- Stok raporları
- Zimmet takibi

#### 🧹 Kat Sorumlusu
- Minibar dolum/kontrol
- Zimmet kullanımı
- Oda işlemleri
- Kişisel raporlar
- Tüketim kayıtları

---

## 2. TEKNİK ÖZELLİKLER

### 2.1 Teknoloji Stack

#### Backend
- **Framework:** Flask 3.0.3
- **ORM:** SQLAlchemy 2.0.36
- **Veritabanı:** MySQL 8.0+
- **Python:** 3.11+

#### Frontend
- **CSS Framework:** Tailwind CSS 3.4
- **JavaScript:** Vanilla JS + Chart.js 4.4
- **Icons:** Heroicons
- **PWA:** Service Worker desteği

#### Güvenlik
- **CSRF:** Flask-WTF CSRFProtect
- **Rate Limiting:** Flask-Limiter
- **Password Hashing:** Werkzeug Security
- **Session:** Flask Secure Cookies

#### Reporting
- **Excel:** OpenPyXL 3.1.5
- **PDF:** ReportLab 4.2.5

### 2.2 Sistem Gereksinimleri

#### Sunucu Gereksinimleri
```
- İşletim Sistemi: Windows/Linux/macOS
- Python: 3.11 veya üzeri
- MySQL: 8.0 veya üzeri
- RAM: Minimum 2GB (Önerilen 4GB)
- Disk: Minimum 1GB
- İnternet: HTTPS için gerekli
```

#### İstemci Gereksinimleri
```
- Modern web tarayıcı:
  * Chrome 90+
  * Firefox 88+
  * Safari 14+
  * Edge 90+
- JavaScript aktif
- Cookies aktif
- Minimum 1280x720 ekran çözünürlüğü
```

### 2.3 Veritabanı Yapısı

#### Ana Tablolar
```
- oteller (Otel bilgileri)
- kullanicilar (Tüm kullanıcılar)
- katlar (Kat tanımları)
- odalar (Oda tanımları)
- urun_gruplari (Ürün kategorileri)
- urunler (Ürün tanımları)
- stok_hareketleri (Stok giriş/çıkış)
- personel_zimmet (Zimmet başlık)
- personel_zimmet_detay (Zimmet detay)
- minibar_islemleri (Minibar işlem başlık)
- minibar_islem_detay (Minibar işlem detay)
- sistem_loglari (İşlem logları)
- hata_loglari (Hata logları)
- audit_logs (Denetim izi)
- sistem_ayarlari (Sistem ayarları)
```

---

## 3. KURULUM

### 3.1 Railway ile Kurulum (Önerilen)

#### Adım 1: GitHub Repository Oluşturma
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

#### Adım 2: Railway Projesi Oluşturma
1. [Railway.app](https://railway.app) sitesine gidin
2. GitHub ile giriş yapın
3. "New Project" → "Deploy from GitHub repo" seçin
4. Repository'nizi seçin

#### Adım 3: MySQL Veritabanı Ekleme
1. Railway projenizde "New" → "Database" → "Add MySQL"
2. Otomatik `DATABASE_URL` environment variable oluşacak

#### Adım 4: Environment Variables Ayarlama
Railway projesinde Settings → Variables:
```env
SECRET_KEY=your-super-secret-key-change-this-min-32-chars
FLASK_ENV=production
```

⚠️ **Önemli:** `SECRET_KEY` minimum 32 karakter olmalı ve güçlü olmalıdır.

#### Adım 5: Deploy
- Railway otomatik deploy edecek
- İlk deploy sırasında `init_db.py` otomatik çalışarak tabloları oluşturacak
- Deploy tamamlandığında URL'niz hazır

### 3.2 Lokal Kurulum

#### Adım 1: Repository'yi Klonlama
```bash
git clone <repo-url>
cd prof
```

#### Adım 2: Virtual Environment Oluşturma
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

#### Adım 3: Bağımlılıkları Yükleme
```bash
pip install -r requirements.txt
```

#### Adım 4: .env Dosyası Oluşturma
Proje kök dizininde `.env` dosyası oluşturun:
```env
# Veritabanı Ayarları
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=minibar_takip
DB_PORT=3306

# Flask Ayarları
SECRET_KEY=your-super-secret-key-change-this-min-32-chars
FLASK_ENV=development

# Port (Opsiyonel)
PORT=5014
```

#### Adım 5: MySQL Veritabanı Oluşturma
```sql
CREATE DATABASE minibar_takip CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### Adım 6: Veritabanını Başlatma
```bash
python init_db.py
```

#### Adım 7: Uygulamayı Çalıştırma
```bash
python app.py
```

#### Adım 8: Tarayıcıda Açma
```
http://localhost:5014
```

---

## 4. İLK YAPILANDIRMA (SETUP)

### 4.1 Setup Süreci

Sistem ilk kez çalıştırıldığında otomatik olarak Setup sayfası açılır.

#### Setup Adımları

**1. Otel Bilgileri**
```
- Otel Adı: Otelin resmi adı
- Adres: Tam adres bilgisi (min 10 karakter)
- Telefon: İletişim telefonu
- E-posta: İletişim e-postası (opsiyonel)
- Vergi No: Vergi numarası (opsiyonel)
```

**2. Sistem Yöneticisi Bilgileri**
```
- Kullanıcı Adı: 3-50 karakter, harf/rakam/(_-.)
- Ad: Yöneticinin adı
- Soyad: Yöneticinin soyadı
- E-posta: Geçerli e-posta adresi
- Telefon: İletişim telefonu (opsiyonel)
- Şifre: Min 8 karakter, güçlü şifre
  * En az 1 büyük harf
  * En az 1 küçük harf
  * En az 1 rakam
  * En az 1 özel karakter (!@#$%^&*...)
- Şifre Onayı: Şifre tekrarı
```

**3. Setup Tamamlama**
- Tüm bilgiler doldurulduktan sonra "Kurulumu Tamamla" butonuna tıklayın
- Sistem otomatik olarak:
  - Otel kaydı oluşturur
  - Sistem Yöneticisi kullanıcısı oluşturur
  - Setup tamamlandı olarak işaretler
- Başarılı setup sonrası login sayfasına yönlendirilirsiniz

### 4.2 İlk Giriş

**1. Login Sayfası**
```
URL: http://localhost:5014/login (veya Railway URL'niz)
Kullanıcı Adı: Setup'ta belirlediğiniz kullanıcı adı
Şifre: Setup'ta belirlediğiniz şifre
```

**2. Güvenlik Kontrolleri**
- Rate Limiting: 5 deneme/dakika
- CSRF Token kontrolü
- Secure session
- IP ve tarayıcı loglanması

**3. İlk Giriş Sonrası**
- Sistem Yöneticisi dashboard'una yönlendirilirsiniz
- Hoş geldiniz mesajı görüntülenir
- İlk yapılandırma adımlarına geçebilirsiniz

### 4.3 Temel Yapılandırma Adımları

#### Adım 1: Kat Tanımlama
```
Menü: Sistem Yöneticisi → Kat Tanımla
- Kat Adı: Zemin Kat, 1. Kat, vb.
- Kat No: Sayısal değer (-5 ile 100 arası)
- Açıklama: Ek bilgiler (opsiyonel)
```

#### Adım 2: Oda Tanımlama
```
Menü: Sistem Yöneticisi → Oda Tanımla
- Kat: Dropdown'dan kat seçimi
- Oda Numarası: Benzersiz oda no (örn: 101, 102)
- Oda Tipi: Standart, Suit, Deluxe vb.
- Kapasite: Kişi sayısı (1-20)
```

#### Adım 3: Admin Kullanıcı Atama
```
Menü: Sistem Yöneticisi → Personel Tanımla
- Kullanıcı Adı, Ad, Soyad, E-posta
- Rol: Admin seçimi
- Güçlü şifre belirleme
```

#### Adım 4: Ürün Grupları Oluşturma (Admin)
```
Admin olarak giriş yapın
Menü: Admin → Ürün Grupları
Örnek gruplar:
- İçecekler
- Atıştırmalıklar
- Alkollü İçecekler
- Soğuk İçecekler
```

#### Adım 5: Ürün Tanımlama (Admin)
```
Menü: Admin → Ürünler
Her ürün için:
- Ürün Grubu seçimi
- Ürün Adı
- Barkod (opsiyonel, benzersiz)
- Birim (Adet, Şişe, Kutu, vb.)
- Kritik Stok Seviyesi
```

#### Adım 6: Personel Tanımlama (Admin)
```
Menü: Admin → Personel Tanımla
Roller:
- Depo Sorumlusu: Stok ve zimmet yönetimi
- Kat Sorumlusu: Minibar işlemleri
```

#### Adım 7: İlk Stok Girişi (Depo Sorumlusu)
```
Depo Sorumlusu olarak giriş yapın
Menü: Depo Sorumlusu → Stok Girişi
- Ürün seçimi
- Hareket Tipi: Giriş/Devir/Sayım
- Miktar
- Açıklama
```

### 4.4 Sistem Hazır!

✅ **Kontrol Listesi**
- [ ] Setup tamamlandı
- [ ] Katlar oluşturuldu
- [ ] Odalar tanımlandı
- [ ] Admin kullanıcı atandı
- [ ] Ürün grupları oluşturuldu
- [ ] Ürünler tanımlandı
- [ ] Personeller oluşturuldu
- [ ] İlk stok girişi yapıldı

Sistem artık kullanıma hazır! 🎉

---

## 5. GÜVENLİK ÖNEMLERİ

### 5.1 Şifre Güvenliği
- Minimum 8 karakter
- Büyük/küçük harf, rakam ve özel karakter içermeli
- Varsayılan şifreler değiştirilmeli
- Periyodik şifre değişimi önerilir

### 5.2 Yetkilendirme
- Her kullanıcıya sadece gerekli yetkiler verilmeli
- Pasif kullanıcılar devre dışı bırakılmalı
- Şüpheli aktiviteler takip edilmeli

### 5.3 Veri Güvenliği
- Düzenli veritabanı yedekleri alınmalı
- Production ortamında HTTPS kullanılmalı
- `.env` dosyası git'e eklenmemeli
- SECRET_KEY güçlü ve benzersiz olmalı

### 5.4 Audit Trail
- Tüm kritik işlemler loglanır
- Kullanıcı aktiviteleri izlenir
- Veri değişiklikleri kaydedilir
- Güvenlik ihlalleri raporlanır

---

# BÖLÜM 2: ROL TABANLI KULLANIM KLAVUZLARI

## 1. SİSTEM YÖNETİCİSİ KULLANIM KILAVUZU

### 1.1 Dashboard (Ana Sayfa)

#### Erişim
```
URL: /sistem-yoneticisi
Menü: Otomatik yönlendirme (login sonrası)
```

#### Dashboard Bileşenleri

**1. İstatistik Kartları**
- **Toplam Kat:** Sistemdeki aktif kat sayısı
- **Toplam Oda:** Sistemdeki aktif oda sayısı
- **Toplam Kullanıcı:** Admin + Personel sayısı
- **Toplam Personel:** Depo + Kat sorumlusu sayısı

**2. Hızlı Erişim Kartları**
- Ürün Grupları ve Toplam Ürün
- Kritik Stoklu Ürünler
- Stok Durum Özeti (Kritik/Dikkat/Normal)

**3. Son Eklenenler**
- Son 5 kat
- Son 5 oda
- Son 5 personel
- Son 5 ürün

**4. Grafikler**
- Kullanıcı rol dağılımı (Pasta grafik)
- Kat bazlı oda sayıları (Bar grafik)
- Ürün tüketim trendleri (Line grafik)

### 1.2 Otel Tanımlama

#### Erişim
```
Menü: Sistem Yöneticisi → Otel Tanımla
URL: /otel-tanimla
```

#### İşlem Adımları

**1. Otel Bilgilerini Görüntüleme**
- Mevcut otel bilgileri formda gösterilir
- Setup'ta oluşturulan otel otomatik yüklenir

**2. Otel Bilgilerini Güncelleme**
```
Form Alanları:
- Otel Adı: (Zorunlu, 2-200 karakter)
- Adres: (Zorunlu, 10-500 karakter)
- Telefon: (Zorunlu, 10-20 karakter)
- E-posta: (Opsiyonel, geçerli e-posta)
- Vergi No: (Opsiyonel, max 50 karakter)
```

**3. Kaydetme**
- "Kaydet" butonuna tıklayın
- Başarı mesajı görüntülenir
- Değişiklikler audit log'a kaydedilir

### 1.3 Kat Yönetimi

#### Kat Tanımlama

**Erişim:** `/kat-tanimla`

**1. Yeni Kat Ekleme**
```
Form Alanları:
- Kat Adı: (Zorunlu, örn: "Zemin Kat", "1. Kat")
- Kat No: (Zorunlu, -5 ile 100 arası)
- Açıklama: (Opsiyonel, max 500 karakter)
```

**2. Kat Listesi**
- Tüm aktif katlar tablo halinde gösterilir
- Kat No'ya göre sıralıdır
- Her kat için işlem butonları:
  - 🖊️ Düzenle
  - 🗑️ Sil

**3. Kat Düzenleme**
- Düzenle butonuna tıklayın
- Kat bilgilerini güncelleyin
- "Güncelle" butonuna tıklayın

**4. Kat Silme**
⚠️ **Uyarı:** Pasif yapılır, kalıcı olarak silinmez
- Sil butonuna tıklayın
- Onay mesajı gelir
- Kat pasif duruma geçer

#### Kat Düzenleme

**Erişim:** `/kat-duzenle/<kat_id>`

**İşlemler:**
- Kat adı değiştirme
- Kat no değiştirme (benzersiz olmalı)
- Açıklama güncelleme

### 1.4 Oda Yönetimi

#### Oda Tanımlama

**Erişim:** `/oda-tanimla`

**1. Yeni Oda Ekleme**
```
Form Alanları:
- Kat: (Dropdown, aktif katlar)
- Oda Numarası: (Zorunlu, benzersiz, 1-20 karakter)
  Örnek: 101, 102, 201-A, vb.
- Oda Tipi: (Opsiyonel, max 50 karakter)
  Örnek: Standart, Suit, Deluxe
- Kapasite: (Opsiyonel, 1-20 kişi)
```

**2. Oda Listesi**
- Tüm aktif odalar tablo halinde
- Oda no'ya göre sıralı
- Kat bilgisi gösterilir
- İşlem butonları:
  - 🖊️ Düzenle
  - 🗑️ Sil

**3. Oda Düzenleme**
- Kat değiştirebilme
- Oda no değiştirebilme (benzersiz)
- Oda tipi ve kapasite güncelleyebilme

**4. Oda Silme**
⚠️ **Uyarı:** Minibar kaydı olan odalar silinemez
- Sil butonuna tıklayın
- Onay mesajı
- Oda kalıcı olarak silinir

### 1.5 Personel Yönetimi (Admin Atama)

#### Personel Tanımlama

**Erişim:** `/personel-tanimla`

**1. Yeni Personel Ekleme**
```
Form Alanları:
- Kullanıcı Adı: (Zorunlu, 3-50 karakter, benzersiz)
  * Sadece harf, rakam, (_-.)
- Ad: (Zorunlu, 2-50 karakter)
- Soyad: (Zorunlu, 2-50 karakter)
- E-posta: (Opsiyonel, benzersiz)
- Telefon: (Opsiyonel, max 20 karakter)
- Rol: (Dropdown)
  * Admin
  * Depo Sorumlusu
  * Kat Sorumlusu
- Şifre: (Zorunlu, min 8 karakter, güçlü)
```

**2. Şifre Gereksinimleri**
```
✓ Minimum 8 karakter
✓ En az 1 büyük harf
✓ En az 1 küçük harf
✓ En az 1 rakam
✓ En az 1 özel karakter (!@#$%^&*...)
```

**3. Personel Listesi**
- Tüm personeller tablo halinde
- Rol bazlı filtreleme
- Aktif/Pasif durumu
- İşlem butonları:
  - 🖊️ Düzenle
  - 🔒 Pasif Yap
  - 🔓 Aktif Yap

**4. Personel Düzenleme**
- Kullanıcı bilgilerini güncelleme
- Rol değiştirme
- Şifre sıfırlama (opsiyonel)

**5. Personel Pasif/Aktif Yapma**
- Pasif: Kullanıcı giriş yapamaz
- Aktif: Kullanıcı tekrar giriş yapabilir
- Pasif kullanıcılar silinmez, devre dışı bırakılır

### 1.6 Sistem Logları

#### Erişim
```
URL: /sistem-loglari
Menü: Sistem Yöneticisi → Sistem Logları
```

#### Log Görüntüleme

**1. Filtreler**
```
- İşlem Tipi: Tümü/Ekleme/Güncelleme/Silme/Giriş/Çıkış
- Modül: Tümü/Urun/Stok/Zimmet/Minibar/vb.
- Kullanıcı: Dropdown ile seçim
- Sayfa: Pagination (50 kayıt/sayfa)
```

**2. Log Bilgileri**
```
Tablo Sütunları:
- ID
- Tarih/Saat
- Kullanıcı (Ad Soyad)
- İşlem Tipi
- Modül
- Detay (JSON formatında)
- IP Adresi
```

**3. Log Detayları**
- Her log satırına tıklayarak detay görülebilir
- JSON formatında işlem bilgileri
- İşlem öncesi/sonrası değerler

### 1.7 Audit Trail (Denetim İzi)

#### Erişim
```
URL: /sistem-yoneticisi/audit-trail
Menü: Sistem Yöneticisi → Audit Trail
```

#### Özellikler

**1. Tam Denetim İzi**
- Tüm veri değişiklikleri kaydedilir
- Eski ve yeni değerler saklanır
- Değişiklik özeti oluşturulur
- Kim, ne, ne zaman, nereden

**2. Filtreler**
```
- Kullanıcı: Dropdown seçim
- İşlem Tipi: create/update/delete/login/logout/view/export
- Tablo: Dropdown seçim
- Tarih Aralığı: Başlangıç-Bitiş
```

**3. Audit Log Detayı**
```
Bilgiler:
- Kullanıcı bilgisi (ID, Ad, Rol)
- İşlem tipi ve tarih
- Etkilenen tablo ve kayıt ID
- Eski değerler (JSON)
- Yeni değerler (JSON)
- Değişiklik özeti (okunabilir)
- HTTP bilgileri (Method, URL, Endpoint)
- Ağ bilgileri (IP, User Agent)
- Başarı durumu ve hata mesajı
```

**4. Excel Export**
- Filtrelenmiş logları Excel'e aktarma
- Maksimum 10,000 kayıt
- Otomatik sütun genişlik ayarı
- Başlık formatlaması

**5. İstatistikler**
```
- Bugün: Bugünün toplam log sayısı
- Bu Hafta: Haftalık toplam
- Bu Ay: Aylık toplam
```

---

## 2. ADMİN KULLANICI KULLANIM KILAVUZU

### 2.1 Dashboard

Admin kullanıcılar Sistem Yöneticisi ile aynı dashboard'u kullanır ve tüm yetkilere sahiptir.

### 2.2 Ürün Grup Yönetimi

#### Erişim
```
URL: /urun-gruplari
Menü: Admin → Ürün Grupları
```

#### Yeni Grup Ekleme

**1. Form Doldurma**
```
- Grup Adı: (Zorunlu, 2-100 karakter, benzersiz)
  Örnek: İçecekler, Atıştırmalıklar, Alkollü İçecekler
- Açıklama: (Opsiyonel, max 500 karakter)
```

**2. Kaydetme**
- "Ekle" butonuna tıklayın
- Başarı mesajı
- Grup listesinde görünür

#### Grup Listesi

**Görünüm:**
- Tüm gruplar tablo halinde
- Grup adına göre alfabetik sıralı
- Aktif/Pasif durumu
- İşlem butonları

**İşlem Butonları:**
- 🖊️ **Düzenle:** Grup adı ve açıklama değiştir
- 🗑️ **Sil:** Grubu sil (ürün yoksa)
- 🔒 **Pasif Yap:** Grubu pasif et
- 🔓 **Aktif Yap:** Grubu aktif et

⚠️ **Önemli:** Gruba ait ürün varsa silinemez!

### 2.3 Ürün Yönetimi

#### Erişim
```
URL: /urunler
Menü: Admin → Ürünler
```

#### Yeni Ürün Ekleme

**1. Form Doldurma**
```
- Ürün Grubu: (Dropdown, zorunlu)
- Ürün Adı: (Zorunlu, 2-200 karakter)
  Örnek: Coca Cola 330ml, Çikolata, Cips
- Barkod: (Opsiyonel, max 50 karakter, benzersiz)
  Örnek: 8690504123456
- Birim: (Dropdown, zorunlu)
  Seçenekler: Adet, Şişe, Kutu, Paket, Gram, Kilogram, Litre
- Kritik Stok Seviyesi: (Zorunlu, 0-10000)
  Bu seviyenin altında uyarı verilir
```

**2. Kaydetme**
- "Ekle" butonuna tıklayın
- Başarı mesajı
- Ürün listesinde görünür
- Stok hareketi otomatik başlatılır (0 stok)

#### Ürün Listesi

**Görünüm:**
- Tüm ürünler tablo halinde
- Filtreleme ve arama
- Grup bilgisi gösterilir
- Mevcut stok gösterilir
- Stok durumu badge'i (Kritik/Dikkat/Normal)

**Stok Durumu Göstergeleri:**
```
🔴 Kritik: Stok ≤ Kritik Seviye
🟡 Dikkat: Stok ≤ Kritik Seviye × 1.5
🟢 Yeterli: Stok > Kritik Seviye × 1.5
```

**İşlem Butonları:**
- 🖊️ **Düzenle:** Ürün bilgilerini güncelle
- 🗑️ **Sil:** Ürünü sil (stok hareketi yoksa)
- 🔒 **Pasif Yap:** Ürünü pasif et
- 🔓 **Aktif Yap:** Ürünü aktif et

#### Ürün Düzenleme

**Güncellenebilir Alanlar:**
- Ürün adı
- Ürün grubu
- Barkod
- Birim
- Kritik stok seviyesi

**Güncellenemez:**
- ID (otomatik)
- Oluşturma tarihi

### 2.4 Personel Yönetimi

Admin kullanıcılar, Sistem Yöneticisi ile aynı personel yönetimi yetkilerine sahiptir.

**Erişim:** `/personel-tanimla`

**Yetkiler:**
- Yeni personel ekleme
- Personel düzenleme
- Personel pasif/aktif yapma
- Şifre sıfırlama

---

## 3. DEPO SORUMLUSU KULLANIM KILAVUZU

### 3.1 Dashboard

#### Erişim
```
URL: /depo
Menü: Otomatik yönlendirme (login sonrası)
```

#### Dashboard Bileşenleri

**1. İstatistik Kartları**
- **Toplam Ürün:** Aktif ürün sayısı
- **Kritik Ürün:** Kritik stokta olan ürünler
- **Aktif Zimmetler:** Devam eden zimmet sayısı
- **Bu Ay İadeler:** Aylık iade işlemi sayısı

**2. Stok Durum Özeti**
- Kritik stokta olanlar (Kırmızı)
- Dikkat gerektiren (Sarı)
- Yeterli stokta olanlar (Yeşil)

**3. Son Stok Hareketleri**
- Son 10 işlem
- Tarih, ürün, hareket tipi, miktar

**4. Grafikler**
- Grup bazlı stok durumu (Bar grafik)
- Son 7 günün stok hareketleri (Line grafik)
- Ürün bazlı tüketim (Bar grafik)

### 3.2 Stok Girişi

#### Erişim
```
URL: /stok-giris
Menü: Depo Sorumlusu → Stok Girişi
```

#### Stok Girişi Yapma

**1. Form Doldurma**
```
- Ürün: (Dropdown, aktif ürünler)
- Hareket Tipi: (Dropdown)
  * Giriş: Yeni stok girişi
  * Devir: Devir stok
  * Sayım: Sayım düzeltmesi
- Miktar: (Pozitif sayı, 1-1,000,000)
- Açıklama: (Opsiyonel, max 500 karakter)
```

**2. Kaydetme**
- "Kaydet" butonuna tıklayın
- Stok otomatik güncellenir
- İşlem loglanır
- Başarı mesajı görüntülenir

#### Stok Hareketleri Listesi

**Görünüm:**
- Son 50 hareket gösterilir
- Tarih, ürün, hareket tipi, miktar, açıklama
- İşlem yapan kullanıcı
- Filtreleme ve arama

**İşlem Butonları:**
- 🖊️ **Düzenle:** Hareketi düzenle
- 🗑️ **Sil:** Hareketi sil

⚠️ **Uyarı:** Stok düzenlemesi ve silme işlemleri dikkatle yapılmalıdır!

### 3.3 Personel Zimmet

#### Erişim
```
URL: /personel-zimmet
Menü: Depo Sorumlusu → Personel Zimmet
```

#### Yeni Zimmet Atama

**1. Personel Seçimi**
- Dropdown'dan Kat Sorumlusu seçin
- Sadece aktif kat sorumluları görünür

**2. Ürün Seçimi**
```
- Ürün Gruplarına Göre Listeleme
- Her ürün için:
  * Checkbox ile seçim
  * Miktar girişi
  * Mevcut stok gösterimi
  * Birim bilgisi
```

**3. Stok Kontrolü**
- Seçilen ürünler için toplam miktar hesaplanır
- Stok uygunluğu kontrol edilir
- Yetersiz stokta uyarı verilir
- Detaylı hata mesajları

**4. Zimmet Oluşturma**
```
- Açıklama: (Opsiyonel)
- "Zimmet Ata" butonuna tıklayın
```

**5. İşlem Sonuçları**
- Zimmet başlık kaydı oluşturulur
- Her ürün için detay kaydı oluşturulur
- Stoktan otomatik çıkış yapılır
- Personelin zimmeti güncellenir
- Başarı mesajı

#### Aktif Zimmetler Listesi

**Görünüm:**
- Tüm aktif zimmetler tablo halinde
- Personel adı
- Zimmet tarihi
- Ürün sayısı
- Toplam miktar
- İşlem butonları

**İşlem Butonları:**
- 👁️ **Detay:** Zimmet detaylarını görüntüle
- ❌ **İptal:** Zimmeti iptal et (tümünü iade al)

#### Zimmet Detay

**Erişim:** `/zimmet-detay/<zimmet_id>`

**Görüntülenen Bilgiler:**
```
Zimmet Başlık:
- Zimmet No
- Personel Adı
- Teslim Eden
- Zimmet Tarihi
- Durum (Aktif/Tamamlandı/İptal)
- Açıklama

Zimmet Detayları (Ürünler):
- Ürün Adı, Birim
- Teslim Edilen Miktar
- Kullanılan Miktar
- İade Edilen Miktar
- Kalan Miktar
- İşlem Butonu: 📥 İade Al
```

**İade Alma İşlemi:**
1. İade Al butonuna tıklayın
2. İade miktarı girin (maksimum: kalan miktar)
3. Açıklama ekleyin (opsiyonel)
4. "İade Al" butonuna tıklayın
5. Stoka otomatik giriş yapılır
6. Zimmet detayı güncellenir

**Zimmet İptal:**
- Tüm kalan ürünler depoya iade edilir
- Zimmet durumu "İptal" olur
- Stok otomatik güncellenir

### 3.4 Minibar Durumları

#### Erişim
```
URL: /minibar-durumlari
Menü: Depo Sorumlusu → Minibar Durumları
```

#### Minibar Görüntüleme

**1. Kat Seçimi**
- Dropdown'dan kat seçin
- Odalar otomatik yüklenir

**2. Oda Seçimi**
- Dropdown'dan oda seçin
- Minibar içeriği yüklenir

**3. Minibar İçeriği**
```
Gösterilen Bilgiler:
- Oda bilgisi (Kat, Oda No)
- Son işlem tarihi ve tipi
- Ürün listesi:
  * Ürün adı
  * Mevcut stok
  * Toplam eklenen
  * Toplam tüketim
  * Birim
```

**4. Ürün Geçmişi**
- Her ürün için "Geçmiş" butonuna tıklayın
- Modal popup açılır
- Tüm minibar işlemleri kronolojik gösterilir
- İşlem tarihi, tipi, başlangıç, eklenen, tüketim, bitiş

### 3.5 Raporlar

#### Erişim
```
URL: /depo-raporlar
Menü: Depo Sorumlusu → Raporlar
```

#### Rapor Tipleri

**1. Stok Durum Raporu**
```
İçerik:
- Tüm ürünlerin mevcut stok durumu
- Ürün adı, grup, birim
- Mevcut stok, kritik seviye
- Durum (Kritik/Normal)

Filtreler:
- Ürün Grubu
```

**2. Stok Hareket Raporu**
```
İçerik:
- Detaylı stok hareketleri
- Tarih, ürün, hareket tipi, miktar
- İşlem yapan, açıklama
- Zimmet bilgisi (varsa)

Filtreler:
- Tarih Aralığı
- Ürün/Ürün Grubu
- Hareket Tipi (Giriş/Çıkış)
```

**3. Zimmet Raporu**
```
İçerik:
- Tüm zimmet kayıtları
- Zimmet no, personel, tarih
- Ürün sayısı, toplam miktar
- Durum (Aktif/Tamamlandı/İptal)

Filtreler:
- Tarih Aralığı
- Personel
```

**4. Zimmet Detay Raporu**
```
İçerik:
- Ürün bazlı zimmet bilgileri
- Personel, ürün, miktar
- Kullanım durumu

Filtreler:
- Tarih Aralığı
- Personel
- Ürün/Ürün Grubu
```

**5. Minibar Tüketim Raporu**
```
İçerik:
- Oda bazlı tüketim kayıtları
- Sadece gerçek tüketim (kontrol/doldurma)
- Ürün, oda, kat, tarih, tuketim
- Kat sorumlusu bilgisi

Filtreler:
- Tarih Aralığı
- Personel
- Ürün/Ürün Grubu
```

**6. Ürün Grubu Raporu**
```
İçerik:
- Grup bazlı stok istatistikleri
- Grup adı
- Toplam ürün sayısı
- Kritik stoklu ürün sayısı
```

**7. Özet Rapor**
```
İçerik:
- Genel sistem durumu
- Toplam ürün
- Kritik ürün sayısı
- Aktif zimmet
- Bugünkü giriş/çıkış
- Bu ayki zimmet sayısı
```

#### Rapor Export

**Excel Export:**
- Her rapor için Excel butonu
- Filtrelenmiş veriler export edilir
- Otomatik formatlanmış tablo
- Başlık ve stil uygulanır

**PDF Export:**
- Her rapor için PDF butonu
- Filtrelenmiş veriler export edilir
- Türkçe karakter desteği (ASCII dönüşüm)
- Tablo formatında çıktı
- Maksimum 100 kayıt (performans için)

---

# BÖLÜM 3: KAT SORUMLUSU VE ÖZELLİK DETAYLARI

## 1. KAT SORUMLUSU KULLANIM KILAVUZU

### 1.1 Dashboard

#### Erişim
```
URL: /kat-sorumlusu
Menü: Otomatik yönlendirme (login sonrası)
```

#### Dashboard Bileşenleri

**1. İstatistik Kartları**
- **Aktif Zimmetler:** Sahip olunan aktif zimmet sayısı
- **Zimmet Toplamı:** Zimmetteki toplam ürün miktarı

**2. Son Minibar İşlemleri**
- Son 10 işlem
- Oda, işlem tipi, tarih

**3. Grafikler**
- Zimmet kullanım durumu (Bar grafik - Ürün bazlı)
- Minibar işlem tipi dağılımı (Pasta grafik)

### 1.2 Zimmetim

#### Erişim
```
URL: /zimmetim
Menü: Kat Sorumlusu → Zimmetim
```

#### Zimmet Görüntüleme

**Zimmet İstatistikleri:**
- Toplam Zimmet: Teslim alınan toplam miktar
- Kullanılan: Minibar'lara aktarılan miktar
- Kalan: Henüz kullanılmayan miktar

**Aktif Zimmetler Listesi:**
```
Her Zimmet için:
- Zimmet No
- Zimmet Tarihi
- Teslim Eden (Depo Sorumlusu)
- Ürün Detayları (Genişletilebilir)

Ürün Detayları:
- Ürün Adı, Birim
- Teslim Edilen Miktar
- Kullanılan Miktar
- Kalan Miktar
- Kullanım Yüzdesi (Progress bar)
```

### 1.3 Minibar Kontrol

#### Erişim
```
URL: /minibar-kontrol
Menü: Kat Sorumlusu → Minibar Kontrol
```

#### İşlem Tipleri

**1. İlk Dolum**
- Yeni odanın ilk defa doldurulması
- Tüm ürünler için başlangıç stoku eklenir
- Zimmetten düşüm yapılır

**2. Kontrol**
- Minibar içeriğini görüntüleme
- Kayıt oluşturmaz (sadece görüntüleme)
- Mevcut stok bilgisi gösterilir

**3. Doldurma**
- Tüketilmiş ürünlerin yeniden doldurulması
- Gerçek sayım yapılır
- Tüketim hesaplanır
- Zimmetten düşüm yapılır

#### İlk Dolum İşlemi

**Adımlar:**

**1. Kat Seçimi**
- Dropdown'dan kat seçin
- Odalar otomatik yüklenir

**2. Oda Seçimi**
- Dropdown'dan oda seçin
- İlk dolum yapılmamış oda olmalı

**3. İşlem Tipi Seçimi**
- "İlk Dolum" seçin

**4. Ürün Seçimi ve Miktar Girişi**
```
- Ürün gruplarına göre listelenir
- Her ürün için:
  * Checkbox ile seçim
  * Miktar girişi
  * Zimmetteki miktar gösterilir
  * Yetersiz zimmet uyarısı
```

**5. Kaydetme**
- "Kaydet" butonuna tıklayın
- Zimmet kontrolü yapılır
- Minibar kaydı oluşturulur
- Zimmetten otomatik düşüm yapılır
- Başarı mesajı

#### Kontrol İşlemi

**Adımlar:**

**1. Kat ve Oda Seçimi**
- Daha önce dolum yapılmış oda seçin

**2. İşlem Tipi**
- "Kontrol" seçin

**3. Mevcut Durum Görüntüleme**
- Odanın son minibar durumu gösterilir
- Her ürün için mevcut stok
- Son işlem tarihi

**4. Kayıt**
- "Görüntüle" butonuna tıklayın
- Sistem logu oluşturulur
- Minibar kaydı oluşturulmaz

#### Doldurma İşlemi (Tekli)

**Adımlar:**

**1. Kat ve Oda Seçimi**
- İlk dolum yapılmış oda seçin

**2. İşlem Tipi**
- "Doldurma" seçin

**3. Mevcut Durum Yükleme**
- Odanın son minibar durumu otomatik yüklenir
- Her ürün için mevcut stok gösterilir

**4. Gerçek Sayım ve Doldurma**
```
Her Ürün için:
- Mevcut Stok: Kayıtlı değer (otomatik)
- Gerçek Stok: Sayım sonucu (manuel girilir)
- Eklenecek: Doldurulacak miktar (manuel girilir)

Hesaplama:
- Tüketim = Kayıtlı Stok - Gerçek Stok
- Yeni Stok = Gerçek Stok + Eklenecek
```

**5. Zimmet Kontrolü**
- Eklenen miktarlar zimmet ile karşılaştırılır
- Yetersiz zimmet uyarısı
- Kullanılabilir zimmet gösterilir

**6. Kaydetme**
- Tüm ürünler için bilgi girildikten sonra
- "Kaydet" butonuna tıklayın
- Minibar kaydı oluşturulur
- Tüketim kaydedilir
- Zimmetten düşüm yapılır

### 1.4 Toplu Oda Doldurma

#### Erişim
```
URL: /toplu-oda-doldurma
Menü: Kat Sorumlusu → Toplu Oda Doldurma
```

#### Özellikler

**Avantajlar:**
- Birden fazla odaya aynı anda ürün ekleme
- Zaman tasarrufu
- Toplu işlem desteği
- Detaylı durum raporlama

**Limitler:**
- Sadece doldurma işlemi (tüketim takibi yok)
- Direkt stok ekleme
- İlk dolum yapılmış odalara uygulanır

#### İşlem Adımları

**1. Kat Seçimi**
- Dropdown'dan kat seçin
- Odalar otomatik checkbox listesi olarak yüklenir

**2. Oda Seçimi**
- İstediğiniz odaları seçin (çoklu seçim)
- "Tümünü Seç" / "Tümünü Kaldır" butonları

**3. Ürün Seçimi**
- Ürün grubu seçin (opsiyonel filtreleme)
- Dropdown'dan ürün seçin

**4. Miktar Belirleme**
- Tüm seçili odalara eklenecek miktar
- Tek bir miktar değeri

**5. Mevcut Durum Görüntüleme**
- "Mevcut Durumu Göster" butonuna tıklayın
- Her oda için mevcut stok gösterilir
- Tablo formatında

**6. Zimmet Kontrolü**
```
Hesaplama:
Toplam Gerekli = Oda Sayısı × Eklenecek Miktar

Kontroller:
- Zimmette yeterli ürün var mı?
- Yetersiz zimmet uyarısı
- Kalan zimmet gösterimi
```

**7. Toplu Doldurma**
- "Toplu Doldur" butonuna tıklayın
- Her oda için işlem başlatılır
- İlerleme gösterilir

**8. Sonuç Raporu**
```
Gösterilen Bilgiler:
- Başarılı Oda Sayısı
- Başarısız Oda Sayısı
- Başarılı Odalar Listesi (Oda No)
- Başarısız Odalar ve Hata Mesajları
- Kullanılan Toplam Zimmet
```

#### Toplu İşlem Detayları

**Arka Plan İşlemi:**
1. Her oda için sırayla işlem yapılır
2. Mevcut minibar durumu alınır
3. Diğer ürünler değişmeden kopyalanır
4. Seçilen ürün için yeni kayıt oluşturulur
5. Zimmetten FIFO mantığıyla düşüm yapılır
6. Hata oluşursa o oda atlanır, diğerleri devam eder

**Önemli Notlar:**
- Tüketim takibi yapılmaz (direkt ekleme)
- Mevcut stoka eklenir
- İlk dolum yapılmamış odalara uygulanamaz
- Zimmetten otomatik düşüm yapılır

### 1.5 Kat Bazlı Rapor

#### Erişim
```
URL: /kat-bazli-rapor
Menü: Kat Sorumlusu → Raporlar → Kat Bazlı Rapor
```

#### Rapor Özellikleri

**Gösterilen Bilgiler:**
- Kat adı ve oda sayısı
- Her oda için:
  * Oda numarası
  * Son işlem tarihi
  * Ürün bazlı mevcut stok
  * Toplam tüketim
- Ürün özeti (Kat geneli)

**Filtreler:**
- Tarih Aralığı: Başlangıç - Bitiş

**İşlemler:**
1. Kat seçin
2. Tarih aralığı belirleyin (opsiyonel)
3. "Rapor Oluştur" butonuna tıklayın
4. Rapor dinamik olarak oluşturulur

**Rapor Bölümleri:**

**1. Kat Özeti**
- Kat adı
- Oda sayısı
- Toplam ürün çeşidi

**2. Oda Detayları**
```
Tablo Sütunları:
- Oda No
- Son İşlem Tarihi
- Ürün Listesi (Genişletilebilir)
  * Ürün Adı
  * Mevcut Stok
  * Tüketim
  * Birim
```

**3. Ürün Özeti**
```
Kat genelinde ürün bazlı toplam:
- Ürün Adı
- Toplam Tüketim
- Birim
Sıralama: En çok tüketilenden en aza
```

### 1.6 Kişisel Raporlar

#### Erişim
```
URL: /kat-raporlar
Menü: Kat Sorumlusu → Raporlar
```

#### Rapor Tipleri

**1. Minibar İşlem Raporu**
```
İçerik:
- Kendi yaptığı tüm minibar işlemleri
- Tarih, oda, işlem tipi, ürün sayısı

Filtreler:
- Tarih Aralığı
```

**2. Tüketim Raporu**
```
İçerik:
- Ürün bazlı toplam tüketim
- Sadece kendi işlemleri
- Ürün adı, toplam tüketim, işlem sayısı

Filtreler:
- Tarih Aralığı
```

**3. Oda Bazlı Rapor**
```
İçerik:
- Oda bazlı işlem ve tüketim istatistikleri
- Sadece kendi işlemleri
- Oda no, işlem sayısı, toplam tüketim, son işlem

Filtreler:
- Tarih Aralığı
```

---

## 2. STOK YÖNETİMİ DETAYLARI

### 2.1 Stok Hesaplama Algoritması

#### Temel Formül
```
Mevcut Stok = Giriş - Çıkış

Detaylı:
Giriş Toplamı = SUM(Giriş + Devir + Sayım)
Çıkış Toplamı = SUM(Çıkış)
Mevcut Stok = Giriş Toplamı - Çıkış Toplamı
```

#### Stok Hareket Tipleri

**1. Giriş**
- Yeni stok alımı
- Tedarikçiden gelen ürünler
- Stoku artırır

**2. Çıkış**
- Personel zimmet atama
- Stoku azaltır
- Otomatik oluşturulur (zimmet atamada)

**3. Devir**
- Başlangıç stoku
- Eski sistemden aktarım
- Stoku artırır

**4. Sayım**
- Sayım sonucu düzeltme
- Fire/Fazla düzeltme
- Pozitif/Negatif olabilir

### 2.2 Kritik Stok Uyarı Sistemi

#### Stok Seviyeleri

**1. Kritik (Kırmızı)**
```
Koşul: Mevcut Stok ≤ Kritik Seviye
Durum: Acil sipariş gerekli
Görünüm: Kırmızı badge, uyarı ikonu
```

**2. Dikkat (Sarı)**
```
Koşul: Kritik Seviye < Mevcut Stok ≤ (Kritik Seviye × 1.5)
Durum: Yakında sipariş gerekli
Görünüm: Sarı badge, dikkat ikonu
```

**3. Yeterli (Yeşil)**
```
Koşul: Mevcut Stok > (Kritik Seviye × 1.5)
Durum: Stok yeterli
Görünüm: Yeşil badge, onay ikonu
```

#### Kritik Stok Bildirimleri

**Dashboard'ta:**
- Kritik ürün sayısı gösterilir
- Kritik ürünler listesi
- Renk kodlu gösterimler

**Ürün Listesinde:**
- Her ürün için stok durumu badge'i
- Filtreleme seçeneği (Sadece Kritik)
- Mevcut stok ve kritik seviye gösterimi

### 2.3 Stok Takip Best Practices

**1. Düzenli Sayım**
- Periyodik fiziksel sayım yapın
- Sayım sonuçlarını sisteme girin
- Fire/Fazla nedenleri belirtin

**2. Kritik Seviye Ayarları**
- Gerçekçi kritik seviyeler belirleyin
- Tüketim hızına göre ayarlayın
- Tedarik süresini dikkate alın

**3. Zimmet Yönetimi**
- Gereksiz zimmetten kaçının
- Düzenli iade alın
- Kullanılmayan zimmetleri iptal edin

**4. Raporlama**
- Düzenli stok raporları alın
- Tüketim trendlerini takip edin
- Anomalileri araştırın

---

## 3. ZİMMET SİSTEMİ DETAYLARI

### 3.1 Zimmet Yaşam Döngüsü

#### Adımlar

**1. Zimmet Atama (Depo Sorumlusu)**
```
İşlem:
- Personel seçimi
- Ürün ve miktar belirleme
- Stok kontrolü
- Zimmet kaydı oluşturma
- Stoktan otomatik çıkış

Sonuç:
- Zimmet Durumu: Aktif
- Stok güncellenir
- Personele bildirim (opsiyonel)
```

**2. Zimmet Kullanımı (Kat Sorumlusu)**
```
İşlem:
- Minibar doldurma sırasında
- Otomatik zimmetten düşüm
- FIFO mantığı (İlk giren ilk çıkar)

Sonuç:
- Kullanılan miktar artar
- Kalan miktar azalır
- Zimmet detayı güncellenir
```

**3. Zimmet İadesi (Depo Sorumlusu)**
```
İşlem:
- Zimmet detay sayfasından
- İade miktarı girişi
- Açıklama ekleme

Sonuç:
- İade edilen miktar artar
- Kalan miktar azalır
- Stoka otomatik giriş
```

**4. Zimmet İptali (Depo Sorumlusu)**
```
İşlem:
- Tüm kalan ürünleri iade al
- Zimmet iptal et

Sonuç:
- Zimmet Durumu: İptal
- Tüm kalan ürünler stoka girer
- Zimmet kapatılır
```

**5. Zimmet Tamamlanması (Otomatik)**
```
Koşul:
- Tüm ürünler kullanıldı veya iade edildi
- Kalan miktar = 0

Sonuç:
- Zimmet Durumu: Tamamlandı
- Zimmet tarihi kaydedilir
```

### 3.2 Zimmet Algoritmaları

#### FIFO (First In First Out)

**Zimmet Kullanımında:**
```python
Senaryo:
Personelin 3 ayrı zimmet kaydı var:
- Zimmet 1: 100 adet (50 kullanılmış, 50 kalan)
- Zimmet 2: 200 adet (0 kullanılmış, 200 kalan)
- Zimmet 3: 150 adet (0 kullanılmış, 150 kalan)

80 adet kullanım yapılacak:
1. Zimmet 1'den 50 adet düşülür (tamamlandı)
2. Zimmet 2'den 30 adet düşülür
3. Toplam 80 adet

Sonuç:
- Zimmet 1: 100 kullanılmış, 0 kalan (Tamamlandı)
- Zimmet 2: 30 kullanılmış, 170 kalan
- Zimmet 3: 0 kullanılmış, 150 kalan
```

#### Zimmet Kontrolü

**Yeterlilik Kontrolü:**
```python
Kontrol:
1. Ürün ID'ye göre tüm aktif zimmetleri bul
2. Her zimmetteki kalan miktarı topla
3. Toplam kalan ≥ Kullanılacak miktar?
   - Evet: İşlem devam eder
   - Hayır: Hata mesajı gösterilir
```

**Zimmet Bilgilendirme:**
```
Kullanıcı Arayüzünde:
- Zimmetteki Miktar: Her ürün için gösterilir
- Renk Kodları:
  * Yeşil: Yeterli zimmet
  * Kırmızı: Yetersiz zimmet
- Tooltip: Detaylı zimmet bilgisi
```

### 3.3 Zimmet Raporlama

**Zimmet Özet Raporu:**
- Personel bazlı zimmet durumu
- Teslim edilen, kullanılan, kalan miktarlar
- Kullanım yüzdesi

**Zimmet Detay Raporu:**
- Ürün bazlı zimmet bilgileri
- Tüm zimmet hareketleri
- Tarih bazlı filtreleme

**Zimmet Geçmişi:**
- Personel bazlı tüm zimmet kayıtları
- Aktif, tamamlanmış, iptal edilmiş
- Detaylı zimmet analizi

---

## 4. MİNİBAR İŞLEMLERİ DETAYLARI

### 4.1 Minibar Veri Modeli

#### İşlem Başlık (MinibarIslem)
```
Alanlar:
- id: Benzersiz işlem no
- oda_id: Hangi oda
- personel_id: İşlemi yapan kat sorumlusu
- islem_tipi: ilk_dolum / kontrol / doldurma
- islem_tarihi: İşlem zamanı
- aciklama: Ek notlar
```

#### İşlem Detay (MinibarIslemDetay)
```
Alanlar:
- id: Benzersiz detay no
- islem_id: Hangi işleme ait
- urun_id: Hangi ürün
- baslangic_stok: İşlem öncesi stok
- bitis_stok: İşlem sonrası stok
- tuketim: Tüketilen miktar
- eklenen_miktar: Eklenen miktar
- zimmet_detay_id: Hangi zimmetten kullanıldı
```

### 4.2 İşlem Tipi Algoritmaları

#### İlk Dolum
```
Adımlar:
1. Oda seçimi (ilk dolum yapılmamış)
2. Ürün ve miktar seçimi
3. Zimmet kontrolü
4. MinibarIslem kaydı oluştur (islem_tipi: ilk_dolum)
5. Her ürün için MinibarIslemDetay oluştur:
   - baslangic_stok = 0
   - eklenen_miktar = Girilen miktar
   - bitis_stok = Eklenen miktar
   - tuketim = 0
6. Zimmetten düşüm yap (FIFO)
7. Başarı mesajı
```

#### Kontrol
```
Adımlar:
1. Oda seçimi (daha önce dolum yapılmış)
2. İşlem tipi: Kontrol
3. Son minibar durumu gösterilir
4. Kayıt OLUŞTURULMAZ (sadece görüntüleme)
5. Sistem logu kaydedilir
6. İşlem tamamlandı mesajı
```

#### Doldurma (Tekli)
```
Adımlar:
1. Oda seçimi
2. Son minibar durumu yüklenir (otomatik)
3. Her ürün için:
   a. Gerçek stok sayımı (manuel giriş)
   b. Eklenecek miktar (manuel giriş)
   c. Tüketim hesaplama:
      Tüketim = Kayıtlı Stok - Gerçek Stok
   d. Yeni stok hesaplama:
      Yeni Stok = Gerçek Stok + Eklenecek
4. Zimmet kontrolü (Eklenen miktar için)
5. MinibarIslem kaydı oluştur (islem_tipi: doldurma)
6. Diğer ürünleri kopyala (değişmeden)
7. Her değişen ürün için MinibarIslemDetay oluştur:
   - baslangic_stok = Gerçek Stok
   - eklenen_miktar = Eklenecek
   - bitis_stok = Yeni Stok
   - tuketim = Hesaplanan tüketim
8. Zimmetten düşüm yap (FIFO, sadece eklenen miktar)
9. Başarı mesajı
```

#### Doldurma (Toplu)
```
Adımlar:
1. Kat ve odalar seçimi (çoklu)
2. Ürün ve miktar seçimi (tek ürün, tek miktar)
3. Toplam zimmet kontrolü:
   Gerekli = Oda Sayısı × Miktar
4. Her oda için sırayla:
   a. Son minibar durumu al
   b. MinibarIslem kaydı oluştur
   c. Diğer ürünleri kopyala
   d. Seçilen ürün için detay oluştur:
      - baslangic_stok = Mevcut
      - eklenen_miktar = Miktar
      - bitis_stok = Mevcut + Miktar
      - tuketim = 0 (Toplu işlemde tüketim takibi yok)
   e. Zimmetten düşüm yap
   f. Hata varsa logla ve devam et
5. Sonuç raporu göster:
   - Başarılı odalar
   - Başarısız odalar ve hata mesajları
```

### 4.3 Minibar Mevcut Durum Hesaplama

#### Algoritma
```
Oda için son işlem:
1. MinibarIslem tablosunda oda_id ile son kaydı bul
2. Bu işleme ait tüm MinibarIslemDetay kayıtlarını al
3. Her detay için bitis_stok değerini al
4. Bu değerler = Mevcut minibar içeriği
```

#### API Endpoint
```
GET /api/minibar-icerigi/<oda_id>

Yanıt:
{
  "success": true,
  "urunler": [
    {
      "urun_id": 1,
      "urun_adi": "Coca Cola",
      "grup_adi": "İçecekler",
      "birim": "Şişe",
      "mevcut_stok": 5,
      "son_islem_tarihi": "31.10.2025 14:30"
    }
  ],
  "ilk_dolum": false,
  "son_islem_tipi": "doldurma"
}
```

### 4.4 Minibar Geçmiş

#### Görüntüleme
```
Erişim: Depo Sorumlusu → Minibar Durumları → Ürün Geçmişi

Bilgiler:
- Tüm işlemler kronolojik (Yeniden eskiye)
- Her işlem için:
  * İşlem tarihi ve saati
  * İşlem tipi (İlk Dolum/Kontrol/Doldurma)
  * Personel adı
  * Başlangıç stok
  * Eklenen miktar
  * Tüketim
  * Bitiş stok
  * Açıklama
```

#### API Endpoint
```
GET /minibar-urun-gecmis/<oda_id>/<urun_id>

Yanıt:
{
  "success": true,
  "oda": "101",
  "urun": "Coca Cola",
  "gecmis": [...]
}
```

---

*Bu dokümantasyon sürekli güncellenmektedir. Son güncelleme: 31 Ekim 2025*
