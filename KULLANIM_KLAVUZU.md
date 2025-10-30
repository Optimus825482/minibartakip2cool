# 📖 Otel Minibar Takip Sistemi - Kullanım Kılavuzu

## 📋 İçindekiler

1. [Sistem Hakkında](#sistem-hakkında)
2. [İlk Kurulum](#ilk-kurulum)
3. [Kullanıcı Rolleri ve Yetkiler](#kullanıcı-rolleri-ve-yetkiler)
4. [Sistem Akış Şeması](#sistem-akış-şeması)
5. [Modül Bazlı Kullanım](#modül-bazlı-kullanım)
6. [Sık Sorulan Sorular](#sık-sorulan-sorular)

---

## 🎯 Sistem Hakkında

Otel Minibar Takip Sistemi, otellerde minibar işlemlerini, stok yönetimini ve personel zimmet takibini dijital ortamda yönetmenizi sağlayan web tabanlı bir uygulamadır.

### Temel Özellikler

- ✅ **Rol Tabanlı Yetkilendirme**: 4 farklı kullanıcı rolü
- 📊 **Stok Yönetimi**: Ürün girişi, çıkışı, kritik stok uyarıları
- 🛏️ **Minibar İşlemleri**: İlk dolum, kontrol, doldurma
- 📦 **Personel Zimmet**: Ürün zimmetleme ve takibi
- 📈 **Raporlama**: Detaylı stok, tüketim ve zimmet raporları
- 🔔 **Dashboard**: Her rol için özelleştirilmiş kontrol paneli

---

## 🚀 İlk Kurulum

### Adım 1: Sisteme İlk Giriş

1. Tarayıcınızda uygulamanın URL'ini açın
2. İlk açılışta **"İlk Kurulum"** sayfası otomatik gelir
3. Bu sayfa sadece sistem ilk kez kurulurken görünür

### Adım 2: Otel Bilgilerini Girin

**İlk Kurulum Formunda:**
- **Otel Adı**: Otelin resmi adı (örn: Grand Hotel Istanbul)
- **Adres**: Tam adres bilgisi
- **Telefon**: İletişim telefonu
- **E-posta**: Otel e-posta adresi

### Adım 3: Sistem Yöneticisi Oluşturun

**Sistem Yöneticisi Bilgileri:**
- **Ad**: Yöneticinin adı
- **Soyad**: Yöneticinin soyadı
- **E-posta**: Giriş için kullanılacak e-posta
- **Şifre**: Güçlü bir şifre belirleyin
- **Şifre Tekrar**: Şifreyi doğrulayın

### Adım 4: İlk Giriş

1. "Kurulumu Tamamla" butonuna tıklayın
2. Login sayfasına yönlendirileceksiniz
3. Oluşturduğunuz e-posta ve şifre ile giriş yapın

---

## 👥 Kullanıcı Rolleri ve Yetkiler

### 1. � Admin (Sistem Yöneticisi)

**Yetkiler:**
- ✅ Otel bilgilerini düzenleme
- ✅ Kat ve oda yönetimi
- ✅ Ürün grupları yönetimi
- ✅ Ürün tanımlama ve düzenleme
- ✅ Personel (Depo Sorumlusu ve Kat Sorumlusu) tanımlama
- ✅ Admin kullanıcı atama/çıkarma
- ✅ Sistem loglarını görüntüleme
- ✅ Tüm raporlara erişim
- ✅ Tüm modüllere erişim

**Ana Görevler:**
1. Katları tanımlama (örn: 1. Kat, 2. Kat)
2. Odaları tanımlama (örn: 101, 102, 201)
3. Ürün gruplarını oluşturma (örn: İçecekler, Atıştırmalıklar)
4. Ürünleri tanımlama (örn: Coca Cola 330ml, Çikolata)
5. Tüm personeli (Admin, Depo Sorumlusu, Kat Sorumlusu) sisteme ekleme
6. Sistem kontrolü ve log takibi
7. Genel raporları inceleme

### 2. 📦 Depo Sorumlusu

**Yetkiler:**
- ✅ Stok girişi yapma
- ✅ Personel zimmet atama ve takibi
- ✅ Minibar durumlarını görüntüleme
- ✅ Stok ve tüketim raporları
- ❌ Ürün tanımlama yetkisi yok

**Ana Görevler:**
1. Depoya gelen ürünleri sisteme giriş yapmak
2. Kat sorumlularına zimmet oluşturmak
3. Zimmet iadelerini almak
4. Minibar tüketimlerini takip etmek
5. Kritik stok kontrolü

### 3. 🛏️ Kat Sorumlusu

**Yetkiler:**
- ✅ Minibar ilk dolum, kontrol, doldurma
- ✅ Kendi zimmetini görüntüleme
- ✅ Zimmetli ürünleri kullanma
- ✅ Kendi raporlarını görüntüleme
- ❌ Başka katların verilerine erişim yok

**Ana Görevler:**
1. Odaların ilk dolumunu yapmak
2. Minibar kontrollerini gerçekleştirmek
3. Tüketilen ürünleri doldurmak
4. Zimmetli ürünleri kullanmak

---

## 📊 Sistem Akış Şeması

```
┌─────────────────────────────────────────────────────────────┐
│                    İLK KURULUM                               │
│      Otel Bilgileri → İlk Admin Oluştur                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   ADMİN AYARLARI                             │
│  • Kat Tanımla (1.Kat, 2.Kat, vb.)                          │
│  • Oda Tanımla (101, 102, 201, vb.)                          │
│  • Ürün Grupları Oluştur (İçecek, Gıda, Atıştırmalık)       │
│  • Ürünler Tanımla (Coca Cola, Su, Çikolata, vb.)           │
│  • Personel Tanımla (Depo Sorumlusu, Kat Sorumluları)       │
│  • Diğer Admin Kullanıcıları Ata (isteğe bağlı)             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 DEPO SORUMLUSU İŞLEMLERİ                     │
│  1. Stok Girişi Yap                                          │
│     └─> Tedarikçiden gelen ürünleri sisteme kaydet          │
│  2. Personel Zimmet Oluştur                                  │
│     └─> Kat sorumlusuna ürün zimmetleme                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                KAT SORUMLUSU İŞLEMLERİ                       │
│  1. Zimmetim Sayfası                                         │
│     └─> Kendisine zimmetlenen ürünleri görüntüle            │
│  2. İlk Dolum                                                │
│     └─> Yeni odaları ilk kez doldur                         │
│  3. Kontrol                                                  │
│     └─> Oda temizliğinde minibar kontrolü yap               │
│  4. Doldurma                                                 │
│     └─> Tüketilen ürünleri tamamla                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    RAPORLAMA                                 │
│  • Depo Sorumlusu: Stok, Tüketim, Zimmet Raporları          │
│  • Kat Sorumlusu: Minibar Tüketim, Kendi İşlemleri          │
│  • Admin: Tüm Sistem Raporları                               │
│  • Sistem Yöneticisi: Sistem Logları                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Detaylı İş Akışları

### 📦 Stok Yönetimi Akışı

```
1. Tedarikçi Gelişi
   ↓
2. Depo Sorumlusu: Stok Girişi
   • Ürün seç
   • Miktar gir
   • Birim fiyat (opsiyonel)
   • Açıklama ekle
   ↓
3. Sistem: Stok Güncelle
   • Mevcut stok artır
   • Stok hareketi kaydet
   ↓
4. Kritik Stok Kontrolü
   • Stok < Kritik Seviye ise UYARI
```

### 🛏️ Minibar İşlem Akışı ⭐ YENİ SİSTEM

```
YENİ ODA (İlk Dolum)
   ↓
1. Kat Sorumlusu: Minibar Kontrol
   • Kat seç → Oda seç
   • İşlem Tipi: İlk Dolum
   ↓
2. Ürün Seçimi (Toplu)
   • Ürün Grubu → Ürün → Miktar
   • Zimmet kontrolü gösterilir
   • Listeye Ekle
   • Tüm ürünler eklendikten sonra Kaydet
   ↓
3. Zimmet Kullanımı
   • Zimmetli ürünler FIFO mantığı ile düşer
   • Hangi zimmetten kullanıldığı kaydedilir
   ↓
4. Sistem Kaydı
   • Minibar işlemi oluştur (tarih, saat, kullanıcı)
   • Zimmet-Tüketim ilişkisi kur
   • Zimmet miktarları güncelle

────────────────────────────

ODA KONTROLÜ ⭐ YENİ
   ↓
1. Kat Sorumlusu: Minibar Kontrol
   • Kat seç → Oda seç
   • İşlem Tipi: Kontrol
   ↓
2. Minibar İçeriği Listesi
   • Tüm ürünler ve mevcut stokları gösterilir
   • Ürün Adı | Grup | Mevcut Stok | Birim
   • SADECE GÖRÜNTÜLEME (işlem yapılmaz)
   ↓
3. Bilgilendirme
   • Oda durumu kontrol edilir
   • Hangi ürünler ne kadar var görülür
   • İşlem kaydı OLUŞTURULMAZ

────────────────────────────

ODA DOLDURMA ⭐ YENİ SİSTEM
   ↓
1. Kat Sorumlusu: Minibar Kontrol
   • Kat seç → Oda seç
   • İşlem Tipi: Doldurma
   ↓
2. Minibar İçeriği Listesi
   • Tüm ürünler ve mevcut stokları gösterilir
   • Her satırda "EKLE" butonu
   ↓
3. TEK ÜRÜN DOLDURMA
   • "Ekle" butonuna tıkla
   • Modal açılır:
     - Ürün bilgisi
     - Mevcut stok
     - Zimmet durumu
   • Miktar gir
   ↓
4. ONAY MESAJI
   • "X adet Y ürünü eklenecek"
   • "Zimmetinizden düşülecek"
   • "Tüketim olarak kaydedilecek"
   • Kullanıcı ONAYLAR
   ↓
5. İŞLEM KAYDI (Her ürün için ayrı)
   • Minibar işlemi oluştur
     - Tarih/Saat
     - Kullanıcı
     - Oda
   • Minibar detay kaydet
     - Ürün
     - Eklenen miktar
     - Zimmetten hangi zimmet_detay_id kullanıldı
   • Zimmetten düş (FIFO)
     - PersonelZimmetDetay.kullanilan_miktar += miktar
     - PersonelZimmetDetay.kalan_miktar güncelle
   ↓
6. ZIMMET-TUKETIM ILIŞKISI
   • MinibarIslemDetay.zimmet_detay_id = kullanılan zimmet ID
   • Hangi zimmetten ne kadar kullanıldığı izlenebilir
   • Raporlarda zimmet-tüketim ilişkisi görünür
   ↓
7. LİSTE GÜNCELLEME
   • Modal kapanır
   • Minibar içeriği listesi yenilenir
   • Yeni stok miktarları gösterilir
   • Bir sonraki ürün için tekrar edilebilir
```

### 📋 Zimmet Akışı

```
1. Depo Sorumlusu: Zimmet Oluştur
   • Personel seç
   • Ürünleri seç ve miktar gir
   • Zimmet oluştur
   ↓
2. Kat Sorumlusu: Zimmetim
   • Zimmetli ürünleri görüntüle
   • Kullanılan miktar takibi
   • Kalan miktar kontrolü
   ↓
3. Minibar İşlemlerinde Kullanım
   • İlk dolum/doldurma yapınca
   • Otomatik zimmetden düşer
   ↓
4. İade (Gerekirse)
   • Depo Sorumlusu: İade Al
   • Kullanılmayan ürünler depoya döner
   • Zimmet kapatılır
   ↓
5. İptal (Gerekirse)
   • Depo Sorumlusu: Zimmet İptal
   • Tüm ürünler depoya döner
   • Zimmet silinir
```

---

## 📱 Modül Bazlı Kullanım

### � Admin Modülü

#### Dashboard
- **Toplam Oda Sayısı**: Sistemdeki toplam oda
- **Toplam Ürün**: Sistemdeki tüm ürünler
- **Ürün Grupları**: Tanımlı grup sayısı
- **Personel Sayısı**: Depo ve Kat sorumluları
- **Kritik Stok**: Kritik seviyenin altındaki ürünler
- **Aktif Kullanıcılar**: Sistemdeki tüm kullanıcılar
- **Kat Sayısı**: Tanımlı kat sayısı

#### Kat Yönetimi
1. **Yeni Kat Tanımla**
   - Sol menü → Kat Tanımla
   - Kat Adı: (örn: 1. Kat, Zemin Kat)
   - Kat No: Sıra numarası
   - Kaydet

2. **Kat Düzenle**
   - Dashboard → Kat listesi → Düzenle
   - Bilgileri güncelle
   - Kaydet

3. **Kat Sil**
   - ⚠️ Kat silinirse bu kattaki odalar da silinir
   - Kayıtlar korunur ama aktif olmaz

#### Oda Yönetimi
1. **Yeni Oda Tanımla**
   - Sol menü → Oda Tanımla
   - Kat seç
   - Oda No: (örn: 101, 102)
   - Oda Tipi: (Standart, Suit, vb.)
   - Kaydet

2. **Oda Düzenle**
   - Dashboard → Oda listesi → Düzenle
   - Bilgileri güncelle

#### Admin Atama
1. **Admin Ata**
   - Sol menü → Admin Ata
   - Kullanıcı bilgilerini gir
   - Rol: Admin seç
   - Kaydet

2. **Admin Çıkar**
   - Sol menü → Admin Düzenle
   - Admin seç → Rolü değiştir veya sil

#### Sistem Logları
- **Log Görüntüleme**
  - Sol menü → Sistem Logları
  - Filtreler: Tarih, Modül, Kullanıcı
  - Detaylı log kaydı

---

#### Ürün Grup Yönetimi
1. **Yeni Grup Oluştur**
   - Sol menü → Ürün Grupları
   - Grup Adı: (örn: İçecekler, Atıştırmalık)
   - Açıklama: Opsiyonel
   - Kaydet

2. **Grup Düzenle**
   - Ürün Grupları → Düzenle
   - Bilgileri güncelle

3. **Grup Sil**
   - ⚠️ Grubu silmek için önce gruba bağlı ürünler silinmeli

#### Ürün Yönetimi
1. **Yeni Ürün Tanımla**
   - Sol menü → Ürünler → Yeni Ürün
   - Ürün Adı: (örn: Coca Cola 330ml)
   - Grup: Grup seç
   - Birim: (Adet, Litre, vb.)
   - Kritik Stok Seviyesi: Minimum stok
   - Birim Fiyat: Opsiyonel
   - Kaydet

2. **Ürün Düzenle**
   - Ürünler listesi → Düzenle
   - Bilgileri güncelle

3. **Ürün Sil**
   - Düzenle → Sil
   - ⚠️ Ürün silinirse stok hareketleri korunur ama ürün inaktif olur

#### Personel Yönetimi
1. **Personel Tanımla**
   - Sol menü → Personel Tanımla
   - Ad, Soyad, E-posta
   - Şifre belirle
   - Rol Seç:
     - Admin (Diğer admin kullanıcılar)
     - Depo Sorumlusu
     - Kat Sorumlusu
   - Kaydet

2. **Personel Düzenle**
   - Personel Tanımla → Liste → Düzenle
   - Bilgileri güncelle
   - Rol değiştirme yapılabilir

---

### 📦 Depo Sorumlusu Modülü

#### Dashboard
- **Toplam Stok Değeri**: Tüm ürünlerin toplam değeri
- **Kritik Stok**: Kritik seviyenin altındaki ürün sayısı
- **Aktif Zimmetler**: Devam eden zimmetler
- **Bu Ay İadeler**: Aylık iade sayısı

#### Stok Girişi
1. **Yeni Stok Girişi**
   - Sol menü → Stok Girişi
   - Ürün seç (dropdown'dan)
   - Miktar: Giriş yapılacak miktar
   - Birim Fiyat: Opsiyonel
   - Açıklama: (örn: Tedarikçi: ABC Firma)
   - Kaydet

2. **Sonuç**
   - Stok otomatik güncellenir
   - Stok hareketi kaydedilir
   - Dashboard güncelenir

#### Stok Düzenleme
1. **Stok Düzelt**
   - Sol menü → Stok Düzenle
   - Ürün seç
   - Yeni Miktar: Düzeltilmiş miktar
   - İşlem Tipi: Düzeltme
   - Açıklama: Neden düzeltildi
   - Kaydet

#### Personel Zimmet
1. **Yeni Zimmet Oluştur**
   - Sol menü → Personel Zimmet
   - Personel Seç: Kat sorumlusu dropdown
   - Ürün Ekle: + butonu ile ürün seç
   - Her ürün için miktar gir
   - Açıklama: Opsiyonel
   - "Zimmet Oluştur" buton

2. **Zimmet İptal**
   - Personel Zimmet → Aktif zimmetler
   - İptal Et butonu
   - Onay ver
   - Tüm ürünler depoya döner

3. **Zimmet İade Al**
   - Zimmet detayına git
   - Ürün satırında "İade Al"
   - İade miktarı gir
   - Kaydet
   - Ürün depoya döner

#### Zimmet Detay
1. **Zimmet Görüntüleme**
   - Personel Zimmet → Detay
   - Zimmet bilgileri
   - Ürün listesi
   - Kullanılan/Kalan miktarlar
   - İade işlemleri

#### Minibar Durumları
1. **Minibar Sorgula**
   - Sol menü → Minibar Durumları
   - Kat seç (dropdown)
   - Oda seç (cascade dropdown)
   - Otomatik yüklenir

2. **Görüntüleme**
   - Toplam ürün çeşidi
   - Toplam miktar
   - Son işlem tipi
   - Son işlem bilgileri
   - Minibar içeriği tablosu

3. **Ürün Geçmişi**
   - Ürün adına tıkla
   - Modal açılır
   - Tüm işlem geçmişi
   - Tarih, personel, miktar bilgileri

#### Raporlar
1. **Stok Durum Raporu**
   - Raporlar → Rapor Tipi: Stok Durum
   - Grup filtresi (opsiyonel)
   - Raporla
   - Tüm ürünler ve stokları listelenir

2. **Stok Hareket Raporu**
   - Raporlar → Stok Hareket
   - Tarih aralığı seç
   - Ürün/Grup filtresi
   - Hareket tipi: Giriş, Çıkış, Düzeltme
   - Tüm hareketler detaylı gösterilir

3. **Zimmet Raporu**
   - Raporlar → Zimmet
   - Tarih aralığı
   - Personel filtresi
   - Durum: Aktif, Tamamlanmış, İptal
   - Liste gösterimi

4. **Minibar Tüketim Raporu** ⭐ YENİ
   - Raporlar → Minibar Tüketim
   - Tarih aralığı seç
   - Ürün/Grup filtresi
   - Personel filtresi
   - **Gösterir:**
     - Hangi üründen ne kadar tüketildi
     - Hangi oda, hangi kat
     - Kim doldurdu, ne zaman
     - İşlem tipi (Doldurma/Kontrol)

---

### 🛏️ Kat Sorumlusu Modülü

#### Dashboard
- **Bugünkü İşlemlerim**: Günlük yapılan işlem sayısı
- **Zimmetim**: Toplam zimmetli ürün miktarı
- **Bu Hafta Tüketim**: Haftalık tüketim
- **Sorumlu Olduğum Odalar**: Kat bilgisi

#### Zimmetim
1. **Zimmet Görüntüleme**
   - Sol menü → Zimmetim
   - Aktif zimmetler listesi
   - Her ürün için:
     - Zimmet miktarı
     - Kullanılan miktar
     - Kalan miktar
     - İade edilen miktar

2. **Zimmet Detayları**
   - Zimmet detayına tıkla
   - Zimmet tarihi
   - Ürün listesi
   - Kullanım geçmişi

#### Minibar Kontrol ⭐ YENİ SİSTEM
1. **Kat, Oda ve İşlem Tipi Seçimi**
   - Sol menü → Minibar Kontrol
   - **Kat Seç** (sadece kendi katı görünür)
   - **Oda Seç** (seçilen kattaki odalar)
   - **İşlem Tipi Seç:**
     - **İlk Dolum**: Yeni oda ilk doldurma
     - **Kontrol**: Minibar içeriğini görüntüleme
     - **Doldurma**: Tek tek ürün ekleme

2. **İlk Dolum İşlemi** (Eski Sistem)
   - Oda daha önce doldurulmamış olmalı
   - **Ürün Grubu Seç** → **Ürün Seç** → **Miktar Gir**
   - **Zimmet Bilgisi** otomatik gösterilir
   - **Listeye Ekle** butonu ile ürünleri ekle
   - Tüm ürünler eklendikten sonra **Kaydet**
   - Zimmetli ürünler otomatik düşer

3. **Kontrol İşlemi** ⭐ YENİ
   - Oda seçilince **minibar içeriği** otomatik gösterilir
   - Liste halinde:
     - Ürün Adı
     - Grup
     - Mevcut Stok
     - Birim
   - **Sadece görüntüleme modu** (işlem yapılmaz)
   - Mevcut durumu kontrol etmek için kullanılır

4. **Doldurma İşlemi** ⭐ YENİ SİSTEM
   - Oda seçilince **minibar içeriği listesi** gösterilir
   - Her ürün satırında **"Ekle"** butonu var
   
   **Tek Ürün Doldurma Adımları:**
   1. **Ekle** butonuna tıkla
   2. **Modal pencere** açılır:
      - Ürün adı
      - Mevcut stok
      - Zimmetinizde kalan miktar
   3. **Eklenecek miktarı gir**
   4. **Onayla ve Ekle** butonuna tıkla
   5. **Onay Mesajı** gösterilir:
      ```
      X adet Y ürünü minibar'a eklenecek.
      
      Bu işlem sonucunda:
      • X adet ürün minibar'a eklenecek
      • Zimmetinizden X adet düşülecek
      • Tüketim olarak kaydedilecek
      
      Onaylıyor musunuz?
      ```
   6. **Evet** derseniz:
      - Ürün minibar'a eklenir
      - Zimmetten düşülür (FIFO mantığı)
      - Tarih, saat, kullanıcı bilgisi ile kaydedilir
      - Zimmet-Tüketim ilişkisi kurulur
   
   **Önemli:**
   - Her ürün için ayrı ayrı işlem yapılır
   - Anlık zimmet kontrolü yapılır
   - Her işlem anında kaydedilir
   - Liste otomatik güncellenir

#### Raporlar
1. **Tüketim Raporu**
   - Raporlar → Rapor Tipi: Tüketim
   - Tarih aralığı seç
   - Ürün bazlı tüketim
   - Toplam tuketim, işlem sayısı

2. **Oda Bazlı Rapor**
   - Raporlar → Oda Bazlı
   - Tarih aralığı
   - Her oda için:
     - İşlem sayısı
     - Toplam tüketim
     - Son işlem tarihi

3. **Genel Özet**
   - Raporlar → Genel Özet
   - Toplam istatistikler
   - Grafik gösterimleri

---

## 💡 Kullanım Senaryoları

### Senaryo 1: Yeni Otel Kurulumu

```
1. Admin (İlk Kullanıcı)
   ├─ İlk kurulumu tamamla
   ├─ Katları tanımla (1.Kat, 2.Kat, 3.Kat)
   ├─ Odaları tanımla (101-110, 201-210, 301-310)
   ├─ Ürün grupları oluştur (İçecek, Gıda, Atıştırmalık)
   ├─ Ürünleri tanımla (50 farklı ürün)
   ├─ Depo sorumlusunu ekle
   ├─ Kat sorumlularını ekle (3 kat sorumlusu)
   └─ İsteğe bağlı: Diğer admin kullanıcıları ata

2. Depo Sorumlusu
   ├─ İlk stok girişi yap (tedarikçiden gelen ürünler)
   └─ Her kat sorumlusuna zimmet oluştur

3. Kat Sorumluları
   └─ Tüm odaların ilk dolumunu yap
```

### Senaryo 2: Günlük Rutin İşlemler

```
Sabah
├─ Kat Sorumlusu
│  ├─ Checkout odaları kontrol et
│  ├─ Temizlik sonrası minibar kontrolü yap
│  └─ Tüketilen ürünleri doldur
│
├─ Depo Sorumlusu
│  ├─ Dashboard'dan kritik stok kontrolü
│  └─ Gerekirse zimmet iade al

Öğlen
└─ Depo Sorumlusu
   ├─ Tedarikçi gelişi varsa stok girişi yap
   └─ Zimmet durumlarını kontrol et

Akşam
├─ Admin
│  └─ Günlük stok raporlarını kontrol et
│
└─ Depo Sorumlusu
   ├─ Günlük minibar tüketim raporunu çıkar
   └─ Ertesi gün için gerekli malzemeleri hazırla
```

### Senaryo 3: Haftalık/Aylık İşlemler

```
Hafta Sonu
├─ Admin
│  ├─ Haftalık stok hareket raporunu incele
│  └─ Kritik stok ürünleri tespit et
│
└─ Depo Sorumlusu
   ├─ Zimmet raporunu çıkar
   └─ Tedarikçi siparişi hazırla

Ay Sonu
├─ Admin
│  ├─ Kullanıcı aktivitelerini kontrol et
│  ├─ Sistem loglarını incele
│  ├─ Aylık tüketim analizi
│  ├─ En çok tüketen ürünleri tespit et
│  └─ Aylık özet rapor hazırla
│
└─ Depo Sorumlusu
   ├─ Aylık zimmet raporunu oluştur
   ├─ İade ve iptal edilen zimmetleri raporla
   └─ Minibar tüketim raporunu incele
```

---

## ❓ Sık Sorulan Sorular

### Genel Sorular

**S: Şifremi unuttum, ne yapmalıyım?**
C: Admin, personel düzenleme sayfasından şifrenizi sıfırlayabilir.

**S: Birden fazla tarayıcı/cihazdan giriş yapabilir miyim?**
C: Evet, aynı anda birden fazla oturumunuz olabilir.

**S: Mobil cihazdan kullanabilir miyim?**
C: Evet, sistem responsive tasarıma sahiptir. Telefon ve tablet'ten kullanılabilir.

**S: İnternet olmadan çalışır mı?**
C: Hayır, sistem web tabanlıdır ve internet bağlantısı gerektirir.

### Stok Yönetimi

**S: Yanlış stok girişi yaptım, nasıl düzeltirim?**
C: Depo Sorumlusu → Stok Düzenle → Ürün seç → Yeni miktar gir → İşlem tipi: Düzeltme

**S: Kritik stok uyarısı geldi, ne yapmalıyım?**
C: Dashboard'da kritik stok ürünleri gösterilir. Tedarikçiden sipariş vererek stok yapın.

**S: Stok sayımı nasıl yaparım?**
C: Stok Düzenle modülünden her ürün için fiili sayımı girin, sistem farkı hesaplar.

**S: Ürün fiyatı değişirse ne olur?**
C: Ürün düzenleme sayfasından yeni fiyatı girin. Geçmiş kayıtlar eski fiyatla kalır.

### Zimmet İşlemleri

**S: Kat sorumlusu zimmetli ürünü kaybederse ne olur?**
C: Zimmet kaydı sistemde kalır. Depo Sorumlusu zimmet iade almaz, kalan miktar personelin sorumluluğundadır.

**S: Zimmet iptal ile iade arasındaki fark nedir?**
C: 
- **İptal**: Tüm zimmet iptal edilir, tüm ürünler depoya döner, zimmet silinir
- **İade**: Belirli ürünler iade alınır, zimmet devam eder

**S: Zimmet süresi var mı?**
C: Hayır, zimmet manuel olarak tamamlanana kadar devam eder.

**S: Bir personel birden fazla aktif zimmeti olabilir mi?**
C: Evet, bir personelin birden fazla aktif zimmeti olabilir.

### Minibar İşlemleri

**S: İlk dolum yaparken stok yetmezse ne olur?**
C: Sistem stok kontrolü yapar. Yeterli stok yoksa işlem yapılmaz, hata mesajı gösterilir.

**S: Yanlış oda numarasına işlem yaptım, nasıl düzeltirim?**
C: Admin, veritabanından manuel düzeltme yapmalıdır. (Gelişmiş özellik)

**S: Minibar geçmişini nasıl görürüm?**
C: Depo Sorumlusu → Minibar Durumları → Oda seç → Ürün adına tıkla

**S: Tüketim nasıl hesaplanır?**
C: Tüketim = Başlangıç Stok - Bitiş Stok

**S: Doldurma ve kontrol arasındaki fark nedir?**
C:
- **Kontrol**: Sadece sayım yapılır, ürün eklenmez
- **Doldurma**: Tüketilen ürünler yeniden eklenir

### Raporlar

**S: Rapor Excel'e aktarılır mı?**
C: Gelecek versiyonda Excel export özelliği eklenecektir.

**S: Geçmiş tarihlerin raporunu alabiliyor muyum?**
C: Evet, tarih aralığı seçerek istediğiniz döneme ait rapor alabilirsiniz.

**S: Minibar tüketim raporu nasıl çalışır?**
C: İlk dolum hariç, tüm doldurma ve kontrol işlemlerinde eklenen miktar = tüketilen miktar olarak raporlanır.

---

## 🎓 İpuçları ve En İyi Uygulamalar

### Stok Yönetimi İçin

1. ✅ **Düzenli Sayım**: Haftada bir fiili stok sayımı yapın
2. ✅ **Kritik Stok**: Her ürün için doğru kritik stok seviyesi belirleyin
3. ✅ **Açıklama**: Stok girişlerinde mutlaka açıklama ekleyin (tedarikçi, fatura no)
4. ✅ **Fiyat Takibi**: Birim fiyatları düzenli güncelleyin

### Zimmet İçin

1. ✅ **Haftalık Zimmet**: Kat sorumlularına haftalık zimmet verin
2. ✅ **Düzenli İade**: Kullanılmayan ürünleri hafta sonunda iade alın
3. ✅ **Takip**: Dashboard'dan zimmet durumlarını günlük kontrol edin
4. ✅ **Açıklama**: Zimmet oluştururken amacı belirtin

### Minibar İçin

1. ✅ **İlk Dolum**: Yeni odaları mutlaka ilk dolum olarak işaretleyin
2. ✅ **Düzenli Kontrol**: Checkout sonrası her oda kontrol edilmeli
3. ✅ **Hızlı Doldurma**: Tüketimi gördüğünüzde hemen doldurun
4. ✅ **Geçmiş Kontrolü**: Ürün geçmişine bakarak anormal tüketim tespit edin

### Raporlama İçin

1. ✅ **Günlük**: Her gün tüketim raporu kontrol edin
2. ✅ **Haftalık**: Stok hareket raporu çıkarın
3. ✅ **Aylık**: Genel analiz ve özet rapor hazırlayın
4. ✅ **Trend**: Aylık raporları karşılaştırarak trend analizi yapın

---

## 🆘 Destek ve Yardım

### Teknik Sorunlar

- **Hata Mesajları**: Ekran görüntüsü alıp Sistem Yöneticisi'ne iletin
- **Yavaşlık**: Tarayıcı cache'ini temizleyin
- **Bağlantı Sorunu**: İnternet bağlantınızı kontrol edin

### İletişim

- **Admin**: Otel içi teknik destek ve işleyiş soruları
- **Dokümantasyon**: Bu kullanım kılavuzu ve README.md

---

## 📚 Ek Kaynaklar

- **README.md**: Teknik dokümantasyon
- **RAILWAY_DEPLOY.md**: Deployment guide
- **DEPLOYMENT_CHECKLIST.md**: Deploy kontrol listesi

---

**Versiyon**: 1.0  
**Son Güncelleme**: 30 Ekim 2025  
**Hazırlayan**: Otel Minibar Takip Sistemi Geliştirme Ekibi

---

*Bu kılavuz düzenli olarak güncellenecektir. Önerileriniz için sistem yöneticinize başvurabilirsiniz.*
