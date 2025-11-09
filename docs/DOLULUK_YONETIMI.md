# Otel Doluluk Yönetimi

## Genel Bakış

Otel Doluluk Yönetimi modülü, otel odalarının doluluk durumlarını Excel dosyaları üzerinden yönetmenizi sağlar. IN HOUSE (mevcut misafirler) ve ARRIVALS (gelecek misafirler) listelerini sisteme yükleyerek oda doluluk bilgilerini otomatik olarak güncelleyebilirsiniz.

## Özellikler

### 1. Excel Dosyası Yükleme
- **Otomatik Tip Algılama**: Sistem, yüklenen Excel dosyasının IN HOUSE veya ARRIVALS olduğunu sütun başlıklarından otomatik algılar
- **Drag & Drop Desteği**: Dosyaları sürükleyip bırakarak yükleyebilirsiniz
- **Asenkron İşleme**: Büyük dosyalar arka planda işlenir, sistem donmaz
- **İlerleme Takibi**: Dosya işleme durumunu gerçek zamanlı takip edebilirsiniz

### 2. Veri İşleme
- **IN HOUSE Listesi**: Otelde hali hazırda konaklayan misafirlerin bilgileri
- **ARRIVALS Listesi**: Otele giriş yapacak misafirlerin bilgileri (giriş saati dahil)
- **Veri Doğrulama**: Tüm veriler yüklenmeden önce doğrulanır
- **Hata Raporlama**: Hatalı satırlar detaylı olarak raporlanır

### 3. Oda Doluluk Bilgileri
- **Mevcut Durum**: Hangi odalar dolu, hangileri boş
- **Kalan Gün**: Misafirlerin çıkış tarihine kaç gün kaldığı
- **Gelecek Rezervasyonlar**: Odaya gelecek misafir bilgileri
- **Geçmiş Kayıtlar**: Odanın geçmiş doluluk geçmişi

### 4. Günlük Doluluk Raporu
- **Özet İstatistikler**: Toplam oda, dolu oda, giriş/çıkış sayıları
- **Haftalık Özet**: 7 günlük doluluk oranları
- **Kat Bazlı Görünüm**: Her kattaki dolu odaların listesi
- **Yazdırma Desteği**: Raporları yazdırabilirsiniz

### 5. Hatalı Yükleme Geri Alma
- **İşlem Kodu**: Her yükleme için benzersiz kod
- **Toplu Silme**: İşlem koduna göre tüm kayıtları silebilirsiniz
- **Audit Trail**: Tüm işlemler loglanır

### 6. Otomatik Dosya Temizleme
- **4 Gün Saklama**: Yüklenen dosyalar 4 gün saklanır
- **Otomatik Silme**: 5. gün otomatik olarak silinir
- **Zamanlanmış Görev**: Her gün saat 02:00'de çalışır

## Kullanım

### Depo Sorumlusu

#### Excel Dosyası Yükleme

1. **Doluluk Yönetimi** menüsüne tıklayın
2. Excel dosyanızı seçin veya sürükleyip bırakın
3. **Dosyayı Yükle ve İşle** butonuna tıklayın
4. İşlem tamamlanana kadar bekleyin

#### Desteklenen Excel Formatları

**IN HOUSE Listesi:**
```
Name | Room no | R.Type | Arrival | Departure | Adult
```

**ARRIVALS Listesi:**
```
Name | Room no | R.Type | Hsk.St. | Arr.Time | Arrival | Departure | Adult
```

#### Hatalı Yükleme Silme

1. Yükleme geçmişinde silmek istediğiniz kaydı bulun
2. **Sil** butonuna tıklayın
3. Onaylayın

### Kat Sorumlusu

#### Günlük Doluluk Görüntüleme

1. **Günlük Doluluk** menüsüne tıklayın
2. Tarih seçin (varsayılan bugün)
3. Raporu görüntüleyin

#### Oda Detay Görüntüleme

1. Günlük doluluk raporunda bir odaya tıklayın
2. Oda detay sayfasında:
   - Mevcut misafir bilgilerini görün
   - Gelecek rezervasyonları kontrol edin
   - Geçmiş kayıtları inceleyin

## Teknik Detaylar

### Veritabanı Tabloları

#### misafir_kayitlari
- Oda doluluk kayıtları
- Giriş/çıkış tarihleri
- Misafir sayısı
- Kayıt tipi (in_house/arrival)

#### dosya_yuklemeleri
- Excel yükleme kayıtları
- İşlem kodu
- Durum bilgisi
- İstatistikler

### API Endpoint'leri

- `GET /doluluk-yonetimi` - Ana sayfa
- `POST /doluluk-yonetimi/yukle` - Dosya yükleme
- `POST /doluluk-yonetimi/sil/<islem_kodu>` - Silme
- `GET /doluluk-yonetimi/durum/<islem_kodu>` - Durum sorgulama
- `GET /oda-doluluk/<oda_id>` - Oda detay
- `GET /gunluk-doluluk` - Günlük rapor

### Servisler

#### ExcelProcessingService
- Excel dosyalarını işler
- Veri doğrulama
- Otomatik tip algılama

#### FileManagementService
- Dosya yükleme/silme
- İşlem kodu oluşturma
- Otomatik temizleme

#### OccupancyService
- Doluluk hesaplamaları
- Günlük raporlar
- Oda detay bilgileri

## Güvenlik

- **Dosya Validasyonu**: Sadece .xlsx ve .xls dosyaları kabul edilir
- **Boyut Limiti**: Maksimum 10 MB
- **Yetkilendirme**: Role-based access control
- **CSRF Koruması**: Tüm form işlemlerinde
- **Audit Trail**: Tüm işlemler loglanır

## Performans

- **Asenkron İşleme**: Büyük dosyalar arka planda işlenir
- **Batch Insert**: Toplu veritabanı işlemleri
- **İndeksler**: Hızlı sorgulama için optimize edilmiş
- **Hedef**: 500 satır/30 saniye

## Sorun Giderme

### Dosya Yüklenmiyor
- Dosya formatını kontrol edin (.xlsx veya .xls)
- Dosya boyutunu kontrol edin (max 10 MB)
- Sütun başlıklarını kontrol edin

### Veriler Görünmüyor
- Dosya işleme durumunu kontrol edin
- Hata detaylarını inceleyin
- Oda numaralarının sistemde kayıtlı olduğundan emin olun

### Performans Sorunları
- Dosya boyutunu küçültün
- Gereksiz satırları temizleyin
- Sunucu kaynaklarını kontrol edin

## Gelecek Geliştirmeler

- PMS entegrasyonu (otomatik veri çekme)
- Gerçek zamanlı bildirimler
- Mobil uygulama desteği
- Gelişmiş raporlama (grafikler, trendler)
- Tahminleme algoritmaları

## Destek

Sorun veya önerileriniz için sistem yöneticinize başvurun.
